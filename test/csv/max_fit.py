# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ----------------------------------------------------------------------------
# Test the max_fit option in option_fit.csv
# This test failed before 2023-11-30 (when balance_sex was true).
max_fit = 4
#
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
import dismod_at
# BEGIN_PYTHON
#
# csv_file
csv_file = dict()
#
# option_fit.csv
random_seed = str( int( time.time() ) )
csv_file['option_fit.csv'] = \
'''name,value
refit_split,false
balance_sex,true
'''
csv_file['option_fit.csv'] += f'max_fit,{max_fit}\n'
#
# option_predict.csv
random_seed = str( int( time.time() ) )
csv_file['option_predict.csv'] = \
'''name,value
'''
#
# node.csv
csv_file['node.csv'] = \
'''node_name,parent_name
n0,
n1,n0
n2,n0
'''
#
# covariate.csv
csv_file['covariate.csv'] = \
'''node_name,sex,income,age,time,omega
n0,female,1.0,50,2000,0.02
n0,male,2.0,50,2000,0.02
n1,female,1.0,50,2000,0.02
n1,male,2.0,50,2000,0.02
n2,female,1.0,50,2000,0.02
n2,male,2.0,50,2000,0.02
'''
#
# fit_goal.csv
csv_file['fit_goal.csv'] = \
'''node_name
n0
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
gaussian_eps_10,1e-6,1.0,0.5,10.0,gaussian
'''
#
# parent_rate.csv
csv_file['parent_rate.csv'] = \
'''rate_name,age,time,value_prior,dage_prior,dtime_prior,const_value
iota,0.0,0.0,gaussian_eps_10,,,
'''
#
# child_rate.csv
csv_file['child_rate.csv'] = \
'''rate_name,value_prior
'''
#
# mulcov.csv
csv_file['mulcov.csv'] = \
'''covariate,type,effected,value_prior,const_value
'''
#
# data_in.csv
header  = 'data_id,integrand_name,node_name,sex,age_lower,age_upper,'
header += 'time_lower,time_upper,meas_value,meas_std,hold_out,'
header += 'density_name,eta,nu'
csv_file['data_in.csv'] = header + \
'''
0,Sincidence,n0,both,0,10,1990,2000,0.01,1e-4,0,gaussian,,
1,Sincidence,n0,female,0,10,1990,2000,0.01,1e-4,0,gaussian,,
2,Sincidence,n0,male,0,10,1990,2000,0.01,1e-4,0,gaussian,,
3,Sincidence,n1,both,0,10,1990,2000,0.01,1e-4,0,gaussian,,
4,Sincidence,n1,female,0,10,1990,2000,0.01,1e-4,0,gaussian,,
5,Sincidence,n1,male,0,10,1990,2000,0.01,1e-4,0,gaussian,,
6,Sincidence,n2,both,0,10,1990,2000,0.01,1e-4,0,gaussian,,
7,Sincidence,n2,female,0,10,1990,2000,0.01,1e-4,0,gaussian,,
8,Sincidence,n2,male,0,10,1990,2000,0.01,1e-4,0,gaussian,,
'''
#
#
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
   at_cascade.csv.fit(fit_dir)
   #
   # data_table, integrand_table
   root_database      = f'{fit_dir}/root_node.db'
   connection         = dismod_at.create_connection(root_database)
   data_table         = dismod_at.get_table_dict(connection, 'data')
   integrand_table    = dismod_at.get_table_dict(connection, 'integrand')
   connection.close()
   #
   # data_subset_table
   fit_database      = f'{fit_dir}/n0/dismod.db'
   connection        = dismod_at.create_connection(fit_database)
   data_subset_table = dismod_at.get_table_dict(connection, 'data_subset')
   connection.close()
   #
   # hold_in_count
   hold_in_count = 0
   for subset_row in data_subset_table :
      data_id        = subset_row['data_id']
      data_row       = data_table[data_id]
      integrand_id   = data_row['integrand_id']
      integrand_name = integrand_table[integrand_id]['integrand_name']
      assert integrand_name == 'Sincidence'
      if data_row['hold_out'] == 0 and subset_row['hold_out'] == 0 :
         hold_in_count += 1
   assert hold_in_count == max_fit
#
if __name__ == '__main__' :
   main()
   print('csv_max_fit: OK')
# END_PYTHON
