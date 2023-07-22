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
\{xrst_begin sim_fit_pred}

Example Simulating Fitting and Predictiong
##########################################


integrand_list
**************
Generate data and predict for the following integrands:
{xrst_code py}'''
integrand_list = [ 'Sincidence', 'remission', 'mtexcess', 'prevalence' ]
'''{xrst_code}

age_grid, time_grid
********************
Use this age-time grid for values that are not constant w.r.t age or time:
{xrst_code py}'''
age_grid   = [0.0, 20.0, 50.0, 80.0, 100.0]
time_grid  = [1980.0, 2000.0, 2020.0]
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
no_effect_rate_truth
********************
This is the true values (used during simulation) for iota, rho, and chi:
{xrst_code py}'''
no_effect_rate_truth = {
   'iota' : 0.02  ,
   'rho'  : 20.0  ,
   'chi'  : 0.001  ,
}
'''{xrst_code}

std_random_effects_truth
************************
This is the true standard deviation of the random effects
{xrst_code py}'''
std_random_effects = 0.1
# ----------------------------------------------------------------------------
# sim_file
# Input files that are placed in the simulate directory
sim_file = dict()
#
# option_sim.csv
sim_file['option_sim.csv'] = \
'''name,value
float_precision,4
random_depend_sex,false
'''
for rate_name in no_effect_rate_truth :
   row = f'std_random_effects_{rate_name},{std_random_effects}\n'
   sim_file['option_sim.csv'] += row
#
# node.csv
sim_file['node.csv'] = \
'node_name,parent_name\n'
for node_name in node_dict :
   parent_name = node_dict[node_name]
   sim_file['node.csv'] += f'{node_name},{parent_name}\n'
#
# covariate.csv
omega_true      = 0.01
sim_file['covariate.csv'] = 'node_name,sex,age,time,omega\n'
for node_name in [ 'n0', 'n1', 'n2' ] :
   for sex in [ 'female', 'male' ] :
      for age in age_grid :
         for time in time_grid :
            row   = f'{node_name},{sex},{age},{time},{omega_true}\n'
            sim_file['covariate.csv'] += row
#
# mutiplier_sim.csv
sim_file['multiplier_sim.csv'] = \
'multiplier_id,rate_name,covariate_or_sex,multiplier_true\n'
#
# simulate.csv
header  = 'simulate_id,integrand_name,node_name,sex,age_lower,age_upper,'
header += 'time_lower,time_upper,meas_std_cv,meas_std_min\n'
meas_std_cv     = 0.01
simulate_id     = 0
meas_std_min    = {
   'Sincidence' : no_effect_rate_truth['iota'] /  100.0 ,
   'remission'  : no_effect_rate_truth['rho'] /  100.0 ,
   'mtexcess'   : no_effect_rate_truth['chi'] /  100.0 ,
   'prevalence' : 1e-6 ,
}

sim_file['simulate.csv'] = header
for integrand_name in integrand_list :
   std_min = meas_std_min[integrand_name]
   for node_name in node_dict :
      for sex in [ 'female', 'male' ] :
         for age in age_grid :
            for time in time_grid :
               row  = f'{simulate_id},{integrand_name},{node_name},{sex},'
               row += f'{age},{age},{time},{time},'
               row += f'{meas_std_cv},{std_min}\n'
               sim_file['simulate.csv'] += row
               simulate_id += 1
#
# no_effect_rate.csv
sim_file['no_effect_rate.csv'] = 'rate_name,age,time,rate_truth\n'
for rate_name in no_effect_rate_truth :
   rate_truth = no_effect_rate_truth[rate_name]
   sim_file['no_effect_rate.csv'] += f'{rate_name},0,0,{rate_truth}\n'
# ----------------------------------------------------------------------------
# fit_file
# Input files that are placed in the fit directory
fit_file = dict()
#
# node.csv
fit_file['node.csv'] = sim_file['node.csv']
#
# covariate.csv
fit_file['covariate.csv'] = sim_file['covariate.csv']
#
# option_fit.csv
fit_file['option_fit.csv']  =  \
'''name,value
refit_split,false
ode_step_size,5.0
quasi_fixed,false
max_num_iter_fixed,50
tolerance_fixed,1e-8
ode_method,iota_pos_rho_pos
'''
#
# fit_goal.csv
fit_file['fit_goal.csv'] = \
'''node_name
n1
n2
'''
#
# prior.csv
fit_file['prior.csv']  = \
   'name,density,mean,std,eta,lower,upper\n' + \
   'delta_prior,log_gaussian,0.0,0.01,1e-10,,\n' + \
   f'random_prior,gaussian,0.0,{std_random_effects},,,,\n'
for rate_name in no_effect_rate_truth :
   rate_truth = no_effect_rate_truth[rate_name]
   lower      = rate_truth / 100.0
   upper      = rate_truth * 100.0
   fit_file['prior.csv'] += \
      f'prior_{rate_name},uniform,{rate_truth},,,{lower},{upper}\n'
#
# parent_rate.csv
fit_file['parent_rate.csv'] = \
   'rate_name,age,time,value_prior,dage_prior,dtime_prior,const_value\n'
for age in age_grid :
   for time in time_grid :
      for rate_name in no_effect_rate_truth :
         row  = f'{rate_name},{age},{time},prior_{rate_name},'
         row += 'delta_prior,delta_prior,\n'
         fit_file['parent_rate.csv'] += row
#
# child_rate.csv
fit_file['child_rate.csv'] = 'rate_name,value_prior\n'
for rate_name in no_effect_rate_truth :
   fit_file['child_rate.csv'] += f'{rate_name},random_prior\n'
#
# mulcov.csv
fit_file['mulcov.csv'] = 'covariate,type,effected,value_prior,const_value\n'
#
# predict_integrand.csv
fit_file['predict_integrand.csv'] = 'integrand_name\n'
for integrand_name in integrand_list :
   fit_file['predict_integrand.csv'] += f'{integrand_name}\n'
# ----------------------------------------------------------------------------
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
