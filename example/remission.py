# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin_parent remission}
{xrst_spell
   dage
   dtime
   rho
}

Example Estimation With Remission and No Incidence Data
#######################################################
For this example everything is constant in time so the
functions below do not depend on time.

Nodes
*****
The following is a diagram of the node tree for this example.
The :ref:`glossary@root_node` is n0,
the :ref:`glossary@fit_goal_set` is equal to the leaf set
{n3, n4, n5, n6}::

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
The non-zero dismod_at rates for this example are
:ref:`glossary@iota`, :ref:`glossary@rho`, and :ref:`glossary@omega`.
For *rate* equal to iota, rho, and omega,
we use *rate(a, n)* to denote the value for *rate*
as a function of age *a* and node *n*.


Covariate
*********
There are not covariates for this example.

Random Effects
**************
For each node, there is a random effect on iota an rho that is constant
in age and time. Note that the total effect for a leaf is the sum
of its random effect plus its parents random effect.

s_n
===
We use *s_n* to denote the sum of the random effects for node *n*.
The code below sets this sum using the name sum_random:
{xrst_literal
   # BEGIN sum_random
   # END sum_random
}

Simulated Data
**************

Random Seed
===========
The random seed can be used to reproduce results.
If the original value of this setting is zero, the clock is used get
a random seed. The actual value or *random_seed* is always printed.
{xrst_literal
   # BEGIN random_seed
   # END random_seed
}

rate_true(rate, a, t, n, c)
===========================
For *rate* equal to iota, rho, omega,
this is the true value for *rate*
in node *n* at age *a*, time *t*, and covariate values *c*.
The time and covariate list are not used.
{xrst_literal
   # BEGIN rate_true
   # END rate_true
}

y_i
===
The simulated integrand for this example are
:ref:`glossary@Sincidence`, and :ref:`glossary@prevalence`.
The data is simulated without any noise
but it is modeled as having noise.

n_i
===
Data is only simulated for the leaf nodes; i.e.,
each *n_i* is in the set { n3, n4, n5, n6 }.
Since the data does not have any nose, the data residuals are a measure
of how good the fit is for the nodes in the fit_goal_set.

a_i
===
For each leaf node, data is generated on the following *age_grid*:
{xrst_literal
   # BEGIN age_grid
   # END age_grid
}

Omega Constraints
*****************
The :ref:`omega_constraint` routine is used
to set the value of omega in the parent and child nodes.

Parent Rate Smoothing
*********************

iota
====
This is the smoothing used in the fit_node model for iota.
Note that the value part of this smoothing is only used for the *root_node*.
This smoothing uses the *age_gird* and one time point.
There are no :ref:`glossary@dtime` priors because there is only one time point.

Parent Rate Priors
==================
The following is the value and dage priors used for the root_node
{xrst_literal
   # BEGIN parent_prior
   # END parent_prior
}
The mean and standard deviation are only used for the root_node.
The :ref:`create_shift_db`
routine replaces them for other nodes.

Child Rate Smoothing
********************
This is the smoothing used for the
random effect for each child of the fit_node.
There are no :ref:`glossary@dage` or dtime
priors because there is only one age and one time point in this smoothing.

Value Prior
===========
The following is the value prior used for the children of the fit_node:
{xrst_literal
   # BEGIN child_value_prior
   # END child_value_prior
}

Checking The Fit
****************
The results of the fit are checked by check_cascade_node
using the :ref:`check_cascade_node@avgint_table`
that was created by the root_node_db routine.
The node_id for each row is replaced by the node_id for the
fit being checked.
routine uses these tables to check that fit against the truth.

{xrst_end remission}
------------------------------------------------------------------------------
{xrst_begin remission.py}

remission: Python Source Code
#############################

{xrst_literal
   BEGIN remission source code
   END remission source code
}

