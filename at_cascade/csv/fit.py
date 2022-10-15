# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
import dismod_at
import at_cascade
import copy
'''

{xrst_begin csv_fit}
{xrst_spell
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

Under Construction
******************

Prototype
*********
{xrst_literal
   # BEGIN_FIT
   # END_FIT
}

fit_dir
*******
This string is the directory name where the csv files
are located.

Input Files
***********

node.csv
========
This csv file has the same description as the simulate
:ref:`csv_simulate@Input Files@node.csv` file.

covariate_csv
=============
This csv file has the same description as the simulate
:ref:`csv_simulate@Input Files@covariate.csv` file.

option.csv
==========
This csv file has two columns,
one called ``name`` and the other called ``value``.
The rows are documented below by the name column:

root_node_name
--------------
This string is the name of the root node.
The default for *root_node_name* is the top (root) of
the entire node tree.

fit_goal.csv
============
If a node is in this file, that node and all it's ancestors will be fit.

node_name
---------
Is the name of a node in the fit goal set.
Each such node must be an descendant of the root node.

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

upper
-----
is a float containing the upper limit for the truncated density
for this prior.

std
---
is a float containing the standard deviation limit for the density
for this prior (before truncation).

density
-------
is one of the following strings:
uniform, gaussian, cen_gaussian, laplace, cen_laplace.
(Only these densities are included, so far, so that we do not have to
worry about the log offset or degrees of freedom.)

{xrst_comment ---------------------------------------------------------------}

smooth_grid.csv
===============
For each value of *smooth_name*,
this file must have a rectangular grid in *age* and *time* .

name
----
is a string containing the name for this smoothing.

age
---
is a float containing the age for this grid point or the empty string.

time
----
is a float containing the time for this grid point or the empty string.

value_prior
-----------
is a string containing the name of the value prior for this grid point.
If value_prior is empty, const_value must be non-empty.

dage_prior
----------
is a string containing the name of the dage prior for this grid point.
The specified prior cannot be censored.

dtime_prior
-----------
is a string containing the name of the dtime prior for this grid point.
The specified prior cannot be censored.

const_value
-----------
is a float specifying a constant value for this grid point or the empty string.
This is equivalent to the upper and lower limits being equal to this value.
If const_value is empty, value_prior must be non-empty.


{xrst_comment ---------------------------------------------------------------}

rate.csv
========
This csv file specifies which rates, besides omega,
are non-zero and what their prior are.

name
----
this string is the name of this rate and is one of the following:
pini, iota, rho, chi (name cannot be omega).

parent_smooth
-------------
This string is the name of the parent smoothing for this rate.

child_smooth
------------
This string is the name of the child smoothing for this rate.

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

smooth
------
is the name of the smoothing for this multiplier.

{xrst_comment ---------------------------------------------------------------}

data_in.csv
===========
This csv file specifies the data set
with each row corresponding to one data point.

data_id
-------
is an :ref:`csv_module@Notation@Index Column` for data.csv.

integrand_name
--------------
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
************
This is the dismod_at sqlite database corresponding to the root node for
the cascade.

all_node.db
***********
This is the at_cascade sqlite all node database for the cascade.


{xrst_end csv_fit}
'''
# ----------------------------------------------------------------------------
# Returns a dictionary version of option table
#
# option_table :
# is the list of dict corresponding to the option table
#
# option_value[name] :
# is the option value corresponding the the specified option name.
# Here name is a string and value
# has been coverted to its corresponding type.
#
# option_value =
def option_table2dict(fit_dir, option_table) :
   option_type  = {
      'root_not_name'     : string ,
   }
   line_number = 0
   for row in option_table :
      line_number += 1
      name         = row['name']
      if name in option_value :
         msg  = f'csv_fit: Error: line {line_number} in option.csv\n'
         msg += f'the name {name} appears twice in this table'
         assert False, msg
      if not name in option_type :
         msg  = f'csv_fit: Error: line {line_number} in option.csv\n'
         msg += f'{name} is not a valid option name'
         assert False, msg
      value        = option_type[name]( row['value'] )
      option_value[name] = value
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
   def set(age, time, value_prior, dage_prior = None, dtime_prior = None) :
      if type( value_prior ) == float :
         self.value[ (age, time) ] = value_prior
      else :
         type(value_prior) == str
         type(dage_prior) == str
         type(dtime_prior) == str
         self.value[ (age, time) ] = (value_prior, dage_prior, dtime_prior)
   def __call__(age, time) :
      if (age, time) not in self.value :
         msg = f'The grid for smoothing {self.name} is not rectangular'
         assert False, msg
      return self.value[ (age, time) ]
