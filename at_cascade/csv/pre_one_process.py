# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ----------------------------------------------------------------------------
# Set this to False when debugging an exception during pre_one_job routine
catch_exceptions_and_continue = True
# ----------------------------------------------------------------------------
r'''
{xrst_begin csv.pre_one_process}
{xrst_spell
  dtype
  numpy
}

Predict Using One Process
#########################
Keep predicting for as long as thee are jobs left to predict for.

Prototype
*********
{xrst_literal
   # BEGIN_DEF
   # END_DEF
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

root_split_reference_id
***********************
is the split_reference table id for the root job of the cascade

at_cascade_log_dict
*******************
For each :ref:`create_job_table@job_table@job_name` in the job table
that is a key in *at_cascade_log_dict*.  The corresponding value

| *at_cascade_log_dict* [ *job_name* ]


is a non-empty ``list`` of ``str`` containing ``at_cascade`` messages
in the log table for that job.
If a *job_name* is not a *key* is in *at_cascade_log_dict*,
there were no at_cascade messages for that job.

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

Csv Output Files
****************
see :ref:`csv.pre_one_job@Csv Output Files`

Parallel Processing
*******************
Always copy ``dismod_at.db`` to another file before predicting with it
because ``dismod_at.db`` may be an ancestor for another prediction or fit
that is running in parallel.

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
# acquire_lock
def acquire_lock(shared_lock) :
   assert type(shared_lock) == multiprocessing.synchronize.Lock
   seconds = 10
   ok = shared_lock.acquire(
      block   = True,
      timeout = seconds
   )
   if not ok :
      msg = f'pre_one_process: did not obtain lock in {seconds} seconds'
      assert False, msg
# ----------------------------------------------------------------------------
# print_begin
def print_begin(job_name) :
   assert type(job_name) == str
   now         = datetime.datetime.now()
   str_time    = now.strftime("%H:%M:%S")
   msg  = f'Begin: {str_time}: predict {job_name}'
   print(msg)
# ----------------------------------------------------------------------------
# print_end
def print_end(
   job_name            ,
   n_done      = None  ,
   n_job_total = None  ,
   job_error   = None  ,
) :
   assert type(job_name) == str
   assert type(n_done)      == int
   assert type(n_job_total) == int
   assert type(job_error)   == str or job_error == None
   #
   now         = datetime.datetime.now()
   str_time    = now.strftime("%H:%M:%S")
   if job_error == None :
      msg  = f'End:   {str_time}: predict {job_name} {n_done}/{n_job_total}'
   else :
      msg  = f'Error: {str_time}: predict {job_name} {n_done}/{n_job_total}: '
      msg += job_error
   print(msg)
# ----------------------------------------------------------------------------
def try_one_job(
   predict_job_name        ,
   fit_dir                 ,
   sim_dir                 ,
   pre_database            ,
   predict_node_id         ,
   predict_sex_id          ,
   all_node_database       ,
   all_covariate_table     ,
   float_precision         ,
   fit_same_as_predict     ,
   db2csv                  ,
   plot                    ,
   zero_meas_value         ,
   number_sample_predict   ,
) :
   assert type(predict_job_name) == str
   assert type(fit_dir) == str
   assert sim_dir == None or type(sim_dir) == str
   assert type(pre_database) == str
   assert type(predict_node_id) == int
   assert type(all_node_database) == str
   assert type(all_covariate_table) == list
   assert type( all_covariate_table[0] ) == dict
   assert type( float_precision ) == int
   assert type( fit_same_as_predict ) == bool
   assert type( db2csv ) == bool
   assert type( plot ) == bool
   assert type( zero_meas_value) == bool
   assert type( number_sample_predict ) == int
   #
   # predict_job_error
   predict_job_error = None
   #
   if not catch_exceptions_and_continue :
      at_cascade.csv.pre_one_job(
         predict_job_name        = predict_job_name          ,
         fit_dir                 = fit_dir                   ,
         sim_dir                 = sim_dir                   ,
         pre_database            = pre_database              ,
         predict_node_id         = predict_node_id           ,
         predict_sex_id          = predict_sex_id            ,
         all_node_database       = all_node_database         ,
         all_covariate_table     = all_covariate_table       ,
         float_precision         = float_precision           ,
         fit_same_as_predict     = fit_same_as_predict       ,
         db2csv                  = db2csv                    ,
         plot                    = plot                      ,
         zero_meas_value         = zero_meas_value           ,
         number_sample_predict   = number_sample_predict     ,
      )
   else :
      try :
         at_cascade.csv.pre_one_job(
            predict_job_name        = predict_job_name          ,
            fit_dir                 = fit_dir                   ,
            sim_dir                 = sim_dir                   ,
            pre_database            = pre_database              ,
            predict_node_id         = predict_node_id           ,
            predict_sex_id          = predict_sex_id            ,
            all_node_database       = all_node_database         ,
            all_covariate_table     = all_covariate_table       ,
            float_precision         = float_precision           ,
            fit_same_as_predict     = fit_same_as_predict       ,
            db2csv                  = db2csv                    ,
            plot                    = plot                      ,
            zero_meas_value         = zero_meas_value           ,
            number_sample_predict   = number_sample_predict     ,
         )
         #
         # predict_job_error
         predict_job_error = None
      except Exception as e :
         predict_job_error = str(e)
   #
   assert predict_job_error == None or type(predict_job_error) == str
   return predict_job_error
# ----------------------------------------------------------------------------
# BEGIN_DEF
# at_cascade.csv.pre_one_process
def pre_one_process(
  fit_dir,
   sim_dir,
   option_predict,
   all_node_database,
   all_covariate_table,
   job_table,
   node_table,
   root_node_id,
   root_split_reference_id,
   at_cascade_log_dict,
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
   assert type(root_split_reference_id)    == int
   assert type(at_cascade_log_dict)        == dict
   assert type(job_status_name)            == list
   assert type( job_status_name[0] )       == str
   assert type(shared_job_status_name)     == str
   assert type(shared_lock)                == multiprocessing.synchronize.Lock
   # END_DEF
   # ----------------------------------------------------------------------
   job_status_skip  = job_status_name.index( 'skip' )
   job_status_ready = job_status_name.index( 'ready' )
   job_status_run   = job_status_name.index( 'run' )
   job_status_done  = job_status_name.index( 'done' )
   # ----------------------------------------------------------------------
   #
   # shm_job_status, shared_job_status
   tmp    = numpy.empty(len(job_table), dtype = int )
   mapped = at_cascade.map_shared( shared_job_status_name )
   shm_job_status = multiprocessing.shared_memory.SharedMemory(
      create = False, size = tmp.nbytes, name = mapped
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
      # print_begin
      print_begin(job_name = predict_job_name)
      #
      # number_sample_predict, zero_meas_value, db2csv, plot
      number_sample_predict = option_predict['number_sample_predict']
      zero_meas_value       = option_predict['zero_meas_value']
      db2csv                = option_predict['db2csv']
      plot                  = option_predict['plot']
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
         at_cascade_log_dict     = at_cascade_log_dict ,
         allow_same_job          = True ,
      )
      if ancestor_job_dir == None :
         if predict_job_id == 0 :
            msg = f'Cannot find a fit for the root job {predict_job_name}'
         else :
            msg = f'Cannot find a fit for {predict_job_name}'
            msg += ' or any of its ancestors'
            assert False, msg
      #
      # predict_directory
      predict_directory = f'{fit_dir}/{predict_job_dir}'
      os.makedirs( f'{predict_directory}', exist_ok = True )
      for prefix in [ 'fit', 'sam', 'tru' ] :
         for suffix in [ 'prior', 'posterior' ] :
            output_file = f'{predict_directory}/{prefix}_{suffix}.csv'
            if os.path.exists( output_file ) :
               os.remove( output_file )
      #
      # predict_job_error
      predict_job_error = None
      if ancestor_job_dir == predict_job_dir :
         #
         # fit_same_as_predict, pre_database
         fit_same_as_predict = True
         fit_database        = f'{predict_directory}/dismod.db'
         pre_database        = f'{predict_directory}/this.db'
         shutil.copyfile(fit_database, pre_database)
         #
         # try_one_job, predict_job_error
         predict_job_error   = try_one_job(
            predict_job_name        = predict_job_name          ,
            fit_dir                 = fit_dir                   ,
            sim_dir                 = sim_dir                   ,
            pre_database            = pre_database              ,
            predict_node_id         = predict_node_id           ,
            predict_sex_id          = predict_sex_id            ,
            all_node_database       = all_node_database         ,
            all_covariate_table     = all_covariate_table       ,
            float_precision         = float_precision           ,
            fit_same_as_predict     = fit_same_as_predict       ,
            db2csv                  = db2csv                    ,
            plot                    = plot                      ,
            zero_meas_value         = zero_meas_value           ,
            number_sample_predict   = number_sample_predict     ,
         )
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
            at_cascade_log_dict     = at_cascade_log_dict ,
            allow_same_job          = False ,
         )
         assert predict_job_dir != ancestor_job_dir
      #
      if ancestor_job_dir == None :
         assert predict_job_id == 0
      else :
         assert predict_job_dir != ancestor_job_dir
         #
         # fit_same_as_predict, pre_database
         fit_same_as_predict = False
         fit_database   = f'{fit_dir}/{ancestor_job_dir}/dismod.db'
         pre_database   = f'{predict_directory}/ancestor.db'
         shutil.copyfile(fit_database, pre_database)
         #
         # pre_database
         level             = predict_job_dir.count('/') + 1
         path2root_node_db = level * '../' + 'root.db'
         command = [
            'dismod_at', pre_database,
            'set', 'option', 'other_database', path2root_node_db
         ]
         dismod_at.system_command_prc(command, print_command = False)
         #
         # try_one_job, prior_job_error
         prior_job_error = try_one_job(
            predict_job_name        = predict_job_name          ,
            fit_dir                 = fit_dir                   ,
            sim_dir                 = sim_dir                   ,
            pre_database            = pre_database              ,
            predict_node_id         = predict_node_id           ,
            predict_sex_id          = predict_sex_id            ,
            all_node_database       = all_node_database         ,
            all_covariate_table     = all_covariate_table       ,
            float_precision         = float_precision           ,
            fit_same_as_predict     = fit_same_as_predict       ,
            db2csv                  = db2csv                    ,
            plot                    = plot                      ,
            zero_meas_value         = zero_meas_value           ,
            number_sample_predict   = number_sample_predict     ,
         )
         if predict_job_error == None :
            predict_job_error = prior_job_error
         elif prior_job_error != None :
            predict_job_error = f'{prior_job_error}: {predict_job_error}'
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
      # print_end
      print_end(
         job_name    = predict_job_name,
         n_done      = n_done,
         n_job_total = n_total,
         job_error   = predict_job_error,
      )
      #
      # End Lock
      shared_lock.release()
      # -------------------------------------------------------------------
