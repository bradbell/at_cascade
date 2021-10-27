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
# input table file names
location_table_csv  = 'location_map.csv'
ldi_table_csv       = 'ldi_covariate_data.csv'
obesity_table_csv   = 'obesity_covariate_data.csv'
data_table_csv      = 'overall_diabetes_input_data_crosswalkv35057.csv'
#
# output table file name
data_table_out      = 'data.csv'
node_table_out      = 'node.csv'
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
# covariate_dict = get_covariate_dict(file_name)
def get_covariate_dict(file_name) :
    # LDI and obseity do do not depend on age
    file_ptr        = open(file_name)
    reader          = csv.DictReader(file_ptr)
    covariate_dict  = dict()
    for row in reader :
        location_id  = int( row['location_id'] )
        year_id      = int( row['year_id'] )
        sex          = row['sex']
        mean_value   = float( row['mean_value'] )
        if not sex in covariate_dict :
            covariate_dict[sex] = dict()
        if not location_id in covariate_dict[sex] :
            covariate_dict[sex][location_id] = dict()
        assert not year_id in covariate_dict[sex][location_id]
        covariate_dict[sex][location_id][year_id] = mean_value
    #
    return covariate_dict
# ---------------------------------------------------------------------------
# location_table = get_location_table(file_name)
def get_location_table(file_name) :
    file_ptr        = open(file_name)
    reader          = csv.DictReader(file_ptr)
    location_table  = list()
    for row_in in reader :
        row_out = dict()
        row_out['location_id']   = int( row_in['location_id'] )
        row_out['location_name'] = row_in['location_name']
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
        row_out['time_upper']   = float( row_in['year_end'] ) + 1.0
        row_out['age_lower']    = float( row_in['age_start'] )
        row_out['age_upper']    = float( row_in['age_end'] ) + 1.0
        row_out['meas_value']   = float( row_in['mean'] )
        row_out['meas_std']     = float( row_in['standard_error'] )
        row_out['obesity']      = None
        row_out['ldi']          = None
        #
        if row_in['measure'] == 'incidence' :
            row_out['integrand']    = 'Sincidence'
        else :
            row_out['integrand']    = row_in['measure']
        #
        data_table.append( row_out )
    return data_table
# ---------------------------------------------------------------------------
def get_covariate(covariate_dict, sex, location_id, time) :
    year    = time + 0.5
    year_id = int( time )
    if not year_id in covariate_dict[sex][location_id] :
        return None
    if not year_id + 1 in covariate_dict[sex][location_id] :
        return None
    cleft  = covariate_dict[sex][location_id][year_id]
    cright = covariate_dict[sex][location_id][year_id + 1]
    cvalue = cright * (time - year_id) + cleft * (year_id  + 1 - time)
    return cvalue
# ---------------------------------------------------------------------------
def write_csv(file_name, table) :
    fieldnames  = table[0].keys()
    file_ptr    = open(file_name, 'w')
    writer      = csv.DictWriter(file_ptr, fieldnames = fieldnames)
    writer.writeheader()
    writer.writerows( table )
    file_ptr.close()
# ---------------------------------------------------------------------------
def print_table(table, n) :
    for data_id in range(n) :
        print(table[data_id])
# ---------------------------------------------------------------------------
# sex_set = get_set(table)
def get_value_set(table, column_name) :
    value_set = set()
    for row in table :
        value_set.add( row[column_name] )
    return value_set
# ---------------------------------------------------------------------------
def main() :
    #
    # data_table
    data_table = get_data_table(data_table_csv)
    #
    # location_table
    location_table = get_location_table(location_table_csv)
    #
    # covariate information by sex, location_id, year_id
    obesity_dict    = get_covariate_dict(obesity_table_csv)
    ldi_dict        = get_covariate_dict(ldi_table_csv)
    #
    # location_id2node_id
    location_id2node_id = dict()
    for (node_id, row) in enumerate(location_table) :
        location_id = row['location_id']
        location_id2node_id[location_id]  = node_id
    #
    # add covariates to data_table
    for row in data_table :
        sex             = row['sex']
        location_id     = row['location_id']
        time            = (row['time_lower'] + row['time_upper']) / 2.0
        row['obesity']  = get_covariate(obesity_dict, sex, location_id, time)
    #
    # change location_id to node_id
    for row in data_table :
        location_id    = row['location_id']
        node_id        = location_id2node_id[location_id]
        row['node_id'] = node_id
        del row['location_id']
    #
    # create data_table_out
    write_csv(data_table_out, data_table)
    #
    # node_table
    node_table = list()
    for (node_id, row_in) in enumerate(location_table) :
        location_name        = row_in['location_name']
        location_id          = row_in['location_id']
        parent_location_id   = row_in['parent_id']
        if parent_location_id == location_id :
            parent_node_id = None
        else :
            parent_node_id = location_id2node_id[parent_location_id]
        row_out = dict()
        row_out['node_id']   = node_id
        row_out['node_name'] = location_name
        row_out['parent']    = parent_node_id
        node_table.append(row_out)
    #
    # create node_table_out
    write_csv(node_table_out, node_table)
    #
main()
print(sys.argv[0] + ': OK')
sys.exit(0)
