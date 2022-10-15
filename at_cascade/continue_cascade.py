# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
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
:ref:`all_node_db`
relative to the current working directory.
This argument can't be ``None``.

fit_node_database
*****************
is a python string specifying the location of a dismod_at database
relative to the current working directory.
This is a :ref:`glossary@fit_node_database` with the
final state after running :ref:`cascade_root_node` on this database.
The necessary state of *fit_node_database* is reached before
cascade_root_node starts runs on any of its child nodes.

fit_goal_set
************
This is a ``set`` with elements of type ``int`` (``str``)
specifying the node_id (node_name) for each element of the
:ref:`glossary@fit_goal_set` .
This argument can't be ``None``.
It can be different from when the original cascade was run; e.g.,
it could include new goal nodes.

fit_type_list
*************
This is a list with one or two elements
and its possible elements are ``both`` and ``fixed``.
For each job, the first type of fit is attempted.
If it fails, and there is a second type of fit, it is attempted.
If it also fails, the corresponding job fails.

{xrst_end   continue_cascade}
'''
import time
import os
import multiprocessing
import dismod_at
import at_cascade
# ----------------------------------------------------------------------------
def continue_cascade(
# BEGIN syntax
# at_cascade.continue_cascade(
   all_node_database = None,
   fit_node_database = None,
   fit_goal_set      = None,
   fit_type_list     = [ 'both', 'fixed' ]
# )
# END syntax
) :
   assert type(all_node_database) == str
   assert type(fit_node_database) == str
   assert type(fit_goal_set)      == set
   assert type(fit_type_list)     == list
   #
   # node_table, covariate_table
   new             = False
   connection      = dismod_at.create_connection(fit_node_database, new)
   node_table      = dismod_at.get_table_dict(connection, 'node')
   covariate_table = dismod_at.get_table_dict(connection, 'covariate')
   connection.close()
   #
   # split_reference_table, all_option, node_split_table
   new              = False
   connection       = dismod_at.create_connection(all_node_database, new)
   all_option_table = dismod_at.get_table_dict(connection, 'all_option')
   node_split_table = dismod_at.get_table_dict(connection, 'node_split')
   split_reference_table = \
      dismod_at.get_table_dict(connection, 'split_reference')
   connection.close()
   #
   # result_dir, root_node_name, max_number_cpu
   result_dir     = None
   root_node_name = None
   max_number_cpu = 1
   for row in all_option_table :
      if row['option_name'] == 'result_dir' :
         result_dir = row['option_value']
      if row['option_name'] == 'root_node_name' :
         root_node_name = row['option_value']
      if row['option_name'] == 'max_number_cpu' :
         max_number_cpu = int( row['option_value'] )
   assert result_dir is not None
   assert root_node_name is not None
   #
   # root_node_id
   root_node_id = at_cascade.table_name2id(node_table, 'node', root_node_name)
   #
   # root_split_reference_id
   root_split_reference_id = None
   for row in all_option_table :
      if row['option_name'] == 'root_split_reference_name' :
         root_split_reference_name = row['option_value']
         root_split_reference_id = at_cascade.table_name2id(
            split_reference_table,
            'split_reference',
            root_split_reference_name
         )
   #
   # fit_integrand
   fit_integrand = at_cascade.get_fit_integrand(fit_node_database)
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
         all_option_table, covariate_table, split_reference_table
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
   # start_child_job_id, end_child_job_id
   start_child_job_id = job_table[0]['start_child_job_id']
   end_child_job_id   = job_table[0]['end_child_job_id']
   #
   # connection
   new        = False
   connection = dismod_at.create_connection(fit_node_database, new)
   #
   # move avgint -> c_root_avgint
   at_cascade.move_table(connection, 'avgint', 'c_root_avgint')
   #
   # node_split_set
   node_split_set = set()
   for row in node_split_table :
      node_split_set.add( row['node_id'] )
   #
   # shift_databases
   shift_databases = dict()
   for job_id in range(start_child_job_id, end_child_job_id) :
      #
      # shift_node_id
      shift_node_id = job_table[job_id]['fit_node_id']
      #
      # shift_split_reference_id
      shift_split_reference_id = job_table[job_id]['split_reference_id']
      #
      # shift_database_dir
      database_dir = at_cascade.get_database_dir(
         node_table              = node_table,
         split_reference_table   = split_reference_table,
         node_split_set          = node_split_set,
         root_node_id            = root_node_id,
         root_split_reference_id = root_split_reference_id,
         fit_node_id             = shift_node_id ,
         fit_split_reference_id  = shift_split_reference_id,
      )
      shift_database_dir = f'{result_dir}/{database_dir}'
      if not os.path.exists(shift_database_dir) :
         os.makedirs(shift_database_dir)
      #
      # shift_node_database
      shift_node_database = f'{shift_database_dir}/dismod.db'
      #
      # shift_name
      shift_name = shift_database_dir.split('/')[-1]
      #
      # shfit_databases
      shift_databases[shift_name] = shift_node_database
   #
   # create shifted databases
   at_cascade.create_shift_db(
      all_node_database,
      fit_node_database,
      shift_databases
   )
   #
   # move c_root_avgint -> avgint
   at_cascade.move_table(connection, 'c_root_avgint', 'avgint')
   #
   # connection
   connection.close()
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
