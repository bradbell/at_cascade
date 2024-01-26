# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-23 Bradley M. Bell
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
import queue
# ----------------------------------------------------------------------------
# BEGIN DEF
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
   # node_table
   connection      = dismod_at.create_connection(
      root_node_database, new = False, readonly = True
   )
   node_table      = dismod_at.get_table_dict(connection, 'node')
   connection.close()
   #
   # root_node_id
   root_node_id = at_cascade.table_name2id(
      node_table, 'node', root_node_name
   )
   #
   # node_split_set
   node_split_set = { root_node_id }
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
   # root_split_reference_id
   root_split_reference_id = 1
   assert 'both' == split_reference_table[1]['split_reference_name']
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
   # error_message_dict
   error_message_dict = at_cascade.check_log(
      message_type       = 'error'              ,
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
   # manager
   manager = multiprocessing.Manager()
   #
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
   # job_queue
   # Need Manager; see https://bugs.python.org/issue18277
   job_queue   = manager.Queue()
   for predict_job_id in predict_job_id_list :
      job_queue.put( predict_job_id )
   #
   # n_job_queue
   n_job_queue = len( predict_job_id_list )
   #
   # n_done_queue
   # The number of job_queue entries that have been completed
   n_done_queue   = manager.Queue()
   n_done_queue.put(0)
   #
   # process_list
   # execute pre_one_process for each process in process_list
   n_spawn      = min(n_job_queue - 1, max_number_cpu - 1)
   print( f'Predict: n_job = {n_job_queue}, n_spawn = {n_spawn}' )
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
            error_message_dict,
            job_queue,
            n_job_queue,
            n_done_queue,
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
      error_message_dict,
      job_queue,
      n_job_queue,
      n_done_queue
   )
   #
   # join
   # wait for all the processes to finish (detect an empty queue).
   for p in process_list :
      p.join()
   #
   # pre_user_csv
   at_cascade.csv.pre_user_csv(
      fit_dir,
      sim_dir,
      job_table,
      start_job_name,
      predict_job_id_list,
      node_table,
      root_node_id,
      root_node_database,
   )
