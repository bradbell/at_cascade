# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
import multiprocessing
import dismod_at
import at_cascade
import copy
import os
import time
'''

{xrst_begin csv_fit}
{xrst_spell
   avg
   avgint
   const
   dage
   dir
   dtime
   laplace
   meas
   pini
   rho
   sincidence
   std
   sqlite
   truncation
}

Fit a Simulated Data Set
########################

Prototype
*********
{xrst_literal
   # BEGIN_FIT
   # END_FIT
}

Example
*******
:ref:`csv_fit_xam` .

fit_dir
*******
This string is the directory name where the csv files
are located.

Input Files
***********

option_in.csv
=============
This csv file has two columns,
one called ``name`` and the other called ``value``.
If an option name does not appear, the corresponding
default value is used for the option.
The rows are documented below by the name column:

max_fit
-------
This is the maximum number of data values to fit per integrand.
If for a particular fit an integrand has more than this number of
data values, a subset of this size is randomly selected.
There is once exception to this rule, the female and male fit
at the root node uses twice this number of values per integrand
(because the covariate multipliers are frozen after these fits).
The default value for *max_fit* is 250.

random_seed
-----------
This integer is used to seed the random number generator.
The default value of *random_seed* is chosen
to be the system time in seconds (as an integer).

root_node_name
--------------
This string is the name of the root node.
The default for *root_node_name* is the top root of the entire node tree.
Only the root node and its descendents will be fit.

node.csv
========
This file has the same description as the simulate
:ref:`csv_simulate@Input Files@node.csv` file.

covariate.csv
=============
This csv file has the same description as the simulate
:ref:`csv_simulate@Input Files@covariate.csv` file.

fit_goal.csv
============
Each node in this file must be a descendant of the root node.
Each node, and all its ancestors up to the root node, will be fit.

node_name
---------
Is the name of a node in the fit goal set.
Each such node must be an descendant of the root node.

predict_integrand.csv
=====================
This is the list of integrands at which predictions are made
and stored in :ref:`csv_fit@Output Files@fit_predict.csv` .

integrand_name
--------------
This string is the name of one of the prediction integrands.


{xrst_comment ---------------------------------------------------------------}

prior.csv
=========
This csv file has the following columns:

name
----
is a string contain the name of this prior.
No two priors can have the same name.

lower
-----
is a float containing the lower limit for the truncated density
for this prior.
If this value is empty, there is no lower bound.

upper
-----
is a float containing the upper limit for the truncated density
for this prior.
If this value is empty, there is no upper bound.

mean
----
is a float containing the mean for the density
for this prior (before truncation).
If density is uniform, this value is only used for a starting
and scaling the optimization.

std
---
is a float containing the standard deviation for the density
for this prior (before truncation).
If density is uniform, this value is not used and can be empty.

density
-------
is one of the following strings:
uniform, gaussian, cen_gaussian, laplace, cen_laplace.
(Only these densities are included, so far, so that we do not have to
worry about the log offset or degrees of freedom.)

{xrst_comment ---------------------------------------------------------------}

parent_rate.csv
===============
This file specifies the prior for the root node parent rates.
For each value of *rate_name*,
this file must have a rectangular grid in *age* and *time* .

rate_name
---------
is a string containing the name for the non-zero rates
(except for omega which is specified by covariate.csv).

age
---
is a float containing the age for this grid point.

time
----
is a float containing the time for this grid point.

value_prior
-----------
is a string containing the name of the value prior for this grid point.
If value_prior is empty, const_value must be non-empty.

dage_prior
----------
is a string containing the name of the dage prior for this grid point.
If dage_prior is empty, there is no prior for the forward age difference
of this rate at this grid point.
This prior cannot be censored.

dtime_prior
-----------
is a string containing the name of the dtime prior for this grid point.
If dtime_prior is empty, there is no prior for the forward time difference
of this rate at this grid point.
The specified prior cannot be censored.

const_value
-----------
is a float specifying a constant value for this grid point or the empty string.
This is equivalent to the upper and lower limits being equal to this value.
If const_value is empty, value_prior must be non-empty.

{xrst_comment ---------------------------------------------------------------}

child_rate.csv
==============
This csv file specifies the prior for the child rates; i.e.,
the random effects.

rate_name
---------
this string is the name of this rate and is one of the following:
pini, iota, rho, chi (name cannot be omega).

value_prior
-----------
is a string containing the name of the value prior for this child rate.
Note that the child rates are in log of rate space.
In addition, they are constant in age and time
(this is a limitation of the csv_fit).

{xrst_comment ---------------------------------------------------------------}

mulcov.csv
==========
This csv file specifies the covariate multipliers.

covariate
---------
this string is the name of the covariate for this multiplier.

type
----
This string is rate_value, meas_value, or meas_noise.

effected
--------
is the name of the integrand or rate affected by this multiplier.

value_prior
-----------
is a string containing the name of the value prior
for this covariate multiplier.
Note that the covariate multipliers are constant in age and time
(this is a limitation of the csv_fit).

{xrst_comment ---------------------------------------------------------------}

data_in.csv
===========
This csv file specifies the data set
with each row corresponding to one data point.

data_id
-------
is an :ref:`csv_module@Notation@Index Column` for data.csv.

integrand
---------
This string is a dismod_at integrand; e.g. ``Sincidence``.

node_name
---------
This string identifies the node corresponding to this data point.

sex
---
This string is the sex for this data point.

age_lower
---------
This float is the lower age limit for this data row.

age_upper
---------
This float is the upper age limit for this data row.

time_lower
----------
This float is the lower time limit for this data row.

time_upper
----------
This float is the upper time limit for this data row.

meas_value
----------
This float is the measured value for this data point.

meas_std
--------
This float is the standard deviation of the measurement noise
for this data point.

hold_out
--------
This integer is one (zero) if this data point is held out (not held out)
from the fit.

{xrst_comment ---------------------------------------------------------------}

Output Files
************

root_node.db
============
This is the dismod_at sqlite database corresponding to the root node for
the cascade.

all_node.db
===========
This is the at_cascade sqlite all node database for the cascade.

option_out.csv
==============
This is a copy of :ref:`csv_fit@Input Files@option_in.csv` with the default
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

integrand
---------
is the integrand for this sample is equal to the integrand names
in predict_integrand.csv

avg_integrand
-------------
This float is the mode value for the average of the integrand,
with covariate and other effects but without measurement noise.

node
----
is the node for this sample and is equal to the nodes in covariate.csv.

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

{xrst_end csv_fit}
'''
#-----------------------------------------------------------------------------
# split_reference_table
split_reference_table = [
   { 'split_reference_name' : 'female' , 'split_reference_value' : -0.5 },
   { 'split_reference_name' : 'both'   , 'split_reference_value' :  0.0 },
   { 'split_reference_name' : 'male'   , 'split_reference_value' : +0.5 },
]
# ----------------------------------------------------------------------------
# Sets global csv_option_value to dict representation of csv option table.
#
# fit_dir
# is the directory where the input csv files are located.
#
# option_table :
# is the list of dict corresponding to the csv option table
#
# top_node_name
# is the name of the top node in the node tree
#
# option_out.csv
# As a side effect, this routine write a copy of the csv option table
# with the default values filled in.
#
# csv_option_value[name] :
# is the option value corresponding the specified option name.
# Here name is a string and value
# has been coverted to its corresponding type.
#
csv_option_value = None
def set_csv_option_value(fit_dir, option_table, top_node_name) :
   global csv_option_value
   assert csv_option_value == None
   assert type(option_table) == list
   if len(option_table) > 0 :
      assert type( option_table[0] ) == dict
   #
   # option_default
   default_seed = int( time.time() )
   option_default  = {
      'max_fit'            : (int,  250)           ,
      'random_seed'        : (int , default_seed ) ,
      'root_node_name'     : (str,  top_node_name) ,
   }
   #
   # csv_option_value
   line_number      = 0
   csv_option_value = dict()
   for row in option_table :
      line_number += 1
      name         = row['name']
      if name in csv_option_value :
         msg  = f'csv_fit: Error: line {line_number} in option_in.csv\n'
         msg += f'the name {name} appears twice in this table'
         assert False, msg
      if not name in option_default :
         msg  = f'csv_fit: Error: line {line_number} in option_in.csv\n'
         msg += f'{name} is not a valid option name'
         assert False, msg
      (option_type, defualt) = option_default[name]
      value                  = option_type( row['value'] )
      csv_option_value[name] = value
   #
   # csv_option_value
   for name in option_default :
      if name not in csv_option_value :
         (option_type, default) = option_default[name]
         csv_option_value[name] = default
   #
   # option_out.csv
   table = list()
   for name in csv_option_value :
      row = { 'name' : name , 'value' : csv_option_value[name] }
      table.append(row)
   file_name = f'{fit_dir}/option_out.csv'
   at_cascade.csv.write_table(file_name, table)
   #
   assert type(csv_option_value) == dict
