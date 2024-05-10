# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ----------------------------------------------------------------------------
# imports
import os
import sys
import time
import shutil
import numpy
import random
import scipy
# import at_cascade with a preference current directory version
current_directory = os.getcwd()
if os.path.isfile( current_directory + '/at_cascade/__init__.py' ) :
   sys.path.insert(0, current_directory)
import at_cascade
# ----------------------------------------------------------------------------
#
age_grid   = [ 0.0,  100.0]
time_grid  = [ 1980, 2020]
#
true_iota  = 0.01
true_omega = 0.02
#
random_seed = str( int( time.time() ) )
random.seed(random_seed)
#
number_data         = 5
number_sample       = 50
meas_std_cv         = 0.5
number_data_set     = 40
# ----------------------------------------------------------------------------
# simulation files
# ----------------------------------------------------------------------------
#
# sim_file
sim_file = dict()
#
# option_sim.csv
sim_file['option_sim.csv'] = \
'''name,value
absolute_tolerance,1e-10
float_precision,12
'''
sim_file['option_sim.csv'] += f'random_seed,{random_seed}\n'
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
for simulate_id in range( number_data ) :
   sim_file['simulate.csv'] += f'{simulate_id},' + row
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
refit_split,false
quasi_fixed,false
tolerance_fixed,1e-8
max_num_iter_fixed,50
'''
fit_file['option_fit.csv'] += f'number_sample,{number_sample}\n'
fit_file['option_fit.csv'] += f'random_seed,{random_seed}\n'
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
Sincidence
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
# summary
summary_dict   = dict()
def weighted_residual(sim_dir, fit_dir) :
   global summary_dict
   #
   # n_grid
   n_grid = len(age_grid) * len(time_grid)
   #
   # n_integrand
   # number of integrands in predict_integrand.csv
   n_integrand = 2
   #
   # prefix
   for prefix in [ 'tru', 'fit', 'sam' ] :
      #
      # table
      table = at_cascade.csv.read_table(
         file_name = f'{fit_dir}/{prefix}_predict.csv'
      )
      if prefix == 'sam' :
         assert len(table) == number_sample * n_grid
      else :
         assert len(table) == n_grid
      #
      # This groups together all rows for same node, age, time.
      key   = lambda row : ( row['node_name'] , row['avgint_id'] )
      table = sorted(table, key = key)
      #
      # summary_dict[ 'true', 'fit', or 'sam' ]
      summary_dict[prefix] = list()
      for row in table :
         summary_dict[prefix].append( float( row['avg_integrand'] ) )
   #
   # summary_dict['std']
   if 'std' not in summary_dict :
      summary_dict['std'] = list()
      for i_grid in range(n_grid) :
         sumsq = 0.0
         for i_sample in range( number_sample ) :
            sample  = summary_dict['sam'][ i_grid * number_sample + i_sample ]
            diff    = sample - summary_dict['fit'][i_grid]
            sumsq  += diff * diff
         #
         summary_dict['std'].append( numpy.sqrt( sumsq / number_sample ) )
   #
   # fit
   eps99 = 99.0 * numpy.finfo(float).eps
   fit    = summary_dict['fit'][0]
   for other_fit in summary_dict['fit'] :
      assert abs( 1.0 -  other_fit/ fit) < eps99
   #
   # residual
   tru      = summary_dict['tru'][0]
   fit      = summary_dict['fit'][0]
   std      = summary_dict['std'][0]
   residual = (fit - tru) / std
   #
   return residual
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
   # residual
   residual_list = list()
   for i_data_set in range(number_data_set) :
      #
      # fit_dir/n0
      at_cascade.empty_directory( f'{fit_dir}/n0' )
      os.rmdir( f'{fit_dir}/n0' )
      #
      # sim
      sim(sim_dir)
      #
      # fit
      fit(sim_dir, fit_dir)
      #
      # predict
      at_cascade.csv.predict(fit_dir, sim_dir)
      #
      # residual
      residual_list.append( weighted_residual(sim_dir, fit_dir) )
   #
   # confidence_theory, confidence_sample
   # probability that residual is in interval [-0.68, +0.68]
   cdf               = scipy.stats.norm.cdf
   confidence_theory = cdf(+0.68) - cdf(-0.68)
   count  = 0
   for residual in residual_list :
      if abs(residual) <= 0.68 :
         count += 1
   confidence_sample = count / number_data_set
   difference = confidence_sample - confidence_theory
   msg  = f'theory = {confidence_theory}, '
   msg += f'sample = {confidence_sample}, '
   msg += f'difference = {difference}'
   print( msg )
   assert abs(difference) < 0.1
   #
   print('csv.coverage: OK')
   sys.exit(0)
# END_PYTHON
main()
