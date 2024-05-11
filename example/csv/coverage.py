# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ----------------------------------------------------------------------------
r'''
{xrst_begin csv.coverage}
{xrst_spell
   cv
   sincidence
   std
   meas
   random random
}

Csv Example Checking Coverage For Asymptotic Samples
####################################################
In order to keep this example simple, and fast to execute:

#. The only model variable is iota and it is constant
   with respect to age and time; see no_effect_rate.csv.

#. The only node (location) is n0 and only the 'both' sex value is fit
   for this node; see node.csv and refit_split in option_fit.csv below.

#. The measurements used the Sincidence integrand so that fitting
   does not need to solve the ode and hence is faster; see simulate.csv.
   (This example is checked every time the at_cascade automated tests
   are run.)

#. The predictions use the prevalence integrand;
   see predict_integrand.csv below.
   We use posterior samples,
   instead of the standard deviation of the samples,
   to approximate the confidence interval because
   the asymptotic distribution of prevalence is not Gaussian
   (The asymptotic distribution of iota is Gaussian).

Age-Time Grid
*************
These are the age and time points that appear in the
:ref:`csv.simulate@Input Files@covariate.csv` file
and the prediction files; see
:ref:`csv.predict@Output Files@fit_predict.csv@age` and time in csv.predict.
{xrst_code py}'''
age_grid   = [ 0.0,  100.0]
time_grid  = [ 1980, 2020]
'''{xrst_code}
Note that Sincidence is predicted for the different
age and time pairs (but do not depend on age or time for this example).

Truth
*****
These are the true value for iota and omega; i.e., the values
used by :ref:`csv.simulate-name` when it simulates the data:
{xrst_code py}'''
true_iota  = 0.01
true_omega = 0.02
'''{xrst_code}
The value of omega is specified in covariate.csv below and
constrained to this value during :ref:`csv.fit-name`
The value of iota is estimated by maximizing the likelihood of the data.

Random Seed
***********
This is the random seed for this example.
Seeding the random number generator is made complicated by the fact that
this example uses multiple calls to :ref:`csv.simulate-name` and
:ref:`csv.fit-name` and each call needs to use a different random seed.
This is done in a way so that if the random seed below is the same,
the result for this example will be reproduced.
{xrst_code py}'''
import time
import random
random_seed = int( time.time() )
random.seed( random_seed )
'''{xrst_code}
Note that the choice above for the random seed changes each time this
example is run.

Number Data Per Fit
*******************
This is the number of data points in each data set; i.e., each fit.
{xrst_code py}'''
n_data_per_fit  = 1
'''{xrst_code}

Number Samples Per Fit
**********************
This is the number of samples from the asymptotic distribution
that generated for each fit.
This is also the number of times each prediction is repeated.
{xrst_code py}'''
n_sample_per_fit = 40
'''{xrst_code}
The more samples per fit, the more accurate the standard deviation
that approximates the posterior statistics.

Number of Fits
**************
This is the number of times a data set is simulated and fit.
The larger this number, the more accurate sample probability that
the fit will be withing the confidence limits.
{xrst_code py}'''
number_fit = 40
assert number_fit % 4 == 0
'''{xrst_code}
The more fits, the more accurate the test of how often the fit is in the
confidence limits.
The time to run this example divided by *number_fit* should be nearly constant.
We require number_fit to be zero mod 4 because the lower and upper
confidence limits correspond to 1/4 below and 1/4 above.

Measurement Noise CV
********************
This the coefficient of variation for the Gaussian measurement noise; i.e.,
the measurement standard deviation is the measurement mean times this value.
{xrst_code py}'''
meas_std_cv = 1.0
'''{xrst_code}

Source Code
***********
{xrst_literal
   # BEGIN PYTHON
   # END PYTHON
}

{xrst_end csv.coverage}
------------------------------------------------------------------------------
'''
# BEGIN PYTHON
import os
import sys
import shutil
import numpy
import scipy
# import at_cascade with a preference current directory version
current_directory = os.getcwd()
if os.path.isfile( current_directory + '/at_cascade/__init__.py' ) :
   sys.path.insert(0, current_directory)
