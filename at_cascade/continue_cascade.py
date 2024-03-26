# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-23 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin continue_cascade}

Continue Cascade From a Fit Node
################################

Syntax
******
{xrst_literal
   # BEGIN syntax
   # END syntax
}

Purpose
*******
Sometimes when running the cascade, the fit or statistics for a node fails.
This may be because of something that happened on the system,
or because of some of the settings in the :ref:`glossary@root_node_database`.
This routine enables you to continue the cascade from such a node.

all_node_database
*****************
is a python string specifying the location of the
:ref:`all_node_db-name`
relative to the current working directory.
This argument can't be ``None``.

fit_node_database
*****************
is a python string specifying the location of a dismod_at database
relative to the current working directory.
This is a :ref:`glossary@fit_node_database` with the
final state after a run of
:ref:`cascade_root_node-name` or :ref:`continue_cascade-name`
that includes fitting this database.
The *fit_node_database* is not changed, it is only used
to identify which child jobs to fit.

fit_goal_set
************
This is a ``set`` with elements of type ``int`` (``str``)
specifying the node_id (node_name) for each element of the
:ref:`glossary@fit_goal_set` .
Each such node must be the root node, or a descendant of the root node.
In addition, it must be in the :ref:`fit_goal_table-name` ,
or an ancestor of a node in the fit goal table.

fit_type_list
*************
This is a list with one or two elements
and its possible elements are ``both`` and ``fixed``.
For each job, the first type of fit is attempted.
If it fails, and there is a second type of fit, it is attempted.
If it also fails, the corresponding job fails.

shared_unique
*************
Under normal circumstances, you should use the empty string (default value)
for this parameter.

#. Parallel runs of continue_cascade must use different values of
   *shared_unique* so the corresponding shared memory names are different;
   see :ref:`fit_parallel@shared_unique` .

#. The *shared_unique* spacial case is where you are running (in parallel)
   continue_cascade with the same *fit_node_database*, and disjoint
   *fit_goal_set* . (The intersection of disjoint sets is empty.)

#. In the special case above, the suggested value for *shared_unique*
   is ``_`` *node_name* , where *node_name* is the name of one of the nodes
   in the *fit_goal_set*. It may be necessary to include the value
   of the splitting covariate in *shared_unique*  .
   (The splitting covariate is sex in the :ref:`csv.fit-name` case.)

{xrst_end   continue_cascade}
'''
import time
import os
import multiprocessing
import dismod_at
import at_cascade
# ----------------------------------------------------------------------------
# BEGIN syntax
# at_cascade.continue_cascade
def continue_cascade(
   all_node_database = None,
   fit_node_database = None,
   fit_goal_set      = None,
   fit_type_list     = [ 'both', 'fixed' ],
   shared_unique     = '',
# )
) :
   assert type(all_node_database) == str
   assert type(fit_node_database) == str
   assert type(fit_goal_set)      == set
   assert type(fit_type_list)     == list
   assert type(shared_unique)     == str
   # END syntax
   #
   # split_reference_table, option_all, node_split_table, fit_goal
   connection       = dismod_at.create_connection(
      all_node_database, new = False, readonly = True
   )
   option_all_table = dismod_at.get_table_dict(connection, 'option_all')
   node_split_table = dismod_at.get_table_dict(connection, 'node_split')
   split_reference_table = \
      dismod_at.get_table_dict(connection, 'split_reference')
   connection.close()
   #
   # result_dir, root_node_name, root_node_database,
   # max_number_cpu, refit_split
   result_dir         = None
   root_node_name     = None
   root_node_database = None
   max_number_cpu     = 1
   refit_split        = False
   for row in option_all_table :
      if row['option_name'] == 'result_dir' :
         result_dir = row['option_value']
      if row['option_name'] == 'root_node_name' :
         root_node_name = row['option_value']
      if row['option_name'] == 'root_node_database' :
         root_node_database = row['option_value']
      if row['option_name'] == 'max_number_cpu' :
         max_number_cpu = int( row['option_value'] )
      if row['option_name'] == 'refit_split' :
         refit_split = row['option_value'] == 'true'
   assert result_dir is not None
   assert root_node_name is not None
   assert root_node_database is not None
   #
   # node_table, covariate_table, fit_integrand
   fit_or_root = at_cascade.fit_or_root_class(
      fit_node_database, root_node_database
   )
   node_table      = fit_or_root.get_table('node')
   covariate_table = fit_or_root.get_table('covariate')
   fit_integrand   = at_cascade.get_fit_integrand(fit_or_root)
   fit_or_root.close()
   #
   # root_node_id
   root_node_id = at_cascade.table_name2id(node_table, 'node', root_node_name)
   #
   # root_split_reference_id
   root_split_reference_id = None
   for row in option_all_table :
      if row['option_name'] == 'root_split_reference_name' :
         root_split_reference_name = row['option_value']
         root_split_reference_id = at_cascade.table_name2id(
            split_reference_table,
            'split_reference',
            root_split_reference_name
         )
   #
   # fit_node_id
   fit_node_name = at_cascade.get_parent_node(fit_node_database)
   fit_node_id   = at_cascade.table_name2id(node_table, 'node', fit_node_name)
   #
   # fit_split_reference_id
   if len(split_reference_table) == 0 :
      fit_split_reference_id = None
   else :
      cov_info = at_cascade.get_cov_info(
         option_all_table, covariate_table, split_reference_table
      )
      fit_split_reference_id = cov_info['split_reference_id']
   #
   # job_table
   job_table = at_cascade.create_job_table(
      all_node_database          = all_node_database,
      node_table                 = node_table,
      start_node_id              = fit_node_id,
      start_split_reference_id   = fit_split_reference_id,
      fit_goal_set               = fit_goal_set,
   )
   #
   # check job_table[0]
   assert fit_node_id == job_table[0]['fit_node_id']
   assert fit_split_reference_id == job_table[0]['split_reference_id']
   #
   # start_job_id
   start_job_id = 0
   #
   # lock
   lock = multiprocessing.Lock()
   #
   # skip_start_job
   skip_start_job = True
   #
   # fit_one_process
   at_cascade.fit_parallel(
      job_table         = job_table ,
      start_job_id      = start_job_id,
      all_node_database = all_node_database,
      node_table        = node_table,
      fit_integrand     = fit_integrand,
      skip_start_job    = skip_start_job,
      max_number_cpu    = max_number_cpu,
      fit_type_list     = fit_type_list,
      shared_unique     = shared_unique,
   )
