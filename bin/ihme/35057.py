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
#
# working_directory (input and output files are relative to this location)
working_directory = 'ihme_db/35057'
#
# input table file names
location_table_csv  = 'location_map.csv'
ldi_table_csv       = 'ldi_covariate_data.csv'
obesity_table_csv   = 'obesity_covariate_data.csv'
data_table_csv      = 'overall_diabetes_input_data_crosswalkv35057.csv'
emr_table_csv       = 'diabetes_emr.csv'
age_group_table_csv = 'age_metadata_gbd2020.csv'
all_node_other      = '../475876/all_node.db'
root_node_other     = '../475876/dismod.db'
#
# output table file name
data_table_out      = 'data.csv'
node_table_out      = 'node.csv'
#
# root_node_name
root_node_name      = 'Global'
#
# Maximum number of data table entries. This is to speed up softward testing.
# In the real case set max_data_table = None
max_data_table      = 40000
#
# maximum number of data row per integrand to include in a fit
max_fit = 500
#
# random_seed (if zero, use clock for random seed)
random_seed = 0
# -----------------------------------------------------------------------------
#
import time
import random
import math
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
# working_directory
if not os.path.exists(working_directory) :
    os.makedirs(working_directory)
#
# remove old verison of working_directory/root_node_name
if os.path.exists(working_directory + '/' + root_node_name) :
    # rmtree is very dangerous so make sure working_directory is as expected
    assert working_directory == 'ihme_db/35057'
    shutil.rmtree(working_directory + '/' + root_node_name)
#
# change into working directory and create root_node_name subdirectory
os.chdir(working_directory)
os.makedirs(root_node_name)
#
# random.seed
if random_seed == 0 :
    random_seed = int( time.time() )