# ----------------------------------------------------------------------------
# Writes the root node data base
#
# root_node.db
# this database is created by root_node_database.
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
# age_grid, time_grid, covariate_table =
def root_node_database(fit_dir) :
   #
   # output_file
   output_file = f'{fit_dir}/root_node.db'
   #
   # input_table
   input_table = dict()
   input_list = [
      'data_in',
      'covariate',
      'node',
      'option',
      'prior',
      'rate',
      'smooth_grid',
   ]
   print('begin reading csv files')
   for name in input_list :
      file_name         = f'{fit_dir}/{name}.csv'
      input_table[name] = at_cascade.csv.read_table(file_name)
   #
   print('being creating root node database' )
   #
   # root_node_name
   option_value = option_table2dict(fit_dir, input_table['option'] )
   root_node_name = option_value['root_node_name']
   #
   # covariate_average
   covariate_average = at_cascade.csv.covariate_average(
      input_table['covariate'], root_node_name
   )
   #
   # forbidden_covariate
   forbidden_covariate = set( input_table['data_in'][0].keys() )
   #
   # covariate_table
   covariate_table = [{
      'name': sex, 'reference': 0.0, 'max_difference' : 0.5
   }]
   for covariate_name in covariate_average.keys() :
      covariate_table.append({
         'name':            covariate_name,
         'reference':       covariate_average[covariate_name],
         'max_difference' : None
      })
   #
   # node_set, root_node_name
   node_set       = set()
   root_node_name = None
   for row in input_table['node'] :
      node_name   = row['node_name']
      parent_name = row['parent_name']
      if node_name in node_set :
         msg = f'node_name {node_name} apprears twice in node.csv'
         assert False, msg
      if parent_name == '' :
         if root_node_name != '' :
            msg = 'node.csv: more than one node has no parent node'
            assert False, msg
         root_node_name = node_name
      node_set.add( node_name )
   if root_node_name == None :
      msg = 'node.csv: no node has an empty parent_name'
      assert False, msg
   #
   # root_node_name
   for row in input_table['option'] :
      if row['name'] == 'root_node_name' :
         root_node_name = row['value']
   #
   # option_table
   option_table = [
      { 'option_name' : 'parent_node_name', 'option_value' : root_node_name }
   ]
   #
   # spline_cov
   age_grid, time_grid, spline_cov = at_cascade.csv.covariate_spline(
      input_table['covariate'], node_set
   )
   #
   # data_table
   data_table = input_table['data_in']
   sex_value  = { 'female' : -0.5, 'both' : 0.0, 'male' : +0.5 }
   for row in data_table () :
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
      sex       = sex_value[ row['sex'] ]
      for index, covariate_name in enumerate( covariate_average.keys() ) :
         spline           = spline_cov[node_name][sex][covariate_name]
         covariate_value  = spline(age_mid, time_mid)
         column_name      = f'c_{index}'
         row[column_name] = covariate_value
      #
      # row
      row['weight']   = ''
      row['subgroup'] = 'world'
      row['density']  = 'cen_gaussian'
   #
   # integrand_table
   integrand_set = set()
   for row in data_table :
      integrand_set.add( row['integrand_name'] )
   integrand_table = list()
   for integrand_name in integrand_set :
      row = { 'name' : integrand_name }
      integrand_table.append(row)

   #
   # subgroup_table
   subgroup_table = [{ 'subgroup' : 'world', 'group' : 'world' }]
   #
   # prior_table
   prior_table = copy.copy( input_table['prior'] )
   for row in prior_table :
      row['lower'] = float( row['lower'] )
      row['upper'] = float( row['upper'] )
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
   # age_list, time_list
   age_set   = {min_data_age, max_data_age}
   time_set = {min_data_time, max_data_time}
   for row in input_table['smooth_grid'] :
      row['age']  = float(row['age'])
      row['time'] = float(row['time'])
      age_set.add( row['age'] )
      time_set.add( row['time'] )
   age_list  = list( age_set )
   time_list = list( time_set )
   #
   # smooth_table
   smooth_dict = dict()
   for row in input_table['smooth_grid'] :
      name = row['name']
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
      smooh_dict[name]['age_id'].add( age_id )
      smooh_dict[name]['time_id'].add( time_id )
      if row['const_value'] != '' :
         const_value = float( row['const_value'] )
         smooth_dict[name].set(age, time, const_value)
      else :
         value_prior = row['value_prior']
         dage_prior  = row['dage_prior']
         dtime_prior = row['dtime_prior']
         smooth_dict[name].set(age, time, value_prior, dage_prior, dtime_prior)
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
   dismod_at.create_database(
         file_name         = output_file,
         age_list          = age_list,
         time_list         = age_list,
         integrand_table   = integrand_table,
         node_table        = input_table['node'],
         subgroup_table    = subgroup_table,
         weight_table      = list(),
         covariate_table   = covariate_table,
         avgint_table      = list(),
         data_table        = data_table,
         prior_table       = prior_table,
         smooth_table      = smooth_table,
         nslist_table      = dict(),
         rate_table        = input_table['rate'],
         mulcov_table      = input_table['mulcov'],
         option_table      = option_table,
   )
   #
   return age_grid, time_grid, input_table['covariate']
