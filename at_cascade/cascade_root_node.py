# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin cascade_root_node}
{xrst_spell
   dir
   var
}

Cascade Fits Starting at Root Node
##################################

Syntax
******
{xrst_literal
   # BEGIN syntax
   # END syntax
}

all_node_database
*****************
is a python string specifying the location of the
:ref:`all_node_db`
relative to the current working directory.
This argument can't be ``None``.

root_node_database
******************
is a python string specifying the location of the dismod_at
:ref:`glossary@root_node_database`.

fit_goal_set
************
This is a ``set`` with elements of type ``int`` (``str``)
specifying the node_id (node_name) for each element of the
:ref:`glossary@fit_goal_set` .
This argument can't be ``None``.

no_ode_fit
**********
if ``True`` ( ``False`` ) the :ref:`no_ode_fit` routine
will (will not) be used to modify the mean of the parent value
and difference priors.

root_fit_database
*****************
This database is located at

   *result_dir*\ ``/``\ *root_node_name*\ ``/dismod.db``

see :ref:`all_option_table@result_dir`
and :ref:`all_option_table@root_node_name`.
If *no_ode_fit* is ``True`` ( ``False`` ) the priors in the
*root_node_database* are modified (are not modified)
before the root node is fit.
Upon return, this is a :ref:`glossary@fit_node_database` with the
extra properties listed below:

fit_type_list
*************
This is a list with one or two elements
and its possible elements are ``both`` and ``fixed``.
For each job, the first type of fit is attempted.
If it fails, and there is a second type of fit, it is attempted.
If it also fails, the corresponding job fails.

Output dismod.db
****************
Upon return for cascade_root_node,
the results for the fits are in ``dismod.db`` in the corresponding
directory relative to *result_dir*; i.e., sub-directory of *result_dir* .
The *.csv* files can be created using the
dismod_at db2csv command.
The dismod_at function ``plot_rate_fit`` and ``plot_data_fit``
can be used to crate the corresponding plots.

The root level fit the directory is
:ref:`all_option_table@root_node_name` .
If the current fit is just before a split,
there will be a sub-directory for the fit of each
:ref:`split_reference_table@split_reference_name` after the split.
Otherwise there will be a sub-directory for the fit of each child of the
node corresponding to the current fit.
You can determine the directory, relative to *result_dir*
corresponding to a fit using the :ref:`get_database_dir` function.


fit_var
=======
The fit_var table correspond to the posterior
mean for the model variables for  this job; i.e., this
:ref:`create_job_table@job_table@fit_node_id` and
:ref:`create_job_table@job_table@split_reference_id`.

sample
======
The sample table contains the corresponding samples from the posterior
distribution for the model variables for this job.

log
===
The log table contains a summary of the operations preformed on dismod.db
between it's input and output state.

{xrst_end cascade_root_node}
'''
# ----------------------------------------------------------------------------
import shutil
import time
import os
import multiprocessing
import dismod_at
import at_cascade
# ----------------------------------------------------------------------------
def cascade_root_node(
# BEGIN syntax
# at_cascade.cascade_root_node(
   all_node_database       = None,
   root_node_database      = None,
   fit_goal_set            = None,
   no_ode_fit              = False,
   fit_type_list           = [ 'both', 'fixed' ]
# )
# END syntax
) :
   assert type(all_node_database)  == str
   assert type(root_node_database) == str
   assert type(fit_goal_set)       == set
   assert type(no_ode_fit)         == bool
   assert type(fit_type_list)      == list
   #
   # split_reference_table, all_option_table
   new         = False
   connection  = dismod_at.create_connection(all_node_database, new)
   split_reference_table = dismod_at.get_table_dict(
      connection, 'split_reference'
   )
   all_option_table = dismod_at.get_table_dict(connection, 'all_option')
   connection.close()
   #
   # all_option_dict
   all_option_dict = dict()
   for row in all_option_table :
      all_option_dict[ row['option_name'] ] = row['option_value']
   #
   # root_node_name, max_number_cpu, result_dir
   result_dir     = all_option_dict['result_dir']
   root_node_name = all_option_dict['root_node_name']
   max_number_cpu = 1
   if 'max_number_cpu' in all_option_dict :
      max_number_cpu = int( all_option_dict['max_number_cpu'] )
   #
   # check root_node_name
   parent_node_name = at_cascade.get_parent_node(root_node_database)
   if parent_node_name != root_node_name :
      msg  = f'{root_node_database} parent_node_name = {parent_node_name}\n'
      msg += f'{all_node_database} root_node_name = {root_node_name}'
      assert False, msg
   #
   # root_fit_database
   root_fit_database = f'{result_dir}/{root_node_name}/dismod.db'
   if not no_ode_fit :
      shutil.copyfile(root_node_database, root_fit_database)
   else :
      at_cascade.no_ode_fit(
         all_node_database  = all_node_database,
         root_node_database = root_node_database,
         all_option_dict    = all_option_dict,
         fit_type           = fit_type_list[0],
      )
   #
   # node_table, covariate_table
   new             = False
   connection      = dismod_at.create_connection(root_fit_database, new)
   node_table      = dismod_at.get_table_dict(connection, 'node')
   covariate_table = dismod_at.get_table_dict(connection, 'covariate')
   avgint_table    = dismod_at.get_table_dict(connection, 'avgint')
   connection.close()
   if len(avgint_table) != 0 :
      msg = 'cascade_root_node: avgint table is not empty'
      assert False, msg
   #
   # fit_integrand
   fit_integrand = at_cascade.get_fit_integrand(root_fit_database)
   #
   # root_node_id
   root_node_id = at_cascade.table_name2id(node_table, 'node', root_node_name)
   #
   # root_split_reference_id
   if len(split_reference_table) == 0 :
      root_split_reference_id = None
   else :
      cov_info = at_cascade.get_cov_info(
         all_option_table, covariate_table, split_reference_table
      )
      root_split_reference_id = cov_info['split_reference_id']
   #
   # job_table
   job_table = at_cascade.create_job_table(
      all_node_database          = all_node_database,
      node_table                 = node_table,
      start_node_id              = root_node_id,
      start_split_reference_id   = root_split_reference_id,
      fit_goal_set               = fit_goal_set,
   )
   #
   # start_job_id
   start_job_id = 0
   #
   # skip_start_job
   skip_start_job = False
   #
   # run_parallel_job
   at_cascade.run_parallel(
      job_table         = job_table ,
      start_job_id      = start_job_id,
      all_node_database = all_node_database,
      node_table        = node_table,
      fit_integrand     = fit_integrand,
      skip_start_job    = skip_start_job,
      max_number_cpu    = max_number_cpu,
      fit_type_list     = fit_type_list,
   )
