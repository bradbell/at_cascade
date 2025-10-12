# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-25 Bradley M. Bell
# ----------------------------------------------------------------------------
# Test that perturb makes starting at solution work.
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
# iota_true
iota_true = 2.0e-3;
#
# csv_file
csv_file = dict()
#
# option_fit.csv
random_seed = str( int( time.time() ) )
csv_file['option_fit.csv'] = \
'''name,value
refit_split,false
ode_method,trapezoidal
perturb_optimization_scale,1.0
perturb_optimization_start,1.0
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
iota_tmp = 1.001 * iota_true;
csv_file['prior.csv']  = 'name,lower,upper,mean,std,density\n'
csv_file['prior.csv'] += f'gaussian,-1.0,1.0,{iota_tmp},1.0,gaussian\n'
#
# parent_rate.csv
csv_file['parent_rate.csv'] = \
'''rate_name,age,time,value_prior,dage_prior,dtime_prior,const_value
iota,0.0,0.0,gaussian,,,
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
header += 'density_name,eta,nu\n'
csv_file['data_in.csv']  = header
csv_file['data_in.csv'] += \
   f'0,Sincidence,n0,both,0,10,1990,2000,{iota_true},1e-4,0,gaussian,,\n'
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
   # connection
   file_name  = f'{fit_dir}/n0/dismod.db'
   connection = dismod_at.create_connection(
      file_name, new = False, readonly = True
   )
   #
   # iota_index
   var_table  = dismod_at.get_table_dict(connection, 'var');
   rate_table = dismod_at.get_table_dict(connection, 'rate');
   iota_index = None
   for index in range( len(var_table) ) :
      if rate_table[ var_table[index]['rate_id'] ]['rate_name'] == 'iota' :
         iota_index = index
   assert iota_index != None
   for tbl_name in [ 'start_var', 'scale_var' ] :
      table      = dismod_at.get_table_dict(connection, tbl_name);
      iota_value = table[iota_index][f'{tbl_name}_value']
      assert abs( 1.0 - iota_value / iota_true ) > 0.1
   #
   # connection
   connection.close()
#
if __name__ == '__main__' :
   main()
   print('csv.perturb: OK')
# END_PYTHON
