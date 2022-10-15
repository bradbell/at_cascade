# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
# imports
# ----------------------------------------------------------------------------
import sys
import os
import copy
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
# alpha_true
alpha_true = - 0.1
#
# avg_income
avg_income       = { 'n1':1.0, 'n2':2.0 }
avg_income['n0'] = ( avg_income['n1'] + avg_income['n2'] ) / 2.0
#
# sum_random_effect
sum_random       = { 'n0': 0.0, 'n1': 0.2, 'n2': -0.2 }
#
# age_grid
age_grid = [0.0, 20.0, 40.0, 60.0, 80.0, 100.0 ]
#
# income_grid
number_income = 5
income_grid   = dict()
for node in [ 'n1', 'n2' ] :
   delta_income      = 2.0 * avg_income[node] / (number_income - 1)
   income_grid[node] = [ j * delta_income for j in range(number_income) ]
# ----------------------------------------------------------------------------
# functions
# ----------------------------------------------------------------------------
# iota_true
def iota_true(a, n = 'n0', I = avg_income['n0'] ) :
   s_n = sum_random[n]
   r_0 = avg_income['n0']
   return (1 + a / 100) * 1e-2 * exp( s_n + alpha_true * ( I - r_0 ) )
# ----------------------------------------------------------------------------
def root_node_db(file_name) :
   #
   # prior_table
   prior_table = [
      {   # prior_iota_n0_value
         'name':    'prior_iota_n0_value',
         'density': 'uniform',
         'lower':   iota_true(0) / 10.0,
         'upper':   iota_true(100) * 10.0,
         'mean':    iota_true(50),
      },{ # prior_iota_dage
         'name':    'prior_iota_dage',
         'density': 'uniform',
         'mean':    0.0,
      },{ # prior_iota_child
         'name':    'prior_iota_child',
         'density': 'uniform',
         'mean':    0.0,
      },{ # prior_alpha_n0
         'name':    'prior_alpha_n0',
         'density': 'uniform',
         'lower':   -abs(alpha_true) * 10,
         'upper':   +abs(alpha_true) * 10,
         'mean':    0.0,
      },
   ]
   #
   # smooth_table
   smooth_table = list()
   #
   # smooth_iota_n0_value
   fun = lambda a, t : ('prior_iota_n0_value', 'prior_iota_dage', None)
   smooth_table.append({
      'name':       'smooth_iota_n0_value',
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
   # smooth_alpha_n0
   fun = lambda a, t : ('prior_alpha_n0', None, None)
   smooth_table.append({
      'name':       'smooth_alpha_n0',
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
      'parent_smooth':  'smooth_iota_n0_value',
      'child_smooth':   'smooth_iota_child' ,
   } ]
   #
   # covariate_table
   covariate_table = [ { 'name':'income',   'reference':avg_income['n0'] } ]
   #
   # mulcov_table
   mulcov_table = [ {
      # alpha
      'covariate':  'income',
      'type':       'rate_value',
      'effected':   'iota',
      'group':      'world',
      'smooth':     'smooth_alpha_n0',
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
   leaf_set    = { 'n1', 'n2' }
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
      for node in leaf_set :
         for income in income_grid[node] :
            meas_value        = iota_true(age, node, income)
            row['node']       = node
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
   # Create all_node.db
   all_node_database = 'all_node.db'
   all_option        = {
      'result_dir':     '.',
      'root_node_name': 'n0',
   }
   at_cascade.create_all_node_db(
      all_node_database       = all_node_database,
      root_node_database      = root_node_database,
      split_reference_table   = list(),
      all_option              = all_option,
   )
   #
   # replace avgint table
   at_cascade.avgint_parent_grid(all_node_database, root_node_database)
   #
   # init
   dismod_at.system_command_prc( [ 'dismod_at', root_node_database, 'init' ] )
   #
   # fit both
   dismod_at.system_command_prc(
      [ 'dismod_at', root_node_database, 'fit', 'both' ]
   )
   #
   # predict
   dismod_at.system_command_prc(
      [ 'dismod_at', root_node_database, 'predict', 'fit_var' ]
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
      #
      # mulcov_id
      mulcov_id = None
      if integrand_name.startswith('mulcov_') :
         mulcov_id = int( integrand_name[7:] )
         assert mulcov_id == 0
         true_value = alpha_true
      #
      # rate_id
      rate_id = None
      if integrand_name == 'Sincidence' :
         rate_id = table_name2id(table['rate'], 'rate_name', 'iota')
         #
         # node_name
         node_id = avgint_row['node_id']
         assert node_id in [ 0, 1, 2 ]
         node_name = table['node'][node_id]['node_name']
         #
         # age
         age_id = avgint_row['c_age_id']
         age    = age_grid[age_id]
         #
         # income
         income = avg_income[node_name]
         #
         # true_value
         true_value = iota_true(age, node_name, income)
      #
      # print(integrand_name, predict_value)
      relative_err = 1.0 - predict_value / true_value
      assert abs( relative_err ) < 1e-7
#
main()
print('avgint_parent_grid.py: OK')
sys.exit(0)
