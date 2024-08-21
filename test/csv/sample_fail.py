# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ----------------------------------------------------------------------------
# Test prdictions when on of the fits or samples fails.
# This also tests predictions when a there is no data for a fit.
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
#
# csv_file
csv_file = dict()
#
# option_fit.csv
random_seed = str( int( time.time() ) )
csv_file['option_fit.csv'] = \
'''name,value
number_sample,3
'''
#
# option_predict.csv
random_seed = str( int( time.time() ) )
csv_file['option_predict.csv'] = \
'''name,value
db2csv,true
plot,true
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
'''node_name,sex,age,time,omega
n0,female,50,2000,0.02
n1,female,50,2000,0.02
n2,female,50,2000,0.02
n0,male,50,2000,0.02
n1,male,50,2000,0.02
n2,male,50,2000,0.02
'''
#
# fit_goal.csv
csv_file['fit_goal.csv'] = \
'''node_name
n1
n2
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
uniform_eps_1,1e-6,1.0,0.5,,uniform
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
'''
#
# mulcov.csv
csv_file['mulcov.csv'] = \
'''covariate,type,effected,value_prior,const_value
'''
#
# data_in.csv
# The 0.00 meas_value in this table gets replaced
header  = 'data_id,integrand_name,node_name,sex,age_lower,age_upper,'
header += 'time_lower,time_upper,meas_value,meas_std,hold_out,'
header += 'density_name,eta,nu'
csv_file['data_in.csv'] = header + \
'''
0,Sincidence,n0,female,0,10,1990,2000,0.00,1e-4,0,gaussian,,
1,Sincidence,n1,female,10,20,2000,2010,0.00,1e-4,0,gaussian,,
2,Sincidence,n2,female,20,30,2010,2020,0.00,1e-4,0,gaussian,,
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
   no_effect_iota    = 0.1
   file_name         = f'{fit_dir}/data_in.csv'
   table             = at_cascade.csv.read_table( file_name )
   for row in table :
      integrand_name = row['integrand_name']
      assert integrand_name == 'Sincidence'
      #
      row['meas_value'] = float_format.format( no_effect_iota )
   at_cascade.csv.write_table(file_name, table)
   #
   # csv.fit, csv.predict
   at_cascade.csv.fit(fit_dir)
   at_cascade.csv.predict(fit_dir)
   #
   # number_sample
   number_sample = 3
   #
   # prefix
   for prefix in [ 'fit', 'sam' ] :
      #
      # predict_table
      file_name = f'{fit_dir}/{prefix}_predict.csv'
      predict_table = at_cascade.csv.read_table(file_name)
      #
      # node
      for node in [ 'n0', 'n1', 'n2' ] :
         # sex_name
         for sex_name in [ 'female', 'both', 'male' ] :
            #
            if node == 'n0' or sex_name != 'both' :
               #
               # sample_list
               sample_list = list()
               for row in predict_table :
                  assert row['integrand_name'] == 'Sincidence'
                  if row['node_name'] == node and row['sex'] == sex_name :
                     sample_list.append(row)
                     if sex_name == 'male' :
                        assert row['fit_node_name'] == 'n0'
                        assert row['fit_sex'] == 'both'
                     else :
                        assert row['fit_node_name'] == node
                        assert row['fit_sex'] == sex_name
               #
               # check sample_list
               if prefix == 'fit' :
                  assert len(sample_list) == 1
               else :
                  assert len(sample_list) == number_sample
               sum_avgint = 0.0
               for row in sample_list :
                  sum_avgint   += float( row['avg_integrand'] )
               avgint    = sum_avgint / len(sample_list)
               rel_error = (avgint - no_effect_iota) / no_effect_iota
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
   subdir_list = {
      ('n0', 'both')   : 'n0' ,
      ('n0', 'female') : 'n0/female' ,
      ('n1', 'female') : 'n0/female/n1' ,
      ('n2', 'female') : 'n0/female/n2' ,
   }
   # These cases should fail to fit, or at the least fail to sample
   # ('n0', 'male')   : 'n0/male' ,
   # ('n1', 'male')   : 'n0/male/n1' ,
   # ('n2', 'male')   : 'n0/male/n2' ,
   #
   # check for db2csv files
   for (node, sex) in subdir_list :
      subdir = subdir_list[(node, sex)]
      for name in db2csv_name_list + [ 'data_plot.pdf', 'rate_plot.pdf' ] :
         file_path = f'{fit_dir}/{subdir}/{name}'
         assert os.path.exists(file_path)
#
if __name__ == '__main__' :
   main()
   print('csv_sample_fail.py: OK')
