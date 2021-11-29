#! /usr/bin/python3
# -----------------------------------------------------------------------------
# at_cascade: Cascading Dismod_at Analysis From Parent To Child Regions
#           Copyright (C) 2021-21 University of Washington
#              (Bradley M. Bell bradbell@uw.edu)
#
# This program is distributed under the terms of the
#     GNU Affero General Public License version 3.0 or later
# see http://www.gnu.org/licenses/agpl.txt
# ----------------------------------------------------------------------------
# These settings can be easily changed without understanding the code below:
#
# working_directory
# This directory is relative to your copy of the at_cascade git directory.
# The input and output files are relative to this directory.
working_directory = 'ihme_db/35057'
#
# input file names
location_table_csv  = 'location_map.csv'
ldi_table_csv       = 'ldi_covariate_data.csv'
obesity_table_csv   = 'gbd_2020_obesity_covariate_updated.csv'
data_table_csv      = 'overall_diabetes_input_data_crosswalkv35057.csv'
emr_table_csv       = 'diabetes_emr.csv'
age_group_table_csv = 'age_metadata_gbd2020.csv'
all_node_other      = '../475876/all_node.db'
root_node_other     = '../475876/dismod.db'
#
# directory where results will be written
ihme_output_dir = '/ihme/j/Project/nfrqe/DisMod_AT/testing_results'
#
# data and node table information that was extracted from the input files
data_table_info     = 'data_info.csv'
node_table_info     = 'node_info.csv'
#
# root_node_name
# name of the node where the cascade will start
root_node_name      = 'Global'
#
# shift_prior_std_factor
# Factor that multipliers standard deviation that is passed down the cascade.
shift_prior_std_factor = 4.0
#
# mas_fit
# Maximum number of data rows per integrand to include in a fit.
max_fit             = 250
#
# max_abs_effect
# Maximum absolute effect for any covriate multiplier.
max_abs_effect      = 2.0
#
# max_plot
# Maximum number of data points to plot per integrand.
max_plot            = 2000
#
# gamma_factor
# The gamma for each integrand is this factor times the median
# of the data for the integrand.
gamma_factor        = 1e-2
#
# random_seed
# If this seed is zero, the clock is used for the random seed.
# Otherwise this value is used. In either case the actual seed is reported.
random_seed = 0
#
# fit_goal_set
# Name of the nodes that we are drilling to (must be below root_node).
# fit_goal_set = {'California', 'Mississippi', 'Germany', 'Ireland' }
fit_goal_set = { 'Global' }
#
# split_fit_set
# Name of the nodes where we are splitting from Both to Female, Male
split_fit_set = {'United_States_of_America', 'Western_Europe'}
#
# all_age_group_id_list
# The integer codes of the IHME ages groups that span all ages.
all_age_group_id_list = [ 22, 27 ]
#
# sex_name2sex_id
# Mapping from sex name to IHME sex_id.
sex_name2sex_id = {'Male' : 1,  'Female' : 2, 'Both' : 3}
#
# sex_name2covariate_value
# Mapping from sex name to dismod_at covariate value.
sex_name2covariate_value = { 'Female' : -0.5, 'Both' : 0.0, 'Male' : +0.5 }
#
# integrand_name2measure_id
# Mappping from the dismod_at integrand name to IHME measure_id;
# see the heading Integrand, I_i(a, t) in the web page
# https://bradbell.github.io/dismod_at/doc/avg_integrand.htm
integrand_name2measure_id = {
    'Sincidence' : 41,
    'remission'  : 7,
    'mtexcess'   : 9,
    'mtother'    : 16,
    'mtwith'     : 13,
    'prevalence' : 5,
    'Tincidence' : 42,
    'mtspecific' : 10,
    'mtall'      : 14,
    'mtstandard' : 12,
    'relrisk'    : 11,
}
#
# copy_file_list
# Files, created by predict command, that are copied to ihme_output_dir
copy_file_list = [
    'variable.csv', 'data.csv', 'ihme.csv', 'rate.pdf', 'ihme.pdf', 'data.pdf'
]
# -----------------------------------------------------------------------------
#
import numpy
from scipy.interpolate import  UnivariateSpline
from scipy.interpolate import  RectBivariateSpline
import statistics
import datetime
import time
import random
import math
import csv
import copy
import sys
import os
import shutil
import dismod_at
#
# import at_cascade with a preference current directory version
current_directory = os.getcwd()
if os.path.isfile( current_directory + '/at_cascade/__init__.py' ) :
    sys.path.insert(0, current_directory)
import at_cascade
#
# working_directory
if not os.path.exists(working_directory) :
    os.makedirs(working_directory)
#
# random.seed
if random_seed == 0 :
    random_seed = int( time.time() )
print('random_seed = ', random_seed)
random.seed(random_seed)
# ---------------------------------------------------------------------------
# location_table = get_location_table(file_name)
def get_location_table(file_name) :
    file_ptr        = open(file_name)
    reader          = csv.DictReader(file_ptr)
    location_table  = list()
    location_id_set = set()
    for row_in in reader :
        location_name = row_in['location_name']
        location_name = location_name.replace(' ', '_')
        location_name = location_name.replace("'", '_')
        #
        row_out = dict()
        location_id              = int( row_in['location_id'] )
        row_out['location_id']   = location_id
        row_out['location_name'] = location_name
        row_out['parent_id']     = int( row_in['parent_id'] )
        location_table.append( row_out )
        #
        assert not location_id in location_id_set
        location_id_set.add( location_id )
        #
    return location_table
# ---------------------------------------------------------------------------
# age_group_dict = get_age_group_dict(file_name)
def get_age_group_dict(file_name) :
    file_ptr   = open(file_name)
    reader     = csv.DictReader(file_ptr)
    age_group_dict = dict()
    csv_row_id = 0
    for row_in in reader :
        csv_row_id += 1
        row_out = dict()
        age_group_id                 = int( row_in['age_group_id'] )
        row_out['csv_row_id']        = csv_row_id
        row_out['age_lower']         = float( row_in['age_group_years_start'] )
        row_out['age_upper']         = float( row_in['age_group_years_end'] )
        age_group_dict[age_group_id] = row_out
        #
        age_group_name = row_in['age_group_name']
        if age_group_name in [ 'All ages', 'Age-standardized' ] :
            assert age_group_id in all_age_group_id_list
        else :
            assert age_group_id not in all_age_group_id_list
    return age_group_dict
