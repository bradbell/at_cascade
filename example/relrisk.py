# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ----------------------------------------------------------------------------
r'''
{xrst_begin relrisk}
{xrst_spell
   avgint
   sincidence
   mtexcess
}

Example Fitting Relative Risk Data
##################################

Nodes
*****
The following is a diagram of the node tree for this example
(the :ref:`glossary@root_node` is n0)::

                n0
          /-----/\-----\
        n1              n2
       /  \            /  \
     n3    n4        n5    n6

{xrst_literal
   # BEGIN node_table
   # END node_table
}

Discussion
**********
This example is interesting because it gives a prefect fit to the
data for all nodes except node n0.
This is because there is two levels of random effects for node n0,
one level of random effects for node n1 and n2,
and no random effects for nodes n3, n4, n5, n6.

relative_tolerance
******************
This is the relative tolerance that we will use when checking that the
results are correct:
{xrst_literal
   # BEGIN relative_tolerance
   # END relative_tolerance
}
The fixed effect values for nodes n1 through n6 are checked to see that
they are correct to this tolerance.
The random effects for node n3, corresponding to the fit of node n1,
is also checked.
Note that all the random effects are zero except for the omega constraints.
In addition, the leaf nodes n3, n4, n5, and n6 do not have any omega random
effects.

fit_goal_set
************
The :ref:`glossary@fit_goal_set`
is the leaf nodes:
{xrst_literal
   # BEGIN fit_goal_set
   # END fit_goal_set
}

rate_true
*********
The true value of the rates (for this example) are:
{xrst_literal
   # BEGIN rate_true
   # END rate_true
}

Rate Priors
***********
The fitted rates for this example are iota and chi
(rho is zero and omega is constrained to have its true value).
The parent and child priors each fitted rate is set as follows
{xrst_literal
   # BEGIN prior_table
   # END prior_table
}

Data Table
**********
Each leaf node has two data values, the true value of Sincidence and relrisk
for the node.

avgint Table
************
Each leaf node has predictions for three avgint values,
Sincidence, mtexcess, and relrisk.
The values corresponding to the fit for each leaf node is compared
to the truth using :ref:`check_cascade_node-name` .

Source Code
***********
{xrst_literal
   # BEGIN PYTHON
   # END PYTHON
}


{xrst_end relrisk}
'''
# BEGIN PYTHON
# ----------------------------------------------------------------------------
# imports
# ----------------------------------------------------------------------------
import numpy
import sys
import os
import copy
import multiprocessing
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
# BEGIN relative_tolerance
relative_tolerance = 1e-14
# END relative_tolerance
#
# BEGIN fit_goal_set
fit_goal_set = { 'n3', 'n4', 'n5', 'n6' }
# END fit_goal_set
#
# BEGIN option_all_table
max_number_cpu = max(1, multiprocessing.cpu_count() - 1)
option_all            = {
   'result_dir':                 'build/example',
   'root_node_name':             'n0',
   'refit_split':                'false',
   'max_number_cpu':             max_number_cpu,
}
option_all['root_node_database'] = option_all['result_dir'] + '/root_node.db'
# END option_all_table
#
# ----------------------------------------------------------------------------
# functions
# ----------------------------------------------------------------------------
# BEGIN rate_true
def rate_true(rate_name, node_name) :
   iota_true  = 1e-3
   rho_true   = 0.0
   chi_true   = 1e-1
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
   rate2true = {
      'iota'   : iota_true ,
      'rho'    : rho_true  ,
      'chi'    : chi_true  ,
      'omega'  : omega_true[node_name]
   }
   return rate2true[ rate_name ]
