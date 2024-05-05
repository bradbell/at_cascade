# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-23 Bradley M. Bell
# ----------------------------------------------------------------------------
# imports
# ----------------------------------------------------------------------------
# recover from a failed fit both at level zero.
# ----------------------------------------------------------------------------
import csv
import sys
import os
import copy
import shutil
import dismod_at
import math
#
# import at_cascade with a preference current directory version
current_directory = os.getcwd()
if os.path.isfile( current_directory + '/at_cascade/__init__.py' ) :
   sys.path.insert(0, current_directory)
import at_cascade
# -----------------------------------------------------------------------------
# global variables
# -----------------------------------------------------------------------------
#
# alpha_true
alpha_true = 0.0
#
# age_grid
age_grid = [0.0, 100.0 ]
#
# fit_goal_set
fit_goal_set = { 'n1', 'n2' }
#
#
# ----------------------------------------------------------------------------
# iota_true
def iota_true(a, node) :
   effect = { 'n0' : 0.0, 'n1' : -1.0, 'n2' : +1.0 }
   iota   = (1 + a / 100) * 1e-2 * math.exp( effect[node]  )
   return iota
# ----------------------------------------------------------------------------
def root_node_db(file_name) :
   #
   # prior_table
   prior_table = [
      { # prior_iota_dage
         'name':    'prior_iota_dage',
         'density': 'uniform',
         'mean':    0.0,
         'std':     0.5,
      },{ # prior_iota_child
         'name':    'prior_iota_child',
         'density': 'uniform',
         'mean':    0.0,
         'std':     1.0,
      },
   ]
   for a in age_grid :
      mean        = iota_true(a, 'n0')
      prior_name  = f'prior_iota_value_{a}'
      prior       = {
         'name':    prior_name,
         'density': 'uniform',
         'lower':   mean / 10.0,
         'upper':   mean * 10.0,
         'mean':    mean,
         'std':     mean / 10.0,
      }
      prior_table.append( prior )
   #
   # smooth_table
   smooth_table = list()
   #
   # smooth_iota_value
   fun = lambda a, t : \
      ('prior_iota_value_' + str(a), 'prior_iota_dage', None)
   smooth_table.append({
      'name':       'smooth_iota_value',
      'age_id':     range( len(age_grid) ),
      'time_id':    [0],
      'fun':        fun,
   })
   #
   # smooth_iota_child
   fun = lambda a, t : ('prior_iota_child', None, None)
   smooth_table.append({
      'name':       'smooth_iota_child',
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
   ]
   #
   # rate_table
   rate_table = [ {
      'name':           'iota',
      'parent_smooth':  'smooth_iota_value',
      'child_smooth':   'smooth_iota_child' ,
   } ]
   #
   # covariate_table
   covariate_table = list()
   #
   # mulcov_table
   mulcov_table = list()
   #
   # subgroup_table
   subgroup_table = [ {'subgroup': 'world', 'group':'world'} ]
   #
   # integrand_table
   integrand_table = [ {'name':'Sincidence'} ]
   #
   # avgint_table
   avgint_table = list()
   #
   # data_table
   data_table  = list()
   row = {
      'subgroup':     'world',
      'weight':       '',
      'time_lower':   2000.0,
      'time_upper':   2000.0,
      'integrand':    'Sincidence',
      'density':      'gaussian',
      'hold_out':     False,
   }
   for node in [ 'n1', 'n2' ] :
      row['node'] = node
      for (age_id, age) in enumerate( age_grid ) :
         meas_value        = iota_true(age, node)
         row['meas_value'] = meas_value
         row['age_lower']  = age
         row['age_upper']  = age
         # model for the measurement noise
         # actual measruement noise is zero
         row['meas_std']   = meas_value / 2.0
         data_table.append( copy.copy(row) )
   #
   # time_grid
   time_grid = [ 2000.0 ]
   #
   # weight table:
   weight_table = list()
   #
   # nslist_table
   #
   nslist_table = dict()
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
def check_fit(result_dir, fit_node_name) :
   #
   # fit_node_database
   if fit_node_name == 'n0' :
      fit_node_database = f'{result_dir}/n0/dismod.db'
   else :
      fit_node_database = f'{result_dir}/n0/{fit_node_name}/dismod.db'
   #
   # root_node_database
   root_node_database  = f'{result_dir}/root_node.db'
   #
   # fit_node_id
   fit_node_id = int( fit_node_name[-1] )
   #
   # age, var_table, fit_var_table
   new           = False
   fit_or_root   = at_cascade.fit_or_root_class(
      fit_node_database, root_node_database
   )
   age_table     = fit_or_root.get_table('age')
   var_table     = fit_or_root.get_table('var')
   fit_var_table = fit_or_root.get_table('fit_var')
   fit_or_root.close()
   #
   for (var_id, row) in enumerate( var_table ) :
      fit_var_value = fit_var_table[var_id]['fit_var_value']
      node_id        = row['node_id']
      assert row['var_type'] == 'rate'
      if node_id == fit_node_id :
         age_id         = row['age_id']
         age            = age_table[age_id]['age']
         true_var_value = iota_true(age, fit_node_name)
         #
         rel_error = 1.0 - fit_var_value / true_var_value
         if abs(rel_error) >= 1e-6 :
            print( f'node = {node}, age = {age}, rel_error = {rel_error}' )
         assert abs(rel_error) < 1e-6
# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------
def main() :
   # -------------------------------------------------------------------------
   #
   # result_dir
   result_dir = 'build/test'
   at_cascade.empty_directory(result_dir)
   #
   # root_node.db
   root_node_database  = f'{result_dir}/root_node.db'
   root_node_db(root_node_database)
   #
   # mulcov_freeze_table
   mulcov_freeze_table = list()
   #
   # option_all
   option_all        = {
      'result_dir':     result_dir,
      'root_node_name': 'n0',
      'root_node_database': root_node_database,
   }
   #
   # all_node.db
   all_node_database = f'{result_dir}/all_node.db'
   at_cascade.create_all_node_db(
      all_node_database       = all_node_database,
      split_reference_table   = list(),
      option_all              = option_all,
      mulcov_freeze_table     = mulcov_freeze_table,
   )
   #
   # root_node_dir
   for node_name in [ 'n0', 'n1' ] :
      root_node_dir = f'{result_dir}/{node_name}'
      if os.path.exists(root_node_dir) :
         # rmtree is dangerous so make sure root_node_dir is as expected
         assert root_node_dir == f'build/test/{node_name}'
         shutil.rmtree( root_node_dir )
   root_node_dir = f'{result_dir}/n0'
   os.makedirs(root_node_dir )
   #
   # cascade starting at root node
   at_cascade.cascade_root_node(
      all_node_database  = all_node_database ,
      fit_goal_set       = fit_goal_set      ,
   )
   #
   for fit_node_name in [ 'n1', 'n2' ] :
      check_fit(result_dir, fit_node_name)
#
main()
print('recover_fit.py: OK')
sys.exit(0)