import at_cascade
# ----------------------------------------------------------------------------
# simulation files
# ----------------------------------------------------------------------------
#
# sim_file
sim_file = dict()
#
# option_sim.csv
# The random_seed will get replaced by the next_random_seed function below.
sim_file['option_sim.csv'] = \
'''name,value
absolute_tolerance,1e-10
float_precision,12
random_seed,0
'''
#
# node.csv
sim_file['node.csv'] = \
'''node_name,parent_name
n0,
'''
#
# covariate.csv
sim_file['covariate.csv']  = 'node_name,sex,age,time,omega\n'
for sex in [ 'male', 'female' ] :
   for age in age_grid :
      for time in time_grid :
         sim_file['covariate.csv'] += f'n0,{sex},{age},{time},{true_omega}\n'
#
# no_effect_rate.csv
sim_file['no_effect_rate.csv'] = 'rate_name,age,time,rate_truth\n'
sim_file['no_effect_rate.csv'] += f'iota,50,2000,{true_iota}\n'
#
# multiplier_sim.csv
sim_file['multiplier_sim.csv'] = \
'multiplier_id,rate_name,covariate_or_sex,multiplier_truth\n'
#
# simulate.csv
header  = 'simulate_id,integrand_name,node_name,sex,age_lower,age_upper,'
row     = 'Sincidence,n0,both,50,50,'
#
header += 'time_lower,time_upper,meas_std_cv,meas_std_min\n'
row    += f'2000,2000,{meas_std_cv},0.0\n'
#
sim_file['simulate.csv'] = header
for simulate_id in range( n_data_per_fit ) :
   sim_file['simulate.csv'] += f'{simulate_id},' + row
# ----------------------------------------------------------------------------
# fit files
# ----------------------------------------------------------------------------
#
# fit_file
fit_file = dict()
#
# option_fit.csv
# The ode step size should not matter because we are using iota_pos_rho_zero.
# The random_seed will get replaced by the next_random_seed function below.
fit_file['option_fit.csv']  =  \
'''name,value
refit_split,false
quasi_fixed,false
tolerance_fixed,1e-8
max_num_iter_fixed,50
ode_method,iota_pos_rho_zero
ode_step_size,1.0
'''
fit_file['option_fit.csv'] += f'number_sample,{n_sample_per_fit}\n'
fit_file['option_fit.csv'] += 'random_seed,0\n'
#
# option_predict.csv
fit_file['option_predict.csv']  =  \
'''name,value
float_precision,12
max_number_cpu,2
'''
#
# fit_goal.csv
fit_file['fit_goal.csv'] = \
'''node_name
n0
'''
#
# predict_integrand.csv
fit_file['predict_integrand.csv'] = \
'''integrand_name
prevalence
'''
#
# prior.csv
fit_file['prior.csv'] = \
'''name,density,mean,std,eta,lower,upper
uniform_eps_1,uniform,0.02,,,1e-6,1.0
'''
#
# parent_rate.csv
fit_file['parent_rate.csv'] = \
'''rate_name,age,time,value_prior,dage_prior,dtime_prior,const_value
iota,50.0,2000.0,uniform_eps_1,,,
'''
#
# child_rate.csv
fit_file['child_rate.csv'] = \
'''rate_name,value_prior
'''
#
# mulcov.csv
fit_file['mulcov.csv'] = \
'''covariate,type,effected,value_prior,const_value
'''
# ----------------------------------------------------------------------------
# next_random_seed
def next_random_seed(option_file) :
   option_table = at_cascade.csv.read_table(option_file)
   max_int      = 2**31 - 1
   found        = False
   for row in option_table :
      if row['name'] == 'random_seed' :
         found        = True
         new_seed     = random.randint(1, max_int)
         row['value'] = str(new_seed)
   assert found
   at_cascade.csv.write_table(option_file, option_table)
