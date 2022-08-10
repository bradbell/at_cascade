# -----------------------------------------------------------------------------
# at_cascade: Cascading Dismod_at Analysis From Parent To Child Regions
#           Copyright (C) 2021-22 University of Washington
#              (Bradley M. Bell bradbell@uw.edu)
#
# This program is distributed under the terms of the
#     GNU Affero General Public License version 3.0 or later
# see http://www.gnu.org/licenses/agpl.txt
# -----------------------------------------------------------------------------
"""
{xrst_begin_parent csv_interface}
{xrst_spell
    dir
    csv
}

Simulate and Fit an AT Cascade Data Set
#######################################

Under Construction
******************

Syntax
**********

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
{xrst_child_table}

Notation
********

Demographer
===========
None of the data is in demographer notation.
For example,
:ref:`csv_simulate@input_files@covariate.csv@time`
1990 means the beginning of 1990,
not the time interval from 1990 to 1991.

Rectangular Grid
================
A csv file is said to have a rectangular grid in columns
*name_a* , *name_b*, *name_c* if the following holds:

#.  The csv file has columns with the names
    *name_a*, *name_b*, *name_c*.

#.  :math:`( a_1 , \ldots , a_L )`
    is the vector of values in column *name_a* .

#.  :math:`( b_1 , \ldots , b_M )`
    is the vector of values in column *name_b* .

#.  :math:`( c_1 , \ldots , c_N )`
    is the vector of values in column *name_c* .

#.  For :math:`\ell = 1 , \ldots , L`,
    :math:`m = 1 , \ldots , M`,
    :math:`n = 1,  \ldots , N` ,
    there is one and only one row with
    *name_a* equal to :math:`a_\ell`,
    *name_b* equal to :math:`b_m`, and
    *name_c* equal to :math:`c_n`.

Covariates
==========
For these simulations, all the covariates are
:ref:`glossary@relative_covariate` (called country covariates at IHME).
Sex is the
:ref:`all_option_table@split_covariate_name` and is not
referred to as a covariate by the simulate routine.

Data Type
=========
The actual data type for each entry in a csv file is a string; i.e.,
an arbitrary sequence of characters. Certain columns have further
restrictions as described below

1.  An integer value is a string represents of an integer.
2.  A float value is a string that represents a floating point number.
3.  A sex value is either ``male`` or ``female`` .

Index Column
============
An index column for a csv file is an integer column
that has the row number corresponding to each row.
It starts with zero at the first row below the header row.

Distributions
=============
Unless other wise specified, the mean and standard deviations that
simulate refers to are for a normal distribution.

{xrst_end csv_interface}

===============================================================================

{xrst_begin csv_simulate}
{xrst_spell
    csv
    std
    cv
    sim
    meas
    bilinear
}

Simulate A Cascade Data Set
###########################

Input Files
***********

option.csv
==========
This csv file has two columns,
one called ``name`` and the other called ``value``.
The rows are documented below by the name column:

std_random_effects
------------------
This is the standard deviation of the random effects.
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

parent
------
This string is the name corresponding to the parent of this node.
The root node of the tree has an empty entry for this column.
If a node is a parent, it must have at least two children.
This avoids fitting the same location twice as one goes from parent
to child nodes.

-----------------------------------------------------------------------------

covariate.csv
=============
This csv file specifies the value of omega and the covariates.
It has a :ref:`csv_interface@notation@rectangular_grid` in the columns
``node_name``, ``sex``, ``age``, ``time`` .

node_name
---------
This string identifies the node, in node.csv, corresponding to this row.

sex
---
This identifies which sex this row corresponds to.
When estimating for both sexes, the
average of the corresponding male and female covariates is used.

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

covariate_name
--------------
For each covariate that we are including in this simulation,
there is a column in the header that contains the *covariate_name*.
The other values in that column are float representations of the covariate.
All of these covariates are
:ref:`glossary@relative_covariate`; see
:ref:`csv_interface@notation@covariates`.

-----------------------------------------------------------------------------

multiplier_sim.csv
==================
This csv file provides information about the covariate multipliers.
Each row of this file, except the header row, corresponds to a
different multiplier. The multipliers are constant in age and time.

multiplier_id
-------------
is an index column for this file.

rate_name
---------
This string is ``iota``, ``rho``, ``chi``, or ``pini`` and specifies
which rate this covariate multiplier is affecting.

covariate_or_sex
----------------
If this is ``sex`` it specifies that this multiplier multiples
the sex values where female = -0.5 and male = +0.5.
Otherwise this is one of the covariate names in the covariate.csv file
and specifies which covariate is being multiplied.

multiplier_truth
----------------
This is the value of the covariate multiplier used to simulate the data.

-----------------------------------------------------------------------------

rate_sim.csv
============
This csv file specifies the grid points at which each rate is modeled
during a simulation. It has a
:ref:`csv_interface@notation@rectangular_grid` in the columns
``rate_name``, ``age``, ``time`` .
These are no-effect rates; i.e., the rates without
the random and covariate effects.
Covariate multipliers that are constrained to zero during the fitting
can be used to get variation between nodes in the
no-effect rates corresponding to the fit.

rate_id
-------
is an index column for this file.

rate_name
---------
This string is ``iota``, ``rho``, ``chi``, or ``pini`` and specifies the rate.
If one of these rates does not appear, it is modeled as always zero.

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

-----------------------------------------------------------------------------

simulate.csv
============
This csv file specifies the simulated data set
with each row corresponding to one data point.

simulate_id
-----------
is an index column for this file.

integrand_name
--------------
This string is a dismod_at integrand; e.g. ``Sincidence``.

node_name
---------
This string identifies the node corresponding to this data point.

sex
---
is the sex for this data pont.

age_lower
---------
is the lower age limit for this data row.

age_upper
---------
is the upper age limit for this data row.

time_lower
----------
is the lower time limit for this data row.

time_upper
----------
is the upper time limit for this data row.

percent_cv
----------
is the coefficient of variation as a percent of the corresponding
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

data_sim.csv
============
This contains the simulated data.
It is created during a simulate command
and has the following columns:

simulate_id
-----------
This integer identifies the row in the simulate.csv
corresponding to this row in data_sim.csv.
This is an index column for both simulate.csv and data.csv.

meas_value
----------
This float is the simulated measured value.

meas_std
--------
This float is the measurement standard deviation for the simulated
data point. This standard deviation is before censoring.

covariate_name
--------------
For each :ref:`csv_simulate@input_files@covariate.csv@covariate_name`
there is a column in the simulate.csv header that contains the name.
In the other rows, this column  contain a float that is the
corresponding covariate value at the mid point of the ages and time
intervals for this data point. This value is obtained using
bilinear interpolation of the covariate values in covariate.csv.
The interpolate is extended as constant in age (time) for points
outside the age rage (time range) in the covariate.csv file.

{xrst_end csv_simulate}

===============================================================================

{xrst_begin csv_fit}
{xrst_spell
    csv
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
This identifies a row in data_csv that is included during the next
file command.

------------------------------------------------------------------------------

multiplier_prior.csv
====================
This file adds prior information for the multipliers in
:ref:`csv_simulate@input_files@multiplier_sim.csv`.

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
:ref:`csv_simulate@input_files@rate_sim.csv`.

rate_id
-------
This integer identifies the row in rate_sim.csv that
corresponds to this row in rate_prior.csv.

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

rate_id
-------
This integer identifies the row in the rate_sim.csv and rate_prior.csv
corresponding to this rate estimate.

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
    csv
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
is an index column for this file.

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
is an index column for this file
and also corresponds to *case_id* in the case.csv file.

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
# -----------------------------------------------------------------------------
# option_dict['std_random_effect']:
# is a float that is greater than zero
#
# option_dict = option_table2dict(option_table)
def option_table2dict(option_table) :
    #
    # option_dict
    option_dict = dict()
    valid_name  = { 'std_random_effects' }
    line_number = 0
    for row in option_table :
        line_number += 1
        name         = row['name']
        value        = row['value']
        if name in option_dict :
            msg  = f'csv_simulate: Error: line {line_number} in option.csv\n'
            msg += f'the name {name} appears twice in this table'
            assert False, msg
        if not name in valid_name :
            msg  = f'csv_simulate: Error: line {line_number} in option.csv\n'
            msg += f'{name} is not a valid option name'
            assert False, msg
        option_dict[name] = value
    #
    # option_dict
    for name in valid_name :
        if not name in option_dict :
            msg  = 'csv_simulate: Error: in option.csv\n'
            msg += f'the name {name} does not apper'
            assert False, msg
    #
    # option_dict['std_random_effects']
    std_random_effects = float( option_dict['std_random_effects'] )
    if std_random_effects <= 0.0 :
        msg  = 'csv_simulate: Error: in option.csv\n'
        msg += f'std_random_effect = {std_random_effect} <= 0'
        assert False, msg
    #
    return option_dict
# ----------------------------------------------------------------------------
def check_node_table( node_table ) :

# ----------------------------------------------------------------------------
def csv_simulate(csv_dir) :
    #
    # input_table
    input_table = dict()
    input_list  = [
        'optiion',
    ]
    for name in input_list :
        file_name         = name + '.csv'
        input_table[name] = at_cascade.read_csv_file(file_name)
    #
    # option_dict
    option_dict = option_table2dict( input_table['option'] )