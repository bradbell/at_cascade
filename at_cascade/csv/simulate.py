# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
import time
import math
import random
import numpy
import dismod_at
import at_cascade
"""
{xrst_begin csv_simulate}
{xrst_spell
   bilinear
   cv
   dir
   integrator
   interpolate
   meas
   pini
   rho
   sim
   sincidence
   std
}

Simulate A Cascade Data Set
###########################

Prototype
*********
{xrst_literal
   # BEGIN_SIMULATE
   # END_SIMULATE
}

sim_dir
*******
This string is the directory name where the csv files
are located.

Example
*******
:ref:`csv_simulate_xam`


Input Files
***********

option.csv
==========
This csv file has two columns,
one called ``name`` and the other called ``value``.
The rows are documented below by the name column:

absolute_tolerance
------------------
This float is the absolute error tolerance for the integrator.

float_precision
---------------
This integer is the number of decimal digits of precision to
include for float values in the output csv files.

integrand_step_size
-------------------
This float is the step size in age and time used to approximate
integrand averages from age_lower to age_upper
and time_lower to time_upper (in data_sim.csv).
It must be greater than zero.

random_seed
-----------
This integer is used to seed the random number generator.

std_random_effects
------------------
This float is the standard deviation of the random effects.
All fo the effects are in log of rate space, so this standard deviation
is also in log of rate space.

-----------------------------------------------------------------------------

node.csv
========
This csv file defines the node tree.
It has the columns documented below.

node_name
---------
This string is a name describing the node in a way that is easy for a human to
remember. It be unique for each row.

parent_name
-----------
This string is the node name corresponding to the parent of this node.
The root node of the tree has an empty entry for this column.
If a node is a parent, it must have at least two children.
This avoids fitting the same location twice as one goes from parent
to child nodes.

-----------------------------------------------------------------------------

covariate.csv
=============
This csv file specifies the value of omega and the covariates.
For each node_name it has a rectangular grid in age and time.
In addition, the rectangular grid is the same for nodes.

node_name
---------
This string identifies the node, in node.csv, corresponding to this row.

sex
---
This identifies which sex this row corresponds to.
The sex values ``male`` and ``female`` must appear in this table.
The sex value ``both`` does not appear.

age
---
This float is the age, in years,  corresponding to this row.

time
----
This float is the time, in years, corresponding to this row.

omega
-----
This float is the value of omega (other cause mortality) for this row.
Often other cause mortality is approximated by all cause mortality.
Omega is a rate, not a covariate.
The values in this column do not matter if
omega does not appear in :ref:`csv_simulate@Input Files@no_effect_rate.csv`,

covariate_name
--------------
For each covariate that we are including in this simulation,
there is a column in the header that contains the *covariate_name*.
The other values in that column are float representations of the covariate.
All of these covariates are
:ref:`glossary@Relative Covariate`; see
:ref:`csv_module@Notation@Covariates`.

-----------------------------------------------------------------------------

no_effect_rate.csv
==================
This csv file specifies the grid points at which each rate is modeled
during a simulation. For each rate_name it has a
:ref:`csv_module@Notation@Rectangular Grid` in age and time.
These are no-effect rates; i.e., the rates without
the random and covariate effects.
Covariate multipliers that are constrained to zero during the fitting
can be used to get variation between nodes in the
no-effect rates corresponding to the fit.

rate_name
---------
This string is ``iota``, ``rho``, ``chi``, or ``pini`` and specifies the rate.
If one of these rates does not appear, it is modeled as always zero.
Other cause mortality ``omega`` is specified in
:ref:`csv_simulate@Input Files@covariate.csv` .

age
---
This float is the age, in years,  corresponding to this row.

time
----
This float is the time, in years, corresponding to this row.

rate_truth
----------
This float is the no-effect rate value for all the nodes.
It is used to simulate the data.
As mentioned, above knocking out covariate multipliers can be
used to get variation in the no-effect rates that correspond to the fit.
If *rate_name* is ``pini``, *rate_truth*  should be constant w.r.t *age*
(because it is prevalence at age zero).

-----------------------------------------------------------------------------

multiplier_sim.csv
==================
This csv file provides information about the covariate multipliers.
Each row of this file, except the header row, corresponds to a
different multiplier. The multipliers are constant in age and time.

multiplier_id
-------------
is an :ref:`csv_module@Notation@Index Column` for multiplier_sim.csv.

rate_name
---------
This string is ``iota``, ``rho``, ``chi``, or ``pini`` and specifies
which rate this covariate multiplier is affecting.

covariate_or_sex
----------------
If this is ``sex`` it specifies that this multiplier multiples
the sex values where
{xrst_code py}"""
sex_covariate_value = { 'female' : -0.5,  'both' : 0.0, 'male' : +0.5 }
"""{xrst_code}
female = -0.5, male = +0.5, and both = 0.0.
Otherwise this is one of the covariate names in the covariate.csv file
and specifies which covariate value is being multiplied.

multiplier_truth
----------------
This is the value of the covariate multiplier used to simulate the data.


-----------------------------------------------------------------------------

simulate.csv
============
This csv file specifies the simulated data set
with each row corresponding to one data point.

simulate_id
-----------
is an :ref:`csv_module@Notation@Index Column` for simulate.csv.

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

percent_cv
----------
This float is the coefficient of variation as a percent of the corresponding
average integrand; i.e., the model for the integrand
without any measurement noise.
The noise will be generated with a normal distribution
that has mean equal to the average integrand and
standard deviation equal to the mean times percent_cv / 100.
If the resulting measurement value would be less than zero,
the value zero is be used; i.e.,
a censored normal is used to simulate the data.

------------------------------------------------------------------------------

Output Files
************

random_effect.csv
=================
This file reports the random effect for each node and rate.
It has a :ref:`csv_module@Notation@Rectangular Grid` in the columns
``node_name`` , ``sex`` and ``rate_name`` .

node_name
---------
This string identifies the row in :ref:`csv_simulate@Input Files@node.csv`
that this row corresponds to.

sex
---
This identifies which sex the random effect corresponds to.
The sex values ``male`` and ``female`` will appear.

rate_name
---------
This is a string and is one of the
For each :ref:`csv_simulate@Input Files@no_effect_rate.csv@rate_name`
in the no_effect rate table,
All of the rates in the no_effect rate table are present in this file.

random_effect
-------------
This float value is the random effect
for the specified node, sex, and rate.

Discussion
----------
1. For a given parent node, sex, and rate,
   the sum of the random effects with respect to the child nodes is zero.
2. All the random effects for the root node are set to zero
   (the root node does not have a parent node).

-----------------------------------------------------------------------------

data_sim.csv
============
This contains the simulated data.
It is created during a simulate command
and has the following columns:

simulate_id
-----------
This integer identifies the row in the simulate.csv
corresponding to this row in data_sim.csv.
This is an :ref:`csv_module@Notation@Index Column`
for simulate.csv and data_sim.csv.

meas_mean
---------
This float is the mean value for the measurement.
This is the model value without any measurement noise.

meas_value
----------
This float is the simulated measured value.

meas_std
--------
This float is the measurement standard deviation for the simulated
data point. This standard deviation is before censoring.

covariate_name
--------------
For each :ref:`csv_simulate@Input Files@covariate.csv@covariate_name`
there is a column with this name in simulate.csv.
The values in these columns are floats
corresponding to the covariate value at the mid point of the ages and time
intervals for this data point. This value is obtained using
bilinear interpolation of the covariate values in covariate.csv.
The interpolate is extended as constant in age (time) for points
outside the age rage (time range) in the covariate.csv file.

{xrst_end csv_simulate}
"""
# -----------------------------------------------------------------------------
# Returns a dictionary verison of option_table.
#
# option_value[name] :
# is the option value corresponding the the specified option name.
# Here name is a string and value
# has been coverted to its corresponding type; e.g.
# option_value['random_seed'] is an ``int``.
#
# Side Effects:
# The random.seed fucntion is called with the seed value
# option_value['random_seed']
#
# option_value =
def option_table2dict(option_table) :
   #
   # option_value
   option_value = dict()
   option_type  = {
      'absolute_tolerance'     : float   ,
      'float_precision'        : int     ,
      'integrand_step_size'    : float   ,
      'random_seed'            : int     ,
      'std_random_effects'     : float   ,
   }
   line_number = 0
   for row in option_table :
      line_number += 1
      name         = row['name']
      if name in option_value :
         msg  = f'csv_simulate: Error: line {line_number} in option.csv\n'
         msg += f'the name {name} appears twice in this table'
         assert False, msg
      if not name in option_type :
         msg  = f'csv_simulate: Error: line {line_number} in option.csv\n'
         msg += f'{name} is not a valid option name'
         assert False, msg
      value        = option_type[name]( row['value'] )
      option_value[name] = value
   #
   # option_value
   for name in option_type :
      if not name in option_value :
         msg  = 'csv_simulate: Error: in option.csv\n'
         msg += f'the name {name} does not apper'
         assert False, msg
   #
   # options that must be greater than zero
   for name in [
      'absolute_tolerance',
      'integrand_step_size',
      'float_precision',
      'std_random_effects',
   ] :
      value = option_value[name]
      if value <= 0 :
         msg  = 'csv_simulate: Error: in option.csv\n'
         msg += f'{name} = {value} <= 0'
         assert False, msg
      option_value[name] = value
   #
   # random_seed
   random.seed( option_value['random_seed'] )
   #
   return option_value