print('random_seed = ', random_seed)
random.seed(random_seed)
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
    return age_group_dict
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
        row_out = dict()
        row_out['csv_row_id']   = csv_row_id
        row_out['location_id']  = int( row_in['location_id'] )
        row_out['sex']          = 'Both'
        row_out['time_lower']   = year_id
        row_out['time_upper']   = year_id + 1.0
        row_out['age_lower']    = age_group_dict[age_group_id]['age_lower']
        row_out['age_upper']    = age_group_dict[age_group_id]['age_upper']
        row_out['meas_value']   = float( row_in['mean'] )
        row_out['meas_std']     = meas_std
        row_out['obesity']      = None
        row_out['ldi']          = None
        #
        if row_in['measure'] == 'incidence' :
            row_out['integrand']    = 'Sincidence'
        else :
            row_out['integrand']    = row_in['measure']
        #
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
        csv_row_id += 1
        row_out = dict()
        row_out['csv_row_id']   = csv_row_id
        row_out['location_id']  = int( row_in['location_id'] )
        row_out['sex']          = row_in['sex']
        row_out['time_lower']   = float( row_in['year_start'] )
        row_out['time_upper']   = float( row_in['year_end'] ) + 1.0
        row_out['age_lower']    = float( row_in['age_start'] )
        row_out['age_upper']    = float( row_in['age_end'] ) + 1.0
        row_out['meas_value']   = float( row_in['mean'] )
        row_out['obesity']      = None
        row_out['ldi']          = None
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
def create_csv_files() :
    #
    # data_table
    data_table = get_data_table(data_table_csv)
    if False :
        age_max   = - math.inf
        time_max   = - math.inf
        for row in data_table :
            age_max  = max(age_max, row['age_upper'] )
            time_max = max(time_max, row['t ime_upper'] )
        print( age_max, time_max)
    #
    # emr_table
    age_group_dict = get_age_group_dict(age_group_table_csv)
    emr_table     = get_emr_table(emr_table_csv, age_group_dict)
    #
    # data_table
    assert set( data_table[0].keys() ) == set( emr_table[0].keys() )
    data_table += emr_table
    if not max_data_table is None :
        subsample = random.sample(range(0, len(data_table)), max_data_table)
        subsample = sorted(subsample)
        temp_table = data_table
        data_table = list()
        for k in range(0, max_data_table) :
            data_table.append( temp_table[subsample[k]] )
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
    # change location_id to data_name and add node_id
    for row in data_table :
        location_id      = row['location_id']
        node_id          = location_id2node_id[location_id]
        row['node_id']   = node_id
        del row['location_id']
    #
    # create data_table_out
    write_csv(data_table_out, data_table)
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
        row_out['c_location_id'] = location_id
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
    # create node_table_out
    write_csv(node_table_out, node_table)
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
    csv_data_table = get_table_csv( data_table_out )
    csv_node_table = get_table_csv( node_table_out )
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
        40.0, 60.0,
        70.0, 80.0, 90.0, 100.0
    ]
    for age in age_grid :
        if age in age_list :
            grid_age_id.append( age_list.index(age) )
        else :
            grid_age_id.append( len(age_list) )
            age_list.append( age )
    # max aage in csv files
    age_list.append( 126.0 )
    #
    # time_list
    time_list = list()
    for row in other_time_table :
        time_list.append( row['time'] )
    #
    # time_list, grid_time_id
    grid_time_id = list()
    time_grid   = [ 1990.0, 2000.0, 2010.0, 2020.0 ]
    for time in time_grid :
        if time in time_list :
            grid_time_id.append( time_list.index(time) )
        else :
            grid_time_id.append( len(time_list) )
            time_list.append( time )
    # max time in csv files
    time_list.append( 1960.0 )
    time_list.append( 2023.0 )
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
        }
    ]
    #
    # integrand_table
    integrand_set = set()
    for row in csv_data_table :
        integrand_set.add( row['integrand'] )
    integrand_table = list()
    for integrand_name in integrand_set :
        integrand_table.append( { 'name' : integrand_name } )
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
    # 2DO: becasue we are using data4cov_reference,
    # obesity reference depends on random_seed and max_data_table
    covariate_table = [
        { 'name':'sex',     'reference':0.0, 'max_difference':0.6},
        { 'name':'one',     'reference':0.0 },
        { 'name':'obesity', 'reference':0.1203},
    ]
    #
    # avgint_table
    ageint_table = list()
    #
    # data_table
    sex_map = { 'Female':-0.5, 'Both':0.0, 'Male':+0.5 }
    data_table = list()
    for row_in in csv_data_table :
        node_id   = int( row_in['node_id'] )
        node_name = node_table[node_id]['name']
        sex       = sex_map[ row_in['sex'] ]
        if row_in['obesity'] == '' :
            obesity = None
        else :
            obesity = float( row_in['obesity'] )
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
            'hold_out'        : False,
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
            'density' :    'gaussian',
            'lower'   :    1e-7,
            'upper'   :    1.0,
            'mean'    :    1e-2,
            'std'     :    1.0
        },{
            'name'    :    'parent_rate_delta',
            'density' :    'log_gaussian',
            'lower'   :    None,
            'upper'   :    None,
            'mean'    :    0.0,
            'std'     :    0.1,
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
            'density' :   'uniform',
            'lower'   :   -1.0,
            'upper'   :   1.0,
            'mean'    :   0.0,
        }
    ]
    #
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
        ('parent_rate_value', None, 'parent_rate_delta')
    smooth_table.append({
        'name':     'parent_pini',
        'age_id':   [0],
        'time_id':  grid_time_id,
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
    # rate_table
    rate_table = [
        {
            'name':          'pini',
            'parent_smooth': None,
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
        { 'name':'parent_node_name',     'value':'Global'},
        { 'name':'zero_sum_child_rate',  'value':'iota chi'},
        { 'name':'random_seed',          'value':str(random_seed)},
        { 'name':'quasi_fixed',          'value':'false' },
        { 'name':'tolerance_fixed',      'value':'1e-3'},
        { 'name':'max_num_iter_fixed',   'value':'30'},
        { 'name':'trace_init_fit_model', 'value':'true'},
        { 'name':'data_extra_columns',   'value':'csv_row_id'},
        { 'name':'print_level_fixed',    'value':'5'},
    ]
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
    # fit_goal table
    # Do a drill to drill_node_name
    drill_node_name = 'Global'
    drill_node_id   = None
    for (node_id, row) in enumerate( node_table ) :
        if row['node_name'] == drill_node_name :
            drill_node_id = node_id
    assert not drill_node_id is None
    tbl_name = 'fit_goal'
    col_name = [ 'node_id' ]
    col_type = [ 'integer' ]
    row_list = [
        [ drill_node_id ]
    ]
    command = 'DROP TABLE IF EXISTS '  + tbl_name
    dismod_at.sql_command(connection, command)
    dismod_at.create_table(connection, tbl_name, col_name, col_type, row_list)
    #
    # mtall_index, mtspecific_index
    # Change sex_id -> split_reference_id and map its values
    # 2 -> 0 (female), 3 -> 1 (both), 1 -> 2 (male)
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
    # all_option_table
    all_option_table  = dismod_at.get_table_dict(connection, 'all_option')
    all_option_id     = None
    for (row_id, row) in enumerate( all_option_table ) :
        # in_parallel
        if row['option_name'] == 'in_parallel' :
            row['option_value'] = 'false'
        # max_fit
        if row['option_name'] == 'max_fit' :
            row['option_value'] = str(max_fit)
        # max_abs_effect
        if row['option_name'] == 'max_abs_effect' :
            all_option_id = row_id
        # split_list
        if row['option_name'] == 'split_list' :
            row['option_value'] = '-1 sex -0.5 0.0 +0.5'
        # split_list
        if row['option_name'] == 'split_list' :
            row['option_value'] = '-1 sex -0.5 0.0 +0.5'
    # max_abs_effect
    if not all_option_id is None :
        del all_option_table[all_option_id]
    # absolute_covariates
    row = { 'option_name':'absolute_covariates', 'option_value':'one' }
    all_option_table.append(row)
    dismod_at.replace_table(connection, 'all_option', all_option_table)
    #
    # connection
    connection.close()
    #
    # all_cov_reference table
    at_cascade.data4cov_reference(
        root_node_database = root_node_database,
        all_node_database  = all_node_database  ,
        trace              = True,
    )
# ---------------------------------------------------------------------------
def display_results(database) :
    #
    # pdf_file
    index    = database.rfind('/')
    pdf_dir  = database[0:index]
    #
    # integrand_table, rate_table
    new             = False
    connection      = dismod_at.create_connection(database, new)
    integrand_table = dismod_at.get_table_dict(connection, 'integrand')
    rate_table      = dismod_at.get_table_dict(connection, 'rate')
    #
    # data.pdf
    integrand_list = list( at_cascade.get_fit_integrand(database) )
    for i in range( len(integrand_list) ) :
        integrand_id      = integrand_list[i]
        integrand_name    = integrand_table[integrand_id]['integrand_name']
        integrand_list[i] = integrand_name
    pdf_file = pdf_dir + '/data.pdf'
    n_point_list = dismod_at.plot_data_fit(database, integrand_list, pdf_file)
    #
    # rate.pdf
    rate_set = set()
    for row in rate_table :
        if not row['parent_smooth_id'] is None :
            rate_set.add( row['rate_name'] )
    pdf_file = pdf_dir + '/rate.pdf'
    plot_set = dismod_at.plot_rate_fit( database, rate_set, pdf_file)
    #
    # db2csv
    dismod_at.system_command_prc([ 'dismodat.py', database, 'db2csv' ])
# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main() :
    root_node_database = 'root_node.db'
    all_node_database  = 'all_node.db'
    #
    # other_age_table, other_time_table
    new        = False
    connection = dismod_at.create_connection(root_node_other, new)
    other_age_table  = dismod_at.get_table_dict(connection, 'age')
    other_time_table = dismod_at.get_table_dict(connection, 'time')
    connection.close()
    #
    # extract info from raw csv files
    create_csv_files()
    #
    # create root_node.db
    create_root_node_database(
        root_node_database, other_age_table, other_time_table
    )
    #
    # create all_node.db
    create_all_node_database(all_node_database, root_node_database)
    #
    # no_ode_fit
    fit_node_database = at_cascade.no_ode_fit(
        all_node_database = all_node_database,
        in_database       = root_node_database,
        max_fit           = max_fit,
        trace_fit         = True,
    )
    assert fit_node_database == root_node_name + '/dismod.db'
    #
    # display_results
    display_results( root_node_name + '/no_ode/dismod.db' )
    #
    # cascade starting at root node
    if True :
        at_cascade.cascade_fit_node(
            all_node_database, fit_node_database, trace_fit = True
        )
# ----------------------------------------------------------------------------
main()
print(sys.argv[0] + ': OK')
sys.exit(0)
