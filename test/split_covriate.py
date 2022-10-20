# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin_parent split_covariate}
{xrst_spell
   dage
   dtime
}

Example Using split_reference Table
###################################
This example splits the analysis by sex.
To simplify the example everything is constant w.r.t. age and time.

Nodes
*****
The following is a diagram of the node tree for this example.
The :ref:`glossary@root_node` is n0,
the :ref:`glossary@fit_goal_set`
and the leaf nodes are {n3, n4, n5, n6}::

            n0
          /-----/\-----\
      n1              n2
       /  \            /  \
     n3    n4        n5    n6

fit_goal_set
============
{xrst_literal
   # BEGIN fit_goal_set
   # END fit_goal_set
}

Rates
*****
The only non-zero dismod_at rates for this example are
:ref:`glossary@iota`.and :ref:`glossary@omega`.

Splitting Covariate
*******************
This cascade is set up to split by the sex covariate at level zero:
{xrst_literal
   # BEGIN all_option_table
   # END all_option_table
}
The :ref:`split_reference_table` for this example is:
{xrst_literal
   # BEGIN split_reference_table
   # END split_reference_table
}
The :ref:`node_split_table` for this example is
{xrst_literal
   # BEGIN node_split_table
   # END node_split_table
}
Note that we have used node_name (instead of node_id) here and let
:ref:`create_all_node_db` do the conversion to node_id.
The cascade computation tree is::

            /-------------n0-------------\
          /---female---\                /----male----\
      n1              n2            n1              n2
       /  \            /  \          /  \            /  \
     n3    n4        n5    n6      n3    n4        n5    n6

The sex reference value for the root node (n0) corresponds to both sexes:
{xrst_literal
   # BEGIN root_split_reference_id
   # END root_split_reference_id
}

Covariate
*********
There is only one covariate for this example, sex.

alpha
=====
We use *alpha*
for the :ref:`glossary@rate_value` covariate multiplier
that multiplies sex.
This multiplier affects the value of iota.
The true value for *alpha* (used which simulating the data) is
{xrst_literal
   # BEGIN alpha_true
   # END alpha_true
}

Random Effects
**************
There are no random effect for this example.

Simulated Data
**************

rate_true(rate, a, t, n, c)
===========================
For *rate* equal to iota or omega,
this is the true value for *rate*
in node *n* at age *a*, time *t*, and covariate values *c=[sex]*.
The covariate values are a list in the same order as the covariate table.
The values *a* and *t* are not used by this function for this example.
{xrst_literal
   # BEGIN rate_true
   # END rate_true
}

y_i
===
The only simulated integrand for this example is :ref:`glossary@Sincidence`
which is a direct measurement of iota.
This data is simulated without any noise; i.e.,
the i-th measurement is simulated as
*y_i = rate_true('iota', None, None, n, [sex])*
where *n* is the node and  *sex* is the sex covariate value.

Cases Simulated
===============
Data is simulated for the leaf nodes for female, male sexes; i.e.,
each *n_i* is in the set { n3, n4, n5, n6 } and the female, male sexes.
Since the data does not have any nose, the data residuals are a measure
of how good the fit is for the nodes in the fit_goal_set below the female
and male sexes.

Parent Rate Smoothing
*********************
This is the iota smoothing used for the fit_node.
There are no :ref:`glossary@dage` or :ref:`glossary@dtime`
priors because there is only one age and one time point in the smoothing grid.

Value Prior
===========
The following is the value prior used for the root_node
{xrst_literal
   # BEGIN parent_value_prior
   # END parent_value_prior
}
The mean and standard deviation are only used for the root_node.
The :ref:`create_shift_db`
routine replaces them for other nodes.

Alpha Smoothing
***************
This is the smoothing used for *alpha* which multiplies the sex covariate.
There is only one age and one time point in this smoothing
so it does not have dage or dtime priors.

Value Prior
===========
The following is the value prior used for this smoothing:
{xrst_literal
   # BEGIN alpha_value_prior
   # END alpha_value_prior
}
The mean and standard deviation are only used for the root_node.
The create_shift_db
routine replaces them for other nodes.

Checking The Fit
****************
The results of the fit are checked by check_cascade_node
using the :ref:`check_cascade_node@avgint_table`
that was created by the root_node_db routine.
The node_id for each row is replaced by the node_id for the
fit being checked.
routine uses these tables to check that fit against the truth.

