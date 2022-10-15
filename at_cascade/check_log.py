# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin check_log}

Checks Logs For Warnings and Errors
###################################

Syntax
******
{xrst_literal
   # BEGIN syntax
   # END syntax
}

Purpose
*******
Read all the logs for a cascade and return any warning or error messages.

message_type
************
is an ``str`` equal to ``error`` or ``warning``.
The corresponding messages are returned.

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

message_dict
************
the return value is a ``dict``.
For each :ref:`create_job_table@job_table@job_name` that is a key in
*message_dict* the corresponding value
*message_dict[job_name]* is a non-empty ``list`` of ``str``
containing the messages for that job.
If an *job_name* is not a *key* is in *message_dict*,
there were not messages of the specified type for that job.

{xrst_end check_log}
'''
# ----------------------------------------------------------------------------
import time
import os
import multiprocessing
import dismod_at
import at_cascade
# ----------------------------------------------------------------------------
def check_log(
# BEGIN syntax
# message_dict = at_cascade.check_log(
   message_type            = None,
   all_node_database       = None,
   root_node_database      = None,
   fit_goal_set            = None,
# )
# END syntax
) :
   assert type(message_type)        is str
   assert type(all_node_database)   is str
   assert type(root_node_database)  is str
   assert type(fit_goal_set)        is set
   #
   assert message_type in [ 'error', 'warning' ]
   #
   # node_table, covariate_table
   new             = False
   connection      = dismod_at.create_connection(root_node_database, new)
   node_table      = dismod_at.get_table_dict(connection, 'node')
   covariate_table = dismod_at.get_table_dict(connection, 'covariate')
   connection.close()
   #
   # split_reference_table, all_option_table, node_split_table
   new         = False
   connection  = dismod_at.create_connection(all_node_database, new)
   split_reference_table = dismod_at.get_table_dict(
      connection, 'split_reference'
   )
   all_option_table = dismod_at.get_table_dict(connection, 'all_option')
   node_split_table = dismod_at.get_table_dict(connection, 'node_split')
   connection.close()
   #
   # root_node_name
   result_dir     = None
   root_node_name = None
   for row in all_option_table :
      if row['option_name'] == 'result_dir' :
         result_dir = row['option_value']
      if row['option_name'] == 'root_node_name' :
         root_node_name = row['option_value']
   assert result_dir is not None
   assert root_node_name is not None
   #
   # check root_node_name
   parent_node_name = at_cascade.get_parent_node(root_node_database)
   if parent_node_name != root_node_name :
      msg  = f'{root_node_database} parent_node_name = {parent_node_name}\n'
      msg  = f'{all_node_database} root_node_name = {root_node_name}'
      assert False, msg
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
   # node_split_set
   node_split_set = set()
   for row in node_split_table :
      node_split_set.add( row['node_id'] )
   #
   # message_dict
   message_dict = dict()
   #
   # job_id
   for job_id in range( len(job_table) ) :
      #
      # job_name
      job_name = job_table[job_id]['job_name']
      #
      # fit_node_id
      fit_node_id = job_table[job_id]['fit_node_id']
      #
      # fit_split_reference_id
      fit_split_reference_id = job_table[job_id]['split_reference_id']
      #
      # fit_node_database
      database_dir = at_cascade.get_database_dir(
         node_table              = node_table,
         split_reference_table   = split_reference_table,
         node_split_set          = node_split_set,
         root_node_id            = root_node_id,
         root_split_reference_id = root_split_reference_id,
         fit_node_id             = fit_node_id ,
         fit_split_reference_id  = fit_split_reference_id,
      )
      fit_node_database = f'{result_dir}/{database_dir}/dismod.db'
      #
      # log_table
      if not os.path.exists(fit_node_database) :
         message = f'Missing fit_node_database {fit_node_database}'
         message_dict[job_name] = [ message ]
      else :
         new        = False
         connection = dismod_at.create_connection(fit_node_database, new)
         log_table  = dismod_at.get_table_dict(connection, 'log')
         connection.close()
         #
         # row
         for row in log_table :
            #
            if row['message_type'] == message_type :
               #
               # message_dict
               if job_name not in message_dict :
                  message_dict[job_name] = list()
               message_dict[job_name].append( row['message'] )
   #
   return message_dict
