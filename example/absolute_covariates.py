# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin_parent absolute_covariates}
{xrst_spell
   dage
   dtime
}

Example Using absolute_covariates Option in all_node_database
#############################################################
For this example everything is constant w.r.t. age and time.

Nodes
*****
The following is a diagram of the node tree for this example.
The :ref:`glossary@root_node` is n0,
the :ref:`glossary@fit_goal_set` is {n3, n4, n2},
and the leaf nodes are {n3, n4, n5, n6}::

                n0
          /-----/\-----\
        n1             (n2)
       /  \            /  \
    (n3)  (n4)       n5    n6

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
===================
This cascade is set up to split by sex reference value; see
:ref:`split_reference_table`
{xrst_literal
   # BEGIN split_reference_table
   # END split_reference_table
}

Covariate
*********
There are three covariates for this example, sex, vaccine, and income.
Income is the only :ref:`glossary@Relative Covariate`.
{xrst_literal
   # BEGIN avg_income
   # END avg_income
}
{xrst_literal
   # BEGIN split_reference_list
   # END split_reference_list
}

absolute_covariates
===================
The only absolute covariate in this example is vaccine
(0 for no vaccine, 1 for yes vaccine).
{xrst_literal
   # BEGIN_1 absolute_covariates
   # END_1 absolute_covariates
}

alpha
=====
We use *alpha*\ ``[income]``
and  *alpha*\ ``[vaccine]``
for the :ref:`glossary@rate_value` covariate multipliers
that multiply the income and vaccine covariates.
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
in node *n* at age *a*, time *t*, and covariate values *c=[sex,income]*.
The covariate values are a list in the
same order as the covariate table.
The values *a*, *t*, *n*, *sex*
are not used by this function for this example.
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
*y_i = rate_true('iota', None, None, None, [None, I_i])*
where *I_i* is the income for the i-th measurement.
The data is modeled as having noise even though there is no simulated noise.

n_i
===
Data is only simulated for the leaf nodes; i.e.,
each *n_i* is in the set { n3, n4, n5, n6 }.
Since the data does not have any nose, the data residuals are a measure
of how good the fit is for the nodes in the fit_goal_set.

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
This is the smoothing used for *alpha* which multiplies the income covariate.
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

{xrst_end absolute_covariates}
------------------------------------------------------------------------------
{xrst_begin absolute_covariates.py}

absolute_covariates: Python Source Code
#######################################

{xrst_literal
   BEGIN_2 absolute_covariates source code
   END_2 absolute_covariates source code
}