{xrst_end split_covariate}
------------------------------------------------------------------------------
{xrst_begin split_covariate.py}

split_covariate: Python Source Code
###################################

{xrst_literal
   BEGIN split_covariate source code
   END split_covariate source code
}

{xrst_end split_covariate.py}
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
# BEGIN all_option_table
all_option            = {
   'result_dir':                 'build/test',
   'root_node_name':             'n0',
   'root_split_reference_name':  'both',
   'split_covariate_name':       'sex',
   'shift_prior_std_factor':      1e3,
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
   result_dir = all_option['result_dir']
   if not os.path.exists(result_dir) :
      os.makedirs(result_dir)
   #
   # Create root_node.db
   root_node_database  = f'{result_dir}/root_node.db'
   root_node_db(root_node_database)
   #
   # omega_grid
   new          = False
   connection   = dismod_at.create_connection(root_node_database, new)
   age_table    = dismod_at.get_table_dict(connection, 'age')
   time_table   = dismod_at.get_table_dict(connection, 'time')
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
               cov    = [ sex ]
               omega  = rate_true('omega', None, None, node_name, cov)
               omega_data[node_name][k].append( omega )
   #
   # Create all_node.db
   all_node_database = f'{result_dir}/all_node.db'
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
   # root_node_dir
   root_node_dir = f'{result_dir}/n0'
   if os.path.exists(root_node_dir) :
      # rmtree is very dangerous so make sure root_node_dir is as expected
      assert root_node_dir == 'build/test/n0'
      shutil.rmtree( root_node_dir )
   os.makedirs(root_node_dir )
   #
   # avgint_table
   # also erase avgint table in root node database
   new             = False
   connection      = dismod_at.create_connection(root_node_database, new)
   avgint_table    = dismod_at.get_table_dict(connection, 'avgint')
   empty_table     = list()
   message         = 'erase avgint table'
   tbl_name        = 'avgint'
   dismod_at.replace_table(connection, tbl_name, empty_table)
   at_cascade.add_log_entry(connection, message)
   connection.close()
   #
   # cascade starting at root node
   at_cascade.cascade_root_node(
      all_node_database  = all_node_database ,
      root_node_database = root_node_database,
      fit_goal_set       = fit_goal_set      ,
   )
   #
   # check results
   for sex in [ 'male', 'female' ] :
      for subdir in [ 'n1/n3', 'n1/n4', 'n2/n5', 'n2/n6' ] :
         goal_database = f'{result_dir}/n0/{sex}/{subdir}/dismod.db'
         at_cascade.check_cascade_node(
            rate_true          = rate_true,
            all_node_database  = all_node_database,
            fit_node_database  = goal_database,
            avgint_table       = avgint_table,
            relative_tolerance = 1e-5,
         )
   #
   # fit_iota, fit_alpha
   fit_node_database = f'{result_dir}/n0/dismod.db'
   new               = False
   connection        = dismod_at.create_connection(fit_node_database, new)
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
   # shift_mean
   shift_database    = f'{result_dir}/n0/female/dismod.db'
   new               = False
   connection        = dismod_at.create_connection(shift_database, new)
   rate_table        = dismod_at.get_table_dict(connection, 'rate')
   smooth_grid_table = dismod_at.get_table_dict(connection, 'smooth_grid')
   prior_table       = dismod_at.get_table_dict(connection, 'prior')
   connection.close()
   for row in rate_table :
      if row['rate_name'] == 'iota' :
         smooth_id = row['parent_smooth_id']
   for row in smooth_grid_table :
      if row['smooth_id'] == smooth_id :
         prior_id = row['value_prior_id']
   shift_mean = prior_table[prior_id]['mean']
   #
   # sex_difference
   sex_difference = 0.0
   for row in split_reference_table :
      if row['split_reference_name'] == 'both' :
         sex_difference -= row['split_reference_value']
      if row['split_reference_name'] == 'female' :
         sex_difference += row['split_reference_value']
   #
   # check
   check = fit_iota * exp( fit_alpha * sex_difference )
   assert abs(1.0 - shift_mean/check) < 1e-12
#
main()
print('split_covariate: OK')
sys.exit(0)
# END split_covariate source code
