# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-23 Bradley M. Bell
# ----------------------------------------------------------------------------
import os
import sys
import time
import shutil
# import at_cascade with a preference current directory version
current_directory = os.getcwd()
if os.path.isfile( current_directory + '/at_cascade/__init__.py' ) :
   sys.path.insert(0, current_directory)
import at_cascade
# BEGIN_PYTHON
# --------------------------------------------------------------------------
#
# random_seed
random_seed = str( int( time.time() ) )
#
# age_grid, time_grid
age_grid   = [0.0, 25.0, 50.0, 75.0, 100.0]
time_grid  = [1980.0, 2000.0, 2020.0]
#
# shock_covariate
def shock_covariate(age, time) :
   if age == 50.0 and time == 2000.0 :
      assert age in age_grid
      assert time in time_grid
      return 1.0
   return 0.0
#
# rate_truth
multiplier_truth = 1.0
no_effect_chi    = 0.03
no_effect_iota   = 0.02
def rate_truth(rate_name, age, time) :
   if rate_name == 'omega' :
      return 0.01
   if rate_name == 'chi' :
      return no_effect_chi
   assert rate_name == 'iota'
   effect = covarite_multiplier * shock_covariate(age, time)
   return no_effect_iota * math.exp( effect )
#
# ----------------------------------------------------------------------------
# simulation files
# ----------------------------------------------------------------------------
#
# sim_file
sim_file = dict()
#
# option_sim.csv
random_seed = str( int( time.time() ) )
sim_file['option_sim.csv'] = \
'''name,value
absolute_tolerance,1e-5
float_precision,4
integrand_step_size,5
random_depend_sex,false
std_random_effects,.2
'''
sim_file['option_sim.csv'] += f'random_seed,{random_seed}\n'
#
# node.csv
sim_file['node.csv'] = \
'''node_name,parent_name
n0,
n1,n0
n2,n0
'''
#
# covariate.csv
sim_file['covariate.csv'] = 'node_name,sex,age,time,omega,shock\n'
for node_name in [ 'n0', 'n1', 'n2' ] :
   for sex in [ 'female', 'male' ] :
      for age in age_grid :
         for time in time_grid :
            omega = rate_truth('omega', age, time)
            shock = shock_covariate(age, time)
            row   = f'{node_name},{sex},{age},{time},{omega},{shock}\n'
            sim_file['covariate.csv'] += row
#
# no_effect_rate.csv
sim_file['no_effect_rate.csv'] = 'rate_name,age,time,rate_truth\n'
sim_file['no_effect_rate.csv'] += f'chi,0,0,{no_effect_chi}\n'
sim_file['no_effect_rate.csv'] += f'iota,0,0,{no_effect_iota}\n'
#
# multiplier_sim.csv
sim_file['multiplier_sim.csv'] = \
'multiplier_id,rate_name,covariate_or_sex,multiplier_truth\n' + \
f'0,iota,shock,{multiplier_truth}\n'
#
# simulate.csv
header  = 'simulate_id,integrand_name,node_name,sex,age_lower,age_upper,'
header += 'time_lower,time_upper,percent_cv\n'
sim_file['simulate.csv'] = header
simulate_id     = -1
percent_cv      = 5.0
for integrand_name in [ 'Sincidence', 'prevalence' ] :
   for node_name in [ 'n0', 'n1', 'n2' ] :
      for sex in [ 'female', 'male' ] :
         for age in age_grid :
            for time in time_grid :
               simulate_id += 1
               row  = f'{simulate_id},{integrand_name},{node_name},{sex},'
               row += f'{age},{age},{time},{time},{percent_cv}\n'
               sim_file['simulate.csv'] += row
# ----------------------------------------------------------------------------
# fit files
# ----------------------------------------------------------------------------
#
# fit_file
fit_file = dict()
#
# option_fit.csv
fit_file['option_fit.csv']  =  \
'''name,value
absolute_covariates,shock
hold_out_integrand,Sincidence
refit_split,false
quasi_fixed,false
max_num_iter_fixed,300
plot,true
db2csv,true
'''
fit_file['option_fit.csv'] += f'random_seed,{random_seed}\n'
#
# fit_goal.csv
fit_file['fit_goal.csv'] = \
'''node_name
n1
n2
'''
#
# predict_integrand.csv
fit_file['predict_integrand.csv'] = \
'''integrand_name
Sincidence
prevalence
'''
#
# prior.csv
fit_file['prior.csv'] = \
'''name,density,mean,std,eta,lower,upper
uniform_-1_1,uniform,0.0,,,-1.0,1.0
uniform_eps_1,uniform,0.02,,,1e-6,1.0
delta_prior,log_gaussian,0.0,0.01,1e-5,,
random_prior,gaussian,0.0,0.2,,,,
'''
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
'shock,rate_value,iota,uniform_-1_1,,'
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
   # fit_file['parent_rate.csv']
   chi  = rate_truth('chi', 0, 0)
   data = 'rate_name,age,time,value_prior,dage_prior,dtime_prior,const_value\n'
   data += f'chi,0.0,0.0,,,,{chi}\n'
   for age in age_grid :
      for time in time_grid :
         data += f'iota,{age},{time},uniform_eps_1,delta_prior,delta_prior,\n'
   fit_file['parent_rate.csv'] = data
   #
   # csv files in fit_file
   for name in fit_file :
      file_name = f'{fit_dir}/{name}'
      file_ptr  = open(file_name, 'w')
      file_ptr.write( fit_file[name] )
      file_ptr.close()
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
      row_in['meas_value'] = row_join['meas_mean']
      row_in['meas_std']   = 1e-3
      row_in['hold_out']   = 0
      #
      table.append( row_in )
   at_cascade.csv.write_table(
         file_name = f'{fit_dir}/data_in.csv' ,
         table     = table ,
   )
   #
   # fit
   at_cascade.csv.fit(fit_dir)
   #
   # fit_predict_table
   fit_predict_table = at_cascade.csv.read_table(
      file_name = f'{fit_dir}/fit_predict.csv'
   )
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
   sys.exit(0)
# END_PYTHON
