# -----------------------------------------------------------------------------
# at_cascade: Cascading Dismod_at Analysis From Parent To Child Regions
#           Copyright (C) 2021-22 University of Washington
#              (Bradley M. Bell bradbell@uw.edu)
#
# This program is distributed under the terms of the
#     GNU Affero General Public License version 3.0 or later
# see http://www.gnu.org/licenses/agpl.txt
# -----------------------------------------------------------------------------
import at_cascade
"""
{xrst_begin_parent csv_interface}
{xrst_spell
   dir
}

Simulate and Fit an AT Cascade Data Set
#######################################

Under Construction
******************

Syntax
******

- ``at_cascade.csv_interface(`` *csv_dir* ``,`` *command* ``)``

Arguments
*********

csv_dir
=======
This string is the directory name where the csv files
are located.

command
=======
This string is either ``simulate``, ``fit`` , or ``predict``  .
{xrst_toc_table
   at_cascade/csv_simulate.py
}

Notation
********

Demographer
===========
None of the data is in demographer notation.
For example,
:ref:`csv_simulate@Input Files@covariate.csv@time`
1990 means the beginning of 1990,
not the time interval from 1990 to 1991.

Rectangular Grid
================
A csv file is said to have a rectangular grid in columns
*name_a* , *name_b*, *name_c* if the following holds:

#. The csv file has columns with the names
   *name_a*, *name_b*, *name_c*.

#. :math:`( a_1 , \ldots , a_L )`
   is the vector of values in column *name_a* .

#. :math:`( b_1 , \ldots , b_M )`
   is the vector of values in column *name_b* .

#. :math:`( c_1 , \ldots , c_N )`
   is the vector of values in column *name_c* .

#. For :math:`\ell = 1 , \ldots , L`,
   :math:`m = 1 , \ldots , M`,
   :math:`n = 1,  \ldots , N` ,
   there is one and only one row with
   *name_a* equal to :math:`a_\ell`,
   *name_b* equal to :math:`b_m`, and
   *name_c* equal to :math:`c_n`.

Covariates
==========
For this csv interface, all the covariates are
:ref:`glossary@Relative Covariate` (called country covariates at IHME).
Other cause mortality ``omega`` is referred to as a
covariate (not as a rate) for this interface.
Sex is the
:ref:`all_option_table@split_covariate_name` and is not
referred to as a covariate.

Data Type
=========
The actual data type for each entry in a csv file is a string; i.e.,
an arbitrary sequence of characters. Certain columns have further
restrictions as described below

1. An integer value is a string represents of an integer.
2. A float value is a string that represents a floating point number.
3. A sex value is either ``female`` , ``male`` or ``both`` .

Index Column
============
An index column for a csv file is an integer column
that has the row number corresponding to each row.
It starts with zero at the first row below the header row.
If a column name is an index column for two or more files,
rows with the same index value in the different files
correspond to each other.

Distributions
=============
Unless other wise specified, the mean and standard deviations that
simulate refers to are for a normal distribution.

{xrst_end csv_interface}

===============================================================================

{xrst_begin csv_fit}
{xrst_spell
   meas
   std
   sim
}

Fit a Simulated Data Set
########################

Input Files
***********
All the csv_simulate :ref:`csv_simulate` input and output files
are inputs to the ``csv_fit`` command.
The files listed below are additional inputs:

data_subset.csv
===============
This file identifies which rows of data_sim.csv are
included during the next fit command.

simulate_id
-----------
This identifies a row in data_sim.csv that is included during the next
fit command.

------------------------------------------------------------------------------

multiplier_prior.csv
====================
This file adds prior information for the multipliers in
:ref:`csv_simulate@Input Files@multiplier_sim.csv`.

multiplier_id
-------------
This integer identifies the row in multiplier_sim.csv that
corresponds to this row in multiplier_prior.csv.

prior_mean
----------
This is the prior mean used when fitting this multiplier.

prior_std
---------
This is the prior standard deviation used when fitting this multiplier.

lower
-----
is the lower limit (during fitting) for this covariate multiplier.

upper
-----
is the upper limit (during fitting) for this covariate multiplier.
If the lower and upper limits are zero and the true value is non-zero,
the multiplier will be included in the simulated data but not in the model fit.

------------------------------------------------------------------------------

rate_prior.csv
==============
This file adds prior information for the rates in
:ref:`csv_simulate@Input Files@no_effect_rate.csv` .

rate_sim_id
-----------
is an :ref:`csv_interface@Notation@Index Column` for rate_sim.csv
and rate_prior.csv.

prior_mean
----------
This float is the mean used in the prior for the rate
without covariate or random effects.

prior_std
---------
This float is the standard deviation used in the prior for the rate
without covariate or random effects

lower
-----
is the lower limit (during fitting) for this no-effect rate.

upper
-----
is the upper limit (during fitting) for this no-effect rate.

------------------------------------------------------------------------------

Output Files
************

data_fit.csv
============
This contains the fit results for the simulated data values.
It is created during a fit command and
has the following columns:

simulate_id
-----------
This integer identifies the row in the simulate.csv and data_sim.csv
corresponding to this data estimate.

estimate
--------
This float is the estimated value for the data

residual
--------
This float is the weighted residual corresponding to this data point.
This has a simple form because there are no noise covariates;
i.e., (meas_value - estimate) / meas_std.

------------------------------------------------------------------------------

rate_fit.csv
============
This contains the fit results for the rate values.
It is created during a fit command and
has the following columns:

rate_sim_id
-----------
is an :ref:`csv_interface@Notation@Index Column` for rate_sim.csv,
rate_prior.csv and rate_fit.csv.

estimate
--------
This float is the estimated value for the rate.

std_error
---------
Is the asymptotic estimate for the accuracy of the estimate.

------------------------------------------------------------------------------

multiplier_fit.csv
==================
This contains the fit results for the multiplier values.
It is created during a fit command and
has the following columns:

multiplier_id
-------------
This integer identifies the row in the multiplier_sim.csv and
multiplier_prior.csv corresponding to this multiplier estimate.

estimate
--------
This float is the estimated value for the multiplier.

std_error
---------
Is the asymptotic estimate for the accuracy of the estimate.

{xrst_end csv_fit}

===============================================================================

{xrst_begin csv_predict}
{xrst_spell
}

Predictions
###########

Input Files
***********
All the csv_simulate :ref:`csv_simulate` and :ref:`csv_fit`
input and output files are inputs to the ``csv_predict`` command.
The files listed below are additional inputs:

case.csv
========
This csv file specifies the prediction cases.
with each row corresponding to one data point.

case_id
-------
is an :ref:`csv_interface@Notation@Index Column` for case.csv.

integrand_name
--------------
This string is a dismod_at integrand; e.g. ``Sincidence`` for this prediction.

node_name
---------
This string identifies the node corresponding to this prediction.

sex
---
is the sex for this prediction.

age_lower
---------
is the lower age limit for this prediction.

age_upper
---------
is the upper age limit for this prediction.

time_lower
----------
is the lower time limit for this prediction.

time_upper
----------
is the upper time limit for this prediction.

------------------------------------------------------------------------------

Output Files
************

predict.csv
===========

case_id
-------
is an :ref:`csv_interface@Notation@Index Column` for
predict.csv and case.csv.

integrand_predict
-----------------
is the value of the predicted integrand value corresponding to this case_id,
the fit values for the variables, plus the covariate effect.
Note that the variables are the no-effect rates and the covariate multipliers.

integrand_truth
---------------
is the value of the predicted integrand value corresponding to this case_id,
truth values for the variables, plus the covariate effect.
Note that the variables are the no-effect rates and the covariate multipliers.


{xrst_end csv_predict}
"""
# ----------------------------------------------------------------------------
def csv_interface(csv_dir, command) :
   #
   # command_dict
   command_dict = {
      'simulate' : at_cascade.csv_simulate,
   }
   if command not in command_dict :
      msg  = f'csv_interface: Error: command {command} is not implemented'
      assert False, msg
   #
   # execute the command
   command_dict[command](csv_dir)
   #
   return
