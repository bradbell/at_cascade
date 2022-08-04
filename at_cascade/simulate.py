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
{xrst_begin_parent simulate}
{xrst_spell
    dir
    csv
}

Simulate and Fit an AT Cascade Data Set
#######################################

Under Construction
******************

Definition
**********
{xrst_file
        # BEGIN Definition
        # END Definition
}

Arguments
*********

csv_dir
=======
This ``str`` is the directory name where the csv input and output files
are located.

command
=======
This ``str`` is either ``simulate`` or ``fit``.
During a simulate command, only the :ref:`simulate_csv_out@data.csv` file
is created.
During a fit command, the data.csv file must already exist
and the other output files are created.

Notation
********

Demographer
===========
None of the data is in demographer notation.
For example,
:ref:`simulate_csv_in@covariate.csv@time` 1990 means the beginning of 1990,
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


Csv Files
*********
{xrst_child_list}

{xrst_end simulate}

===============================================================================

{xrst_begin simulate_csv_in}
{xrst_spell
    csv
    std
    cv
}

simulate Csv Input Files
#########################

option.csv
**********
This csv file has two columns,
one called ``name`` and the other called ``value``.
The rows are documented below by the name column:

std_random_effects
==================
This is the standard deviation of the random effects.
All fo the effects are in log of rate space, so this standard deviation
is also in log of rate space.

-----------------------------------------------------------------------------

node.csv
********
This csv file defines the node tree.
It has the columns documented below.
Columns that are not documented are not used by simulate.
This is true for all the :ref:`@simulate_csv_in`.

node_name
=========
This string is a name describing the node in a way that is easy for a human to
remember. It be unique for each row.

node_id
=======
is an :ref:`simulate@notation@index_column` for this file.

parent_node_id
==============
This integer is the node_id corresponding to the parent of this node.
The root node of the tree has an empty entry for this column.
If a node is a parent, it must have at least two children.
This avoids fitting the same location twice as one goes from parent
to child nodes.

-----------------------------------------------------------------------------

covariate.csv
*************
This csv file specifies the value of omega and the covariates.
It has a :ref:`simulate@notation@rectangular_grid` in the columns
``node_id``, ``sex``, ``age``, ``time`` .

node_id
=======
This integer identifies the node, in node.csv, corresponding to this row.

sex
===
This identifies which sex this row corresponds to.
When estimating for both sexes, the
average of the corresponding male and female covariates is used.

age
===
This float is the age, in years,  corresponding to this row.

time
====
This float is the time, in years, corresponding to this row.

omega
=====
This float is the value of omega (other cause mortality) for this row.
Often other cause mortality is approximated by all cause mortality.
Omega is a rate, not a covariate.

covariate_name
==============
For each covariate that we are including in this simulation,
there is a column in the header that contains the *covariate_name*.
The other values in that column are float representations of the covariate.
All of these covariates are
:ref:`glossary@relative_covariate`; see
:ref:`simulate@notation@covariates`.

-----------------------------------------------------------------------------

multiplier.csv
**************
This csv file provides information about the covariate multipliers.
Each row of this file, except the header row, corresponds to a
different multiplier. The multipliers are constant in age and time.

multiplier_id
=============
is an index column for this file.

rate_name
=========
This string is ``iota``, ``rho``, ``chi``, or ``pini`` and specifies
which rate this covariate multiplier is affecting.

covariate_or_sex
================
If this is ``sex`` it specifies that this multiplier multiples
the sex values where female = -0.5 and male = +0.5.
Otherwise this is one of the covariate names in the covariate.csv file
and specifies which covariate is being multiplied.

truth
=====
This is the value of the covariate multiplier used to simulate the data.

mean
====
This is the prior mean used when fitting this multiplier.
This column is not used during the ``simulate`` command.


std
===
This is the prior standard deviation used when fitting this multiplier.
This column is not used during the ``simulate`` command.

lower
=====
is the lower limit (during fitting) for this covariate multiplier.
This column is not used during the ``simulate`` command.

upper
=====
is the upper limit (during fitting) for this covariate multiplier.
If the lower and upper limits are zero and the true value is non-zero,
the multiplier will be included in the simulated data but not in the model fit.
This column is not used during the ``simulate`` command.


-----------------------------------------------------------------------------

rate.csv
********
This csv file specifies the grid points at which each rate is modeled.
This file has a
:ref:`simulate@notation@rectangular_grid` in the columns
``rate_name``, ``age``, ``time`` .
These are no-effect rates; i.e., the rates without
the random and covariate effects.
Covariate multipliers that are constrained to zero during the fitting
can be used to get variation between nodes in the
no-effect rates corresponding to the fit.

rate_id
=======
is an index column for this file.