{xrst_end absolute_covariates.py}
'''
# BEGIN_2 absolute_covariates source code
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
fit_goal_set = { 'n3', 'n4', 'n2' }
# END fit_goal_set
#
# BEGIN split_reference_table
all_option            = {
   'result_dir':                'build/example',
   'root_node_name':            'n0',
   'root_split_reference_name': 'both',
   'split_covariate_name':      'sex',
}
split_reference_table = [
   {'split_reference_name': 'female', 'split_reference_value': 1.0},
   {'split_reference_name': 'both',   'split_reference_value': 2.0},
   {'split_reference_name': 'male',   'split_reference_value': 3.0},
]
# END split_reference_table
#
# BEGIN split_index
split_index = 2
# END split_index
#
# BEGIN avg_income
avg_income = dict()
leaf_node_set     = { 3, 4, 5, 6 }
for node_id in leaf_node_set :
   node_name = 'n' + str(node_id)
   avg_income[node_name] = [ 1.0 - node_id / 10.0, 1.0, 1.0 + node_id / 10.0 ]
# child_list
# children of node 0, 1, 2 in that order
child_list = [ (1,2), (3,4), (5,6) ]
for node_id in [2, 1, 0] :
   avg_list = list()
   for split_reference_id in range(3) :
      avg = 0.0
      for child_id in child_list[node_id] :
         child_name = 'n' + str(child_id)
         avg += avg_income[child_name][split_reference_id]
      avg = avg / len( child_list[node_id] )
      avg_list.append( avg )
   node_name = 'n' + str(node_id)
   #
   avg_income[node_name] = avg_list
# END avg_income
#
# BEGIN alpha_true
alpha_true = {'vaccine': -0.3,  'income': -0.2}
# END alpha_true
#
# BEGIN split_reference_list
split_reference_list = list()
for row in split_reference_table :
   split_reference_list.append( row['split_reference_value'] )
# END split_reference_list
#
# BEGIN_1 absolute_covariates
all_option['absolute_covariates'] = 'vaccine'
# END_1 absolute_covariates
# ----------------------------------------------------------------------------
# functions
# ----------------------------------------------------------------------------
# BEGIN rate_true
def rate_true(rate, a, t, n, c) :
   sex     = c[0]
   vaccine = c[1]
   income  = c[2]
   r_0     = avg_income['n0'][split_index]
   effect  = alpha_true['income']*(income - r_0)
   effect += alpha_true['vaccine'] * vaccine
   if rate == 'iota' :
      return 1e-2 * exp(effect)
   if rate == 'omega' :
      return 2e-2 * exp(effect)
   return 0.0
# END rate_true
# ----------------------------------------------------------------------------
def root_node_db(file_name) :
   #
   # iota_n0
   sex     = split_reference_list[split_index]
   vaccine = 0.0
   income  = avg_income['n0'][split_index]
   covariate_list = [ sex, vaccine, income ]
   iota_n0        = rate_true('iota', None, None, None, covariate_list)
   # END iota_50
   #
   # prior_table
   prior_table = list()
   prior_table = [
      # BEGIN parent_value_prior
      {   'name':    'parent_value_prior',
         'density': 'gaussian',
         'lower':   iota_n0 / 10.0,
         'upper':   iota_n0 * 10.0,
         'mean':    iota_n0 ,
         'std':     iota_n0 * 10.0,
         'eta':     iota_n0 * 1e-3
      },
      # END parent_value_prior
      # BEGIN alpha_value_prior
      {
         'name':    'alpha_vaccine_value_prior',
         'density': 'gaussian',
         'lower':   - 10 * abs(alpha_true['vaccine']),
         'upper':   + 10 * abs(alpha_true['vaccine']),
         'std':     + 10 * abs(alpha_true['vaccine']),
         'mean':    0.0,
      },{
         'name':    'alpha_income_value_prior',
         'density': 'gaussian',
         'lower':   - 10 * abs(alpha_true['income']),
         'upper':   + 10 * abs(alpha_true['income']),
         'std':     + 10 * abs(alpha_true['income']),
         'mean':    0.0,
      }
      # END alpha_value_prior
   ]
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
   # alpha_vaccine_smooth
   fun = lambda a, t : ('alpha_vaccine_value_prior', None, None)
   smooth_table.append({
      'name':       'alpha_vaccine_smooth',
      'age_id':     [0],
      'time_id':    [0],
      'fun':        fun,
   })
   #
   # alpha_income_smooth
   fun = lambda a, t : ('alpha_income_value_prior', None, None)
   smooth_table.append({
      'name':       'alpha_income_smooth',
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
   covariate_table = [
      {
      'name':     'sex',
      'reference': split_reference_list[split_index],
      },{
      'name':     'vaccine',
      'reference': 0.0,      # 0 for no vaccine, 1 for yes vaccine
      },{
      'name':     'income',
      'reference': avg_income['n0'][split_index],
      }
   ]
   #
   # mulcov_table
   mulcov_table = [
      {
      # alpha_vaccine
      'covariate':  'vaccine',
      'type':       'rate_value',
      'effected':   'iota',
      'group':      'world',
      'smooth':     'alpha_vaccine_smooth',
      },{
      # alpha_income
      'covariate':  'income',
      'type':       'rate_value',
      'effected':   'iota',
      'group':      'world',
      'smooth':     'alpha_income_smooth',
      }
   ]
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
      'vaccine':      None,
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
   for node in leaf_set :
      sex        = split_reference_list[split_index]
      income     = avg_income[node][split_index]
      for vaccine in [ 0.0, 1.0 ] :
         covariate_list = [ None, vaccine, income ]
         meas_value = rate_true('iota', None, None, None, covariate_list)
         #
         row['node']       = node
         row['meas_value'] = meas_value
         row['sex']        = sex
         row['vaccine']    = vaccine
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
   # result_dir
   result_dir = all_option['result_dir']
   if not os.path.exists(result_dir) :
      os.makedirs(result_dir)
   #
   # Create root_node.db
   root_node_database  = f'{result_dir}/root_node.db'
   root_node_db(root_node_database)
   #
   # connection
   new          = False
   connection   = dismod_at.create_connection(root_node_database, new)
   #
   # avgint_table
   # also erase table in root node database
   avgint_table = dismod_at.get_table_dict(connection, 'avgint')
   empty_table     = list()
   message         = 'erase avgint table'
   tbl_name        = 'avgint'
   dismod_at.replace_table(connection, tbl_name, empty_table)
   at_cascade.add_log_entry(connection, message)
   #
   # omega_grid
   age_table    = dismod_at.get_table_dict(connection, 'age')
   time_table   = dismod_at.get_table_dict(connection, 'time')
   age_id_list  = list( range( len(age_table) ) )
   time_id_list = list( range( len(age_table) ) )
   omega_grid   = { 'age': age_id_list, 'time' : time_id_list }
   #
   # n_split
   n_split = len( split_reference_list )
   #
   # omega_data
   omega_data      = dict()
   for node_name in [ 'n0', 'n1', 'n2', 'n3', 'n4', 'n5', 'n6' ] :
      omega_data[node_name] = list()
      for k in range(n_split) :
         omega_data[node_name].append( list() )
         for age_id in omega_grid['age'] :
            for time_id in omega_grid['time'] :
               age     = age_table[age_id]['age']
               time    = time_table[time_id]['time']
               sex     = split_reference_list[k]
               vaccine = 0.0
               income  = avg_income[node_name][k]
               cov     = [ sex, vaccine, income ]
               omega   = rate_true('omega', None, None, None, cov)
               omega_data[node_name][k].append( omega )
   #
   # Create all_node.db
   all_node_database = f'{result_dir}/all_node.db'
   at_cascade.create_all_node_db(
      all_node_database      = all_node_database,
      root_node_database     = root_node_database,
      split_reference_table  = split_reference_table,
      all_option             = all_option,
      omega_grid             = omega_grid,
      omega_data             = omega_data,
   )
   #
   # root_fit_dir
   root_fit_dir = f'{result_dir}/n0'
   if os.path.exists( root_fit_dir ) :
      # rmtree is very dangerous so make sure root_fit_dir is as expected
      assert root_fit_dir == 'build/example/n0'
      shutil.rmtree( root_fit_dir )
   os.makedirs( root_fit_dir )
   #
   # cascade starting at root node
   at_cascade.cascade_root_node(
      all_node_database  = all_node_database ,
      root_node_database = root_node_database ,
      fit_goal_set       = fit_goal_set      ,
   )
   #
   # check results
   for goal_dir in [ 'n0/n1/n3', 'n0/n1/n4', 'n0/n2' ] :
      goal_database = f'{result_dir}/{goal_dir}/dismod.db'
      at_cascade.check_cascade_node(
         rate_true          = rate_true,
         all_node_database  = all_node_database,
         fit_node_database  = goal_database,
         avgint_table       = avgint_table,
         relative_tolerance = 1e-2
      )
   #
   # check that fits were not run for n5 and n6
   for not_fit_dir in [ 'n0/n2/n5', 'n0/n2/n6' ] :
      assert not os.path.exists( f'{result_dir}/{not_fit_dir}' )
#
main()
print('absolute_covariates: OK')
sys.exit(0)
# END_2 absolute_covariates source code
