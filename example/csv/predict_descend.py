# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2025 Bradley M. Bell
# ----------------------------------------------------------------------------
#
'''
{xrst_begin csv.predict_descend}
{xrst_spell
   eps
   dage
   dtime
   const
   eps
   std
   Sincidence
}

Example Predicting From Self and a Descendant
#############################################

iota_true
*********
There are only two non-zero rate in this model, omega and the
parent value for *iota* (the model for incidence).
{xrst_code py}'''
omega_true = 0.01
iota_true  = 0.01
'''{xrst_code}

node_dict
*********
Keys are nodes and values are corresponding parent node:
{xrst_code py}'''
node_dict = {
   'n0' : ''   ,
   'n1' : 'n0' ,
   'n2' : 'n0' ,
}
'''{xrst_code}


age_grid, time_grid
*******************
The only rate for this example is *iota* and it is constant in
age and time so we use a very simple age and time grid:
{xrst_code py}'''
age_grid   = [0.0, 100.0]
time_grid  = [1980.0, 2020.0]
'''{xrst_code}

number_sample
*************
This is the number of samples of the posterior distribution
to generate for each successful fit. Note that each sample includes
values for all the dismod_at model variables-name . For this example
there is only one model variable *iota* .
{xrst_code py}'''
number_sample = 4000
'''{xrst_code}

descendant_std_factor
=====================
This is the
:ref:`csv.predict@Input Files@option_predict.csv@descendant_std_factor` .
This example checks that this factor is (is not) used when
predicting for the node that was fit
(for a descendant of the node that was fit).
{xrst_code py}'''
descendant_std_factor = 2.0
'''{xrst_code}




random_seed
***********
We us the current time in seconds to seed the random number generator:
{xrst_code py}'''
import time
random_seed = int( time.time() )
'''{xrst_code}

n_data, std_data
****************
There are *n_data* simulated measurements.
These measurements are a Gaussian with mean *iota_true*
and standard deviation *std_data* :
{xrst_code py}'''
n_data = 1
std_data = iota_true * 0.2
'''{xrst_code}

input_file
**********
Input CSV files that are placed in the fit directory:
{xrst_code py}'''
input_file = dict()
'''{xrst_code}

predict_integrand.csv
=====================
All the measurements and predictions
for this example are for Sincidence; i.e..
a direct measurement of iota:
{xrst_code py}'''
input_file['predict_integrand.csv']  = 'integrand_name\n'
input_file['predict_integrand.csv'] += 'Sincidence\n'
'''{xrst_code}
There are measurements for n0, but not for n1 or n2.
Thus node n0 will predict for itself and for n2
( n1 is not in :ref:`csv.predict_descend@input_file@fit_goal.csv` . )

option_fit.csv
==============
{xrst_code py}'''
input_file['option_fit.csv']  =  \
"""name,value
refit_split,false
"""
input_file['option_fit.csv'] += f'number_sample,{number_sample}\n'
input_file['option_fit.csv'] += f'random_seed,{random_seed}\n'
'''{xrst_code}

option_predict.csv
==================
{xrst_code py}'''
input_file['option_predict.csv']  =  'name,value\n'
input_file['option_predict.csv']  +=  \
   f'descendant_std_factor,{descendant_std_factor}\n'
'''{xrst_code}

fit_goal.csv
============
There will be no fit or predictions for n1:
{xrst_code py}'''
input_file['fit_goal.csv']  = 'node_name\n'
input_file['fit_goal.csv'] += 'n2'
'''{xrst_code}

node.csv
========
{xrst_code py}'''
input_file['node.csv'] = \
'node_name,parent_name\n'
for node_name in node_dict :
   parent_name = node_dict[node_name]
   input_file['node.csv'] += f'{node_name},{parent_name}\n'
'''{xrst_code}

covariate.csv
=============
{xrst_code py}'''
input_file['covariate.csv'] = 'node_name,sex,age,time,omega\n'
for node_name in [ 'n0', 'n1', 'n2' ] :
   for sex in [ 'female', 'male' ] :
      for age in age_grid :
         for time in time_grid :
            row   = f'{node_name},{sex},{age},{time},{omega_true}\n'
            input_file['covariate.csv'] += row