# ---------------------------------------------------------------------------
# interpolate_covariate  = get_interpolate_covariate(
#   file_name, age_group_dict, one_age_group
# )
def get_interpolate_covariate(file_name, age_group_dict, one_age_group) :
    file_ptr   = open(file_name)
    reader     = csv.DictReader(file_ptr)
    #
    # triple_list
    triple_list = dict()
    #
    # row
    for row in reader :
        #
        # age_group_id
        age_group_id = int( row['age_group_id'] )
        if one_age_group or age_group_id not in all_age_group_id_list :
            #
            # location_id
            location_id = int( row['location_id'] )
            if location_id not in triple_list :
                triple_list[location_id]  = dict()
            #
            # sex
            sex = row['sex']
            if sex not in triple_list[location_id] :
                triple_list[location_id][sex] = list()
            #
            # age
            age_lower    = age_group_dict[age_group_id]['age_lower']
            age_upper    = age_group_dict[age_group_id]['age_upper']
            age          = (age_upper + age_lower) / 2.0
            #
            # time
            time         = int( row['year_id'] ) + 0.5
            #
            # covariate
            covariate    = float( row['mean_value'] )
            #
            # triple_list
            triple = (age, time, covariate)
            triple_list[location_id][sex].append( triple )
    #
    # interpolate_covariate
    interpolate_covariate = dict()
    #
    # location_id
    for location_id in triple_list :
        interpolate_covariate[location_id] = dict()
        # sex
        for sex in triple_list[location_id] :
            #
            # triple_list
            this_list = triple_list[location_id][sex]
            this_list = sorted(this_list)
            triple_list[location_id][sex] = this_list
            #
            # age_grid, time_grid
            age_set  = set()
            time_set = set()
            for triple in this_list :
                age_set.add( triple[0] )
                time_set.add( triple[1] )
            age_grid  = sorted(age_set)
            time_grid = sorted(time_set)
            #
            # n_age, n_time
            n_age  = len(age_grid)
            n_time = len(time_grid)
            #
            if one_age_group :
                assert n_age == 1
                #
                # covariate_grid
                covariate_grid = list()
                for triple in this_list :
                    covariate_grid.append( triple[2] )
                #
                # interpolate_covariate
                spline =  UnivariateSpline(
                    time_grid, covariate_grid, k = 1, s = 0.0, ext = 3
                )
                interpolate_covariate[location_id][sex] = spline
            #
            # 22 and 27 are the all ages groups
            elif age_group_id not in all_age_group_id_list :
                assert n_age > 1
                #
                # covariate_grid
                covariate_grid    = numpy.empty( (n_age, n_time) )
                covariate_grid[:] = numpy.nan
                #
                # covariate_grid
                for (index, triple) in enumerate(this_list) :
                    age        = triple[0]
                    time       = triple[1]
                    #
                    age_index  = int( index / n_time )
                    time_index = index % n_time
                    #
                    assert age  == age_grid[age_index]
                    assert time == time_grid[time_index]
                    covariate_grid[age_index][time_index] = triple[2]
                #
                # interpolate_covariate
                spline= RectBivariateSpline(
                    age_grid, time_grid, covariate_grid, kx=1, ky=1, s=0
                )
                interpolate_covariate[location_id][sex] = spline
            #
    return interpolate_covariate
# ---------------------------------------------------------------------------
# emr_table = get_emr_table(file_name, age_group_dict)
def get_emr_table(file_name, age_group_dict) :
    file_ptr   = open(file_name)
    reader     = csv.DictReader(file_ptr)
    emr_table  = list()
    csv_row_id = 0
    for row_in in reader :
        csv_row_id += 1
        year_id      = float( row_in['year_id'] )
        age_group_id = int( row_in['age_group_id'] )
        lower        = float( row_in['lower'] )
        upper        = float( row_in['upper'] )
        meas_std     = (upper - lower) / 2.0
        sex_id       = int( row_in['sex_id'] )
        sex_name     = None
        for key in sex_name2sex_id :
            if sex_name2sex_id[key] == sex_id :
                sex_name = key
        row_out = dict()
        row_out['csv_row_id']   = csv_row_id
        row_out['location_id']  = int( row_in['location_id'] )
        row_out['sex']          = sex_name
        row_out['time_lower']   = year_id
        row_out['time_upper']   = year_id + 1.0
        row_out['age_lower']    = age_group_dict[age_group_id]['age_lower']
        row_out['age_upper']    = age_group_dict[age_group_id]['age_upper']
        row_out['meas_value']   = float( row_in['mean'] )
        row_out['hold_out']     = 0
        row_out['meas_std']     = meas_std
        row_out['obesity']      = None
        row_out['log_ldi']      = None
        #
        if row_in['measure'] == 'incidence' :
            row_out['integrand']    = 'Sincidence'
        else :
            row_out['integrand']    = row_in['measure']
        #
        if row_out['age_upper'] - row_out['age_lower'] > 50.0 :
            assert age_group_id in all_age_group_id_list
        else :
            emr_table.append( row_out )
    return emr_table
