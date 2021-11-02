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
work_dir = 'ihme_db/475876'
distutils.dir_util.mkpath(work_dir)
os.chdir(work_dir)
#
# max_fit
max_fit = 250
#
# root_node_database
root_node_database = 'dismod.db'
#
# all_node_database
all_node_database = 'all_node.db'
#
# all_node_copy
all_node_copy = 'all_node_copy.db'
shutil.copyfile(all_node_database, all_node_copy)
#
# root_node_copy
root_node_copy =  'root_node_copy.db'
shutil.copyfile(root_node_database, root_node_copy)
#
# root_node_dir
root_node_dir = 'Global'
if os.path.exists(root_node_dir) :
    # rmtree is very dangerous so make sure root_node_dir is as expected
    os.chdir('../..')
    assert work_dir == 'ihme_db/475876'
    shutil.rmtree(work_dir + '/' + root_node_dir)
    os.chdir(work_dir)
os.makedirs(root_node_dir )
#
# connect_all, connect_root
new          = False
connect_all  = dismod_at.create_connection(all_node_copy, new)
connect_root = dismod_at.create_connection(root_node_copy, new)
#
# node_table
node_table   = dismod_at.get_table_dict(connect_root, 'node')
#
# fit_goal table
# Do a drill to drill_node_name
drill_node_name = 'New York'
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
dismod_at.sql_command(connect_all, command)
dismod_at.create_table(connect_all, tbl_name, col_name, col_type, row_list)
#
# covariate_table
# The covariates names in this database are useless, replace them
covariate_table = dismod_at.get_table_dict(connect_root, 'covariate')
for row in covariate_table :
    row['covariate_name'] = row['c_covariate_name']
dismod_at.replace_table(connect_root, 'covariate', covariate_table)
#
# option_table
option_table = dismod_at.get_table_dict(connect_root, 'option')
count = 0
for row in option_table :
    if row['option_name'] == 'zero_sum_child_rate' :
        row['option_value'] = 'iota chi'
        count += 1
    if row['option_name'] == 'random_seed' :
        row['option_value'] = '0'
        count += 1
    if row['option_name'] == 'tolerance_fixed' :
        row['option_value'] = '1e-3'
        count += 1
    if row['option_name'] == 'max_num_iter_fixed' :
        row['option_value'] = '30'
        count += 1
assert count == 4
row = { 'option_name' : 'trace_init_fit_model', 'option_value' : 'true' }
option_table.append( row )
dismod_at.replace_table(connect_root, 'option', option_table)
# ----------------------------------------------------------------------------
# new prior for pini
#
# tables
tables = dict()
for tbl_name in ['prior', 'density', 'rate', 'time', 'smooth', 'smooth_grid'] :
    tables[tbl_name] =dismod_at.get_table_dict(connect_root, tbl_name)
pini_rate_id = 0
assert tables['rate'][pini_rate_id]['rate_name'] == 'pini'
#
# density_id, value_prior_id
density_id     = at_cascade.table_name2id(
    tables['density'], 'density', 'log_gaussian'
)
value_prior_id = len(tables['prior'])
prior_name     =  f'pini_value_prior_{value_prior_id}'
lower          = 0.0
upper          = 1.0
mean           = 1e-5
std            = 1e-4
eta            = 1e-7
nu             = None
keys           = [
    'prior_name', 'density_id', 'lower', 'upper', 'mean', 'std', 'eta', 'nu'
]
values         = [ prior_name, density_id, lower, upper, mean, std, eta, nu ]
prior_row      = dict( zip(keys, values) )
tables['prior'].append(prior_row)
#
# dtime_prior_id
dtime_prior_id = len(tables['prior'])
prior_name     =  f'pini_dtime_prior_{dtime_prior_id}'
lower          = None
upper          = None
mean           = 0.0
std            = 2.0
eta            = 1e-7
nu             = None
keys           = [
    'prior_name', 'density_id', 'lower', 'upper', 'mean', 'std', 'eta', 'nu'
]
values         = [ prior_name, density_id, lower, upper, mean, std, eta, nu ]
prior_row      = dict( zip(keys, values) )
tables['prior'].append(prior_row)
#
# time_grid
time_grid = [ 1960.0, 1980.0, 2000.0, 2020.0 ]
#
# smooth_id, n_time
smooth_id   = len(tables['smooth'])
smooth_name =  f'pini_smooth_{smooth_id}'
n_age       = 1
n_time      = len(time_grid)
smooth_row  = { 'smooth_name':smooth_name, 'n_age':n_age, 'n_time':n_time }
for middle in [ 'value', 'dage', 'dtime' ] :
    key = f'mulstd_{middle}_prior_id'
    smooth_row[key] = None
