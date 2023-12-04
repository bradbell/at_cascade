# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-23 Bradley M. Bell
# ----------------------------------------------------------------------------
# imports
import time
import os
import sys
import shutil
current_directory = os.getcwd()
if os.path.isfile( current_directory + '/at_cascade/__init__.py' ) :
   sys.path.insert(0, current_directory)
import at_cascade
'''
{xrst_begin csv.sim_fit_pred}
{xrst_spell
   const
   cv
   dage
   dtime
   iter
   meas
   mtexcess
   rho
   sincidence
   std
   temporaries
}

Csv Example Simulating, Fitting and Predicting
##############################################

Global Variables
****************
Global variables besides sim_file and fit_file.
Variables that do not appear in a heading are temporaries.

integrand_list
==============
Generate data and predict for the following integrands:
{xrst_code py}'''
integrand_list = [ 'Sincidence', 'remission', 'mtexcess', 'prevalence' ]
'''{xrst_code}

age_grid, time_grid
===================
Use this age-time grid for values the covariate grid and the
parent rage grid.
{xrst_code py}'''
age_grid   = [0.0, 20.0, 50.0, 80.0, 100.0]
time_grid  = [1980.0, 2000.0, 2020.0]
'''{xrst_code}

node_dict
=========
Keys are nodes and values are corresponding parent node:
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
   'iota' : 0.02  ,
   'rho'  : 20.0  ,
   'chi'  : 0.001  ,
}
'''{xrst_code}

omega_truth
===========
{xrst_code py}'''
omega_truth      = 0.01
'''{xrst_code}

std_random_effects_truth
========================
This is the true standard deviation of the random effects
{xrst_code py}'''
std_random_effects_truth = 0.2
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
sim_file['option_sim.csv'] = \
'''name,value
float_precision,4
random_depend_sex,false
'''
for rate_name in no_effect_rate_truth :
   row = f'std_random_effects_{rate_name},{std_random_effects_truth}\n'
   sim_file['option_sim.csv'] += row
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
{xrst_code py}'''
sim_file['covariate.csv'] = 'node_name,sex,age,time,omega\n'
for node_name in [ 'n0', 'n1', 'n2' ] :
   for sex in [ 'female', 'male' ] :
      for age in age_grid :
         for time in time_grid :
            row   = f'{node_name},{sex},{age},{time},{omega_truth}\n'
            sim_file['covariate.csv'] += row
'''{xrst_code}

multiplier_sim.csv
==================
There are no covariate multipliers in this example.
{xrst_code py}'''
sim_file['multiplier_sim.csv'] = \
   'multiplier_id,rate_name,covariate_or_sex,multiplier_true\n'
'''{xrst_code}

simulate.csv
============
{xrst_code py}'''
header  = 'simulate_id,integrand_name,node_name,sex,age_lower,age_upper,'
header += 'time_lower,time_upper,meas_std_cv,meas_std_min\n'
meas_std_cv     = 0.01
simulate_id     = 0
sim_file['simulate.csv'] = header
for integrand_name in integrand_list :
   std_min = 0.0
   if integrand_name == 'prevalence' :
      std_min = 1e-6
   for node_name in node_dict :
      for sex in [ 'female', 'male' ] :
         for age in age_grid :
            for time in time_grid :
               row  = f'{simulate_id},{integrand_name},{node_name},{sex},'
               row += f'{age},{age},{time},{time},'
               row += f'{meas_std_cv},{std_min}\n'
               sim_file['simulate.csv'] += row
               simulate_id += 1
'''{xrst_code}

no_effect_rate.csv
==================
The rates are constant, w.r.t age and time, during the simulation.
{xrst_code py}'''
sim_file['no_effect_rate.csv'] = 'rate_name,age,time,rate_truth\n'
for rate_name in no_effect_rate_truth :
   rate_truth = no_effect_rate_truth[rate_name]
   sim_file['no_effect_rate.csv'] += f'{rate_name},0,0,{rate_truth}\n'
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
{xrst_code py}'''
fit_file['option_fit.csv']  =  \
'''name,value
refit_split,false
ode_step_size,5.0
quasi_fixed,false
max_num_iter_fixed,50
tolerance_fixed,1e-8
ode_method,iota_pos_rho_pos
'''
'''{xrst_code}

option_predict.csv
==================
A predict is run using the same directory as the corresponding fit.
All of its input files are also inputs for the fit except for
the option_predict.csv file.
{xrst_code py}'''
fit_file['option_predict.csv']  =  \
'''name,value
db2csv,true
plot,true
float_precision,5
'''
'''{xrst_code}

fit_goal.csv
============
{xrst_code py}'''
fit_file['fit_goal.csv'] = \
'''node_name
n1
n2
'''
'''{xrst_code}

prior.csv
=========
{xrst_code py}'''
delta_prior_std        = 0.1
std_random_effects_fit = 10.0 * std_random_effects_truth
fit_file['prior.csv']  = \
   'name,density,mean,std,eta,lower,upper\n' + \
   f'delta_prior,log_gaussian,0.0,{delta_prior_std},1e-10,,\n' + \
   f'random_prior,gaussian,0.0,{std_random_effects_fit},,,,\n'
for rate_name in no_effect_rate_truth :
   rate_truth = no_effect_rate_truth[rate_name]
   lower      = rate_truth / 100.0
   upper      = rate_truth * 100.0
   fit_file['prior.csv'] += \
      f'prior_{rate_name},uniform,{rate_truth},,,{lower},{upper}\n'
'''{xrst_code}

