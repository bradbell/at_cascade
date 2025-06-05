# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-25 Bradley M. Bell
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
#
# csv_file
csv_file = dict()
#
# option_fit.csv
# choose asymptotic_rcond_lower so that its test will fail
random_seed = str( int( time.time() ) )
csv_file['option_fit.csv'] = \
'''name,value
sample_method,asymptotic
no_ode_ignore,iota
root_node_name,n0
asymptotic_rcond_lower,0.1
'''
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
'''
#
# covariate.csv
csv_file['covariate.csv'] = \
'''node_name,sex,age,time,omega
n0,female,50,2000,0.02
n0,male,50,2000,0.02
'''
#
# fit_goal.csv
# n-1 and n3 are not not below the root node n0, hence not fit
csv_file['fit_goal.csv'] = \
'''node_name
'''
#
# predict_integrand.csv
csv_file['predict_integrand.csv'] = \
'''integrand_name
'''
#
# prior.csv
# The correspnding reciprocal condition number is (4 / 10) squared; i.e., 0.04
csv_file['prior.csv'] = \
'''name,lower,upper,mean,std,density
gaussian_eps_10,1e-6,1.0,0.5,10.0,gaussian
gaussian_eps_2,1e-6,1.0,0.5,2.0,gaussian
'''
#
# parent_rate.csv
csv_file['parent_rate.csv'] = \
'''rate_name,age,time,value_prior,dage_prior,dtime_prior,const_value
iota,0.0,0.0,gaussian_eps_10,,,
iota,100.0,0.0,gaussian_eps_2,,,
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
csv_file['data_in.csv'] = header
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
   database= f'{fit_dir}/n0/dismod.db'
   connection = dismod_at.create_connection(
      database, new = False, readonly = True
   )
   sample_exists = at_cascade.table_exists(connection, 'sample')
   assert not sample_exists
#
main()
print( 'rcond_lower.py: OK' )
