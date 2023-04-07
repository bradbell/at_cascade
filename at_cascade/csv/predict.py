# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-23 Bradley M. Bell
# ----------------------------------------------------------------------------
import multiprocessing
import queue
import dismod_at
import at_cascade
import copy
import os
import time
'''

{xrst_begin csv_predict}
{xrst_spell
   dir
   boolean
   pdf
   avgint
   avg
   cpus
   multiprocessing
}

Prediction for a CSV Fit
########################

Prototype
*********
{xrst_literal
   # BEGIN_PREDICT
   # END_PREDICT
}

Example
*******
:ref:`csv_fit_xam-name` .

fit_dir
*******
This string is the directory name where the csv files
are located.

Input Files
***********

option_predict.csv
==================
This csv file has two columns,
one called ``name`` and the other called ``value``.
The rows of this table are documented below by the name column.
If an option name does not appear, the corresponding
default value is used for the option.
The final value for each of the options is reported in the file
:ref:`csv_predict@Output Files@option_predict_out.csv` .
Because each option has a default value,
new option are added in such a way that
previous option_predict.csv files are still valid.

db2csv
------
If this boolean option is true,
the dismod_at `db2csv_command`_ is used to generate the csv files
corresponding to each :ref:`csv_fit@Output Files@dismod.db` .
If this option is true, the csv files will make it more difficult
to see the tree structure corresponding to the ``dismod.db`` files.
The default value for this option is false .

.. _db2csv_command: https://bradbell.github.io/dismod_at/doc/db2csv_command.htm

max_number_cpu
--------------
This integer is the maximum number of cpus (processes) to use
This must be greater than zero. If it is one, the jobs are run
sequentially, more output is printed to the screen, and the program
can be cleanly stopped with a control-C.
The default value for this option is
{xrst_code py}
   max_number_cpu = max(1, multiprocessing.cpu_count() - 1)
{xrst_code}

plot
----
If this boolean option is true,
a ``data_plot.pdf`` and ``rate_plot.pdf`` file is created for each
:ref:`csv_fit@Output Files@dismod.db` database.
The data plot includes a maximum of 1,000 randomly chosen points for each
integrand in the predict_integrand.csv file.
The rate plot includes all the non-zero rates.
The default value for this option is false .

These are no effect rates; i.e., they are the estimated rate
for this node an sex without any covariate effects
If you want to include covariate effects, you will have to make your
own plots using the
:ref:`csv_predict@Output Files@fit_predict.csv` and
:ref:`csv_predict@Output Files@sam_predict.csv` files.
The dismod_at `plot_curve`_ routine may be helpful in this regard.

.. _plot_curve: https://bradbell.github.io/dismod_at/doc/plot_curve.htm

covariate.csv
=============
Same as the csv fit
:ref:`csv_fit@Input Files@covariate.csv` .

fit_goal.csv
============
Same as the csv fit
:ref:`csv_fit@Input Files@fit_goal.csv` .

predict_integrand.csv
=====================
This is the list of integrands at which predictions are made
and stored in :ref:`csv_predict@Output Files@fit_predict.csv` .

integrand_name
--------------
This string is the name of one of the prediction integrands.
You can use the integrand name ``mulcov_0`` , ``mulcov_1`` , ...
which corresponds to the first , second , ...
covariate multiplier in the csv fit
:ref:`csv_fit@Input Files@mulcov.csv` file.


{xrst_comment ---------------------------------------------------------------}


Output Files
************

option_predict_out.csv
======================
This is a copy of
:ref:`csv_predict@Input Files@option_predict.csv` with the default
filled in for missing values.

fit_predict.csv
===============
This is the predictions for all of the nodes at the age, time and
covariate values specified in covariate.csv.
The prediction is done using the optimal variable values.

avgint_id
---------
Each avgint_id corresponds to a different value for age, time, or
integrand in the sam_predict file.
The age and time values comes from the covariate.csv file.
The integrands come for the predict_integrand.csv file.

integrand_name
--------------
is the integrand for this sample is equal to the integrand names
in predict_integrand.csv

avg_integrand
-------------
This float is the mode value for the average of the integrand,
with covariate and other effects but without measurement noise.

node_name
---------
is the node name for this sample and
cycles through the nodes in covariate.csv.

age
---
is the age for this prediction and is one of
the ages in covariate.csv.

time
----
is the time for this prediction and is one of
the times in covariate.csv.

sex
---
is female, both, or male.

covariate_names
---------------
The rest of the columns are covariate names and contain the value
of the corresponding covariate in covariate.csv.

sam_predict.csv
===============
This is a sampling of the predictions for all of the nodes at the age, time and
covariate values specified in covariate.csv.
It has the same columns as fit_predict.csv (see above) plus
an extra column named sample_index.

sample_index
------------
For each sample_index value, there is a complete set of all the values
in the fit_predict.csv table.
A different (independent) sample from of the model variables
from their posterior distribution is used to do the predictions for
each sample index.

{xrst_end csv_predict}
'''
#-----------------------------------------------------------------------------
# split_reference_table
split_reference_table = [
   { 'split_reference_name' : 'female' , 'split_reference_value' : -0.5 },
   { 'split_reference_name' : 'both'   , 'split_reference_value' :  0.0 },
   { 'split_reference_name' : 'male'   , 'split_reference_value' : +0.5 },
]
# ----------------------------------------------------------------------------
# Sets global global_option_value to dict representation of option_predict.csv
#
# fit_dir
# is the directory where the input csv files are located.
#
# option_table :
# is the list of dict corresponding to option_predict.csv
#
# top_node_name
# is the name of the top node in the node tree
#
# option_predict_out.csv
# As a side effect, this routine write a copy of the option table
# with the default values filled in.
#
# global_option_value[name] :
# is the option value corresponding the specified option name.
# Here name is a string and value
# has been coverted to its corresponding type.
#
global_option_value = None
def set_global_option_value(fit_dir, option_table, top_node_name) :
   global global_option_value
   assert type(global_option_value) == dict or global_option_value == None
   assert type(option_table) == list
   if len(option_table) > 0 :
      assert type( option_table[0] ) == dict
   #
   # user
   user = os.environ.get('USER')
   if user == None :
      user = 'none'
   else :
      user = user.replace(' ', '_')
   #
   # option_default
   max_number_cpu = max(1, multiprocessing.cpu_count() - 1)
   random_seed    = int( time.time() )
   # BEGIN_SORT_THIS_LINE_PLUS_2
   option_default  = {
      'db2csv'                : (bool,  False)              ,
      'max_number_cpu'        : (int,   max_number_cpu)     ,
      'plot'                  : (bool,  False)              ,
   }
   # END_SORT_THIS_LINE_MINUS_2
   #
   # global_option_value
   line_number      = 0
   global_option_value = dict()
   for row in option_table :
      line_number += 1
      name         = row['name']
      if name in global_option_value :
         msg  = f'csv_predict: Error: line {line_number}'
         msg += ' in option_predict.csv\n'
         msg += f'the name {name} appears twice in this table'
         assert False, msg
      if not name in option_default :
         msg  = f'csv_predict: Error: line {line_number}'
         msg += ' in option_predict.csv\n'
         msg += f'{name} is not a valid option name'
         assert False, msg
      (option_type, defualt) = option_default[name]
      value                  = row['value']
      if value == '' :
         option_value[name] = None
      elif option_type == bool :
         if value not in [ 'true', 'false' ] :
            msg  = f'csv_predict: Error: line {line_number}'
            msg += ' in option_predict.csv\n'
            msg += f'The value for {name} is not true or false'
            assert False, msg
         global_option_value[name] = value == 'true'
      else :
         global_option_value[name] = option_type( value )
   #
   # global_option_value
   for name in option_default :
      if name not in global_option_value :
         (option_type, default) = option_default[name]
         global_option_value[name] = default
   #
   # option_predict_out.csv
   table = list()
   for name in global_option_value :
      value = global_option_value[name]
      if type(value) == bool :
         if value :
            value = 'true'
         else :
            value = 'false'
      row = { 'name' : name , 'value' : value }
      table.append(row)
   file_name = f'{fit_dir}/option_predict_out.csv'
   at_cascade.csv.write_table(file_name, table)
   #
   assert type(global_option_value) == dict
