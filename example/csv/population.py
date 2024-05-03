# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ----------------------------------------------------------------------------
import os
import sys
import time
import math
import shutil
import csv
import multiprocessing
# import at_cascade with a preference current directory version
current_directory = os.getcwd()
if os.path.isfile( current_directory + '/at_cascade/__init__.py' ) :
   sys.path.insert(0, current_directory)
import at_cascade
"""
{xrst_begin csv.population}
{xrst_spell
   const
   dage
   delim
   dtime
   eps
   meas
   sincidence
   std
   uniform uniform
}

Population Weighting of Measurement Values
##########################################

ode_step_size
*************
The only integrand Sincidence does use the dismod_at ODE.
Thus this step size is only
used when approximating averages with respect to age and time.
It is very small so that the predictions are very accurate.
{xrst_code py}"""
ode_step_size = 0.01
"""{xrst_code}

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
   compress_interval| use zero so that no intervals get compressed.
   tolerance_fixed| this is set small, 1e-8, so we can check accuracy.
   ode_step_size| step size use to approximate averages w.r.t. age, time.

The population covariate is used to weight the data; see
:ref:`csv.fit@Input Files@covariate.csv@population` in the covariate.csv table.
It does not matter if it is an
:ref:`csv.fit@Input Files@option_fit.csv@absolute_covariates`
because it does not appear in the
:ref:`csv.fit@Input Files@mulcov.csv@covariate` column of the mulcov.csv table.

{xrst_code py}"""
random_seed    = str( int( time.time() ) )
csv_file['option_fit.csv']  = 'name,value\n'
csv_file['option_fit.csv'] += f'random_seed,{random_seed}\n'
csv_file['option_fit.csv'] += f'compress_interval,0.0 0.0\n'
csv_file['option_fit.csv'] += f'tolerance_fixed,1e-8\n'
csv_file['option_fit.csv'] += f'ode_step_size,{ode_step_size}\n'
"""{xrst_code}

option_predict.csv
******************
This example uses the default value for all the options in option_predict.csv.
{xrst_code py}"""
csv_file['option_predict.csv']  = 'name,value\n'
"""{xrst_code}

covariate.csv
*************
This example has one covariate,  population.
Other cause mortality, omega, is constant and equal to 0.02.
THe population depends on age (but not time or sex):
{xrst_code py}"""
population_age_0   = 1e4
population_age_100 = 1e3
csv_file['covariate.csv'] = \
   'node_name,sex,age,time,omega,population\n' + \
   'n0,female,0,2000,0.02,'   + str(population_age_0) + '\n' \
   'n0,female,100,2000,0.02,' + str(population_age_100) + '\n' \
   'n0,male,0,2000,0.02,'     + str(population_age_0) + '\n' \
   'n0,male,100,2000,0.02,'   + str(population_age_100) + '\n'
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

prior.csv
*********
We define three priors:

.. csv-table::
   :widths: auto
   :delim: ;

   uniform_1_1;   a uniform distribution on [ -1, 1 ]
   uniform_eps_1; a uniform distribution on [ 1e-6, 1 ]
   gauss_01;      a Gaussian with mean 0 standard deviation 1

{xrst_code py}"""
csv_file['prior.csv'] = \
'''name,lower,upper,mean,std,density
uniform_-1_1,-1.0,1.0,0.5,,uniform
uniform_eps_1,1e-6,1.0,0.5,,uniform
gauss_01,,,0.0,1.0,gaussian
'''
"""{xrst_code}

parent_rate.csv
***************
The only non-zero rates are omega and iota
(omega is known and specified by the covariate.csv file).
The model for iota is linear w.r.t age and constant w.r.t. time.
Its value prior is uniform_eps_1 and its dage prior is gauss_01.
It does not have any dtime priors because
there are no time differences between grid values.
{xrst_code py}"""
csv_file['parent_rate.csv'] = \
'''rate_name,age,time,value_prior,dage_prior,dtime_prior,const_value
iota,0.0,2000,uniform_eps_1,gauss_01,,
iota,100.0,2000,uniform_eps_1,gauss_01,,
'''
"""{xrst_code}

