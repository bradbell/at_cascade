# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ----------------------------------------------------------------------------
# This case was crashing because n3 was included in the job table.
# The error messages ended with
# AssertionError: get_name_type: table log does not exist in
#     .../at_cascade.git/build/test/csv/n0/female/n1/dismod.db
#
#  root_node :                n0
#                            /  \
#  prior_only:              n1   n2 : fit_goal_set = {n2}
#                           |
#  child_of_prior_only:     n3      : fit_goal_table = {n2, n3}
#
# Step 1: only fit n0 (create priors for n1, n2).
# Step 2: only fit n2
#
# ----------------------------------------------------------------------------
import os
import sys
import time
import math
import shutil
import csv
import multiprocessing
#
# import at_cascade with a preference current directory version
current_directory = os.getcwd()
if os.path.isfile( current_directory + '/at_cascade/__init__.py' ) :
   sys.path.insert(0, current_directory)
import at_cascade

#csv_filt
csv_file = dict()
#
# node.csv
csv_file['node.csv'] = \
'''node_name,parent_name
n0,
n1,n0
n2,n0
n3,n1
'''
#
# option_fit.csv
csv_file['option_fit.csv']  = \
'''name,value
'''

#
# option_predict.csv
csv_file['option_predict.csv']  = 'name,value\n'
#
# covariate.csv
csv_file['covariate.csv'] = \
'''node_name,sex,age,time,omega
n0,female,50,2000,0.02
n1,female,50,2000,0.02
n2,female,50,2000,0.02
n3,female,50,2000,0.02
n0,male,50,2000,0.02
n1,male,50,2000,0.02
n2,male,50,2000,0.02
n3,male,50,2000,0.02
'''
#
# fit_goal.csv
csv_file['fit_goal.csv'] = \
'''node_name
n2
n3
'''
#
# predict_integrand.csv
csv_file['predict_integrand.csv'] = \
'''integrand_name
Sincidence
'''
#
# prior.csv
csv_file['prior.csv'] = \
'''name,lower,upper,mean,std,density
uniform_eps_1,1e-6,1.0,0.5,1.0,uniform
gauss_01,,,0.0,1.0,gaussian
'''
#
# parent_rate.csv
csv_file['parent_rate.csv'] = \
'''rate_name,age,time,value_prior,dage_prior,dtime_prior,const_value
iota,0.0,0.0,uniform_eps_1,,,
'''
#
# child_rate.csv
csv_file['child_rate.csv'] = \
'''rate_name,value_prior
iota,gauss_01
'''
#
# mulcov.csv
csv_file['mulcov.csv']  = 'covariate,type,effected,value_prior,const_value\n'
#
# iota_true, data_in.csv
iota_true = 0.01
header    = 'data_id, integrand_name, node_name, sex, age_lower, age_upper, '
header   += 'time_lower, time_upper, meas_value, meas_std, hold_out, '
header   += 'density_name, eta, nu'
csv_file['data_in.csv'] = header + \
'''
0, Sincidence, n1, female, 0,  10, 1990, 2000, 0.01,  1e-4, 0, gaussian, ,
1, Sincidence, n1, male,   0,  10, 1990, 2000, 0.01,  1e-4, 0, gaussian, ,
2, Sincidence, n3, female, 20, 30, 2010, 2020, 0.01,  1e-4, 0, gaussian, ,
3, Sincidence, n3, male,   20, 30, 2010, 2020, 0.01,  1e-4, 0, gaussian, ,
4, Sincidence, n2, female, 20, 30, 2010, 2020, 0.01,  1e-4, 0, gaussian, ,
5, Sincidence, n2, male,   20, 30, 2010, 2020, 0.01,  1e-4, 0, gaussian, ,
'''
csv_file['data_in.csv'] = csv_file['data_in.csv'].replace(' ', '')
#
# main
def main() :
   #
   # fit_dir
   fit_dir = 'build/test/csv'
   at_cascade.empty_directory(fit_dir)
   #
   # write csv files
   for name in csv_file :
      file_name = f'{fit_dir}/{name}'
      file_ptr  = open(file_name, 'w')
      file_ptr.write( csv_file[name] )
      file_ptr.close()
   #
   # csv.fit
   at_cascade.csv.fit(fit_dir, max_node_depth=0)
   at_cascade.continue_cascade(
      all_node_database = f'{fit_dir}/all_node.db'  ,
      fit_database      = f'{fit_dir}/n0/dismod.db' ,
      fit_goal_set      = { 'n2' }                  ,
   )
   #
   # csv.predict
   at_cascade.csv.predict(
      fit_dir        = fit_dir,
      sim_dir        = None,
      start_job_name = 'n2.female',
   )
   #
   # predict/fit_n2.female.csv
   file_name    = f'{fit_dir}/predict/fit_n2.female.csv'
   predict_data = at_cascade.csv.read_table(file_name)
   for row in predict_data :
      relerr = 1.0 - float( row['avg_integrand'] ) / iota_true
      if abs(relerr) > 1e-4 :
         print( f'relerr = {relerr}' )
         assert False
      assert row['fit_node_name'] in { 'n0', 'n2' }
      assert row['fit_sex'] == 'female'
      assert row['integrand_name'] == 'Sincidence'
      assert row['node_name'] == 'n2'
      assert row['sex'] == 'female'


if __name__ == '__main__' :
   main()
   print('check_log: ok')
