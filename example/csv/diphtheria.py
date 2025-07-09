# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-25 Bradley M. Bell
# ----------------------------------------------------------------------------
# imports
import time
import os
import sys
import shutil
import numpy
current_directory = os.getcwd()
if os.path.isfile( current_directory + '/at_cascade/__init__.py' ) :
   sys.path.insert(0, current_directory)
import at_cascade
'''
{xrst_begin csv.diphtheria}
{xrst_spell
   const
   dage
   dtime
   mtwith
   mtexcess
   mtspecific
   Sincidence
   num
   cv
   pos
   meas
   iter
   std
   dtp
}

Csv Example Simulating, Fitting and Predicting Diphtheria
#########################################################

Under Construction
******************

Global Variables
****************
Global variables besides
:ref:`csv.diphtheria@sim_file` and :ref:`csv.diphtheria@fit_file`.
Variables that do not appear in a heading are temporaries.

ode_step_size
=============
The step size used to approximate the ode solution and to
average integrals with respect to age and time.
{xrst_code py}'''
ode_step_size = 5.0
'''{xrst_code}

integrand_list
==============
Generate data and predict for the following integrands:
{xrst_code py}'''
integrand_list = [ 'mtexcess', 'mtspecific', 'mtwith', 'Sincidence' ]
'''{xrst_code}

age_grid, time_grid
===================
Use this age-time grid for values the covariate grid and the
parent rage grid.
{xrst_code py}'''
#
age_grid = dict()
age_grid['iota'] = [ 0.0, 100.00 ]
age_grid['chi']  = [ 0.0 ]
age_grid['rho']  = [ 0.0 ]
age_grid['all']  = sorted( set(
   [100.0] + age_grid['iota'] + age_grid['chi'] + age_grid['rho']
) )
#
time_grid = dict()
time_grid['iota'] = [ 1980.0, 2025.0 ]
time_grid['chi']  = [ 1980.0 ]
time_grid['rho']  = [ 1980.0 ]
time_grid['all']  = sorted( set(
   [2025.0] + time_grid['iota'] + time_grid['chi'] + time_grid['rho']
) )
'''{xrst_code}

node_dict
=========
Keys are nodes,  values are corresponding parent node:
{xrst_code py}'''
node_dict = {
   'n0' : ''   ,
   'n1' : 'n0' ,
   'n2' : 'n0' ,
}
'''{xrst_code}

no_effect_rate_truth
====================
The true values (values used during simulation) for iota, rho, and chi
are constant w.r.t age and time:
{xrst_code py}'''
no_effect_rate_truth = {
   'iota' : 1e-6  ,
   'rho'  : 13.0 ,
   'chi'  : 1e-1 ,
}
'''{xrst_code}

omega_truth
===========
{xrst_code py}'''
omega_truth      = 0.02
'''{xrst_code}

std_random_effects_truth
========================
This is the true standard deviation of the random effects
{xrst_code py}'''
std_random_effects_truth = 1.0
'''{xrst_code}

dtp3_multiplier_truth
=====================
This factor multiples the dtp3 covariate to get the reduction in diphtheria
incidence due to the vaccine:
{xrst_code py}'''
dtp3_multiplier_truth = -3.0
'''{xrst_code}

sim_file
********
Input CSV files that are placed in the simulate directory:
{xrst_code py}'''
sim_file = dict()
'''{xrst_code}

option_sim.csv
==============
{xrst_code py}'''
sim_file['option_sim.csv'] =  \
   'name,value\n' + \
   'float_precision,5\n' + \
   'random_depend_sex,false\n' + \
   f'integrand_step_size,{ode_step_size}\n' + \
   f'std_random_effects_iota,{std_random_effects_truth}\n'
'''{xrst_code}
node.csv
========
{xrst_code py}'''
sim_file['node.csv'] = \
'node_name,parent_name\n'
for node_name in node_dict :
   parent_name = node_dict[node_name]
   sim_file['node.csv'] += f'{node_name},{parent_name}\n'
'''{xrst_code}

covariate.csv
=============
The covariate dtp3 is the fraction of the population that received the
diphtheria-tetanus-pertussis vaccine during their first year of life.
{xrst_code py}'''
sim_file['covariate.csv'] = 'node_name,sex,age,time,omega,dtp3\n'
for node_name in node_dict :
   for sex in [ 'female', 'male' ] :
      for age in age_grid['all' ] :
         for time in time_grid['all'] :
            r     = (time - 2020.0) / 100.0
            dtp3  = 0.9 * ( 1.0 - r * r )
            row   = f'{node_name},{sex},{age},{time},{omega_truth},{dtp3}\n'
            sim_file['covariate.csv'] += row
'''{xrst_code}

multiplier_sim.csv
==================
There are is one covariate multiplier in this example.
{xrst_code py}'''
sim_file['multiplier_sim.csv'] = \
   'multiplier_id,rate_name,covariate_or_sex,multiplier_truth\n' + \
   f'0,iota,dtp3,{dtp3_multiplier_truth}'
