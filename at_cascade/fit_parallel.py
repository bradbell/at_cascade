# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-23 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin fit_parallel}
{xrst_spell
   cpus
}

Fit With Specified Maximum Number of Processes
##############################################

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

start_job_id
************
This is the :ref:`create_job_table@job_table@job_id`
for the starting job.
The fit_parallel routine will not return until this job,
and all it descendants in the job table, have been run,
or an error occurs that prevents a job from completing..

all_node_database
*****************
:ref:`fit_one_job@all_node_database`

node_table
**********
:ref:`fit_one_job@node_table`

fit_integrand
*************
:ref:`fit_one_job@fit_integrand`

skip_start_job
**************
If this is true (false) the job corresponding to *start_job_id*
will be skipped (will not be skipped).
If this argument is true, the start job must have already been run.
This is useful when using :ref:`continue_cascade-name` .

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

shared_unique
*************
All of these jobs us the following two python multiprocessing
shared memory names:

|  *shared_memory_prefix* _ *shared_unique* _  *job_name* _number_cpu_in_use
|  *shared_memory_prefix* _ *shared_unique* _  *job_name* _job_status``

#. *shared_unique* is text that makes this shared name unique among
   all the currently running calls to fit_parallel.
   It is suggested that you use ``fit`` for this value unless you
   are running more than one call with the same prefix and job name.
#. *job_name* is *job_table* [ *start_job_id* ] [ ``"job_name"`` ]
#. :ref:`option_all_table@shared_memory_prefix` is specified
   in the option all table.

trace.out
*********
If the *max_number_cpu* is one, standard output is not redirected.
Otherwise, standard output for each job is written to a file called
``trace.out`` in the same directory as the database for the job.

{xrst_end fit_parallel}
'''
# ----------------------------------------------------------------------------
import multiprocessing
import numpy
import at_cascade
import dismod_at
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
# at_cascade.fit_parallel
def fit_parallel(
   job_table         ,
   start_job_id      ,
   all_node_database ,
   node_table        ,
   fit_integrand     ,
   skip_start_job    ,
   max_number_cpu    ,
   fit_type_list     ,
   shared_unique     ,
# )
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
   assert type(shared_unique)     == str
   # END DEF
   # ----------------------------------------------------------------------
   # job_status_name
   job_status_name = [
      'skip' , # This is a prior only job and completed by the parent fit
      'wait' , # job is waiting for it's parent job to finish
      'ready', # job is readiy to run
      'run'  , # job is running
      'done' , # job finished running
      'error', # job had an exception and could not recover
      'abort', # job is a descendant of a job that could not recover
   ]
   job_status_skip  = job_status_name.index( 'skip' )
   job_status_wait  = job_status_name.index( 'wait' )
   job_status_ready = job_status_name.index( 'ready' )
   job_status_run   = job_status_name.index( 'run' )
   job_status_done  = job_status_name.index( 'done' )
   job_status_error = job_status_name.index( 'error' )
   job_status_abort = job_status_name.index( 'abort' )
   # ----------------------------------------------------------------------
   # shared_memory_prefix_plus
   shared_memory_prefix = get_shared_memory_prefix(all_node_database)
   start_name           = job_table[start_job_id]['job_name']
   shared_memory_prefix_plus = \
      f'{shared_memory_prefix}_{shared_unique}_fit_{start_name}'
   print(f'create: {shared_memory_prefix_plus} shared memory')
   # -------------------------------------------------------------------------
   # shm_number_cpu_inuse, shared_number_cpu_inuse
   tmp  = numpy.empty(1, dtype = int )
   name = shared_memory_prefix_plus + '_number_cpu_inuse'
   shm_number_cpu_inuse = multiprocessing.shared_memory.SharedMemory(
      create = True, size = tmp.nbytes, name = name
   )
   shared_number_cpu_inuse = numpy.ndarray(
      tmp.shape, dtype = tmp.dtype, buffer = shm_number_cpu_inuse.buf
   )
   # -------------------------------------------------------------------------
   # shm_job_status, shared_job_status
   tmp  = numpy.empty(len(job_table), dtype = int )
   name = shared_memory_prefix_plus + '_job_status'
   shm_job_status = multiprocessing.shared_memory.SharedMemory(
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
   for job_id in range( len(job_table) ) :
      if job_table[job_id]['prior_only'] :
         shared_job_status[job_id] = job_status_skip
      else :
         shared_job_status[job_id]  = job_status_wait
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
   # shared_lock
   shared_lock = multiprocessing.Lock()
   #
   # shared_event
   # shared memory has changed
   shared_event = multiprocessing.Event()
   shared_event.set()
   #
   # fit_one_process
   at_cascade.fit_one_process(
      job_table,
      start_job_id,
      all_node_database,
      node_table,
      fit_integrand,
      skip_start_job,
      max_number_cpu,
      master_process,
      fit_type_list,
      job_status_name,
      shm_job_status.name,
      shm_number_cpu_inuse.name,
      shared_lock,
      shared_event,
   )
   #
   # shared_number_cpu_inuse
   if shared_number_cpu_inuse[0] != 1 :
      n_inuse = shared_number_cpu_inuse[0]
      msg =f'{shared_memory_prefix_plus}_number_cpu_inuse[0] = {n_inuse}'
      assert msg, False
   #
   # shared_job_status
   # 2DO: jobs that come before the start job should be in wait state ?
   for job_id in range(0, len(job_table) ):
      status = shared_job_status[job_id]
      assert status in \
         [job_status_done, job_status_error, job_status_abort, job_status_skip]
   #
   # free shared memory objects
   print(f'remove: {shared_memory_prefix_plus} shared memory')
   for shm in shm_list :
      shm.close()
      shm.unlink()
   #
   return
