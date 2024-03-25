# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-23 Bradley M. Bell
# ----------------------------------------------------------------------------
# Set this to False when debugging an exception during fit_one_job routine
catch_exceptions_and_continue = True
# ----------------------------------------------------------------------------
'''
{xrst_begin fit_one_process}
{xrst_spell
   cpus
   inuse
   numpy
   dtype
}

Fit Using One Process
#####################
Keep fitting jobs for as long as there are jobs ready to be fit.

Prototype
*********
{xrst_literal
   # BEGIN DEF
   # END DEF
}

job_table
*********
This is a :ref:`create_job_table@job_table` containing all the jobs
necessary to fit the :ref:`glossary@fit_goal_set` .

this_job_id
***********
if skip_this_job is false,
the fit for this ref:`create_job_table@job_table@job_id` is ready to be fit
and will be fit first.
Otherwise, *this_job_id* is ignored.

all_node_database
*****************
:ref:`fit_one_job@all_node_database`

node_table
**********
:ref:`fit_one_job@node_table`

fit_integrand
*************
:ref:`fit_one_job@fit_integrand`

skip_this_job
*************
see :ref:`fit_one_process@this_job_id` above.

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

job_status_name
***************
is the name corresponding to each possible job status integer values.
If *i* is an integer job status value, *job_status_name* [ *i* ] is the
corresponding name.

.. csv-table::
   :header-rows: 1

   Name,    Meaning
   'skip' , This is a prior only job and completed by the parent fit
   'wait',  job is waiting for it's parent job to finish
   'ready', job is ready to run
   'run',   job is running
   'done',  job finished running
   'error', job had an exception
   'abort', job is a descendant of a job that had an exception

shared_job_status_name
**********************
This is the name of the shared job status memory.
The corresponding multiprocessing shared memory is
a numpy array with ``dtype`` equal to ``int`` and
with length equal to the length of *job_table* .
The value *shared_job_status* [ *job_table_index* ] is the
integer status code for the corresponding job; see *job_status_name* above.

number_cpu_inuse
****************
This is the name of the number of cpus in use memory.
The corresponding multiprocessing shared memory is
a numpy array with ``dtype`` equal to ``int`` and
with length equal to one.
The value *number_cpu_inuse* [0] is the number of cpus (precesses)
currently fitting this cascade.

shared_lock
***********
is a shared memory lock, used by all the fit processes,
that must be acquired to read or write shared memory; i.e.,
*shared_job_status* or *shared_number_cpu_in_use* .

shared_event
************
is multiprocessing event,  used by all the fit processes,
that is used to signal that the shared memory has changed.

{xrst_end fit_one_process}
'''
# ----------------------------------------------------------------------------
import sys
import datetime
import multiprocessing
from multiprocessing import shared_memory
import numpy
import at_cascade
import dismod_at
# ----------------------------------------------------------------------------
# acquire lock
def acquire_lock(shared_lock) :
   seconds = 10
   ok = shared_lock.acquire(
      block   = True,
      timeout = seconds
   )
   if not ok :
      msg = f'pre_one_process: did not obtain lock in {seconds} seconds'
      sys.exit(msg)
