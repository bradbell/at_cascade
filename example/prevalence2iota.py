# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin_parent prevalence2iota}
{xrst_spell
   avg
   dage
   dtime
}

Example Estimation of iota From Prevalence Data
###############################################
For this example everything is constant in time so the
functions below do not depend on time.

Nodes
*****
The following is a diagram of the node tree for this example.
The :ref:`glossary@root_node` is n0,
the :ref:`glossary@fit_goal_set` is {n1, n5, n6},
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
:ref:`glossary@iota` and :ref:`glossary@omega`.
We use *iota(a, n, I)* to denote the value for iota
as a function of age *a*, node number *n*, and income *I*.
We use *omega(a, n)* to denote the value for omega
as a function of age *a* and node number *n*.


Covariate
*********
There are two covariates for this example is income and *one*.
The reference value for income is the average income corresponding
to the :ref:`glossary@fit_node`.
The *one* covariate is always equal to 1 and its reference is always zero.

r_n
===
We use *r_n* for the reference value of income at node *n*.
The code below sets this reference using the name avg_income:
{xrst_literal
   # BEGIN avg_income
   # END avg_income
}

alpha
=====
We use *alpha*
for the :ref:`glossary@rate_value` covariate multiplier
which multiplies income.
This multiplier affects the value of iota.
The true value for *alpha* (used which simulating the data) is
{xrst_literal
   # BEGIN alpha_true
   # END alpha_true
}

gamma
=====
We use *gamma*
for the :ref:`glossary@meas_noise` covariate multiplier
which multiplies *one*.
This multiplier adds to the nose level for prevalence in log space,
because the density for the prevalence data is log Gaussian.


Random Effects
**************
For each node, there is a random effect on iota that is constant
in age and time. Note that the leaf nodes have random effect for the node
above them as well as their own random effect.

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
For *rate* equal to iota and omega,
this is the true value for *rate*
in node *n* at age *a*, time *t*, and covariate values *c*.
The covariate values are a list in the
same order as the covariate table.
The values *t* and *c[1]* are not used by this function for this example.
{xrst_literal
   # BEGIN rate_true
   # END rate_true
}

y_i
===
The only simulated integrand for this example is :ref:`glossary@prevalence`.
This data is simulated without any noise
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

I_i
===
For each leaf node and each age in *age_grid*,
data is generated for the following *income_grid*:
{xrst_literal
   # BEGIN income_grid
   # END income_grid
}
Note that the check of the fit for the nodes in the fit_goal_set
expects much more accuracy when the income grid is not chosen randomly.

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

Value Prior
===========
The following is the value prior used for the root_node
{xrst_literal
   # BEGIN iota_50
   # END iota_50
}
{xrst_literal
   # BEGIN parent_value_prior
   # END parent_value_prior
}
The mean and standard deviation are only used for the root_node.
The :ref:`create_shift_db`
routine replaces them for other nodes.

dage Prior
==========
The following is the dage prior used for the fit_node:
{xrst_literal
   # BEGIN parent_dage_prior
   # END parent_dage_prior
}

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

Gamma Smoothing
***************
This is the smoothing used for *gamma* which multiplies the *one* covariate.
There is only one age and one time point in this smoothing
so it does not have dage or dtime priors.
In addition, the value prior has upper and lower limits equal
to the constant returned by the lambda function in this smoothing:
{xrst_literal
   # BEGIN gamma_smooth
   # END gamma_smooth
}

Checking The Fit
****************
The results of the fit are checked by check_cascade_node
using the :ref:`check_cascade_node@avgint_table`
that was created by the root_node_db routine.
The node_id for each row is replaced by the node_id for the
fit being checked.
routine uses these tables to check that fit against the truth.

{xrst_end prevalence2iota}
------------------------------------------------------------------------------
{xrst_begin prevalence2iota.py}

prevalence2iota: Python Source Code
###################################

{xrst_literal
   BEGIN prevalence2iota source code
   END prevalence2iota source code
}