'''{xrst_code}

simulate.csv
============
{xrst_code py}'''
header  = 'simulate_id,integrand_name,node_name,sex,age_lower,age_upper,'
header += 'time_lower,time_upper,meas_std_cv,meas_std_min\n'
meas_std_cv     = 1.0
std_min         = 1e-6
simulate_id     = 0
sim_file['simulate.csv'] = header
for integrand_name in integrand_list :
   for node_name in node_dict :
      for sex in [ 'female', 'male' ] :
         for age in age_grid['all'] :
            for time in time_grid['all'] :
               row  = f'{simulate_id},{integrand_name},{node_name},{sex},'
               row += f'{age},{age},{time},{time},'
               row += f'{meas_std_cv},{std_min}\n'
               sim_file['simulate.csv'] += row
               simulate_id += 1
'''{xrst_code}

no_effect_rate.csv
==================
The no effect rates are constant, w.r.t age and time, during the simulation.
{xrst_code py}'''
sim_file['no_effect_rate.csv'] = 'rate_name,age,time,rate_truth\n'
for rate_name in no_effect_rate_truth :
   rate_truth = no_effect_rate_truth[rate_name]
   sim_file['no_effect_rate.csv'] += f'{rate_name},0.0,0.0,{rate_truth}\n'
'''{xrst_code}

fit_file
********
Input CSV files that are placed in the fit directory:
{xrst_code py}'''
fit_file = dict()
'''{xrst_code}

Copies of Simulation Files
==========================
{xrst_code py}'''
fit_file['node.csv']      = sim_file['node.csv']
fit_file['covariate.csv'] = sim_file['covariate.csv']
'''{xrst_code}

option_fit.csv
==============
#. The priors for iota are uniform.
   We use ``censor_asymptotic`` to make sure we do not get
   negative samples for iota and prevalence, which would cause
   the predictions to fail.
#. We are completely ignoring the mtexcess data.
   It gets set to zero just before the fit, to test ignoring it.
{xrst_code py}'''
fit_file['option_fit.csv']  =  \
"""name,value
max_fit,500
max_fit_parent,10000
sample_method,censor_asymptotic
max_num_iter_fixed,50
root_node_name,n0
refit_split,false
max_abs_effect,4
quasi_fixed,false
child_prior_std_factor,2
ode_method,iota_pos_rho_pos
balance_sex,false
freeze_type,mean
child_prior_std_factor_mulcov,1
tolerance_fixed,1e-10
no_ode_ignore,mtexcess
hold_out_integrand,mtexcess
"""
fit_file['option_fit.csv'] += f'ode_step_size,{ode_step_size}\n'
'''{xrst_code}

option_predict.csv
==================
A predict is run using the same directory as the corresponding fit.
All of its input files are also inputs for the fit except for
the option_predict.csv file.
{xrst_code py}'''
fit_file['option_predict.csv']  =  \
"""name,value
db2csv,true
plot,true
float_precision,5
"""
'''{xrst_code}

fit_goal.csv
============
An empty fit_goal.csv corresponds to fitting n0 an n1 (skipping n2):
{xrst_code py}'''
fit_file['fit_goal.csv'] = \
"""node_name
n1
"""
'''{xrst_code}

prior.csv
=========
We are using a uniform because we have good data,
know the true random effects, and are trying to reproduce it with the fit.
(Often one uses a Gaussian prior on the random effects.)
We are using a Gaussian for the fixed effects.
If we used a uniform for the fixed effects,
the child prior standard deviations would not matter.
Note that the stand deviation at the root level is 1.0
(which is very large relative to the true rate values).
{xrst_code py}'''
delta_prior_std        = 0.2
fit_file['prior.csv']  = \
   'name,density,mean,std,eta,lower,upper\n' + \
   f'delta_prior,log_gaussian,0.0,{delta_prior_std},1e-10,,\n' + \
   f'random_effects_prior,uniform,0.0,,,,,\n'
for rate_name in no_effect_rate_truth :
   rate_truth = no_effect_rate_truth[rate_name]
   if rate_name == 'rho' :
      lower = rate_truth
      upper = rate_truth
   else :
      lower      = rate_truth / 10.0
      upper      = rate_truth * 10.0
   fit_file['prior.csv'] += \
      f'prior_{rate_name},gaussian,{rate_truth},1.0,,{lower},{upper}\n'
'''{xrst_code}

parent_rate.csv
===============
The rates are constant during simulation, but not during fitting.
{xrst_code py}'''
fit_file['parent_rate.csv'] = \
   'rate_name,age,time,value_prior,dage_prior,dtime_prior,const_value\n'
for rate_name in no_effect_rate_truth :
   for age in age_grid[rate_name] :
      for time in time_grid[rate_name] :
         row  = f'{rate_name},{age},{time},prior_{rate_name},'
         row += 'delta_prior,delta_prior,\n'
         fit_file['parent_rate.csv'] += row
