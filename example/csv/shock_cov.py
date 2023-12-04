# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-23 Bradley M. Bell
# ----------------------------------------------------------------------------
import os
import sys
import time
import math
import shutil
# import at_cascade with a preference current directory version
current_directory = os.getcwd()
if os.path.isfile( current_directory + '/at_cascade/__init__.py' ) :
   sys.path.insert(0, current_directory)
import at_cascade
# --------------------------------------------------------------------------
'''
{xrst_begin csv.shock_cov}
{xrst_spell
   bilinear
   const
   cv
   dage
   dtime
   eps
   iter
   meas
   pdf
   sim
   sincidence
   std
   trapezoidal
}

Simulate and Fit Incidence Using Prevalence Data and a Shock Covariate
######################################################################

sim_file, fit_file
******************
These two dictionaries are used to hold the simulation and fit
csv input file data:
{xrst_code py}'''
sim_file = dict()
fit_file = dict()
'''{xrst_code}

random_seed
***********
Get the random seed before we use time as a float variable.
{xrst_code py}'''
random_seed = str( int( time.time() ) )
'''{xrst_code}

Simulation
**********
The setting below are used by :ref:`csv.simulate-name` to
simulate random effects and data.

age_grid, time_grid
===================
We use the same age-time grid for the model and the data in order to keep
the example simple. We are recovering iota (more incidence) from prevalence
measurements. The model for prevalence always has zero for prevalence at age zero.
Putting an age point close to zero increases the probability that some of the
data points near zero will be censored and hence tests fitting censored data.
{xrst_code py}'''
age_grid   = [0.0, 1.0, 25.0, 50.0, 75.0, 100.0]
time_grid  = [1980.0, 2000.0, 2020.0]
'''{xrst_code}

shock_covariate
===============
The shock covariate is zero at each age time grid point except for
age equal 50. and time equal 2000.0 where it is one.
Bilinear interpolation is used to evaluate the shock between grid points.
Thus the closer the other grid points are to (50,2000),
the narrower the shock.
{xrst_code py}'''
def shock_covariate(age, time) :
   if age == 50.0 and time == 2000.0 :
      return 1.0
   return 0.0
'''{xrst_code}

option_sim.csv
==============
#. The files output by the simulation are set to have 4 digits of precision.
#. The random effects are different for female versus male.
   (This seems to require fitting after the female male split.)
#. Only iota has random effects. Note that effects are in log space.
#. Use the random seed chosen above.
{xrst_code py}'''
sim_file['option_sim.csv'] = \
'''name,value
absolute_covariates,shock
float_precision,4
random_depend_sex,true
std_random_effects_iota,.2
'''
sim_file['option_sim.csv'] += f'random_seed,{random_seed}\n'
'''{xrst_code}

node.csv
========
For this example, n0 is the root node.
It has two children, n1 and n2.
{xrst_code py}'''
sim_file['node.csv'] = \
'''node_name,parent_name
n0,
n1,n0
n2,n0
'''
'''{xrst_code}

covariate.csv
=============
#. This sets omega to be constant and equal to *omega_truth* .
#. It also sets the values of the shock covariate on the age-tim grid.
{xrst_code py}'''
omega_truth      = 0.01
sim_file['covariate.csv'] = 'node_name,sex,age,time,omega,shock\n'
for node_name in [ 'n0', 'n1', 'n2' ] :
   for sex in [ 'female', 'male' ] :
      for age in age_grid :
         for time in time_grid :
            shock = shock_covariate(age, time)
            row   = f'{node_name},{sex},{age},{time},{omega_truth},{shock}\n'
            sim_file['covariate.csv'] += row
'''{xrst_code}

multiplier_sim.csv
==================
#. This defines one covariate multiplier that multiplies the
   shock covariate and affects iota.
#. The value of multiplier used during the simulation is *multiplier_truth* .
{xrst_code py}'''
multiplier_truth = 1.0
sim_file['multiplier_sim.csv'] = \
'multiplier_id,rate_name,covariate_or_sex,multiplier_truth\n' + \
f'0,iota,shock,{multiplier_truth}\n'
'''{xrst_code}

simulate.csv
============
#. n_repeat data points are simulated for each combination of
   integrand_name, node_name, sex, age and time below.
#. The mean (meas_meas) and simulated data value (meas_value) are
   be reported for each data point.
#. The prevalence integrand is intended for fitting the data.
#. The Sincidence integrand is intended to be held out so its
   residuals can be used to check the accuracy of the fit.
#. The meas_std_cv is the coefficient of variation used for the
   simulated data noise.
#. The meas_std_min is the minimum value used for the
   standard deviation of the simulated data noise.
#. A larger value for meas_std_cv or meas_std_min will result in a larger
   percent of the simulated data having the value zero.
   This will require a larger value of n_repeat to get a good fit.
{xrst_code py}'''
header  = 'simulate_id,integrand_name,node_name,sex,age_lower,age_upper,'
header += 'time_lower,time_upper,meas_std_cv,meas_std_min\n'
sim_file['simulate.csv'] = header
n_repeat        = 10
simulate_id     = 0
meas_std_cv     = 0.01
meas_std_min    = 0.02
for integrand_name in [ 'Sincidence', 'prevalence' ] :
   for node_name in [ 'n0', 'n1', 'n2' ] :
      for sex in [ 'female', 'male' ] :
         for age in age_grid :
            for time in time_grid :
               for i in range(n_repeat) :
                  row  = f'{simulate_id},{integrand_name},{node_name},{sex},'
                  row += f'{age},{age},{time},{time},'
                  row += f'{meas_std_cv},{meas_std_min}\n'
                  sim_file['simulate.csv'] += row
                  simulate_id += 1
