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
   sincidence
}

Fit a Simulated Data Set
########################

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

option.csv
==========
This csv file has two columns,
one called ``name`` and the other called ``value``.
The rows are documented below by the name column:

root_node_name
--------------
This string is the name of the root node.

node.csv
========
This csv file has the same description as the simulate
:ref:`csv_simulate@Input Files@node.csv` file.

covariate_csv
=============
This csv file has the same description as the simulate
:ref:`csv_simulate@Input Files@covariate.csv` file.

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

covariate_name
--------------
For each :ref:`csv_simulate@Input Files@covariate.csv@covariate_name`
there is a column with this name in data.csv.
The values in these columns are floats corresponding to the covariate value
at the mid point of the ages and time intervals for this data point.

------------------------------------------------------------------------------

Output Files
************

data_out.csv
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
is an :ref:`csv_module@Notation@Index Column` for rate_sim.csv,
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
def root_node_database(fit_dir) :
   #
   # output_file
   output_file = f'{csr_dir}/root_node_db'
   #
   # input_table
   input_table = dict()
   input_list = [
      'data',
      'covariate',
      'node',
      'option',
   ]
   print('begin reading csv files')
   for name in input_list :
      file_name         = f'{sim_dir}/{name}.csv'
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
   # covariate_table
   covariate_table = [{
      'name': sex, 'reference': 0.0, 'max_difference' : 0.5
   }]
   for key in covariate_average :
      covariate_table.append({
         'name':            key,
         'reference':       covariate_average[key],
         'max_difference' : None
      })
   #
   # data_table
   data_table = input_table['data']
   for row in data_table () :
      row['weight'] = ''
      row['subgroup'] = 'world'
   #
   dismod_at.create_database(
         file_name         = output_file,
         age_list          = None,
         time_list         = None,
         integrand_table   = None,
         node_table        = input_table['node'],
         subgroup_table    = None,
         weight_table      = None,
         covariate_table   = covariate_table,
         avgint_table      = list(),
         data_table        = data_table,
         prior_table_copy  = None,
         smooth_table      = None,
         nslist_table      = None,
         rate_table        = None,
         mulcov_table      = None,
         option_table      = None,
   )
# ----------------------------------------------------------------------------
# BEGIN_FIT
def fit(fit_dir) :
   assert type(fit_dir) == str
# END_FIT