# -----------------------------------------------------------------------------
# sim
# Simulate the data for one fit
def run_sim(sim_dir) :
   #
   # write input csv files
   for name in sim_file :
      file_name = f'{sim_dir}/{name}'
      file_ptr  = open(file_name, 'w')
      file_ptr.write( sim_file[name] )
      file_ptr.close()
   #
   # option_sim.csv
   file_name = f'{sim_dir}/option_sim.csv'
   next_random_seed(file_name)
   #
   # csv.simulate
   at_cascade.csv.simulate(sim_dir)
   #
   # data_join.csv
   at_cascade.csv.join_file(
      left_file   = f'{sim_dir}/simulate.csv' ,
      right_file  = f'{sim_dir}/data_sim.csv' ,
      result_file = f'{sim_dir}/data_join.csv',
   )
# -----------------------------------------------------------------------------
# fit
# Do one fit
def run_fit(sim_dir, fit_dir) :
   #
   # node.csv, covarite.csv
   for file_name in [ 'node.csv', 'covariate.csv' ] :
      shutil.copyfile(
         src = f'{sim_dir}/{file_name}' ,
         dst = f'{fit_dir}/{file_name}' ,
      )
   #
   # csv files in fit_file
   for name in fit_file :
      file_name = f'{fit_dir}/{name}'
      file_ptr  = open(file_name, 'w')
      file_ptr.write( fit_file[name] )
      file_ptr.close()
   #
   # option_fit.csv
   file_name = f'{fit_dir}/option_fit.csv'
   next_random_seed(file_name)
   #
   #
   # data_join_table
   # This is a join of simulate.csv and dats_sim.csv
   data_join_table = at_cascade.csv.read_table(
      file_name = f'{sim_dir}/data_join.csv'
   )
   #
   # table
   table = list()
   #
   # row_join
   for row_join in data_join_table :
      assert row_join['integrand_name'] == 'Sincidence'
      #
      # row_in
      row_in = dict()
      copy_list  = [ 'integrand_name', 'node_name', 'sex' ]
      copy_list += [ 'age_lower', 'age_upper', 'time_lower', 'time_upper' ]
      copy_list += [ 'meas_value', 'meas_std' ]
      for key in copy_list :
         row_in[key] = row_join[key]
      #
      row_in['data_id']        = row_join['simulate_id']
      row_in['hold_out']       = '0'
      row_in[ 'density_name' ] = 'gaussian'
      row_in[ 'eta' ]          = ''
      row_in[ 'nu' ]           = ''
      #
      # table
      table.append( row_in )
   #
   # data_in.csv
   at_cascade.csv.write_table(
         file_name = f'{fit_dir}/data_in.csv' ,
         table     = table ,
   )
   #
   # fit
   at_cascade.csv.fit(fit_dir)
# -----------------------------------------------------------------------------
def posterior_fit(fit_dir) :
   #
   # n_grid
   n_grid = len(age_grid) * len(time_grid)
   #
   # table
   table = at_cascade.csv.read_table(
      file_name = f'{fit_dir}/fit_predict.csv'
   )
   assert len(table) == n_grid
   #
   # fit
   fit = dict()
   for age in age_grid :
      fit[age] = dict()
   #
   # predict
   for row in table :
      age           = float( row['age'] )
      time          = float( row['time'] )
      avg_integrand = float( row['avg_integrand'] )
      fit[age][time] = avg_integrand
   #
   return fit
# -----------------------------------------------------------------------------
def posterior_truth(fit_dir) :
   #
   # n_grid
   n_grid = len(age_grid) * len(time_grid)
   #
   # table
   table = at_cascade.csv.read_table(
      file_name = f'{fit_dir}/fit_predict.csv'
   )
   assert len(table) == n_grid
   #
   # truth
   truth = dict()
   for age in age_grid :
      truth[age] = dict()
   #
   # predict
   for row in table :
      age           = float( row['age'] )
      time          = float( row['time'] )
      avg_integrand = float( row['avg_integrand'] )
      truth[age][time] = avg_integrand
   #
   return truth