# ----------------------------------------------------------------------------
# parent_node_dict[node_name]:
# The is the name of the node that is the parent of node_node.
# The keys and values in this dictionary are strings.
#
# child_list_node[node_name]:
# A ``list`` of nodes that has all the children of node_name
# where node_name is an ``str`` .
#
# parent_node_dict, child_list_node =
def get_parent_node_dict( node_table ) :
   #
   # parent_node_dict, count_children, root_node_name
   line_number = 0
   parent_node_dict  = dict()
   child_list_node   = dict()
   root_node_name    = None
   for row in node_table :
      line_number += 1
      node_name                  = row['node_name']
      parent_name                = row['parent_name']
      child_list_node[node_name] = list()
      if node_name in parent_node_dict :
         msg  = f'csv_simulate: Error: line {line_number} in node.csv\n'
         msg += f'node_name {node_name} appears twice'
         assert False, msg
      parent_node_dict[node_name] = parent_name
      #
      if parent_name == '' :
         if root_node_name != None :
            msg  = f'csv_simulate: Error: line {line_number} in node.csv\n'
            msg += 'one and only one node should have no parent\n'
            msg += 'node {node_name} and {root_node_name} have no parent'
            assert False, msg
         root_node_name = node_name
   if root_node_name == None :
      msg  = f'csv_simulate: Error in node.csv\n'
      msg += 'there is no root node; i.e.,  node with no parent node'
      assert False, msg
   #
   # child_list_node
   line_number    = 0
   for row in node_table :
      line_number += 1
      node_name    = row['node_name']
      parent_name  = row['parent_name']
      if parent_name != '' :
         if parent_name not in child_list_node :
            msg  = f'csv_simulate: Error: line {line_number} in node.csv\n'
            msg += f'parent_name {parent_name} is not a valid node_name'
            assert False, msg
         else :
            child_list_node[parent_name].append(node_name)
   #
   # check number of children
   for parent_name in child_list_node :
      if len( child_list_node[parent_name] ) == 1 :
         msg  = 'csv_simulate: Error in node.csv\n'
         msg += f'the parent_name {parent_name} apprears once and only once'
         assert False, msg
   #
   # check that no node is and ancestor of itself
   for node_name in parent_node_dict :
      ancestor_set = { node_name }
      parent_name  = parent_node_dict[node_name]
      while parent_name != '' :
         if parent_name in ancestor_set :
            msg  = 'csv_simulate: Error in node_table.csv\n'
            msg += f'node {parent_name} is an ancestor of itself'
            assert False, msg
         ancestor_set.add(parent_name)
         parent_name = parent_node_dict[parent_name]
   #
   return parent_node_dict, child_list_node
