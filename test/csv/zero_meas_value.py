# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
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
import dismod_at
# BEGIN_PYTHON
#
# no_effect_iota_true
no_effect_iota_true    = 0.01
#
# csv_file
csv_file = dict()
#
# option_fit.csv
random_seed = str( int( time.time() ) )
csv_file['option_fit.csv'] = \
'''name,value
max_abs_effect,3.0
number_sample,10
sample_method,asymptotic
no_ode_ignore,iota
root_node_name,n0
absolute_covariates,young
'''
#
# option_predict.csv
random_seed = str( int( time.time() ) )
csv_file['option_predict.csv'] = \
'''name,value
db2csv,true
plot,true
zero_meas_value,true
max_number_cpu,1
'''
#
# node.csv
# Use node n-1 to test starting below the base of the tree
csv_file['node.csv'] = \
'''node_name,parent_name
n0,
n1,n0
'''
#
# covariate.csv
csv_file['covariate.csv'] = \
'''node_name,sex,age,time,young,omega
n0,female,20,2000,1.0,0.02
n0,female,80,2000,0.0,0.02
n0,male,20,2000,1.0,0.02
n0,male,80,2000,0.0,0.02
n1,female,20,2000,1.0,0.02
n1,female,80,2000,0.0,0.02
n1,male,20,2000,1.0,0.02
n1,male,80,2000,0.0,0.02
'''
#
# fit_goal.csv
# n-1 is not included in test because it is not below the root node n0
csv_file['fit_goal.csv'] = \
'''node_name
n1
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
'''name,lower,upper,std,density,mean
uniform_-2_2,-2.0,2.0,10.0,uniform,0.0
gauss_eps_10,1e-6,1.0,100.0,gaussian,'''
csv_file['prior.csv'] += str( no_effect_iota_true )
#
# parent_rate.csv
csv_file['parent_rate.csv'] = \
'''rate_name,age,time,value_prior,dage_prior,dtime_prior,const_value
iota,0.0,0.0,gauss_eps_10,,,
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
young,meas_value,Sincidence,uniform_-2_2,
'''
#
# data_in.csv
# The 0.00 meas_value and meas_std in this table get replaced
header  = 'data_id,integrand_name,node_name,sex,age_lower,age_upper,'
header += 'time_lower,time_upper,meas_value,meas_std,hold_out,'
header += 'density_name,eta,nu'
csv_file['data_in.csv'] = header + \
'''
0,Sincidence,n0,both,10,10,2000,2000,0.00,0.00,0,gaussian,,
1,Sincidence,n0,both,80,80,2000,2000,0.00,0.00,0,gaussian,,
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
   # table
   file_name  = f'{fit_dir}/covariate.csv'
   table      = at_cascade.csv.read_table( file_name )
   #
   # data_in.csv
   float_format        = '{0:.8g}'
   mulcov_young_true   = 0.5
   file_name           = f'{fit_dir}/data_in.csv'
   table               = at_cascade.csv.read_table( file_name )
   for row in table :
      age            = float(row['age_lower'])
      young          = float( age < 20 )
      integrand_name = row['integrand_name']
      assert integrand_name == 'Sincidence'
      #
      effect            = mulcov_young_true * young
      Sincidence        = math.exp(effect) * no_effect_iota_true
      row['meas_value'] = float_format.format( Sincidence )
      row['meas_std']   = float_format.format( Sincidence / 10.0 )
   at_cascade.csv.write_table(file_name, table)
   #
   # csv.fit, csv.predict
   at_cascade.csv.fit(fit_dir)
   at_cascade.csv.predict(fit_dir)
   #
   # predict_table
   file_name = f'{fit_dir}/fit_predict.csv'
   predict_table = at_cascade.csv.read_table(file_name)
   #
   # node
   for row in predict_table :
      avg_integrand = float( row['avg_integrand'] )
      assert abs( 1.0 - avg_integrand / no_effect_iota_true ) < 1e-5
#
if __name__ == '__main__' :
   main()
   print('csv_fit.py: OK')
# END_PYTHON
