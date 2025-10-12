# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-25 Bradley M. Bell
# ----------------------------------------------------------------------------
r'''
{xrst_begin no_ode_fit}
{xrst_spell
  init
  mtexcess
  mtother
  relrisk
  sincidence
}

Do A No Ode Fit For One Node
############################

Prototype
*********
{xrst_literal ,
   # BEGIN_DEF, # END_DEF
   # BEGIN_RETURN, # END_RETURN
}

all_node_database
*****************
is a python string containing the name of the :ref:`all_node_db-name`.

root_database
*************
is a python string specifying the location of the
:ref:`glossary@root_database`.

option_all_dict
***************
is a ``dict`` containing the values in the option_all table.
This dictionary has a key for each
:ref:`option_all_table@Table Format@option_name`
and the corresponding value is
:ref:`option_all_table@Table Format@option_value`.
If an option does not appear in the table, the corresponding key
does not appear in *option_all_dict*.

fit_type
********
is a ``str`` equal to both or fixed
(fit both fixed and random effect or just fixed effects).

no_ode_database
***************
An intermediate database is stored in the file

   *result_dir*\ /\ *root_node_name*\ /no_ode/dismod.db

see :ref:`option_all_table@result_dir`
and :ref:`option_all_table@root_node_name`.
This contains the results of fitting with only the integrand that
do not require solving the ODE; i.e.
Sincidence, remission, and mtexcess which measure
iota, rho, and chi respectively.
It also include relrisk which measures

   ( *omega* + *chi* ) / *omega*

1. These integrands are included even if they are held out in the
   *root_fit_database* using the hold_out_integrand option.
2. The integrand mtother is excluded because omega is constrained using
   :ref:`omega_constraint-name`.
3. The data likelihoods are fit as Gaussian using the dismod_at data_density
   command.
4. The results of fitting this data base can be converted to
   csv files and plotted using the dismod_at db2csv and plotting routines.

root_fit_database
*****************
The return value *root_fit_database* is equal to

   *result_dir*\ /\ *root_node_name*\ /dismod.db

which can't be the same file name as *root_database*.
This is an input_node_database similar to *root_database*.
The difference is that the mean value in the priors for the fixed effects
have been replace by the optimal estimate for fitting with out the integrands
that use the ODE.
The last operation on this database is a dismod_at init command.

{xrst_end no_ode_fit}
'''
import datetime
import time
import math
import sys
import os
import copy
import dismod_at
import at_cascade
# -----------------------------------------------------------------------------
def system_command(command, file_stdout) :
   if file_stdout is None :
      dismod_at.system_command_prc(
         command,
         print_command = True,
         return_stdout = False,
         return_stderr = False,
         file_stdout   = None,
         file_stderr   = None,
         write_command = False,
      )
   else :
      dismod_at.system_command_prc(
         command,
         print_command = False,
         return_stdout = False,
         return_stderr = False,
         file_stdout   = file_stdout,
         file_stderr   = None,
         write_command = True,
      )
# ----------------------------------------------------------------------------
def add_index_to_name(table, name_col) :
   row   = table[-1]
   name  = row[name_col]
   ch    = name[-1]
   while name != '' and name[-1] in '0123456789' :
      name = name[: -1]
   if name[-1] == '_' :
      name = name[: -1]
   row[name_col] = name + '_' + str( len(table) )