# ----------------------------------------------------------------------------
# Calculate the predictions for One Fit
#
# fit_title
# *********
# This string specifies the node and sex correpsonding to this fit.
# In the special case of a no_ode fit, 'no_ode' should be included
# in the fit_title.
#
# fit_dir
# *******
# This string is the directory name where the input and output csv files
# are located.
#
# fit_node_database
# This string is the location, relative to fit_dir, of the dismod_at
# databse for a fit.
#
# fit_node_id
# This int is the node_id in the fit node for this database.
#
# all_node_database
# This string is the all node database for this fit.
#
# all_covariate_table
# The list of dict is the in memory representation of the
# covariate.csv file
#
# global_option_value
# This routine assues that global_option_value has been set.
# If global_option_value['d2b2csv'] is true (false), the csvfiles
# for this fit node database are (are not) created.
#
# fit_predict.csv
# This output file is locatied in the same directory as fit_node_database.
# It contains the predictions for this fit node at the age and time
# specified by the covariate.csv file.
# The predictions are done using the optimal variable values.
#
# sam_predict.csv
# This output file is locatied in the same directory as fit_node_database.
# It contains the predictions for this fit node at the age and time
# specified by the covariate.csv file.
# The predictions are done using samples of the asymptotic distribution
# for the variable values.
#
def predict_one(
   fit_title             ,
   fit_dir               ,
   fit_node_database     ,
   fit_node_id           ,
   all_node_database     ,
   all_covariate_table   ,
) :
   assert type(fit_title) == str
   assert type(fit_dir) == str
   assert type(fit_node_database) == str
   assert type(fit_node_id) == int
   assert type(all_node_database) == str
   assert type(all_covariate_table) == list
   assert type( all_covariate_table[0] ) == dict
   #
   # all_option_table
   new               = False
   connection       = dismod_at.create_connection(all_node_database, new)
   all_option_table = dismod_at.get_table_dict(connection, 'all_option')
   connection.close()
   #
   # fit_covariate_table, integrand_table, node_table
   new                 = False
   connection          = dismod_at.create_connection(fit_node_database, new)
   fit_covariate_table = dismod_at.get_table_dict(connection, 'covariate')
   integrand_table     = dismod_at.get_table_dict(connection, 'integrand')
   node_table          = dismod_at.get_table_dict(connection, 'node')
   connection.close()
   #
   # integrand_id_list
   predict_integrand_table = at_cascade.csv.read_table(
         f'{fit_dir}/predict_integrand.csv'
   )
   integrand_id_list = list()
   for row in predict_integrand_table :
      integrand_id = at_cascade.table_name2id(
         integrand_table, 'integrand', row['integrand_name']
      )
      integrand_id_list.append( integrand_id )
   #
   # fit_node_name
   fit_node_name = node_table[fit_node_id]['node_name']
   #
   # fit_split_reference_id
   cov_info = at_cascade.get_cov_info(
      all_option_table, fit_covariate_table, split_reference_table
   )
   fit_split_reference_id  = cov_info['split_reference_id']
   #
   # sex_value
   row       = split_reference_table[fit_split_reference_id]
   sex_value = row['split_reference_value']
   sex_name  = row['split_reference_name']
   #
   # avgint_table
   avgint_table = list()
   #
   # male_index_dict
   male_index_dict = dict()
   if sex_name == 'both' :
      for (i_row, row) in enumerate(all_covariate_table) :
         if row['node_name'] == fit_node_name :
            sex  = row['sex']
            age  = float( row['age'] )
            time = float( row['time'] )
            if sex == 'male' :
               if age not in male_index_dict :
                  male_index_dict[age] = dict()
               if time not in male_index_dict[age] :
                  male_index_dict[age][time] = i_row
   #
   # cov_row
   for cov_row in all_covariate_table :
      #
      # select
      if cov_row['sex'] == sex_name :
         select = True
      elif cov_row['sex'] == 'female' and sex_name == 'both' :
         select = True
      else :
         select = False
      select = select and cov_row['node_name'] == fit_node_name
      if select :
         #
         # avgint_row
         age  = float( cov_row['age'] )
         time = float( cov_row['time'] )
         avgint_row = {
            'node_id'         : fit_node_id,
            'subgroup_id'     : 0,
            'weight_id'       : None,
            'age_lower'       : age,
            'age_upper'       : age,
            'time_lower'      : time,
            'time_upper'      : time,
         }
         #
         # covariate_id
         for covariate_id in range( len(fit_covariate_table) ) :
            #
            # covariate_name
            covariate_name = fit_covariate_table[covariate_id]['covariate_name']
            #
            # covariate_value
            if covariate_name == 'one' :
               covariate_value = 1.0
            elif covariate_name == 'sex' :
               covariate_value = sex_value
            else :
               covariate_value = float( cov_row[covariate_name] )
               if sex_name == 'both' :
                  male_row  = all_covariate_table[ male_index_dict[age][time] ]
                  assert male_row['sex'] == 'male'
                  assert cov_row['sex']  == 'female'
                  covariate_value += float( male_row[covariate_name] )
                  covariate_value /= 2.0
            #
            # avgint_row
            key = f'x_{covariate_id}'
            avgint_row[key] = covariate_value
         #
         # integrand_id
         for integrand_id in integrand_id_list :
            avgint_row['integrand_id'] = integrand_id
            avgint_table.append( copy.copy( avgint_row ) )
   #
   # connection
   new        = False
   connection = dismod_at.create_connection(fit_node_database, new)
   #
   # avgint table
   dismod_at.replace_table(connection, 'avgint', avgint_table)
   #
   # prefix_list
   prefix_list = list()
   if at_cascade.table_exists(connection, 'fit_var') :
      prefix_list.append( 'fit' )
   if at_cascade.table_exists(connection, 'sample') :
      prefix_list.append( 'sam' )
   connection.close()
   #
   # fit_node_dir
   index        = fit_node_database.rfind('/')
   fit_node_dir = fit_node_database[: index]
   #
   # prefix
   for prefix in prefix_list :
      #
      # command
      command = [ 'dismod_at', fit_node_database, 'predict' ]
      if prefix == 'fit' :
         command.append( 'fit_var' )
      else :
         command.append( 'sample' )
      dismod_at.system_command_prc(command, print_command = False )
      #
      # predict_table
      new           = False
      connection    = dismod_at.create_connection(fit_node_database, new)
      predict_table = dismod_at.get_table_dict(connection, 'predict')
      connection.close()
      for pred_row in predict_table :
         avgint_id  = pred_row['avgint_id']
         avgint_row = avgint_table[avgint_id]
         for key in avgint_row.keys() :
            pred_row[key] = avgint_row[key]
         avg_integrand             = float( pred_row['avg_integrand'] )
         pred_row['avg_integrand'] = format(avg_integrand, '.5g')
         if prefix == 'fit' :
            assert pred_row['sample_index'] == None
            del pred_row['sample_index']
      #
      # prefix_predict.csv
      file_name    = f'{fit_node_dir}/{prefix}_predict.csv'
      at_cascade.csv.write_table(file_name, predict_table)
   #
   if global_option_value['db2csv'] :
      #
      # db2csv output files
      command = [ 'dismodat.py', fit_node_database, 'db2csv' ]
      dismod_at.system_command_prc(
         command, print_command = False, return_stdout = True
      )
   #
   if global_option_value['plot'] :
      #
      # data_plot.pdf
      pdf_file       = f'{fit_node_dir}/data_plot.pdf'
      integrand_list = list()
      for row in predict_integrand_table :
         integrand_name = row['integrand_name']
         if not integrand_name.startswith('mulcov_') :
            integrand_list.append( integrand_name )
      dismod_at.plot_data_fit(
         database       = fit_node_database  ,
         pdf_file       = pdf_file           ,
         plot_title     = fit_title          ,
         max_plot       = 1000               ,
         integrand_list = integrand_list     ,
      )
      #
      # rate_plot.pdf
      pdf_file = f'{fit_node_dir}/rate_plot.pdf'
      rate_set = { 'pini', 'iota', 'chi', 'omega' }
      dismod_at.plot_rate_fit(
         database       = fit_node_database  ,
         pdf_file       = pdf_file           ,
         plot_title     = fit_title          ,
         rate_set       = rate_set           ,
      )
