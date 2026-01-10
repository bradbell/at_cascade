# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ----------------------------------------------------------------------------
r'''
Test freeze_type == posterior using following node table
                n0
               /  \
freeze node = n1    n4
             /
            n2
            /
           n3
The priors for n1 and and n4 are equal.
The priors for n2 and and n3 are equal (and different from n1 and n4).
'''
# ----------------------------------------------------------------------------
# imports
# ----------------------------------------------------------------------------
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
#
# import at_cascade with a preference current directory version
current_directory = os.getcwd()
if os.path.isfile( current_directory + '/at_cascade/__init__.py' ) :
   sys.path.insert(0, current_directory)
import at_cascade
# -----------------------------------------------------------------------------
# global variables
# -----------------------------------------------------------------------------
# fit_goal_set
fit_goal_set = { 'n3', 'n4' }
# random_seed
random_seed = 0
if random_seed == 0 :
   random_seed = int( time.time() )
random.seed(random_seed)
print('mulcov_freeze: random_seed = ', random_seed)
#
# no_effect_iota
no_effect_iota = 1e-3;
#
# no_effect_omega
no_effect_omega = 2e-3;
#
# alpha_true, alpha_true_max_abs
alpha_true = { 'n0': 1.0, 'n1': 0.0, 'n2':-0.5, 'n3':-0.5, 'n4':-1.0  }
alpha_true_max_abs = 1.0
#
# average_income
avg_income = 1.0
#
# node_list
node_set = set( alpha_true.keys() )
#
#
# age_grid
age_grid = [0.0, 50.0, 100.0 ]
#
# income_grid
n_income_grid = 3
d_income_grid = 2.0 * avg_income / (n_income_grid - 1)
income_grid = [ j * d_income_grid for j in range(n_income_grid) ]
# ----------------------------------------------------------------------------
# functions
# ----------------------------------------------------------------------------
#
# rate_true
def rate_true(rate, a, t, n, income) :
   if rate in [ 'pini', 'rho', 'chi' ] :
      return 0.0
   I_n      = avg_income
   if rate == 'iota' :
      effect   = alpha_true[n] * ( income - I_n )
      return no_effect_iota * math.exp( effect  )
   if rate == 'omega' :
      effect   = (a - 50) / 100
      return  no_effect_omega * math.exp( effect)
   assert False
#
# average_integrand
def average_integrand(integrand_name, age, node_name, income) :
   def iota(a, t) :
      return rate_true('iota', a, t, node_name, income)
   def omega(a, t) :
      return rate_true('omega', a, t, node_name, income)
   rate           = { 'iota': iota,  'omega': omega }
   grid           = { 'age' : [age], 'time': [2000.0] }
   abs_tol        = 1e-6
   avg_integrand   = dismod_at.average_integrand(
      rate, integrand_name, grid,  abs_tol
   )
   return avg_integrand
