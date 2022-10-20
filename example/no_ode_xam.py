# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin_parent no_ode_xam}
{xrst_spell
   avg
   dage
   dtime
   mtexcess
   sincidence
   smoothings
}

Example Using no_ode_fit To Initialize Optimization
###################################################
This example uses :ref:`glossary@mtexcess` data during a :ref:`no_ode_fit`
and then holds it out during the actual estimation.
This is meant to simulate the case where mtexcess is obtain
form other data to help initialize the optimization
(and without this smart initialization the optimization would fail).
For this example everything is constant in time so the
functions below do not depend on time.

Nodes
*****
The following is a diagram of the node tree for this example.
The :ref:`glossary@root_node` is n0,
the :ref:`glossary@fit_goal_set` and the leaf node set
are both {n2, n3} for this example::

                n0
          /-----/\-----\
        n1              n2

fit_goal_set
============
{xrst_literal
   # BEGIN fit_goal_set
   # END fit_goal_set
}

Rates
*****
The non-zero dismod_at rates for this example are
:ref:`glossary@iota`, :ref:`glossary@chi`, and :ref:`glossary@omega`.
We use *iota(a, n, I)* , *chi(a, n, I)*
to denote the value for iota and chi
as a function of age *a*, node number *n*, and income *I*.
We use *omega(a, n)* to denote the value for omega
as a function of age *a* and node *n*.


Covariate
*********
There is one covariate for this example, income.
The reference value for income is the average income corresponding
to the :ref:`glossary@root_node`.

I_n
===
We use *I_n* for the reference value of income at node *n*.
The code below sets this reference using the name avg_income:
{xrst_literal
   # BEGIN avg_income
   # END avg_income
}

alpha
=====
We use *alpha_iota* ( *alpha_chi* )
for the :ref:`glossary@rate_value` covariate multiplier
which multiplies income and affects iota (chi).
The true value for these multipliers
(used which simulating the data) is
{xrst_literal
   # BEGIN alpha_true
   # END alpha_true
}

Random Effects
**************
For each node, there is a random effect on iota and chi that is constant
in age and time. Note that the leaf nodes have random effect for the node
above them as well as their own random effect.

