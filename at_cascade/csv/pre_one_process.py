# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-23 Bradley M. Bell
# ----------------------------------------------------------------------------
# Set this to False when debugging an exception during pre_one_job routine
catch_exceptions_and_continue = True
# ----------------------------------------------------------------------------
r'''
{xrst_begin csv.pre_one_process}
{xrst_spell
   numpy
   dtype
}

Predict Using One Process
#########################
Keep predicting for as long as thee are jobs left to predict for.

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

option_predict
**************
This is an in memory representation of
:ref:`csv.predict@Input Files@option_predict.csv` .

all_node_database
*****************
This is the all node database for this fit.

all_covariate_table
*******************
This is an in memory representation of
:ref:`csv.fit@Input Files@covariate.csv` .

job_table
*********
is the :ref:`create_job_table@job_table` for this cascade.

node_table
**********
is the dismod_at node table for this cascade.

root_node_id
************
is the node table id for the root node of the cascade.

error_message_dict
******************
For each :ref:`create_job_table@job_table@job_name` in the job table
that is a key in *error_message_dict*.  The corresponding value

| *error_message_dict* [ *job_name* ]


is a non-empty ``list`` of ``str`` containing the error messages for that job.
If a *job_name* is not a *key* is in *error_message_dict*,
there were no error messages for that job.

job_status_name
***************
is the name corresponding to each possible job status integer values.
If *i* is an integer job status value, *job_status_name* [ *i* ] is the
corresponding name.

.. csv-table::
   :header-rows: 1

   Name,    Meaning
   'skip',  job is not included in the predictions
   'ready', job is ready to run
   'run',   job is running
   'done',  job finished running

shared_job_status_name
**********************
This the name of the shared job status memory.
The corresponding multiprocessing shared memory is
a numpy array with ``dtype`` equal to ``int`` and
with length equal to the length of *job_table* .
The value *shared_job_status* [ *job_table_index* ] is the
integer status code for the corresponding job; see *job_status_name* above.

shared_lock
***********
This lock must be acquired during the time that
a process reads or changes *shared_job_status* .


{xrst_end csv.pre_one_process}
'''
# ----------------------------------------------------------------------------
import numpy
import os
import datetime
import shutil
import dismod_at
import at_cascade
import multiprocessing
# ----------------------------------------------------------------------------
# acquire lock
def acquire_lock(shared_lock) :
   seconds = None
   ok = shared_lock.acquire(
      block   = True,
      timeout = seconds
   )
   if not ok :
      msg = f'pre_one_process: did not obtain lock in {seconds} seconds'
      assert False, msg
# ----------------------------------------------------------------------------
# prints the durrent time and job name
def print_time(
   begin               ,
   job_name            ,
   n_done      = None  ,
   n_job_total = None  ,
   job_error   = None  ,
) :
   assert type(begin)    == bool
   assert type(job_name) == str
   if begin :
      assert n_done      == None
      assert n_job_total == None
      assert job_error   == None
   else :
      assert type(n_done)      == int
      assert type(n_job_total) == int
      assert type(job_error)   == str or job_error == None
   #
   now         = datetime.datetime.now()
   str_time    = now.strftime("%H:%M:%S")
   if begin :
      msg  = f'Begin: {str_time}: predict {job_name}'
   elif job_error == None :
      msg  = f'End:   {str_time}: predict {job_name} {n_done}/{n_job_total}'
   else :
      msg  = f'Error: {str_time}: predict {job_name} {n_done}/{n_job_total}: '
      msg += job_error
   print(msg)