# ----------------------------------------------------------------------------
# BEGIN_DEF
# at_cascade.no_ode_fit
def no_ode_fit(
   all_node_database   ,
   root_database  ,
   option_all_dict     ,
   fit_type            ,
) :
   assert type(all_node_database) == str
   assert type(root_database) == str
   assert type(option_all_dict) == dict
   assert fit_type == 'fixed' or fit_type == 'both'
   # END_DEF
   #
   # result_dir, max_fit, max_abs_effect, max_number_cpu
   result_dir     = None
   max_fit        = None
   max_abs_effect = None
   balance_fit    = None
   max_number_cpu = 1
   if 'result_dir' in option_all_dict :
      result_dir =  option_all_dict['result_dir']
   if 'max_fit' in option_all_dict :
      max_fit = int( option_all_dict['max_fit'] )
   if 'balance_fit' in option_all_dict :
      balance_fit = option_all_dict['balance_fit'].split()
   if 'max_abs_effect' in option_all_dict :
      max_abs_effect = float( option_all_dict['max_abs_effect'] )
   if 'max_number_cpu' in option_all_dict :
      max_number_cpu = float( option_all_dict['max_number_cpu'] )
   assert result_dir is not None
   #
   # name_rate2integrand
   name_rate2integrand = {
      'pini'  : 'prevalence',
      'iota'  : 'Sincidence',
      'rho'   : 'remission',
      'chi'   : 'mtexcess',
   }
   #
   # root_table
   connection = dismod_at.create_connection(
      root_database, new = False, readonly = True
   )
   root_table = dict()
   for name in [
      'avgint',
      'covariate',
      'integrand',
      'mulcov',
      'node',
      'option',
      'prior',
      'rate',
      'smooth',
      'smooth_grid'
   ] :
      root_table[name] = dismod_at.get_table_dict(connection, name)
   connection.close()
   if len( root_table['avgint'] ) > 0 :
      msg = 'no_ode_fit: root_database: avgint table is not empty'
      assert False, msg
   #
   # root_node_name
   root_node_name = at_cascade.get_parent_node(root_database)
   #
   # root_node_id
   root_node_id   = at_cascade.table_name2id(
      root_table['node'], 'node', root_node_name
   )
   #
   # root_split_reference_id
   connection        = dismod_at.create_connection(
      all_node_database, new = False, readonly = True
   )
   option_all_table  = dismod_at.get_table_dict(connection, 'option_all')
   split_reference_table = \
      dismod_at.get_table_dict(connection, 'split_reference')
   cov_info = at_cascade.get_cov_info(
      option_all_table, root_table['covariate'], split_reference_table
   )
   connection.close()
   root_split_reference_id = None
   if 'split_reference_id' in cov_info :
      root_split_reference_id = cov_info['split_reference_id']
   root_split_reference_id = None
   if 'split_reference_id' in cov_info :
      root_split_reference_id = cov_info['split_reference_id']
   #
   # no_ode_daabase, root_fit_database
   root_fit_database    = f'{result_dir}/{root_node_name}/dismod.db'
   no_ode_database      = f'{result_dir}/{root_node_name}/no_ode/dismod.db'
   os.makedirs(f'{result_dir}/{root_node_name}/no_ode')
   if root_database      == root_fit_database :
      msg   = f'root_database and root_fit_database are equal'
      assert False, msg
   #
   # trace_file_name, file_stdout
   trace_file_name = None
   file_stdout     = None
   if max_number_cpu > 1 :
      trace_file_name = f'{result_dir}/{root_node_name}/no_ode/trace.out'
      file_stdout    = open(trace_file_name, 'w')
      now            = datetime.datetime.now()
      current_time   = now.strftime("%H:%M:%S")
      print( f'Begin: {current_time}: no_ode fit {fit_type}' )
   # ------------------------------------------------------------------------
   # no_ode_database
   # ------------------------------------------------------------------------
   at_cascade.copy_root_db(root_database, no_ode_database)
   #
   # connection
   connection = dismod_at.create_connection(
      no_ode_database, new = False, readonly = False
   )
   #
   # omega_constraint
   at_cascade.omega_constraint(all_node_database, no_ode_database)
   #
   # move avgint -> c_root_avgint
   at_cascade.move_table(connection, 'avgint', 'c_root_avgint')
   #
   # avgint_parent_grid
   at_cascade.avgint_parent_grid(
      all_node_database = all_node_database ,
      fit_database      = no_ode_database   ,
   )
   at_cascade.add_log_entry(connection, 'avgint_parent_grid')
   #
   # hold_out_integrand
   hold_out_integrand = ''
   use_integrand = [ 'mtexcess', 'Sincidence', 'remission', 'relrisk' ]
   for row in root_table['integrand'] :
      integrand_name = row['integrand_name']
      if not integrand_name.startswith('mulcov_') :
         if integrand_name not in use_integrand :
            hold_out_integrand = hold_out_integrand + ' ' + integrand_name
   name  = 'hold_out_integrand'
   value = hold_out_integrand
   command = [
      'dismod_at', no_ode_database, 'set', 'option', name, value
   ]
   system_command(command, file_stdout)
   #
   # init
   command = [ 'dismod_at', no_ode_database, 'init' ]
   system_command(command, file_stdout)
   #
   # bnd_mulcov
   if not max_abs_effect is None :
      command = [
         'dismod_at', no_ode_database, 'bnd_mulcov', str(max_abs_effect)
      ]
      system_command(command, file_stdout)
   #
   # enforce max_fit
   fit_integrand = set()
   if not max_fit is None :
      fit_or_root   = at_cascade.fit_or_root_class(
         root_database, root_database
      )
      fit_integrand = at_cascade.get_fit_integrand(fit_or_root)
      fit_or_root.close()
   for integrand_id in fit_integrand :
      row            = root_table['integrand'][integrand_id]
      integrand_name = row['integrand_name']
      if integrand_name in use_integrand :
         density_name = 'gaussian'
         eta_factor   = '1e-2' # not used for gaussian
         nu           = '5'    # not used for gaussian
         command  = ['dismod_at', no_ode_database, 'data_density' ]
         command += [integrand_name, density_name, eta_factor, nu]
         system_command(command, file_stdout)
         if not max_fit is None :
            command  = [ 'dismod_at', no_ode_database ]
            command += [ 'hold_out', integrand_name, str(max_fit) ]
            if not balance_fit is None :
               command += balance_fit
            system_command(command, file_stdout)
   #
   # perturb start and scale
   if False :
      for perturb in [ 'start', 'scale' ] :
         key = f'perturb_optimization_{perturb}'
         if key in option_all_dict :
            sigma = option_all_dict[key]
            tbl_name = f'{key}_var'
            dismod_at.perturb_command( fit_database, tbl_name, sigma )
   #
   # fit both
   command = [ 'dismod_at', no_ode_database, 'fit', fit_type ]
   system_command(command, file_stdout)
   #
   # c_shift_predict_fit_var
   command = [ 'dismod_at', no_ode_database, 'predict', 'fit_var' ]
   system_command(command, file_stdout)
   at_cascade.move_table(connection, 'predict', 'c_shift_predict_fit_var')
   #
   # c_shift_avgint
   at_cascade.move_table(connection, 'avgint', 'c_shift_avgint')
   #
   # root_fit_database
   shift_databases = { root_node_name : root_fit_database }
   at_cascade.create_shift_db(
      all_node_database = all_node_database ,
      fit_database      = no_ode_database   ,
      shift_databases   = shift_databases   ,
      no_ode_fit        = True              ,
      job_table         = None              ,
   )
   #
   # move c_root_avgint -> avgint
   at_cascade.move_table(connection, 'c_root_avgint', 'avgint')
   #
   # connection
   connection.close()
   #
   # hold_out_integrand
   # restore to original values in option table
   hold_out_integrand = ''
   for row in root_table['option'] :
      if row['option_name'] == 'hold_out_integrand' :
         if row['option_value'] is not None :
            hold_out_integrand = row['option_value']
   name     = 'hold_out_integrand'
   command  = [ 'dismod_at', root_fit_database ]
   command += [ 'set', 'option', name, hold_out_integrand ]
   system_command(command, file_stdout)
   #
   if max_number_cpu > 1 :
      now            = datetime.datetime.now()
      current_time   = now.strftime("%H:%M:%S")
      print( f'End:   {current_time}: no_ode' )
   #
   # BEGIN_RETURN
   # ...
   assert type(root_fit_database) == str
   return root_fit_database
   # END_RETURN