tables['smooth'].append(smooth_row)
#
# grid_time_id
time_list = list()
for row in tables['time'] :
    time_list.append( row['time'] )
grid_time_id = list()
for time in time_grid :
    if time in time_list :
        grid_time_id.append( time_list.index( time ) )
    else :
        grid_time_id.append( len(tables['time']) )
        time_row = { 'time': time }
        tables['time'].append( time_row )
#
# smooth_grid table
dage_prior_id = None
const_value   = None
keys = [
    'smooth_id', 'age_id', 'time_id',
    'value_prior_id', 'dage_prior_id', 'dtime_prior_id', 'const_value'
]
age_id  = 0
for time_id in grid_time_id :
    values = [
        smooth_id, age_id, time_id,
        value_prior_id, dage_prior_id, dtime_prior_id, const_value
    ]
    smooth_grid_row = dict( zip(keys, values) )
    tables['smooth_grid'].append( smooth_grid_row )
#
# rate table
tables['rate'][pini_rate_id]['parent_smooth_id'] = smooth_id
#
# replace tables
for tbl_name in tables.keys() :
    dismod_at.replace_table(connect_root, tbl_name, tables[tbl_name] )
# --------------------------------------------------------------------------
# Corrections to root_node_database and all_node_database
#
# integrand_table
# Add missing mulcov_j to integrand table.
integrand_table = dismod_at.get_table_dict(connect_root, 'integrand')
mulcov_table    = dismod_at.get_table_dict(connect_root, 'mulcov')
name_list       = list()
for row in integrand_table :
    name_list.append( row['integrand_name'] )
for mulcov_id in range( len(mulcov_table) ) :
    integrand_name = f'mulcov_{mulcov_id}'
    if not integrand_name in name_list :
        row = copy.copy( integrand_table[0] )
        row['integrand_name']  = integrand_name
        row['minimum_meas_cv'] = 0.0
        integrand_table.append( row )
dismod_at.replace_table(connect_root, 'integrand', integrand_table)
#
# option_table, parent_node_id
# at_cascade requires one to use parent_node_name (not parent_node_id)
parent_node_name     = None
parent_node_id       = None
for row in option_table :
    assert row['option_name'] != 'parent_node_name'
    if row['option_name'] == 'parent_node_id' :
        parent_node_id   = int( row['option_value'] )
        parent_node_name = node_table[parent_node_id]['node_name']
        row['option_name']  = 'parent_node_name'
        row['option_value'] = parent_node_name
assert not parent_node_name is None
assert not parent_node_id is None
dismod_at.replace_table(connect_root, 'option', option_table)
#
# avgint table
old_avgint_table = dismod_at.get_table_dict(connect_root, 'avgint')
new_avgint_table = list()
for row in old_avgint_table :
    if row['node_id'] == parent_node_id :
        new_avgint_table.append( row )
dismod_at.replace_table(connect_root, 'avgint', new_avgint_table)
#
# mtall_index, mtspecific_index
# Change sex_id -> split_reference_id and map its values
# 2 -> 0 (female), 3 -> 1 (both), 1 -> 2 (male)
split_map = { 1:2, 2:0, 3:1}
for tbl_name in [ 'mtall_index', 'mtspecific_index' ] :
    command  = 'ALTER TABLE ' + tbl_name + ' '
    command += 'RENAME COLUMN sex_id TO split_reference_id'
    dismod_at.sql_command(connect_all, command)
    #
    this_table = \
        dismod_at.get_table_dict(connect_all, tbl_name)
    for row in this_table :
        split_reference_id = split_map[ row['split_reference_id'] ]
        row['split_reference_id'] = split_reference_id
    dismod_at.replace_table( connect_all, tbl_name, this_table)
