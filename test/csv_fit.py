# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
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
"""
{xrst_begin csv_fit_xam}
{xrst_spell
   dir
}

Example Using csv.fit
#####################

Node Tree
*********
::

                n0
          /-----/\-----\
        n1              n2

.. list-table::
   :header-rows: 1

   *  -  Symbol
      -  Documentation
   *  -  fit_dir
      -  :ref:`csv_fit@fit_dir`
   *  -  csv_file['node.csv']
      -  :ref:`csv_fit@Input Files@node.csv`
   *  -  csv_file['covariate.csv']
      -  :ref:`csv_fit@Input Files@covariate.csv`
   *  -  csv_file['option_in.csv']
      -  :ref:`csv_fit@Input Files@option_in.csv`
   *  -  csv_file['fit_goal.csv']
      -  :ref:`csv_fit@Input Files@fit_goal.csv`
   *  -  csv_file['predict_integrand.csv']
      -  :ref:`csv_fit@Input Files@predict_integrand.csv`
   *  -  csv_file['prior.csv']
      -  :ref:`csv_fit@Input Files@prior.csv`
   *  -  csv_file['parent_rate.csv']
      -  :ref:`csv_fit@Input Files@parent_rate.csv`
   *  -  csv_file['child_rate.csv']
      -  :ref:`csv_fit@Input Files@child_rate.csv`
   *  -  csv_file['mulcov.csv']
      -  :ref:`csv_fit@Input Files@mulcov.csv`
   *  -  csv_file['data_in.csv']
      -  :ref:`csv_fit@Input Files@data_in.csv`
   *  -  root_node.db
      -  :ref:`csv_fit@Output Files@root_node.db`
   *  -  option_out.csv
      -  :ref:`csv_fit@Output Files@option_out.csv`
   *  -  fit_predict.csv
      -  :ref:`csv_fit@Output Files@fit_predict.csv`
   *  -  sam_predict.csv
      -  :ref:`csv_fit@Output Files@sam_predict.csv`

{xrst_literal
   BEGIN_PYTHON
   END_PYTHON
}


{xrst_end csv_fit_xam}
"""
# BEGIN_PYTHON
#
# csv_file
csv_file = dict()
#
# option_in.csv
random_seed = str( int( time.time() ) )
csv_file['option_in.csv'] = \
'''name,value
db2csv,true
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
header  = 'data_id,integrand,node_name,sex,age_lower,age_upper,'
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
   fit_dir = 'build/csv'
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
      sex_name = row['sex']
      integrand = row['integrand']
      assert integrand == 'Sincidence'
      #
      sex_name  = row['sex']
      effect    = true_mulcov_sex * sex_name2value[sex_name]
      iota      = math.exp(effect) * no_effect_iota
      row['meas_value'] = float_format.format( iota )
   at_cascade.csv.write_table(file_name, table)
   #
   # csv.fit
   at_cascade.csv.fit(fit_dir)
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
               if row['integrand'] == 'Sincidence' and \
                     row['node'] == node and \
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
      for name in db2csv_name_list :
         file_path = f'{fit_dir}/{subdir}/{name}'
         assert os.path.exists(file_path)
#
main()
print('csv_fit: OK')
sys.exit(0)
# END_PYTHON
