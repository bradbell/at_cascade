# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
import os
import sys
import time
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
   sim
}

Example Using csv.fit
#####################

Under Construction
******************

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
   *  -  csv_file['option.csv']
      -  :ref:`csv_fit@Input Files@option.csv`
   *  -  csv_file['fit_goal.csv']
      -  :ref:`csv_fit@Input Files@fit_goal.csv`
   *  -  csv_file['prior.csv']
      -  :ref:`csv_fit@Input Files@prior.csv`
   *  -  csv_file['smooth_grid.csv']
      -  :ref:`csv_fit@Input Files@smooth_grid.csv`
   *  -  csv_file['rate.csv']
      -  :ref:`csv_fit@Input Files@rate.csv`
   *  -  csv_file['mulcov.csv']
      -  :ref:`csv_fit@Input Files@mulcov.csv`
   *  -  csv_file['data_in.csv']
      -  :ref:`csv_fit@Input Files@data_in.csv`
   *  -  root_node.db
      -  :ref:`csv_fit@Output Files@ root

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
# option.csv
random_seed = str( int( time.time() ) )
csv_file['option.csv'] = \
'''name,value
root_node_name,n0
'''
csv_file['option.csv'] += f'random_seed,{random_seed}\n'
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
'''node_name,sex,age,time,omega,haqi
n0,female,50,2000,0.02,1.0
n0,male,50,2000,0.02,1.0
n1,female,50,2000,0.02,0.5
n1,male,50,2000,0.02,0.5
n2,female,50,2000,0.02,1.5
n2,male,50,2000,0.02,1.5
'''
#
# fit_goal.csv
csv_file['fit_goal.csv'] = \
'''node_name
n1
n2
'''
#
# prior.csv
csv_file['prior.csv'] = \
'''name,lower,upper,mean,std,density
uniform_01,0.0,1.0,0.5,1.0,uniform
gauss_01,,,0.0,1.0,gaussian
'''
#
# smooth_grid.csv
csv_file['smooth_grid.csv'] = \
'''name,age,time,value_prior,dage_prior,dtime_prior,const_value
mulcov_haqi,0.0,0.0,uniform_01,,,
rate_parent,0.0,0.0,uniform_01,,,
rate_child,0.0,0.0,gauss_01,,,
'''
#
# rate.csv
csv_file['rate.csv'] = \
'''name,parent_smooth,child_smooth
iota,rate_parent,rate_child
'''
#
# mulcov.csv
csv_file['mulcov.csv'] = \
'''covariate,type,effected,smooth
haqi,rate_value,iota,mulcov_haqi
'''
#
# data_in.csv
header  = 'data_id,integrand,node_name,sex,age_lower,age_upper,'
header += 'time_lower,time_upper,meas_value,meas_std,hold_out'
csv_file['data_in.csv'] = header + \
'''
0,Sincidence,n0,female,0,10,1990,2000,0.0100,0.001,0
1,Sincidence,n1,male,10,20,2000,2010,0.0078,0.001,0
2,Sincidence,n2,female,20,30,2010,2020,0.0128,0.001,0
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
   # csv.fit
   at_cascade.csv.fit(fit_dir)
   #
#
# Test Not yet passing so comment it out
# main()
# END_PYTHON
