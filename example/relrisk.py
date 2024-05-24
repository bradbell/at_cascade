# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ----------------------------------------------------------------------------
r'''
Change this to docuemtaton for relrisk.py example
(once main() defined below runs without error).
'''
# BEGIN PYTHON
# ----------------------------------------------------------------------------
# imports
# ----------------------------------------------------------------------------
import numpy
import sys
import os
import copy
import dismod_at
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
   'result_dir':                 'build/example',
   'root_node_name':             'n0',
   'refit_split':                'false',
}
option_all['root_node_database'] = option_all['result_dir'] + '/root_node.db'
# END option_all_table
#
# ----------------------------------------------------------------------------
# functions
# ----------------------------------------------------------------------------
# BEGIN rate_true
def rate_true(rate, a, t, n, c) :
   # omega_true
   omega_true = {
      'n3' : 1e-2,
      'n4' : 2e-2,
      'n5' : 3e-2,
      'n6' : 4e-2
   }
   omega_true['n1'] = (omega_true['n3'] + omega_true['n4']) / 2
   omega_true['n2'] = (omega_true['n5'] + omega_true['n6']) / 2
   omega_true['n0'] = (omega_true['n1'] + omega_true['n2']) / 2
   #
   if rate == 'iota' :
      return 1e-3
   elif rate == 'rho' :
      return 0.0
   elif rate == 'chi' :
      return 1e-1
   elif rate == 'omega' :
      return omega_true[n]
   assert False
# END rate_true
# ----------------------------------------------------------------------------
def root_node_db(file_name) :
   #
   # prior_table
   prior_table = list()
   for rate_name in [ 'iota', 'chi' ] :
      rate_0   = rate_true(rate_name, None, None, 'n0', None)
      prior_table.append(
         {  'name':    f'parent_{rate_name}_prior',
            'density': 'uniform',
            'lower':   rate_0 / 10.0,
            'upper':   rate_0 * 10.0,
            'mean':    rate_0 * 2,
         }
      )
   #
   # smooth_table
   smooth_table = list()
   fun = lambda a, t : ( f'parent_iota_prior', None, None)
   smooth_table.append({
      'name':       f'parent_iota_smooth',
      'age_id':     [0],
      'time_id':    [0],
      'fun':        fun,
   })
   fun = lambda a, t : ( f'parent_chi_prior', None, None)
   smooth_table.append({
      'name':       f'parent_chi_smooth',
      'age_id':     [0],
      'time_id':    [0],
      'fun':        fun,
   })
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
   rate_table = list()
   for rate_name in [ 'iota', 'chi' ] :
      rate_table.append( {
         'name':           rate_name,
         'parent_smooth':  f'parent_{rate_name}_smooth',
         'child_smooth':   None ,
      } )
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
      { 'name' : 'Sincidence' } ,
      { 'name' : 'mtexcess' }   ,
      { 'name' : 'relrisk' }    ,
   ]
   #
   # avgint_table
   avgint_table = list()
   for integrand in [ 'Sincidence', 'mtexcess', 'relrisk' ] :
      row = {
         'node':         'n0',
         'subgroup':     'world',
         'weight':       '',
         'time_lower':   2000.0,
         'time_upper':   2000.0,
         'age_lower':    50.0,
         'age_upper':    50.0,
         'integrand':    integrand,
      }
      avgint_table.append( copy.copy(row) )
   #
   # data_table
   data_table  = list()
   leaf_set    = { 'n3', 'n4', 'n5', 'n6' }
   for integrand in [ 'Sincidence', 'mtexcess', 'relrisk' ] :
      row = {
         'subgroup':     'world',
         'weight':       '',
         'time_lower':   2000.0,
         'time_upper':   2000.0,
         'age_lower':      50.0,
         'age_upper':      50.0,
         'integrand':    integrand,
         'density':      'gaussian',
         'hold_out':     False,
      }
      for node in leaf_set :
         #
         # meas_value
         iota    = rate_true('iota',  None, None, node, None)
         chi     = rate_true('chi',   None, None, node, None)
         omega   = rate_true('omega', None, None, node, None)
         relrisk = 1 + chi / omega
         if integrand == 'Sincidence' :
            meas_value = iota
         elif integrand == 'mtexcess' :
            meas_value = chi
         elif integrand == 'relrisk' :
            meas_value = relrisk
         #
         # row
         row['node']       = node
         row['meas_value'] = meas_value
         row['meas_std']   = meas_value / 10.0
         #
         # data_table
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
   # omega_data
   omega_data      = dict()
   for node_id in range(7) :
      node_name             = f'n{node_id}'
      omega_data[node_name] = list()
      omega_data[node_name].append( list() )
      for age_id in omega_grid['age'] :
         for time_id in omega_grid['time'] :
            age    = age_table[age_id]['age']
            time   = time_table[time_id]['time']
            omega  = rate_true('omega', None, None, node_name, None)
            omega_data[node_name][0].append( omega )
   #
   # Create all_node.db
   all_node_database = f'{result_dir}/all_node.db'
   at_cascade.create_all_node_db(
      all_node_database      = all_node_database,
      split_reference_table  = None,
      node_split_table       = None,
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
   # This also erases the avgint table from root_node_database
   avgint_table = at_cascade.extract_avgint( root_node_database )
   #
   # cascade starting at root node
   at_cascade.cascade_root_node(
      all_node_database  = all_node_database ,
      fit_goal_set       = fit_goal_set      ,
   )
   #
   # check results
   for subdir in [ 'n1/n3', 'n1/n4', 'n2/n5', 'n2/n6' ] :
      goal_database = f'{result_dir}/n0/{subdir}/dismod.db'
      at_cascade.check_cascade_node(
         rate_true          = rate_true,
         all_node_database  = all_node_database,
         fit_node_database  = goal_database,
         avgint_table       = avgint_table,
         relative_tolerance = float( numpy.finfo(float).eps * 100.0 ),
      )
#
main()
print('relrisk: OK')
#
sys.exit(0)
# END PYTHON