# ---------------------------------------------------------------------------
# data_table = get_data_table(file_name)
def get_data_table(file_name) :
    file_ptr   = open(file_name)
    reader     = csv.DictReader(file_ptr)
    data_table = list()
    csv_row_id = 0
    for row_in in reader :
        # year_end is in demographer notaiton and age_end is not
        csv_row_id += 1
        row_out = dict()
        row_out['csv_row_id']   = csv_row_id
        row_out['location_id']  = int( row_in['location_id'] )
        row_out['sex']          = row_in['sex']
        row_out['time_lower']   = float( row_in['year_start'] )
        row_out['time_upper']   = float( row_in['year_end'] ) + 1.0
        row_out['age_lower']    = float( row_in['age_start'] )
        row_out['age_upper']    = float( row_in['age_end'] )
        row_out['meas_value']   = float( row_in['mean'] )
        row_out['hold_out']     = int( row_in['is_outlier'] )
        row_out['obesity']      = None
        row_out['log_ldi']      = None
        #
        meas_std                = float( row_in['standard_error'] )
        if meas_std <= 0.0 :
            sample_size = float( row_in['sample_size'] )
            meas_value  = row_out['meas_value']
            std_5 = math.sqrt( meas_value / sample_size )
            if meas_value * sample_size < 5.0 :
                std_0 = 1.0 / sample_size
                meas_std  = (5.0 - meas_value * sample_size) * std_0
                meas_std += meas_value * sample_size * std_5
                meas_std  = meas_std / 5.0
        row_out['meas_std']     = meas_std
        #
        if row_in['measure'] == 'incidence' :
            row_out['integrand']    = 'Sincidence'
        else :
            row_out['integrand']    = row_in['measure']
        #
        data_table.append( row_out )
    return data_table
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
def create_csv_info_files() :
    print('begin create_csv_info_files')
    #
    # age_group_dict
    age_group_dict = get_age_group_dict(age_group_table_csv)
    #
    # data_table
    data_table = get_data_table(data_table_csv)
    #
    # emr_table
    emr_table     = get_emr_table(emr_table_csv, age_group_dict)
    #
    # data_table
    assert set( data_table[0].keys() ) == set( emr_table[0].keys() )
    data_table += emr_table
    #
    # location_table
    location_table = get_location_table(location_table_csv)
    #
    # interpolate_obesity
    one_age_group = False
    interpolate_obesity  = get_interpolate_covariate(
        obesity_table_csv, age_group_dict, one_age_group
    )
    #
    # interpolate_ldi
    one_age_group = True
    interpolate_ldi  = get_interpolate_covariate(
        ldi_table_csv, age_group_dict, one_age_group
    )
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
        age             = (row['age_lower']  + row['age_upper']) / 2.0
        time            = (row['time_lower'] + row['time_upper']) / 2.0
        #
        # log_ldi, hold_out
        if location_id in interpolate_ldi :
            ldi             = interpolate_ldi[location_id]['Both'](time)
            row['log_ldi']  = math.log10( ldi )
        else :
            row['log_ldi']  = None
            row['hold_out'] = 1
        #
        # obesito, hold_out
        if location_id in interpolate_obesity :
            if sex == 'Both' :
                assert sex not in interpolate_obesity[location_id]
                fun    = interpolate_obesity[location_id]['Male']
                male   = fun(age, time, grid = False)
                fun    = interpolate_obesity[location_id]['Female']
                female = fun(age, time, grid = False)
                obesity  = ( male + female ) / 2.0
            else :
                fun     = interpolate_obesity[location_id][sex]
                obesity = fun(age, time, grid = False)
            row['obesity'] = obesity
        else :
            row['obesity']  = None
            row['hold_out'] = 1
    #
    # change location_id to node_id
    for row in data_table :
        location_id      = row['location_id']
        node_id          = location_id2node_id[location_id]
        row['node_id']   = node_id
        del row['location_id']
    #
    # create data_table_info
    write_csv(data_table_info, data_table)
    #
    # node_table
    node_table      = list()
    node_name_set   = set()
    double_name_set = set()
    for (node_id, row_in) in enumerate(location_table) :
        location_name        = row_in['location_name']
        location_id          = row_in['location_id']
        parent_location_id   = row_in['parent_id']
        if parent_location_id == location_id :
            parent_node_id = None
        else :
            parent_node_id = location_id2node_id[parent_location_id]
        row_out = dict()
        row_out['node_id']       = node_id
        row_out['node_name']     = location_name
        row_out['parent']        = parent_node_id
        row_out['location_id']   = location_id
        node_table.append(row_out)
        #
        # double_name_set
        if location_name in node_name_set :
            double_name_set.add( location_name )
        #
        # node_name_set
        node_name_set.add( location_name )
    #
    # location_name
    for location_name in double_name_set :
        # row
        for row in node_table :
            if row['node_name'] == location_name :
                # add parent to node_name for this row
                parent           = row['parent']
                node_name        = f'{location_name}_{parent}'
                row['node_name'] = node_name
    #
    # create node_table_info
    write_csv(node_table_info, node_table)
    #
    print('end create_csv_info_files')
# -----------------------------------------------------------------------------
def get_table_csv(file_name) :
    file_ptr   = open(file_name)
    reader     = csv.DictReader(file_ptr)
    table      = list()
    for row in reader :
        table.append(row)
    return table
