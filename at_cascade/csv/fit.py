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

{xrst_begin csv_fit}
{xrst_spell
   avg
   avgint
   bnd
   boolean
   const
   cov
   cpus
   cv
   dage
   dir
   dtime
   ipopt
   iter
   laplace
   meas
   mul
   multiprocessing
   pini
   rho
   sincidence
   std
   sqlite
   truncation
   underbars
   mtexcess
   mtother
   mtwith
   relrisk
   trapezoidal
   eigen
}

Fit a CSV Specified Cascade
###########################

Prototype
*********
{xrst_literal
   # BEGIN_FIT
   # END_FIT
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

option_fit.csv
==============
This csv file has two columns,
one called ``name`` and the other called ``value``.
The rows of this table are documented below by the name column.
If an option name does not appear, the corresponding
default value is used for the option.
The final value for each of the options is reported in the file
:ref:`csv_fit@Output Files@option_fit_out.csv` .
Because each option has a default value,
new option are added in such a way that
previous option_fit.csv files are still valid.

absolute_covariates
-------------------
This is a space separated list of the names of the absolute covariates.
The reference value for an absolute covariate is always zero.
(The reference value for a relative covariate is its average for the
location that is being fit.)
The default value for *absolute_covariates* is the empty string; i.e.,
there are no absolute covariates.


age_avg_split
-------------
This string contains a space separated list of float values
(there is one or more spaces between each float value).
Each float value is age at which to split the integration of both the
ODE and the average of an integrand over an interval.
The default for this value is the empty string; i.e.,
no extra age splitting over the uniformly spaced grid specified by
:ref:`csv_fit@Input Files@option_fit.csv@ode_step_size`.

hold_out_integrand
------------------
This string contains a space separate list of integrand names.
These integrands are held out from all the fits except for the
:ref:`no_ode_fit-name` .
The no_ode_fit is used to initialize the rates.
You can use this option to hold out direct measurements of the
rates that are only intended to help with the initialization
(are not real data).
The following is a list of the rates and corresponding integrand
that is a direct measurement of the rate:

.. csv-table::
   :widths: auto
   :header-rows: 1

   Rate,Integrand
   iota,Sincidence
   rho,remission
   chi,mtexcess

The default value for *hold_out_integrand* is the empty string; i.e.,
all of the data is real data and is included in the fits.

max_abs_effect
--------------
This float option specifies an extra bound on the
absolute value of the covariate multipliers,
except for the measurement noise multipliers.
To be specific, the bound on the covariate multiplier is as large as possible
under the condition

   *max_abs_effect* <= | *mul_bnd* * ( *cov_value* - *cov_ref* ) |

where *mul_bnd* is the non-negative covariate multiplier bound,
*cov_value* is a data table value of the covariate,
and *cov_ref* is the reference value for the covariate.
It is an extra bound because it is in addition to the priors for a
covariate multiplier.
The default value for this option is 2.

max_fit
-------
This integer is the maximum number of data values to fit per integrand.
If for a particular fit an integrand has more than this number of
data values, a subset of this size is randomly selected.
There is an exception to this rule, the three fits for the root node
(corresponding to sex equal to female, both and male)
use twice this number of values per integrand.
This is because the sex covariate multiplier is frozen after the both fit
and the other covariate multipliers are frozen of the female and male fits.
The default value for *max_fit* is 250.

max_num_iter_fixed
------------------
This integer is the maximum number of Ipopt iterations to try before
giving up on fitting the fixed effects.
The default value for *max_num_iter_fixed* is 100.

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

minimum_meas_cv
---------------
This float must be non-negative (greater than or equal zero).
It specifies a lower bound on the standard deviation for each measured data
value as a fraction of the measurement value.
The default value for *minimum_meas_cv* is zero.

ode_step_size
-------------
This float must be positive (greater than zero).
It specifies the step size in age and time to use when solving the ODE.
It is also used as the step size for approximating average integrands
over age-time intervals.
The smaller *ode_step_size*, the more computation is required to
approximation the ODE solution and the average integrands.
Finer resolution for specific ages can be achieved using the
:ref:`csv_fit@Input Files@option_fit.csv@age_avg_split` option.
The default value for this option is 10.0.

quasi_fixed
-----------
If this boolean option is true,
a quasi-Newton method is used to optimize the fixed effects.
Otherwise a Newton method is used
The Newton method uses second derivatives of the objective
and hence requires more work per iteration but it can often attain
much more accuracy in the final solution.
The default value *quasi_fixed* is true.

random_seed
-----------
This integer is used to seed the random number generator.
The default value for this option is
{xrst_code py}
   random_seed = int( time.time() )
{xrst_code}

ode_method
----------
This default for *ode_method* is ``iota_pos_rho_zero`` (see below).

no_ode
......
The *ode_method* value does not matter for the following integrands:
``Sincidence`` ,
``remission`` ,
``mtexcess`` ,
``mtother`` ,
``mtwith`` ,
``relrisk`` ,
``mulcov_`` *mulcov_id* .
If all of your integrands are in the set above, you can use
``no_ode`` as the *ode_method* and avoid having to worry about
constraining certain rates to be positive or zero.

trapezoidal
...........
If *ode_method* is ``trapezoidal`` ,
a trapezoidal method is used to approximation the ODE solution.
Like ``no_ode``, you do not have to worry about constraining
certain rates to be positive or zero when using the trapezoidal method.

iota_zero_rho_zero
..................
If *ode_method* is ``iota_zero_rho_zero`` ,
the smoothing for
*iota* and *rho* must always have lower and upper limit zero.
In this case an eigen vector method is used to approximate the ODE solution.

iota_pos_rho_zero
.................
If *ode_method* is ``iota_pos_rho_zero`` ,
the smoothing for
*iota* must always have lower limit greater than zero and for
*rho* lower and upper limit zero.
In this case an eigen vector method is used to approximate the ODE solution.

iota_zero_rho_pos
.................
If *ode_method* is ``iota_zero_rho_pos`` ,
the smoothing for
*rho* must always have lower limit greater than zero and for
*iota* lower and upper limit zero.
In this case an eigen vector method is used to approximate the ODE solution.

iota_pos_rho_pos
................
If *ode_method* is `iota_zero_rho_pos`` ,
the smoothing for
*iota* and *rho*
must always have lower limit greater than zero.
In this case an eigen vector method is used to approximate the ODE solution.

refit_split
-----------
#. If this boolean is true,
   there is a  female, male, and both fit at the root level.
   The both fit is used for the female and male priors.
   The female and male fits are used for the priors below the root level.
#. If *refit_split* is false,
   There is no female or male fit at the root level and
   the both fit is used for the priors below the root level.
#. The default value for this option is true.

Multiplier Freeze
.................
If *refit_split* is true,
the covariate multipliers are frozen after the sex split; i.e.,
after the separate female, male fits at the root level.
If *refit_split* is false,
the covariate multipliers are frozen after the both fit at the root level.

root_node_name
--------------
This string is the name of the root node.
The default for *root_node_name* is the top root of the entire node tree.
Only the root node and its descendents will be fit.

shared_memory_prefix
--------------------
This string is used added to the front of the name of the shared
memory objects used to run the cascade in parallel.
No two cascades can run at the same time with the same shared memory prefix.
If a cascade does not terminate cleanly, you may have to clear the
shared memory before you can run it again; see :ref:`clear_shared-name` .
The default value for this option is your user name ($USER) with spaces
replaced by underbars.
If the USER environment variable is not defined,
the value ``none`` is used for this default.

child_prior_std_factor
----------------------
This factor multiplies the parent fit posterior standard deviation for the
value priors in the during a child fit.
If it is greater (less) than one, the child priors are larger (smaller)
than indicated by the posterior corresponding to the parent fit.
The default value for this option is 2.0.

tolerance_fixed
---------------
is the tolerance for convergence of the fixed effects optimization problem.
This is relative to one and its default value is 1e-4.

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
and stored in :ref:`csv_predict@Output Files@fit_predict.csv` .

integrand_name
--------------
This string is the name of one of the prediction integrands.
You can use the integrand name ``mulcov_0`` , ``mulcov_1`` , ...
which corresponds to the first , second , ...
covariate multiplier in the mulcov.csv file.


{xrst_comment ---------------------------------------------------------------}

prior.csv
=========
This csv file has the following columns:

name
----
is a string contain the name of this prior.
No two priors can have the same name.

density
-------
is one of the following strings:
uniform,
gaussian, cen_gaussian, log_gaussian
laplace, cen_laplace, log_laplace.
(Only these densities are included, so far, so that we do not have to
worry about the degrees of freedom.)

mean
----
is a float containing the mean for the density
for this prior (before truncation).
If density is uniform, this value is only used for starting
and scaling the optimization.
This column must appear and its value cannot be empty.

std
---
is a float containing the standard deviation for the density
for this prior (before truncation).
If density is uniform, this value is not used and can be empty.
If all the densities are uniform, this column is optional.

eta
---
is a float specifying the offset for
the log_gaussian, and log_laplace densities.
If the density is not log_gaussian or log_laplace,
this value is not used and can be empty.
If none of the densities are log_gaussian or log_laplace,
this column is optional.

lower
-----
is a float containing the lower limit for the truncated density
for this prior.
This column is optional,
if it does not appear or its value is empty, there is no lower bound.

upper
-----
is a float containing the upper limit for the truncated density
for this prior.
This column is optional,
if it does not appear or its value is empty, there is no upper bound.

{xrst_comment ---------------------------------------------------------------}

parent_rate.csv
===============
This file specifies the prior for the root node parent rates.
These are no effect rates; i.e., no random or covariate effects are
included in these rates.
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
Either *value_prior* or *const_value* must be non-empty but not both.

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
This prior cannot be censored.

const_value
-----------
is a float specifying a constant value for this grid point or the empty string.
This is equivalent to the upper and lower limits being equal to this value.
Either *const_value* or *value_prior* must be non-empty but not both.

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
The covariate
``one`` is an absolute covariate that is always equal to one and
``sex`` is the splitting covariate and has the following values:
{xrst_code py}'''
sex_name2value = { 'female' : -0.5, 'both' : 0.0, 'male' : 0.5 }
'''{xrst_code}
All the other covariates are specified by
:ref:`csv_fit@Input Files@covariate.csv`.
If one of these covariates appears in the
:ref:`csv_fit@Input Files@option_fit.csv@absolute_covariates` list it is an
absolute covariate.
The other covariates in covariate.csv are
:ref:`relative covariates<glossary@Relative Covariate>` .
For relative covariates,
the average of the covariate
(for the current node and sex being fit)
is subtracted before it is multiplied by a multiplier.

type
----
This string is rate_value, meas_value, or meas_noise.

rate_value
..........
The multiplier times the covariate affects the rate
in the effected column; i.e.
the exponential of the product multiplies the rate.

meas_value
..........
The multiplier times the covariate affects the model for the integrand
in the effected column; i.e.
the exponential of the product multiplies the model for the integrand.

meas_noise
..........
The multiplier times the covariate affects the model for the
measurement noise for the integrand in the effected column.
To be more specific, the product is added to the standard deviation for
measurements for the integrand.

effected
--------
is the name of the integrand or rate affected by this multiplier;
see type above.

value_prior
-----------
is a string containing the name of the value prior
for this covariate multiplier.
Note that the covariate multipliers are constant in age and time
(this is a limitation of the csv_fit).
Either *value_prior* or *const_value* must be non-empty but not both.

const_value
-----------
is a float specifying a constant value for this grid point or the empty string.
This is equivalent to the upper and lower limits being equal to this value.
Either *value_prior* or *const_value* must be non-empty but not both.

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
This string is a dismod_at integrand name; e.g. ``Sincidence``.

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
All the data points are modeled using a censored Gaussian distribution.
The standard deviation is before the censoring.

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

dismod.db
=========
1. There is a subdirectory of the :ref:csv_fit@`fit_dir` with the
   name of the root node. The ``dismod.db`` file in this directory is
   the `dismod_at_database`_ corresponding to the fit and predictions for
   the root node fit for both sexes.
2. The root node directory has a ``female`` and ``male`` subdirectory.
   These directories contain ``dismod.db`` database for
   the root node fit of the corresponding sex.
3. For each node between the root node and the
   :ref:`fit_goal nodes <csv_fit@Input Files@fit_goal.csv>` ,
   and for the ``female`` and ``male`` sex, there is a directory.
   This is directly below the directory for its parent node and same sex.
   It contains the ``dismod.db`` data base for the corresponding fit.

.. _dismod_at_database: https://bradbell.github.io/dismod_at/doc/database.htm

option_fit_out.csv
==================
This is a copy of :ref:`csv_fit@Input Files@option_fit.csv` with the default
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
# Sets global global_option_value to dict representation of option_fit.csv
#
# fit_dir
# is the directory where the input csv files are located.
#
# option_table :
# is the list of dict corresponding to option_fit.csv
#
# top_node_name
# is the name of the top node in the node tree
#
# option_fit_out.csv
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
      'absolute_covariates'   : (str,   None)               ,
      'age_avg_split'         : (str,   None)               ,
      'hold_out_integrand'    : (str,   None)               ,
      'max_abs_effect'        : (float, 2.0)                ,
      'max_fit'               : (int,   250)                ,
      'max_num_iter_fixed'    : (int,   100)                ,
      'max_number_cpu'        : (int,   max_number_cpu)     ,
      'minimum_meas_cv'       : (float, 0.0)                ,
      'ode_method'            : (str,   'iota_pos_rho_zero'),
      'ode_step_size'         : (float, 10.0)               ,
      'quasi_fixed'           : (bool,  'true' )            ,
      'random_seed'           : (int ,  random_seed )       ,
      'refit_split'           : (bool,  'true' )            ,
      'root_node_name'        : (str,   top_node_name)      ,
      'tolerance_fixed'       : (float, 1e-4)               ,
      'shared_memory_prefix'  : (str,   user)               ,
      'child_prior_std_factor': (float,  2.0)               ,
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
         msg  = f'csv_fit: Error: line {line_number} in option_fit.csv\n'
         msg += f'the name {name} appears twice in this table'
         assert False, msg
      if not name in option_default :
         msg  = f'csv_fit: Error: line {line_number} in option_fit.csv\n'
         msg += f'{name} is not a valid option name'
         assert False, msg
      (option_type, defualt) = option_default[name]
      value                  = row['value']
      if value == '' :
         option_value[name] = None
      elif option_type == bool :
         if value not in [ 'true', 'false' ] :
            msg  = f'csv_fit: Error: line {line_number} in option_fit.csv\n'
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
   # option_fit_out.csv
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
   file_name = f'{fit_dir}/option_fit_out.csv'
   at_cascade.csv.write_table(file_name, table)
   #
   assert type(global_option_value) == dict
# ----------------------------------------------------------------------------
# Converts smoothing priors on a grid to a prior function
#
# set:      set the function value at one of the grid points
# __call__: get the function value at one of the grid points
#
class smoothing_function :
   def __init__(self, name) :
      assert type(name) == str
      self.name  = name
      self.value = dict()
   def set(self, age, time, value_prior, dage_prior, dtime_prior) :
      assert type(age)         == float
      assert type(time)        == float
      assert type(value_prior) == str or type(value_prior) == float
      assert type(dage_prior)  == str or dage_prior  == None
      assert type(dtime_prior) == str or dtime_prior == None
      self.value[ (age, time) ] = (value_prior, dage_prior, dtime_prior)
   def __call__(self, age, time) :
      if (age, time) not in self.value :
         msg = f'The grid for smoothing {self.name} is not rectangular'
         assert False, msg
      return self.value[ (age, time) ]
# ----------------------------------------------------------------------------
# Converts weighting on a grid to a function
#
# set:      set the function value at one of the grid points
# __call__: get the function value at one of the grid points
#
class weighting_function :
   def __init__(self, index) :
      assert type(index) == int
      self.index  = index
      self.value  = dict()
   def set(self, age, time, weight) :
      assert type(age)         == float
      assert type(time)        == float
      assert type(weight)      == float
      self.value[ (age, time) ] = weight
   def __call__(self, age, time) :
      if (age, time) not in self.value :
         msg = f'The grid for weighting {self.name} is not rectangular'
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
# global_option_value
# This routine assues that global_option_value has been set.
#
# age_grid, time_grid, covariate_table =
def create_root_node_database(fit_dir) :
   assert type(fit_dir) == str
   #
   # name_rate2integrand
   name_rate2integrand = {
      'pini':   'prevalence',
      'iota':   'Sincidence',
      'rho':    'remission',
      'chi':    'mtexcess',
   }
   #
   # output_file
   output_file = f'{fit_dir}/root_node.db'
   #
   # input_table
   input_table = dict()
   input_list = [
      'node',
      'covariate',
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
      at_cascade.csv.check_table(file_name, input_table[name])
   print('begin creating root node database' )
   #
   # covariate_table
   # This is different from dismod_at_covariate table created below
   covariate_table = input_table['covariate']
   #
   # node_set
   node_set       = set()
   for row in input_table['node'] :
      node_name   = row['node_name']
      node_set.add( node_name )
   #
   # root_node_name, random_seed
   root_node_name = global_option_value['root_node_name']
   random_seed    = global_option_value['random_seed']
   #
   # root_covariate_ref
   root_covariate_ref = at_cascade.csv.covariate_avg(
      covariate_table, root_node_name
   )
   #
   # covariate_list
   covariate_list = list( root_covariate_ref.keys() )
   #
   # root_covariate_ref
   absolute_covariates = global_option_value['absolute_covariates']
   if absolute_covariates != None :
      for covariate_name in absolute_covariates.split() :
         if covariate_name not in covariate_list :
            msg  = f'{covariate_name} is in option_fit absolute_covariates '
            msg += 'but it is not in covariate.csv'
            assert False, msg
         root_covariate_ref[covariate_name] = 0.0
   #
   # forbidden_covariate
   forbidden_covariate = set( input_table['data_in'][0].keys() )
   forbidden_covariate.add( "one" )
   for covariate_name in covariate_list :
      if covariate_name in forbidden_covariate :
         msg  = f'cannot use the covariate name {covariate_name}\n'
         msg += 'because it is "one" or a column in the data_in.csv file'
         assert False, msg
   #
   # dismod_at_covariate_table
   dismod_at_covariate_table = [
      { 'name': 'sex', 'reference': 0.0, 'max_difference' : 0.5 }  ,
      { 'name': 'one', 'reference': 0.0, 'max_difference' : None } ,
   ]
   for covariate_name in covariate_list :
      dismod_at_covariate_table.append({
         'name':            covariate_name,
         'reference':       root_covariate_ref[covariate_name],
         'max_difference' : None
      })
   #
   # option_table
   age_avg_split      = global_option_value['age_avg_split']
   hold_out_integrand = global_option_value['hold_out_integrand']
   max_num_iter_fixed = global_option_value['max_num_iter_fixed']
   ode_step_size      = global_option_value['ode_step_size']
   tolerance_fixed    = global_option_value['tolerance_fixed']
   minimum_meas_cv    = global_option_value['minimum_meas_cv']
   ode_method         = global_option_value['ode_method']
   #
   if global_option_value['quasi_fixed'] :
      quasi_fixed = 'true'
   else :
      quasi_fixed = 'false'
   #
   if len(covariate_list) == 0 :
      splitting_covariate = None
   else :
      splitting_covariate = 'sex'
   option_table = [
      { 'name' : 'age_avg_split',       'value' : age_avg_split             },
      { 'name' : 'hold_out_integrand',  'value' : hold_out_integrand        },
      { 'name' : 'max_num_iter_fixed',  'value' : str( max_num_iter_fixed ) },
      { 'name' : 'ode_step_size',       'value' : str( ode_step_size)       },
      { 'name' : 'parent_node_name',    'value' : root_node_name            },
      { 'name' : 'print_level_fixed',   'value' : '5'                       },
      { 'name' : 'random_seed',         'value' : str( random_seed )        },
      { 'name' : 'tolerance_fixed',     'value' : str( tolerance_fixed)     },
      { 'name' : 'meas_noise_effect',   'value' : 'add_std_scale_none'      },
      { 'name' : 'quasi_fixed',         'value' : quasi_fixed               },
      { 'name' : 'splitting_covariate', 'value' : splitting_covariate       },
      { 'name' : 'rate_case'          , 'value' : ode_method                },
   ]
   #
   # spline_cov
   age_grid, time_grid, spline_cov = at_cascade.csv.covariate_spline(
      covariate_table, node_set
   )
   #
   # data_table
   data_table     = input_table['data_in']
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
      for index, covariate_name in enumerate( root_covariate_ref.keys() ) :
         spline              = spline_cov[node_name][sex][covariate_name]
         covariate_value     = spline(age_mid, time_mid)
         row[covariate_name] = covariate_value
      #
      # row
      row['node']       = row['node_name']
      row['integrand']  = row['integrand_name']
      row['age_lower']  = age_lower
      row['age_upper']  = age_lower
      row['time_lower'] = time_lower
      row['time_upper'] = time_lower
      row['weight']     = ''
      row['subgroup']   = 'world'
      row['density']    = 'cen_gaussian'
      row['sex']        = sex_name2value[sex]
      row['one']        = '1.0'
   #
   # integrand_table
   integrand_set = set()
   for row in data_table :
      integrand_set.add( row['integrand_name'] )
   for row in input_table['predict_integrand'] :
      integrand_set.add( row['integrand_name'] )
   for rate_name in name_rate2integrand :
      integrand_set.add( name_rate2integrand[rate_name] )
   integrand_table = list()
   for integrand in integrand_set :
      row = { 'name' : integrand , 'minimum_meas_cv'  : minimum_meas_cv }
      integrand_table.append(row)
   for mulcov_id in range( len( input_table['mulcov'] ) ) :
      integrand_name = f'mulcov_{mulcov_id}'
      if integrand_name not in integrand_set :
         integrand_table.append( { 'name': integrand_name } )
   #
   # subgroup_table
   subgroup_table = [{ 'subgroup' : 'world', 'group' : 'world' }]
   #
   # prior_table
   prior_table = copy.copy( input_table['prior'] )
   for row in prior_table :
      for key in [ 'lower', 'upper', 'std', 'eta' ] :
         if key in row :
            if row[key] != None :
               row[key] = float( row[key] )
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
   # node_table, node_set
   node_table = list()
   for row_in in input_table['node'] :
      row_out = { 'name' : row_in['node_name'] }
      if row_in['parent_name'] == None :
         row_out['parent'] = ''
      else :
         row_out['parent'] = row_in['parent_name']
      node_table.append( row_out )
   #
   # weight_dict, weight_index
   weight_dict    = dict()
   weight_index   = 0
   check_node_set = set()
   check_sex_set  = set()
   for row in covariate_table :
      age  = float( row['age'] )
      time = float( row['time'] )
      #
      node_name = row['node_name']
      sex_name  = row['sex']
      #
      check_node_set.add(node_name)
      check_sex_set.add(sex_name)
      #
      for covariate_name in covariate_list :
         key = (node_name, sex_name, covariate_name)
         if key not in weight_dict :
            fun           = weighting_function(weight_index)
            weight_index += 1
            weight_dict[key] = fun
         weight = float( row[covariate_name] )
         weight_dict[key].set(age, time, weight)
   if check_sex_set != { 'female', 'male' } :
      print(check_sex_set)
      msg  = 'The sexes above are in covariate.csv '
      msg += 'but it should be female and male'
      assert False, msg
   if len(node_set - check_node_set) > 0 :
      difference = node_set - check_node_set
      print(difference)
      msg = 'The nodes above are in node.csv but not in covariate.csv'
      assert False, msg
   if len(check_node_set - node_set) > 0 :
      difference = check_node_set - node_set
      print(difference)
      msg = 'The nodes above are in covariate.csv but not in node.csv'
   #
   # weight_dict
   for node_name in node_set :
      for covariate_name in covariate_list :
         key        = (node_name, 'female', covariate_name)
         fun_female = weight_dict[key]
         key        = (node_name, 'male', covariate_name)
         fun_male   = weight_dict[key]
         #
         fun_both      = weighting_function(weight_index)
         weight_index += 1
         for age  in age_grid :
            for time in time_grid :
               weight = ( fun_female(age, time) + fun_male(age, time) ) / 2.0
               fun_both.set(age, time, weight)
         key              = (node_name, 'both', covariate_name)
         weight_dict[key] = fun_both
   #
   # weight_table
   weight_table = list()
   age_id_list  = [ age_list.index(age) for age in age_grid ]
   time_id_list = [ time_list.index(time) for time in time_grid ]
   for key in weight_dict :
      fun   = weight_dict[key]
      index = fun.index
      name  = f'weight_{index}'
      row = {
         'name'     : f'weight_{index}'   ,
         'age_id'   : age_id_list         ,
         'time_id'  : time_id_list        ,
         'fun'      : fun                 ,
      }
      weight_table.append(row)
   #
   # rate_eff_cov_table
   rate_eff_cov_table = list()
   for key in weight_dict :
      #
      fun         = weight_dict[key]
      index       = fun.index
      weight_name = f'weight_{index}'
      #
      (node_name, sex_name, covariate_name) = key
      sex_value = sex_name2value[sex_name]
      #
      row = {
         'node_name'      : node_name       ,
         'covariate_name' : covariate_name  ,
         'split_value'    : sex_value       ,
         'weight_name'    : weight_name     ,
      }
      rate_eff_cov_table.append(row)
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
      value_prior = row['value_prior']
      dage_prior  = row['dage_prior']
      dtime_prior = row['dtime_prior']
      if row['const_value'] != None :
         if row['value_prior'] != None :
            rate_name = row['rate_name']
            msg  = f'parent_rate.csv: '
            msg += f'rate = {rate_name}, age = {age}, time = {time}\n'
            msg += 'both const_value and value_prior are non-empty'
            assert False, msg
         const_value = float( row['const_value'] )
         smooth_dict[name]['fun'].set(
            age, time, const_value, dage_prior, dtime_prior
         )
      else :
         if row['value_prior'] == None :
            rate_name = row['rate_name']
            msg  = f'parent_rate.csv: '
            msg += f'rate = {rate_name}, age = {age}, time = {time}\n'
            msg += 'both const_value and value_prior are empty'
            assert False, msg
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
      if row['const_value'] != None :
         value_prior = float( row['const_value'] )
      else :
         value_prior = row['value_prior']
         if value_prior == None :
            line = i_row + 2
            msg  = f'In line {line} of mulcov.csv\n'
            msg += 'const_value and value_prior are both empty'
            assert False, msg
      smooth_dict[name]['fun'].set(
         age         = age_list[0]            ,
         time        = time_list[0]           ,
         value_prior = value_prior            ,
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
   # mulcov_table
   mulcov_table = input_table['mulcov']
   for (i_row, row) in enumerate(mulcov_table) :
      del row['value_prior']
      del row['const_value']
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
         file_name           = output_file,
         age_list            = age_list,
         time_list           = time_list,
         integrand_table     = integrand_table,
         node_table          = node_table,
         subgroup_table      = subgroup_table,
         weight_table        = weight_table,
         covariate_table     = dismod_at_covariate_table,
         avgint_table        = list(),
         data_table          = data_table,
         prior_table         = prior_table,
         smooth_table        = smooth_table,
         rate_table          = rate_table,
         mulcov_table        = mulcov_table,
         option_table        = option_table,
         rate_eff_cov_table  = rate_eff_cov_table,
   )
   #
   assert type(age_grid) == list
   assert type(time_grid) == list
   assert type(covariate_table) == list
   assert type( covariate_table[0] ) == dict
   return age_grid, time_grid, covariate_table
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
# global_option_value
# This routine assues that global_option_value has been set.
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
   # all_option
   child_prior_std_factor = global_option_value['child_prior_std_factor']
   shared_memory_prefix   = global_option_value['shared_memory_prefix']
   absolute_covariates    = global_option_value['absolute_covariates']
   if absolute_covariates == None :
      absolute_covariates = 'one'
   else :
      absolute_covariates += ' one'
   if global_option_value['refit_split'] :
      refit_split = 'true'
   else :
      refit_split = 'false'
   all_option = {
      'absolute_covariates'          : absolute_covariates ,
      'balance_fit'                  : 'sex -0.5 +0.5' ,
      'max_abs_effect'               : global_option_value['max_abs_effect'],
      'max_fit'                      : global_option_value['max_fit'],
      'max_number_cpu'               : global_option_value['max_number_cpu'],
      'number_sample'                : '20',
      'perturb_optimization_scale'   : 0.2,
      'perturb_optimization_start'   : 0.2,
      'shared_memory_prefix'         : shared_memory_prefix,
      'refit_split'                  : refit_split,
      'result_dir'                   : fit_dir,
      'root_node_name'               : root_node_name,
      'split_covariate_name'         : 'sex',
      'root_split_reference_name'    : 'both',
      'shift_prior_std_factor'       : child_prior_std_factor,
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
         if global_option_value['refit_split'] :
            split_reference_id_list = [ 0 , 2 ]
         else :
            split_reference_id_list = [ 0 , 1, 2 ]
         for split_reference_id in split_reference_id_list :
            # split_reference_id 0 for female, 1 for both, 2 for male
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
            both   = (female + male) / 2.0
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
# BEGIN_FIT
# at_cascadde.csv.predict(fit_dir)
def fit(fit_dir) :
   assert type(fit_dir) == str
# END_FIT
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
   option_table = at_cascade.csv.read_table(f'{fit_dir}/option_fit.csv')
   set_global_option_value(
      fit_dir, option_table, top_node_name
   )
   #
   root_node_name = global_option_value['root_node_name']
   file_name      = f'{fit_dir}/{root_node_name}'
   if os.path.exists( file_name ) :
      msg  = f'{file_name} already exists.\n'
      msg == 'you must remove it before running this csv fit'
      assert False, msg
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