# ----------------------------------------------------------------------------
# Converts smoothing prioros on a grid to a prior function
#
# set:      sets the function value at one of the grid points
# __call__: gets the function value at one of the grid points
#
class smoothing_function :
   def __init__(self, name) :
      self.name  = name
      self.value = dict()
   def set(self, age, time, value_prior, dage_prior, dtime_prior) :
      if type( value_prior ) == float :
         assert dage_prior == None
         assert dtime_prior == None
         self.value[ (age, time) ] = value_prior
      else :
         type(value_prior) == str
         type(dage_prior) == str
         type(dtime_prior) == str
         self.value[ (age, time) ] = (value_prior, dage_prior, dtime_prior)
   def __call__(self, age, time) :
      if (age, time) not in self.value :
         msg = f'The grid for smoothing {self.name} is not rectangular'
         assert False, msg
      return self.value[ (age, time) ]
# ----------------------------------------------------------------------------
# Writes the root node data base
#
# root_node.db
# this database is created by create_root_node_database.
# If there is an existing version of this file it is overwrittern.
#
# fit_dir
# is the directory where the csv and database files are located.
#
# age_grid
# is a sorted list of the age values in the covariate.csv file.
#
# time_grid
# is a sorted list of the time values in the covariae.csv file.
#
# covariate_table
# is the list of dict corresponding to the covariate.csv file
#
# csv_option_value
# As a side effect,
# this routine sets csv_option_value; see set_csv_option_value.
#
# age_grid, time_grid, covariate_table =
def create_root_node_database(fit_dir) :
   assert type(fit_dir) == str
   #
   # output_file
   output_file = f'{fit_dir}/root_node.db'
   #
   # input_table
   input_table = dict()
   input_list = [
      'node',
      'covariate',
      'option_in',
      'predict_integrand',
      'prior',
      'parent_rate',
      'child_rate',
      'mulcov',
      'data_in',
   ]
   print('begin reading csv files')
   for name in input_list :
      file_name         = f'{fit_dir}/{name}.csv'
      table             = at_cascade.csv.read_table(file_name)
      input_table[name] = at_cascade.csv.empty_str(table, 'to_none')
   #
   print('being creating root node database' )
   #
   # node_set, top_node_name
   node_set       = set()
   top_node_name  = None
   for row in input_table['node'] :
      node_name   = row['node_name']
      parent_name = row['parent_name']
      if node_name in node_set :
         msg = f'node_name {node_name} apprears twice in node.csv'
         assert False, msg
      if parent_name == None :
         if top_node_name != None :
            msg = 'node.csv: more than one node has no parent node'
            assert False, msg
         top_node_name = node_name
      node_set.add( node_name )
   if top_node_name == None :
      msg = 'node.csv: no node has an empty parent_name'
      assert False, msg
   #
   # csv_option_value
   set_csv_option_value(
      fit_dir, input_table['option_in'], top_node_name
   )
   #
   # root_node_name, random_seed
   root_node_name = csv_option_value['root_node_name']
   random_seed    = csv_option_value['random_seed']
   #
   # covariate_average
   covariate_average = at_cascade.csv.covariate_avg(
      input_table['covariate'], root_node_name
   )
   #
   # forbidden_covariate
   forbidden_covariate = set( input_table['data_in'][0].keys() )
   #
   # covariate_table
   covariate_table = [{
      'name': 'sex', 'reference': 0.0, 'max_difference' : 0.5
   }]
   for covariate_name in covariate_average.keys() :
      covariate_table.append({
         'name':            covariate_name,
         'reference':       covariate_average[covariate_name],
         'max_difference' : None
      })
   #
   # option_table
   option_table = [
      { 'name' : 'parent_node_name',  'value' : root_node_name },
      { 'name' : 'random_seed',       'value' : str( random_seed ) },
      { 'name' : 'print_level_fixed', 'value' : '5' },
   ]
   #
   # spline_cov
   age_grid, time_grid, spline_cov = at_cascade.csv.covariate_spline(
      input_table['covariate'], node_set
   )
   #
   # data_table
   data_table     = input_table['data_in']
   sex_name2value = { 'female' : -0.5, 'both' : 0.0, 'male' : 0.5 }
   for row in data_table :
      #
      # age_mid
      age_lower = float( row['age_lower'] )
      age_upper = float( row['age_upper'] )
      age_mid   = (age_lower + age_upper) / 2.0
      #
      # time_mid
      time_lower = float( row['time_lower'] )
      time_upper = float( row['time_upper'] )
      time_mid   = (time_lower + time_upper) / 2.0
      #
      # row[c_j] for j = 0, ..., n_covariate - 1
      node_name = row['node_name']
      sex       = row['sex']
      for index, covariate_name in enumerate( covariate_average.keys() ) :
         spline              = spline_cov[node_name][sex][covariate_name]
         covariate_value     = spline(age_mid, time_mid)
         row[covariate_name] = covariate_value
      #
      # row
      row['node']       = row['node_name']
      row['age_lower']  = age_lower
      row['age_upper']  = age_lower
      row['time_lower'] = time_lower
      row['time_upper'] = time_lower
      row['weight']     = ''
      row['subgroup']   = 'world'
      row['density']    = 'gaussian'
      row['sex']        = sex_name2value[sex]
   #
   # integrand_table
   integrand_set = set()
   for row in data_table :
      integrand_set.add( row['integrand'] )
   for row in input_table['predict_integrand'] :
      integrand_set.add( row['integrand_name'] )
   integrand_table = list()
   for integrand in integrand_set :
      row = { 'name' : integrand }
      integrand_table.append(row)
   for mulcov_id in range( len( input_table['mulcov'] ) ) :
      integrand_table.append( { 'name': f'mulcov_{mulcov_id}' } )
   #
   # subgroup_table
   subgroup_table = [{ 'subgroup' : 'world', 'group' : 'world' }]
   #
   # prior_table
   prior_table = copy.copy( input_table['prior'] )
   for row in prior_table :
      if row['lower'] != None :
         row['lower'] = float( row['lower'] )
      if row['upper'] != None :
         row['upper'] = float( row['upper'] )
      if row['std'] != None :
         row['std']   = float( row['std'] )
   #
   # min_data_age,  max_data_age
   # min_data_time, max_data_time
   min_data_age  = data_table[0]['age_lower']
   max_data_age  = data_table[0]['age_upper']
   min_data_time = data_table[0]['time_lower']
   max_data_time = data_table[0]['time_upper']
   for row in data_table :
      min_data_age  = min( min_data_age, row['age_lower'] )
      max_data_age  = max( max_data_age, row['age_upper'] )
      min_data_time = min( min_data_time, row['time_lower'] )
      max_data_time = max( max_data_time, row['time_upper'] )
   #
   # age_list
   age_set = set( age_grid )
   age_set.add(min_data_age)
   age_set.add(max_data_age)
   for row in input_table['parent_rate'] :
      age_set.add( float( row['age'] ) )
   age_list = sorted( list( age_set ) )
   #
   # time_list
   time_set = set( time_grid )
   time_set.add(min_data_time)
   time_set.add(max_data_time)
   for row in input_table['parent_rate'] :
      time_set.add( float( row['time'] ) )
   time_list = sorted( list( time_set ) )
   #
   # smooth_dict
   smooth_dict = dict()
   for row in input_table['parent_rate'] :
      name = row['rate_name'] + '_parent'
      age  = float( row['age'] )
      time = float( row['time'] )
      if name not in smooth_dict :
         fun = smoothing_function(name)
         smooth_dict[name] = {
            'age_id'  : set() ,
            'time_id' : set() ,
            'fun'     : fun    ,
         }
      age_id  = age_list.index( age )
      time_id = time_list.index( time )
      smooth_dict[name]['age_id'].add( age_id )
      smooth_dict[name]['time_id'].add( time_id )
      if row['const_value'] != None :
         const_value = float( row['const_value'] )
         smooth_dict[name]['fun'].set(age, time, const_value)
      else :
         value_prior = row['value_prior']
         dage_prior  = row['dage_prior']
         dtime_prior = row['dtime_prior']
         smooth_dict[name]['fun'].set(
            age, time, value_prior, dage_prior, dtime_prior
         )
   #
   # smooth_dict
   for row in input_table['child_rate'] :
      name = row['rate_name'] + '_child'
      fun = smoothing_function(name)
      smooth_dict[name] = {
         'age_id'  : {0},
         'time_id' : {0},
         'fun'     : fun    ,
      }
      smooth_dict[name]['fun'].set(
         age         = age_list[0]            ,
         time        = time_list[0]           ,
         value_prior = row['value_prior']     ,
         dage_prior  = None                   ,
         dtime_prior = None                   ,
      )
   #
   # smooth_dict
   for (i_row, row) in enumerate( input_table['mulcov'] ) :
      name = f'mulcov_{i_row}'
      fun = smoothing_function(name)
      smooth_dict[name] = {
         'age_id'  : {0},
         'time_id' : {0},
         'fun'     : fun    ,
      }
      smooth_dict[name]['fun'].set(
         age         = age_list[0]            ,
         time        = time_list[0]           ,
         value_prior = row['value_prior']     ,
         dage_prior  = None                   ,
         dtime_prior = None                   ,
      )

   #
   # smooth_table
   smooth_table = list()
   for name in smooth_dict :
      row = {
         'name'    : name                           ,
         'age_id'  : smooth_dict[name]['age_id']    ,
         'time_id' : smooth_dict[name]['time_id']   ,
         'fun'     : smooth_dict[name]['fun']       ,
      }
      smooth_table.append( row )
   #
   # node_table
   node_table = list()
   for row_in in input_table['node'] :
      row_out = { 'name' : row_in['node_name'] }
      if row_in['parent_name'] == None :
         row_out['parent'] = ''
      else :
         row_out['parent'] = row_in['parent_name']
      node_table.append( row_out )
   #
   # mulcov_table
   mulcov_table = input_table['mulcov']
   for (i_row, row) in enumerate(mulcov_table) :
      del row['value_prior']
      row['smooth'] = f'mulcov_{i_row}'
      row['group'] = 'world'
   #
   # rate_table
   rate_table = list()
   for rate_name in [ 'pini', 'iota', 'rho', 'chi' ] :
      parent_smooth = rate_name + '_parent'
      if parent_smooth in smooth_dict :
         child_smooth  = rate_name + '_child'
         if child_smooth not in smooth_dict :
            child_smooth = None
         row = {
            'name'          : rate_name      ,
            'parent_smooth' : parent_smooth  ,
            'child_smooth'  : child_smooth   ,
         }
         rate_table.append( row )
   #
   dismod_at.create_database(
         file_name         = output_file,
         age_list          = age_list,
         time_list         = time_list,
         integrand_table   = integrand_table,
         node_table        = node_table,
         subgroup_table    = subgroup_table,
         weight_table      = list(),
         covariate_table   = covariate_table,
         avgint_table      = list(),
         data_table        = data_table,
         prior_table       = prior_table,
         smooth_table      = smooth_table,
         nslist_table      = dict(),
         rate_table        = rate_table,
         mulcov_table      = mulcov_table,
         option_table      = option_table,
   )
   covariate_table = input_table['covariate']
   #
   assert type(age_grid) == list
   assert type(time_grid) == list
   assert type(covariate_table) == list
   assert type( covariate_table[0] ) == dict
   return age_grid, time_grid, input_table['covariate']