{xrst_end remission.py}
'''
# BEGIN remission source code
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
# BEGIN fit_goal_set
fit_goal_set = { 'n3', 'n4', 'n5', 'n6' }
# END fit_goal_set
#
# BEGIN random_seed
# random_seed = 1629371067
random_seed = 0
if random_seed == 0 :
   random_seed = int( time.time() )
random.seed(random_seed)
print('remission: random_seed = ', random_seed)
# END random_seed
#
# BEGIN sum_random_effect
size_level1      = 0.2
size_level2      = 0.2
sum_random       = { 'n0': 0.0, 'n1': size_level1, 'n2': -size_level1 }
sum_random['n3'] = sum_random['n1'] + size_level2;
sum_random['n4'] = sum_random['n1'] - size_level2;
sum_random['n5'] = sum_random['n2'] + size_level2;
sum_random['n6'] = sum_random['n2'] - size_level2;
# END sum_random_effect
#
# BEGIN age_grid
age_grid = [0.0, 20.0, 40.0, 60.0, 80.0, 100.0 ]
# END age_grid
#
# ----------------------------------------------------------------------------
# functions
# ----------------------------------------------------------------------------
# BEGIN rate_true
def rate_true(rate, a, t, n, c) :
   effect = sum_random[n]
   if rate == 'iota' :
      return (1 + a / 100) * 1e-3 * math.exp(effect)
   if rate == 'rho' :
      return (1 + a / 100) * 1e-1 * math.exp(effect)
   if rate == 'omega' :
      return (1 + a / 100) * 1e-2 * math.exp(effect)
   return 0.0
# END rate_true
# ----------------------------------------------------------------------------
def average_integrand(integrand_name, age, node_name) :
   c = list()
   def iota(a, t) :
      return rate_true('iota', a, None, node_name, None)
   def rho(a, t) :
      return rate_true('rho', a, None, node_name, None)
   def omega(a, t) :
      return rate_true('omega', a, None, node_name, None)
   rate           = { 'iota': iota,  'rho': rho,   'omega': omega }
   grid           = { 'age' : [age], 'time': [2000.0] }
   abs_tol        = 1e-6
   avg_integrand   = dismod_at.average_integrand(
      rate, integrand_name, grid,  abs_tol
   )
   return avg_integrand
# ----------------------------------------------------------------------------
def root_node_db(file_name) :
   #
   #
   # prior_table
   prior_table = list()
   # BEGIN parent_prior
   for rate in [ 'iota', 'rho' ] :
      rate_50  = rate_true(rate, 50.0, None, 'n0', None)
      prior_table.append( {
         'name':    f'{rate}_value_prior',
         'density': 'gaussian',
         'lower':   rate_50 / 10.0,
         'upper':   rate_50 * 10.0,
         'mean':    rate_50,
         'std':     rate_50 * 10.0,
         'eta':     rate_50 * 1e-3,
      } )
      prior_table.append( {
         'name':    f'{rate}_dage_prior',
         'density': 'log_gaussian',
         'mean':    0.0,
         'std':     4.0,
         'eta':     rate_50 * 1e-3,
      } )
   # END parent_prior
   prior_table.append(
      # BEGIN child_value_prior
      {   'name':    'child_value_prior',
         'density': 'gaussian',
         'mean':    0.0,
         'std':     1.0,
      }
      # END child_value_prior
   )
   #
   # smooth_table
   smooth_table = list()
   #
   # iota_smooth
   fun = lambda a, t : ('iota_value_prior', 'iota_dage_prior', None)
   smooth_table.append({
      'name':       'iota_smooth',
      'age_id':     range( len(age_grid) ),
      'time_id':    [0],
      'fun':        fun,
   })
   #
   # rho_smooth
   fun = lambda a, t : ('rho_value_prior', 'rho_dage_prior', None)
   smooth_table.append({
      'name':       'rho_smooth',
      'age_id':     range( len(age_grid) ),
      'time_id':    [0],
      'fun':        fun,
   })
   #
   # child_smooth
   fun = lambda a, t : ('child_value_prior', None, None)
   smooth_table.append({
      'name':       'child_smooth',
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
   rate_table = [
      {   'name':           'iota',
         'parent_smooth':  'iota_smooth',
         'child_smooth':   'child_smooth' ,
      },
      {   'name':           'rho',
         'parent_smooth':  'rho_smooth',
         'child_smooth':   'child_smooth' ,
      },

   ]
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
      {'name': 'remission'},
      {'name': 'prevalence'},
   ]
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
      'integrand':    'Sincidence',
   }
   for age in age_grid :
      row['age_lower'] = age
      row['age_upper'] = age
      avgint_table.append( copy.copy(row) )
   #
   # data_table
   data_table = list()
   leaf_set   = { 'n3', 'n4', 'n5', 'n6' }
   for node in leaf_set :
      for integrand_name in [ 'remission', 'prevalence' ] :
         row = {
            'node':         node,
            'subgroup':     'world',
            'weight':       '',
            'time_lower':   2000.0,
            'time_upper':   2000.0,
            'integrand':    integrand_name,
            'density':      'log_gaussian',
            'hold_out':     False,
         }
         row_list       = list()
         max_meas_value = 0.0
         for (age_id, age) in enumerate( age_grid ) :
            meas_value = average_integrand(
               integrand_name, age, node
            )
            row['meas_value'] = meas_value
            row['age_lower']  = age
            row['age_upper']  = age
            max_meas_value    = max(meas_value, max_meas_value)
            row_list.append( copy.copy(row) )
         for row in row_list :
            # The model for the measurement noise is small so a few
            # data points act like lots of real data points.
            # The actual measruement noise is zero.
            row['meas_std'] = max_meas_value / 50.0
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
      { 'name':'rate_case',             'value':'iota_pos_rho_pos'},
      { 'name': 'zero_sum_child_rate',  'value':'iota'},
      { 'name':'quasi_fixed',           'value':'false'},
      { 'name':'max_num_iter_fixed',    'value':'50'},
      { 'name':'tolerance_fixed',       'value':'1e-10'},
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
   result_dir = 'build/example'
   if not os.path.exists(result_dir) :
      os.makedirs(result_dir)
   #
   # Create root_node.db
   root_node_database  = f'{result_dir}/root_node.db'
   root_node_db(root_node_database)
   #
   # omega_grid
   omega_grid = dict()
   omega_grid['age']  = range( len(age_grid) )
   omega_grid['time'] = [ 0 ]
   #
   # omega_data
   integrand_name = 'mtother'
   omega_data     = dict()
   for node_name in [ 'n0', 'n1', 'n2', 'n3', 'n4', 'n5', 'n6' ] :
      omega_list = list()
      for age_id in omega_grid['age'] :
         age     = age_grid[age_id]
         time    = 2000.0
         mtother = average_integrand(integrand_name, age, node_name)
         omega_list.append(mtother)
      omega_data[node_name] = [ omega_list ]
   #
   # Create all_node.db
   all_node_database = f'{result_dir}/all_node.db'
   all_option        = {
      'result_dir'          : result_dir,
      'root_node_name'      : 'n0',
   }
   at_cascade.create_all_node_db(
      all_node_database       = all_node_database,
      root_node_database      = root_node_database,
      all_option              = all_option,
      omega_grid              = omega_grid,
      omega_data              = omega_data,
   )
   #
   # root_node_dir
   root_node_dir = f'{result_dir}/n0'
   if os.path.exists(root_node_dir) :
      # rmtree is very dangerous so make sure root_node_dir is as expected
      assert root_node_dir == 'build/example/n0'
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
   for goal_dir in [ 'n0/n1/n3', 'n0/n1/n4', 'n0/n2/n5', 'n0/n2/n6' ] :
      goal_database = f'{result_dir}/{goal_dir}/dismod.db'
      at_cascade.check_cascade_node(
         rate_true = rate_true,
         all_node_database  = all_node_database,
         fit_node_database  = goal_database,
         avgint_table       = avgint_table,
         relative_tolerance = 0.05,
      )
   #
#
main()
print('remission: OK')
sys.exit(0)
# END remission source code