'''{xrst_code}

no_effect_rate.csv
==================
#. The no effect version of a rate
   is the rate without random or covariate effects.
#. This simulation has two non-zero rates, iota and chi.
   The no effect rates for iota and chi are constant and equal to
   *no_effect_iota* and *no_effect_chi* respectively.
#. These rates each have one line in the no_effect_rate.csv file
   because the are constant.
{xrst_code py}'''
no_effect_iota   = 0.02
no_effect_chi    = 0.03
sim_file['no_effect_rate.csv'] = 'rate_name,age,time,rate_truth\n'
sim_file['no_effect_rate.csv'] += f'iota,0,0,{no_effect_iota}\n'
sim_file['no_effect_rate.csv'] += f'chi,0,0,{no_effect_chi}\n'
'''{xrst_code}

Fitting
*******
The setting below are used by :ref:`csv.fit-name` to
fit the simulated data.

node.csv
========
This is a copy of the
:ref:`csv.shock_cov@Simulation@node.csv` file above.

covariate.csv
=============
This is a copy of the
:ref:`csv.shock_cov@Simulation@covariate.csv` file above.

option_fit.csv
==============
#. The shock is a absolute covariate; i.e., its reference value is always zero.
   (The reference value for a relative covariate is its average for
   the particular node and sex being fit.)
#. We are holding out the Sincidence data except during the no_ode fit,
   where it is used to initialize iota for the optimization.
#. We are refitting after the split by sex at node zero.
   This should to be done when the random effects are different between
   females and males.
#. Given that we are using a small number of prevalence points, it is
   necessary for them to be very accurate. This in turn requires a small
   value for ode_step_size.
#. This example seems to fit well using the quasi-Newton and Newton methods;
   i.e., quasi_fixed true and false.
#. A smaller (larger) value of max_num_iter_fixed is
   required when quasi_fixed is true (false).
#. The shock, as a function of age, is not smooth at ages 25.0, 50.0, and 75.0.
   The :ref:`csv.fit@Input Files@option_fit.csv@age_avg_split`
   below instructs at_cascade not to integrate across these points.
{xrst_code py}'''
fit_file['option_fit.csv']  =  \
'''name,value
absolute_covariates,shock
hold_out_integrand,Sincidence
refit_split,true
ode_step_size,5.0
quasi_fixed,false
max_num_iter_fixed,50
tolerance_fixed,1e-8
ode_method,trapezoidal
'''
fit_file['option_fit.csv'] += f'random_seed,{random_seed}\n'
'''{xrst_code}

option_predict.csv
==================
Both the csv files and plot files (pdf files) are generated for each fit.
{xrst_code py}'''
fit_file['option_predict.csv']  =  \
'''name,value
plot,true
db2csv,true
'''
'''{xrst_code}

fit_goal.csv
============
We are fitting from the root node n0 to the goal nodes n1 and n2.
The root node is n0 because root_node_name did not appear in
option_fit.csv above.
{xrst_code py}'''
fit_file['fit_goal.csv'] = \
'''node_name
n1
n2
'''
'''{xrst_code}

prior.csv
=========
Let std denote standard deviation and eta an offset
in the log Gaussian distribution.
The file prior.csv defines the following densities:

.. csv-table::
   :widths: auto
   :header-rows: 1

   Name,Description
   uniform\_-1_1,"a uniform density on the interval [-1,1]"
   uniform\_eps_1,"a uniform density on the interval [1e-6,1]"
   delta_prior,a log Gaussian density with mean 0 std 0.1 and eta 1e-5
   random_prior,a Gaussian density with mean 0 and std 0.2

{xrst_code py}'''
fit_file['prior.csv'] = \
'''name,density,mean,std,eta,lower,upper
uniform_-1_1,uniform,0.0,,,-1.0,1.0
uniform_eps_1,uniform,0.02,,,1e-6,1.0
delta_prior,log_gaussian,0.0,0.01,1e-5,,
age_0_delta,log_gaussian,0.0,0.001,1e-5,,
random_prior,gaussian,0.0,0.2,,,,
'''
'''{xrst_code}

parent_rate.csv
===============
This file defines the parent rate grid and priors for each fit.
For this example, the rate chi is known and constant in age and time.
The parent prior for iota uses
the same grid as for the covariate just to keep the example simple.
At each grid point, the value prior is the uniform_eps_1 prior defined above.
The forward difference prior in age and time is the delta_prior defined above.

Note that when fitting node n0, n1 is a child node and its rate values
correspond to random effects.
On the other hand, when fitting node n1, it is the parent node
and is rate vales is fit on this grid.
{xrst_code py}'''
data = 'rate_name,age,time,value_prior,dage_prior,dtime_prior,const_value\n'
data += f'chi,0.0,0.0,,,,{no_effect_chi}\n'
for age in age_grid :
   for time in time_grid :
      data += f'iota,{age},{time},uniform_eps_1,'
      if age == 0.0 :
         data += 'age_0_delta,delta_prior,\n'
      else :
         data += 'delta_prior,delta_prior,\n'
