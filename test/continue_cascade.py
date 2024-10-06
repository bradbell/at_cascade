# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ----------------------------------------------------------------------------
# This tests continuing the cascade from the splitting node
# when refit_split is false. This was crashing on 2024-03-07.
#
r'''
                /-------------n0-------------\
          /---female---\                /----male----\
        n1              n2            n1              n2
       /  \            /  \          /  \            /  \
     n3    n4        n5    n6      n3    n4        n5    n6
'''
# BEGIN split_covariate source code
# ----------------------------------------------------------------------------
# imports
# ----------------------------------------------------------------------------
import math
import sys
import os
import copy
import time
import csv
import random
import shutil
import dismod_at
from math import exp
#
# import at_cascade with a preference current directory version
current_directory = os.getcwd()
if os.path.isfile( current_directory + '/at_cascade/__init__.py' ) :
   sys.path.insert(0, current_directory)
import at_cascade
# -----------------------------------------------------------------------------
# global varables
# -----------------------------------------------------------------------------
# BEGIN fit_goal_set
fit_goal_set = { 'n3', 'n4', 'n5', 'n6' }
# END fit_goal_set
#
# BEGIN option_all_table
option_all            = {
   'refit_split':                'false',
   'result_dir':                 'build/test',
   'root_node_name':             'n0',
   'root_split_reference_name':  'both',
   'split_covariate_name':       'sex',
   'shift_prior_std_factor':      1e3,
}
option_all['root_node_database'] = option_all['result_dir'] + '/root_node.db'
# END option_all_table
#
#
# BEGIN split_reference_table
split_reference_table = [
   {'split_reference_name': 'female', 'split_reference_value': 1.0},
   {'split_reference_name': 'both',   'split_reference_value': 2.0},
   {'split_reference_name': 'male',   'split_reference_value': 3.0},
]
split_reference_list = list()
for row in split_reference_table :
   split_reference_list.append( row['split_reference_value'] )
# END split_reference_table
# BEGIN node_split_table
node_split_table = [ { 'node_name' :   'n0'} ]
# END node_split_table
#
# BEGIN root_split_reference_id
root_split_reference_id = 1
assert  \
split_reference_table[root_split_reference_id]['split_reference_name']=='both'
# END root_split_reference_id
#
# BEGIN alpha_true
alpha_true = - 0.2
# END alpha_true
# ----------------------------------------------------------------------------
# functions
# ----------------------------------------------------------------------------
# BEGIN rate_true
def rate_true(rate, a, t, n, c) :
   # both_iota
   both_iota = {
      'n3' : 1e-2,
      'n4' : 2e-2,
      'n5' : 3e-2,
      'n6' : 4e-2
   }
   both_iota['n1'] = (both_iota['n3'] + both_iota['n4']) / 2.9
   both_iota['n2'] = (both_iota['n5'] + both_iota['n6']) / 2.9
   both_iota['n0'] = (both_iota['n1'] + both_iota['n2']) / 2.9
   #
   # both_sex
   both_sex = None
   for row in split_reference_table :
      if row['split_reference_name'] == 'both' :
         both_sex = row['split_reference_value']
   #
   # sex
   sex    = c[0]
   #
   effect   = alpha_true * ( sex - both_sex )
   #
   if rate == 'iota' :
      return both_iota[n] * exp(effect)
   if rate == 'omega' :
      return 2.0 * both_iota[n] * exp(effect)
   return 0.0
