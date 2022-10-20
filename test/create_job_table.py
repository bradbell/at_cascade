# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
                         (n0,s1)
             (n1,s1)                     (n2,s1)
   (n1,s0)          (n1,s2)         (n5,s1) (n6,s1)
(n3,s0) (n4,s0)  (n3,s2) (n4,s2)
'''
check_job_table = [
# (n0,s1) j0
{ 'fit_node_id' : 0,  'split_reference_id' : 1, 'parent_job_id' : None },
# (n1,s1) j1
{ 'fit_node_id' : 1,  'split_reference_id' : 1, 'parent_job_id' : 0    },
# (n2,s1) j2
{ 'fit_node_id' : 2,  'split_reference_id' : 1, 'parent_job_id' : 0    },
# (n1,s0) j3
{ 'fit_node_id' : 1,  'split_reference_id' : 0, 'parent_job_id' : 1    },
# (n1,s2) j4
{ 'fit_node_id' : 1,  'split_reference_id' : 2, 'parent_job_id' : 1    },
# (n5,s1) j5
{ 'fit_node_id' : 5,  'split_reference_id' : 1, 'parent_job_id' : 2    },
# (n5,s1) j6
{ 'fit_node_id' : 6,  'split_reference_id' : 1, 'parent_job_id' : 2    },
# (n3,s0) j7
{ 'fit_node_id' : 3,  'split_reference_id' : 0, 'parent_job_id' : 3    },
# (n4,s0) j8
{ 'fit_node_id' : 4,  'split_reference_id' : 0, 'parent_job_id' : 3    },
# (n3,s2) j9
{ 'fit_node_id' : 3,  'split_reference_id' : 2, 'parent_job_id' : 4    },
# (n4,s2) j10
{ 'fit_node_id' : 4,  'split_reference_id' : 2, 'parent_job_id' : 4    },
]
#
for job_id in range(5) :
   check_job_table[job_id]['start_child_job_id'] = 2 * job_id + 1
   check_job_table[job_id]['end_child_job_id']   = 2 * job_id + 3
#
for job_id in range(5, 11) :
   check_job_table[job_id]['start_child_job_id'] = len(check_job_table)
   check_job_table[job_id]['end_child_job_id']   = len(check_job_table)
# -----------------------------------------------------------------------------
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
# BEGIN all_option_table
all_option            = {
   'result_dir':                  '.',
   'root_node_name':              'n0',
   'root_split_reference_name':   'both',
   'split_covariate_name':        'sex',
   'shift_prior_std_factor':       1e3,
}
# END all_option_table
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
node_split_table = [ { 'node_name' :   'n1'} ]
# END node_split_table
#
# BEGIN root_split_reference_id
root_split_reference_id = 1
assert  \
split_reference_table[root_split_reference_id]['split_reference_name']=='both'

# END root_split_reference_id
#
# BEGIN avg_income
avg_income = dict()
for node_id in range(7) :
   node_name = 'n' + str(node_id)
   avg_income[node_name] = [ 1.0 - node_id / 10.0, 1.0, 1.0 + node_id / 10.0 ]
# END avg_income
#
# BEGIN alpha_true
alpha_true = - 0.2
# END alpha_true
# ----------------------------------------------------------------------------
# functions
# ----------------------------------------------------------------------------
# BEGIN rate_true
def rate_true(rate, a, t, n, c) :
   # true_iota
   true_iota = {
      'n3' : 1e-2,
      'n4' : 2e-2,
      'n5' : 3e-2,
      'n6' : 4e-2
   }
   true_iota['n1'] = (true_iota['n3'] + true_iota['n4']) / 2.9
   true_iota['n2'] = (true_iota['n5'] + true_iota['n6']) / 2.9
   true_iota['n0'] = (true_iota['n1'] + true_iota['n2']) / 2.9
   #
   # effect
   sex    = c[0]
   income = c[1]
   #
   # split_reference_id
   split_reference_id = None
   for (row_id, row) in enumerate(split_reference_table) :
      if row['split_reference_value'] == sex :
         split_reference_id = row_id
   #
   r_income = avg_income[n][split_reference_id]
   effect   = alpha_true * ( income - r_income )
   #
   if rate == 'iota' :
      return true_iota[n] * exp(effect)
   if rate == 'omega' :
      return 2.0 * true_iota[n] * exp(effect)
   return 0.0
# END rate_true
# ----------------------------------------------------------------------------
def root_node_db(file_name) :
   #
   # iota_n0
   sex       = split_reference_list[root_split_reference_id]
   income    = avg_income['n0'][root_split_reference_id]
   c         = [ sex, income ]
   iota_n0   = rate_true('iota', None, None, 'n0', c)
   # END iota_50
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
   income =  avg_income['n0'][root_split_reference_id]
   covariate_table.append(
      { 'name': 'sex',      'reference': sex, 'max_difference': 1.1 }
   )
   covariate_table.append( { 'name':  'income',  'reference': income } )
   #
   # mulcov_table
   mulcov_table = [ {
      # alpha
      'covariate':  'income',
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
      'income':       None,
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
         sex      = split_reference_list[split_reference_id]
         r_income = avg_income[node][split_reference_id]
         for factor in [ 0.5, 1.0, 2.0 ] :
            income = factor * r_income
            c      = [sex, income]
            meas_value = rate_true('iota', None, None, node, c)
            row['node']       = node
            row['meas_value'] = meas_value
            row['sex']        = sex
            row['income']     = income
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
   # wrok_dir
   work_dir = 'build/example'
   if not os.path.exists(work_dir) :
      os.makedirs(work_dir)
   os.chdir(work_dir)
   #
   # Create root_node.db
   root_node_database  = 'root_node.db'
   root_node_db(root_node_database)
   #
   # node_table, age_table, time_table
   new          = False
   connection   = dismod_at.create_connection(root_node_database, new)
   node_table   = dismod_at.get_table_dict(connection, 'node')
   age_table    = dismod_at.get_table_dict(connection, 'age')
   time_table   = dismod_at.get_table_dict(connection, 'time')
   connection.close()
   #
   # check_job_table
   for (job_id, row) in enumerate(check_job_table) :
      fit_node_id          = row['fit_node_id']
      node_name            = node_table[fit_node_id]['node_name']
      split_reference_id   = row['split_reference_id']
      split_reference_name = \
         split_reference_table[split_reference_id]['split_reference_name']
      job_name = f'{node_name}.{split_reference_name}'
      check_job_table[job_id]['job_name'] = job_name
   #
   # omega_grid
   age_id_list  = list( range( len(age_table) ) )
   time_id_list = list( range( len(age_table) ) )
   omega_grid   = { 'age': age_id_list, 'time' : time_id_list }
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
               income = avg_income[node_name][k]
               cov    = [ sex, income ]
               omega  = rate_true('omega', None, None, node_name, cov)
               omega_data[node_name][k].append( omega )
   #
   # Create all_node.db
   all_node_database = 'all_node.db'
   at_cascade.create_all_node_db(
      all_node_database      = all_node_database,
      root_node_database     = root_node_database,
      split_reference_table  = split_reference_table,
      node_split_table       = node_split_table,
      all_option             = all_option,
      omega_grid             = omega_grid,
      omega_data             = omega_data,
   )
   #
   # job_table
   root_node_id = 0
   job_table = at_cascade.create_job_table(
      all_node_database         = all_node_database,
      node_table                = node_table,
      start_node_id             = root_node_id,
      start_split_reference_id  = root_split_reference_id,
      fit_goal_set              = fit_goal_set,
   )
   assert job_table == check_job_table
#
main()
print('create_job_table: OK')
sys.exit(0)
