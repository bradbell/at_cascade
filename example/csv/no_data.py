# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-25 Bradley M. Bell
# ----------------------------------------------------------------------------
import os
import sys
import time
import numpy
# import at_cascade with a preference current directory version
current_directory = os.getcwd()
if os.path.isfile( current_directory + '/at_cascade/__init__.py' ) :
   sys.path.insert(0, current_directory)
import at_cascade
"""
{xrst_begin csv.no_data}
{xrst_spell
  diota
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
listed below.
The number of samples is huge so that the sample covariance
is close to the true covariance (for testing).

.. csv-table::
   :header: Name, Value
   :delim: |

   tolerance_fixed | this is set small, 1e-8, so we can check accuracy.
   random_seed | chosen using current seconds reported by python time package.
   number_sample | The number of samples of the posterior for each fit

{xrst_code py}"""
random_seed    = str( int( time.time() ) )
number_sample  = 10000
csv_file['option_fit.csv']  = 'name,value\n'
csv_file['option_fit.csv'] += 'tolerance_fixed,1e-8\n'
csv_file['option_fit.csv'] += f'random_seed,{random_seed}\n'
csv_file['option_fit.csv'] += f'number_sample,{number_sample}\n'
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
This example only fits the root node n0.
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

iota_std
********
This is the standard deviation value of iota in the gauss_eps_1 prior:
{xrst_code py}"""
iota_std = 0.1
"""{xrst_code}

diota_std
*********
This is the standard deviation of the iota age difference in gauss_0d prior:
{xrst_code py}"""
diota_std = 0.2
"""{xrst_code}

prior.csv
*********
We define three priors:

.. csv-table::
   :widths: auto
   :delim: ;

   gauss_eps_1; a Gaussian with lower eps, upper 1, iota_mean, iota_std
   gauss_0_d;    a Gaussian with mean 0 standard deviation diota_std

{xrst_code py}"""
csv_file['prior.csv'] = \
   'name,lower,upper,mean,std,density\n' \
   f'gauss_eps_1,1e-6,1.0,{iota_mean},{iota_std},gaussian\n' \
   f'gauss_0_d,,,0.0,{diota_std},gaussian\n'
"""{xrst_code}

parent_rate.csv
***************
The only non-zero rates are omega and iota
(omega is known and specified by the covariate.csv file).
The model for iota is linear w.r.t age and constant w.r.t. time.
Its value prior is gauss_eps_1 and its dage prior is gauss_0_d.
It does not have any dtime priors because
there are no time differences between grid values.
{xrst_code py}"""
csv_file['parent_rate.csv'] = \
'''rate_name,age,time,value_prior,dage_prior,dtime_prior,const_value
iota,0.0,2000,gauss_eps_1,gauss_0_d,,
iota,100.0,2000,gauss_eps_1,gauss_0_d,,
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
r"""{xrst_code}

Negative Log Likelihood
***********************
The standard deviation in the difference prior above is one.
Consider the root job; i.e., the fit for node n0 and both sexes.
Two times the negative log likelihood for this example :math:`2 L(x)` is:

.. math::

   2 L( x ) =
      - \log( 2 \pi d^2 )
      + \left( \frac{ x_1 - x_0 }{ d } \right)^2
      + \sum_{j=0}^1
         - \log( 2 \pi \sigma^2 )
         + \left( \frac{ x_j - \bar{\iota} }{ \sigma } \right)^2

where
:math:`x_0` is iota at age 0,
:math:`x_1` is iota at age 100,
:math:`\bar{\iota}` is *iota_mean* ,
:math:`\sigma` is *iota_std* ,
:math:`d` is *diota_std* ,

Gradient
========
The partial of :math:`L(x)` with respect to :math:`x_j` is:

.. math::

   \frac{ \partial L(x)} { \partial x_j } =
      \frac{x_j - x_{1-j}}{ d^2 }  + \frac{ x_j - \bar{\iota} }{ \sigma^2 }

Hessian
=======
The second partial of :math:`L(x)` with respect to :math:`x_j` is:

.. math::

   \frac{ \partial^2 L(x)} { \partial x_j^2 } = d^{-2} + \sigma^{-2}

The cross partial with respect to :math:`x_0` and :math:`x_1` is:

.. math::

   \frac{ \partial^2 L(x)} { \partial x_0 \partial x_1 } = - d^{-2}

The Hessian of :math:`L(x)` is:

.. math::

   H & =
   \begin{bmatrix}
   d^{-2} + \sigma^{-2} & -d^{-2} \\
   -d^{-2}              & d^{-2} + \sigma^{-2}
   \end{bmatrix}
   \\
   H & =
   d^{-2} \begin{bmatrix}
   1 + ( d / \sigma )^2    & - 1 \\
   - 1                     & 1 + ( d / \sigma )^2
   \end{bmatrix}

