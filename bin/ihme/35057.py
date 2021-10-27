#! /usr/bin/python3
# -----------------------------------------------------------------------------
# at_cascade: Cascading Dismod_at Analysis From Parent To Child Regions
#           Copyright (C) 2021-21 University of Washington
#              (Bradley M. Bell bradbell@uw.edu)
#
# This program is distributed under the terms of the
#     GNU Affero General Public License version 3.0 or later
# see http://www.gnu.org/licenses/agpl.txt
# -----------------------------------------------------------------------------
disease_name        = 'diabetes'
age_table_csv       = 'age_metadata_gbd2020.csv'
location_table_csv  = 'location_map.csv'
ldi_table_csv       = 'ldi_covariate_data.csv'
obesity_table_csv   = 'obesity_covariate_data.csv'
data_table_csv      = 'overall_diabetes_input_data_crosswalkv35057.csv'
# -----------------------------------------------------------------------------
#
import csv
import copy
import sys
import os
import distutils.dir_util
import shutil
import dismod_at
#
# import at_cascade with a preference current directory version
current_directory = os.getcwd()
if os.path.isfile( current_directory + '/at_cascade/__init__.py' ) :
    sys.path.insert(0, current_directory)
import at_cascade
#
# work_dir
work_dir = 'ihme_db/csv/35057'
distutils.dir_util.mkpath(work_dir)
os.chdir(work_dir)
# ---------------------------------------------------------------------------
# age_table = get_age_table(file_name)
def get_age_table(file_name) :
    file_ptr  = open(file_name)
    reader    = csv.DictReader(file_ptr)
    age_table = list()
    for row_in in reader :
        row_out = dict()
        row_out['age_group_id'] = int( row_in['age_group_id'] )
        row_out['age_lower'] = float( row_in['age_group_years_start'] )
        row_out['age_upper'] = float( row_in['age_group_years_end'] )
        age_table.append( row_out )
    #
    age_table = sorted(age_table, key = lambda row: row['age_lower'] )
    #
    # check that age_table splits ages into non-overlapping intervals
    row_prev = None
    for row in age_table :
        assert row['age_lower'] < row['age_upper']
        if not row_prev is None :
            assert row['age_lower'] == row_prev['age_upper']
    #
    return age_table
# ---------------------------------------------------------------------------
# covariate_table = get_covariate_table(file_name)
def get_covariate_table(file_name) :
    file_ptr        = open(file_name)
    reader          = csv.DictReader(file_ptr)
    covariate_table = list()
    for row_in in reader :
        row_out = dict()
        row_out['age_group_id'] = int( row_in['age_group_id'] )
        row_out['sex']          = row_in['sex']
        row_out['year_id']      = int( row_in['year_id'] )
        row_out['value']        = float( row_in['mean_value'] )
        covariate_table.append( row_out )
    return covariate_table
# ---------------------------------------------------------------------------
# location_table = get_location_table(file_name)
def get_location_table(file_name) :
    file_ptr        = open(file_name)
    reader          = csv.DictReader(file_ptr)
    location_table  = list()
    for row_in in reader :
        row_out = dict()
        row_out['location_name'] = row_in['location_name']
        row_out['location_id']   = int( row_in['location_id'] )
        row_out['parent_id']     = int( row_in['parent_id'] )
        location_table.append( row_out )
    return location_table
# ---------------------------------------------------------------------------
# data_table = get_data_table(file_name)
def get_data_table(file_name) :
    file_ptr   = open(file_name)
    reader     = csv.DictReader(file_ptr)
    data_table = list()
    for row_in in reader :
        row_out = dict()
        row_out['location_id']  = int( row_in['location_id'] )
        row_out['sex']          = row_in['sex']
        row_out['time_lower']   = float( row_in['year_start'] )
        row_out['time_upper']   = float( row_in['year_end'] )
        row_out['age_lower']    = float( row_in['age_start'] )
        row_out['age_upper']    = float( row_in['age_end'] )
        row_out['meas_value']   = float( row_in['mean'] )
        row_out['meas_std']     = float( row_in['standard_error'] )
        #
        if row_in['measure'] == 'incidence' :
            row_out['integrand']    = 'Sincidence'
        else :
            row_out['integrand']    = row_in['measure']
        #
        data_table.append( row_out )
    return data_table
# --------------------------------------------------------------------------
def age_and_time_id2cov(covariate_table, group_id2age_id) :
    result = dict()
    for row in covariate_table :
        group_id = row['age_group_id']
        if group_id in group_id2age_id :
            age_id   = group_id2age_id[group_id]
            time_id  = row['time_id']
            value    = row['value']
            if not age_id in result :
                result[age_id] = dict()
            assert not time_id  in result[age_id]
            result[age_id][time_id] = value
    return result
# ---------------------------------------------------------------------------
def print_table(table) :
    for row in table :
        print(row)
# ---------------------------------------------------------------------------
# sex_set = get_sex_set(table)
def get_value_set(table, column_name) :
    value_set = set()
    for row in table :
        value_set.add( row[column_name] )
    return value_set
# ---------------------------------------------------------------------------
# table = get_table()
def get_table() :
    table = dict()
    table['location'] = get_location_table(location_table_csv)
    table['age']      = get_age_table(age_table_csv)
    table['ldi']      = get_covariate_table( ldi_table_csv )
    table['obesity']  = get_covariate_table( obesity_table_csv )
    table['data']     = get_data_table( data_table_csv )

    return table
# ---------------------------------------------------------------------------
def main() :
    #
    # table
    table = get_table()
    print_table( table['ldi'] )
    #
    # group_id2age_d, age_id2group_id
    # Due to sorting, age is monotone increase with age_id
    group_id2age_id = dict()
    age_id2group_id = dict()
    for (age_id, row) in enumerate(table['age']) :
        group_id = row['age_group_id']
        group_id2age_id[group_id] = age_id
        age_id2group_id[age_id]    = group_id
    #
    # ldi_age_time
    ldi_age_time     = age_and_time_id2cov(table['ldi'], group_id2age_id)
    obesity_age_time = age_and_time_id2cov(table['obesity'], group_id2age_id)
    #
main()
print(sys.argv[0] + ': OK')
sys.exit(0)
