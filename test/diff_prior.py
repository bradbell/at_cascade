# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ----------------------------------------------------------------------------
# Test case where no_ode does not converge and the approximatte solution
# does not satisfy does not satisfiy age difference constraint.
# This makes sure that the mean used for the differnce prior
# satisfies the constraint for the difference prior.
# ----------------------------------------------------------------------------
# imports
import sys
import os
import copy
import time
import csv
import random
import numpy
import shutil
import dismod_at
import math
import dismod_at
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
# fit_goal_set
fit_goal_set = { 'n0' }
#
# random_seed
random_seed = 0
if random_seed == 0 :
   random_seed = int( time.time() )
random.seed(random_seed)
#
# age_grid
age_grid = [0.0, 100.0 ]
#
# iota_true
iota_true = [ 0.01, 0.02 ]
iota_avg  = sum(iota_true) / len(iota_true)
#
# ----------------------------------------------------------------------------
# functions
# ----------------------------------------------------------------------------
def root_node_db(file_name) :
   #
   # prior_table
   prior_table = list()
   #
   prior_table.append(
      # parent_iota_value_prior
      {  'name':    'parent_iota_value_prior',
         'density': 'uniform',
         'lower':   1e-5,
         'upper':   1.0,
         'mean':    iota_avg,
      }
   )
   prior_table.append(
      # parent_dage_prior
      {  'name':    'parent_dage_prior',
         'density': 'uniform',
         'lower':   iota_avg,
         'upper':   1.0,
         'mean':    iota_avg,
      }
   )
   #
   # smooth_table
   smooth_table = list()
   #
   # parent_iota_smooth
   fun = lambda a, t : ('parent_iota_value_prior', 'parent_dage_prior', None)
   smooth_table.append({
      'name':       'parent_iota_smooth',
      'age_id':     range( len(age_grid) ),
      'time_id':    [0],
      'fun':        fun,
   })
   # node_table
   node_table = [
      { 'name':'n0',        'parent':''   },
   ]
   #
   # rate_table
   rate_table = [ {
         'name':           'iota',
         'parent_smooth':  'parent_iota_smooth',
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
   integrand_table = [
      {'name': 'Sincidence'},
   ]
   for mulcov_id in range( len(mulcov_table) ) :
      integrand_table.append( { 'name': f'mulcov_{mulcov_id}' } )
   #
   # avgint_table
   avgint_table = list()
   #
   # data_table
   data_table = list()
   row = {
      'subgroup':     'world',
      'weight':       '',
      'time_lower':   2000.0,
      'time_upper':   2000.0,
      'density':      'gaussian',
      'hold_out':     False,
      'integrand':    'Sincidence',
      'meas_std':     iota_avg * 1e-3,
      'node':         'n0',
   }
   for (index, age) in enumerate(age_grid) :
      row['age_lower']  = age
      row['age_upper']  = age
      row['meas_value'] = iota_true[index]
      #
      data_table.append( copy.copy(row) )
   #
   # time_grid
   time_grid = [ 2000.0 ]
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
      { 'name':'max_num_iter_fixed',    'value':'0'},
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
   result_dir = 'build/test'
   at_cascade.empty_directory(result_dir)
   #
   # root_database
   root_database       = f'{result_dir}/root.db'
   root_node_db(root_database)
   #
   # Create all_node.db
   all_node_database = f'{result_dir}/all_node.db'
   option_all        = {
      'result_dir'                : result_dir,
      'root_node_name'            : 'n0',
      'root_database'        : root_database,
   }
   at_cascade.create_all_node_db(
      all_node_database       = all_node_database,
      option_all              = option_all,
   )
   #
   # root_node_dir
   root_node_dir = f'{result_dir}/n0'
   os.mkdir(root_node_dir)
   #
   # cascade starting at root node
   at_cascade.cascade_root_node(
      all_node_database  = all_node_database ,
      fit_goal_set       = fit_goal_set,
      no_ode_fit         = True,
   )
   #
   # var_table, fit_var_table, rate_table, age_table
   fit_database      = f'{result_dir}/n0/dismod.db'
   connection        = dismod_at.create_connection(
      fit_database, new = False, readonly = True
   )
   var_table         = dismod_at.get_table_dict(connection, 'var')
   rate_table        = dismod_at.get_table_dict(connection, 'rate')
   fit_var_table     = dismod_at.get_table_dict(connection, 'fit_var')
   connection.close()
   connection        = dismod_at.create_connection(
      root_database, new = False, readonly = True
   )
   age_table         = dismod_at.get_table_dict(connection, 'age')
   connection.close()
   #
   # check
   for (var_id, var_row) in enumerate(var_table) :
      assert var_row['var_type'] == 'rate'
      #
      # rate_name
      rate_id   = var_row['rate_id']
      rate_name = rate_table[rate_id]['rate_name']
      assert rate_name == 'iota'
      #
      # fit_value
      fit_value = fit_var_table[var_id]['fit_var_value']
      #
      # initial_value
      # max_num_iter_fixed and perturp_optimixzation_start are zero
      # hence the initial mean is the final fit value.
      initial_value = iota_avg
      #
      assert abs( 1.0 - fit_value / initial_value ) < 1e-6
#
if __name__ == '__main__' :
   main()
   print('diff_prior: OK')
