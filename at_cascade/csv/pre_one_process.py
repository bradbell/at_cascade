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
import at_cascade
# ----------------------------------------------------------------------------
# prints the durrent time and job name
def print_time(begin, job_name, n_done = None, n_job_queue = None) :
   assert type(begin) == bool
   assert type(job_name) == str
   assert n_done == None or type(n_done) == int
   assert n_job_queue == None or type(n_job_queue) == int
   #
   import datetime
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
   float_precision,
   all_node_database,
   all_covariate_table,
   job_queue,
   n_job_queue,
   n_done_queue,
) :
   # END DEF
   try :
      while True :
         args = job_queue.get(block = False)
         #
         # predict_job_name
         predict_job_name = args[0]
         #
         # print Begin message
         n_done = n_done_queue.get(block = True)
         print_time(begin = True, job_name = predict_job_name)
         n_done_queue.put(n_done)
         #
         # pre_one_job
         at_cascade.csv.pre_one_job(
            fit_dir                 = fit_dir             ,
            sim_dir                 = sim_dir             ,
            float_precision         = float_precision     ,
            all_node_database       = all_node_database   ,
            all_covariate_table     = all_covariate_table ,
            predict_job_name        = args[0]             ,
            ancestor_node_database  = args[1]             ,
            predict_node_id         = args[2]             ,
            predict_sex_id          = args[3]             ,
            db2csv                  = args[4]             ,
            plot                    = args[5]             ,
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