# ----------------------------------------------------------------------------
# Writes the all node data base.
#
# all_node.db
# this database is created by create_all_node_database.
# If there is an existing version of this file it is overwrittern.
#
# root_node.db
# is the name of the root node database
# This data base must exist and is not modified.
#
# fit_dir
# is the directory where the csv and database files are located.
#
# age_grid
# is a sorted list of the age values in the covariate.csv file.
#
# time_grid
# is a sorted list of the time values in the covariae.csv file.
#
# covariate_table
# is the list of dict corresponding to the covariate.csv file.
#
def create_all_node_database(fit_dir, age_grid, time_grid, covariate_table) :
   assert type(fit_dir) == str
   assert type(age_grid) == list
   assert type(time_grid) == list
   assert type(covariate_table) == list
   assert type( covariate_table[0] ) == dict
   #
   # root_node_table
   root_node_table = dict()
   new          = False
   database     = f'{fit_dir}/root_node.db'
   connection   = dismod_at.create_connection(database, new)
   for name in [ 'mulcov', 'age', 'time', 'covariate' ] :
      root_node_table[name] = dismod_at.get_table_dict(
         connection = connection, tbl_name = name)
   connection.close()
   #
   # root_node_name
   root_node_name = at_cascade.get_parent_node(database)
   #
   # user
   user  = os.environ.get('USER').replace(' ', '_')
   #
   # max_number_cpu
   max_number_cpu = max(1, multiprocessing.cpu_count() - 1)
   #
   # all_option
   all_option = {
      # 'absolute_covariates'        : None,
      'balance_fit'                  : 'sex -0.5 +0.5' ,
      'max_abs_effect'               : 2.0 ,
      'max_fit'                      : csv_option_value['max_fit'],
      'max_number_cpu'               : max_number_cpu,
      'perturb_optimization_scale'   : 0.2,
      'perturb_optimization_start'   : 0.2,
      'shared_memory_prefix'         : user,
      'result_dir'                   : fit_dir,
      'root_node_name'               : root_node_name,
      'split_covariate_name'         : 'sex',
      'root_split_reference_name'    : 'both',
      'shift_prior_std_factor'       : 2.0,
   }
   #
   # node_split_table
   node_split_table = [ { 'node_name' : root_node_name } ]
   #
   # mulcov_freeze_table
   mulcov_freeze_table = list()
   for (mulcov_id, row) in enumerate(root_node_table['mulcov']) :
      covariate_id    = row['covariate_id']
      cov_row         = root_node_table['covariate'][covariate_id]
      covariate_name = cov_row['covariate_name']
      if covariate_name == 'sex' :
         assert split_reference_table[1]['split_reference_name'] == 'both'
         row = {
            'fit_node_name'      : root_node_name     ,
            'split_reference_id' : 1                  ,
            'mulcov_id'          : mulcov_id          ,
         }
         mulcov_freeze_table.append(row)
      else :
         for split_reference_id in [ 0 , 2 ] :
            # split_reference_id 0 for female, 2 for male
            row = {
               'fit_node_name'      : root_node_name     ,
               'split_reference_id' : split_reference_id ,
               'mulcov_id'          : mulcov_id          ,
            }
            mulcov_freeze_table.append(row)
   #
   # omega_grid
   age_list     = [ row['age'] for row  in root_node_table['age'] ]
   age_id_grid  = [ age_list.index(age)  for age in age_grid ]
   #
   time_list    = [ row['time'] for row in root_node_table['time'] ]
   time_id_grid = [ time_list.index(time) for time in time_grid ]
   #
   omega_grid = { 'age' : age_id_grid, 'time' : time_id_grid }
   #
   # omega_data
   # This is set equal to the value of omega and is only used for the
   # omega constraint.
   n_age      = len( age_grid )
   n_time     = len( time_grid )
   none_list  = (n_age * n_time)  * [ None ]
   omega_data = dict()
   for row in covariate_table :
      node_name          = row['node_name']
      sex                = row['sex']
      age                = float( row['age'] )
      time               = float( row['time'] )
      omega              = float( row['omega'] )
      #
      if sex not in [ 'female', 'male' ] :
         msg  = 'covariate.csv: sex is not female or male'
         assert False, msg
      split_reference_id = at_cascade.table_name2id(
         split_reference_table, 'split_reference', sex
      )
      assert split_reference_id != 1
      if node_name not in omega_data :
         omega_data[node_name] = list()
         for k in range( len(split_reference_table) ) :
               row = list()
               for ij in range( n_age * n_time ) :
                  row.append(None)
               omega_data[node_name].append(row)
      #
      k = split_reference_id
      i = age_grid.index(age)
      j = time_grid.index(time)
      omega_data[node_name][k][i * n_time + j] = omega
   for node_name in omega_data :
      for i in range( n_age ) :
         for j in range( n_time ) :
            female = omega_data[node_name][0][i * n_time + j]
            both   = omega_data[node_name][1][i * n_time + j]
            male   = omega_data[node_name][2][i * n_time + j]
            assert female != None and both == None and male != None
            both   = (male + female) / 2.0
            omega_data[node_name][1][i * n_time + j] = both
   #
   # create_all_node_db
   at_cascade.create_all_node_db(
      all_node_database         = f'{fit_dir}/all_node.db'  ,
      root_node_database        = f'{fit_dir}/root_node.db' ,
      all_option                = all_option                ,
      split_reference_table     = split_reference_table     ,
      node_split_table          = node_split_table          ,
      mulcov_freeze_table       = mulcov_freeze_table       ,
      omega_grid                = omega_grid                ,
      omega_data                = omega_data                ,
   )