# ----------------------------------------------------------------------------
# spline = spline_no_effect_rate[rate_name] :
# 1. rate_name is any of the rate names in the no_effect_rate table.
# 2. value = spline(age, time) evaluates the no_effect spline
#    for rate_name at the specified age and time where age, time, value
#    are all floats.
#
# no_effect_rate_table:
# is the table correspnding to no_effect_rate.csv
#
# spline_no_effect_rate =
def get_spline_no_effect_rate(no_effect_rate_table) :
   #
   # age_set, time_set
   rate_row_list   = dict()
   for row in no_effect_rate_table :
      rate_name    = row['rate_name']
      age          = float( row['age'] )
      time         = float( row['time'] )
      rate_truth   = float( row['rate_truth'] )
      #
      if rate_name not in rate_row_list :
         rate_row_list[rate_name] = list()
      rate_row_list[rate_name].append( row )
   #
   # spline_no_effect_rate
   spline_no_effect_rate = dict()
   #
   # rate_name
   for rate_name in rate_row_list :
      #
      # age_grid, time_grid, spline_dict
      age_grid, time_grid, spline_dict = at_cascade.bilinear(
         table  = rate_row_list[rate_name],
         x_name = 'age',
         y_name = 'time',
         z_list = [ 'rate_truth' ]
      )
      #
      if spline_dict == None :
         msg  = 'csv_simulate: Error in no_effect_rate.csv\n'
         msg += 'rate_name = {rate_name}\n'
         msg += 'Expected following rectangular grid:\n'
         msg += f'age_grid  = {age_grid}\n'
         msg += f'time_grid = {time_grid}'
         assert False, msg
      #
      # spline_no_effect_rate
      spline_no_effect_rate[rate_name]= spline_dict['rate_truth']
   #
   return spline_no_effect_rate
