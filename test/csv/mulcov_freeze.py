# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ----------------------------------------------------------------------------
import os
import sys
import time
import math
import numpy
import shutil
# import at_cascade with a preference current directory version
current_directory = os.getcwd()
if os.path.isfile( current_directory + '/at_cascade/__init__.py' ) :
   sys.path.insert(0, current_directory)
import at_cascade
import dismod_at
# BEGIN_PYTHON
#
# age_list, node_list, sex_list, no_effect_iota, alpha_true
age_list       = [ 0.0, 50.0, 100.0 ]
node_list      = [ 'n0', 'n1', 'n2', 'n3' ]
sex_list       = [ 'female', 'male' ]
no_effect_iota = 1e-3
alpha_true     = -0.5
#
# csv_file
csv_file = dict()
#
# option_fit.csv
random_seed = str( int( time.time() ) )
csv_file['option_fit.csv'] = \
'''name,value
max_abs_effect,3.0
no_ode_ignore,iota
root_node_name,n0
number_sample,100
freeze_type,posterior
tolerance_fixed,1e-8
child_prior_std_factor,1.0
'''
#
# option_predict.csv
random_seed = str( int( time.time() ) )
csv_file['option_predict.csv'] = \
'''name,value
db2csv,true
plot,false
'''
#
# node.csv
# Use node n-1 to test starting below the base of the tree
csv_file['node.csv'] = \
'''node_name,parent_name
n0,
n1,n0
n2,n1
n3,n2
'''
# covariate.csv
csv_file['covariate.csv'] = 'node_name,sex,income,age,time,omega\n'
for node in node_list :
   for sex in sex_list :
      for age in age_list :
         income = age / 100.
         line   = f'{node},{sex},{income},{age},2000,0.02\n'
         csv_file['covariate.csv'] += line
#
# fit_goal.csv
csv_file['fit_goal.csv'] = \
'''node_name
'''
#
# predict_integrand.csv
csv_file['predict_integrand.csv'] = \
'''integrand_name
mulcov_0
'''
#
# prior.csv
csv_file['prior.csv'] = \
'''name,lower,upper,mean,std,density
gaussian_0_100,-1.0,1.0,0.5,100.0,gaussian
uniform_eps_10,1e-6,1.0,0.005,10.0,uniform
gauss_01,,,0.0,1.0,gaussian
'''
#
# parent_rate.csv
csv_file['parent_rate.csv'] = \
'''rate_name,age,time,value_prior,dage_prior,dtime_prior,const_value
iota,0.0,0.0,uniform_eps_10,,,
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
income,rate_value,iota,gaussian_0_100,
'''
#
# data_in.csv
header  = 'data_id,integrand_name,node_name,sex,age_lower,age_upper,'
header += 'time_lower,time_upper,meas_value,meas_std,hold_out,'
header += 'density_name,eta,nu\n'
csv_file['data_in.csv'] = header
data_id = 0
for node in node_list :
   # age_range
   # Only node n0 has income variation. Hence the fits below n0
   # will have the prior and posterior for alpha equal.
   age_range = age_list if node == 'n0' else [ 50.0 ]
   for sex in sex_list :
      for age in age_range :
         income     = age / 100.
         meas_value = no_effect_iota * math.exp(- alpha_true * income)
         meas_std   = meas_value
         line   = f'{data_id},Sincidence,{node},{sex},{age},{age},'
         line  += f'2000,2000,{meas_value:.5g},{meas_std},0,'
         line  += 'gaussian,,\n'
         csv_file['data_in.csv'] += line
         data_id += 1
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
   # csv.fit, csv.predict
   at_cascade.csv.fit(fit_dir)
   at_cascade.csv.predict(fit_dir)
   #
   # sam_predict_table
   file_name = f'{fit_dir}/sam_predict.csv'
   sam_predict_table = at_cascade.csv.read_table(file_name)
   #
   # sex
   for sex in sex_list :
      #
      # sample_list
      sample_list = dict()
      for node in node_list :
         sample_list[node] = list()
      for row in sam_predict_table :
         if int(row['avgint_id']) == 0 :
            node = row['node_name']
            if node == row['fit_node_name'] and sex == row['fit_sex'] :
               sample_list[node].append( float( row['avg_integrand'] ) )

      # sample_mean, sample_std
      sample_std = dict()
      sample_mean = dict()
      for node in node_list :
         sample_mean[node] = numpy.mean(sample_list[node])
         sample_std[node]  = numpy.std(sample_list[node])
      #
      # check
      for node in [ 'n1', 'n2', 'n3' ] :
         relative_difference = 1.0 - sample_std[node] / sample_std['n0']
         if abs(relative_difference) > 0.2 :
            print(relative_difference)
            assert False
      #
      # 2DO:
      # The simulations for n1, n2, n3, and n4 are using the exact
      # same random seed. This should be fixed
      eps99 = numpy.finfo(float).eps
      for node in [ 'n2', 'n3' ] :
         relative_difference = 1.0 - sample_std[node] / sample_std['n1']
         if abs( relative_difference ) > eps99 :
            print(relative_difference)
            assert False
      #
      # 2DO:
      # The simulations for n1, n2, n3, and n4 are using the exact

#
if __name__ == '__main__' :
   main()
   print('mulcov_freeze.py: OK')
# END_PYTHON