parent_rate.csv
===============
The rates are constant during simulation, but not during fitting.
{xrst_code py}'''
fit_file['parent_rate.csv'] = \
   'rate_name,age,time,value_prior,dage_prior,dtime_prior,const_value\n'
for age in age_grid :
   for time in time_grid :
      for rate_name in no_effect_rate_truth :
         row  = f'{rate_name},{age},{time},prior_{rate_name},'
         row += 'delta_prior,delta_prior,\n'
         fit_file['parent_rate.csv'] += row
'''{xrst_code}

child_rate.csv
==============
{xrst_code py}'''
fit_file['child_rate.csv'] = 'rate_name,value_prior\n'
for rate_name in no_effect_rate_truth :
   fit_file['child_rate.csv'] += f'{rate_name},random_prior\n'
'''{xrst_code}

mulcov.csv
==========
{xrst_code py}'''
fit_file['mulcov.csv'] = 'covariate,type,effected,value_prior,const_value\n'
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
{xrst_end csv.sim_fit_pred}
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
      row_in['data_id'] = row_join['simulate_id']
      for key in copy_column :
         row_in[key] = row_join[key]
      row_in['meas_value']    = row_join['meas_value']
      row_in['hold_out']      = 0
      row_in['density_name']  = 'gaussian'
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
def check_predict(fit_dir) :
   #
   # predict_table
   predict_table = dict()
   for prefix in [ 'fit', 'tru', 'sam' ] :
      file_name = f'{fit_dir}/{prefix}_predict.csv'
      file_obj  = open(file_name, 'r')
      predict_table[prefix] = at_cascade.csv.read_table(file_name)
      file_obj.close()
   #
   # predict_table
   key = lambda row : int( row['avgint_id'] )
   for prefix in [ 'fit', 'tru', 'sam' ] :
      predict_table[prefix] = sorted(predict_table[prefix], key=key)
   #
   # max_tru, max_fit_diff, max_sam_diff
   max_tru      = dict()
   max_fit_diff = dict()
   max_sam_diff = dict()
   for integrand_name in integrand_list :
      max_tru[integrand_name]      = 0.0
      max_fit_diff[integrand_name] = 0.0
      max_sam_diff[integrand_name] = 0.0
   #
   # max_tru, max_fit_diff
   for i in range( len(predict_table['tru'] ) ) :
      tru_row        = predict_table['tru'][i]
      fit_row        = predict_table['fit'][i]
      tru_value      = float( tru_row['avg_integrand'] )
      fit_value      = float( fit_row['avg_integrand'] )
      integrand_name = tru_row['integrand_name']
      #
      assert int(tru_row['avgint_id']) == int(fit_row['avgint_id'])
      assert tru_row['integrand_name'] == fit_row['integrand_name']
      #
      tru                      = max_tru[integrand_name]
      max_tru[integrand_name]  = max(tru, abs( tru_value ) )
      #
      max_diff  = max_fit_diff[integrand_name]
      max_diff  = max(max_diff, abs( fit_value - tru_value ) )
      max_fit_diff[integrand_name] = max_diff
   #
   # check max_fit_diff
   for integrand_name in integrand_list :
      assert max_fit_diff[integrand_name] / max_tru[integrand_name] < 0.1
   #
   # max_sam_diff
   n_tru = len(predict_table['tru'])
   n_sam = len(predict_table['sam'])
   assert n_sam % n_tru == 0
   n_sample = int( n_sam / n_tru )
   for i in range(n_tru) :
      tru_row        = predict_table['tru'][i]
      tru_value      = float( tru_row['avg_integrand'] )
      integrand_name = tru_row['integrand_name']
      for j in range(n_sample) :
         sam_row    = predict_table['sam'][i * n_sample + j]
         sam_value  = float( sam_row['avg_integrand'] )
         #
         assert int(tru_row['avgint_id']) == int(sam_row['avgint_id'])
         assert tru_row['integrand_name'] == sam_row['integrand_name']
         #
         max_diff  = max_sam_diff[integrand_name]
         max_diff  = max(max_diff, abs( sam_value - tru_value ) )
         max_sam_diff[integrand_name] = max_diff
   #
   # check max_sam_diff
   for integrand_name in integrand_list :
      assert max_fit_diff[integrand_name] / max_tru[integrand_name] < 0.1
# ---------------------------------------------------------------------------
if __name__ == '__main__' :
   #
   # sim_dir
   sim_dir = 'build/example/csv/sim'
   if not os.path.exists(sim_dir) :
      os.makedirs(sim_dir)
   #
   # sim
   sim(sim_dir)
   #
   # fit_dir
   fit_dir = 'build/example/csv/fit'
   if not os.path.exists(fit_dir) :
      os.mkdir(fit_dir)
   #
   # clear out a previous fit
   if os.path.exists( f'{fit_dir}/n0' ) :
      shutil.rmtree( f'{fit_dir}/n0' )
   #
   # fit
   fit(sim_dir, fit_dir)
   #
   # predict
   at_cascade.csv.predict(fit_dir, sim_dir)
   #
   # check_predict
   check_predict(fit_dir)
   #
   print('sim_fit_pred.py: OK')
# END PYTHON