# ----------------------------------------------------------------------------
# multiplier_list_rate[rate_name]:
# list of rows in multiplier_sim_table that have the specified rate name
# were rate_name is a string.
#
# multiplier_sim_table:
# is the table corresponding to multiplier_sim.csv.
#
# multiplier_list_rate =
def get_multiplier_list_rate(multiplier_sim_table) :
   #
   # multiplier_list_rate
   multiplier_list_rate = dict()
   for rate_name in [ 'pini', 'iota', 'rho', 'chi' ] :
      multiplier_list_rate[rate_name] = list()
   for row in multiplier_sim_table :
      rate_name = row['rate_name']
      multiplier_list_rate[rate_name].append(row)
   return multiplier_list_rate
# ----------------------------------------------------------------------------
# rate_fun = rate_fun_dict[rate_name] :
# For each of rate_name in spline_no_effect_rate, value = rate_fun(age, time)
# is the value of the corresponding rate included all fo the effects
# where age, time, and value are floats.
#
# parent_node_dict:
# is mapping from each node name to the name of its parent node.
#
# spline_no_effect_rate[rate_name] :
# is a spline that evaluates the specified no_effect rate.
#
# random_effect_node_sex_rate[node_name][sex][rate_name] :
# is the random effect for the specified node, sex, and rate.
# Note that to get the difference from the root node, one has to sum
# the random effect for this node and its ancestors not including the
# root node in the sum.
#
# spline = spline_node_sex_cov[node_name][sex][cov_name] :
# is a function that evaluates value = spline(age, time) where
# node_name is a node name, sex is 'male' or 'female' (not 'both'),
# cov_name is a covariate name or 'sex',
# age, time, and value are floats
#
# root_covariate_avg[covariate_name] :
# is the average, restricted to the root node, of the specified covariate.
#
# multiplier_list_rate[rate_name] :
# is the list of rows, in the multiplier_sim table, that have rate_name
# equal to the specified rate_name.
#
# node_name :
# The node that rate_fun will compute rates for.
#
# sex :
# The sex that rate_fun will compute rates for.
# This can be male, female or both.
#
# rate_fun_dict =
def get_rate_fun_dict(
   parent_node_dict            ,
   spline_no_effect_rate       ,
   random_effect_node_sex_rate ,
   spline_node_sex_cov         ,
   root_covariate_avg          ,
   multiplier_list_rate        ,
   node_name                   ,
   sex                         ,
) :
   assert sex in { 'female', 'male', 'both' }
   # -----------------------------------------------------------------------
   # rate_fun
   def rate_fun(age, time, rate_name) :
      #
      # no_effect_rate
      spline         = spline_no_effect_rate[rate_name]
      no_effect_rate = spline(age, time)
      #
      # effect
      # random effects
      effect         = 0.0
      parent_node    = parent_node_dict[node_name]
      while parent_node != '' :
         effect     += \
            random_effect_node_sex_rate[node_name][sex][rate_name]
         parent_node = parent_node_dict[parent_node]
      #
      # effect
      # covariate and sex effects
      for row in multiplier_list_rate[rate_name] :
         assert row['rate_name'] == rate_name
         #
         covariate_or_sex = row['covariate_or_sex']
         if covariate_or_sex == 'sex' :
            difference = sex_covariate_value[sex]
         else :
            covariate_name = covariate_or_sex
            if sex in [ 'male', 'female' ] :
               spline         = \
                  spline_node_sex_cov[node_name][sex][covariate_name]
               covariate      = spline(age, time)
               reference      = root_covariate_avg[covariate_name]
               difference     = covariate - reference
            else :
               assert sex == 'both'
               spline         = \
                  spline_node_sex_cov[node_name]['female'][covariate_name]
               female         = spline(age, time)
               spline         = \
                  spline_node_sex_cov[node_name]['male'][covariate_name]
               male           = spline(age, time)
               reference      = root_covariate_avg[covariate_name]
               difference     = (female + male) / 2.0  - reference
         effect    += float( row['multiplier_truth'] ) * difference
      #
      # rate
      rate = math.exp(effect) * no_effect_rate
      return rate
   # -----------------------------------------------------------------------
   # omega_fun
   def omega_fun(age, time) :
      if sex in [ 'male', 'female' ] :
         spline = spline_node_sex_cov[node_name][sex]['omega']
         omega  = spline(age, time)
      else :
         assert sex == 'both'
         spline = spline_node_sex_cov[node_name]['female']['omega']
         female = spline(age, time)
         spline = spline_node_sex_cov[node_name]['male']['omega']
         male   = spline(age, time)
         omega  = (female + male) / 2.0
      return omega
   #
   rate_fun_dict = dict()
   rate_fun_dict['omega'] = lambda age, time : omega_fun(age, time)
   #
   # cannot loop over rate name becasue it does not bind on assignment.
   if 'iota' in  spline_no_effect_rate :
      rate_fun_dict['iota'] = \
         lambda age, time : rate_fun(age, time, 'iota')
   if 'rho' in  spline_no_effect_rate :
      rate_fun_dict['rho'] = \
         lambda age, time : rate_fun(age, time, 'rho')
   if 'chi' in  spline_no_effect_rate :
      rate_fun_dict['chi'] = \
         lambda age, time : rate_fun(age, time, 'chi')
   #
   #
   return rate_fun_dict