# ----------------------------------------------------------------------------
def root_node_db(file_name) :
   #
   # prior_table
   prior_table = list()
   #
   # parent_iota_value_prior
   prior_table.append(
      {   'name':    'parent_iota_value_prior',
         'density': 'uniform',
         'lower':   no_effect_iota / 10.0,
         'upper':   no_effect_iota * 10.0,
         'mean':    no_effect_iota,
      }
   )
   #
   # parent_dage_prior
   prior_table.append(
      {  'name':    'parent_dage_prior',
         'density': 'log_gaussian',
         'mean':    0.0,
         'std':     4.0,
         'eta':     no_effect_iota * 1e-3,
      }
   )
   #
   # alpha_value_prior
   prior_table.append(
      {   'name':    'alpha_value_prior',
         'density': 'uniform',
         'lower':   - 10 * alpha_true_max_abs,
         'upper':   + 10 * alpha_true_max_abs,
         'std'  :     10 * alpha_true_max_abs,
         'mean':    0.0,
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
      { 'name':'n2',        'parent':'n1' },
      { 'name':'n3',        'parent':'n2' },
      { 'name':'n4',        'parent':'n0' },
   ]
   #
   # rate_table
   rate_table = [ {
         'name':           'iota',
         'parent_smooth':  'parent_iota_smooth',
         'child_smooth':   None ,
   } ]
   #
   # covariate_table
   covariate_table = [
      { 'name':'income',   'reference':avg_income },
   ]
   #
   # mulcov_table
   mulcov_table = [
      {   # alpha_iota
         'covariate':  'income',
         'type':       'rate_value',
         'effected':   'iota',
         'group':      'world',
         'smooth':     'alpha_smooth',
      }
   ]
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
   integrand         = 'Sincidence'
   time              = 2000.0
   for node in node_set :
      row = {
         'subgroup':     'world',
         'weight':       '',
         'time_lower':   time,
         'time_upper':   time,
         'density':      'log_gaussian',
         'hold_out':     False,
      }
      row_list       = list()
      #
      max_meas_value = 0.0
      for (age_id, age) in enumerate( age_grid ) :
         for income in income_grid :
            row['node']       = node
            row['age_lower']  = age
            row['age_upper']  = age
            row['income']     = income
            meas_value        = rate_true( 'iota', age, time, node, income )
            row['integrand']  = integrand
            row['meas_value'] = meas_value
            max_meas_value  = max( meas_value, max_meas_value)
            row_list.append( copy.copy(row) )
      n_row = len(age_grid) * len(income_grid)
      assert len(row_list) == n_row
      for row in row_list :
         # The model for the measurement noise is small so a few
         # data points act like lots of real data points.
         # The actual measruement noise is zero.
            if row['integrand'] == integrand :
               row['meas_std'] = max_meas_value
               row['eta']      = 1e-4 * max_meas_value
      #
      data_table += row_list
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
      { 'name': 'zero_sum_child_rate',  'value':'iota chi'},
      { 'name':'quasi_fixed',           'value':'false'},
      { 'name':'max_num_iter_fixed',    'value':'50'},
      { 'name':'max_num_iter_random',   'value':'200'},
      { 'name':'tolerance_fixed',       'value':'1e-10'},
      { 'name':'tolerance_random',      'value':'1e-10'},
      { 'name':'random_seed',           'value':str(random_seed)},
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
# ---------------------------------------------------------------------------
def main() :
   # -------------------------------------------------------------------------
   # result_dir
   result_dir = 'build/test'
   at_cascade.empty_directory(result_dir)
   #
   # Create root.db
   root_database       = f'{result_dir}/root.db'
   root_node_db(root_database)
   #
   # omega_grid
   omega_grid = dict()
   omega_grid['age']  = range( len(age_grid) )
   omega_grid['time'] = [ 0 ]
   #
   # mulcov_freeze_table
   mulcov_freeze_table =  [
      { 'fit_node_name' : 'n1', 'split_reference_id' : None, 'mulcov_id' : 0 },
   ]
   #
   # omega_all_data
   omega_all_data     = dict()
   for node_name in node_set :
      omega_list = list()
      income     = avg_income
      for age_id in omega_grid['age'] :
         age            = age_grid[age_id]
         time           = 2000.0
         integrand_name = 'mtother'
         mtother        = rate_true( 'omega', age, time, node_name, income )
         omega_list.append(mtother)
      omega_all_data[node_name] = [ omega_list ]
   #
   # Create all_node.db
   all_node_database = f'{result_dir}/all_node.db'
   option_all        = {
      'result_dir'         : result_dir,
      'root_node_name'     : 'n0',
      'root_database'      : root_database,
      'freeze_type'        : 'posterior',
   }
   at_cascade.create_all_node_db(
      all_node_database       = all_node_database,
      option_all              = option_all,
      omega_grid              = omega_grid,
      omega_data              = omega_all_data,
      mulcov_freeze_table     = mulcov_freeze_table,
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
      no_ode_fit         = False,
   )
   #
   # mulcov_prior_dict
   mulcov_prior_dict = dict()
   #
   # directory
   directory_list = [ 'n0', 'n0/n1', 'n0/n1/n2', 'n0/n1/n2/n3', 'n0/n4' ]
   for directory in directory_list :
      #
      # node
      node = directory.split('/')[-1]
      #
      # prior_table, mulcov_table, smooth_table, smooth_grid_table
      database = f'{result_dir}/{directory}/dismod.db'
      connection = dismod_at.create_connection(
         file_name = database, new = False, readonly = False
      )
      prior_table  = dismod_at.get_table_dict(connection, tbl_name = 'prior')
      mulcov_table = dismod_at.get_table_dict(connection, tbl_name = 'mulcov')
      smooth_table = dismod_at.get_table_dict(connection, tbl_name = 'smooth')
      smooth_grid_table = dismod_at.get_table_dict(
         connection, tbl_name = 'smooth_grid'
      )
      connection.close()
      #
      # smooth_row
      assert len(mulcov_table) == 1
      smooth_id   = mulcov_table[0]['group_smooth_id']
      smooth_row  = smooth_table[smooth_id]
      assert smooth_row['n_age'] == 1 and smooth_row['n_time'] == 1
      #
      # value_prior_id
      value_prior_id = None
      for grid_row in smooth_grid_table :
         if grid_row['smooth_id'] == smooth_id :
            value_prior_id = grid_row['value_prior_id']
      #
      # mulcov_prior_dict
      mulcov_prior_dict[node] = prior_table[value_prior_id]
   #
   # lower and upper
   for node in mulcov_prior_dict :
      prior = mulcov_prior_dict[node]
      assert prior['lower'] ==  - 10 * alpha_true_max_abs
      assert prior['upper'] ==  + 10 * alpha_true_max_abs
   #
   # mean
   assert mulcov_prior_dict['n0']['mean'] == 0.0
   assert mulcov_prior_dict['n1']['mean'] != 0.0
   assert mulcov_prior_dict['n2']['mean'] != mulcov_prior_dict['n1']['mean']
   #
   assert mulcov_prior_dict['n1'] == mulcov_prior_dict['n4']
   assert mulcov_prior_dict['n2'] == mulcov_prior_dict['n3']
#
if __name__ == '__main__' :
   main()
   print('mulcov_freeze: OK')