# ---------------------------------------------------------------------------
def create_root_node_database(file_name, other_age_table, other_time_table) :
    #
    # csv_data_table, csv_node_table
    csv_data_table = get_table_csv( data_table_info )
    csv_node_table = get_table_csv( node_table_info )
    #
    # integrand_median
    integrand_list = dict()
    for row in csv_data_table :
        integrand = row['integrand']
        if integrand not in integrand_list :
            integrand_list[integrand] = list()
        integrand_list[integrand].append( float(row['meas_value']) )
    integrand_median = dict()
    for integrand in integrand_list :
        integrand_median[integrand] = \
            statistics.median( integrand_list[integrand] )
    #
    # subgroup_table
    subgroup_table = [ {'subgroup': 'world', 'group':'world'} ]
    #
    # age_list
    age_list = list()
    for row in other_age_table :
        age_list.append( row['age'] )
    #
    # age_list, grid_age_id
    grid_age_id = list()
    age_grid    = [
        0.0, 5.0, 10.0, 15.0, 20.0,
        30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0
    ]
    for age in age_grid :
        if age in age_list :
            grid_age_id.append( age_list.index(age) )
        else :
            grid_age_id.append( len(age_list) )
            age_list.append( age )
    #
    # time_list
    time_list = list()
    for row in other_time_table :
        time_list.append( row['time'] )
    #
    # time_list, grid_time_id
    grid_time_id = list()
    time_grid   = [ 1960, 1975, 1990, 1995, 2000, 2005, 2010, 2015, 2020 ]
    for time in time_grid :
        if time in time_list :
            grid_time_id.append( time_list.index(time) )
        else :
            grid_time_id.append( len(time_list) )
            time_list.append( time )
    #
    # ensure all data is with in age and time limits
    age_min =   math.inf
    age_max = - math.inf
    time_min =  math.inf
    time_max = - math.inf
    for row in csv_data_table :
        age_min  = min(age_min,  float( row['age_lower'] ) )
        time_min = min(time_min, float( row['time_lower'] ) )
        age_max  = max(age_max,  float( row['age_upper'] ) )
        time_max = max(time_max, float( row['time_upper'] ) )
    if age_min < min( age_list ) :
        age_list.append( age_min )
    if age_max > max( age_list ) :
        age_list.append( age_max )
    if time_min < min( time_list ) :
        time_list.append( time_min )
    if time_max > max( time_list ) :
        time_list.append( time_max )
    #
    # mulcov_table
    mulcov_table = [
        {
            # alpha_iota_obesity
            'covariate': 'obesity',
            'type':      'rate_value',
            'effected':  'iota',
            'group':     'world',
            'smooth':    'alpha_smooth',
        },{
            # alpha_iota_sex
            'covariate': 'sex',
            'type':      'rate_value',
            'effected':  'iota',
            'group':     'world',
            'smooth':    'alpha_smooth',
        },{
            # alpha_chi_log_ldi
            'covariate': 'log_ldi',
            'type':      'rate_value',
            'effected':  'chi',
            'group':     'world',
            'smooth':    'alpha_smooth',
        },{
            # alpha_chi_sex
            'covariate': 'sex',
            'type':      'rate_value',
            'effected':  'chi',
            'group':     'world',
            'smooth':    'alpha_smooth',
        }
    ]
    for integrand in integrand_median :
        mulcov_table.append(
            {   # gamma_integrand
                'covariate':  'one',
                'type':       'meas_noise',
                'effected':   integrand,
                'group':      'world',
                'smooth':     f'gamma_{integrand}',
            }
        )
    #
    # integrand_table
    integrand_table = list()
    for integrand_name in integrand_name2measure_id :
        row = { 'name' : integrand_name, 'minimum_meas_cv' : '0.1' }
        integrand_table.append( row )
    for j in range( len(mulcov_table) ) :
        integrand_table.append( { 'name' : f'mulcov_{j}' } )
    #
    # node_table
    node_table = list()
    for (node_id, row) in enumerate(csv_node_table) :
        parent         = row['parent']
        if parent == '' :
            parent_name = ''
        else :
            parent_node_id = int( parent )
            parent_name    =  csv_node_table[parent_node_id]['node_name']
        node_table.append({ 'name':row['node_name'], 'parent':parent_name })
    #
    # covarite_table
    # Becasue we are using data4cov_reference, the reference for obesity and
    # log_ldi will get replaced (because they are relative covariates).
    covariate_table = [
        { 'name':'sex',     'reference':0.0, 'max_difference':0.6},
        { 'name':'one',     'reference':0.0 },
        { 'name':'obesity', 'reference':0.0},
        { 'name':'log_ldi', 'reference':0.0},
    ]
    #
    # data_table
    data_table = list()
    for row_in in csv_data_table :
        node_id   = int( row_in['node_id'] )
        node_name = node_table[node_id]['name']
        sex       = sex_name2covariate_value[ row_in['sex'] ]
        if row_in['obesity'] == '' :
            obesity = None
        else :
            obesity = float( row_in['obesity'] )
        if row_in['log_ldi'] == '' :
            log_ldi = None
        else :
            log_ldi = float( row_in['log_ldi'] )
        row_out  = {
            'integrand'       : row_in['integrand'],
            'node'            : node_name,
            'subgroup'        : 'world',
            'weight'          : '',
            'age_lower'       : float( row_in['age_lower'] ),
            'age_upper'       : float( row_in['age_upper'] ),
            'time_lower'      : float( row_in['time_lower'] ),
            'time_upper'      : float( row_in['time_upper'] ),
            'sex'             : sex,
            'one'             : 1.0,
            'obesity'         : obesity,
            'log_ldi'         : log_ldi,
            'hold_out'        : int( row_in['hold_out'] ),
            'density'         : 'gaussian',
            'meas_value'      : float( row_in['meas_value'] ),
            'meas_std'        : float( row_in['meas_std'] ),
            'csv_row_id'      : int( row_in['csv_row_id'] ),
        }
        data_table.append( row_out )
    #
    # prior_table
    prior_table = [
        {
            'name'    :    'parent_rate_value',
            'density' :    'log_gaussian',
            'lower'   :    1e-7,
            'upper'   :    1.0,
            'mean'    :    1e-2,
            'std'     :    1.0,
            'eta'     :    1e-7,
        },{
            'name'    :    'parent_pini_value',
            'density' :    'gaussian',
            'lower'   :    0.0,
            'upper'   :    1e-4,
            'mean'    :    1e-5,
            'std'     :    1.0,
        },{
            'name'    :    'parent_rate_delta',
            'density' :    'log_gaussian',
            'lower'   :    None,
            'upper'   :    None,
            'mean'    :    0.0,
            'std'     :    0.20,
            'eta'     :    1e-7,
        },{
            'name'    :   'child_rate_value',
            'density' :   'gaussian',
            'lower'   :   None,
            'upper'   :   None,
            'mean'    :   0.0,
            'std'     :   1.0,
        },{
            'name'    :   'alpha_value',
            'density' :   'gaussian',
            'lower'   :   None,
            'upper'   :   None,
            'mean'    :   0.0,
            'std'     :   1.0,
        }
    ]
    for integrand in integrand_median :
        gamma = gamma_factor * integrand_median[integrand]
        prior_table.append(
            {
                'name'    :   f'gamma_{integrand}',
                'density' :   'uniform',
                'lower'   :   gamma,
                'upper'   :   gamma,
                'mean'    :   gamma,
            }
        )
    # ------------------------------------------------------------------------
    # smooth_table
    smooth_table = list()
    #
    # parrent_smooth
    fun = lambda a, t :  \
        ('parent_rate_value', 'parent_rate_delta', 'parent_rate_delta')
    smooth_table.append({
        'name':     'parent_rate',
        'age_id':   grid_age_id,
        'time_id':  grid_time_id,
        'fun':      fun
    })
    fun = lambda a, t :  \
        ('parent_pini_value', None, None)
    smooth_table.append({
        'name':     'parent_pini',
        'age_id':   [0],
        'time_id':  [0],
        'fun':      fun
    })
    #
    # child_smooth
    fun = lambda a, t : ('child_rate_value', None, None)
    smooth_table.append({
         'name':    'child_smooth',
        'age_id':   [0],
        'time_id':   [0],
        'fun':       fun
    })
    #
    # alpha_smooth
    fun = lambda a, t : ('alpha_value', None, None)
    smooth_table.append({
        'name':    'alpha_smooth',
        'age_id':   [0],
        'time_id':   [0],
        'fun':       fun
    })
    #
    # gamma_integrand
    for integrand in integrand_median :
        # fun = lambda a, t : ('gamma_{integrand}', None, None) )
        fun = eval( f"lambda a, t : ( 'gamma_{integrand}', None, None)" )
        smooth_table.append({
            'name':    f'gamma_{integrand}',
            'age_id':   [0],
            'time_id':  [0],
            'fun':      copy.copy(fun)
        })
    #
    # rate_table
    rate_table = [
        {
            'name':          'pini',
            'parent_smooth': 'parent_pini',
            'child_smooth':  None,
        },{
            'name':           'iota',
            'parent_smooth': 'parent_rate',
            'child_smooth':  'child_smooth',
        },{
            'name':           'chi',
            'parent_smooth': 'parent_rate',
            'child_smooth':  'child_smooth',
        }
    ]
    #
    # option_table
    option_table = [
        { 'name':'parent_node_name',     'value':root_node_name},
        { 'name':'zero_sum_child_rate',  'value':'iota chi'},
        { 'name':'random_seed',          'value':str(random_seed)},
        { 'name':'trace_init_fit_model', 'value':'true'},
        { 'name':'data_extra_columns',   'value':'csv_row_id'},
        { 'name':'meas_noise_effect',    'value':'add_std_scale_none'},
        { 'name':'age_avg_split',        'value':'0.1 1.0'},
        #
        { 'name':'quasi_fixed',                  'value':'false' },
        { 'name':'tolerance_fixed',              'value':'1e-8'},
        { 'name':'max_num_iter_fixed',           'value':'35'},
        { 'name':'print_level_fixed',            'value':'5'},
        { 'name':'accept_after_max_steps_fixed', 'value':'10'},
    ]
    # Diabetes does not have enough incidence data to estimate
    # both iota and chi without mtexcess. Also see the minimum_cv setting
    # for mtexcess in the integand table.
    # { 'name':'hold_out_integrand',   'value':'mtexcess'},
    #
    # create_database
    nslist_table   = list()
    avgint_table   = list()
    weight_table   = list()
    dismod_at.create_database(
         file_name,
         age_list,
         time_list,
         integrand_table,
         node_table,
         subgroup_table,
         weight_table,
         covariate_table,
         avgint_table,
         data_table,
         prior_table,
         smooth_table,
         nslist_table,
         rate_table,
         mulcov_table,
         option_table
    )
