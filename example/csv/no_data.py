# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-25 Bradley M. Bell
# ----------------------------------------------------------------------------
import os
import sys
import time
import math
# import at_cascade with a preference current directory version
current_directory = os.getcwd()
if os.path.isfile( current_directory + '/at_cascade/__init__.py' ) :
   sys.path.insert(0, current_directory)
import at_cascade
"""
{xrst_begin csv.no_data}
{xrst_spell
  const
  dage
  delim
  dtime
  eps
  meas
  sincidence
  std
}

Use a No Data Example to Understand Priors
##########################################

csv_file
********
This dictionary is used to hold the data corresponding to the
csv files for this example:
{xrst_code py}"""
csv_file = dict()
"""{xrst_code}

node.csv
********
For this example the root node, n0, has no children.
{xrst_code py}"""
csv_file['node.csv'] = \
'''node_name,parent_name
n0,
'''
"""{xrst_code}

option_fit.csv
**************
This example uses the default value for the options that are not
listed below:

.. csv-table::
   :header: Name, Value
   :delim: |

   random_seed| chosen using current seconds reported by python time package.
   tolerance_fixed| this is set small, 1e-8, so we can check accuracy.

{xrst_code py}"""
random_seed    = str( int( time.time() ) )
csv_file['option_fit.csv']  = 'name,value\n'
csv_file['option_fit.csv'] += f'random_seed,{random_seed}\n'
csv_file['option_fit.csv'] += f'tolerance_fixed,1e-8\n'
"""{xrst_code}

option_predict.csv
******************
This example uses the default value for all the options in option_predict.csv.
(Future versions of this example will discuss the predictions.)
{xrst_code py}"""
csv_file['option_predict.csv'] = 'name,value\n'
csv_file['option_predict.csv'] += 'db2csv,true\n'
"""{xrst_code}

covariate.csv
*************
This example has no covariates
{xrst_code py}"""
csv_file['covariate.csv'] = \
'''node_name,sex,age,time,omega
n0,female,0,2000,0.02
n0,female,100,2000,0.02
n0,male,0,2000,0.02
n0,male,100,2000,0.02
'''
"""{xrst_code}

fit_goal.csv
************
This example only fits node n0.
{xrst_code py}"""
csv_file['fit_goal.csv'] = \
'''node_name
n0
'''
"""{xrst_code}

predict_integrand.csv
*********************
For this example we want to know the values of Sincidence.
(Note that Sincidence is a direct measurement of iota.)
{xrst_code py}"""
csv_file['predict_integrand.csv'] = \
'''integrand_name
Sincidence
'''
"""{xrst_code}

iota_mean
*********
This is the mean value of iota in the gauss_eps_1 prior:
{xrst_code py}"""
iota_mean = 0.01
"""{xrst_code}

prior.csv
*********
We define three priors:

.. csv-table::
   :widths: auto
   :delim: ;

   gauss_01;    a Gaussian with mean 0 standard deviation 1
   gauss_eps_1; a Gaussian with lower eps, upper 1, mean iota_mean, and std .1

{xrst_code py}"""
csv_file['prior.csv'] = \
   'name,lower,upper,mean,std,density\n' \
   f'gauss_eps_1,1e-6,1.0,{iota_mean},0.1,gaussian\n' \
   'gauss_01,,,0.0,1.0,gaussian\n'
"""{xrst_code}

parent_rate.csv
***************
The only non-zero rates are omega and iota
(omega is known and specified by the covariate.csv file).
The model for iota is linear w.r.t age and constant w.r.t. time.
Its value prior is gauss_eps_1 and its dage prior is gauss_01.
It does not have any dtime priors because
there are no time differences between grid values.
{xrst_code py}"""
csv_file['parent_rate.csv'] = \
'''rate_name,age,time,value_prior,dage_prior,dtime_prior,const_value
iota,0.0,2000,gauss_eps_1,gauss_01,,
iota,100.0,2000,gauss_eps_1,gauss_01,,
'''
"""{xrst_code}

child_rate.csv
**************
The are no children (hence no random effects) in this example.
{xrst_code py}"""
csv_file['child_rate.csv'] = \
'''rate_name,value_prior
'''
"""{xrst_code}

mulcov.csv
**********
There are no covariate multipliers in this example:
{xrst_code py}"""
csv_file['mulcov.csv'] = \
'''covariate,type,effected,value_prior,const_value
'''
"""{xrst_code}

data_in.csv
***********
There is no data in this example
{xrst_code py}"""
header  = 'data_id, integrand_name, node_name, sex, age_lower, age_upper, '
header += 'time_lower, time_upper, meas_value, meas_std, hold_out, '
header += 'density_name, eta, nu'
csv_file['data_in.csv'] = header + '\n'
"""{xrst_code}

Source Code
***********
{xrst_literal
   BEGIN_PROGRAM
   END_PROGRAM
}

{xrst_end csv.no_data}
"""
# BEGIN_PROGRAM
#
# prior calculator
def calculate_prior_from_vals(x_0, x_1, v_0, v_1, d_0):
   return -math.log(
      0.5 * (x_0 - v_0)**2 + 0.5 * (x_1 - v_1)**2 + 0.5 * (x_0 - x_1 - d_0)**2
   )
#
# main
def main() :
   #
   # fit_dir
   fit_dir = 'build/example/csv'
   at_cascade.empty_directory(fit_dir)
   #
   # write csv files
   for name in csv_file :
      file_name = f'{fit_dir}/{name}'
      file_ptr  = open(file_name, 'w')
      file_ptr.write( csv_file[name] )
      file_ptr.close()
   #
   # fit
   at_cascade.csv.fit(fit_dir)
   #
   # predict
   at_cascade.csv.predict(fit_dir)
   #
   # predict_table
   file_name = f'{fit_dir}/fit_predict.csv'
   predict_table = at_cascade.csv.read_table(file_name)
   #
   # row
   for row in predict_table :
      assert row['integrand_name'] == 'Sincidence'
      assert row['node_name'] == 'n0'
      iota      = float( row['avg_integrand'] )
      rel_error = 1.0 - iota / iota_mean
      assert abs( rel_error ) < 1e-8
#
#
if __name__ == '__main__' :
   main()
   print('prior_sam: OK')
# END_PROGRAM
