# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
# imports
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
# avg_income
avg_income       = 1.5
#
# income_grid
income_grid      = [ 0.5 * avg_income, avg_income, 1.5 * avg_income ]
#
# alpha_true
# 2.0 = exp( alpha_true * (income_grid[2] - income_grid[0])
alpha_true = math.log(2.0) / ( income_grid[2] - income_grid[0] )
#
# age_grid
age_grid = [0.0, 20.0, 40.0, 60.0, 80.0, 100.0 ]
#
# fit_goal_set
fit_goal_set = { 'n1', 'n2' }
#
#
# ----------------------------------------------------------------------------
# iota_true
def iota_true(a, I = avg_income) :
   r_0 = avg_income
   return (1 + a / 100) * 1e-2 * math.exp( alpha_true * ( I - r_0 ) )
# ----------------------------------------------------------------------------
def root_node_db(file_name) :
   #
   # prior_table
   prior_table = [
      { # prior_iota_dage
         'name':    'prior_iota_dage',
         'density': 'gaussian',
         'mean':    0.0,
         'std':     0.5,
      },{ # prior_iota_child
         'name':    'prior_iota_child',
         'density': 'gaussian',
         'mean':    0.0,
         'std':     1.0,
      },{ # prior_alpha
         'name':    'prior_alpha',
         'density': 'uniform',
         'lower':   -abs(alpha_true) * 10,
         'upper':   +abs(alpha_true) * 10,
         'mean':    0.0,
      },
   ]
   for a in age_grid :
      mean        = iota_true(a)
      prior_name  = f'prior_iota_value_{a}'
      prior       = {
         'name':    prior_name,
         'density': 'gaussian',
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
   # smooth_alpha
   fun = lambda a, t : ('prior_alpha', None, None)
   smooth_table.append({
      'name':       'smooth_alpha',
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
   covariate_table = [ { 'name':'income',   'reference':avg_income } ]
   #
   # mulcov_table
   mulcov_table = [ {
      # alpha
      'covariate':  'income',
      'type':       'rate_value',
      'effected':   'iota',
      'group':      'world',
      'smooth':     'smooth_alpha',
   } ]
   #
   # subgroup_table
   subgroup_table = [ {'subgroup': 'world', 'group':'world'} ]
   #
   # integrand_table
   integrand_table = [ {'name':'Sincidence'}, {'name':'mulcov_0'} ]
   #
   # avgint_table
   avgint_table = list()
   #
   # data_table
   data_table  = list()
   row = {
      'node':         'n0',
      'subgroup':     'world',
      'weight':       '',
      'time_lower':   2000.0,
      'time_upper':   2000.0,
      'income':       None,
      'integrand':    'Sincidence',
      'density':      'gaussian',
      'hold_out':     False,
   }
   for (age_id, age) in enumerate( age_grid ) :
      for income in income_grid :
         meas_value        = iota_true(age, income)
         row['meas_value'] = meas_value
         row['age_lower']  = age
         row['age_upper']  = age
         row['income']     = income
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
   # fit_node_id
   fit_node_id = int( fit_node_name[-1] )
   #
   # age, var_table, fit_var_table
   new           = False;
   connection    = dismod_at.create_connection(fit_node_database, new)
   age_table     = dismod_at.get_table_dict(connection, 'age')
   var_table     = dismod_at.get_table_dict(connection, 'var')
   fit_var_table = dismod_at.get_table_dict(connection, 'fit_var')
   connection.close()
   #
   for (var_id, row) in enumerate( var_table ) :
      fit_var_value = fit_var_table[var_id]['fit_var_value']
      node_id        = row['node_id']
      if row['var_type'] == 'mulcov_rate_value' :
         true_var_value = alpha_true
      elif node_id == fit_node_id :
         age_id         = row['age_id']
         age            = age_table[age_id]['age']
         income         = avg_income
         true_var_value = iota_true(age, income)
      else :
         true_var_value = 0.0
      #
      if true_var_value == 0.0 :
         rel_error = None
      else :
         rel_error = 1.0 - fit_var_value / true_var_value
         assert abs(rel_error) < 1e-4
# ----------------------------------------------------------------------------
def check_dage_mean(result_dir, fit_node_name) :
   #
   # fit_node_dir
   if fit_node_name == 'n0' :
      fit_node_dir = f'{result_dir}/n0'
   else :
      fit_node_dir = f'{result_dir}/n0/{fit_node_name}'
   #

   #
   # db2csv
   fit_node_database = f'{fit_node_dir}/dismod.db'
   dismod_at.system_command_prc(
      ['dismodat.py', fit_node_database, 'db2csv']
   )
   #
   # variable_table
   file_name       = f'{fit_node_dir}/variable.csv'
   file_ptr        = open(file_name, 'r')
   reader          = csv.DictReader(file_ptr)
   previous_mean_v = None
   previous_age    = None
   for row in reader :
      age      = float( row['age'] )
      mean_v   = float( row['mean_v'] )
      if row['mean_a'] == '' :
         mean_a = None
      else :
         mean_a   = float( row['mean_a'] )
      var_type = row['var_type']
      node     = row['node']
      if var_type == 'rate' :
         assert node == fit_node_name
         if previous_mean_v is not None :
            #
            assert type(previous_age)    == float
            assert type(previous_mean_v) == float
            assert type(previous_mean_a) == float
            #
            diff = mean_v - previous_mean_v
            rel_error = 1.0 - diff / previous_mean_a
            assert abs(rel_error) < 1e-4
      previous_age      = age
      previous_mean_v   = mean_v
      previous_mean_a   = mean_a
# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------
def main() :
   # -------------------------------------------------------------------------
   #
   # result_dir
   result_dir = 'build/test'
   if not os.path.exists(result_dir) :
      os.makedirs(result_dir)
   #
   # root_node.db
   root_node_database  = f'{result_dir}/root_node.db'
   root_node_db(root_node_database)
   #
   # mulcov_freeze_table
   mulcov_freeze_table = [{
      'fit_node_name' :      'n0',
      'split_reference_id' : None,
      'mulcov_id':           0,
   } ]

   #
   # all_option
   all_option        = {
      'result_dir':     result_dir,
      'root_node_name': 'n0',
   }
   #
   # all_node.db
   all_node_database = f'{result_dir}/all_node.db'
   at_cascade.create_all_node_db(
      all_node_database       = all_node_database,
      root_node_database      = root_node_database,
      split_reference_table   = list(),
      all_option              = all_option,
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
      root_node_database = root_node_database,
      fit_goal_set       = fit_goal_set      ,
   )
   #
   for fit_node_name in [ 'n0', 'n1', 'n2' ] :
      check_fit(result_dir, fit_node_name)
   #
   for fit_node_name in [ 'n1', 'n2' ] :
      check_dage_mean(result_dir, fit_node_name)
#
main()
print('no_child_data.py: OK')
sys.exit(0)