# ----------------------------------------------------------------------------
# Calculate the predictions for All the Fits
#
# fit_dir
# *******
# This string is the directory name where the input and output csv files
# are located.
#
# covariate_table
# This list of dict is an in memory representation of covariate.csv.
#
# fit_goal_set
# This set contains the node that we are required to fit.
# Ancestors between these nodes and the root node are also fit.
#
# global_option_value
# This routine assues that global_option_value has been set.
#
def predict_all(fit_dir, covariate_table, fit_goal_set) :
   assert type(fit_dir) == str
   assert type(covariate_table) == list
   assert type( covariate_table[0] ) == dict
   assert type(fit_goal_set) == set
   #
   # max_number_cpu
   max_number_cpu = global_option_value['max_number_cpu']
   #
   # all_node_db
   all_node_db = f'{fit_dir}/all_node.db'
   #
   # root_node_db
   root_node_db = f'{fit_dir}/root_node.db'
   #
   # root_node_name
   root_node_name = at_cascade.get_parent_node(root_node_db)
   #
   # node_table
   new             = False
   connection      = dismod_at.create_connection(root_node_db, new)
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
   new             = False
   connection      = dismod_at.create_connection(all_node_db, new)
   split_reference_table = \
      dismod_at.get_table_dict(connection, 'split_reference')
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
   # error_message_dict
   error_message_dict = at_cascade.check_log(
      message_type = 'error',
      all_node_database  = all_node_db    ,
      root_node_database = root_node_db   ,
      fit_goal_set       = fit_goal_set   ,
   )
   #
   # n_job
   n_job = len( job_table )
   #
   # process_list
   process_list = list()
   #
   # job_queue, n_job_queue
   job_queue   = multiprocessing.Queue()
   n_job_queue = 0
   #
   # job_id, job_row, fit_node_database_list
   fit_node_database_list = list()
   for job_id in range(-1, n_job) :
      #
      if job_id == -1 :
         # no_ode is for same node and sex as row zero in the job table
         job_row = job_table[0]
      else :
         job_row = job_table[job_id]
      #
      # job_name, fit_node_id, fit_split_reference_id
      job_name                = job_row['job_name']
      fit_node_id             = job_row['fit_node_id']
      fit_split_reference_id  = job_row['split_reference_id']
      #
      # fit_database_dir
      fit_database_dir = at_cascade.get_database_dir(
         node_table              = node_table               ,
         split_reference_table   = split_reference_table    ,
         node_split_set          = node_split_set           ,
         root_node_id            = root_node_id             ,
         root_split_reference_id = root_split_reference_id  ,
         fit_node_id             = fit_node_id              ,
         fit_split_reference_id  = fit_split_reference_id   ,
      )
      #
      # fit_database_dir
      if job_id == -1 :
         fit_database_dir += '/no_ode'
      #
      # fit_node_database
      fit_node_database = f'{fit_dir}/{fit_database_dir}/dismod.db'
      #
      # sam_node_predict
      sam_node_predict = f'{fit_dir}/{fit_database_dir}/sam_predict.csv'
      #
      # fit_title
      if job_id == -1 :
         fit_title = job_name + '.no_ode'
      else :
         fit_title = job_name
      #
      # job_description
      # check for an error during fit both and fit fixed
      two_errors = False
      if job_name in error_message_dict :
            two_errors = len( error_message_dict[job_name] ) > 1
      if two_errors :
         if os.path.exists( sam_node_predict ) :
            os.remove( sam_node_predict )
         print( f'Error in {job_name}' )
      elif not os.path.exists( fit_node_database ) :
         print( f'Missing dismod.db for {job_name}' )
      else :
         job_description = 'Done: fit_predict.csv, sam_predict.csv'
         if global_option_value['db2csv'] :
            job_description  += f',  db2csv files'
         if global_option_value['plot'] :
            job_description  += f',  plots'
         job_description  += f', for {fit_title}'
         #
         # ????
         # Matplotlib leaks memrory, so use a separate proccess
         # for this call to predict_csv_one_job so the memory will be
         # freed when it is no longer needed
         # ????
         #
         # job_queue
         args = (
            fit_title         ,
            fit_dir           ,
            fit_node_database ,
            fit_node_id       ,
            all_node_db       ,
            covariate_table   ,
         )
         job_queue.put( (job_description, args) )
         n_job_queue += 1
         #
         #
         # fit_node_database_list
         # skip the no_ode fit (job_id == -1 and not in job_table)
         if 0 <= job_id :
            fit_node_database_list.append( fit_node_database )
   #
   # n_done_queue
   # The number of job_queue entries that have been completed
   n_done_queue   = multiprocessing.Queue()
   n_done_queue.put(0)
   #
   # process_target
   def process_target(job_queue, n_done_queue) :
      try :
         while True :
            (job_description, args)  = job_queue.get(block = False)
            # predict_one
            predict_one(
               fit_title             = args[0]          ,
               fit_dir               = args[1]          ,
               fit_node_database     = args[2]           ,
               fit_node_id           = args[3]           ,
               all_node_database     = args[4]           ,
               all_covariate_table   = args[5]           ,
            )
            n_done = n_done_queue.get(block = True) + 1
            print( f'{n_done}/{n_job_queue} {job_description}' )
            n_done_queue.put(n_done)
      except queue.Empty :
         pass
   #
   # process_list
   # execute process_target for each process in process_list
   n_spawn      = min(n_job_queue - 1, max_number_cpu - 1)
   process_list = list()
   for i in range(n_spawn) :
      p = multiprocessing.Process(
         target = process_target, args=(job_queue, n_done_queue,)
      )
      p.start()
      process_list.append(p)
   #
   # process_target
   # use this process as well to execute proess_target
   process_target(job_queue, n_done_queue)
   #
   # join
   # wait for all the processes to finish (detect an empty queue).
   for p in process_list :
      p.join()
   #
   # sex_value2name
   sex_value2name = dict()
   for row in split_reference_table :
      name  = row['split_reference_name']
      value = row['split_reference_value']
      sex_value2name[value] = name
   #
   # sam_predict_table, fit_predict_tale
   sam_predict_table = list()
   fit_predict_table = list()
   #
   # fit_node_database
   for fit_node_database in fit_node_database_list :
      #
      # fit_node_dir
      index = fit_node_database.rindex('/')
      fit_node_dir           = fit_node_database[: index]
      #
      # fit_covariate_table
      new                 = False
      connection          = dismod_at.create_connection(fit_node_database, new)
      fit_covariate_table = dismod_at.get_table_dict(connection, 'covariate')
      integrand_table     = dismod_at.get_table_dict(connection, 'integrand')
      connection.close()
      #
      # prefix
      for prefix in [ 'fit', 'sam' ] :
         #
         # predict_table
         file_name     = f'{fit_node_dir}/{prefix}_predict.csv'
         predict_table =  at_cascade.csv.read_table(file_name)
         #
         # row_in
         for row_in in predict_table :
            #
            # row_out
            row_out = dict()
            for key in ['avgint_id', 'avg_integrand' ] :
               row_out[key] = row_in[key]
            if prefix == 'sam' :
               row_out['sample_index'] = row_in['sample_index']
            assert float(row_in['age_lower'])  == float(row_in['age_upper'])
            assert float(row_in['time_lower']) == float(row_in['time_upper'])
            row_out['age']  = row_in['age_lower']
            row_out['time'] = row_in['time_lower']
            #
            node_id              = int( row_in['node_id'] )
            row_out['node_name'] = node_table[node_id]['node_name']
            #
            integrand_id  = int( row_in['integrand_id'] )
            row_out['integrand_name'] = \
               integrand_table[integrand_id]['integrand_name']
            #
            # row_out
            for (i_cov, cov_row) in enumerate( fit_covariate_table ) :
               covariate_name = cov_row['covariate_name']
               covariate_key  = f'x_{i_cov}'
               cov_value      = float( row_in[covariate_key] )
               if covariate_name == 'sex' :
                  cov_value = sex_value2name[cov_value]
               row_out[covariate_name] = cov_value
            #
            # sam_predict_table, fit_predict_table
            if prefix == 'fit' :
               fit_predict_table.append( row_out )
            else :
               sam_predict_table.append( row_out )
   #
   # fit_predict.csv
   file_name = f'{fit_dir}/fit_predict.csv'
   at_cascade.csv.write_table(file_name, fit_predict_table )
   #
   # sam_predict.csv
   file_name = f'{fit_dir}/sam_predict.csv'
   at_cascade.csv.write_table(file_name, sam_predict_table )