rate_name
=========
This string is ``iota``, ``rho``, ``chi``, or ``pini`` and specifies the rate.
If one of these rates does not appear, it is modeled as always zero.

age
===
This float is the age, in years,  corresponding to this row.

time
====
This float is the time, in years, corresponding to this row.

truth
=====
This float is the no-effect rate value for all the nodes.
It is used to simulate the data.
As mentioned, above knocking out covariate multipliers can be
used to get variation in the no-effect rates that correspond to the fit.

mean
====
This float is the mean used in the prior for the rate
without covariate or random effects.
This column is not used during the ``simulate`` command.

std
===
This float is the standard deviation used in the prior for the rate
without covariate or random effects
This column is not used during the ``simulate`` command.

lower
=====
is the lower limit (during fitting) for this no-effect rate.
This column is not used during the ``simulate`` command.

upper
=====
is the upper limit (during fitting) for this no-effect rate.
This column is not used during the ``simulate`` command.

-----------------------------------------------------------------------------

simulate.csv
************
This csv file specifies the simulated data set
with each row corresponding to one data point.

simulate_id
===========
is an index column for this file.
This column avoids having data.csv reproduce the columns in this file.

integrand_name
==============
This string is a dismod_at integrand; e.g. ``Sincidence``.

node_id
=======
This integer identifies the node corresponding to this data point.

sex
===
is the sex for this data pont.

age_lower
=========
is the lower age limit for this data row.

age_upper
=========
is the upper age limit for this data row.

time_lower
==========
is the lower time limit for this data row.

time_upper
==========
is the upper time limit for this data row.

percent_cv
==========
is the coefficient of variation as a percent of the corresponding
average integrand; i.e., the model for the integrand
without any measurement noise.
The noise will be generated with a normal distribution
that has mean equal to the average integrand and
standard deviation equal to the mean times percent_cv / 100.
If the resulting measurement value would be less than zero,
the value zero is be used; i.e.,
a censored normal is used to simulate the data.


{xrst_end simulate_csv_in}

==============================================================================

{xrst_begin simulate_csv_out}
{xrst_spell
    csv
    meas
    std
    bilinear
}

simulate Csv Output Files
##########################

data.csv
********
This contains the simulated data.
It is created during a simulate command
and has the following columns:

simulate_id
===========
This integer identifies the row in the simulate.csv table
corresponding to this data point.

node_id
=======
This integer identifies the node for this data row.

integrand_name
==============
This string identifies the integrand.

meas_value
==========
This float is the simulated measured value.

meas_std
========
This float is the measurement standard deviation for the simulated
data point. This standard deviation is before censoring.

covariate_name
==============
For each :ref:`simulate_csv_in@covariate.csv@covariate_name`
there is a column in the simulate.csv header that contains the name.
In the other rows, this column  contain a float that is the
corresponding covariate value at the mid point of the ages and time
intervals for this data point. This value is obtained using
bilinear interpolation of the covariate values in covariate.csv.
The interpolate is extended as constant in age (time) for points
outside the age rage (time range) in the covariate.csv file.

------------------------------------------------------------------------------

multiplier_fit.csv
******************
This contains the fit results for the covariate multipliers.
It is created during a fit command and
has the following columns:

multiplier_id
=============
This integer identifies the row in the multiplier.csv file
corresponding to this multiplier estimate.

estimate
========
This float is the estimated value for the covariate multiplier.

estimate_std
============
This float is the asymptotic statistics approximation
for the standard deviation of the estimate.

------------------------------------------------------------------------------

rate_fit.csv
************
This contains the fit results for the no-effect rate values.
It is created during a fit command and
has the following columns:

node_id
=======
This integer identifies the row in the node.csv file
corresponding to this rate estimate.

rate_id
=======
This integer identifies the row in the rate.csv file
corresponding to this the rate estimate.

sex
===
This is the sex for this rate estimate.

estimate
========
This float is the estimated value for the no-effect rate.

estimate_std
============
This float is the asymptotic statistics approximation
for the standard deviation of the estimate.

------------------------------------------------------------------------------

data_fit.csv
************
This contains the fit results for the simulated data values.
It is created during a fit command and
has the following columns:

data_id
=======
This integer identifies the row in the data.csv file
corresponding to this data estimate.

estimate
========
This float is the estimated value for the data

residual
========
This float is the weighted residual corresponding to this data point.
This has a simple form because there are no noise covariates; i.e.,
(meas_value - estimate) / meas_std.


{xrst_end simulate_csv_out}
"""
# BEGIN Definition
# at_cascade.simulate
def simulate(
    csv_dir ,
    command ,
) :
# END Definition
    assert type(csv_dir) == str
    assert False
