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

{xrst_begin csv_fit}
{xrst_spell
   dir
   meas
   sim
   std
}

Fit a Simulated Data Set
########################

Prototype
*********
{xrst_literal
   # BEGIN_CSV_FIT
   # END_CSV_FIT
}

fit_dir
*******
This string is the directory name where the csv files
are located.

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
"""
# ----------------------------------------------------------------------------
def root_node_database(fit_dir) :
   file_name = f'{csr_dir}/root_node_db'
   #
   dismod_at.create_database(
         file_name         = file_name,
         age_list          = age_list,
         time_list         = time_list,
         integrand_table   = integrand_table,
         node_table        = node_table,
         subgroup_table    = subgroup_table,
         weight_table      = weight_table,
         covariate_table   = covariate_table,
         avgint_table      = avgint_table,
         data_table        = data_table,
         prior_table_copy  = prior_table_copy,
         smooth_table      = smooth_table,
         nslist_table      = nslist_table,
         rate_table        = rate_table,
         mulcov_table      = mulcov_table,
         option_table      = option_table,
   )
# ----------------------------------------------------------------------------
# BEGIN_CSV_FIT
def csv_fit(fit_dir) :
   assert type(fit_dir) == str
# END_CSV_FIT
