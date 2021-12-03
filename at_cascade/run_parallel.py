# -----------------------------------------------------------------------------
# at_cascade: Cascading Dismod_at Analysis From Parent To Child Regions
#           Copyright (C) 2021-21 University of Washington
#              (Bradley M. Bell bradbell@uw.edu)
#
# This program is distributed under the terms of the
#     GNU Affero General Public License version 3.0 or later
# see http://www.gnu.org/licenses/agpl.txt
# -----------------------------------------------------------------------------
'''
{xsrst_begin run_parallel}
{xsrst_spell
    cpus
}

Run With Specified Maximum Number of Processes
##############################################

Under Construction
******************

Syntax
******
{xsrst_file
    # BEGIN syntax
    # END syntax
}

Default Value
*************
None of the arguments to this routine can be ``None``.

job_table
*********
:ref:`run_one_job.job_table`

start_job_id
************
This is the :ref:`create_job_table.job_table.job_id`
for the starting job.
The run_parallel routine will not return until this job,
and all it descendants in the job table, have been run.

all_node_database
*****************
:ref:`run_one_job.all_node_database`

node_table
**********
:ref:`run_one_job.node_table`

fit_integrand
*************
:ref:`run_one_job.fit_integrand`

trace_fit
*********
:ref:`run_one_job.trace_fit`

fit_node_database
*****************
:ref:`run_one_job.fit_node_database`

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

{xsrst_end run_parallel}
'''
# ----------------------------------------------------------------------------
import multiprocessing
import at_cascade
# ----------------------------------------------------------------------------
shared_number_cpu_inuse = 0
shared_job_wait_list    = list()
shared_job_run_list     = list()
# ----------------------------------------------------------------------------
def run_parallel_job(
    job_table,
    this_job_id,
    all_node_database,
    node_table,
    fit_integrand,
    trace_fit,
    skip_this_job,
    max_number_cpu,
    master_process,
    lock,
    event,
) :
    assert type(job_table) is list
    assert type(this_job_id) is int
    assert type(all_node_database) is str
    assert type(node_table) is list
    assert type(fit_integrand) is set
    assert type(trace_fit) is bool
    assert type(skip_this_job) is bool
    assert type(max_number_cpu) is int
    assert type(master_process) is bool
    #
    global shared_number_cpu_inuse
    global shared_job_wait_list
    global shared_job_run_list
    #
    if not skip_this_job :
        #
        # run_one_job
        # do not want the lock to be aquired during this operation
        at_cascade.run_one_job(
            job_table         = job_table,
            run_job_id        = this_job_id ,
            all_node_database = all_node_database,
            node_table        = node_table,
            fit_integrand     = fit_integrand,
            trace_fit         = trace_fit,
        )
    #
    # lock
    lock.acquire()
    #
    # shared_job_run_list
    if not skip_this_job :
        index = shared_job_run_list.index( this_job_id )
        del shared_job_run_list[index]
        #
    #
    # shared_job_wait_list
    start_child_job_id    = job_table[this_job_id ]['start_child_job_id']
    end_child_job_id      = job_table[this_job_id ]['end_child_job_id']
    new_wait_range        = range(start_child_job_id, end_child_job_id)
    shared_job_wait_list += list( new_wait_range )
    #
    while True :
        # lock
        # lock is acquired at beginning of this loop
        #
        # event
        # shared_job_wait_list or shared_job_run_list may have changed
        event.set()
        #
        # n_job_wait
        n_job_wait = len(shared_job_wait_list)
        #
        if n_job_wait == 0 :
            if len( shared_job_run_list ) == 0 :
                #
                # no jobs running or waiting
                if master_process :
                    # we are done, return to run_parallel
                    lock.release()
                    return
                else :
                    # return this processor
                    shared_number_cpu_inuse -= 1
                    lock.release()
                    return
            else :
                #
                # jobs are running but none are waiting
                if master_process :
                    #
                    # wait for an event on another process,
                    # then go back to the while True point above
                    event.clear()
                    lock.release()
                    evant.wait()
                    lock.acquire()
                else :
                    # return this processor
                    shared_number_cpu_inuse -= 1
                    lock.release()
                    return
        else :
            #
            # n_cpu_spawn
            n_cpu_available  = max_number_cpu - shared_number_cpu_inuse
            n_cpu_spawn      = min(n_cpu_available, n_job_wait - 1)
            #
            # shared_numper_cpu_inuse
            shared_number_cpu_inuse += n_cpu_spawn
            #
            # job_run_list
            job_run_list = shared_job_wait_list[: n_cpu_spawn + 1]
            #
            # shared_job_wait_list
            shared_job_wait_list = shared_job_wait_list[n_cpu_spawn + 1 :]
            #
            # shared_job_run_list
            shared_job_run_list += job_run_list
            #
            # lock
            lock.release()
            #
            # event
            # shared_job_wait_list or shared_job_run_list may have changed
            event.set()
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
                # p
                args = (
                    job_table,
                    job_run_list[i] ,
                    all_node_database,
                    node_table,
                    fit_integrand,
                    trace_fit,
                    skip_child_job,
                    max_number_cpu,
                    is_child_master_process,
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
            job_id = job_run_list[n_cpu_spawn]
            #
            # run_one_job
            # do not want the lock to be aquired during this operation
            at_cascade.run_one_job(
                job_table         = job_table,
                run_job_id        = job_id,
                all_node_database = all_node_database,
                node_table        = node_table,
                fit_integrand     = fit_integrand,
                trace_fit         = trace_fit,
            )
            #
            # lock
            lock.acquire()
            #
            # shared_job_run_list
            index = shared_job_run_list.index( job_id )
            del shared_job_run_list[index]
            #
            # shared_job_wait_list
            start_child_job_id    = job_table[job_id]['start_child_job_id']
            end_child_job_id      = job_table[job_id]['end_child_job_id']
            new_wait_range        = range(start_child_job_id, end_child_job_id)
            shared_job_wait_list += list( new_wait_range )
        #
        # lock
        # lock is acquired at end of this loop
# ----------------------------------------------------------------------------
def run_parallel(
# BEGIN syntax
# at_cascade.run_parallel(
    job_table         = None,
    start_job_id      = None,
    all_node_database = None,
    node_table        = None,
    fit_integrand     = None,
    trace_fit         = None,
    skip_start_job    = None,
    max_number_cpu    = None,
# )
# END syntax
) :
    global shared_number_cpu_inuse
    global shared_job_wait_list
    global shared_job_run_list
    #
    assert job_table         is not None
    assert start_job_id      is not None
    assert all_node_database is not None
    assert node_table        is not None
    assert fit_integrand     is not None
    assert trace_fit         is not None
    assert skip_start_job    is not None
    assert max_number_cpu    is not None
    #
    # shared_number_cpu_inuse
    shared_number_cpu_inuse = 1
    #
    # shared_job_wait_list
    shared_job_wait_list = list()
    #
    # shared_job_run_list
    if skip_start_job :
        shared_job_run_list = list()
    else :
        shared_job_run_list = [ start_job_id ]
    #
    # master_process
    master_process = True
    #
    # lock
    lock = multiprocessing.Lock()
    #
    # event
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
        trace_fit,
        skip_start_job,
        max_number_cpu,
        master_process,
        lock,
        event,
    )
