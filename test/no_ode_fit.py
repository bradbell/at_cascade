# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ----------------------------------------------------------------------------
# BEGIN no_ode_xam source code
# ----------------------------------------------------------------------------
# imports
# ----------------------------------------------------------------------------
# Test no_ode fit for iota with data and chi without data
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
# ----------------------------------------------------------------------------
# functions
# ----------------------------------------------------------------------------
#
# rate_true
def rate_true(rate, a, t) :
   if rate in [ 'pini', 'rho' ] :
      return 0.0
   if rate == 'iota' :
      return (1 + a / 100) * 1e-3
   if rate == 'chi' :
      return (1 + a / 100) * 2e-2
   if rate == 'omega' :
      return (1 + a / 100) * 1e-2
   assert False
# END rate_true
# ----------------------------------------------------------------------------
def average_integrand(integrand_name, age, node_name) :
   def iota(a, t) :
      return rate_true('iota', a, t)
   def chi(a, t) :
      return rate_true('chi', a, t)
   def omega(a, t) :
      return rate_true('omega', a, t)
   rate           = { 'iota': iota,  'chi': chi, 'omega': omega }
   grid           = { 'age' : [age], 'time': [2000.0] }
   abs_tol        = 1e-6
   avg_integrand   = dismod_at.average_integrand(
      rate, integrand_name, grid,  abs_tol
   )
   return avg_integrand
# ----------------------------------------------------------------------------
def root_node_db(file_name) :
   #
   # iota_50, chi_50
   iota_50        = rate_true('iota', 50.0, None )
   chi_50         = rate_true('chi',  50.0, None )
   #
   # prior_table
   prior_table = list()
   #
   prior_table.append(
      # parent_iota_value_prior
      {  'name':    'parent_iota_value_prior',
         'density': 'gaussian',
         'lower':   iota_50 / 10.0,
         'upper':   iota_50 * 10.0,
         'mean':    iota_50,
         'std' :    iota_50 * 10,
      }
   )
   prior_table.append(
      # parent_chi_value_prior
      {  'name':    'parent_chi_value_prior',
         'density': 'gaussian',
         'lower':   chi_50 / 10.0,
         'upper':   chi_50 * 10.0,
         'mean':    chi_50,
         'std':     chi_50 * 10.0,
      }
   )
   #
   prior_table.append(
      # parent_dage_prior
      {  'name':    'parent_dage_prior',
         'density': 'gaussian',
         'mean':    0.0,
         'std':     1.0,
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
   # parent_chi_smooth
   fun = lambda a, t : ('parent_chi_value_prior', 'parent_dage_prior', None)
   smooth_table.append({
      'name':       'parent_chi_smooth',
      'age_id':     range( len(age_grid) ),
      'time_id':    [0],
      'fun':        fun,
   })
   #
   # node_table
   node_table = [
      { 'name':'n0',        'parent':''   },
   ]
   #
   # rate_table
   rate_table = [ {
         'name':           'iota',
         'parent_smooth':  'parent_iota_smooth',
      },{
         'name':           'chi',
         'parent_smooth':  'parent_chi_smooth',
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
      {'name': 'mtexcess' },
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
      'meas_std':     iota_50 * 1e-3,
      'node':         'n0',
   }
   for age in age_grid :
      row['age_lower']  = age
      row['age_upper']  = age
      row['meas_value'] = rate_true('iota', age, None)
      row['meas_std']   = row['meas_value'] * 1e-2
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
      { 'name':'quasi_fixed',           'value':'false'},
      { 'name':'max_num_iter_fixed',    'value':'50'},
      { 'name':'max_num_iter_random',   'value':'200'},
      { 'name':'tolerance_fixed',       'value':'1e-15'},
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
   # omega_grid
   omega_grid = dict()
   omega_grid['age']  = range( len(age_grid) )
   omega_grid['time'] = [ 0 ]
   #
   # mulcov_freeze_table
   mulcov_freeze_table =  list()
   #
   # omega_all_data
   omega_all_data     = dict()
   for node_name in [ 'n0' ] :
      omega_list = list()
      for age_id in omega_grid['age'] :
         age            = age_grid[age_id]
         time           = 2000.0
         integrand_name = 'mtother'
         mtother        = \
            average_integrand(integrand_name, age, node_name)
         omega_list.append(mtother)
      omega_all_data[node_name] = [ omega_list ]
   #
   # Create all_node.db
   all_node_database = f'{result_dir}/all_node.db'
   option_all        = {
      'result_dir'                : result_dir,
      'root_node_name'            : 'n0',
      'root_database'        : root_database,
      'perturb_optimization_scale': .2,
      'perturb_optimization_start': .2,

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
      #
      # fit_value
      fit_value = fit_var_table[var_id]['fit_var_value']
      #
      # true_value
      age        = age_table[ var_row['age_id' ] ]['age']
      true_value = rate_true(rate_name, age, None)
      #
      if rate_name == 'omega' :
         assert fit_value == true_value
      elif rate_name == 'iota' :
         assert abs( 1.0 - fit_value / true_value ) < 1e-6
      else :
         # no data so should match mean
         assert rate_name == 'chi'
         chi_50  = rate_true('chi',  50.0, None )
         assert abs( 1.0 - fit_value / chi_50 ) < 1e-6


#
if __name__ == '__main__' :
   main()
   print('no_ode_xam: OK')
# END no_ode_xam source code