# ----------------------------------------------------------------------------
# grid['age'] :
# is a list of age point starting at age_lower, ending at age_upper
# and such that the difference between points is less than or equal
# step_size.
#
# grid['time'] :
# is a list of time point starting at time_lower, ending at time_upper
# and such that the difference between points is less than or equal
# step_size.
#
# step_size :
# The maximum allowable distance between grid point.
# This must be grater than zero
#
# grid =
def average_integrand_grid(
   step_size, age_lower, age_upper, time_lower, time_upper
) :
   #
   # age_grid
   if age_lower == age_upper :
      age_grid = [ age_lower ]
   else :
      n_age    = int( (age_upper - age_lower) / step_size) + 1
      dage     = (age_upper - age_lower) / n_age
      age_grid = [ age_lower + i * dage for i in range(n_age+1) ]
   #
   # time_grid
   if time_lower == time_upper :
      time_grid = [ time_lower ]
   else :
      n_time    = int( (time_upper - time_lower) / step_size) + 1
      dtime     = (time_upper - time_lower) / n_time
      time_grid = [ time_lower + i * dtime for i in range(n_time+1) ]
   # grid
   grid = { 'age' : age_grid , 'time' : time_grid }
   #
   return grid
# ----------------------------------------------------------------------------
# random_effect_node_sex_rate[node_name][sex][rate_name] :
# is the simulated random effect for the corresponding node, sex and rate.
# For a given node_name, sex and rate_name, the sum of
#  random_effect_node_sex_rate[child_node][sex][rate_name]
# is zero where child_node ranges over values in child_list_node[node_name]
# All the random effects for the root node are zero
# (prent_node_dict[root_node_name] == '' )
#
#
# std_random_effects:
# is a float specifying the standard deviation of the random effects
#
# rate_name_list:
# is the list of rate_names the the random effects are simulated for
#
# parent_node_dict;
# is the mapping from a node_name to its parent node_name.
#
# child_list_node:
# for each node_name in parent_node_dict this is a list of
# node that have node_name as its parent node.
#
# random_effect_node_sex_rate =
def get_random_effect_node_sex_rate (
   std_random_effects ,
   rate_name_list     ,
   parent_node_dict   ,
   child_list_node    ,
) :
   def recursive_call(
      random_effect_node_sex_rate ,
      node_name                   ,
      sex                         ,
      rate_name                   ,
      std_random_effects          ,
      parent_node_dict            ,
      child_list_node             ,
   ) :
      #
      # child_list
      child_list = child_list_node[node_name]
      #
      # n_children
      n_children = len(child_list)
      if n_children == 0 :
         return None
      assert 1 < n_children
      #
      # factor
      factor  = n_children / (n_children - 1)
      assert type(factor) == float
      factor  = math.sqrt( factor )
      #
      # random_effect_dict, sum_random_effect
      random_effect_dict = dict()
      sum_random_effect  = 0.0
      for child_name in child_list :
         random_effect = random.gauss(0.0, factor * std_random_effects)
         sum_random_effect += random_effect
         random_effect_dict[child_name] = random_effect
      #
      # random_effect_dict
      avg_random_effect = sum_random_effect / n_children
      for child_name in child_list :
         random_effect_dict[child_name] -= avg_random_effect
      #
      # random_effect_node_sex_rate
      for child_name in child_list :
         random_effect_node_sex_rate[child_name][sex][rate_name] = \
            random_effect_dict[child_name]
      #
      # random_effect_node_sex_rate
      for child_name in child_list :
         recursive_call(
            random_effect_node_sex_rate ,
            child_name                  ,
            sex                         ,
            rate_name                   ,
            std_random_effects          ,
            parent_node_dict            ,
            child_list_node             ,
         )
      return None
   #
   # root_node_name
   root_node_name = None
   for node_name in parent_node_dict :
      if parent_node_dict[node_name] == '' :
         root_node_name = node_name
   assert root_node_name != None
   #
   # random_effect_node_sex_rate
   random_effect_node_sex_rate  = dict()
   for node_name in parent_node_dict :
      random_effect_node_sex_rate[node_name] = dict()
      for sex in ['male', 'female'] :
         random_effect_node_sex_rate[node_name][sex] = dict()
   #
   # random_effect_node_sex_rate[root_node_name]
   for sex in [ 'male', 'female' ] :
      for rate_name in rate_name_list :
         random_effect_node_sex_rate[root_node_name][sex][rate_name] = 0.0

   #
   # random_effect_node_sex_rate
   for sex in [ 'male', 'female' ] :
      for rate_name in rate_name_list :
         recursive_call(
            random_effect_node_sex_rate ,
            root_node_name              ,
            sex                         ,
            rate_name                   ,
            std_random_effects          ,
            parent_node_dict            ,
            child_list_node             ,
         )
   #
   return random_effect_node_sex_rate
