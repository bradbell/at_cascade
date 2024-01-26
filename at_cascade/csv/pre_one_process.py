# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-23 Bradley M. Bell
# ----------------------------------------------------------------------------
r'''
{xrst_begin csv.pre_one_process}

Predict Using One Process
#########################
Keep predicting for as long as thee are jobs left to predict for.

Prototype
*********
{xrst_literal
   # BEGIN DEF
   # END DEF
}

{xrst_end csv.pre_one_process}
'''
# ----------------------------------------------------------------------------
import queue
import os
import datetime
import shutil
import dismod_at
import at_cascade
# ----------------------------------------------------------------------------
# prints the durrent time and job name
def print_time(begin, job_name, n_done = None, n_job_queue = None) :
   assert type(begin) == bool
   assert type(job_name) == str
   assert n_done == None or type(n_done) == int
   assert n_job_queue == None or type(n_job_queue) == int
   #
   now         = datetime.datetime.now()
   str_time    = now.strftime("%H:%M:%S")
   if begin :
      msg = f'Begin: {str_time}: predict {job_name}'
   else :
      msg = f'End:   {str_time}: predict {job_name}'
   if type(n_done) == int :
      msg += f' {n_done}/{n_job_queue}'
   print(msg)
# ----------------------------------------------------------------------------
# BEGIN DEF
def pre_one_process(
   fit_dir,
   sim_dir,
   all_node_database,
   all_covariate_table,
   #
   job_table,
   node_table,
   root_node_id,
   split_reference_table,
   error_message_dict,
   option_predict,
   #
   job_queue,
   n_job_queue,
   n_done_queue,
) :
   #
   # float_precision
   float_precision = option_predict['float_precision']
   #
   # root_split_reference_id
   root_split_reference_id = 1
   assert 'both' == split_reference_table[1]['split_reference_name']
   #
   # END DEF
   try :
      while True :
         #
         # predict_job_id
         predict_job_id = job_queue.get(block = False)
         #
         # predict_job_name, predict_node_id, predict_sex_id
         predict_job_row         = job_table[predict_job_id]
         predict_job_name        = predict_job_row['job_name']
         predict_node_id         = predict_job_row['fit_node_id']
         predict_sex_id          = predict_job_row['split_reference_id']
         #
         # print Begin message
         n_done = n_done_queue.get(block = True)
         print_time(begin = True, job_name = predict_job_name)
         n_done_queue.put(n_done)
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
         #
         # n_done, print End messsage
         n_done = n_done_queue.get(block = True) + 1
         print_time(
            begin       = False,
            job_name    = predict_job_name,
            n_done      = n_done,
            n_job_queue = n_job_queue
         )
         n_done_queue.put(n_done)
         #
   except queue.Empty :
      pass