# END rate_true
# ----------------------------------------------------------------------------
def root_node_db(file_name) :
   #
   # iota_n0
   sex       = split_reference_list[root_split_reference_id]
   c         = [ sex ]
   iota_n0   = rate_true('iota', None, None, 'n0', c)
   #
   # prior_table
   prior_table = list()
   prior_table.append(
      # BEGIN parent_value_prior
      {   'name':    'parent_value_prior',
         'density': 'gaussian',
         'lower':   iota_n0 / 10.0,
         'upper':   iota_n0 * 10.0,
         'mean':    iota_n0 ,
         'std':     iota_n0 * 10.0,
         'eta':     iota_n0 * 1e-3
      }
      # END parent_value_prior
   )
   prior_table.append(
      # BEGIN alpha_value_prior
      {   'name':    'alpha_value_prior',
         'density': 'gaussian',
         'lower':   - 10 * abs(alpha_true),
         'upper':   + 10 * abs(alpha_true),
         'std':     + 10 * abs(alpha_true),
         'mean':    0.0,
      }
      # END alpha_value_prior
   )
   #
   # smooth_table
   smooth_table = list()
   #
   # parent_smooth
   fun = lambda a, t : ('parent_value_prior', None, None)
   smooth_table.append({
      'name':       'parent_smooth',
      'age_id':     [0],
      'time_id':    [0],
      'fun':        fun,
   })
   #
   # alpha_smooth
   fun = lambda a, t : ('alpha_value_prior', None, None)
   smooth_table.append({
      'name':       'alpha_smooth',
      'age_id':     [0],
      'time_id':    [0],
      'fun':        fun,
   })
   #
   # node_table
   node_table = [
      { 'name':'n0',        'parent':''   },
      { 'name':'n1',        'parent':'n0' },
      { 'name':'n2',        'parent':'n0' },
      { 'name':'n3',        'parent':'n1' },
      { 'name':'n4',        'parent':'n1' },
      { 'name':'n5',        'parent':'n2' },
      { 'name':'n6',        'parent':'n2' },
   ]
   #
   # rate_table
   rate_table = [ {
      'name':           'iota',
      'parent_smooth':  'parent_smooth',
      'child_smooth':   None ,
   } ]
   #
   # covariate_table
   covariate_table = list()
   sex    = split_reference_list[root_split_reference_id]
   covariate_table.append(
      { 'name': 'sex',      'reference': sex, 'max_difference': 1.1 }
   )
   #
   # mulcov_table
   mulcov_table = [ {
      # alpha
      'covariate':  'sex',
      'type':       'rate_value',
      'effected':   'iota',
      'group':      'world',
      'smooth':     'alpha_smooth',
   } ]
   #
   # subgroup_table
   subgroup_table = [ {'subgroup': 'world', 'group':'world'} ]
   #
   # integrand_table
   integrand_table = [ {'name':'Sincidence'} ]
   for mulcov_id in range( len(mulcov_table) ) :
      integrand_table.append( { 'name': f'mulcov_{mulcov_id}' } )
   #
   # avgint_table
   avgint_table = list()
   row = {
      'node':         'n0',
      'subgroup':     'world',
      'weight':       '',
      'time_lower':   2000.0,
      'time_upper':   2000.0,
      'age_lower':    50.0,
      'age_upper':    50.0,
      'sex':          None,
      'integrand':    'Sincidence',
   }
   avgint_table.append( copy.copy(row) )
   #
   # data_table
   data_table  = list()
   leaf_set    = { 'n3', 'n4', 'n5', 'n6' }
   row = {
      'subgroup':     'world',
      'weight':       '',
      'time_lower':   2000.0,
      'time_upper':   2000.0,
      'age_lower':      50.0,
      'age_upper':      50.0,
      'integrand':    'Sincidence',
      'density':      'gaussian',
      'hold_out':     False,
   }
   assert split_reference_table[0]['split_reference_name'] == 'female'
   assert split_reference_table[2]['split_reference_name'] == 'male'
   for split_reference_id in [ 0, 2 ] :
      for node in leaf_set :
         sex  = split_reference_list[split_reference_id]
         c    = [sex]
         meas_value = rate_true('iota', None, None, node, c)
         row['node']       = node
         row['meas_value'] = meas_value
         row['sex']        = sex
         row['meas_std']   = meas_value / 10.0
         data_table.append( copy.copy(row) )
   #
   # age_grid
   age_grid = [ 0.0, 100.0 ]
   #
   # time_grid
   time_grid = [ 1980.0, 2020.0 ]
   #
   # weight table:
   weight_table = list()
   #
   # nslist_table
   nslist_table = dict()
   #
   # option_table
   option_table = [
      { 'name':'parent_node_name',      'value':'n0'},
      { 'name':'rate_case',             'value':'iota_pos_rho_zero'},
      { 'name': 'zero_sum_child_rate',  'value':'iota'},
      { 'name':'quasi_fixed',           'value':'false'},
      { 'name':'max_num_iter_fixed',    'value':'50'},
      { 'name':'tolerance_fixed',       'value':'1e-8'},
   ]
   # ----------------------------------------------------------------------
   # create database
   dismod_at.create_database(
      file_name,
      age_grid,
      time_grid,
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
# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------
def main() :
   # -------------------------------------------------------------------------
   # result_dir
   result_dir = option_all['result_dir']
   at_cascade.empty_directory(result_dir)
   #
   # Create root_node.db
   root_node_database  = option_all['root_node_database']
   root_node_db(root_node_database)
   #
   # omega_grid
   connection   = dismod_at.create_connection(
      root_node_database, new = False, readonly = True
   )
   age_table    = dismod_at.get_table_dict(connection, 'age')
   time_table   = dismod_at.get_table_dict(connection, 'time')
   age_id_list  = list( range( len(age_table) ) )
   time_id_list = list( range( len(age_table) ) )
   omega_grid   = { 'age': age_id_list, 'time' : time_id_list }
   connection.close()
   #
   # n_split
   n_split  = len( split_reference_list )
   #
   # omega_data
   omega_data      = dict()
   for node_name in [ 'n0', 'n1', 'n2', 'n3', 'n4', 'n5', 'n6' ] :
      omega_data[node_name] = list()
      for k in range(n_split) :
         omega_data[node_name].append( list() )
         for age_id in omega_grid['age'] :
            for time_id in omega_grid['time'] :
               age    = age_table[age_id]['age']
               time   = time_table[time_id]['time']
               sex    = split_reference_list[k]
               cov    = [ sex ]
               omega  = rate_true('omega', None, None, node_name, cov)
               omega_data[node_name][k].append( omega )
   #
   # Create all_node.db
   all_node_database = f'{result_dir}/all_node.db'
   at_cascade.create_all_node_db(
      all_node_database      = all_node_database,
      split_reference_table  = split_reference_table,
      node_split_table       = node_split_table,
      option_all             = option_all,
      omega_grid             = omega_grid,
      omega_data             = omega_data,
   )
   #
   # root_node_dir
   root_node_dir = f'{result_dir}/n0'
   os.mkdir(root_node_dir)
   #
   # avgint_table
   # also erase avgint table in root node database
   connection      = dismod_at.create_connection(
      root_node_database, new = False, readonly = False
   )
   avgint_table    = dismod_at.get_table_dict(connection, 'avgint')
   empty_table     = list()
   message         = 'erase avgint table'
   tbl_name        = 'avgint'
   dismod_at.replace_table(connection, tbl_name, empty_table)
   at_cascade.add_log_entry(connection, message)
   connection.close()
   #
   # only fit the root node
   at_cascade.cascade_root_node(
      all_node_database  = all_node_database ,
      fit_goal_set       = { 'n0' }          ,
   )
   #
   # complete the cascade
   at_cascade.continue_cascade(
      all_node_database  = all_node_database ,
      fit_database       = f'{root_node_dir}/dismod.db' ,
      fit_goal_set       = fit_goal_set ,
   )
   #
   # check results
   for sex in [ 'female', 'male' ] :
      for subdir in [ 'n1/n3', 'n1/n4', 'n2/n5', 'n2/n6' ] :
         goal_database = f'{result_dir}/n0/{sex}/{subdir}/dismod.db'
         at_cascade.check_cascade_node(
            rate_true          = rate_true,
            all_node_database  = all_node_database,
            fit_database       = goal_database,
            avgint_table       = avgint_table,
            relative_tolerance = 1e-5,
         )
   #
   # fit_iota, fit_alpha
   fit_database      = f'{result_dir}/n0/dismod.db'
   connection        = dismod_at.create_connection(
      fit_database, new = False, readonly = True
   )
   var_table         = dismod_at.get_table_dict(connection, 'var')
   fit_var_table     = dismod_at.get_table_dict(connection, 'fit_var')
   rate_table        = dismod_at.get_table_dict(connection, 'rate')
   prior_table       = dismod_at.get_table_dict(connection, 'prior')
   connection.close()
   for (var_id, row) in enumerate(var_table) :
      rate_id   = row['rate_id']
      rate_name = rate_table[rate_id]['rate_name']
      if rate_name == 'iota' :
         if row['var_type'] == 'rate' :
            fit_iota = fit_var_table[var_id]['fit_var_value']
         else :
            assert row['var_type'] == 'mulcov_rate_value'
            fit_alpha = fit_var_table[var_id]['fit_var_value']
#
if __name__ == '__main__' :
   main()
   print('continue_cascade: OK')
# END split_covariate source code