# ----------------------------------------------------------------------------
# BEGIN DEF
def pre_one_process(
   fit_dir,
   sim_dir,
   option_predict,
   all_node_database,
   all_covariate_table,
   job_table,
   node_table,
   root_node_id,
   error_message_dict,
   job_status_name,
   shared_job_status_name,
   shared_lock,
) :
   assert type(fit_dir)                    == str
   assert sim_dir == None or type(sim_dir) == str
   assert type(option_predict)             == dict
   assert type(all_node_database)          == str
   assert type(all_covariate_table)        == list
   assert type( all_covariate_table[0] )   == dict
   assert type(job_table)                  == list
   assert type(node_table)                 == list
   assert type(node_table[0])              == dict
   assert type(root_node_id)               == int
   assert type(error_message_dict)         == dict
   assert type(job_status_name)            == list
   assert type( job_status_name[0] )       == str
   assert type(shared_job_status_name)     == str
   assert type(shared_lock)                == multiprocessing.synchronize.Lock
   # END DEF
   # ----------------------------------------------------------------------
   job_status_skip  = job_status_name.index( 'skip' )
   job_status_ready = job_status_name.index( 'ready' )
   job_status_run   = job_status_name.index( 'run' )
   job_status_done  = job_status_name.index( 'done' )
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
   # job_table_index
   job_table_index = numpy.array( range(len(job_table)), dtype = int)
   #
   # split_reference_table
   split_reference_table = at_cascade.csv.split_reference_table
   #
   # float_precision
   float_precision = option_predict['float_precision']
   #
   # root_split_reference_id
   root_split_reference_id = 1
   assert 'both' == split_reference_table[1]['split_reference_name']
   #
   # n_skip
   n_skip = None
   #
   while True :
      #
      # Begin Lock
      acquire_lock(shared_lock)
      #
      # n_skip, predict_job_id, shared_job_status
      #
      job_id_ready = job_table_index[shared_job_status == job_status_ready]
      job_id_skip  = job_table_index[shared_job_status == job_status_skip]
      #
      # if n_ready is zero, all jobs are done or running
      n_ready      = len(job_id_ready)
      if n_ready == 0 :
         shared_lock.release()
         shm_job_status.close()
         return
      #
      if n_skip == None :
         n_skip = len(job_id_skip)
      assert n_skip == len(job_id_skip)
      #
      predict_job_id                    = int( job_id_ready[0] )
      shared_job_status[predict_job_id] = job_status_run
      #
      # End Lock
      shared_lock.release()
      # -------------------------------------------------------------------
      #
      # predict_job_name, predict_node_id, predict_sex_id
      predict_job_row         = job_table[predict_job_id]
      predict_job_name        = predict_job_row['job_name']
      predict_node_id         = predict_job_row['fit_node_id']
      predict_sex_id          = predict_job_row['split_reference_id']
      #
      # print_time
      print_time(begin = True, job_name = predict_job_name)
      #
      # predict_job_dir, ancestor_job_dir
      predict_job_dir, ancestor_job_dir = at_cascade.csv.ancestor_fit(
         fit_dir                 = fit_dir ,
         job_table               = job_table ,
         predict_job_id          = predict_job_id ,
         node_table              = node_table ,
         root_node_id            = root_node_id ,
         split_reference_table   = split_reference_table ,
         root_split_reference_id = root_split_reference_id ,
         error_message_dict      = error_message_dict ,
      )
      #
      if ancestor_job_dir == None :
         sam_node_predict = f'{fit_dir}/{predict_job_dir}/sam_predict.csv'
         if os.path.exists( sam_node_predict ) :
            os.remove( sam_node_predict )
         msg = f'Cannot find an ancestor that fit for {predict_job_name}'
         assert False, msg
      #
      # db2csv, plot, fit_database
      if ancestor_job_dir == predict_job_dir :
         db2csv            = option_predict['db2csv']
         plot              = option_predict['plot']
         fit_database      = f'{fit_dir}/{predict_job_dir}/dismod.db'
      else :
         db2csv            = False
         plot              = False
         fit_database      = f'{fit_dir}/{ancestor_job_dir}/dismod.db'
      #
      # ancestor_database
      # Must copy ancestor database because predictions will change it
      ancestor_database = f'{fit_dir}/{predict_job_dir}/ancestor.db'
      level             = predict_job_dir.count('/') + 1
      path2root_node_db = level * '../' + 'root_node.db'
      os.makedirs( f'{fit_dir}/{predict_job_dir}', exist_ok = True )
      shutil.copyfile(fit_database, ancestor_database)
      command = [
         'dismod_at', ancestor_database,
         'set', 'option', 'other_database', path2root_node_db
      ]
      dismod_at.system_command_prc(command, print_command = False)
      #
      # pre_one_job
      if not catch_exceptions_and_continue :
         predict_job_error = None
         at_cascade.csv.pre_one_job(
            fit_dir                 = fit_dir                   ,
            sim_dir                 = sim_dir                   ,
            float_precision         = float_precision           ,
            all_node_database       = all_node_database         ,
            all_covariate_table     = all_covariate_table       ,
            predict_job_name        = predict_job_name          ,
            ancestor_node_database  = ancestor_database         ,
            predict_node_id         = predict_node_id           ,
            predict_sex_id          = predict_sex_id            ,
            db2csv                  = db2csv                    ,
            plot                    = plot                      ,
         )
      else :
         try :
            at_cascade.csv.pre_one_job(
               fit_dir                 = fit_dir                   ,
               sim_dir                 = sim_dir                   ,
               float_precision         = float_precision           ,
               all_node_database       = all_node_database         ,
               all_covariate_table     = all_covariate_table       ,
               predict_job_name        = predict_job_name          ,
               ancestor_node_database  = ancestor_database         ,
               predict_node_id         = predict_node_id           ,
               predict_sex_id          = predict_sex_id            ,
               db2csv                  = db2csv                    ,
               plot                    = plot                      ,
            )
            # job_error
            predict_job_error = None
         except Exception as e :
            predict_job_error = str(e)
      #
      # Begin Lock
      acquire_lock(shared_lock)
      #
      # shared_job_status, n_done
      assert shared_job_status[predict_job_id] == job_status_run
      shared_job_status[predict_job_id] = job_status_done
      job_id_done = job_table_index[ shared_job_status == job_status_done]
      n_done      = len(job_id_done)
      n_total     = len(job_table) - n_skip
      #
      # print_time
      print_time(
         begin       = False,
         job_name    = predict_job_name,
         n_done      = n_done,
         n_job_total = n_total,
         job_error   = predict_job_error,
      )
      #
      # End Lock
      shared_lock.release()
      # -------------------------------------------------------------------
