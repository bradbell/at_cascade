# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin check_log}

Checks Logs For Warnings and Errors
###################################

Prototype
*********
{xrst_literal ,
   # BEGIN DEF, # END DEF
   # BEGIN RETURN, # END RETURN
}

Purpose
*******
Read the logs for a cascade and return all the messages of a certain type.
The databases are not modified (are opened in a read only fashion).

message_type
************
is  equal to ``error``, ``warning`` or ``at_cascade`` .
The corresponding messages are returned.

all_node_database
*****************
specifies the location of the
:ref:`all_node_db-name`
relative to the current working directory.
This argument can't be ``None``.

root_node_database
******************
specifies the location of the dismod_at
:ref:`glossary@root_node_database`.

job_table
*********
This is the :ref:`create_job_table@job_table` that we are checking
the log messages in.
Only jobs for which :ref:`create_job_table@job_table@prior_only` is false
are included; i.e., only jobs that correspond to fits.

start_job_id
************
This is the job that the log messages should start at.
If this is None, the first job in the job table is the start job.
Jobs before this job in the :ref:`create_job_table@job_table`
are not included.

max_job_depth
*************
This is the number of generations below the start job that are included;
see :ref:`job_descendent@Node Depth Versus Job Depth` .
If *max_job_depth* is None, all the jobs below the start job are included.
If *max_job_depth* is zero, only the start job is included.

message_dict
************
For each :ref:`create_job_table@job_table@job_name` in the job table
that is a key in *message_dict*.  The corresponding value

| *message_dict* [ *job_name* ]


is a non-empty ``list`` of ``str`` containing the messages for that job.
If a *job_name* is not a *key* is in *message_dict*,
there were no messages of the specified type for that job.

{xrst_end check_log}
'''
# ----------------------------------------------------------------------------
import time
import os
import multiprocessing
import dismod_at
import at_cascade
# ----------------------------------------------------------------------------
# BEGIN DEF
# at_cascade.check_log
def check_log(
   message_type                  ,
   all_node_database             ,
   root_node_database            ,
   job_table                     ,
   start_job_id           = None ,
   max_job_depth          = None ,
# )
) :
   assert type(message_type)        == str
   assert type(all_node_database)   == str
   assert type(root_node_database)  == str
   if start_job_id == None :
      start_job_id = 0
   assert max_job_depth == None or type(max_job_depth) == int
   # END DEF
   #
   assert message_type in [ 'error', 'warning', 'at_cascade' ]
   #
   # node_table, covariate_table
   connection      = dismod_at.create_connection(
      root_node_database, new = False, readonly = True
   )
   node_table      = dismod_at.get_table_dict(connection, 'node')
   covariate_table = dismod_at.get_table_dict(connection, 'covariate')
   connection.close()
   #
   # split_reference_table, option_all_table, node_split_table
   connection  = dismod_at.create_connection(
      all_node_database, new = False, readonly = True
   )
   split_reference_table = dismod_at.get_table_dict(
      connection, 'split_reference'
   )
   option_all_table = dismod_at.get_table_dict(connection, 'option_all')
   node_split_table = dismod_at.get_table_dict(connection, 'node_split')
   connection.close()
   #
   # root_node_name
   result_dir     = None
   root_node_name = None
   for row in option_all_table :
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
   if len(split_reference_table) == 0 :
      root_split_reference_id = None
   else :
      cov_info = at_cascade.get_cov_info(
         option_all_table, covariate_table, split_reference_table
      )
      root_split_reference_id = cov_info['split_reference_id']
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
      # include_this_job
      job_depth = at_cascade.job_descendent(job_table, start_job_id, job_id)
      if job_depth == None :
         include_this_job = False
      elif max_job_depth == None :
         include_this_job = True
      else :
         include_this_job = job_depth <= max_job_depth
      if include_this_job :
         include_this_job = not job_table[job_id]['prior_only']
      if include_this_job :
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
            connection = dismod_at.create_connection(
                     fit_node_database, new = False, readonly = True
            )
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
   # BEGIN RETURN
   # ...
   assert type(message_dict) == dict
   return message_dict
   # END RETURN