# ----------------------------------------------------------------------------
def predict_one(
   fit_dir               ,
   fit_node_database     ,
   fit_node_id           ,
   all_node_database     ,
   all_covariate_table   ,
) :
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
            if covariate_name == 'sex' :
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
   # avgint_table
   new        = False
   connection = dismod_at.create_connection(fit_node_database, new)
   dismod_at.replace_table(connection, 'avgint', avgint_table)
   connection.close()
   #
   # fit_node_dir
   index        = fit_node_database.rfind('/')
   fit_node_dir = fit_node_database[: index]
   #
   # prefix
   for prefix in [ 'fit' , 'sam' ] :
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
# ----------------------------------------------------------------------------
def predict_all(fit_dir, covariate_table, fit_goal_set) :
   assert type(fit_dir) == str
   assert type(covariate_table) == list
   assert type( covariate_table[0] ) == dict
   assert type(fit_goal_set) == set
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
   # job_id, job_row, fit_node_database_list
   fit_node_database_list = list()
   for (job_id, job_row) in enumerate(job_table) :
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
      # fit_node_database, fit_node_database_list
      fit_node_database = f'{fit_dir}/{fit_database_dir}/dismod.db'
      fit_node_database_list.append( fit_node_database )
      #
      # sam_node_predict
      sam_node_predict = f'{fit_dir}/{fit_database_dir}/sam_predict.csv'
      #
      # check for an error during fit both and fit fixed
      two_errors = False
      if job_name in error_message_dict :
            two_errors = len( error_message_dict[job_name] ) > 1
      if two_errors :
         if os.path.exists( sam_node_predict ) :
            os.remove( sam_node_predict )
         print( f'{job_id+1}/{n_job} Error in {job_name}' )
      elif not os.path.exists( fit_node_database ) :
         print( f'{job_id+1}/{n_job} Missing dismod.db for {job_name}' )
      else :
         print( f'{job_id+1}/{n_job} Creating sam_predict.csv for {job_name}' )
      #
      # predict_one
      predict_one(
         fit_dir               = fit_dir          ,
         fit_node_database     = fit_node_database ,
         fit_node_id           = fit_node_id       ,
         all_node_database     = all_node_db       ,
         all_covariate_table   = covariate_table   ,
      )
   #
   # sex_value2name
   sex_value2name = dict()
   for row in split_reference_table :
      name  = row['split_reference_name']
      value = row['split_reference_value']
      sex_value2name[value] = name
   #
   # fit_node_dir
   index = fit_node_database.rindex('/')
   fit_node_dir           = fit_node_database[: index]
   #
   # sam_predict_table, fit_predict_tale
   sam_predict_table = list()
   fit_predict_table = list()
   #
   # fit_node_database
   for fit_node_database in fit_node_database_list :
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
            node_id         = int( row_in['node_id'] )
            row_out['node'] = node_table[node_id]['node_name']
            #
            integrand_id         = int( row_in['integrand_id'] )
            row_out['integrand'] = integrand_table[integrand_id]['integrand_name']
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
# BEGIN_FIT
def fit(fit_dir) :
   assert type(fit_dir) == str
# END_FIT
   #
   # fit_goal_set
   fit_goal_set   = set()
   file_name      = f'{fit_dir}/fit_goal.csv'
   fit_goal_table = at_cascade.csv.read_table(file_name)
   for row in fit_goal_table :
      fit_goal_set.add( row['node_name'] )
   #
   # root_node.db
   age_grid, time_grid, covariate_table = create_root_node_database(fit_dir)
   #
   # all_node.db
   create_all_node_database(fit_dir, age_grid, time_grid, covariate_table)
   #
   # cascade_root_node
   at_cascade.cascade_root_node(
      all_node_database  = f'{fit_dir}/all_node.db'  ,
      root_node_database = f'{fit_dir}/root_node.db' ,
      fit_goal_set       = fit_goal_set              ,
      no_ode_fit         = True                      ,
      fit_type_list      = [ 'both', 'fixed']        ,
   )
   #
   # predict
   predict_all(fit_dir, covariate_table, fit_goal_set)
