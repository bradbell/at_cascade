# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin_parent continue_cascade_xam}
{xrst_spell
   dage
   dtime
}

Example Continuing a Cascade
############################
For this example everything is constant in age and time.

Nodes
*****
The following is a diagram of the node tree for this example.
The :ref:`glossary@root_node` is n0,
the first :ref:`glossary@fit_goal_set` is {n3, n4, n2},
the second :ref:`glossary@fit_goal_set` is {n5, n6},
and the leaf nodes are {n3, n4, n5, n6}::

                n0
          /-----/\-----\
        n1             (n2)
       /  \            /  \
    (n3)  (n4)      [n5]  [n6]

fit_goal_set
============
{xrst_literal
   # BEGIN fit_goal_set
   # END fit_goal_set
}
A cascade using the first fit_goal_set is started at node n0.
After that finishes, the cascade is continued from node n2
using the second fit_goal_set.

Parallel Processing
*******************
This example sets :ref:`all_option_table@max_number_cpu`
as an example of parallel processing.
The results for nodes n3 and n4 are computed in parallel
during the call to :ref:`cascade_root_node`.
The results for nodes n5 and n6 are computed in parallel
during the call to :ref:`continue_cascade`.
{xrst_literal
   # BEGIN all_option
   # END all_option
}
see :ref:`create_all_node_db@all_option`.

Rates
*****
The only non-zero dismod_at rate for this example is
:ref:`glossary@iota`.

Covariate
*********
There are no covariates for this example.

Simulated Data
**************

rate_true(rate, a, t, n, c)
===========================
For *rate* equal to iota,
this is the true value for *rate*
in node *n* at age *a*, time *t*, and covariate values *c*.
The values *a*, *t*. *c*, are not used by this function for this example.
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
*y_i = rate_true('iota', None, None, n_i, None)* where *n_i* is the node.
The data is modeled as having noise even though there is no simulated noise.

n_i
===
Data is only simulated for the leaf nodes; i.e.,
each *n_i* is in the set { n3, n4, n5, n6 }.
Since the data does not have any nose, the data residuals are a measure
of how good the fit is for the nodes in the fit goal sets.

Parent Rate Smoothing
*********************
This is the iota smoothing used for the fit_node.
There are no :ref:`glossary@dage` or :ref:`glossary@dtime`
priors because there is only one age and one time point.

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

Child Rate Smoothing
********************
This is the smoothing used for the
random effect for each child of the fit_node.
There are no dage or dtime
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

{xrst_end continue_cascade_xam}
------------------------------------------------------------------------------
{xrst_begin continue_cascade.py}

continue_cascade: Python Source Code
####################################

{xrst_literal
   BEGIN source code
   END source code
}