# ----------------------------------------------------------------------------
# Writes the all node data base.
#
# all_node.db
# this database is created by all_node_database.
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
def all_node_database(fit_dir, age_grid, time_grid, covariate_table) :
   #
   # root_node_table
   root_node_table = dict()
   new          = False
   database     = f'{fit_dir}/root_node.db'
   connection   = dismod_at.create_connection(database, new)
   for name in [ 'mulcov', 'age', 'time' ] :
      root_node_table[name] = dismod_at.get_table_dict(
         connection = connection, tbl_name = name)
   connection.close()
   #
   # root_node_name
   root_node_name = at_cascade.get_parent_node(root_node_database)
   #
   # all_node_database
   all_node_database = f'{fit_dir}/all_node.db'
   #
   # all_node_db
   new = True
   all_node_db = dismod_at.create_connection(output_file, new)
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
      'max_fit'                      : 250,
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
   # split_reference_table
   split_reference_table = [
      { 'split_reference_name' : 'female' , 'split_reference_value' : -0.5 },
      { 'split_reference_name' : 'both'   , 'split_reference_value' :  0.0 },
      { 'split_reference_name' : 'male'   , 'split_reference_value' : +0.5 },
   ]
   #
   # node_split_table
   node_split_table = [ { 'node_name' : root_node_name } ]
   #
   # mulcov_freeze_table
   mulcov_freeze_table = list()
   for mulcov_id in range( len(root_node_table['mulcov']  ) ) :
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
   time_list    = [ row['time'] for row in root_node_table['time'] ]
   age_id_grid  = [ age_list.index(age)  for age in age_grid ]
   time_id_grid = [ time_list.index(age) for time in time_grid ]
   omega_grid = { 'age' : age_id_grid, 'time' : time_id_grid }
   #
   # mtall_data
   # This is set equal to the value of omega and is only used for the
   # omega constraint.
   none_list  = len( age_grid) * len( time_grid ) * [ None ]
   mtall_data = dict()
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
      if node_name not in mtall_data :
         mtall_data[node_name] = len(split_refernece_table) * [ none_list ]
      #
      k = split_reference_id
      i = age_list.index(age)
      j = time_list.index(time)
      assert k in [0, 2]
      mtall_data[node_name][k][i * len( time_grid )  + j] = omega
   for node_name in mtall_data :
      for i in range( len(age_grid) ) :
         for j in range( len(time_grid) ) :
            female = mtall_data[node_name][0][i * len( time_grid ) + j]
            both   = mtall_data[node_name][1][i * len( time_grid ) + j]
            male   = mtall_data[node_name][2][i * len( time_grid ) + j]
            assert female != None and both == None and male != None
            both   = (male + female) / 2.0
            mtall_data[node_name][1][i * len( time_grid ) + j] = both
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
   mtall_data                = mtall_data                ,
   mtspecific_data           = None,
   )

# ----------------------------------------------------------------------------
# BEGIN_FIT
def fit(fit_dir) :
   #
   # fit_goal_set
   fit_goal_set   = set()
   file_name      = f'{fit_dir}/fit_goal.csv'
   fit_goal_table = at_cascade.read_table(file_name)
   for row in fit_goal_table :
      fit_goal_set.add( row['node_name'] )
   #
   # root_node.db
   age_grid, time_grid, covariate_table = root_node_database(fit_dir)
   #
   # all_node.db
   all_node_database(fit_dir, age_grid, time_grid, covariate_table)
   #
   # cascade_root_node
   at_cascade.cascade_root_node(
      all_node_database  = f'{fit_dir}/all_node.db'  ,
      root_node_database = f'{fit_dir}/root_node.db' ,
      fit_goal_set       = fit_goal_set              ,
      no_ode_fit         = True                      ,
      fit_type_list      = [ 'both', 'fixed']        ,
   )
# END_FIT
