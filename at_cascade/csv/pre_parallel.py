# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ----------------------------------------------------------------------------
r'''
{xrst_begin csv.pre_parallel}

Predict With Specified Maximum Number of Processes
##################################################

Prototype
*********
{xrst_literal
   # BEGIN DEF
   # END DEF
}

fit_dir
*******
Same as the csv fit :ref:`csv.fit@fit_dir` .

sim_dir
*******
Same as :ref:`csv.predict@sim_dir` .


all_covariate_table
*******************
This is an in memory representation of
:ref:`csv.fit@Input Files@covariate.csv` .

fit_goal_set
************
This set contains the node that we are required to fit; i.e.,
the nodes in :ref:`csv.fit@Input Files@fit_goal.csv` .
Ancestors between these nodes and the root node are also fit.

start_job_name
**************
Is the name of the job (fit) that the predictions should start at.
This is a node name, followed by a period, followed by a sex.
Only this fit, and its descendents, will be included in the predictions.
If this argument is None, all of the jobs (fits) will be included.

max_job_depth
*************
This is the number of generations below start_job_name are.
If max_job_depth is zero,  only the start job will be included.
If max_job_depth is None,  start job and all its descendants are included.

option_predict
**************
This is an in memory representation of
:ref:`csv.predict@Input Files@option_predict.csv` .

{xrst_end csv.pre_parallel}
r'''
# ----------------------------------------------------------------------------
import at_cascade
import dismod_at
import multiprocessing
import numpy
# ----------------------------------------------------------------------------
# shared_memory_prefix = get_shared_memory_prefix(all_node_database)
def get_shared_memory_prefix(all_node_database) :
   assert type(all_node_database) == str
   #
   connection           = dismod_at.create_connection(
      all_node_database, new = False, readonly = True
   )
   option_all_table     = dismod_at.get_table_dict(connection, 'option_all')
   connection.close()
   shared_memory_prefix = ""
   for row in option_all_table :
      if row['option_name'] == 'shared_memory_prefix' :
         shared_memory_prefix = row['option_value']
   return shared_memory_prefix
