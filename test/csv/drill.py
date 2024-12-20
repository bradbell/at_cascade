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
# csv_file
csv_file = dict()
#
# option_fit.csv
random_seed = str( int( time.time() ) )
csv_file['option_fit.csv'] = \
'''name,value
max_abs_effect,3.0
number_sample,10
sample_method,simulate
no_ode_ignore,iota
root_node_name,n0
'''
#
# option_predict.csv
random_seed = str( int( time.time() ) )
csv_file['option_predict.csv'] = \
'''name,value
db2csv,false
plot,false
'''
#
# node.csv
# Use node n-1 to test starting below the base of the tree
csv_file['node.csv'] = \
'''node_name,parent_name
n-1,
n0,n-1
n1,n0
n2,n0
n3,n-1
'''
#
# sex_name2income
sex_name2income = { 'female' : 1.0, 'both' : 1.5, 'male' : 2.0 }
#
# covariate.csv
csv_file['covariate.csv'] = \
'''node_name,sex,income,age,time,omega
n-1,female,1.0,50,2000,0.02
n0,female,1.0,50,2000,0.02
n1,female,1.0,50,2000,0.02
n2,female,1.0,50,2000,0.02
n3,female,1.0,50,2000,0.02
n-1,male,2.0,50,2000,0.02
n0,male,2.0,50,2000,0.02
n1,male,2.0,50,2000,0.02
n2,male,2.0,50,2000,0.02
n3,male,2.0,50,2000,0.02
'''
#
# fit_goal.csv
# do a drill do n2
csv_file['fit_goal.csv'] = \
'''node_name
n2
'''
#
# predict_integrand.csv
csv_file['predict_integrand.csv'] = \
'''integrand_name
Sincidence
prevalence
mulcov_0
mulcov_1
'''
#
# prior.csv
csv_file['prior.csv'] = \
'''name,lower,upper,mean,std,density
gaussian_0_10,-1.0,1.0,0.5,10.0,gaussian
gaussian_eps_10,1e-6,1.0,0.5,10.0,gaussian
gauss_01,,,0.0,1.0,gaussian
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
iota,gauss_01
'''
#
# mulcov.csv
csv_file['mulcov.csv'] = \
'''covariate,type,effected,value_prior,const_value
income,rate_value,iota,gaussian_0_10,
one,meas_noise,Sincidence,,1e-3
'''
#
# data_in.csv
# The 0.00 meas_value in this table gets replaced
header  = 'data_id,integrand_name,node_name,sex,age_lower,age_upper,'
header += 'time_lower,time_upper,meas_value,meas_std,hold_out,'
header += 'density_name,eta,nu'
csv_file['data_in.csv'] = header + \
'''
0,Sincidence,n0,both,0,10,1990,2000,0.00,1e-4,0,gaussian,,
1,Sincidence,n0,both,0,10,1990,2000,0.00,1e-4,0,gaussian,,
2,Sincidence,n1,female,10,20,2000,2010,0.00,1e-4,0,gaussian,,
3,Sincidence,n1,male,10,20,2000,2010,0.00,1e-4,0,gaussian,,
4,Sincidence,n2,female,20,30,2010,2020,0.00,1e-4,0,gaussian,,
5,Sincidence,n2,male,20,30,2010,2020,0.00,1e-4,0,gaussian,,
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
   float_format      = '{0:.5g}'
   true_mulcov_sex   = 0.5
   no_effect_iota    = 0.1
   file_name         = f'{fit_dir}/data_in.csv'
   table             = at_cascade.csv.read_table( file_name )
   for row in table :
      sex_name       = row['sex']
      integrand_name = row['integrand_name']
      assert integrand_name == 'Sincidence'
      #
      sex_name  = row['sex']
      effect    = true_mulcov_sex * ( sex_name2income[sex_name] - 1.5)
      iota      = math.exp(effect) * no_effect_iota
      row['meas_value'] = float_format.format( iota )
   at_cascade.csv.write_table(file_name, table)
   #
   # csv.fit, csv.predict
   at_cascade.csv.fit(fit_dir)
   at_cascade.csv.predict(fit_dir)
   #
   # number_sample
   number_sample = 10
   #
   # prefix
   for prefix in [ 'fit', 'sam' ] :
      #
      # predict_table
      file_name = f'{fit_dir}/{prefix}_predict.csv'
      predict_table = at_cascade.csv.read_table(file_name)
      #
      # node
      for node in [ 'n-1', 'n0', 'n1', 'n2', 'n3' ] :
         # sex_name
         for sex_name in [ 'female', 'both', 'male' ] :
            #
            # sample_list
            sample_list = list()
            for row in predict_table :
               if row['integrand_name'] == 'Sincidence' and \
               row['node_name'] == node and \
               row['sex'] == sex_name :
                  sample_list.append(row)
            #
            # check sample_list
            if node in [ 'n-1', 'n1' , 'n3' ] :
               assert len(sample_list) == 0
            elif node != 'n0' and sex_name == 'both' :
               assert len(sample_list) == 0
            elif node == 'n0' and sex_name == 'both' :
               if prefix == 'fit' :
                  assert len(sample_list) == 1
               else :
                  assert len(sample_list) == number_sample
            else :
               if prefix == 'fit' :
                  assert len(sample_list) == 2
               else :
                  assert len(sample_list) == 2 * number_sample
            if len(sample_list) > 0 :
               sum_avgint = 0.0
               for row in sample_list :
                  sum_avgint   += float( row['avg_integrand'] )
               avgint    = sum_avgint / len(sample_list)
               income    = sex_name2income[sex_name]
               effect    = true_mulcov_sex * (income - 1.5)
               iota      = math.exp(effect) * no_effect_iota
               rel_error = (avgint - iota) / iota
               if abs(rel_error) > 0.01 :
                  print('rel_error =', rel_error)
                  assert False
   #
   # db2csv_file_list
   # hes_fixed.csv would be included if sample_method was asymptotic.
   db2csv_name_list = [
      'log.csv',
      'age_avg.csv',
      'trace_fixed.csv',
      'mixed_info.csv',
      'variable.csv',
      'data.csv',
      'predict.csv',
   ]
   #
   # subdir_list
   check_list = [
      { 'dir' : 'n0',            'exists' : True },
      { 'dir' : 'n0/female',     'exists' : True },
      { 'dir' : 'n0/male',       'exists' : True },
      { 'dir' : 'n0/female/n1',  'exists' : False},
      { 'dir' : 'n0/male/n1',    'exists' : False},
      { 'dir' : 'n0/female/n2',  'exists' : True  },
      { 'dir' : 'n0/male/n2',    'exists' : True  },
   ]
   #
   # check for db2csv files
   for check in check_list :
      subdir = check['dir']
      path   = f'{fit_dir}/{subdir}'
      assert os.path.exists(path) == check['exists']
   #
   file_name = f'{fit_dir}/n0/dismod.db'
   new      = False
   connection = dismod_at.create_connection(file_name, new)
   tbl_name   = 'bnd_mulcov'
   bnd_mulcov_table = dismod_at.get_table_dict(connection, tbl_name)
   connection.close()
   max_mulcov     = bnd_mulcov_table[0]['max_mulcov']
   max_cov_diff   = bnd_mulcov_table[0]['max_cov_diff']
   max_abs_effect = 3.0
   assert max_cov_diff == 0.5
   assert max_mulcov == max_abs_effect / max_cov_diff
#
if __name__ == '__main__' :
   main()
   print('csv_fit.py: OK')
# END_PYTHON
