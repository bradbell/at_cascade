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

trace.out
*********
If the *max_number_cpu* is one, standard output is not redirected.
Otherwise, standard output for each job is written to a file called
``trace.out`` in the same directory as the database for the job.

Shared Memory
*************
All of these jobs us the following two python multiprocessing
shared memory names:

|  *shared_memory_prefix*\ ``_``\ *job_name*\ ``_number_cpu_in_use``
|  *shared_memory_prefix*\ ``_``\ *job_name*\ ``_job_status``

where *job_name* is *job_table* [ *start_job_id* ] [ ``"job_name"`` ]
and :ref:`option_all_table@shared_memory_prefix` is specified
in the option all table.

{xrst_end fit_parallel}
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
   # END DEF
   # ----------------------------------------------------------------------
   # shared_memory_prefix_plus
   shared_memory_prefix = get_shared_memory_prefix(all_node_database)
   start_name           = job_table[start_job_id]['job_name']
   shared_memory_prefix_plus = shared_memory_prefix + f'_{start_name}'
   print(f'create: {shared_memory_prefix_plus} shared memory')
   # -------------------------------------------------------------------------
   # shared_number_cpu_inuse
   tmp  = numpy.empty(1, dtype = int )
   name = shared_memory_prefix_plus + '_number_cpu_inuse'
   shm_number_cpu_inuse = shared_memory.SharedMemory(
      create = True, size = tmp.nbytes, name = name
   )
   shared_number_cpu_inuse = numpy.ndarray(
      tmp.shape, dtype = tmp.dtype, buffer = shm_number_cpu_inuse.buf
   )
   # -------------------------------------------------------------------------
   # shared_job_status
   tmp  = numpy.empty(len(job_table), dtype = int )
   name = shared_memory_prefix_plus + '_job_status'
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
   # fit_one_process
   at_cascade.fit_one_process(
      shared_memory_prefix_plus,
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
   if shared_number_cpu_inuse[0] != 1 :
      n_inuse = shared_number_cpu_inuse[0]
      msg =f'{shared_memory_prefix_plus}_number_cpu_inuse[0] = {n_inuse}'
      assert msg, False
   #
   # shared_job_status
   for job_id in range(0, len(job_table) ):
      status = shared_job_status[job_id]
      assert status in [ job_status_done, job_status_error, job_status_abort ]
   #
   # free shared memory objects
   print(f'remove: {shared_memory_prefix_plus} shared memory')
   for shm in shm_list :
      shm.close()
      shm.unlink()
   #
   return
