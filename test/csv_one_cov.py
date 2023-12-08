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
#
# sim_file, file_file
sim_file = dict()
fit_file = dict()
#
# random_seed
random_seed = str( int( time.time() ) )
#
# age_grid, time_grid
age_grid   = [0.0, 1.0, 25.0, 50.0, 75.0, 100.0]
time_grid  = [1980.0, 2000.0, 2020.0]
#
# the_covariate
age_range  = max(age_grid)  - min(age_grid)
time_range = max(time_grid) - min(time_grid)
def the_covariate(age, time) :
   age_ratio  =  (age - min(age_grid))  / age_range
   time_ratio =  (time - min(time_grid)) / time_range
   return age_ratio * time_ratio
#
# option_sim.csv
sim_file['option_sim.csv'] = \
'''name,value
float_precision,4
random_depend_sex,false
std_random_effects_iota,.2
'''
sim_file['option_sim.csv'] += f'random_seed,{random_seed}\n'
#
# node.csv
sim_file['node.csv'] = \
'''node_name,parent_name
n0,
'''
#
# covariate.csv, cov_reference
cov_reference    = 0.0
count            = 0
omega_truth      = 0.01
sim_file['covariate.csv'] = 'node_name,sex,age,time,omega,the_cov\n'
for node_name in [ 'n0' ] :
   for sex in [ 'female', 'male' ] :
      for age in age_grid :
         for time in time_grid :
            cov            = the_covariate(age, time)
            cov_reference += cov
            count         += 1
            row   = f'{node_name},{sex},{age},{time},{omega_truth},{cov}\n'
            sim_file['covariate.csv'] += row
cov_reference = cov_reference / count
#
# mul_the_cov_truth, multiplier_sim.csv
mul_the_cov_truth = 0.5
sim_file['multiplier_sim.csv'] = \
'multiplier_id,rate_name,covariate_or_sex,multiplier_truth\n' + \
f'0,iota,the_cov,{mul_the_cov_truth}\n'
#
# simulate.csv
header  = 'simulate_id,integrand_name,node_name,sex,age_lower,age_upper,'
header += 'time_lower,time_upper,meas_std_cv,meas_std_min\n'
sim_file['simulate.csv'] = header
n_repeat        = 1
simulate_id     = 0
meas_std_cv     = 0.1
meas_std_min    = 0.002
for integrand_name in [ 'Sincidence', 'prevalence' ] :
   for node_name in [ 'n0' ] :
      for sex in [ 'female', 'male', 'both' ] :
         for age in age_grid :
            for time in time_grid :
               for i in range(n_repeat) :
                  row  = f'{simulate_id},{integrand_name},{node_name},{sex},'
                  row += f'{age},{age},{time},{time},'
                  row += f'{meas_std_cv},{meas_std_min}\n'
                  sim_file['simulate.csv'] += row
                  simulate_id += 1
#
# no_effect_rate.csv
no_effect_iota   = 0.02
no_effect_chi    = 0.03
sim_file['no_effect_rate.csv'] = 'rate_name,age,time,rate_truth\n'
sim_file['no_effect_rate.csv'] += f'iota,0,0,{no_effect_iota}\n'
sim_file['no_effect_rate.csv'] += f'chi,0,0,{no_effect_chi}\n'
#
# option_fit.csv
fit_file['option_fit.csv']  =  \
'''name,value
hold_out_integrand,Sincidence
refit_split,false
ode_step_size,5.0
quasi_fixed,false
max_num_iter_fixed,50
tolerance_fixed,1e-8
no_ode_ignore,all
'''
fit_file['option_fit.csv'] += f'random_seed,{random_seed}\n'
#
# option_predict.csv
fit_file['option_predict.csv']  =  \
'''name,value
plot,true
db2csv,true
'''
#
# fit_goal.csv
fit_file['fit_goal.csv'] = \
'''node_name
n0
'''
#
# prior.csv
fit_file['prior.csv'] = \
'''name,density,mean,std,eta,lower,upper
uniform_eps_1,uniform,0.02,,,1e-6,1.0
delta_prior,log_gaussian,0.0,0.1,1e-5,,
random_prior,gaussian,0.0,0.2,,,,
'''
#
# parent_rate.csv
data = 'rate_name,age,time,value_prior,dage_prior,dtime_prior,const_value\n'
data += f'chi,0.0,0.0,,,,{no_effect_chi}\n'
for age in age_grid :
   for time in time_grid :
      data += f'iota,{age},{time},uniform_eps_1,delta_prior,delta_prior,\n'
