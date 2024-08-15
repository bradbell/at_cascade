# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ----------------------------------------------------------------------------
import os
import sys
import time
import math
import shutil
import csv
import multiprocessing
# import at_cascade with a preference current directory version
current_directory = os.getcwd()
if os.path.isfile( current_directory + '/at_cascade/__init__.py' ) :
   sys.path.insert(0, current_directory)
import at_cascade
import dismod_at
#
csv_file = dict()
csv_file['node.csv'] = \
'''node_name,parent_name
n0,
n1,n0
n2,n0
'''
#
max_number_cpu = 1
random_seed    = str( int( time.time() ) )
csv_file['option_fit.csv']  = 'name,value\n'
csv_file['option_fit.csv'] += f'random_seed,{random_seed}\n'
csv_file['option_fit.csv'] += 'refit_split,false\n'
#
if max_number_cpu == 1 :
   csv_file['option_fit.csv'] += f'max_number_cpu,1\n'
csv_file['option_predict.csv']  = 'name,value\n'
#
csv_file['covariate.csv'] = \
'''node_name,sex,age,time,omega,haqi
n0,female,50,2000,0.002,1.0
n1,female,50,2000,0.002,1.0
n2,female,50,2000,0.002,1.0
n0,male,50,2000,0.002,1.0
n1,male,50,2000,0.002,1.0
n2,male,50,2000,0.002,1.0
'''
#
csv_file['fit_goal.csv'] = \
'''node_name
n0
n1
n2
'''
#
csv_file['predict_integrand.csv'] = \
'''integrand_name
Sincidence
prevalence
'''
#
csv_file['prior.csv'] = \
'''name,lower,upper,mean,std,density
uniform_-1_1,-1.0,1.0,0.5,1.0,uniform
uniform_eps_1,1e-6,1.0,0.5,1.0,uniform
gauss_01,,,0.0,0.05,gaussian
gauss_1e-6,1e-6,10,0.1,0.02,gaussian
'''
#
csv_file['parent_rate.csv'] = \
'''rate_name,age,time,value_prior,dage_prior,dtime_prior,const_value
iota,0.0,0.0,gauss_1e-6,,,
'''
#
csv_file['child_rate.csv'] = \
'''rate_name,value_prior
iota,gauss_01
'''
#
csv_file['mulcov.csv'] = \
'''covariate,type,effected,value_prior,const_value
haqi,rate_value,iota,gauss_1e-6,
'''
#
header  = 'data_id, integrand_name, node_name, sex, age_lower, age_upper, '
header += 'time_lower, time_upper, meas_value, meas_std, hold_out, '
header += 'density_name, eta, nu'
csv_file['data_in.csv'] = header + \
'''
0, Sincidence, n0, female, 0,  10, 1990, 2000, 0.0000, 0.001, 0, gaussian, ,
1, Sincidence, n0, male,   0,  10, 1990, 2000, 0.0000, 0.001, 0, gaussian, ,
2, Sincidence, n1, female, 10, 20, 2000, 2010, 0.0000, 0.001, 0, gaussian, ,
3, Sincidence, n1, male,   10, 20, 2000, 2010, 0.0000, 0.001, 0, gaussian, ,
4, Sincidence, n2, female, 20, 30, 2010, 2020, 0.0000, 0.001, 0, gaussian, ,
5, Sincidence, n2, male,   20, 30, 2010, 2020, 0.0000, 0.001, 0, gaussian, ,
'''
csv_file['data_in.csv'] = csv_file['data_in.csv'].replace(' ', '')
#
breakup_computation = True
#
# BEGIN_PROGRAM
#
# computation
def computation(fit_dir) :
   #
   # csv.fit, csv.predict_prior
   if not breakup_computation:
      at_cascade.csv.fit(fit_dir)
      at_cascade.csv.predict_prior(fit_dir)
   else :
      # csv.fit: Just fit the root node
      # Since refit_split is false, this will only fit include n0.both.
      at_cascade.csv.fit(fit_dir, max_node_depth = 0)
      #
      # all_node_database
      all_node_database = f'{fit_dir}/all_node.db'
      #
      # Run two continues starting at n0.both.
      # If max_number_cpu != 1, run them in parallel.
      # p_fit
      p_fit = dict()
      fit_node_database = f'{fit_dir}/n0/dismod.db'
      fit_type          = [ 'both', 'fixed']
      for node_name in [ 'n1' , 'n2' ] :
         fit_goal_set  = { node_name }
         shared_unique = '_' + node_name
         args          = (
            all_node_database,
            fit_node_database,
            fit_goal_set,
            fit_type,
            shared_unique,
         )
         if max_number_cpu == 1 :
            at_cascade.continue_cascade( *args )
         else :
            p_fit[node_name] = multiprocessing.Process(
               target = at_cascade.continue_cascade , args = args ,
            )
            p_fit[node_name].start()
      #
      # Run one predict for n0.both using this process
      # If max_number_cpu != 1, this is in parallel with the continues above
      p_predict      = dict()
      sim_dir        = None
      start_job_name = 'n0.both'
      max_job_depth  = 0
      args           = ( fit_dir, f'{fit_dir}/n0/', start_job_name, max_job_depth )
      at_cascade.csv.predict_prior( *args )
      #
      # If max_number_cpu != 1, wait for continue jobs to finish
      for key in p_fit :
         p_fit[key].join()
      #
      #
      # Run predict starting at
      # n1.female, n1.male, n2.female, n2.male.
      # If max_number_cpu != 1, run them in parallel.
      sim_dir       = None
      max_job_depth = 0
      for node_name in [ 'n1', 'n2' ] :
         for sex in [ 'female', 'male' ] :
            start_job_name = f'{node_name}.{sex}'
            job_dir = f'{fit_dir}/n0/{sex}/{node_name}/'
            args           = ( fit_dir, job_dir, start_job_name, max_job_depth )
            if max_number_cpu == 1 :
               at_cascade.csv.predict_prior(*args)
            else :
               key            = (node_name, sex)
               p_predict[key] = multiprocessing.Process(
                  target = at_cascade.csv.predict_prior, args = args
                )
               p_predict[key].start()
      #
      # If max_number_cpu != 1, wait for predict jobs to finish
      for key in p_predict :
         p_predict[key].join()
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
   # node2haqi, haqi_avg
   node2haqi  = { 'n0' : 1.0, 'n1' : 1.0, 'n2' : 1.0 }
   file_name  = f'{fit_dir}/covariate.csv'
   table      = at_cascade.csv.read_table( file_name )
   haqi_sum   = 0.0
   for row in table :
      node_name = row['node_name']
      haqi      = float( row['haqi'] )
      haqi_sum += haqi
      assert haqi == node2haqi[node_name]
   haqi_avg = haqi_sum / len(table)
   #
   # data_in.csv
   float_format      = '{0:.5g}'
   true_mulcov_haqi  = 0.5
   no_effect_iota    = 0.5
   file_name         = f'{fit_dir}/data_in.csv'
   table             = at_cascade.csv.read_table( file_name )
   for row in table :
      node_name      = row['node_name']
      integrand_name = row['integrand_name']
      assert integrand_name == 'Sincidence'
      #
      # BEGIN_MEAS_VALUE
      haqi              = node2haqi[node_name]
      effect            = true_mulcov_haqi * (haqi - haqi_avg)
      iota              = math.exp(effect) * no_effect_iota
      row['meas_value'] = float_format.format( iota )
      # END_MEAS_VALUE
   at_cascade.csv.write_table(file_name, table)
   #
   # computation
   computation(fit_dir)
   #
   # prefix
   for prefix in [ 'fit' , 'sam' ] :
      #
      # node
      for node in [ 'n0', 'n1', 'n2' ] :
         # sex
         for sex in [ 'female', 'both', 'male' ] :
            #
            # sample_list
            # predict_table
            file_name = f'{fit_dir}/{prefix}_predict.csv'
            predict_table = at_cascade.csv.read_table(file_name)
            #
            sample_list = list()
            for row in predict_table :
               if row['integrand_name'] == "Sincidence" and \
                     row['node_name'] == node and \
                        row['sex'] == sex :
                           sample_list.append(row)
            if node == 'n0' and sex == 'both' :
               assert len(sample_list) != 0
            elif node != 'n0' and sex != 'both' :
               assert len(sample_list) != 0
            else :
               assert len(sample_list) == 0
            #
            if len(sample_list) > 0 :
               sum_avgint = 0.0
               for row in sample_list :
                  sum_avgint   += float( row['avg_integrand'] )
               avgint    = sum_avgint / len(sample_list)
               haqi      = float( row['haqi'] )
               effect    = true_mulcov_haqi * (haqi - haqi_avg)
               iota      = math.exp(effect) * no_effect_iota
               rel_error = (avgint - iota) / iota
               assert abs(rel_error) < 0.01
#
if __name__ == '__main__' :
   main()
   print('prior_pred.py: OK')
# END_PROGRAM