R_n
===
We use *R_n* to denote the random effects for node *n*.
The code below sets this value:
{xrst_literal
   # BEGIN random_effect_true
   # END random_effect_true
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
For *rate* equal to iota, chi, and omega,
this is the true value for *rate*
in node *n* at age *a*, time *t*, and covariate values *c*.
The covariate values are a list in the
same order as the covariate table.
The values *t* and *c[1]* are not used by this function for this example.
{xrst_literal
   # BEGIN rate_true
   # END rate_true
}
The true model for chi is constant below the second age grid point
because it is not possible to determine chi at age zero from Sincidence
and prevalence measurements.

y_i
===
The simulated integrands for this example are
:ref:`glossary@mtexcess`,
:ref:`glossary@Sincidence`, and
:ref:`glossary@prevalence`.
The data is simulated without any noise
but it is modeled as having noise.
In addition, the mtexcess data is only used for the
no_ode_fit and is held out during actual fits.
This simulates the case where the mtexcess data was constructed from
the other data in order to help initialize the optimization.

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
The parent smoothings use the true value of iota and chi at age 50
and in the root_node:
{xrst_literal
   # BEGIN iota_chi_50
   # END iota_chi_50
}

iota and chi
============
This is the smoothing used in the root_node model for the rates.
Note that the value part of this smoothing is only used for the *root_node*.
This smoothing uses the *age_gird* and one time point.
There are no :ref:`glossary@dtime` priors because there is only one time point.
The smoothing for chi does not use the first age grid point, age zero,
because it is not possible to determine chi at age zero from Sincidence
and prevalence measurements.

Value Prior
===========
The following is the value prior used for the root_node
{xrst_literal
   # BEGIN parent_iota_value_prior
   # END parent_iota_value_prior
}
{xrst_literal
   # BEGIN parent_chi_value_prior
   # END parent_chi_value_prior
}
The mean and standard deviation are only used for the root_node.
The :ref:`create_shift_db`
routine replaces them for other nodes.

dage Prior
==========
The following is the dage prior used for the root_node:
{xrst_literal
   # BEGIN parent_dage_prior
   # END parent_dage_prior
}

Child Rate Smoothing
********************
This is the smoothing used for the
random effect for each child of the root_node.
There are no :ref:`glossary@dage` or dtime
priors because there is only one age and one time point in this smoothing.

Value Prior
===========
The following is the value prior used for the children of the root_node:
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

Checking The Fit
****************
The results of the fit are checked by check_cascade_node
using the :ref:`check_cascade_node@avgint_table`
that was created by the root_node_db routine.
The node_id for each row is replaced by the node_id for the
fit being checked.
routine uses these tables to check that fit against the truth.

{xrst_end no_ode_xam}
------------------------------------------------------------------------------
{xrst_begin no_ode_xam.py}
{xrst_spell
   xam
}

no_ode_xam: Python Source Code
##############################

{xrst_literal
   BEGIN no_ode_xam source code
   END no_ode_xam source code
}

{xrst_end no_ode_xam.py}
'''
# BEGIN no_ode_xam source code
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
fit_goal_set = { 'n1', 'n2' }
# END fit_goal_set
#
# BEGIN random_seed
random_seed = 0
if random_seed == 0 :
   random_seed = int( time.time() )
random.seed(random_seed)
print('no_ode_xam: random_seed = ', random_seed)
# END random_seed
#
# BEGIN alpha_true
alpha_true = { 'iota':- 0.25, 'chi':-0.15 }
alpha_true_max_abs = 0.3
# END alpha_true
#
# BEGIN avg_income
avg_income       = { 'n1':1.0, 'n2':2.0 }
avg_income['n0'] = ( avg_income['n1'] + avg_income['n2'] ) / 2.0
# END avg_income
#
# BEGIN random_effect_true
random_effect_true  = { 'n0': 0.0, 'n1': 0.3, 'n2': -0.3}
# END random_effect_true
#
# BEGIN age_grid
age_grid = [0.0, 20.0, 40.0, 60.0, 80.0, 100.0 ]
# END age_grid
#
# BEGIN income_grid
random_income = False
income_grid   = dict()
for node in [ 'n1', 'n2' ] :
   max_income  = 2.0 * avg_income[node]
   n_income_grid = 3
   d_income_grid = max_income / (n_income_grid - 1)
   income_grid[node] = [ j * d_income_grid for j in range(n_income_grid) ]
# END income_grid
# ----------------------------------------------------------------------------
# functions
# ----------------------------------------------------------------------------
# BEGIN rate_true
def rate_true(rate, a, t, n, c) :
   if rate in [ 'pini', 'rho' ] :
      return 0.0
   income   = c[0]
   R_n      = random_effect_true[n]
   I_n      = avg_income['n0']
   if rate == 'iota' :
      effect   = R_n + alpha_true[rate] * ( income - I_n )
      return (1 + a / 100) * 1e-3 * math.exp( effect  )
   if rate == 'chi' :
      effect   = R_n + alpha_true[rate] * ( income - I_n )
      # chi is constant up to second age grid point because prevalence
      # cannot determine chi at age zero.
      aa = max(a, age_grid[1] )
      return (1 + aa / 100) * 1e-2 * math.exp( effect )
   if rate == 'omega' :
      # omega random effect is constrained for each node so to get an
      # exact match it cannot depend on income, but it can depend on
      # age and time
      effect   = R_n +  a / 10000
      return (1 + a / 100) * 1e-2 * math.exp( effect)
   assert False
# END rate_true
# ----------------------------------------------------------------------------
def average_integrand(integrand_name, age, node_name, income) :
   covariate_list = [ income ]
   def iota(a, t) :
      return rate_true('iota', a, t, node_name, covariate_list)
   def chi(a, t) :
      return rate_true('chi', a, t, node_name, covariate_list)
   def omega(a, t) :
      return rate_true('omega', a, t, node_name, covariate_list)
   rate           = { 'iota': iota,  'chi': chi, 'omega': omega }
   grid           = { 'age' : [age], 'time': [2000.0] }
   abs_tol        = 1e-6
   avg_integrand   = dismod_at.average_integrand(
      rate, integrand_name, grid,  abs_tol
   )
   return avg_integrand
# ----------------------------------------------------------------------------
def root_node_db(file_name) :
   # BEGIN iota_chi_50
   covariate_list = [ avg_income['n0'] ]
   iota_50        = rate_true('iota', 50.0, None, 'n0', covariate_list )
   chi_50         = rate_true('chi',  50.0, None, 'n0', covariate_list )
   # END iota_chi_50
   #
   # prior_table
   prior_table = list()
   #
   prior_table.append(
      # BEGIN parent_iota_value_prior
      {   'name':    'parent_iota_value_prior',
         'density': 'uniform',
         'lower':   iota_50 / 10.0,
         'upper':   iota_50 * 10.0,
         'mean':    iota_50,
         'std' :    iota_50 * 10.0,
         'eta':     iota_50 * 1e-3,
      }
      # END parent_iota_value_prior
   )
   prior_table.append(
      # BEGIN parent_chi_value_prior
      {   'name':    'parent_chi_value_prior',
         'density': 'uniform',
         'lower':   chi_50 / 10.0,
         'upper':   chi_50 * 10.0,
         'mean':    chi_50,
         'std':     chi_50 * 10.0,
         'eta':     chi_50 * 1e-3,
      }
      # END parent_chi_value_prior
   )
   #
   prior_table.append(
      # BEGIN parent_dage_prior
      {   'name':    'parent_dage_prior',
         'density': 'log_gaussian',
         'mean':    0.0,
         'std':     4.0,
         'eta':     min(iota_50 , chi_50 ) * 1e-3,
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
         'density': 'uniform',
         'lower':   - 10 * alpha_true_max_abs,
         'upper':   + 10 * alpha_true_max_abs,
         'mean':    0.0,
      }
      # END alpha_value_prior
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
      'age_id':     range(1, len(age_grid) ),
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
         'parent_smooth':  'parent_iota_smooth',
         'child_smooth':   'child_smooth' ,
      },{
         'name':           'chi',
         'parent_smooth':  'parent_chi_smooth',
         'child_smooth':   'child_smooth' ,
   } ]
   #
   # covariate_table
   covariate_table = [
      { 'name':'income',   'reference':avg_income['n0'] },
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
      },{ # alpha_chi
         'covariate':  'income',
         'type':       'rate_value',
         'effected':   'chi',
         'group':      'world',
         'smooth':     'alpha_smooth',
      },
   ]
   #
   # subgroup_table
   subgroup_table = [ {'subgroup': 'world', 'group':'world'} ]
   #
   # integrand_table
   integrand_table = [
      {'name': 'Sincidence'},
      {'name': 'mtexcess' },
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
   }
   for age in age_grid :
      row['age_lower'] = age
      row['age_upper'] = age
      for integrand in [ 'prevalence' ] :
         row['integrand'] = integrand
         avgint_table.append( copy.copy(row) )
   #
   # data_table
   data_table = list()
   leaf_set   = [ 'n1', 'n2' ]
   for node in leaf_set :
      row = {
         'subgroup':     'world',
         'weight':       '',
         'time_lower':   2000.0,
         'time_upper':   2000.0,
         'density':      'log_gaussian',
         'hold_out':     False,
      }
      row_list       = list()
      max_meas_value =  {
         'mtexcess': 0.0, 'Sincidence': 0.0, 'prevalence': 0.0
      }
      for (age_id, age) in enumerate( age_grid ) :
         for income in income_grid[node] :
            row['node']       = node
            row['age_lower']  = age
            row['age_upper']  = age
            row['income']     = income
            for integrand in max_meas_value :
               meas_value = average_integrand(
                  integrand, age, node, income
               )
               row['integrand']  = integrand
               row['meas_value'] = meas_value
               max_meas_value[integrand]  = max(
                  meas_value, max_meas_value[integrand]
               )
               row_list.append( copy.copy(row) )
      n_row = len(age_grid) * n_income_grid * len(max_meas_value)
      assert len(row_list) == n_row
      for row in row_list :
         # The model for the measurement noise is small so a few
         # data points act like lots of real data points.
         # The actual measruement noise is zero.
         for integrand in max_meas_value :
            if row['integrand'] == integrand :
               row['meas_std'] = max_meas_value[integrand] / 50.0
               row['eta']      = 1e-4 * max_meas_value[integrand]
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
      { 'name':'tolerance_fixed',       'value':'1e-8'},
      { 'name':'tolerance_random',      'value':'1e-8'},
      { 'name':'hold_out_integrand',    'value':'mtexcess'},
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
def display_no_ode_fit(root_node_dir) :
   #
   # database
   database = root_node_dir + '/no_ode/dismod.db'
   #
   # pdf_file
   pdf_dir  = root_node_dir + '/no_ode'
   #
   # data.pdf
   integrand_list = [ 'Sincidence', 'mtexcess', 'prevalence' ]
   pdf_file       = pdf_dir + '/data.pdf'
   dismod_at.plot_data_fit(
      database       = database        ,
      pdf_file       = pdf_file        ,
      integrand_list = integrand_list  ,
   )
   #
   # rate.pdf
   rate_set = [ 'iota', 'chi' ]
   pdf_file = pdf_dir + '/rate.pdf'
   plot_title = 'rate'
   dismod_at.plot_rate_fit(database, pdf_file, plot_title, rate_set)
   #
   # db2csv
   dismod_at.system_command_prc([ 'dismodat.py', database, 'db2csv' ])
# ----------------------------------------------------------------------------
def check_no_ode_fit(root_node_dir) :
   #
   # no_ode_database
   no_ode_database = root_node_dir + '/no_ode/dismod.db'
   #
   # predict
   dismod_at.system_command_prc([
      'dismod_at', no_ode_database, 'predict', 'fit_var'
   ] )
   #
   # connection
   new        = False
   connection = dismod_at.create_connection(no_ode_database, new)
   #
   # table
   table = dict()
   for tbl_name in [
      'age', 'time', 'var', 'rate', 'node', 'fit_var', 'avgint',
      'integrand', 'predict'

   ] :
      table[tbl_name] = dismod_at.get_table_dict(connection, tbl_name)
   #
   # connection
   connection.close()
   #
   # check variable values
   for (var_id, var_row) in enumerate( table['var'] ) :
      #
      # fit_var_value
      fit_var_value = table['fit_var'][var_id]['fit_var_value']
      #
      # var_type
      var_type      = var_row['var_type']
      #
      # rate_name
      rate_id       = var_row['rate_id']
      rate_name     = table['rate'][rate_id]['rate_name']
      #
      if var_type == 'rate' :
         #
         # node_name
         node_id       = var_row['node_id']
         node_name     = table['node'][node_id]['node_name']
         #
         # c_0
         c_0           = [ avg_income['n0'] ]
         #
         # rate_true_n0
         age_id        = var_row['age_id']
         time_id       = var_row['time_id']
         age           = table['age'][age_id]['age']
         time          = table['time'][time_id]['time']
         rate_true_n0  = rate_true(rate_name, age, time, 'n0', c_0)
         #
         if node_name == 'n0' :
            # fixed effect
            rel_error     = (1.0 - fit_var_value / rate_true_n0 )
            if rate_name == 'omega' :
               assert rel_error < 1e-12
            else :
               assert abs( rel_error ) < 1e-5
         elif rate_name in [ 'iota', 'chi'] :
            # These random effects are constant w.r.t age and time
            rate_true_n  = rate_true(rate_name, age, time, node_name, c_0)
            effect_true  = math.log( rate_true_n / rate_true_n0 )
            rel_error     = (1.0 - fit_var_value / effect_true )
            assert abs( rel_error ) < 1e-4
         else :
            # These random effects are constraints
            c_n          = [ avg_income[node_name] ]
            rate_true_n  = rate_true(rate_name, age, time, node_name, c_n)
            effect_true  = math.log( rate_true_n / rate_true_n0 )
            rel_error     = (1.0 - fit_var_value / effect_true )
            assert abs( rel_error ) < 1e-12
      else :
         assert var_type == 'mulcov_rate_value'
         rel_error = (1.0 - fit_var_value / alpha_true[rate_name])
         assert abs( rel_error ) < 1e-4
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
   # all_omega_data
   all_omega_data     = dict()
   for node_name in [ 'n0', 'n1', 'n2' ] :
      omega_list = list()
      income     = avg_income[node_name]
      for age_id in omega_grid['age'] :
         age            = age_grid[age_id]
         time           = 2000.0
         integrand_name = 'mtother'
         mtother        = \
            average_integrand(integrand_name, age, node_name, income)
         omega_list.append(mtother)
      all_omega_data[node_name] = [ omega_list ]
   #
   # Create all_node.db
   all_node_database = f'{result_dir}/all_node.db'
   all_option        = {
      'result_dir'         : result_dir,
      'root_node_name'     : 'n0',
   }
   at_cascade.create_all_node_db(
      all_node_database       = all_node_database,
      root_node_database      = root_node_database,
      all_option              = all_option,
      omega_grid              = omega_grid,
      omega_data              = all_omega_data,
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
      fit_goal_set       = fit_goal_set,
      no_ode_fit         = True,
   )
   #
   # check_no_ode_fit
   check_no_ode_fit(root_node_dir)
   #
   # display_no_ode_fit
   display_no_ode_fit(root_node_dir)
   #
   # check results
   for goal_dir in [ 'n0/n1', 'n0/n2' ] :
      goal_database = f'{result_dir}/{goal_dir}/dismod.db'
      at_cascade.check_cascade_node(
         rate_true          = rate_true,
         all_node_database  = all_node_database,
         fit_node_database  = goal_database,
         avgint_table       = avgint_table,
         relative_tolerance = 1e-2,
      )
#
main()
print('no_ode_xam: OK')
sys.exit(0)
# END no_ode_xam source code