# ----------------------------------------------------------------------------
# BEGIN_PREDICT
# at_cascadde.csv.fit(fit_dir)
def predict(fit_dir) :
   assert type(fit_dir) == str
# END_PREDICT
   #
   # top_node_name
   node_table      = at_cascade.csv.read_table(f'{fit_dir}/node.csv')
   top_node_name = None
   for row in node_table :
      if row['parent_name'] == '' :
         if top_node_name != None :
            msg = 'node.csv: more than one node has no parent node'
            assert False, msg
         top_node_name = row['node_name']
   if top_node_name == None :
      msg = 'node.csv: no node has an empty parent_name'
      assert False, msg
   #
   # global_option_value
   option_table = at_cascade.csv.read_table(f'{fit_dir}/option_predict.csv')
   set_global_option_value(
      fit_dir, option_table, top_node_name
   )
   #
   # fit_goal_set
   fit_goal_set   = set()
   file_name      = f'{fit_dir}/fit_goal.csv'
   fit_goal_table = at_cascade.csv.read_table(file_name)
   for row in fit_goal_table :
      fit_goal_set.add( row['node_name'] )
   #
   # covariate_table
   file_name       = f'{fit_dir}/covariate.csv'
   covariate_table = at_cascade.csv.read_table(file_name)
   #
   # predict
   predict_all(fit_dir, covariate_table, fit_goal_set)