# ---------------------------------------------------------------------------
def create_all_node_database(all_node_database, root_node_database) :
    #
    # all_node_database
    shutil.copyfile(all_node_other, all_node_database)
    #
    # node_table
    new        = False
    connection = dismod_at.create_connection(root_node_database, new)
    node_table = dismod_at.get_table_dict(connection, 'node')
    connection.close()
    #
    # connection
    new        = False
    connection = dismod_at.create_connection(all_node_database, new)
    #
    # mtall_index, mtspecific_index
    # Change sex_id -> split_reference_id and map its values
    # 2 -> 0 (Female), 3 -> 1 (both), 1 -> 2 (Male)
    split_map = { 1:2, 2:0, 3:1}
    for tbl_name in [ 'mtall_index', 'mtspecific_index' ] :
        command  = 'ALTER TABLE ' + tbl_name + ' '
        command += 'RENAME COLUMN sex_id TO split_reference_id'
        dismod_at.sql_command(connection, command)
        #
        this_table = \
            dismod_at.get_table_dict(connection, tbl_name)
        for row in this_table :
            split_reference_id = split_map[ row['split_reference_id'] ]
            row['split_reference_id'] = split_reference_id
        dismod_at.replace_table( connection, tbl_name, this_table)
    #
    # split_reference table
    tbl_name = 'split_reference'
    col_name = [ 'split_reference_name', 'split_reference_value' ]
    col_type = [ 'text',                 'real']
    row_list = list()
    for sex_name in sex_name2covariate_value :
        row = [ sex_name , sex_name2covariate_value[sex_name] ]
        row_list.append( row )
    dismod_at.create_table(connection, tbl_name, col_name, col_type, row_list)
    #
    # node_split table
    tbl_name = 'node_split'
    col_name = [ 'node_id' ]
    col_type = [ 'integer' ]
    row_list = list()
    for node_name in split_fit_set :
        node_id = at_cascade.table_name2id(node_table, 'node', node_name)
        row_list.append( [ node_id ] )
    dismod_at.create_table(connection, tbl_name, col_name, col_type, row_list)
    #
    # connection
    connection.close()
    #
    # all_option_table (needed by data4cov_reference)
    set_all_option_table(all_node_database)
    #
    # all_cov_reference table
    at_cascade.data4cov_reference(
        root_node_database = root_node_database,
        all_node_database  = all_node_database  ,
        trace_interval     = 100,
    )
# ---------------------------------------------------------------------------
def display_results(database, plot_title) :
    #
    # pdf_file
    index      = database.rfind('/')
    pdf_dir    = database[0:index]
    #
    # integrand_table, rate_table
    new             = False
    connection      = dismod_at.create_connection(database, new)
    integrand_table = dismod_at.get_table_dict(connection, 'integrand')
    rate_table      = dismod_at.get_table_dict(connection, 'rate')
    #
    # data.pdf
    pdf_file = pdf_dir + '/data.pdf'
    n_point_list = dismod_at.plot_data_fit(
        database = database,
        pdf_file          = pdf_file,
        plot_title        = plot_title,
        max_plot          = max_plot,
    )
    #
    # rate.pdf
    rate_set = set()
    for row in rate_table :
        if not row['parent_smooth_id'] is None :
            rate_set.add( row['rate_name'] )
    pdf_file = pdf_dir + '/rate.pdf'
    plot_set = dismod_at.plot_rate_fit(
        database, rate_set, pdf_file, plot_title
    )
    #
    # db2csv
    dismod_at.system_command_prc([ 'dismodat.py', database, 'db2csv' ])
# ---------------------------------------------------------------------------
def replace_relative_covariate_reference(
        all_node_database, root_node_database
) :
    #
    # all_option_table, all_cov_reference_table, split_reference_table
    new               = False
    connection        = dismod_at.create_connection(all_node_database, new)
    all_option_table  = dismod_at.get_table_dict(connection, 'all_option')
    all_cov_reference_table = dismod_at.get_table_dict(
        connection, 'all_cov_reference'
    )
    split_reference_table = dismod_at.get_table_dict(
        connection, 'split_reference'
    )
    connection.close()
    #
    # covariate_table, option_table
    new             = False
    connection      = dismod_at.create_connection(root_node_database, new)
    covariate_table = dismod_at.get_table_dict(connection, 'covariate')
    option_table    = dismod_at.get_table_dict(connection, 'option')
    node_table      = dismod_at.get_table_dict(connection, 'node')
    connection.close()
    #
    # cov_info
    cov_info = at_cascade.get_cov_info(
        all_option_table, covariate_table, split_reference_table
    )
    #
    # parent_node_id
    parent_node_name = None
    for row in option_table :
        if row['option_name'] == 'parent_node_name' :
            parent_node_name = row['option_value']
    assert not parent_node_name is None
    parent_node_id = at_cascade.table_name2id(
        node_table, 'node', parent_node_name
    )
    # covriate_table
    for row in all_cov_reference_table :
        node_id            = row['node_id']
        covariate_id       = row['covariate_id']
        split_reference_id = row['split_reference_id']
        reference          = row['reference']
        if split_reference_id == cov_info['split_reference_id'] \
            and node_id == parent_node_id :
                covariate_table[covariate_id]['reference'] = reference
    new             = False
    connection      = dismod_at.create_connection(root_node_database, new)
    dismod_at.replace_table(connection, 'covariate', covariate_table)
    connection.close()
# ---------------------------------------------------------------------------
def set_all_option_table(all_node_database) :
    #
    # all_option_table
    max_abs_effect_str = str( max_abs_effect )
    all_option_table  = [
    {'option_name': 'absolute_covariates',    'option_value':'one'},
    {'option_name': 'in_parallel',            'option_value':'false'},
    {'option_name': 'split_covariate_name',   'option_value':'sex'},
    #
    {'option_name': 'max_abs_effect',   'option_value':max_abs_effect_str},
    {'option_name': 'max_fit',          'option_value':str(max_fit)},
    {'option_name': 'root_node_name',   'option_value':root_node_name},
    {   'option_name':  'shift_prior_std_factor',
        'option_value': str(shift_prior_std_factor)
    },
    ]
    new               = False
    connection        = dismod_at.create_connection(all_node_database, new)
    dismod_at.replace_table(connection, 'all_option', all_option_table)
    connection.close()