#
# all_option_table
all_option_table  = dismod_at.get_table_dict(connect_all, 'all_option')
all_option_id     = None
for (row_id, row) in enumerate( all_option_table ) :
    if row['option_name'] == 'in_parallel' :
        row['option_value'] = 'false'
    if row['option_name'] == 'max_fit' :
        row['option_value'] = str(max_fit)
    if row['option_name'] == 'max_abs_effect' :
        all_option_id = row_id
if not all_option_id is None :
    del all_option_table[all_option_id]
dismod_at.replace_table(connect_all, 'all_option', all_option_table)
# ----------------------------------------------------------------------------
# connect_all, connect_root
connect_all.close()
connect_root.close()
# ---------------------------------------------------------------------------
# More corrections
#
# all_cov_reference table
at_cascade.data4cov_reference(
    root_node_database = root_node_copy ,
    all_node_database  = all_node_copy  ,
    trace              = True,
)
#
# connect_all, connect_root
new               = False
connect_root      = dismod_at.create_connection(root_node_copy, new)
connect_all       = dismod_at.create_connection(all_node_copy, new)
#
# Use all_cov_reference table for relative covariate reference values
covariate_table   = dismod_at.get_table_dict(connect_root, 'covariate')
all_cov_reference = dismod_at.get_table_dict(connect_all, 'all_cov_reference')
cov_info          = at_cascade.get_cov_info(all_option_table, covariate_table)
if 'split_list' in cov_info :
    split_reference_id = cov_info['split_reference_id']
else :
    split_reference_id = None
for row in all_cov_reference :
    if row['node_id'] == parent_node_id :
        if row['split_reference_id'] == split_reference_id :
            covariate_id = row['covariate_id']
            covariate_table[covariate_id]['reference'] = row['reference']
dismod_at.replace_table(connect_root, 'covariate', covariate_table)
#
# connect_all, connect_roow
connect_all.close()
connect_root.close()
# ----------------------------------------------------------------------------
#
# no_ode_fit
fit_node_database = at_cascade.no_ode_fit(
    in_database = root_node_copy,
    max_fit     = max_fit,
    trace_fit   = True,
)
assert fit_node_database == root_node_dir + '/dismod.db'
no_ode_database = root_node_dir + '/no_ode.db'
#
# data.pdf
integrand_list = list( at_cascade.get_fit_integrand(no_ode_database) )
for i in range( len(integrand_list) ) :
    integrand_id      = integrand_list[i]
    integrand_name    = integrand_table[integrand_id]['integrand_name']
    integrand_list[i] = integrand_name
pdf_file = root_node_dir + '/data.pdf'
n_point_list = dismod_at.plot_data_fit(
    no_ode_database, integrand_list, pdf_file
)
#
# rate.pdf
new        = False
connection = dismod_at.create_connection(no_ode_database, new)
rate_table = dismod_at.get_table_dict(connection, 'rate')
connection.close()
rate_set = set()
for row in rate_table :
    if not row['parent_smooth_id'] is None :
        rate_set.add( row['rate_name'] )
pdf_file = root_node_dir + '/rate.pdf'
plot_set = dismod_at.plot_rate_fit(
    no_ode_database, rate_set, pdf_file
)
#
dismod_at.system_command_prc([ 'dismodat.py', no_ode_database, 'db2csv' ])
#
# cascade starting at root node
at_cascade.cascade_fit_node(all_node_copy, fit_node_database, trace_fit = True)
#
print(f'all_node_database = {all_node_copy}')
print(f'fit_node_database = {fit_node_database}')
print('476875.py: OK')
sys.exit(0)