fit_file['parent_rate.csv'] = data
#
# child_rate.csv
fit_file['child_rate.csv'] = \
'''rate_name,value_prior
iota,random_prior
'''
#
# mulcov.csv
fit_file['mulcov.csv'] = \
'covariate,type,effected,value_prior,const_value\n' + \
f'the_cov,rate_value,iota,,{mul_the_cov_truth}'
#
# predict_integrand.csv
fit_file['predict_integrand.csv'] = \
'''integrand_name
Sincidence
prevalence
mulcov_0
'''
#
# -----------------------------------------------------------------------------
# sim
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
   # data_join_table
   # This is a join of simulate.csv and data_sim.csv
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
      row_in['meas_value']   = row_join['meas_mean']
      row_in['meas_std']     = row_join['meas_std']
      row_in['hold_out']     = 0
      row_in['density_name'] = 'gaussian'
      #
      table.append( row_in )
   at_cascade.csv.write_table(
         file_name = f'{fit_dir}/data_in.csv' ,
         table     = table ,
   )
   #
   # fit, predict
   at_cascade.csv.fit(fit_dir)
   at_cascade.csv.predict(fit_dir, sim_dir)
   #
   # fit_predict_table
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
   max_error  = { 'mulcov_0': 0.0, 'iota' : 0.0}
   predict_node_set = set()
   for row in fit_predict_table :
      node_name = row['node_name']
      assert node_name == 'n0'
      sex            = row['sex']
      age            = float( row['age'] )
      integrand_name = row['integrand_name']
      avg_integrand  = float( row['avg_integrand'] )
      if integrand_name == 'mulcov_0' :
         if mul_the_cov_truth == 0.0 :
            # This case is used for testing this program without covariates
            abs_error = abs(avg_integrand)
            max_error['mulcov_0'] = max(max_error['mulcov_0'], abs_error)
         else :
            rel_error     = (1.0 - avg_integrand / mul_the_cov_truth)
            max_error['mulcov_0'] = max(max_error['mulcov_0'], abs(rel_error) )
      if integrand_name == 'Sincidence' :
         node_name     = row['node_name']
         time          = float( row['time'] )
         if sex == 'both' :
            random_male   = random_effect_dict[node_name]['male']['iota']
            random_female = random_effect_dict[node_name]['female']['iota']
            random_effect = (random_male + random_female) / 2.0
         else :
            random_effect = random_effect_dict[node_name][sex]['iota']
         cov_diff          = the_covariate(age, time) - cov_reference
         cov_effect        = mul_the_cov_truth * cov_diff
         total_effect      = random_effect + cov_effect
         iota              = math.exp(total_effect) * no_effect_iota
         rel_error         = (1.0 - avg_integrand / iota )
         max_error['iota'] = max(max_error['iota'], abs(rel_error) )
   for name in max_error :
      if max_error[name] > 5e-3 :
         msg  = f'max_error = {max_error}\n'
         msg += 'csv_one_cov.py: Relative error is to large (see above)'
         assert False, msg
# -----------------------------------------------------------------------------
# Without this, the mac will try to execute main on each processor.
if __name__ == '__main__' :
   #
   # sim_dir
   sim_dir = 'build/test/'
   if not os.path.exists(sim_dir) :
      os.makedirs(sim_dir)
   #
   # clear out a previous run
   if os.path.exists( 'build/test/fit/n0' ) :
      shutil.rmtree( 'build/test/fit/n0' )
   #
   # fit_dir
   fit_dir = 'build/test/fit'
   if not os.path.exists(fit_dir) :
      os.mkdir(fit_dir)
   #
   # sim
   sim(sim_dir)
   #
   # fit
   fit(sim_dir, fit_dir)
   #
   print('csv_one_cov.py: OK')
   sys.exit(0)
# END_SOURCE_CODE