The determinant of :math:`d^2 H` is:

.. math::

   \det(d^2 H )  = 2 ( d / \sigma )^2    + ( d / \sigma )^4

The inverse of :math:`d^2 H` is:

.. math::

   d^{-2} H^{-1} & =
      \frac{1}{ 2 ( d / \sigma )^2    + ( d / \sigma )^4    }
      \begin{bmatrix}
      1 + ( d / \sigma )^2    & 1 \\
      1                     & 1 + ( d / \sigma )^2
      \end{bmatrix}
   \\
   d^{-2} H^{-1} & =
      \frac{ ( d / \sigma )^2    }{ 2  + ( d / \sigma )^2    }
      \begin{bmatrix}
      1 + ( d / \sigma )^2    & 1 \\
      1                     & 1 + ( d / \sigma )^2
      \end{bmatrix}

It follows that:

.. math::

   H^{-1} & =
      \frac{ \sigma^{-2} }{ 2  + ( d / \sigma )^2    }
      \begin{bmatrix}
      1 + ( d / \sigma )^2    & 1 \\
      1                     & 1 + ( d / \sigma )^2
      \end{bmatrix}
   \\
   H^{-1} & =
      \frac{ \sigma^{-2} }{ 2 ( \sigma / d )^{-2}  + 1    }
      \begin{bmatrix}
       ( \sigma / d )^{-2}  + 1 & ( \sigma / d )^{-2}  \\
      ( \sigma / d )^{-2}   & ( \sigma / d )^{-2} + 1
      \end{bmatrix}

Covariance of sam_predict.csv
=============================
The covariance of the samples in o
:ref:`csv.fit@Output Files@sam_predict.csv` is equal to
:math:`H^{-1}` .
Note that as :math:`\sigma / d` (i.e. *iota_std* / *diota_std* ) gets small,
the variance of the estimates for iota
gets close to :math:`\sigma^2` (i.e., the square of *iota_std* ) .

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
   # fit_predict
   # 3 sexes, 2 ages
   file_name   = f'{fit_dir}/fit_predict.csv'
   fit_predict = at_cascade.csv.read_table(file_name)
   assert len( fit_predict ) == 3 * 2
   #
   # row
   for row in fit_predict :
      # Sincidence is the only integerand in predict_integrand.csv
      assert row['integrand_name'] == 'Sincidence'
      # n0 is the only node in fit_goal.csv and it has no ancestors
      assert row['node_name'] == 'n0'
      # Since there is no data, only the root job (n0, both) is fit
      assert row['fit_sex'] == 'both'
      # Predictions are made for all sexes
      assert row['sex'] in [ 'female', 'male', 'both' ]
      # There are two age values in covariate.csv
      assert float(row['age']) in [ 0.0, 100.0 ]
      # There is only on time value in covariate.csv
      assert float(row['time']) == 2000.0
      #
      # rel_error
      iota      = float( row['avg_integrand'] )
      rel_error = 1.0 - iota / iota_mean
      assert abs( rel_error ) < 1e-8
   #
   # sam_predict
   # 3 sexes, 2 ages, number_sample samples
   file_name   = f'{fit_dir}/sam_predict.csv'
   sam_predict = at_cascade.csv.read_table(file_name)
   assert len( sam_predict ) == 3 * 2 * number_sample
   #
   # sample_array
   age2variable_index = { 0.0 : 0, 100.0 : 1 }
   sample_array    = numpy.empty( (number_sample, 2) )
   sample_array[:] = numpy.nan
   for row in sam_predict :
      if row['sex'] == 'both' :
         iota           = float( row['avg_integrand'] )
         sample_index   = int( row['sample_index'] )
         age            = float( row['age'] )
         variable_index = age2variable_index[age]
         sample_array[sample_index , variable_index]  = iota
   #
   # sample_cov
   sample_cov = numpy.cov( sample_array , rowvar = False )
   #
   # Hinv
   d2    = 1.0 / ( diota_std * diota_std )
   s2    = 1.0 / ( iota_std * iota_std )
   H     = [ [ d2 + s2 , - d2 ], [ - d2 , d2 + s2 ] ]
   H     = numpy.array(H)
   Hinv  = numpy.linalg.inv(H)
   #
   rel_error = (Hinv - sample_cov) / Hinv
   assert numpy.max( numpy.abs( rel_error ) ) < 0.1
#
#
if __name__ == '__main__' :
   main()
   print('prior_sam: OK')
# END_PROGRAM
