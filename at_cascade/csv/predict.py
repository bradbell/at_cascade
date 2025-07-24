# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-25 Bradley M. Bell
# ----------------------------------------------------------------------------
import multiprocessing
import queue
import dismod_at
import at_cascade
import copy
import os
import time
r'''
{xrst_begin csv.predict}
{xrst_spell
  avg
  avgint
  cpus
  meas
  pdf
  tru
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
:ref:`csv.sim_fit_pred-name` .

fit_dir
*******
Same as the csv fit :ref:`csv.fit@fit_dir` .

sim_dir
*******
If this is None, the file
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
If an option name does not appear, or the corresponding value is empty,
the default value is used for the option.
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

.. _db2csv_command: https://dismod-at.readthedocs.io/latest/db2csv_command.html

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

.. _plot_curve: https://dismod-at.readthedocs.io/latest/plot_curve.html

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

zero_meas_value
---------------
If this boolean option is true, the
:ref:`csv.fit@Input Files@mulcov.csv@type@meas_value` covariate
multipliers are set to zero during the predictions
(instead of their simulation values, fit, or sample values).
The default value for this option is false .

number_sample_predict
---------------------
This integer option specifies the number of samples generated for each
prediction. The default value is
:ref:`csv.fit@Input Files@option_fit.csv@number_sample` from
:ref:`csv.fit@Input Files@option_fit.csv` will be used.

covariate.csv
=============
Same as the csv fit
:ref:`csv.fit@Input Files@covariate.csv` .

fit_goal.csv
============
Same as the csv fit
:ref:`csv.fit@Input Files@fit_goal.csv` .

option_fit.csv
==============
The value option_fit.csv
:ref:`csv.fit@Input Files@option_fit.csv@refit_split` value is used.

predict_integrand.csv
=====================
This is the list of integrands at which predictions are made
and stored in :ref:`csv.predict@Output Files@fit_predict.csv` .


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
#. If :ref:`csv.predict@start_job_name` is None,
   ``fit_predict.csv`` contains the predictions for all the fits.
   These predictions for all of the nodes at the age, time and
   covariate values specified in covariate.csv.
   The prediction is done using the optimal variable values.

#. If :ref:`csv.predict@start_job_name` is not None,
   the predictions are only for jobs at or below the starting job.
   In addition, the predictions are stored below *fit_dir* in the file

      ``predict/fit_``\ *start_job_name*\ ``.csv``

   and not in ``fit_predict.csv`` .


avgint_id
---------
Each avgint_id corresponds to a different value for age, time,
or integrand in the fit_predict file.
The age and time values comes from the covariate.csv file.
The integrands values come from the predict_integrand.csv file
and the covariate multiplier list.

sample_index
------------
Each sample_index corresponds to an independent random sample
of the model variables.

#. If :ref:`option_all_table@sample_method` is asymptotic,
   model variables for each sample are Gaussian correlated with mean equal to
   the optimal value and variance equal to the asymptotic approximation.
#. If :ref:`option_all_table@sample_method` is censor_asymptotic,
   model variables are the same as for asymptotic expect that values above
   (below) their upper bound (lower bound) are converted to the corresponding
   bound.
#. If :ref:`option_all_table@sample_method` is simulate,
   the model variables for each sample at the optimal values corresponding
   to an independent data set.

integrand_name
--------------
is the integrand for this sample is equal to the integrand names
in predict_integrand.csv
The integrand names ``mulcov_0`` , ``mulcov_1`` , ...
corresponds to the first , second , ...
covariate multiplier in the csv fit
:ref:`csv.fit@Input Files@mulcov.csv` file.

avg_integrand
-------------
This float is the mode value for the average of the integrand,
with covariate and other effects but without measurement noise.

node_name
---------
is the node name for this sample is predicting for.
This cycles through all the nodes in covariate.csv.

sex
---
is the sex, female, both, or male, that the predictions are for.

fit_node_name
-------------
is the node name corresponding to the fit, and samples, that was used
to do these predictions.
This identifies the nearest ancestor that had a successful fit and samples.

fit_sex
-------
is the sex corresponding to the fit, and samples, that were used
to do these prediction.

posterior
.........
If *fit_node_name* and *fit_sex* are the same as *node_name* and *sex* ,
the fit and samples succeeded for this *node_name* and *sex* and
this row contains a posterior prediction for this *node_name* and *sex* .

prior
.....
If *fit_node_name* is not the same as *node_name* ,
or *fit_sex* is not the same as *sex* ,
this row contains a prior prediction for this *node_name* and *sex* .
The pair ( *fit_node_name* , *fit_sex* ) correspond to
the closest ancestor fit that was successful.

age
---
is the age for this prediction and is one of
the ages in covariate.csv.

time
----
is the time for this prediction and is one of
the times in covariate.csv.

covariate_names
---------------
The rest of the columns are covariate names and contain the value
of the corresponding covariate in
:ref:`csv.fit@Input Files@covariate.csv` .

tru_predict.csv
===============
If :ref:`csv.predict@sim_dir` is None, this file is not created.
Otherwise, this file contains the predictions for the model variables
corresponding to the simulation.
It is similar to :ref:`csv.predict@Output Files@fit_predict.csv`
with the following differences:

#. The first line (header line) is the same in this file and
   fit_predict.csv.
#. If the other lines, in both files, are sorted by
   ( *node_name* , *avgint_id* ) ,
   the other lines are the same except for the value in the
   avg_integrand column.
#. The model variables and true values, are for the
   *fit_node_name* and *fit_sex* . Hence this does not really represent truth
   unless these are the same as *node_name* and *sex* .

sam_predict.csv
===============
This is a sampling of the predictions,
using the posterior distribution of the model variables:
It is similar to :ref:`csv.predict@Output Files@fit_predict.csv`
with the following differences:

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
# ----------------------------------------------------------------------------
# Returns the node indices for the ancestors of the node specified by node_id.
# The node specified by node_id is included in this set.
def ancestor_set(node_table, node_id) :
   result = { node_id }
   while node_table[node_id]['parent'] != None :
      node_id = node_table[node_id]['parent']
      result.add(node_id)
   return result
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
def set_global_option_value(fit_dir, option_table, number_sample_fit, top_node_name) :
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
      'number_sample_predict' : (int,   number_sample_fit)  ,
      'plot'                  : (bool,  False)              ,
      'zero_meas_value'       : (bool,  False)              ,
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
      if value.strip() != '' :
         if option_type == bool :
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
# BEGIN_PREDICT
# at_cascade.csv.predict
def predict(fit_dir, sim_dir=None, start_job_name=None, max_job_depth=None) :
   assert type(fit_dir)  == str
   assert sim_dir        == None or type(sim_dir) == str
   assert start_job_name == None or type(start_job_name) == str
   assert max_job_depth  == None or type(max_job_depth) == int
   # END_PREDICT
   #
   # dismod_node_table, dismod_option_table
   database     = f'{fit_dir}/root.db'
   connection   = dismod_at.create_connection(
      database, new = False, readonly = True
   )
   dismod_node_table   = dismod_at.get_table_dict(connection, 'node')
   dismod_option_table = dismod_at.get_table_dict(connection, 'option')
   connection.close()
   #
   # top_node_name
   top_node_name = None
   for row in dismod_node_table :
      if row['parent'] == None :
         if top_node_name != None :
            msg = 'root.db: node table: more than one node has no parent'
            assert False, msg
         top_node_name = row['node_name']
   if top_node_name == None :
      msg = 'root.db: node_table: no node has None for parent'
      assert False, msg
   #
   # refit_split
   refit_split  = True
   option_table = at_cascade.csv.read_table(f'{fit_dir}/option_fit.csv')
   for row in option_table :
      if row['name'] == 'refit_split' :
         if row['value'] == 'false' :
            refit_split = False
   #
   # global_option_value
   option_table = at_cascade.csv.read_table(f'{fit_dir}/option_predict.csv')
   option_fit_table = at_cascade.csv.read_table(f'{fit_dir}/option_fit_out.csv')
   for row in option_fit_table:
      if row['name'] == 'number_sample':
         number_sample_fit = int(row['value'])
   set_global_option_value(
      fit_dir, option_table, number_sample_fit, top_node_name
   )
   #
   # start_node_name
   start_node_name = None
   if start_job_name == None :
      for row in dismod_option_table :
         if row['option_name'] == 'parent_node_name' :
            start_node_name = row['option_value']
         elif row['option_value'] == 'parent_node_id' :
            start_node_id   = int( row['option_value'] )
            start_node_name = dismod_node_table[parent_node_id]['node_name']
   else :
      index           = start_job_name.rindex('.')
      start_node_name = start_job_name[: index]
   assert start_node_name != None
   #
   # max_node_depth
   if max_job_depth == None :
      max_node_depth = None
   elif not refit_split :
      max_node_depth = max_job_depth
   elif start_job_name == None or start_job_name.endswith('.both') :
      if refit_split :
         if max_job_depth > 0 :
            max_node_depth = max_job_depth - 1
         else :
            max_node_depth = 0
      else :
         max_node_depth = max_job_depth
   else :
         max_node_depth = max_job_depth
   #
   # fit_goal_table
   file_name      = f'{fit_dir}/fit_goal.csv'
   fit_goal_table = at_cascade.csv.read_table(file_name)
   if len(fit_goal_table) == 0 :
      fit_goal_table = list()
      for node_id in range( len(dismod_node_table) ) :
         node_name = dismod_node_table[node_id]['node_name']
         row = { 'node_id' : node_id , 'node_name' : node_name}
         fit_goal_table.append( row )
   for row in fit_goal_table :
      node_name = row['node_name']
      node_id   = at_cascade.table_name2id(dismod_node_table, 'node', node_name)
      row['node_id'] = node_id
   #
   # fit_goal_set
   fit_goal_set   = set()
   start_node_id  = \
      at_cascade.table_name2id(dismod_node_table, 'node', start_node_name)
   for row in fit_goal_table :
      node_id   = row['node_id']
      node_list = [ node_id ]
      while node_id != start_node_id and node_id != None :
         node_id   = dismod_node_table[node_id]['parent']
         if node_id != None :
            node_list.append( node_id )
      if node_id == start_node_id :
         if max_node_depth == None :
            node_id   = node_list[0]
         elif len(node_list) <= max_node_depth + 1 :
            node_id   = node_list[0]
         else :
            node_id  = node_list[-max_node_depth - 1]
         node_name = dismod_node_table[node_id]['node_name']
         fit_goal_set.add( node_name )
   #
   if len(fit_goal_set) == 0 :
      msg  = f'Cannot find start_node_name = {start_node_name},\n'
      msg += 'or any of its children, in fit_goal.csv'
      assert False, msg
   #
   # covariate_table
   file_name       = f'{fit_dir}/covariate.csv'
   covariate_table = at_cascade.csv.read_table(file_name)
   #
   # predict
   at_cascade.csv.pre_parallel(
      fit_dir,
      sim_dir,
      covariate_table,
      fit_goal_set,
      start_job_name,
      max_job_depth,
      global_option_value,
   )