# ---------------------------------------------------------------------------
def drill() :
    #
    # root_node_database
    root_node_database = 'root_node.db'
    #
    # all_node_database
    all_node_database = 'all_node.db'
    #
    # other_age_table, other_time_table
    new        = False
    connection = dismod_at.create_connection(root_node_other, new)
    other_age_table  = dismod_at.get_table_dict(connection, 'age')
    other_time_table = dismod_at.get_table_dict(connection, 'time')
    connection.close()
    #
    # extract info from raw csv files
    if os.path.exists(data_table_info) and os.path.exists(node_table_info) :
        print(f'using existing {data_table_info} and {node_table_info}')
    else :
        create_csv_info_files()
    #
    # create root_node.db
    create_root_node_database(
        root_node_database, other_age_table, other_time_table
    )
    #
    # create all_node.db
    if not os.path.exists(all_node_database) :
        print(f'creating {all_node_database}')
        create_all_node_database(all_node_database, root_node_database)
    else :
        print(f'using existing {all_node_database}')
        replace_relative_covariate_reference(
            all_node_database, root_node_database
        )
    #
    # set_all_option_table
    set_all_option_table(all_node_database)
    #
    # no_ode_fit
    fit_node_database = at_cascade.no_ode_fit(
        all_node_database = all_node_database,
        in_database       = root_node_database,
        max_fit           = max_fit,
        max_abs_effect    = max_abs_effect,
        trace_fit         = True,
    )
    assert fit_node_database == root_node_name + '/dismod.db'
    #
    # display_results
    database =  root_node_name + '/no_ode/dismod.db'
    plot_title = root_node_name + '/no_ode'
    display_results(database, plot_title)
    #
    # cascade starting at root node
    if True :
        at_cascade.cascade_fit_node(
            all_node_database = all_node_database,
            fit_node_database = fit_node_database,
            fit_goal_set      = fit_goal_set,
            trace_fit         = True,
        )
# ---------------------------------------------------------------------------
# create_ihme_results_node( fit_node_database )
def create_ihme_results_node(
    fit_node_database   = None ,
    age_group_dict      = None ,
    interpolate_obesity = None ,
    interpolate_ldi     = None ,
) :
    assert fit_node_database is not None
    assert age_group_dict is not None
    assert interpolate_obesity is not None
    assert interpolate_ldi is not None
    #
    # fit_node_dir
    assert fit_node_database.endswith('/dismod.db')
    index        = fit_node_database.rfind('/')
    fit_node_dir = fit_node_database[0:index]
    #
    print(fit_node_dir)
    #
    # integrand_table, age_table, time_table
    new        = False
    connection      = dismod_at.create_connection(fit_node_database, new)
    integrand_table = dismod_at.get_table_dict(connection, 'integrand')
    age_table       = dismod_at.get_table_dict(connection, 'age')
    time_table      = dismod_at.get_table_dict(connection, 'time')
    covariate_table = dismod_at.get_table_dict(connection, 'covariate')
    connection.close()
    #
    # all_option_table, split_reference_table
    all_node_database = 'all_node.db'
    new               = False
    connection        = dismod_at.create_connection(all_node_database, new)
    all_option_table  = dismod_at.get_table_dict(connection, 'all_option')
    split_reference_table = \
        dismod_at.get_table_dict(connection, 'split_reference')
    connection.close()
    #
    # split_reference_id
    cov_info = at_cascade.get_cov_info(
        all_option_table, covariate_table, split_reference_table
    )
    split_reference_id    = cov_info['split_reference_id']
    #
    # integrand_id_list
    integrand_id_list = list()
    for integrand_name in integrand_name2measure_id :
        integrand_id = at_cascade.table_name2id(
            integrand_table, 'integrand', integrand_name
        )
        integrand_id_list.append( integrand_id )
    #
    # year_grid
    # year_id is output file is in demographer notation
    year_grid = [ 1990.5, 1995.5, 2000.5, 2005.5, 2010.5, 2015.5, 2020.5 ]
    #
    # age_group_dict
    age_group_dict = get_age_group_dict(age_group_table_csv)
    #
    # age_group_id_list
    age_group_id_list = list()
    for age_group_id in age_group_dict :
        if age_group_id not in all_age_group_id_list :
            age_group_id_list.append( age_group_id )
    #
    # fit_node_name
    fit_node_name   = at_cascade.get_parent_node(fit_node_database)
    #
    # fit_node_id, location_id
    node_info_table = get_table_csv( node_table_info )
    location_id     = None
    fit_node_id     = None
    for row in node_info_table :
        if row['node_name'] == fit_node_name :
            location_id = int( row['location_id'] )
            fit_node_id = int( row['node_id'] )
    assert location_id is not None
    assert fit_node_id is not None
    #
    # output_csv
    output_csv = f'{fit_node_dir}/ihme.csv'
    print('ihme.csv')
    #
    # avgint_table
    avgint_table = list()
    #
    # sex
    sex = split_reference_table[split_reference_id]['split_reference_value']
    #
    # sex_name
    sex_name = \
        split_reference_table[split_reference_id]['split_reference_name']
    #
    # sex_id
    sex_id = sex_name2sex_id[sex_name]
    #
    # obesity_fun_male
    obesity_fun_male = interpolate_obesity[location_id]['Male']
    #
    # obesity_fun_female
    obesity_fun_female = interpolate_obesity[location_id]['Female']
    #
    # ldi_fun
    ldi_fun = interpolate_ldi[location_id]['Both']
    #
    # age_index
    for age_index in range( len(age_group_id_list) ) :
        #
        # age_group_id
        age_group_id = age_group_id_list[age_index]
        #
        # age_lower, age_upper, age
        age_lower = age_group_dict[age_group_id]['age_lower']
        age_upper = age_group_dict[age_group_id]['age_upper']
        age       = (age_lower + age_upper) / 2.0
        #
        # time
        for time in year_grid :
            #
            # obesity
            if sex_name == 'Male' :
                obesity = obesity_fun_male(age, time, grid = False)
            elif sex_name == 'Female' :
                obesity = obesity_fun_female(age, time, grid = False)
            else :
                obesity  = obesity_fun_male(age, time, grid = False)
                obesity += obesity_fun_female(age, time, grid = False)
                obesity /= 2.0
            #
            # log_ldi
            ldi     = ldi_fun(time)
            log_ldi = math.log10( ldi )
            #
            for integrand_id in integrand_id_list :
                #
                # row
                # Covariates are in same order as covariate_table in the
                # create_root_node_database routine above.
                row = {
                    'integrand_id'    : integrand_id,
                    'node_id'         : fit_node_id,
                    'subgroup_id'     : 0,
                    'weight_id'       : None,
                    'age_lower'       : age_lower,
                    'age_upper'       : age_upper,
                    'time_lower'      : time,
                    'time_upper'      : time,
                    'x_0'             : sex,
                    'x_1'             : 1.0,
                    'x_2'             : obesity,
                    'x_3'             : log_ldi,
                    'c_age_group_id'  : age_group_id,
                }
                avgint_table.append( row )
    #
    # avgint_table
    new        = False
    connection = dismod_at.create_connection(fit_node_database, new)
    dismod_at.replace_table(connection, 'avgint', avgint_table)
    connection.close()
    #
    # predict sample
    print( 'sample' )
    command = [ 'dismod_at', fit_node_database, 'predict', 'sample' ]
    dismod_at.system_command_prc(command, print_command = False )
    #
    # db2csv
    print( 'db2csv' )
    dismod_at.db2csv_command(fit_node_database)
    #
    # rate.pdf
    pdf_file = f'{fit_node_dir}/rate.pdf'
    print( 'rate.pdf' )
    plot_title = f'{fit_node_name}.{sex_name}'
    rate_set   = { 'iota', 'chi', 'omega' }
    dismod_at.plot_rate_fit(
        fit_node_database, rate_set, pdf_file, plot_title
    )
    #
    # data.pdf
    pdf_file = f'{fit_node_dir}/data.pdf'
    print( 'data.pdf' )
    plot_title = f'{fit_node_name}.{sex_name}'
    dismod_at.plot_data_fit(
        database   = fit_node_database,
        pdf_file   = pdf_file,
        plot_title = plot_title,
        max_plot   = max_plot,
    )
    #
    # predict_table
    new           = False
    connection    = dismod_at.create_connection(fit_node_database, new)
    predict_table = dismod_at.get_table_dict(connection, 'predict')
    connection.close()
    #
    # n_sample
    assert len(predict_table) % len(avgint_table) == 0
    n_sample = int( len(predict_table) / len(avgint_table) )
    #
    # n_avgint
    n_avgint = len( avgint_table )
    #
    # output_table
    output_table = list()
    #
    # plot_data
    plot_data = dict()
    #
    # avgint_row
    for (avgint_id, avgint_row) in enumerate( avgint_table ) :
        #
        # measure_id
        integrand_id    = avgint_row['integrand_id']
        integrand_name  = integrand_table[integrand_id]['integrand_name']
        measure_id      = integrand_name2measure_id[integrand_name]
        #
        x_0 = avgint_row['x_0']
        assert x_0 == sex
        #
        # obesity
        obesity = avgint_row['x_2']
        #
        # ldi
        log_ldi = avgint_row['x_3']
        ldi     = math.exp( math.log(10.0) * log_ldi )
        #
        # plot_data[integrand_name]
        if integrand_name not in plot_data :
            plot_data[integrand_name] = list()
        #
        # age_group_id
        age_group_id  = avgint_row['c_age_group_id']
        #
        # year_id
        assert avgint_row['time_lower'] == avgint_row['time_upper']
        year_id = int( avgint_row['time_lower'] )
        #
        # avg_integrand_list
        avg_integrand_list = list()
        #
        # sample_index
        for sample_index in range( n_sample ) :
            #
            # predict_row
            predict_id = sample_index * n_avgint + avgint_id
            predict_row = predict_table[predict_id]
            #
            # some checks
            assert sample_index  == predict_row['sample_index']
            assert avgint_id     == predict_row['avgint_id']
            #
            # avg_integrand
            avg_integrand = predict_row['avg_integrand']
            avg_integrand_list.append( avg_integrand )
        #
        # row
        row = {
            'location_id'    : location_id,
            'sex_id'         : sex_id,
            'obesity'        : obesity,
            'ldi'            : ldi,
            'age_group_id'   : age_group_id,
            'year_id'        : year_id,
            'measure_id'     : measure_id,
        }
        for sample_index in range( n_sample ) :
            key = f'draw_{sample_index}'
            row[key] = avg_integrand_list[sample_index]
        #
        # output_table
        output_table.append(row)
        #
        # row
        mean      = numpy.mean( avg_integrand_list )
        std       = numpy.std( avg_integrand_list, ddof = 1 )
        age_lower = age_group_dict[age_group_id]['age_lower']
        age_upper = age_group_dict[age_group_id]['age_upper']
        age       = (age_lower + age_upper) / 2.0
        time      = avgint_row['time_lower']
        row = {
            'age'   : age,
            'time'  : time,
            'value' : mean,
            'std'   : std,
        }
        #
        # plot_data[integrand_name]
        plot_data[integrand_name].append( row )
    #
    # z_name
    z_list = list( plot_data.keys() )
    for z_name in z_list :
        #
        # max_std, max_value
        max_std   = 0.0
        max_value = 0.0
        for row in plot_data[z_name] :
            max_value = max(max_value, row['std'])
            max_std   = max(max_std, row['std'])
        #
        if max_value == 0.0 :
            # remove both plots for this integrand
            del plot_data[z_name]
        #
        elif max_std == 0.0 :
            # remove std plot for this integrand
            for row in plot_data[z_name] :
                del row['std']
    #
    # output_csv
    write_csv(output_csv, output_table)
    #
    # plot_limit
    age_min = min(  [ row['age']  for row in age_table  ] )
    age_max = max(  [ row['age']  for row in age_table  ] )
    time_min = min( [ row['time'] for row in time_table ] )
    time_max = max( [ row['time'] for row in time_table ] )
    plot_limit = {
        'age_min'  : age_min,
        'age_max'  : age_max,
        'time_min' : time_min,
        'time_max' : time_max,
    }
    #
    # ihme.pdf
    pdf_file = f'{fit_node_dir}/ihme.pdf'
    print( 'ihme.pdf' )
    plot_title = f'{fit_node_name}.{sex_name}'
    dismod_at.plot_curve(
        pdf_file   = pdf_file      ,
        plot_limit = plot_limit      ,
        plot_title = plot_title      ,
        plot_data  = plot_data       ,
    )