child_rate.csv
**************
The are not children (hence no random effects) in this example.
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
The only integrand for this example is Sincidence
(a direct measurement of iota.)
The age intervals are is [0, 0], [0, 100], and [100, 100].
The time intervals are all the same, [2000, 2010].
The measurement standard deviation is 0.001 (during the fitting) and
none of the data is held out.
The actual
{xrst_code py}"""
header  = 'data_id, integrand_name, node_name, sex, age_lower, age_upper, '
header += 'time_lower, time_upper, meas_value, meas_std, hold_out, '
header += 'density_name, eta, nu'
csv_file['data_in.csv'] = header + \
'''
0, Sincidence, n0, female, 0,     0, 2000, 2000, 0.0000, 0.001, 0, gaussian, ,
1, Sincidence, n0, female, 0,   100, 2000, 2000, 0.0000, 0.001, 0, gaussian, ,
2, Sincidence, n0, female, 100, 100, 2000, 2000, 0.0000, 0.001, 0, gaussian, ,
3, Sincidence, n0, male,   0,     0, 2000, 2000, 0.0000, 0.001, 0, gaussian, ,
4, Sincidence, n0, male,   0,   100, 2000, 2000, 0.0000, 0.001, 0, gaussian, ,
5, Sincidence, n0, male,   100, 100, 2000, 2000, 0.0000, 0.001, 0, gaussian, ,
'''
csv_file['data_in.csv'] = csv_file['data_in.csv'].replace(' ', '')
"""{xrst_code}
The measurement value meas_value is 0.0000 above and gets replaced by
the following code:
{xrst_literal
   # BEGIN_MEAS_VALUE
   # END_MEAS_VALUE
}

Source Code
***********
{xrst_literal
   BEGIN_PROGRAM
   END_PROGRAM
}

{xrst_end csv.population}
"""
# BEGIN_PROGRAM
#
# no_effect_iota
def no_effect_iota(age) :
   age_0    = 0.01
   age_100  = 0.03
   iota     = ( age_0 * (100.0 - age) + age_100 * (age - 0.0) ) / 100.0
   return iota
#
# population
def population(age) :
   age_0    = population_age_0
   age_100  = population_age_100
   pop      = ( age_0 * (100.0 - age) + age_100 * (age - 0.0) ) / 100.0
   return pop
#
# average_Sincidence
def average_Sincidence(age_lower, age_upper) :
   if age_lower == age_upper :
      return no_effect_iota(age_lower)
   #
   max_step = ode_step_size
   n_step    = int( (age_upper - age_lower) / max_step ) + 1
   step_size = (age_upper - age_lower) / n_step
   #
   average   = 0.0
   sum_pop   = 0.0
   for i_step in range(n_step + 1) :
      age     = age_lower + i_step * step_size
      pop     = population(age)
      iota    = no_effect_iota(age)
      average += pop * iota
      sum_pop += pop
   average /= sum_pop
   return average
#
# main
def main() :
   #
   # fit_dir
   fit_dir = 'build/example/csv'
   if not os.path.exists(fit_dir) :
      os.makedirs(fit_dir)
   root_node_name = 'n0'
   if os.path.exists( fit_dir + '/' + root_node_name  ) :
      shutil.rmtree( fit_dir + '/' + root_node_name  )
   #
   # write csv files
   for name in csv_file :
      file_name = f'{fit_dir}/{name}'
      file_ptr  = open(file_name, 'w')
      file_ptr.write( csv_file[name] )
      file_ptr.close()
   #
   # data_in.csv
   float_format      = '{0:.5g}'
   file_name         = f'{fit_dir}/data_in.csv'
   table             = at_cascade.csv.read_table( file_name )
   for row in table :
      node_name      = row['node_name']
      integrand_name = row['integrand_name']
      age_lower      = float( row['age_lower'] )
      age_upper      = float( row['age_upper'] )
      assert integrand_name == 'Sincidence'
      #
      # BEGIN_MEAS_VALUE
      row['meas_value'] = average_Sincidence(age_lower, age_upper)
      # END_MEAS_VALUE
   at_cascade.csv.write_table(file_name, table)
   #
   # fit
   at_cascade.csv.fit(fit_dir)
   #
   # predict
   at_cascade.csv.predict(fit_dir)
   #
   #
   # predict_table
   file_name = f'{fit_dir}/fit_predict.csv'
   predict_table = at_cascade.csv.read_table(file_name)
   #
   # row
   for row in predict_table :
      assert row['integrand_name'] == 'Sincidence'
      assert row['node_name'] == 'n0'
      age       = float( row['age'] )
      iota      = float( row['avg_integrand'] )
      check     = no_effect_iota(age)
      rel_error = (iota - check) / check
      assert abs(rel_error) < 1e-4
   #
   print('population.py: OK')
#
main()
# END_PROGRAM