# ----------------------------------------------------------------------------
# BEGIN DEF
# at_cascade.csv.pre_parallel
def pre_parallel(
   fit_dir,
   sim_dir,
   all_covariate_table,
   fit_goal_set,
   start_job_name,
   max_job_depth,
   option_predict,
) :
   assert type(fit_dir)                     == str
   assert sim_dir == None or type(sim_dir)  == str
   assert type(all_covariate_table)         == list
   assert type( all_covariate_table[0] )    == dict
   assert type(fit_goal_set)                == set
   assert type( next(iter(fit_goal_set) ))  == str
   assert type( option_predict )            == dict
   # END DEF
   # ----------------------------------------------------------------------
   # job_status_name
   job_status_name = [
      'skip' , # will not process this job
      'ready', # job is readiy to run
      'run'  , # job is running
      'done' , # job finished running
   ]
   job_status_skip  = job_status_name.index( 'skip' )
   job_status_ready = job_status_name.index( 'ready' )
   job_status_run   = job_status_name.index( 'run' )
   job_status_done  = job_status_name.index( 'done' )
   # -------------------------------------------------------------------------
   #
   # max_number_cpu
   max_number_cpu = option_predict['max_number_cpu']
   #
   # all_node_db
   all_node_db = f'{fit_dir}/all_node.db'
   #
   # root_node_database
   root_node_database = f'{fit_dir}/root_node.db'
   #
   # root_node_name
   root_node_name = at_cascade.get_parent_node(root_node_database)
   #
   # node_table, covariate_table
   connection      = dismod_at.create_connection(
      root_node_database, new = False, readonly = True
   )
   node_table      = dismod_at.get_table_dict(connection, 'node')
   covariate_table = dismod_at.get_table_dict(connection, 'covariate')
   connection.close()
   #
   # root_split_reference_id
   root_split_reference_id = None
   sex_value               = None
   for row in covariate_table :
      if row['covariate_name'] == 'sex' :
            sex_value = row['reference']
   for (row_id, row) in enumerate( at_cascade.csv.split_reference_table ) :
      if row['split_reference_value'] == sex_value :
         root_split_reference_id = row_id
   assert root_split_reference_id != None
   #
   # root_node_id
   root_node_id = at_cascade.table_name2id(
      node_table, 'node', root_node_name
   )
   #
   # split_reference_table
   connection      = dismod_at.create_connection(
      all_node_db, new = False, readonly = True
   )
   split_reference_table = \
      dismod_at.get_table_dict(connection, 'split_reference')
   connection.close()
   assert split_reference_table == at_cascade.csv.split_reference_table
   #
   # job_table
   job_table = at_cascade.create_job_table(
      all_node_database          = all_node_db              ,
      node_table                 = node_table               ,
      start_node_id              = root_node_id             ,
      start_split_reference_id   = root_split_reference_id  ,
      fit_goal_set               = fit_goal_set             ,
   )
   #
   # start_job_id
   if start_job_name == None :
      start_job_id = 0
   else :
      start_job_id = None
   for (job_id, row) in enumerate(job_table) :
      if row['job_name'] == start_job_name :
         start_job_id = job_id
   if start_job_id == None :
      root_job_name = job_table[0]['job_name']
      msg  = f'start_job_name = {start_job_name} is not a valid job name '
      msg += 'for this cascade.\n'
      msg += f'The root job name for this cascade is {root_job_name}.'
      assert False, msg
   #
   # at_cascade_log_dict
   at_cascade_log_dict = at_cascade.check_log(
      message_type       = 'at_cascade'         ,
      all_node_database  = all_node_db          ,
      root_node_database = root_node_database   ,
      fit_goal_set       = fit_goal_set         ,
      start_job_id       = start_job_id         ,
      max_job_depth      = max_job_depth        ,
   )
   #
   # n_job
   n_job = len( job_table )
   assert job_table[0]['parent_job_id'] == None
   #
   # process_list
   process_list = list()
   #
   # predict_job_id_list
   predict_job_id_list    = list()
   for predict_job_id in range(n_job) :
      #
      # include_this_job
      job_depth = at_cascade.job_descendent(
         job_table, start_job_id, predict_job_id
      )
      include_this_job = False
      if job_depth != None :
         if max_job_depth == None :
            include_this_job = True
         else :
            include_this_job = job_depth <= max_job_depth
      if include_this_job :
         predict_job_id_list.append( predict_job_id )
   #
   # n_predict
   n_predict = len(predict_job_id_list)
   #
   # ----------------------------------------------------------------------
   # shared_job_status_name
   shared_memory_prefix      = get_shared_memory_prefix(all_node_db)
   start_name                = job_table[start_job_id]['job_name']
   shared_memory_prefix_plus = shared_memory_prefix + f'_pre_{start_name}'
   shared_job_status_name    = shared_memory_prefix_plus + '_job_status'
   print(f'create: {shared_job_status_name} shared memory')
   #
   # shm_job_status, shared_job_status
   tmp    = numpy.empty(len(job_table), dtype = int )
   mapped = at_cascade.map_shared( shared_job_status_name )
   shm_job_status = multiprocessing.shared_memory.SharedMemory(
      create = True, size = tmp.nbytes, name = mapped
   )
   shared_job_status = numpy.ndarray(
      tmp.shape, dtype = tmp.dtype, buffer = shm_job_status.buf
   )
   shared_job_status[:] = job_status_skip
   for predict_job_id in predict_job_id_list :
      shared_job_status[predict_job_id] = job_status_ready
   #
   # shared_lock
   shared_lock = multiprocessing.Lock()
   #
   # -------------------------------------------------------------------------
   #
   # process_list
   # execute pre_one_process for each process in process_list
   n_spawn      = min(n_predict - 1, max_number_cpu - 1)
   print( f'Predict: n_predict = {n_predict}, n_spawn = {n_spawn}' )
   process_list = list()
   for i in range(n_spawn) :
      p = multiprocessing.Process(
         target = at_cascade.csv.pre_one_process,
         args=(
            fit_dir,
            sim_dir,
            option_predict,
            all_node_db,
            all_covariate_table,
            job_table,
            node_table,
            root_node_id,
            root_split_reference_id,
            at_cascade_log_dict,
            job_status_name,
            shared_job_status_name,
            shared_lock,
         )
      )
      p.start()
      process_list.append(p)
   #
   # pre_one_process
   # use this process as well to execute pre_one_process
   at_cascade.csv.pre_one_process(
      fit_dir,
      sim_dir,
      option_predict,
      all_node_db,
      all_covariate_table,
      job_table,
      node_table,
      root_node_id,
      root_split_reference_id,
      at_cascade_log_dict,
      job_status_name,
      shared_job_status_name,
      shared_lock,
   )
   #
   # join
   # wait for all the processes to finish
   for p in process_list :
      p.join()
   #
   # pre_user
   at_cascade.csv.pre_user(
      fit_dir,
      sim_dir,
      job_table,
      start_job_name,
      predict_job_id_list,
      node_table,
      root_node_id,
      root_split_reference_id,
      root_node_database,
   )
   #
   # shm_job_status
   print(f'remove: {shared_job_status_name} shared memory')
   shm_job_status.close()
   shm_job_status.unlink()