# ---------------------------------------------------------------------------
def create_ihme_results(
    fit_node_database   = None ,
    fit_children        = None ,
    age_group_dict      = None ,
    interpolate_obesity = None ,
    interpolate_ldi     = None ,
) :
    assert fit_node_database is not None
    #
    # root_node_database
    root_node_database = 'root_node.db'
    #
    # all_node_database
    all_node_database = 'all_node.db'
    #
    # node_table
    new        = False
    connection = dismod_at.create_connection(root_node_database, new)
    node_table = dismod_at.get_table_dict(connection, 'node')
    connection.close()
    #
    # split_reference_table
    new        = False
    connection            = dismod_at.create_connection(all_node_database, new)
    split_reference_table = \
        dismod_at.get_table_dict(connection, 'split_reference')
    #
    # fit_children
    if fit_children is None :
        #
        # root_node_name
        root_node_name = at_cascade.get_parent_node(root_node_database)
        #
        # root_node_id
        root_node_id = at_cascade.table_name2id(
            node_table, 'node', root_node_name
        )
        #
        # fit_children
        fit_children = at_cascade.get_fit_children(
            root_node_id = root_node_id ,
            fit_goal_set = fit_goal_set ,
            node_table   = node_table   ,
        )
    #
    # age_group_dict
    if age_group_dict is None :
        age_group_dict = get_age_group_dict(age_group_table_csv)
    #
    # both
    if interpolate_obesity is None :
        one_age_group = False
        interpolate_obesity  = get_interpolate_covariate(
            obesity_table_csv, age_group_dict, one_age_group
        )
    #
    # interpolate_ldi
    if interpolate_ldi is None :
        one_age_group = True
        interpolate_ldi  = get_interpolate_covariate(
            ldi_table_csv, age_group_dict, one_age_group
        )
    #
    # fit_node_id
    fit_node_name = at_cascade.get_parent_node(fit_node_database)
    fit_node_id   = at_cascade.table_name2id(
        node_table, 'node', fit_node_name
    )
    #
    # location_id
    node_info_table = get_table_csv( node_table_info )
    location_id = int( node_info_table[fit_node_id]['location_id'] )
    if location_id in interpolate_obesity and location_id in interpolate_ldi :
        # can only compute resutls when have relative covariate values
        #
        # fit_node results
        create_ihme_results_node(
            fit_node_database   = fit_node_database   ,
            age_group_dict      = age_group_dict      ,
            interpolate_obesity = interpolate_obesity ,
            interpolate_ldi     = interpolate_ldi     ,
        )
    #
    # fit_node_dir
    index = fit_node_database.find('/dismod.db')
    fit_node_dir = fit_node_database[0 : index]
    #
    # shift_name_list
    shift_name_list = list()
    for row in split_reference_table :
        shift_name = row['split_reference_name']
        dir_name   = f'{fit_node_dir}/{shift_name}'
        if os.path.isdir(dir_name) :
            shift_name_list.append( shift_name )
    if len(shift_name_list) == 0 :
        for child_node_id in fit_children[fit_node_id] :
            shift_name = node_table[child_node_id]['node_name']
            shift_name_list.append( shift_name )
    #
    # results at next level
    for shift_name in shift_name_list :
        shift_node_database = f'{fit_node_dir}/{shift_name}/dismod.db'
        create_ihme_results(
            fit_node_database   = shift_node_database   ,
            fit_children        = fit_children          ,
            age_group_dict      = age_group_dict        ,
            interpolate_obesity = interpolate_obesity   ,
            interpolate_ldi     = interpolate_ldi       ,
        )