# ----------------------------------------------------------------------------
# BEGIN_SIMULATE
def simulate(sim_dir) :
   assert type(sim_dir) == str
# END_SIMULATE
   valid_integrand_name = {
      'Sincidence',
      'remission',
      'mtexcess',
      'mtother',
      'mtwith',
      'susceptible',
      'withC',
      'prevalence',
      'Tincidence',
      'mtspecific',
      'mtall',
      'mtstandard',
      'relrisk',
   }
   #
   # input_table
   input_table = dict()
   input_list  = [
      'option',
      'node',
      'covariate',
      'multiplier_sim',
      'no_effect_rate',
      'simulate',
   ]
   print('begin reading csv files')
   for name in input_list :
      file_name         = f'{sim_dir}/{name}.csv'
      input_table[name] = at_cascade.csv.read_table(file_name)
   #
   print('being creating data structures' )
   #
   # option_value
   option_value = option_table2dict(input_table['option'] )
   #
   # parent_node_dict, child_list_node
   parent_node_dict, child_list_node = \
      get_parent_node_dict( input_table['node'] )
   #
   # spline_node_sex_cov
   node_set = set( parent_node_dict.keys() )
   age_grid, time_grid, spline_node_sex_cov = at_cascade.csv.covariate_spline(
      input_table['covariate'], node_set
   )
   #
   # root_node_name
   root_node_name = None
   for node_name in parent_node_dict :
      if parent_node_dict[node_name] == '' :
         if root_node_name != None :
            msg = 'node.csv has more than one node with no parent'
            assert False, msg
         root_node_name = node_name
   if root_node_name == None :
      msg = 'node.csv every node has a parent node; i.e, no root node'
      assert False, msg
   #
   # root_covariate_avg
   root_covariate_avg = at_cascade.csv.covariate_avg(
      input_table['covariate'] , root_node_name
   )
   #
   # covariate_name_list
   covariate_name_list = root_covariate_avg.keys()
   #
   # spline_no_effect_rate
   spline_no_effect_rate = get_spline_no_effect_rate(
      input_table['no_effect_rate']
   )
   #
   # random_effect_node_sex_rate
   std_random_effects  = option_value['std_random_effects']
   rate_name_list      = spline_no_effect_rate.keys()
   random_effect_node_sex_rate = get_random_effect_node_sex_rate(
      std_random_effects ,
      rate_name_list     ,
      parent_node_dict   ,
      child_list_node    ,
   )
   #
   # multiplier_list_rate
   multiplier_list_rate = get_multiplier_list_rate(
      input_table['multiplier_sim']
   )
   #
   # s_last, s_start
   simulate_id = len( input_table['simulate'] )
   print( f'begin simulation: total id = {simulate_id:,}' )
   s_last  = time.time()
   s_start = s_last
   #
   # float_format
   n_digits = str( option_value['float_precision'] )
   float_format = '{0:.' + n_digits + 'g}'
   #
   # data_sim_table
   data_sim_table = list()
   for (simulate_id, sim_row) in enumerate( input_table['simulate'] ) :
      line_number = simulate_id + 2
      #
      # s_current
      s_current = time.time()
      if s_current - s_last > 30.0 :
            #
            # seconds, s_last
            seconds = s_current - s_start
            s_last  = s_current
            print( f'{simulate_id:,} id, {seconds:.0f} sec' )
      #
      # simulate_id
      if True :
         if simulate_id != int( float(sim_row['simulate_id']) ) :
            msg  = f'csv_simulate: Error at line {line_number} '
            msg += f'in simulate.csv\n'
            msg += f'simulate_id = ' + sim_row['simulate_id']
            msg += ' is not equal line number minus two'
            assert False, msg
      #
      # integrand_name
      integrand_name = sim_row['integrand_name']
      if integrand_name not in valid_integrand_name :
         msg  = f'csv_simulate: Error at line {line_number} '
         msg += f' in simulate.csv\n'
         msg += f'integrand_name = ' + integrand_name
         msg += ' is not a valid integrand name'
         assert False, msg
      #
      # node_name
      node_name = sim_row['node_name']
      if node_name not in node_set :
         msg  = f'csv_simulate: Error at line {line_number} '
         msg += f' in simulate.csv\n'
         msg += f'node_name = ' + node_name
         msg += ' is not in node.csv'
         assert False, msg
      #
      # sex
      sex = sim_row['sex']
      if sex not in [ 'male', 'female', 'both' ] :
         msg  = f'csv_simulate: Error at line {line_number} '
         msg += f' in simulate.csv\n'
         msg += f'sex = ' + sex
         msg += ' is not male, feamle, or both'
         assert False, msg
      #
      # age_lower, age_upper, time_lower, time_upper
      age_lower  = float( sim_row['age_lower'] )
      age_upper  = float( sim_row['age_upper'] )
      time_lower = float( sim_row['time_lower'] )
      time_upper = float( sim_row['time_upper'] )
      #
      # age_mid, time_mid
      age_mid  = ( age_lower  + age_upper )  / 2.0
      time_mid = ( time_lower + time_upper ) / 2.0
      #
      # covariate_value_list
      covariate_value_list = list()
      for (index, covariate_name) in enumerate( covariate_name_list ) :
         spline = spline_node_sex_cov[node_name][sex][covariate_name]
         value  =  spline(age_mid, time_mid)
         covariate_value_list.append(value )
      #
      # data_row
      data_row = dict( zip(covariate_name_list, covariate_value_list) )
      data_row['simulate_id'] = simulate_id
      #
      # rate_fun_dict
      rate_fun_dict = get_rate_fun_dict(
         parent_node_dict            ,
         spline_no_effect_rate       ,
         random_effect_node_sex_rate ,
         spline_node_sex_cov         ,
         root_covariate_avg          ,
         multiplier_list_rate        ,
         node_name                   ,
         sex
      )
      #
      # grid
      integrand_step_size = option_value['integrand_step_size']
      grid = average_integrand_grid(
         integrand_step_size, age_lower, age_upper, time_lower, time_upper
      )
      #
      # avg_integrand
      abs_tol = option_value['absolute_tolerance']
      avg_integrand = dismod_at.average_integrand(
         rate_fun_dict, integrand_name, grid, abs_tol,
      )
      #
      # data_row['meas_mean']
      meas_mean             = avg_integrand
      data_row['meas_mean'] = meas_mean
      #
      # data_row['meas_std']
      percent_cv           = float( sim_row['percent_cv'] )
      meas_std             = percent_cv * meas_mean / 100.0
      data_row['meas_std'] = meas_std
      #
      # data_row['meas_value']
      meas_value             = random.gauss(meas_mean, meas_std )
      meas_value             = max(meas_value, 0.0)
      data_row['meas_value'] = meas_value
      #
      # data_row
      for key in data_row :
         value = data_row[key]
         if type( value ) == float :
            data_row[key] = float_format.format(value)
      #
      # data_sim_table
      data_sim_table.append( data_row )
   #
   # seconds, simulate_id
   seconds = s_current - s_start
   simulate_id = len( input_table['simulate'] )
   print( f'end simulation: total seconds = {seconds:.0f}' )
   #
   print( 'write files' )
   #
   # data.csv
   file_name = f'{sim_dir}/data_sim.csv'
   at_cascade.csv.write_table(file_name, data_sim_table)
   #
   # random_effect_table
   random_effect_table = list()
   for node_name in parent_node_dict :
      for sex in [ 'male', 'female' ] :
         for rate_name in spline_no_effect_rate :
            #
            # row
            row                  = { 'node_name' : node_name, 'sex' : sex }
            row['rate_name']     = rate_name
            random_effect = \
               random_effect_node_sex_rate[node_name][sex][rate_name]
            row['random_effect'] = float_format.format(random_effect)
            #
            # random_effect_table
            random_effect_table.append( row )
   #
   # random_effect.csv
   file_name = f'{sim_dir}/random_effect.csv'
   at_cascade.csv.write_table(file_name, random_effect_table)
   #
   print( 'csv_simulate done' )