{xrst_end continue_cascade.py}
'''
# BEGIN source code
# ----------------------------------------------------------------------------
# imports
# ----------------------------------------------------------------------------
import math
import sys
import os
import copy
import time
import csv
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
first_fit_goal_set  = { 'n3', 'n4', 'n2' }
second_fit_goal_set = { 'n5', 'n6' }
# END fit_goal_set
# BEGIN all_option
all_option  = {
   'result_dir':     'build/example',
   'root_node_name': 'n0',
   'max_number_cpu':  '2',
}
# END all_option
# ----------------------------------------------------------------------------
# functions
# ----------------------------------------------------------------------------
# BEGIN rate_true
def rate_true(rate, a, t, n, c) :
   iota_true = {
      'n3' : 0.04,
      'n4' : 0.05,
      'n5' : 0.06,
      'n6' : 0.07,
   }
   iota_true['n1'] = (iota_true['n3'] + iota_true['n4']) / 2.0
   iota_true['n2'] = (iota_true['n5'] + iota_true['n6']) / 2.0
   iota_true['n0'] = (iota_true['n1'] + iota_true['n2']) / 2.0
   if rate == 'iota' :
      return iota_true[n]
   return 0.0
# END rate_true
# ----------------------------------------------------------------------------
def root_node_db(file_name) :
   #
   # BEGIN iota_mean
   iota_mean = rate_true('iota', None, None, 'n0', None)
   # END iota_mean
   #
   # prior_table
   prior_table = list()
   prior_table.append(
      # BEGIN parent_value_prior
      {   'name':    'parent_value_prior',
         'density': 'gaussian',
         'lower':   iota_mean / 10.0,
         'upper':   iota_mean * 10.0,
         'mean':    iota_mean,
         'std':     iota_mean,
         'eta':     iota_mean * 1e-3
      }
      # END parent_value_prior
   )
   prior_table.append(
      # BEGIN child_value_prior
      {   'name':    'child_value_prior',
         'density': 'gaussian',
         'mean':    0.0,
         'std':     10.0,
      }
      # END child_value_prior
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
   rate_table = [ {
      'name':           'iota',
      'parent_smooth':  'parent_smooth',
      'child_smooth':   'child_smooth',
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
   integrand_table = [ {'name':'Sincidence'} ]
   #
   # avgint_table
   avgint_table = list()
   row = {
      'node':         'n0',
      'subgroup':     'world',
      'weight':       '',
      'age_lower':    50.0,
      'age_upper':    50.0,
      'time_lower':   2000.0,
      'time_upper':   2000.0,
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
      'age_lower':    50.0,
      'age_upper':    50.0,
      'time_lower':   2000.0,
      'time_upper':   2000.0,
      'integrand':    'Sincidence',
      'density':      'gaussian',
      'hold_out':     False,
   }
   for node in leaf_set :
         meas_value        = rate_true('iota', None, None, node, None)
         row['node']       = node
         row['meas_value'] = meas_value
         row['meas_std']   = meas_value / 10.0
         data_table.append( copy.copy(row) )
   #
   # age_grid
   age_grid = [ 0.0, 100.0 ]
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
   # print_level_fixed is 5 and max_number_cpu > 1 so optimizer trace
   # is printed to a file in same directory as corresponding database.
   option_table = [
      { 'name':'parent_node_name',      'value':'n0'},
      { 'name':'rate_case',             'value':'iota_pos_rho_zero'},
      { 'name': 'zero_sum_child_rate',  'value':'iota'},
      { 'name':'quasi_fixed',           'value':'false'},
      { 'name':'max_num_iter_fixed',    'value':'50'},
      { 'name':'tolerance_fixed',       'value':'1e-8'},
      { 'name':'print_level_fixed',     'value':'5'},
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
def two_fit_goal_set_example(result_dir) :
   # -------------------------------------------------------------------------
   #
   # root_node_database
   root_node_database  = f'{result_dir}/root_node.db'
   #
   # all_node_database
   all_node_database = f'{result_dir}/all_node.db'
   #
   # root_fit_dir
   root_fit_dir = f'{result_dir}/n0'
   if os.path.exists(root_fit_dir) :
      # rmtree is very dangerous so make sure root_fit_dir is as expected
      assert root_fit_dir == 'build/example/n0'
      shutil.rmtree( root_fit_dir )
   os.makedirs(root_fit_dir )
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
   # cascade starting at n0
   at_cascade.cascade_root_node(
      all_node_database  = all_node_database  ,
      root_node_database = root_node_database  ,
      fit_goal_set       = first_fit_goal_set ,
   )
   #
   # continue starting at at n2
   fit_node_database =  root_fit_dir + '/n2/dismod.db'
   at_cascade.continue_cascade(
      all_node_database = all_node_database   ,
      fit_node_database = fit_node_database   ,
      fit_goal_set      = second_fit_goal_set ,
   )
   #
   # check leaf node results
   leaf_dir_list = [ 'n0/n1/n3', 'n0/n1/n4', 'n0/n2/n5', 'n0/n2/n6' ]
   for leaf_dir in leaf_dir_list :
      leaf_database = f'{result_dir}/{leaf_dir}/dismod.db'
      at_cascade.check_cascade_node(
         rate_true          = rate_true,
         all_node_database  = all_node_database,
         fit_node_database  = leaf_database,
         avgint_table       = avgint_table,
         relative_tolerance = 1e-7,
      )
# ----------------------------------------------------------------------------
def one_fit_goal_set_example(result_dir ) :
   #
   # root_node_database
   root_node_database  = f'{result_dir}/root_node.db'
   #
   # all_node_database
   all_node_database = f'{result_dir}/all_node.db'
   #
   # root_fit_dir
   root_fit_dir = f'{result_dir}/n0'
   if os.path.exists(root_fit_dir) :
      # rmtree is very dangerous so make sure root_fit_dir is as expected
      assert root_fit_dir == 'build/example/n0'
      shutil.rmtree( root_fit_dir )
   os.makedirs(root_fit_dir )
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
   # cascade starting at n0
   fit_goal_set = first_fit_goal_set | second_fit_goal_set
   at_cascade.cascade_root_node(
      all_node_database  = all_node_database  ,
      root_node_database = root_node_database  ,
      fit_goal_set       = fit_goal_set ,
   )
   #
   # check leaf node results
   leaf_dir_list = [ 'n0/n1/n3', 'n0/n1/n4', 'n0/n2/n5', 'n0/n2/n6' ]
   for leaf_dir in leaf_dir_list :
      leaf_database = f'{result_dir}/{leaf_dir}/dismod.db'
      at_cascade.check_cascade_node(
         rate_true          = rate_true,
         all_node_database  = all_node_database,
         fit_node_database  = leaf_database,
         avgint_table       = avgint_table,
         relative_tolerance = 1e-7,
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
   # root_node_database
   root_node_database  = f'{result_dir}/root_node.db'
   root_node_db(root_node_database)
   #
   # all_node_database
   all_node_database = f'{result_dir}/all_node.db'
   at_cascade.create_all_node_db(
      all_node_database       = all_node_database,
      root_node_database      = root_node_database,
      all_option              = all_option,
   )
   #
   # example using continue_cascade
   # two_fit_goal_set_example(result_dir)
   #
   # same calculation without continue_cascade
   one_fit_goal_set_example(result_dir)
#
# Without this, the mac will try to execute main on each processor.
if __name__ == '__main__' :
   main()
   print('max_fit_option: OK')
   sys.exit(0)
# END source code