'''{xrst_code}

prior.csv
=========
uniform_eps_0.1 is uniform on the interval [eps,.1] where eps = 1e-6,
the mean, which is only used for initialization, is 0.03.
{xrst_code py}'''
input_file['prior.csv'] = \
"""name,density,mean,std,eta,lower,upper
uniform_eps_0.1,uniform,0.01,,,1e-6,0.1
"""
'''{xrst_code}

parent_rate.csv
===============
The parent rate for *iota* is has a uniform_eps_0.1 prior
and is constant w.r.t. age and time:
{xrst_code py}'''
input_file['parent_rate.csv'] = \
"""rate_name,age,time,value_prior,dage_prior,dtime_prior,const_value
iota,0.0,0.0,uniform_eps_0.1,,,
"""
'''{xrst_code}

child_rate.csv
==============
All the child rates (rate random effects) are zero
{xrst_code py}'''
input_file['child_rate.csv'] = 'rate_name,value_prior\n'
'''{xrst_code}

mulcov.csv
==========
There are no covariate multipliers
{xrst_code py}'''
input_file['mulcov.csv'] = 'covariate,type,effected,value_prior,const_value\n'
r'''{xrst_code}

Hessian of Likelihood
*********************
For this example, *iota* is the only model variable
(that does not have equal lower and upper bounds).
Let :math:`m` be *n_data* ,
:math:`sigma` be *std_data*, and
:math:`y_i` be the measurement values.
The negative log likelihood for the n0 fit is:

.. math::

   L( \iota , y ) = \frac{1}{2} \sum_{i=0}^{m}
      \log \left( 2 \pi \sigma^2 \right)
      +
      \left( \frac{y_i - \iota }{\sigma} \right)^2

The Hessian with respect to iota ( :math:`\iota` ) is

.. math::

   \frac{ \partial^2 }{\partial \iota^2} L = \frac{m}{ \sigma^2 }


Rest of Source Code
*******************
Below is the source code, except for the settings above.
{xrst_literal
   # BEGIN REST_OF_SOURCE
   # END REST_OF_SOURCE
}

{xrst_end csv.predict_descend}
'''
# BEGIN REST_OF_SOURCE
#
# os, sys, copy
import os
import sys
import copy
#
# random
import random
random.seed(random_seed)
#
# at_cascade
current_directory = os.getcwd()
if os.path.isfile( current_directory + '/at_cascade/__init__.py' ) :
   sys.path.insert(0, current_directory)
import at_cascade
#
# fit
def create_input_files(fit_dir) :
   #
   # csv files in input_file
   for name in input_file :
      file_name = f'{fit_dir}/{name}'
      file_ptr  = open(file_name, 'w')
      file_ptr.write( input_file[name] )
      file_ptr.close()
   #
   # data_table
   data_table = list()
   data_id    = -1
   age        = 50.0
   time       = 2000.0
   row = {
      'node_name'      : 'n0',
      'integrand_name' : 'Sincidence',
      'hold_out'       : 0,
      'density_name'   : 'gaussian',
      'age_lower'      : age,
      'age_upper'      : age,
      'time_lower'     : time,
      'time_upper'     : time,
      'eta'            : None,
      'nu'             : None,
      'meas_std'       : std_data,
   }
   for i in range(n_data) :
      if i % 2 == 0 :
         sex = 'female'
      else :
         sex = 'male'
      data_id          += 1
      row['data_id']    = data_id
      row['sex']        = sex
      row['meas_value'] = random.normalvariate( iota_true, std_data )
      data_table.append( copy.copy( row ) )
   #
   # data_in.csv
   at_cascade.csv.write_table(
      file_name = f'{fit_dir}/data_in.csv' ,
      table     = data_table ,
   )
#
# main
def main() :
   #
   # fit_dir
   fit_dir = 'build/example/csv/fit'
   at_cascade.empty_directory(fit_dir)
   #
   # create_input_files
   create_input_files(fit_dir)
   #
   # at_cascade.csv.fit
   at_cascade.csv.fit(fit_dir)
   #
   # at_cascade.csv.predict
   at_cascade.csv.predict(fit_dir)
   #
   # fit
   file_name = f'{fit_dir}/fit_predict.csv'
   fit_predict_table = at_cascade.csv.read_table(file_name);
   fit               = dict()
   for row in fit_predict_table :
      avgint_id = int( row['avgint_id'] )
      node_name = row['node_name']
      sex       = row['sex']
      key       = (avgint_id, node_name, sex)
      assert key not in fit
      fit[key]  = float( row['avg_integrand']  )
   #
   # sam
   file_name = f'{fit_dir}/sam_predict.csv'
   sam_predict_table = at_cascade.csv.read_table(file_name);
   sam               = dict()
   for row in sam_predict_table :
      avgint_id = int( row['avgint_id'] )
      node_name = row['node_name']
      sex       = row['sex']
      key       = (avgint_id, node_name, sex)
      if key not in sam :
         sam[key] = list()
      sam[key].append(  float( row['avg_integrand']  ) )
   #
   # hessian_like
   hessian_like = n_data / ( std_data * std_data )
   #
   # check predctions for n0
   for avgint_id in range(4) :
      key   = ( avgint_id, 'n0', 'both' )
      sumsq = 0.0
      assert number_sample == len( sam[key] )
      for avg_integrand in sam[key] :
         sumsq += ( avg_integrand - fit[key] )**2
      sam_cov = sumsq / number_sample
      relerr  = 1.0 -  sam_cov * hessian_like
      assert abs( relerr ) < 0.05
   #
   # check predctions for n2
   for avgint_id in range(4) :
      for sex in [ 'female', 'male' ] :
         key   = ( avgint_id, 'n2', sex )
         sumsq = 0.0
         assert number_sample == len( sam[key] )
         for avg_integrand in sam[key] :
            sumsq  += ( avg_integrand - fit[key] )**2
         sam_cov    =  sumsq / number_sample
         cov_factor = descendant_std_factor * descendant_std_factor
         relerr     = 1.0 -  (sam_cov / cov_factor) * hessian_like
         assert abs( relerr ) < 0.05
   #
   #
   print('predict_descend.py: OK')
#
if __name__ == '__main__' :
   main()
#
# END REST_OF_SOURCE