# -----------------------------------------------------------------------------
def posterior_sample(fit_dir) :
   #
   # truth
   truth = posterior_truth(fit_dir)
   #
   # fit
   fit  = posterior_fit(fit_dir)
   #
   # n_grid
   n_grid = len(age_grid) * len(time_grid)
   #
   # table
   table = at_cascade.csv.read_table(
      file_name = f'{fit_dir}/sam_predict.csv'
   )
   assert len(table) == n_grid * n_sample_per_fit
   #
   # sample_list
   sample_list = dict()
   for age in age_grid :
      sample_list[age] = dict()
      for time in time_grid :
         sample_list[age][time] = list()
   #
   # sample_list
   # We shift the samples from being centered on the fit to being centered
   # on the truth. This enables us to check how often a fits falls within
   # the confidence interval from the truth.
   for row in table :
      age           = float( row['age'] )
      time          = float( row['time'] )
      avg_integrand = float( row['avg_integrand'] )
      shift         = truth[age][time] - fit[age][time]
      assert age in age_grid
      assert time in time_grid
      sample_list[age][time].append( avg_integrand + shift )
   #
   # sample_list
   for age in age_grid :
      for time in time_grid :
         assert len( sample_list[age][time] ) == n_sample_per_fit
         sample_list[age][time] = sorted( sample_list[age][time] )
   #
   return sample_list
# -----------------------------------------------------------------------------
def main() :
   #
   # sim_dir
   sim_dir = 'build/example/csv/sim'
   at_cascade.empty_directory(sim_dir)
   #
   # fit_dir
   fit_dir = 'build/example/csv/fit'
   at_cascade.empty_directory(fit_dir)
   #
   # fit_list
   fit_list = dict()
   for age in age_grid :
      fit_list[age] = dict()
      for time in time_grid :
         fit_list[age][time] = list()
   #
   # fit_list, posterior_sam
   for i_fit in range(number_fit) :
      #
      # fit_dir/n0
      at_cascade.empty_directory( f'{fit_dir}/n0' )
      os.rmdir( f'{fit_dir}/n0' )
      #
      # run_sim
      run_sim(sim_dir)
      #
      # run_fit
      run_fit(sim_dir, fit_dir)
      #
      # predict
      at_cascade.csv.predict(fit_dir, sim_dir)
      #
      # posterior_sam
      if i_fit == 0 :
         posterior_sam = posterior_sample(fit_dir)
      #
      # fit_list
      fit = posterior_fit(fit_dir)
      for age in age_grid :
         for time in time_grid :
            fit_list[age][time].append( fit[age][time] )
   #
   # lower_index, upper_index
   # sample index corresponding to 1/4 of the values below (above)
   lower_index = round( n_sample_per_fit / 4 )
   upper_index = round( n_sample_per_fit * 3 / 4 )
   #
   # sample_lower, sample_upper
   sample_lower = dict()
   sample_upper = dict()
   for age in age_grid :
      sample_lower[age] = dict()
      sample_upper[age] = dict()
      for time in time_grid :
         sample_lower[age][time] = posterior_sam[age][time][lower_index]
         sample_upper[age][time] = posterior_sam[age][time][upper_index]
   #
   #
   # age
   # Exclude age zero because prevalence at age zero is indentically zero.
   ok = True
   for age in age_grid[1 :] :
      # time
      for time in time_grid :
         assert len(fit_list[age][time]) == number_fit
         count = 0
         lower = sample_lower[age][time]
         upper = sample_upper[age][time]
         for fit in fit_list[age][time] :
            if lower < fit and fit < upper :
               count += 1
         probability = count / number_fit
         msg  = f'random_seed = {random_seed}, '
         msg += f'age = {age}, '
         msg += f'time = {time}, '
         msg += f'lower = {lower:.4f}, '
         msg += f'upper = {upper:.4f}, '
         msg += f'probability = {probability}'
         print( msg )
         # print( f'fit_list =\n{fit_list}' )
         # 0.5 should be the probability of being within the limits
         ok = ok and abs( probability - 0.5 ) <= 0.2
   assert ok
   #
   print('csv.coverage: OK')
   sys.exit(0)
# -----------------------------------------------------------------------------
main()
# END PYTHON