fit_file['parent_rate.csv'] = data
'''{xrst_code}

child_rate.csv
==============
In csv.fit, child rates are a random effects and are constant in age and time.
Note that when fitting node n0, n1 is a child node and its rate values
correspond to random effects (and hence are in log of rate space).
On the other hand, when fitting node n1, there are not child rates.
{xrst_code py}'''
fit_file['child_rate.csv'] = \
'''rate_name,value_prior
iota,random_prior
'''
'''{xrst_code}

mulcov.csv
==========
In csv.fit,  covariate multipliers are constant in age and time.
As in the data simulation, there is one covariate multiplier.
It multiplies the shock covariate and affects the iota rate.
It prior is the uniform\_-1_1 density defined above.
{xrst_code py}'''
fit_file['mulcov.csv'] = \
'covariate,type,effected,value_prior,const_value\n' + \
'shock,rate_value,iota,uniform_-1_1,,'
'''{xrst_code}

predict_integrand.csv
=====================
The predict integrand will be output on the same grid as the covariates.
We use Sincidence to check the iota fit and
mulcov_0 to check the covariate multiplier fit
(mulcov_0 is the first multiplier in mulcov.csv;
i.e., the one with index zero).

{xrst_code py}'''
fit_file['predict_integrand.csv'] = \
'''integrand_name
Sincidence
mulcov_0
'''
'''{xrst_code}

data_in.csv
===========
The columns in :ref:`csv.fit@Input Files@data_in.csv`
are a direct copy of the corresponding columns in the simulation files
:ref:`csv.simulate@Input Files@simulate.csv` and
:ref:`csv.simulate@Output Files@data_sim.csv` .
The exceptions to this are listed below:

#. The data_id in data_in.csv is equal to the simulate_id in
   simulate.csv and data_sim.csv.

#. The density column is set to gaussian and the eta, nu columns
   are empty.

Source Code
===========
Below is the rest of the source code for this example:
{xrst_literal
   # BEGIN_SOURCE_CODE
   # END_SOURCE_CODE
}

{xrst_end csv.shock_cov}
'''
#
# -----------------------------------------------------------------------------
# BEGIN_SOURCE_CODE
def sim(sim_dir) :
   #
   # write input csv files
   for name in sim_file :
      file_name = f'{sim_dir}/{name}'
      file_ptr  = open(file_name, 'w')
      file_ptr.write( sim_file[name] )
      file_ptr.close()
   #
   # csv.simulate
   at_cascade.csv.simulate(sim_dir)
   #
   # data_join.csv
   at_cascade.csv.join_file(
      left_file   = f'{sim_dir}/simulate.csv' ,
      right_file  = f'{sim_dir}/data_sim.csv' ,
      result_file = f'{sim_dir}/data_join.csv'     ,
   )
