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
{xrst_begin simulate}
{xrst_spell
    csv
    std
}

Under Construction: Simulate an AT Cascade Data Set
###################################################

Discussion
**********
So far this is just specifications for the input to the simulations.
The following inputs are missing:

#.  The standard deviation of the random effects.

-----------------------------------------------------------------------------

node.csv
********
This csv file defines the node tree.
It has the following columns (it may have others):

node_name
=========
This text is a name describing the node in a way that is easy for a human to
remember. It be unique for each row.

node_id
=======
For each row, the value in this column is the number of rows that come before
this row, not counting the header row.
In other words, it counts the data rows starting at row index zero.

parent_node_id
==============
This integer is the node_id corresponding to the parent node for this node.
The root node of the tree has an empty entry for this column.
If a node is a parent, it must have at least two children.
This avoids fitting the same location twice as one goes from parent
to child nodes.

n_simulate
==========
This integer is the number of rows in simulate.csv that will be randomly chosen
(without replacement) for this node. This value must be less than or equal
the number of rows (not counting the header) in the simulate.csv file.
For example, we could only simulate data for the leaf nodes by setting
n_simulate to zero for the other nodes.


-----------------------------------------------------------------------------

covariate.csv
*************
1.  This csv file specifies the value of omega and the covariates.
2.  None of the data in this file uses demographer notation; e.g.,
    year 1990 means the beginning of 1990,
    not the time interval from 1990 to 1991.
3.  There is a vector of ages :math:`(a_1 , \ldots , a_m )`
    and a vector of times :math:`(t_1 , \ldots , t_n)`
    that define the rectangular grid for this age time csv file.
    In other words, for each node_id, for each sex,
    for :math:`i = 1 , \dots , m`,
    and for :math:`j = 1, \ldots , n`
    there is one and only one row with the corresponding
    node_id, sex, age, and time.

node_id
=======
This integer identifies the node corresponding to this row.

sex
===
This text is ``male`` or ``female`` and identifies which sex
this row corresponds to. When estimating for both sexes, the
average of the corresponding male and female data is used.

age
===
This real is the age, in years,  corresponding to this row.

time
====
This real is the time, in years, corresponding to this row.

omega
=====
This real is the value of  omega (other cause mortality) for this row.
Often other cause mortality is approximated by all cause mortality.
Omega is a rate, not a covariate.

covariate_name
==============
For each covariate that we are including in this simulation,
there is a column in the header that contains the *covariate_name*.
In the other rows, this column  contain a real that is the
corresponding covariate value.

-----------------------------------------------------------------------------

multiplier.csv
**************
This csv file provides information about the covariate multipliers.
Each row of this file, except the header row, corresponds to a multiplier.

rate_name
=========
This text is ``iota``, ``rho``, ``chi``, or ``pini`` and specifies
which rate this covariate multiplier is affecting.

covariate_name
==============
This text is a covariate name and specifies which covariate
is being multiplied by this multiplier.
It can be ``sex`` or any of the covariate names in covariate.csv file.
Note that for sex, the corresponding covariate values are
female = -0.5 and male = +0.5.

truth
=====
This is the value of the covariate multiplier used to simulate the data.

mean
====
This is the prior mean used when fitting this multiplier
(normal distribution).

std
===
This is the prior standard deviation used when fitting this multiplier
(normal distribution).

lower
=====
is the lower limit (during fitting) for this covariate multiplier.

upper
=====
is the upper limit (during fitting) for this covariate multiplier.
Note that using lower and upper limit are zero and the true value is non-zero,
one can simulate data that does not correspond to the model.


-----------------------------------------------------------------------------

rate.csv
********
This csv file specifies the grid points at which each rate is modeled.
It also specifies the true value (for the world).
For each rate, the  (age, time) grid is rectangular.
None of this data is in demographer notation.

rate_name
=========
This text is ``iota``, ``rho``, ``chi``, or ``pini`` and specifies the rate.
If one of these rates doe not appear, it is modeled as always zero.

age
===
This real is the age, in years,  corresponding to this row.

time
====
This real is the time, in years, corresponding to this row.

truth
=====
This real is the rate value for the root node (the world)
with no covariate or random effects.
It is used to simulate the data.

mean
====
This real is the mean used in the prior for the rate
without covariate or random effects
(normal distribution).

std
===
This real is the standard deviation used in the prior for the rate
without covariate or random effects
(normal distribution).

lower
=====
is the lower limit (during fitting) for this covariate multiplier.

upper
=====
is the upper limit (during fitting) for this covariate multiplier.
Note that using lower and upper limit are zero and the true value is non-zero,
one can simulate data that does not correspond to the model.

-----------------------------------------------------------------------------

simulate.csv
************
This csv file specifies the complete data set.
Subsets of the complete data set will be used when fitting the data.
For each row of this file,
a data point is simulated for each sex and
each node (with data equal to one in node.csv).

simulate_id
===========
For each row, the value in this column is the number of rows that come before
this row, not counting the header row.
In other words, it counts the data rows starting at row index zero.
This column is used to select subsets of the simulation corresponding
to each node.


integrand
=========
This text is a dismod_at integrand; e.g. ``Sincidence``.

age_lower
=========
is the lower age limit for this data row.

age_upper
=========
is the upper age limit for this data row.
Note that the age midpoint will be used to interpolate covariates values
corresponding to this data row.

time_lower
==========
is the lower time limit for this data row.

time_upper
==========
is the upper time limit for this data row.

std_log
=======
is the standard deviation, in log space,
used ot simulate data corresponding to this row
(log-normal distribution).


{xrst_end simulate}
"""
def simulate() :
    assert False