'''{xrst_code}

child_rate.csv
==============
{xrst_code py}'''
fit_file['child_rate.csv'] = \
"""rate_name,value_prior
iota,random_effects_prior
"""
'''{xrst_code}

mulcov.csv
==========
{xrst_code py}'''
fit_file['mulcov.csv'] = \
   'covariate,type,effected,value_prior,const_value\n' + \
   f'dtp3,rate_value,iota,,{dtp3_multiplier_truth}\n'
'''{xrst_code}

predict_integrand.csv
=====================
{xrst_code py}'''
fit_file['predict_integrand.csv'] = 'integrand_name\n'
for integrand_name in integrand_list :
   fit_file['predict_integrand.csv'] += f'{integrand_name}\n'
'''{xrst_code}

Rest of Source Code
*******************
{xrst_literal
   BEGIN PYTHON
   END PYTHON
}
{xrst_end csv.diphtheria}
'''
# ----------------------------------------------------------------------------
# BEGIN PYTHON
def sim(sim_dir ) :
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
# ---------------------------------------------------------------------------
def fit(sim_dir, fit_dir) :
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
   # copy_row
   # columns that are just copied from data_join_table to data_in_table
   copy_column  = [ 'integrand_name', 'node_name', 'sex' ]
   copy_column += [ 'age_lower', 'age_upper', 'time_lower', 'time_upper' ]
   copy_column += [ 'meas_std']
   #
   # data_in_table
   data_in_table = list()
   for row_join in data_join_table :
      #
      # row_in
      row_in            = dict()
      for key in copy_column :
         row_in[key] = row_join[key]
      #
      # row_in
      # All the mtexcess data is ignored; see option_fit.csv table.
      # The model for mtspecific is not numerically stable near zero prevalence.
      row_in['data_id']       = row_join['simulate_id']
      row_in['density_name']  = 'gaussian'
      row_in['hold_out']      = 0
      if row_join['integrand_name'] == 'mtexcess' :
         row_in['meas_value']    = 0
      else :
         row_in['meas_value']    = row_join['meas_mean']
      if float( row_join['age_upper'] ) <= ode_step_size :
         if row_join['integrand_name'] == 'mtspecific' :
            row_in['hold_out'] = 1
      #
      # data_in_table
      data_in_table.append( row_in )
   #
   # data_in.csv
   at_cascade.csv.write_table(
      file_name = f'{fit_dir}/data_in.csv' ,
      table     = data_in_table            ,
   )
   #
   # fit
   at_cascade.csv.fit(fit_dir)
# ---------------------------------------------------------------------------
def check_variable_csv(fit_dir) :
   file_name      = f'{fit_dir}/n0/variable.csv'
   variable_table = at_cascade.csv.read_table(file_name)
   for row in variable_table :
      fit_value = float( row['fit_value'] )
      truth     = float( row['truth'] )
      if truth == 0.0 :
         assert fit_value == 0.0
      else :
         # This test failed before 2025-07-07 because the covariate reference
         # used for the random effects in set_truth.py were not correct.
         relerr = ( 1.0 - fit_value / truth )
         assert abs(relerr) < 5e-2

# ---------------------------------------------------------------------------
def check_fit_predict(fit_dir) :
   #
   # predict_table
   predict_table = dict()
   for prefix in [ 'fit', 'tru' ] :
      file_name = f'{fit_dir}/{prefix}_predict.csv'
      predict_table[prefix] = at_cascade.csv.read_table(file_name)
   #
   # predict_table
   key = lambda row : (
      int( row['avgint_id'] ) ,
      row['node_name'] ,
      row['sex'] ,
      row['fit_node_name'] ,
      row['fit_sex']
   )
   for prefix in [ 'fit', 'tru' ] :
      predict_table[prefix] = sorted(predict_table[prefix], key=key)
   #
   # i
   for i in range( len(predict_table['tru'] ) ) :
      #
      # tru_value, fit_value
      tru_row        = predict_table['tru'][i]
      fit_row        = predict_table['fit'][i]
      #
      assert int(tru_row['avgint_id']) == int(fit_row['avgint_id'])
      assert tru_row['integrand_name'] == fit_row['integrand_name']
      #
      tru_value      = float( tru_row['avg_integrand'] )
      fit_value      = float( fit_row['avg_integrand'] )
      #
      # check fit_value
      if tru_value == 0.0 :
         assert fit_value == 0.0
      else :
         relerr = 1.0 - fit_value / tru_value
         assert abs(relerr) < 5e-2
   #
# ---------------------------------------------------------------------------
if __name__ == '__main__' :
   #
   # sim_dir
   sim_dir = 'build/example/csv/sim'
   at_cascade.empty_directory(sim_dir)
   #
   # sim
   sim(sim_dir)
   #
   # fit_dir
   fit_dir = 'build/example/csv/fit'
   at_cascade.empty_directory(fit_dir)
   #
   # fit
   fit(sim_dir, fit_dir)
   #
   # predict
   at_cascade.csv.predict(fit_dir, sim_dir)
   #
   # check_variable_csv
   check_variable_csv(fit_dir)
   #
   # check_fit_predict
   check_fit_predict(fit_dir)
   #
   print('diphtheria.py: OK')
# END PYTHON
