# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin run_parallel}
{xrst_spell
   cpus
}

Run With Specified Maximum Number of Processes
##############################################

Syntax
******
{xrst_literal
   # BEGIN syntax
   # END syntax
}

Default Value
*************
None of the arguments to this routine can be ``None``.

job_table
*********
:ref:`run_one_job@job_table`

start_job_id
************
This is the :ref:`create_job_table@job_table@job_id`
for the starting job.
The run_parallel routine will not return until this job,
and all it descendants in the job table, have been run.

all_node_database
*****************
:ref:`run_one_job@all_node_database`

node_table
**********
:ref:`run_one_job@node_table`

fit_integrand
*************
:ref:`run_one_job@fit_integrand`

fit_node_database
*****************
:ref:`run_one_job@fit_node_database`

skip_start_job
**************
If this is true (false) the job corresponding to *start_job_id*
will be skipped (will not be skipped).
If this argument is true, the start job must have already been run.
This is useful when continuing a cascade.

max_number_cpu
**************
This is the maximum number of cpus (processes) to use.
This must be greater than zero.
If it is one, the jobs are run sequentially; i.e., not in parallel.

fit_type_list
*************
This is a list with one or two elements
and its possible elements are ``both`` and ``fixed``.
For each job, the first type of fit is attempted.
If it fails, and there is a second type of fit, it is attempted.
If it also fails, the corresponding job fails.

trace.out
*********
If the *max_number_cpu* is one, standard output is not redirected.
Otherwise, standard output for each job is written to a file called
``trace.out`` in the same directory as the database for the job.

