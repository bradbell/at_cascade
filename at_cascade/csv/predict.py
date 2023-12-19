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

{xrst_begin csv.predict}
{xrst_spell
   avg
   avgint
   boolean
   cpus
   multiprocessing
   pdf
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
:ref:`csv.predict_xam-name` .

fit_dir
*******
Same as the csv fit :ref:`csv.fit@fit_dir` .

sim_dir
*******
This is either None, the file
:ref:`csv.predict@Output Files@tru_predict.csv` is not created.
Otherwise, :ref:`csv.simulate@sim_dir` is the directory
used to simulate the data for this fit and the file
tru_predict.csv is created.

start_job_name
**************
Is the name of the job (fit) that the predictions should start at.
This is a node name, followed by a period, followed by a sex.
Only this fit, and its descendents, will be included in the predictions.
If this argument is None, all of the jobs (fits) will be included.

max_job_depth
*************
This is the number of generations below start_job_name that are included;
see :ref:`job_descendent@Node Depth Versus Job Depth`
and note that sex is the :ref:`option_all_table@split_covariate_name` .
If max_job_depth is zero,  only the start job will be included.
If max_job_depth is None,  start job and all its descendants are included;

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
:ref:`csv.predict@Output Files@option_predict_out.csv` .
Because each option has a default value,
new option are added in such a way that
previous option_predict.csv files are still valid.

db2csv
------
If this boolean option is true,
the dismod_at `db2csv_command`_ is used to generate the csv files
corresponding to each :ref:`csv.fit@Output Files@dismod.db` .
If this option is true, the csv files will make it more difficult
to see the tree structure corresponding to the ``dismod.db`` files.
The default value for this option is false .

.. _db2csv_command: https://dismod-at.readthedocs.io/db2csv_command.html

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
:ref:`csv.fit@Output Files@dismod.db` database.
The data plot includes a maximum of 1,000 randomly chosen points for each
integrand in the predict_integrand.csv file.
The rate plot includes all the non-zero rates.
The default value for this option is false .

float_precision
---------------
This integer is the number of decimal digits of precision to
include for float values in the output csv files.
The default value for this option is 5.

These are no effect rates; i.e., they are the estimated rate
for this node an sex without any covariate effects
If you want to include covariate effects, you will have to make your
own plots using the
:ref:`csv.predict@Output Files@fit_predict.csv` and
:ref:`csv.predict@Output Files@sam_predict.csv` files.
The dismod_at `plot_curve`_ routine may be helpful in this regard.

.. _plot_curve: https://dismod-at.readthedocs.io/plot_curve.html

covariate.csv
=============
Same as the csv fit
:ref:`csv.fit@Input Files@covariate.csv` .

fit_goal.csv
============
Same as the csv fit
:ref:`csv.fit@Input Files@fit_goal.csv` .

predict_integrand.csv
=====================
This is the list of integrands at which predictions are made
and stored in :ref:`csv.predict@Output Files@fit_predict.csv` .

integrand_name
--------------
This string is the name of one of the prediction integrands.
You can use the integrand name ``mulcov_0`` , ``mulcov_1`` , ...
which corresponds to the first , second , ...
covariate multiplier in the csv fit
:ref:`csv.fit@Input Files@mulcov.csv` file.


{xrst_comment ---------------------------------------------------------------}


Output Files
************

option_predict_out.csv
======================
This is a copy of
:ref:`csv.predict@Input Files@option_predict.csv` with the default
filled in for missing values.

fit_predict.csv
===============
If :ref:`csv.predict@start_job_name` is None,
this file contains the predictions for all the fits.
These predictions for all of the nodes at the age, time and
covariate values specified in covariate.csv.
The prediction is done using the optimal variable values.

start_job_name
--------------
If *start_job_name* is not None,
the predictions are only for jobs at or below the starting job.
In addition, the predictions are stored below *fit_dir* in the file

   ``predict/fit_``\ *start_job_name*\ ``.csv``

and not in ``fit_predict.csv`` .

avgint_id
---------
Each avgint_id corresponds to a different value for age, time,
or integrand in the fit_predict file.
The age and time values comes from the covariate.csv file.
The integrands values come from the predict_integrand.csv file.

sample_index
------------
Each sample_index corresponds to an independent random sample
of the model variables.

#. If :ref:`option_all_table@sample_method` is asymptotic,
   model variables for each sample are Gaussian correlated with mean equal to
   the optimal value and variance equal to the asymptotic approximation.
#. If :ref:`option_all_table@sample_method` is simulate,
   the model variables for each sample at the optimal values corresponding
   to an independent data set.

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

tru_predict.csv
===============
If :ref:`csv.predict@sim_dir` is None, this file is not created.
Otherwise, this file contains the predictions for the model variables
corresponding to the simulation.

#. The first line (header line) is the same in this file and
   fit_predict.csv.
#. If the other lines, in both files, are sorted by
   ( *node_name* , *avgint_id* ) ,
   the other lines are the same except for the value in the
   avg_integrand column.

sam_predict.csv
===============
This is a sampling of the predictions,
using the posterior distribution of the model variables:

#. The first line (header line) is the same in this file and
   fit_predict.csv except that sam_predict.csv has an extra column
   named sample_index.
#. Suppose that the other lines in sam_predict.csv and fit_predict.csv
   are sorted by ( *node_name* , *avgint_id* ) .
#. Let *n_sample* be the number of other lines in sam_predict.csv divided by
   the number of other lines in fit_predict.csv.
#. For each line in fit_predict.csv (not counting the header line),
   there are *n_sample* lines in sam_predict.csv,
   that are the same as the line in fit_predict.csv except for the value in the
   avg_integrand column and the extra sample_index column in
   sam_predict.csv.

start_job_name
--------------
If *start_job_name* is not None,
the predictions are only for jobs at or below the starting job.
In addition, the predictions are stored below *fit_dir* in the file

   ``predict/sam_``\ *start_job_name*\ ``.csv``

and not in ``sam_predict.csv`` .

sample_index
------------
For each sample_index value, there is a complete set of all the values
in the fit_predict.csv table.
A different (independent) sample from of the model variables
from their posterior distribution is used to do the predictions for
each sample index.

{xrst_end csv.predict}
'''
#
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
      'float_precision'       : (int,   5)                  ,
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
         msg  = f'csv.predict: Error: line {line_number}'
         msg += ' in option_predict.csv\n'
         msg += f'the name {name} appears twice in this table'
         assert False, msg
      if not name in option_default :
         msg  = f'csv.predict: Error: line {line_number}'
         msg += ' in option_predict.csv\n'
         msg += f'{name} is not a valid option name'
         assert False, msg
      (option_type, defualt) = option_default[name]
      value                  = row['value']
      if value == '' :
         option_value[name] = None
      elif option_type == bool :
         if value not in [ 'true', 'false' ] :
            msg  = f'csv.predict: Error: line {line_number}'
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
# Calculate the predictions for All the Fits
#
# fit_dir
# *******
# This string is the directory name where the input and output csv files
# are located.
#
# sim_dir
# *******
# is the directory name where the csv simulation files are located.
#
# covariate_table
# This list of dict is an in memory representation of covariate.csv.
#
# fit_goal_set
# This set contains the node that we are required to fit.
# Ancestors between these nodes and the root node are also fit.
#
# start_job_name
# Is the name of the job (fit) that the predictions should start at.
# This is a node name, followed by a period, followed by a sex.
# Only this fit, and its descendents, will be included in the predictions.
# If this argument is None, all of the jobs (fits) will be included.
#
# max_job_depth
# This is the number of generations below start_job_name are.
# If max_job_depth is zero,  only the start job will be included.
# If max_job_depth is None,  start job and all its descendants are included.
#
# global_option_value
# This routine assues that global_option_value has been set.
#
def predict_all(
   fit_dir, sim_dir,
   covariate_table, fit_goal_set, start_job_name, max_job_depth
) :
   assert type(fit_dir)                    == str
   assert sim_dir == None or type(sim_dir) == str
   assert type(covariate_table)            == list
   assert type( covariate_table[0] )       == dict
   assert type(fit_goal_set)               == set
   #
   # max_number_cpu
   max_number_cpu = global_option_value['max_number_cpu']
   #
   # all_node_db
   all_node_db = f'{fit_dir}/all_node.db'
   #
   # root_node_database
   root_node_database = f'{fit_dir}/root_node.db'
   #
   # root_node_name
   root_node_name = at_cascade.get_parent_node(root_node_database)
   #
   # node_table
   connection      = dismod_at.create_connection(
      root_node_database, new = False, readonly = True
   )
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
   connection      = dismod_at.create_connection(
      all_node_db, new = False, readonly = True
   )
   split_reference_table = \
      dismod_at.get_table_dict(connection, 'split_reference')
   connection.close()
   assert split_reference_table == at_cascade.csv.split_reference_table
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
   # start_job_id
   if start_job_name == None :
      start_job_id = 0
   else :
      start_job_id = None
   for (job_id, row) in enumerate(job_table) :
      if row['job_name'] == start_job_name :
         start_job_id = job_id
   if start_job_id == None :
      root_job_name = job_table[0]['job_name']
      msg  = f'start_job_name = {start_job_name} is not a valid job name '
      msg += 'for this cascade.\n'
      msg += f'The root job name for this cascade is {root_job_name}.'
      assert False, msg
   #
   # error_message_dict
   error_message_dict = at_cascade.check_log(
      message_type = 'error',
      all_node_database  = all_node_db          ,
      root_node_database = root_node_database   ,
      fit_goal_set       = fit_goal_set         ,
      start_job_id       = start_job_id         ,
      max_job_depth      = max_job_depth        ,
   )
   #
   # n_job
   n_job = len( job_table )
   assert job_table[0]['parent_job_id'] == None
   #
   # process_list
   process_list = list()
   #
   # manager
   manager = multiprocessing.Manager()
   #
   # job_queue, n_job_queue
   # Need Manager; see https://bugs.python.org/issue18277
   job_queue   = manager.Queue()
   n_job_queue = 0
   #
   # job_id, job_row, fit_node_database_list
   fit_node_database_list = list()
   for job_id in range(-1, n_job) :
      #
      # include_this_job, job_row
      if job_id == -1 :
         job_tmp = 0
      else :
         job_tmp = job_id
      job_depth = at_cascade.job_descendent(job_table, start_job_id, job_tmp)
      include_this_job = False
      if job_depth != None :
         if max_job_depth == None :
            include_this_job = True
         else :
            include_this_job = job_depth <= max_job_depth
      if include_this_job :
         job_row = job_table[job_tmp]
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
            if sim_dir != None :
               job_description  += ', tru_predict.csv'
            if global_option_value['db2csv'] :
               job_description  += ',  db2csv files'
            if global_option_value['plot'] :
               job_description  += ',  plots'
            job_description  += f', for {fit_title}'
            #
            # ????
            # Matplotlib leaks memrory, so use a separate proccess
            # for this call to predict_csv_one_job so the memory will be
            # freed when it is no longer needed
            # ????
            #
            # job_queue
            # skip predict for no_ode fit (job_id == -1 and not in job_table)
            if 0 <= job_id :
               args = (
                  fit_title         ,
                  fit_dir           ,
                  sim_dir           ,
                  fit_node_database ,
                  fit_node_id       ,
                  all_node_db       ,
                  covariate_table   ,
                  global_option_value['float_precision'] ,
                  global_option_value['db2csv']          ,
                  global_option_value['plot']            ,
               )
               if max_number_cpu == 1 :
                  at_cascade.csv.predict_one(*args)
                  print(job_description)
               else :
                  job_queue.put( (job_description, args) )
                  n_job_queue += 1
               #
               # fit_node_database_list
               fit_node_database_list.append( fit_node_database )
   #
   # max_number_cpu > 1
   if max_number_cpu > 1 :
      #
      # n_done_queue
      # The number of job_queue entries that have been completed
      n_done_queue   = manager.Queue()
      n_done_queue.put(0)
      #
      # process_target
      def process_target(job_queue, n_done_queue) :
         try :
            while True :
               (job_description, args)  = job_queue.get(block = False)
               # predict_one
               fit_title = args[0]
               at_cascade.csv.predict_one(
                  fit_title             = args[0]           ,
                  fit_dir               = args[1]           ,
                  sim_dir               = args[2]           ,
                  fit_node_database     = args[3]           ,
                  fit_node_id           = args[4]           ,
                  all_node_database     = args[5]           ,
                  all_covariate_table   = args[6]           ,
                  float_precision       = args[7]           ,
                  db2csv                = args[8]           ,
                  plot                  = args[9]           ,
               )
               n_done = n_done_queue.get(block = True) + 1
               print( f'Done: {n_done}/{n_job_queue}: {fit_title}' )
               n_done_queue.put(n_done)
         except queue.Empty :
            pass
      #
      # process_list
      # execute process_target for each process in process_list
      n_spawn      = min(n_job_queue - 1, max_number_cpu - 1)
      print( f'Predict: n_job = {n_job_queue}, n_spawn = {n_spawn}' )
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
   # prefix_predict_table
   prefix_predict_table = { 'tru':list(), 'fit':list(), 'sam':list() }
   #
   # prefix_list
   if sim_dir == None :
      prefix_list = [ 'fit', 'sam' ]
   else :
      prefix_list = [ 'tru', 'fit', 'sam' ]
   #
   # fit_node_database
   for fit_node_database in fit_node_database_list :
      #
      # fit_node_dir
      index = fit_node_database.rindex('/')
      fit_node_dir  = fit_node_database[: index]
      #
      # fit_covariate_table, integrand_table
      fit_or_root   = at_cascade.fit_or_root_class(
         fit_node_database, root_node_database
      )
      fit_covariate_table = fit_or_root.get_table('covariate')
      integrand_table     = fit_or_root.get_table('integrand')
      fit_or_root.close()
      #
      # prefix
      for prefix in prefix_list :
         #
         # predict_table
         file_name     = f'{fit_node_dir}/{prefix}_predict.csv'
         assert os.path.isfile(file_name)
         predict_table =  at_cascade.csv.read_table(file_name)
         #
         # prefix_predict_table
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
            # prefix_predict_table
            prefix_predict_table[prefix].append( row_out )
   #
   # fit_dir/predict
   if start_job_name != None :
      os.makedirs( f'{fit_dir}/predict', exist_ok = True )
   #
   # prefix_predict.csv
   for prefix in prefix_list :
      if start_job_name == None :
         file_name    = f'{fit_dir}/{prefix}_predict.csv'
      else :
         file_name    = f'{fit_dir}/predict/{prefix}_{start_job_name}.csv'
      at_cascade.csv.write_table(file_name, prefix_predict_table[prefix] )
# ----------------------------------------------------------------------------
# BEGIN_PREDICT
# at_cascade.csv.predict
def predict(fit_dir, sim_dir=None, start_job_name=None, max_job_depth=None) :
   assert type(fit_dir)  == str
   assert sim_dir        == None or type(sim_dir) == str
   assert start_job_name == None or type(start_job_name) == str
   assert max_job_depth  == None or type(max_job_depth) == int
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
   predict_all(fit_dir, sim_dir,
      covariate_table, fit_goal_set, start_job_name, max_job_depth
   )
