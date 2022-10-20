# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
# imports
# ----------------------------------------------------------------------------
import sys
import os
import copy
import time
import random
import numpy
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
# global variables
# -----------------------------------------------------------------------------
#
# age_grid
age_grid   = [0.0, 20.0, 40.0, 60.0, 80.0, 100.0 ]
#
# time_grid
time_grid  = [ 1980.0, 2020.0 ]
# ----------------------------------------------------------------------------
# functions
# ----------------------------------------------------------------------------
# omega_true
def omega_true(a, t, n) :
   random_effect = { 'n0': 0.0, 'n1': -0.2, 'n2': +0.2 }
   iota          = (1 + a / 100 + (t - 1980.0)/40.0 ) * 1e-2
   iota          = exp( random_effect[n] ) * iota
   return iota
#
# ----------------------------------------------------------------------------
def root_node_db(file_name) :
   #
   # prior_table
   prior_table = list()
   #
   # smooth_table
   smooth_table = list()
   #
   # node_table
   node_table = [
      { 'name':'n0',        'parent':''   },
      { 'name':'n1',        'parent':'n0' },
      { 'name':'n2',        'parent':'n0' },
   ]
   #
   # rate_table
   rate_table = list()
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
   integrand_table = [ {'name':'mtother'} ]
   #
   # avgint_table
   avgint_table = list()
   integrand_name = 'mtother'
   row = {
      'subgroup':     'world',
      'weight':       '',
      'integrand':    'mtother',
   }
   for node_name in [ 'n0', 'n1', 'n2' ] :
      for age in age_grid :
         for time in time_grid :
            row['node']       = node_name
            row['age_lower']  = age
            row['age_upper']  = age
            row['time_lower'] = time
            row['time_upper'] = time
            avgint_table.append( copy.copy(row) )
   #
   # data_table
   data_table = list()
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
      { 'name':'rate_case',             'value':'iota_zero_rho_zero'},
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
def table_name2id(table, col_name, row_name) :
   for (row_id, row) in enumerate(table) :
      if row[col_name] == row_name :
         return row_id
   assert False
# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------
def main() :
   # -------------------------------------------------------------------------
   # change into the build/test directory
   if not os.path.exists('build/test') :
      os.makedirs('build/test')
   os.chdir('build/test')
   #
   # Create root_node.db
   root_node_database  = 'root_node.db'
   root_node_db(root_node_database)
   #
   # n_omega_age
   n_omega_age = len(age_grid)
   #
   # n_omega_time
   n_omega_time = len(time_grid)
   #
   # omega_grid
   omega_grid         = dict()
   omega_grid['age']  = list( range(n_omega_age) )
   omega_grid['time'] = list( range(n_omega_time) )
   #
   # omega_data
   omega_data = dict()
   for node_name in [ 'n0', 'n1', 'n2' ] :
      omega_data[node_name] = [ list() ]
      for i in range(n_omega_age) :
         for j in range(n_omega_time) :
            age_id  = omega_grid['age'][i]
            time_id = omega_grid['time'][j]
            age     = age_grid[age_id]
            time    = time_grid[time_id]
            omega   = omega_true(age, time, node_name)
            omega_data[node_name][0].append( omega )
   #
   # Create all_node.db
   all_node_database = 'all_node.db'
   all_option        = {
      'result_dir':      '.',
      'root_node_name': 'n0',
   }
   at_cascade.create_all_node_db(
      all_node_database      = all_node_database,
      root_node_database     = root_node_database,
      split_reference_table  = list(),
      all_option             = all_option,
      omega_grid             = omega_grid,
      omega_data             = omega_data,
   )
   #
   # set omega constraints
   at_cascade.omega_constraint(all_node_database, root_node_database)
   #
   # init
   dismod_at.system_command_prc( [ 'dismod_at', root_node_database, 'init' ] )
   #
   # truth_var = prior_mean
   dismod_at.system_command_prc(
      [ 'dismod_at', root_node_database, 'set', 'truth_var', 'prior_mean' ]
   )
   #
   # predict
   dismod_at.system_command_prc(
      [ 'dismod_at', root_node_database, 'predict', 'truth_var' ]
   )
   #
   # tables
   new        = False
   connection = dismod_at.create_connection(root_node_database, new)
   table      = dict()
   for table_name in [
      'avgint',
      'integrand',
      'node',
      'predict',
      'rate',
   ] :
      table[table_name] = dismod_at.get_table_dict(connection, table_name)
   #
   # predict_row
   for predict_row in table['predict'] :
      #
      # avgint_id
      avgint_id = predict_row['avgint_id']
      #
      # avgint_row
      avgint_row = table['avgint'][avgint_id]
      #
      # predict_value
      predict_value = predict_row['avg_integrand']
      #
      # integrand_name
      integrand_id   = avgint_row['integrand_id']
      integrand_name = table['integrand'][integrand_id]['integrand_name']
      assert integrand_name == 'mtother'
      #
      # rate_id
      rate_id = table_name2id(table['rate'], 'rate_name', 'omega')
      #
      # node_name
      node_id = avgint_row['node_id']
      node_name = table['node'][node_id]['node_name']
      #
      # age
      age = avgint_row['age_lower']
      assert age == avgint_row['age_upper']
      #
      # time
      time = avgint_row['time_lower']
      assert time == avgint_row['time_upper']
      #
      # true_value
      true_value = omega_true(age, time, node_name)
      #
      relative_err = 1.0 - predict_value / true_value
      # print(node_name, true_value, predict_value, relative_err)
      eps99 = 99.0 * numpy.finfo(float).eps
      assert abs( relative_err ) < eps99
#
main()
print('avgint_parent_grid.py: OK')
sys.exit(0)