{xrst_end run_parallel}
'''
# ----------------------------------------------------------------------------
import datetime
import multiprocessing
from multiprocessing import shared_memory
import numpy
import at_cascade
import dismod_at
# ----------------------------------------------------------------------------
job_status_wait  = 0 # job is waiting for it's parent job to finish
job_status_ready = 1 # job is readiy to run
job_status_run   = 2 # job is running
job_status_done  = 3 # job finished running
job_status_error = 4 # job had an exception
job_status_abort = 5 # job is a descendant of a job that had an exception
job_status_name  = [ 'wait', 'ready', 'run', 'done', 'error', 'abort' ]
# ----------------------------------------------------------------------------
def get_shared_memory_prefix(all_node_database) :
   new                  = False
   connection           = dismod_at.create_connection(all_node_database, new)
   all_option_table     = dismod_at.get_table_dict(connection, 'all_option')
   shared_memory_prefix = ""
   for row in all_option_table :
      if row['option_name'] == 'shared_memory_prefix' :
         shared_memory_prefix = row['option_value']
   return shared_memory_prefix
# ----------------------------------------------------------------------------
def get_result_database_dir(
   all_node_database, node_table, fit_node_id, fit_split_reference_id
) :
   #
   # all_option, node_split_table, split_reference_table
   new              = False
   connection       = dismod_at.create_connection(all_node_database, new)
   all_option_table = dismod_at.get_table_dict(connection, 'all_option')
   node_split_table = dismod_at.get_table_dict(connection, 'node_split')
   split_reference_table = \
      dismod_at.get_table_dict(connection, 'split_reference')
   connection.close()
   #
   # result_dir, root_node_name
   result_dir              = None
   root_node_id            = None
   root_split_reference_id = None
   for row in all_option_table :
      if row['option_name'] == 'result_dir' :
         result_dir = row['option_value']
      if row['option_name'] == 'root_node_name' :
         root_node_name = row['option_value']
         root_node_id   = \
            at_cascade.table_name2id(node_table, 'node', root_node_name)
      if row['option_name'] == 'root_split_reference_name' :
         root_split_reference_name = row['option_value']
         root_split_reference_id = at_cascade.table_name2id(
            split_reference_table,
            'split_reference',
            root_split_reference_name
         )
   assert result_dir is not None
   assert root_node_id is not None
   #
   # node_split_set
   node_split_set = set()
   for row in node_split_table :
      node_split_set.add( row['node_id'] )
   #
   database_dir = at_cascade.get_database_dir(
      node_table              = node_table,
      split_reference_table   = split_reference_table,
      node_split_set          = node_split_set,
      root_node_id            = root_node_id,
      root_split_reference_id = root_split_reference_id,
      fit_node_id             = fit_node_id,
      fit_split_reference_id  = fit_split_reference_id,
   )
   return f'{result_dir}/{database_dir}'
# )
# ----------------------------------------------------------------------------
def try_one_job(
   job_table,
   this_job_id,
   all_node_database,
   node_table,
   fit_integrand,
   skip_this_job,
   max_number_cpu,
   master_process,
   fit_type_list,
   lock,
   event,
   shared_job_status,
)  :
   assert type(job_table) == list
   assert type(this_job_id) == int
   assert type(all_node_database) == str
   assert type(node_table) == list
   assert type(fit_integrand) == set
   assert type(skip_this_job) == bool
   assert type(max_number_cpu) == int
   assert type(master_process) == bool
   assert type(fit_type_list) == list
   #
   # database_dir
   row = job_table[this_job_id]
   fit_node_id            = row['fit_node_id']
   fit_split_reference_id = row['split_reference_id']
   result_database_dir = get_result_database_dir(
      all_node_database,
      node_table,
      fit_node_id,
      fit_split_reference_id
   )
   #
   # job_name
   job_name = job_table[this_job_id]['job_name']
   #
   # trace_file_obj
   trace_file_obj = None
   if max_number_cpu > 1 :
      trace_file_name = f'{result_database_dir}/trace.out'
      trace_file_obj  = open(trace_file_name, 'w')
   #
   # job_done, fit_type_index, fit_type
   job_done       = False
   fit_type_index = 0
   while (not job_done) and ( fit_type_index < len(fit_type_list) ) :
      fit_type        = fit_type_list[fit_type_index]
      fit_type_index += 1
      #
      # print message at start of this fit
      now             = datetime.datetime.now()
      current_time    = now.strftime("%H:%M:%S")
      print( f'Begin: fit {fit_type:<5} {current_time}: {job_name}' )
      #
      try :
         # run_one_job
         # the lock should not be aquired during this operation
         at_cascade.run_one_job(
            job_table         = job_table,
            run_job_id        = this_job_id ,
            all_node_database = all_node_database,
            node_table        = node_table,
            fit_integrand     = fit_integrand,
            fit_type          = fit_type,
            first_fit         = fit_type_index == 1,
            trace_file_obj    = trace_file_obj,
         )
         #
         # job_done
         job_done = True
      except Exception as e:
         job_done = False
         #
         print( f'\nfit {fit_type:<5} {job_name} message:\n' + str(e) )
   #
   if job_done :
      #
      # lock
      lock.acquire()
      #
      # shared_job_status
      assert shared_job_status[this_job_id] == job_status_run
      shared_job_status[this_job_id] = job_status_done
      #
      # shared_job_status[child_job_id] = job_status_ready
      start_child_job_id    = job_table[this_job_id ]['start_child_job_id']
      end_child_job_id      = job_table[this_job_id ]['end_child_job_id']
      child_range = range(start_child_job_id, end_child_job_id)
      for child_job_id in child_range :
         assert shared_job_status[child_job_id] == job_status_wait
         shared_job_status[child_job_id] = job_status_ready
      #
      # release
      # shared memory has changed
      event.set()
      lock.release()
      #
   else :
      # if job not ok
      #
      # descendant_set
      descendant_set = { this_job_id }
      n_job          = len(job_table)
      for job_id in range(this_job_id + 1, n_job) :
         parent_job_id = job_table[job_id]['parent_job_id']
         if parent_job_id in descendant_set :
            descendant_set.add( job_id )
      descendant_set.remove( this_job_id )
      #
      # lock
      lock.acquire()
      #
      # shared_job_status[this_job_id]
      if shared_job_status[this_job_id] != job_status_run :
         msg  = 'try_one_job: except: shared_job_status[this_job_id] = '
         msg += job_status_name[ shared_job_status[this_job_id] ]
         print(msg)
      shared_job_status[this_job_id] = job_status_error
      #
      # shared_job_status[descendant_set]
      for job_id in descendant_set :
         if shared_job_status[job_id] != job_status_wait :
            msg  = 'try_one_job: except: shared_job_status[job_id] = '
            msg += job_status_name[ shared_job_status[job_id] ]
            print(msg)
         shared_job_status[job_id] = job_status_abort
      #
      # release
      # shared memory has changed
      event.set()
      lock.release()
      #
      # raise
      # This prints stack trace when we are not running in parallel
      if max_number_cpu == 1 :
         raise
      #
      # ok
      job_done = False
   #
   if max_number_cpu > 1 :
      #
      # print message at end
      job_name     = job_table[this_job_id]['job_name']
      now          = datetime.datetime.now()
      current_time = now.strftime("%H:%M:%S")
      if job_done :
         print( f'End:   fit {fit_type:<5} {current_time}: {job_name}' )
      else :
         print( f'Error: fit {fit_type:<5} {current_time}: {job_name}' )
      #
      # status_count
      lock.acquire()
      n_status      = len( job_status_name )
      status_count  = dict()
      for job_status_i in range(n_status) :
         name               = job_status_name[job_status_i]
         status_count[name] =  sum( shared_job_status == job_status_i )
      lock.release()
      #
      print( f'       {status_count}' )
      #
      trace_file_obj.close()
   return
# ----------------------------------------------------------------------------
def run_parallel_job(
   job_table,
   this_job_id,
   all_node_database,
   node_table,
   fit_integrand,
   skip_this_job,
   max_number_cpu,
   master_process,
   fit_type_list,
   lock,
   event,
) :
   assert type(job_table)         == list
   assert type(this_job_id)       == int
   assert type(all_node_database) == str
   assert type(node_table)        == list
   assert type(fit_integrand)     == set
   assert type(skip_this_job)     == bool
   assert type(max_number_cpu)    == int
   assert type(master_process)    == bool
   assert type(fit_type_list)     == list
   # ----------------------------------------------------------------------
   # shared_memory_prefix
   shared_memory_prefix = get_shared_memory_prefix(all_node_database)
   # ----------------------------------------------------------------------
   # shared_number_cpu_inuse
   tmp  = numpy.empty(1, dtype = int )
   name = shared_memory_prefix + '_number_cpu_inuse'
   shm_number_cpu_inuse = shared_memory.SharedMemory(
      create = False, name = name
   )
   shared_number_cpu_inuse = numpy.ndarray(
      tmp.shape, dtype = tmp.dtype, buffer = shm_number_cpu_inuse.buf
   )
   # ----------------------------------------------------------------------
   # shared_job_status
   tmp  = numpy.empty(len(job_table), dtype = int )
   name = shared_memory_prefix + '_job_status'
   shm_job_status = shared_memory.SharedMemory(
      create = False, name = name
   )
   shared_job_status = numpy.ndarray(
      tmp.shape, dtype = tmp.dtype, buffer = shm_job_status.buf
   )
   # ----------------------------------------------------------------------
   #
   # shm_list
   shm_list = [
         shm_number_cpu_inuse,
         shm_job_status,
   ]
   # job_id_array
   # job_id_array
   job_id_array = numpy.array( range(len(job_table)), dtype = int )
   #
   if not skip_this_job :
      #
      # try_one_job
      # assumes lock not aquired during this operation
      try_one_job(
         job_table,
         this_job_id,
         all_node_database,
         node_table,
         fit_integrand,
         skip_this_job,
         max_number_cpu,
         master_process,
         fit_type_list,
         lock,
         event,
         shared_job_status,
      )
   #
   while True :
      # lock
      lock.acquire()
      #
      # job_id_ready
      job_id_ready = job_id_array[ shared_job_status == job_status_ready ]
      #
      # job_id_run
      job_id_run  = job_id_array[ shared_job_status == job_status_run ]
      #
      # n_job_ready
      n_job_ready = job_id_ready.size
      #
      if n_job_ready == 0 :
         if job_id_run.size == 0 :
            #
            # no jobs running or ready
            if master_process and shared_number_cpu_inuse[0] == 1:
               # We are done, return to run_parallel which wuill use
               # the shared memory for error checking and then free it.
               #
               # should not need this release
               lock.release()
               #
               return
            else :
               # return this processor
               shared_number_cpu_inuse[0] -= 1
               #
               # release
               # shared memory has changed
               event.set()
               lock.release()
               #
               # this process is done with its shared memory
               for shm in shm_list :
                  shm.close()
               return
         else :
            #
            # jobs are running but none are ready
            if master_process :
               #
               # wait for another process to shared memory,
               # then go back to the while True point above
               event.clear()
               lock.release()
               event.wait()
            else :
               # return this processor
               shared_number_cpu_inuse[0] -= 1
               #
               # release
               lock.release()
               #
               # this process is done with its shared memory
               for shm in shm_list :
                  shm.close()
               return
      else :
         #
         # n_cpu_spawn
         n_cpu_available  = max_number_cpu - shared_number_cpu_inuse[0]
         n_cpu_spawn      = min(n_cpu_available, n_job_ready - 1)
         #
         # shared_numper_cpu_inuse
         shared_number_cpu_inuse[0] += n_cpu_spawn
         #
         # shared_job_status
         for i in range( n_cpu_spawn + 1 ) :
            job_id = job_id_ready[i]
            #
            assert shared_job_status[job_id] == job_status_ready
            shared_job_status[job_id] = job_status_run
         #
         # release
         # shared memory has changed
         event.set()
         lock.release()
         #
         # skip_child_job
         skip_child_job = False
         #
         # is_child_master_process
         is_child_master_process = False
         #
         # spawn the new processes
         for i in range(n_cpu_spawn) :
            #
            # job_id
            job_id = int( job_id_ready[i] )
            #
            # p
            args = (
               job_table,
               job_id,
               all_node_database,
               node_table,
               fit_integrand,
               skip_child_job,
               max_number_cpu,
               is_child_master_process,
               fit_type_list,
               lock,
               event,
            )
            target = run_parallel_job
            p = multiprocessing.Process(target = target, args = args)
            #
            p.deamon = False
            p.start()
         #
         # job_id
         job_id = int( job_id_ready[n_cpu_spawn] )
         #
         # try_one_job
         # assumes lock is not acquired during this operation
         try_one_job(
            job_table,
            job_id,
            all_node_database,
            node_table,
            fit_integrand,
            skip_this_job,
            max_number_cpu,
            master_process,
            fit_type_list,
            lock,
            event,
            shared_job_status,
         )
# ----------------------------------------------------------------------------
def run_parallel(
# BEGIN syntax
# at_cascade.run_parallel(
   job_table         = None,
   start_job_id      = None,
   all_node_database = None,
   node_table        = None,
   fit_integrand     = None,
   skip_start_job    = None,
   max_number_cpu    = None,
   fit_type_list     = None,
# )
# END syntax
) :
   #
   assert type(job_table)         == list
   assert type(start_job_id)      == int
   assert type(all_node_database) == str
   assert type(node_table)        == list
   assert type(fit_integrand)     == set
   assert type(skip_start_job)    == bool
   assert type(max_number_cpu)    == int
   assert type(fit_type_list)     == list
   # ----------------------------------------------------------------------
   # shared_memory_prefix
   shared_memory_prefix = get_shared_memory_prefix(all_node_database)
   # -------------------------------------------------------------------------
   # shared_number_cpu_inuse
   tmp  = numpy.empty(1, dtype = int )
   name = shared_memory_prefix + '_number_cpu_inuse'
   shm_number_cpu_inuse = shared_memory.SharedMemory(
      create = True, size = tmp.nbytes, name = name
   )
   shared_number_cpu_inuse = numpy.ndarray(
      tmp.shape, dtype = tmp.dtype, buffer = shm_number_cpu_inuse.buf
   )
   # -------------------------------------------------------------------------
   # shared_job_status
   tmp  = numpy.empty(len(job_table), dtype = int )
   name = shared_memory_prefix + '_job_status'
   shm_job_status = shared_memory.SharedMemory(
      create = True, size = tmp.nbytes, name = name
   )
   shared_job_status = numpy.ndarray(
      tmp.shape, dtype = tmp.dtype, buffer = shm_job_status.buf
   )
   # -------------------------------------------------------------------------
   #
   # shm_list
   shm_list = [
         shm_number_cpu_inuse,
         shm_job_status,
   ]
   #
   # shared_number_cpu_inuse
   shared_number_cpu_inuse[0] = 1
   #
   # shared_job_status
   shared_job_status[:]  = job_status_wait
   if skip_start_job :
      shared_job_status[start_job_id] = job_status_done
      #
      # shared_job_status[child_job_id] = job_status_ready
      start_child_job_id    = job_table[start_job_id ]['start_child_job_id']
      end_child_job_id      = job_table[start_job_id ]['end_child_job_id']
      child_range = range(start_child_job_id, end_child_job_id)
      for child_job_id in child_range :
         shared_job_status[child_job_id] = job_status_ready
   else :
      shared_job_status[start_job_id] = job_status_run
   #
   # master_process
   master_process = True
   #
   # lock
   lock = multiprocessing.Lock()
   #
   # event
   # shared memory has changed
   event = multiprocessing.Event()
   event.set()
   #
   # run_parallel_job
   run_parallel_job(
      job_table,
      start_job_id,
      all_node_database,
      node_table,
      fit_integrand,
      skip_start_job,
      max_number_cpu,
      master_process,
      fit_type_list,
      lock,
      event,
   )
   #
   # shared_number_cpu_inuse
   assert shared_number_cpu_inuse == 1
   #
   # shared_job_status
   for job_id in range(0, len(job_table) ):
      status = shared_job_status[job_id]
      assert status in [ job_status_done, job_status_error, job_status_abort ]
   #
   # free shared memory objects
   for shm in shm_list :
      shm.close()
      shm.unlink()
   #
   return