{xrst_end prevalence2iota.py}
'''
# BEGIN prevalence2iota source code
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
fit_goal_set = { 'n1', 'n5', 'n6' }
# END fit_goal_set
#
# BEGIN random_seed
# random_seed = 1629371067
random_seed = 0
if random_seed == 0 :
   random_seed = int( time.time() )
random.seed(random_seed)
print('prevalence2iota: random_seed = ', random_seed)
# END random_seed
#
# BEGIN alpha_true
alpha_true = - 0.2
# END alpha_true
#
# BEGIN avg_income
avg_income       = { 'n3':1.0, 'n4':2.0, 'n5':3.0, 'n6':4.0 }
avg_income['n2'] = ( avg_income['n5'] + avg_income['n6'] ) / 2.0
avg_income['n1'] = ( avg_income['n3'] + avg_income['n4'] ) / 2.0
avg_income['n0'] = ( avg_income['n1'] + avg_income['n2'] ) / 2.0
# END avg_income
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
# BEGIN income_grid
random_income = False
income_grid   = dict()
for node in [ 'n3', 'n4', 'n5', 'n6' ] :
   max_income  = 2.0 * avg_income[node]
   if random_income :
      n_income_grid = 10
      income_grid[node] = \
         [ random.uniform(0.0, max_income) for j in range(n_income_grid) ]
      income_grid[node] = sorted( income_grid[node] )
   else :
      n_income_grid = 3
      d_income_grid = max_income / (n_income_grid - 1)
      income_grid[node] = [ j * d_income_grid for j in range(n_income_grid) ]
# END income_grid
# ----------------------------------------------------------------------------
# functions
# ----------------------------------------------------------------------------
# BEGIN rate_true
def rate_true(rate, a, t, n, c) :
   income = c[0]
   one    = c[1]
   s_n    = sum_random[n]
   r_0    = avg_income['n0']
   r_n    = avg_income[n]
   effect = s_n + alpha_true * ( income - r_0 )
   if rate == 'iota' :
      return (1 + a / 100) * 1e-3 * math.exp(effect)
   if rate == 'omega' :
      return (1 + a / 100) * 1e-2 * math.exp(effect)
   return 0.0
# END rate_true
# ----------------------------------------------------------------------------
def average_integrand(integrand_name, age, node_name, income) :
   covariate_list = [income, None]
   def iota(a, t) :
      return rate_true('iota', a, t, node_name, covariate_list)
   def omega(a, t) :
      return rate_true('omega', a, t, node_name, covariate_list)
   rate           = { 'iota': iota,     'omega': omega }
   grid           = { 'age' : [age],    'time': [2000.0] }
   abs_tol        = 1e-6
   avg_integrand   = dismod_at.average_integrand(
      rate, integrand_name, grid,  abs_tol
   )
   return avg_integrand
# ----------------------------------------------------------------------------
def root_node_db(file_name) :
   #
   # BEGIN iota_50
   covariate_list = [ avg_income['n0'], None ]
   iota_50        = rate_true('iota', 50.0, None, 'n0', covariate_list)
   # END iota_50
   #
   # prior_table
   prior_table = list()
   prior_table.append(
      # BEGIN parent_value_prior
      {   'name':    'parent_value_prior',
         'density': 'gaussian',
         'lower':   iota_50 / 10.0,
         'upper':   iota_50 * 10.0,
         'mean':    iota_50,
         'std':     iota_50 * 10.0,
         'eta':     iota_50 * 1e-3,
      }
      # END parent_value_prior
   )
   prior_table.append(
      # BEGIN parent_dage_prior
      {   'name':    'prior_iota_dage',
         'density': 'log_gaussian',
         'mean':    0.0,
         'std':     4.0,
         'eta':     iota_50 * 1e-3,
      }
      # END parent_dage_prior
   )
   prior_table.append(
      # BEGIN child_value_prior
      {   'name':    'child_value_prior',
         'density': 'gaussian',
         'mean':    0.0,
         'std':     1.0,
      }
      # END child_value_prior
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
   fun = lambda a, t : ('parent_value_prior', 'prior_iota_dage', None)
   smooth_table.append({
      'name':       'parent_smooth',
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
   # alpha_smooth
   fun = lambda a, t : ('alpha_value_prior', None, None)
   smooth_table.append({
      'name':       'alpha_smooth',
      'age_id':     [0],
      'time_id':    [0],
      'fun':        fun,
   })
   #
   # BEGIN gamma_smooth
   fun = lambda a, t : (1.0, None, None)
   smooth_table.append({
      'name':       'gamma_smooth',
      'age_id':     [0],
      'time_id':    [0],
      'fun':        fun
   })
   # END gamma_smooth
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
      'child_smooth':   'child_smooth' ,
   } ]
   #
   # covariate_table
   covariate_table = [
      { 'name':'income',   'reference':avg_income['n0'] },
      { 'name':'one',      'reference':0.0              },
   ]
   #
   # mulcov_table
   mulcov_table = [
      {   # alpha
         'covariate':  'income',
         'type':       'rate_value',
         'effected':   'iota',
         'group':      'world',
         'smooth':     'alpha_smooth',
      },{ # gamma
         'covariate':  'one',
         'type':       'meas_noise',
         'effected':   'prevalence',
         'group':      'world',
         'smooth':     'gamma_smooth',
   } ]
   #
   # subgroup_table
   subgroup_table = [ {'subgroup': 'world', 'group':'world'} ]
   #
   # integrand_table
   integrand_table = [
      {'name': 'Sincidence'},
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
      'income':       None,
      'integrand':    'Sincidence',
      'one':          1.0,
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
      row = {
         'subgroup':     'world',
         'weight':       '',
         'time_lower':   2000.0,
         'time_upper':   2000.0,
         'integrand':    'prevalence',
         'density':      'log_gaussian',
         'hold_out':     False,
         'one':          1.0,
      }
      row_list       = list()
      max_meas_value = 0.0
      for (age_id, age) in enumerate( age_grid ) :
         for income in income_grid[node] :
            integrand_name = 'prevalence'
            meas_value = average_integrand(
               integrand_name, age, node, income
            )
            row['node']       = node
            row['meas_value'] = meas_value
            row['age_lower']  = age
            row['age_upper']  = age
            row['income']     = income
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
      { 'name':'rate_case',             'value':'iota_pos_rho_zero'},
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
      income                = avg_income[node_name]
      for age_id in omega_grid['age'] :
         age     = age_grid[age_id]
         time    = 2000.0
         mtother = average_integrand(integrand_name, age, node_name, income)
         omega_list.append(mtother)
      omega_data[node_name] = [ omega_list ]
   #
   # Create all_node.db
   all_node_database = f'{result_dir}/all_node.db'
   all_option        = {
      'result_dir'          : result_dir,
      'root_node_name'      : 'n0',
      'absolute_covariates' : 'one',
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
   for goal_dir in [ 'n0/n1', 'n0/n2/n5', 'n0/n2/n6' ] :
      goal_database = f'{result_dir}/{goal_dir}/dismod.db'
      at_cascade.check_cascade_node(
         rate_true = rate_true,
         all_node_database = all_node_database,
         fit_node_database = goal_database,
         avgint_table      = avgint_table,
         relative_tolerance = 0.1
      )
   #
   # check that fits were not run for n3 and n4
   for not_fit_dir in [ 'n0/n1/n3', 'n0/n1/n4' ] :
      assert not os.path.exists( not_fit_dir )

#
main()
print('prevalence2iota: OK')
sys.exit(0)
# END prevalence2iota source code