# END rate_true
# ----------------------------------------------------------------------------
def root_node_db(file_name) :
   #
   # BEGIN prior_table
   prior_table = list()
   for rate_name in [ 'iota', 'chi' ] :
      rate_0   = rate_true(rate_name, 'n0')
      prior_table.append(
         {  'name':    f'parent_{rate_name}_prior',
            'density': 'uniform',
            'lower':   rate_0 / 10.0,
            'upper':   rate_0 * 10.0,
            'mean':    rate_0 * 2,
         }
      )
   # END prior_table
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
   # BEGIN node_table
   node_table = [
      { 'name':'n0',        'parent':''   },
      { 'name':'n1',        'parent':'n0' },
      { 'name':'n2',        'parent':'n0' },
      { 'name':'n3',        'parent':'n1' },
      { 'name':'n4',        'parent':'n1' },
      { 'name':'n5',        'parent':'n2' },
      { 'name':'n6',        'parent':'n2' },
   ]
   # END node_table
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
   leaf_set    = fit_goal_set
   for integrand in [ 'Sincidence', 'relrisk' ] :
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
         iota    = rate_true('iota',  node)
         chi     = rate_true('chi',   node)
         omega   = rate_true('omega', node)
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
      { 'name':'tolerance_fixed',       'value':relative_tolerance},
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
            omega  = rate_true('omega', node_name)
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
   # check fixed effects
   # The parent rate values for all but node n0 should fit exactly because
   # the prior is uniform and there is only one level of random effects
   for subdir in [ 'n1', 'n2', 'n1/n3', 'n1/n4', 'n2/n5', 'n2/n6' ] :
      goal_database = f'{result_dir}/n0/{subdir}/dismod.db'
      rate_fun      = lambda r, a, t, n, c : rate_true(r, n)
      at_cascade.check_cascade_node(
         rate_true          = rate_fun,
         all_node_database  = all_node_database,
         fit_node_database  = goal_database,
         avgint_table       = avgint_table,
         relative_tolerance = float( numpy.finfo(float).eps * 100.0 ),
      )
   # -------------------------------------------------------------------------
   # Check omega random effects are set correctly
   # -------------------------------------------------------------------------
   #
   # n1_database
   # n1 is the parent node for this fit
   n1_database = f'{result_dir}/n0/n1/dismod.db'
   #
   # avgint_table
   # n3 is the child node for the predictions
   connection = dismod_at.create_connection(
      n1_database, new = False, readonly = False
   )
   for row in avgint_table :
      row['node_id'] = 3
   tbl_name    = 'avgint'
   dismod_at.replace_table(connection, tbl_name, avgint_table)
   connection.close()
   #
   # predict
   # create predictions for node n3 corresponding to fit for n1
   command = [ 'dismod_at', n1_database, 'predict', 'fit_var' ]
   dismod_at.system_command_prc(command)
   #
   # name_table
   # for name = predict, integrand, node
   fit_or_root     = at_cascade.fit_or_root_class(
      n1_database, root_node_database
   )
   predict_table   = fit_or_root.get_table('predict')
   integrand_table = fit_or_root.get_table('integrand')
   node_table      = fit_or_root.get_table('node')
   connection.close()
   #
   for (predict_id, predict_row) in enumerate(predict_table) :
      #
      # avgint_id
      avgint_id  = predict_row['avgint_id']
      avgint_row = avgint_table[avgint_id]
      assert avgint_id == predict_id
      #
      # node_name
      node_id   = avgint_row['node_id']
      node_name = node_table[node_id]['node_name']
      assert node_name == 'n3'
      #
      # integrand_name
      integrand_id   = avgint_table[avgint_id]['integrand_id']
      integrand_name = integrand_table[integrand_id]['integrand_name']
      #
      # avg_integrand
      avg_integrand  = predict_table[avgint_id]['avg_integrand']
      #
      # check
      iota  = rate_true('iota', node_name)
      chi   = rate_true('chi',  node_name)
      omega = rate_true('omega', node_name)
      if integrand_name == 'Sincidence' :
         check = iota
      elif integrand_name == 'mtexcess' :
         check = chi
      else :
         assert integrand_name == 'relrisk'
         check = 1.0 + chi / omega
      #
      # rel_error
      rel_error = 1.0 - avg_integrand / check
      if abs(rel_error) > relative_tolerance :
         msg = f'subdir = {subdir}, rel_error = {rel_error}'
         assert False, msg

#
if __name__ == '__main__' :
   main()
   print('relrisk: OK')
# END PYTHON
