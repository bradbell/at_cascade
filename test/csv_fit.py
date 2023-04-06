# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-23 Bradley M. Bell
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
db2csv,true
plot,true
max_abs_effect,3.0
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
prevalence
mulcov_0
mulcov_1
'''
#
# prior.csv
csv_file['prior.csv'] = \
'''name,lower,upper,mean,std,density
uniform_1_1,-1.0,1.0,0.5,1.0,uniform
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
csv_file['mulcov.csv'] = \
'''covariate,type,effected,value_prior,const_value
sex,rate_value,iota,uniform_1_1,
one,meas_noise,Sincidence,,1e-3
'''
#
# data_in.csv
# The 0.00 meas_value in this table gets replaced
header  = 'data_id,integrand_name,node_name,sex,age_lower,age_upper,'
header += 'time_lower,time_upper,meas_value,meas_std,hold_out'
csv_file['data_in.csv'] = header + \
'''
0,Sincidence,n0,female,0,10,1990,2000,0.00,1e-4,0
0,Sincidence,n0,male,0,10,1990,2000,0.00,1e-4,0
1,Sincidence,n1,female,10,20,2000,2010,0.00,1e-4,0
1,Sincidence,n1,male,10,20,2000,2010,0.00,1e-4,0
2,Sincidence,n2,female,20,30,2010,2020,0.00,1e-4,0
2,Sincidence,n2,male,20,30,2010,2020,0.00,1e-4,0
'''

#
#
def main() :
   #
   # fit_dir
   fit_dir = 'build/test'
   if not os.path.exists(fit_dir) :
      os.makedirs(fit_dir)
   root_node_name = 'n0'
   if os.path.exists( fit_dir + '/' + root_node_name  ) :
      shutil.rmtree( fit_dir + '/' + root_node_name  )
   #
   # write csv files
   for name in csv_file :
      file_name = f'{fit_dir}/{name}'
      file_ptr  = open(file_name, 'w')
      file_ptr.write( csv_file[name] )
      file_ptr.close()
   #
   # sex_name2value
   sex_name2value  = { 'female' : -0.5, 'both' : 0.0, 'male' : 0.5 }
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
      effect    = true_mulcov_sex * sex_name2value[sex_name]
      iota      = math.exp(effect) * no_effect_iota
      row['meas_value'] = float_format.format( iota )
   at_cascade.csv.write_table(file_name, table)
   #
   # csv.fit, csv.predict
   at_cascade.csv.fit(fit_dir)
   at_cascade.csv.predict(fit_dir)
   #
   # number_sample
   number_sample = 20
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
            # sample_list
            sample_list = list()
            for row in predict_table :
               if row['integrand_name'] == 'Sincidence' and \
                     row['node_name'] == node and \
                        row['sex'] == sex_name :
                  #
                  sample_list.append(row)
            #
            # check sample_list
            if node == 'n0' or sex_name != 'both' :
               if prefix == 'fit' :
                  assert len(sample_list) == 1
               else :
                  assert len(sample_list) == number_sample
               sum_avgint = 0.0
               for row in sample_list :
                  sum_avgint   += float( row['avg_integrand'] )
               avgint    = sum_avgint / len(sample_list)
               sex_value = sex_name2value[sex_name]
               effect    = true_mulcov_sex * sex_value
               iota      = math.exp(effect) * no_effect_iota
               rel_error = (avgint - iota) / iota
               if abs(rel_error) > 0.01 :
                  print('rel_error =', rel_error)
                  assert False
   #
   # db2csv_file_list
   db2csv_name_list = [
      'log.csv',
      'age_avg.csv',
      'hes_fixed.csv',
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
      ('n0', 'male')   : 'n0/male' ,
      ('n1', 'female') : 'n0/female/n1' ,
      ('n1', 'male')   : 'n0/male/n1' ,
      ('n2', 'female') : 'n0/female/n2' ,
      ('n2', 'male')   : 'n0/male/n2' ,
   }
   #
   # check for db2csv files
   for (node, sex) in subdir_list :
      subdir = subdir_list[(node, sex)]
      for name in db2csv_name_list + [ 'data_plot.pdf', 'rate_plot.pdf' ] :
         file_path = f'{fit_dir}/{subdir}/{name}'
         assert os.path.exists(file_path)
   #
   new      = False
   file_name = f'{fit_dir}/n0/dismod.db'
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
main()
print('csv_fit: OK')
sys.exit(0)
# END_PYTHON
