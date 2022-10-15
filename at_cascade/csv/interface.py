# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
import at_cascade.csv
"""
{xrst_begin_parent csv_interface}

Simulate and Fit an AT Cascade Data Set
#######################################

Under Construction
******************

Syntax
******

- ``at_cascade.csv_interface(`` *directory* ``,`` *command* ``)``

Arguments
*********

directory
=========
This string is the directory name where the input and output  files
for the command are located.

command
=======
This string is either ``simulate``, ``fit`` , or ``predict``  .

{xrst_end csv_interface}


===============================================================================

{xrst_begin csv_predict}
{xrst_spell
   sincidence
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
is an :ref:`csv_module@Notation@Index Column` for case.csv.

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
is an :ref:`csv_module@Notation@Index Column` for
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
def interface(directory, command) :
   #
   # command_dict
   command_dict = {
      'simulate' : at_cascade.csv.simulate,
   }
   if command not in command_dict :
      msg  = f'csv_interface: Error: command {command} is not implemented'
      assert False, msg
   #
   # execute the command
   command_dict[command](directory)
   #
   return