# ----------------------------------------------------------------------------
def get_result_database_dir(
   all_node_database, node_table, fit_node_id, fit_split_reference_id
) :
   #
   # option_all, node_split_table, split_reference_table
   connection       = dismod_at.create_connection(
      all_node_database, new = False, readonly = True
   )
   option_all_table = dismod_at.get_table_dict(connection, 'option_all')
   node_split_table = dismod_at.get_table_dict(connection, 'node_split')
   split_reference_table = \
      dismod_at.get_table_dict(connection, 'split_reference')
   connection.close()
   #
   # result_dir, root_node_name
   result_dir              = None
   root_node_id            = None
   root_split_reference_id = None
   for row in option_all_table :
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
   shared_lock,
   shared_event,
   shared_job_status,
   job_status_name,
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
   # job_status_name
   job_status_skip  = job_status_name.index( 'skip' )
   job_status_wait  = job_status_name.index( 'wait' )
   job_status_ready = job_status_name.index( 'ready' )
   job_status_run   = job_status_name.index( 'run' )
   job_status_done  = job_status_name.index( 'done' )
   job_status_error = job_status_name.index( 'error' )
   job_status_abort = job_status_name.index( 'abort' )
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
   # prior_only
   assert not job_table[this_job_id]['prior_only']
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
      print( f'Begin: {current_time}: fit {fit_type:<5} {job_name}' )
      #
      # fit_one_job
      # the lock should not be aquired during this operation
      if not catch_exceptions_and_continue :
         at_cascade.fit_one_job(
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
      else :
         try :
            at_cascade.fit_one_job(
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
      # shared_lock
      acquire_lock(shared_lock)
      #
      # shared_job_status
      assert shared_job_status[this_job_id] == job_status_run
      shared_job_status[this_job_id] = job_status_done
      #
      # shared_job_status[child_job_id]
      start_child_job_id    = job_table[this_job_id ]['start_child_job_id']
      end_child_job_id      = job_table[this_job_id ]['end_child_job_id']
      child_range = range(start_child_job_id, end_child_job_id)
      for child_job_id in child_range :
         if shared_job_status[child_job_id] == job_status_wait :
            assert not job_table[child_job_id]['prior_only']
            shared_job_status[child_job_id] = job_status_ready
         else :
            assert job_table[child_job_id]['prior_only']
            assert shared_job_status[child_job_id] == job_status_skip
      #
      # release
      # shared memory has changed
      shared_event.set()
      shared_lock.release()
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
      # shared_lock
      acquire_lock(shared_lock)
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
         if shared_job_status[job_id] != job_status_skip :
            if shared_job_status[job_id] != job_status_wait :
               msg  = 'try_one_job: except: shared_job_status[job_id] = '
               msg += job_status_name[ shared_job_status[job_id] ]
               print(msg)
            shared_job_status[job_id] = job_status_abort
      #
      # release
      # shared memory has changed
      shared_event.set()
      shared_lock.release()
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
         print( f'End:   {current_time}: fit {fit_type:<5} {job_name}' )
      else :
         print( f'Error: {current_time}: fit {fit_type:<5} {job_name}' )
      #
      # status_count
      acquire_lock(shared_lock)
      n_status      = len( job_status_name )
      status_count  = dict()
      for job_status_i in range(n_status) :
         name               = job_status_name[job_status_i]
         status_count[name] =  sum( shared_job_status == job_status_i )
      shared_lock.release()
      #
      print( f'       {status_count}' )
      #
      trace_file_obj.close()
   return
# ----------------------------------------------------------------------------
# BEGIN DEF
def fit_one_process(
   job_table,
   this_job_id,
   all_node_database,
   node_table,
   fit_integrand,
   skip_this_job,
   max_number_cpu,
   master_process,
   fit_type_list,
   job_status_name,
   shared_job_status_name,
   shared_number_cpu_inuse_name,
   shared_lock,
   shared_event,
) :
   assert type(job_table)            == list
   assert type(this_job_id)          == int
   assert type(all_node_database)    == str
   assert type(node_table)           == list
   assert type(fit_integrand)        == set
   assert type(skip_this_job)        == bool
   assert type(max_number_cpu)       == int
   assert type(master_process)       == bool
   assert type(fit_type_list)        == list
   assert type(job_status_name)      == list
   assert type( job_status_name[0] ) == str
   assert type(shared_job_status_name)       == str
   assert type(shared_number_cpu_inuse_name) == str
   assert type(shared_lock)          == multiprocessing.synchronize.Lock
   assert type(shared_event)         == multiprocessing.synchronize.Event
   # END DEF
   # ----------------------------------------------------------------------
   job_status_skip  = job_status_name.index( 'skip' )
   job_status_wait  = job_status_name.index( 'wait' )
   job_status_ready = job_status_name.index( 'ready' )
   job_status_run   = job_status_name.index( 'run' )
   job_status_done  = job_status_name.index( 'done' )
   job_status_error = job_status_name.index( 'error' )
   job_status_abort = job_status_name.index( 'abort' )
   # ----------------------------------------------------------------------
   #
   # shm_job_status, shared_job_status
   tmp  = numpy.empty(len(job_table), dtype = int )
   shm_job_status = multiprocessing.shared_memory.SharedMemory(
      create = False, size = tmp.nbytes, name = shared_job_status_name
   )
   shared_job_status = numpy.ndarray(
      tmp.shape, dtype = tmp.dtype, buffer = shm_job_status.buf
   )
   #
   # shm_number_cpu_inuse, shared_number_cpu_inuse
   tmp  = numpy.empty(1, dtype = int )
   shm_number_cpu_inuse = multiprocessing.shared_memory.SharedMemory(
      create = False, size = tmp.nbytes, name = shared_number_cpu_inuse_name
   )
   shared_number_cpu_inuse = numpy.ndarray(
      tmp.shape, dtype = tmp.dtype, buffer = shm_number_cpu_inuse.buf
   )
   #
   # job_table_index
   job_table_index = numpy.array( range(len(job_table)), dtype = int )
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
         shared_lock,
         shared_event,
         shared_job_status,
         job_status_name,
      )
   #
   while True :
      # shared_lock
      acquire_lock(shared_lock)
      #
      # job_id_ready
      job_id_ready = job_table_index[ shared_job_status == job_status_ready ]
      #
      # job_id_run
      job_id_run  = job_table_index[ shared_job_status == job_status_run ]
      #
      # n_job_ready
      n_job_ready = job_id_ready.size
      #
      if n_job_ready == 0 :
         if job_id_run.size == 0 :
            #
            # no jobs running or ready
            if master_process and shared_number_cpu_inuse[0] == 1:
               # We are done, return to fit_parallel which wuill use
               # the shared memory for error checking and then free it.
               #
               # should not need this release
               shared_lock.release()
               #
               shm_job_status.close()
               shm_number_cpu_inuse.close()
               return
            else :
               # return this processor
               shared_number_cpu_inuse[0] -= 1
               #
               # release
               # shared memory has changed
               shared_event.set()
               shared_lock.release()
               #
               shm_job_status.close()
               shm_number_cpu_inuse.close()
               return
         else :
            #
            # jobs are running but none are ready
            if master_process :
               #
               # wait for another process to change shared memory,
               # then go back to the while True point above
               shared_event.clear()
               shared_lock.release()
               seconds = 10.0
               shared_event.wait(timeout = seconds)
            else :
               # return this processor
               shared_number_cpu_inuse[0] -= 1
               #
               # release
               shared_lock.release()
               #
               shm_job_status.close()
               shm_number_cpu_inuse.close()
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
         shared_event.set()
         shared_lock.release()
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
               job_status_name,
               shared_job_status_name,
               shared_number_cpu_inuse_name,
               shared_lock,
               shared_event,
            )
            target = fit_one_process
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
            shared_lock,
            shared_event,
            shared_job_status,
            job_status_name,
         )