# -----------------------------------------------------------------------------
# fit
def fit(sim_dir, fit_dir) :
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
   # fit_goal_set
   fit_goal_table = at_cascade.csv.read_table(
      file_name = f'{fit_dir}/fit_goal.csv'
   )
   fit_goal_set = set()
   for row in fit_goal_table :
      node_name = row['node_name']
      for sex in [ 'female', 'male' ] :
         fit_goal_set.add( (node_name, sex) )
   #
   # data_join_table
   # This is a join of simulate.csv and dats_sim.csv
   data_join_table = at_cascade.csv.read_table(
      file_name = f'{sim_dir}/data_join.csv'
   )
   #
   # data_in.csv
   table = list()
   for row_join in data_join_table :
      #
      # row_in
      row_in = dict()
      copy_list  = [ 'integrand_name', 'node_name', 'sex' ]
      copy_list += [ 'age_lower', 'age_upper', 'time_lower', 'time_upper' ]
      row_in['data_id']   = row_join['simulate_id']
      for key in copy_list :
         row_in[key] = row_join[key]
      row_in['meas_value']    = row_join['meas_value']
      row_in['meas_std']      = row_join['meas_std']
      row_in['hold_out']      = 0
      row_in['density_name']  = 'gaussian'
      #
      table.append( row_in )
   at_cascade.csv.write_table(
         file_name = f'{fit_dir}/data_in.csv' ,
         table     = table ,
   )
   #
   # fit, predict
   at_cascade.csv.fit(fit_dir)
   at_cascade.csv.predict(fit_dir)
   #
   # fit_predict_dict
   fit_predict_table = at_cascade.csv.read_table(
      file_name = f'{fit_dir}/fit_predict.csv'
   )
   #
   # random_effect_dict
   random_effect_table = at_cascade.csv.read_table(
      file_name = f'{sim_dir}/random_effect.csv'
   )
   random_effect_dict = { 'n0' : dict(), 'n1' : dict(), 'n2' : dict() }
   for node_name in random_effect_dict :
      for sex in [ 'female', 'male' ] :
         random_effect_dict[node_name][sex] = dict()
   for row in random_effect_table :
      node_name     = row['node_name']
      sex           = row['sex']
      rate_name     = row['rate_name']
      random_effect = float( row['random_effect'] )
      random_effect_dict[node_name][sex][rate_name] = random_effect
   #
   # row
   max_mul_error    = 0.0
   max_iota_error   = 0.0
   max_iota_age     = 0.0
   predict_node_set = set()
   for row in fit_predict_table :
      node_name = row['node_name']
      sex       = row['sex']
      age       = float( row['age'] )
      if (node_name,sex) in fit_goal_set :
         predict_node_set.add( (node_name, sex) )
         if row['integrand_name'] == 'mulcov_0' :
            avg_integrand = float( row['avg_integrand'] )
            rel_error     = (1.0 - avg_integrand / multiplier_truth)
            max_mul_error = max(max_mul_error, abs(rel_error) )
         if row['integrand_name'] == 'Sincidence' and age != age_grid[-1]:
            # exclude last age because it has very little effect on prealence
            node_name     = row['node_name']
            time          = float( row['time'] )
            avg_integrand = float( row['avg_integrand'] )
            if sex == 'both' :
               random_male   = random_effect_dict[node_name]['male']['iota']
               random_female = random_effect_dict[node_name]['female']['iota']
               random_effect = (random_male + random_female) / 2.0
            else :
               random_effect = random_effect_dict[node_name][sex]['iota']
            cov_effect    = multiplier_truth * shock_covariate(age, time)
            total_effect  = random_effect + cov_effect
            iota          = math.exp(total_effect) * no_effect_iota
            rel_error     = (1.0 - avg_integrand / iota )
            if abs(rel_error) > max_iota_error :
               max_iota_error = abs(rel_error)
               max_iota_age   = age
   if max_mul_error > 0.1 or max_iota_error > 0.1 :
      print( f'max_mul_error  = {max_mul_error}' )
      print( f'max_iota_error = {max_iota_error}' )
      msg = 'cov_shock.py: Relative error is to large (see above)'
      assert False, msg
   if fit_goal_set != predict_node_set :
      difference  = list( fit_goal_set.difference(predict_node_set) )
      (node, sex) = difference[0]
      msg  = f'cov_shock.py: the file {fit_dir}/predict.csv\n'
      msg += f'missing resutls for the fit gloal node.sex = {node}.{sex}'
      assert False, msg
# -----------------------------------------------------------------------------
# Without this, the mac will try to execute main on each processor.
if __name__ == '__main__' :
   #
   # sim_dir
   sim_dir = 'build/example/csv/sim'
   if not os.path.exists(sim_dir) :
      os.makedirs(sim_dir)
   #
   # clear out a previous run
   if os.path.exists( 'build/example/csv/fit/n0' ) :
      shutil.rmtree( 'build/example/csv/fit/n0' )
   #
   # fit_dir
   fit_dir = 'build/example/csv/fit'
   if not os.path.exists(fit_dir) :
      os.mkdir(fit_dir)
   #
   # sim
   sim(sim_dir)
   #
   # fit
   fit(sim_dir, fit_dir)
   #
   print('shock_cov.py: OK')
   sys.exit(0)
# END_SOURCE_CODE