# ----------------------------------------------------------------------------
def copy_ihme_results(
    fit_node_database = None ,
    fit_children      = None ,
    date              = None ,
) :
    assert fit_node_database is not None
    #
    if date is None :
        date = str( datetime.date.today() ).replace('-', '.')
    #
    # root_node_database
    root_node_database = 'root_node.db'
    #
    # all_node_database
    all_node_database = 'all_node.db'
    #
    # node_table
    new        = False
    connection = dismod_at.create_connection(root_node_database, new)
    node_table = dismod_at.get_table_dict(connection, 'node')
    connection.close()
    #
    # split_reference_table
    new        = False
    connection            = dismod_at.create_connection(all_node_database, new)
    split_reference_table = \
        dismod_at.get_table_dict(connection, 'split_reference')
    #
    # fit_children
    if fit_children is None :
        #
        # root_node_name
        root_node_name = at_cascade.get_parent_node(root_node_database)
        #
        # root_node_id
        root_node_id = at_cascade.table_name2id(
            node_table, 'node', root_node_name
        )
        #
        # fit_children
        fit_children = at_cascade.get_fit_children(
            root_node_id = root_node_id ,
            fit_goal_set = fit_goal_set ,
            node_table   = node_table   ,
        )
    #
    # fit_node_id
    fit_node_name = at_cascade.get_parent_node(fit_node_database)
    fit_node_id   = at_cascade.table_name2id(
        node_table, 'node', fit_node_name
    )
    #
    # fit_node_dir
    index = fit_node_database.find('/dismod.db')
    fit_node_dir = fit_node_database[0 : index]
    #
    # to_dir
    to_dir = f'{ihme_output_dir}/{date}'
    if not os.path.exists(to_dir) :
        os.makedirs(to_dir)
    #
    # sex
    sex_name = 'Both'
    for name in [ 'Female', 'Male' ] :
        if 0 < fit_node_dir.find(name) :
            sex_name = name
    #
    # check if ihme results have been computed for this node
    if not os.path.exists( f'{fit_node_dir}/ihme.csv' ) :
        print( f'skipping {fit_node_dir}' )
    else :
        print( f'copying {fit_node_dir}' )
        #
        # to_dir
        to_dir = f'{to_dir}/{fit_node_name}.{sex_name}'
        if not os.path.exists(to_dir) :
            os.makedirs(to_dir)
        #
        # file
        for file in copy_file_list :
            #
            # from_path
            from_path = f'{fit_node_dir}/{file}'
            #
            # to_path
            to_path = f'{to_dir}/{file}'
            #
            # copy file
            print( file )
            shutil.copyfile(from_path, to_path)
    #
    # shift_name_list
    shift_name_list = list()
    for row in split_reference_table :
        shift_name = row['split_reference_name']
        dir_name   = f'{fit_node_dir}/{shift_name}'
        if os.path.isdir(dir_name) :
            shift_name_list.append( shift_name )
    if len(shift_name_list) == 0 :
        for child_node_id in fit_children[fit_node_id] :
            shift_name = node_table[child_node_id]['node_name']
            shift_name_list.append( shift_name )
    #
    # results at next level
    for shift_name in shift_name_list :
        shift_node_database = f'{fit_node_dir}/{shift_name}/dismod.db'
        copy_ihme_results(
            fit_node_database   = shift_node_database   ,
            fit_children        = fit_children          ,
            date                = date                  ,
        )
# ----------------------------------------------------------------------------
def main() :
    #
    # command_line_option
    command_line_ok = False
    if len(sys.argv) == 2 :
        command_line_option = sys.argv[1]
        command_line_ok =  command_line_option in [
            'drill', 'predict', 'copy'
        ]
    if not command_line_ok :
        usage  = 'usage: bin/ihme/35057.py (drill|predict|copy)\n'
        usage += 'drill must run first, then predict, then copy'
        sys.exit(usage)
    #
    if command_line_option == 'drill' :
        #
        # remove old verison of working_directory/root_node_name
        if os.path.exists(working_directory + '/' + root_node_name) :
            # rmtree is dangerous so make sure working_directory is as expected
            assert working_directory == 'ihme_db/35057'
            shutil.rmtree(working_directory + '/' + root_node_name)
        #
        # change into working directory and create root_node_name subdirectory
        os.chdir(working_directory)
        os.makedirs(root_node_name)
        #
        # drill
        drill()
    elif command_line_option == 'predict' :
        # change into working directory and create root_node_name subdirectory
        os.chdir(working_directory)
        #
        # start at the fit for the root node
        fit_node_database = f'{root_node_name}/dismod.db'
        create_ihme_results(fit_node_database)
    else :
        # change into working directory and create root_node_name subdirectory
        os.chdir(working_directory)
        #
        # start at the fit for the root node
        fit_node_database = f'{root_node_name}/dismod.db'
        copy_ihme_results(fit_node_database)
# ----------------------------------------------------------------------------
main()
print(sys.argv[0] + ': OK')
sys.exit(0)
