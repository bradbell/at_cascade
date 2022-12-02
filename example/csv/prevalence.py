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
{xrst_begin csv_prevalence}
{xrst_spell
   dir
}

Example Fitting iota From Just Prevalnce Data
#############################################

Under Construction
******************

Node Tree
*********
::

                n0
          /-----/\-----\
        n1              n2

{xrst_literal
   BEGIN_PYTHON
   END_PYTHON
}


{xrst_end csv_prevalence}
"""
# BEGIN_PYTHON
# --------------------------------------------------------------------------
#
# age_grid, time_grid
age_grid  = range(0, 110, 10)
time_grid = range(1980, 2025, 5)
#
# rate_truth
def rate_truth(rate_name, time) :
   if rate_name == 'omega' :
      return 0.01
   if rate_name == 'chi' :
      return 0.1
   assert rate_name == 'iota'
   assert 40 in age_grid
   assert 1990 in time_grid
   if age == 40 and time == 1990 :
      return 0.01
   else :
      return 0.01
#
# csv_file
csv_file = dict()
# ----------------------------------------------------------------------------
# simulation
# ----------------------------------------------------------------------------
#
# option.csv
random_seed = str( int( time.time() ) )
csv_file['option.csv'] = \
'''name,value
absolute_tolerance,1e-5
float_precision,4
integrand_step_size,5
random_depend_sex,true
std_random_effects,.1
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
omega = rate_truth('omega', 0)
csv_file['covariate.csv'] = 'node_name,sex,age,time,omega\n'
omega_truth = 0.01
for node_name in [ 'n0', 'n1', 'n2' ] :
   for sex in [ 'female', 'male' ] :
      for age in age_grid :
         for time in time_grid :
            row = f'{node_name},{sex},{age},{time},{omega}\n'
            csv_file['covariate.csv'] += row
#
# no_effect_rate.csv
chi = rate_truth('chi', 0)
csv_file['no_effect_rate.csv'] = 'rate_name,age,time,rate_truth\n'
csv_file['no_effect_rate.csv'] += f'chi,0,0,{chi}\n'
for age in age_grid :
   for time in time_grid :
      iota = rate_truth('iota', time)
      csv_file['no_effect_rate.csv'] += f'iota,{age},{time},{iota}\n'
#
# multiplier_sim.csv
csv_file['multiplier_sim.csv'] = \
'multiplier_id,rate_name,covariate_or_sex,multiplier_truth\n'
#
# simulate.csv
header  = 'simulate_id,integrand_name,node_name,sex,age_lower,age_upper,'
header += 'time_lower,time_upper,percent_cv\n'
csv_file['simulate.csv'] = header
integrand_name = 'prevalence'
simulate_id     = -1
percent_cv      = 5.0
for node_name in [ 'n0', 'n1', 'n2' ] :
   for sex in [ 'female', 'male' ] :
      for age in age_grid :
         for time in time_grid :
            simulate_id += 1
            row  = f'{simulate_id},{integrand_name},{node_name},{sex},'
            row += f'{age},{age},{time},{time},{percent_cv}\n'
            csv_file['simulate.csv'] += row
#
def sim() :
   #
   # sim_dir
   sim_dir = 'build/csv'
   if not os.path.exists(sim_dir) :
      os.makedirs(sim_dir)
   #
   # write csv files
   for name in csv_file :
      file_name = f'{sim_dir}/{name}'
      file_ptr  = open(file_name, 'w')
      file_ptr.write( csv_file[name] )
      file_ptr.close()
   #
   # csv.simulate
   at_cascade.csv.simulate(sim_dir)
   #
   # data.csv
   at_cascade.csv.join_file(
      left_file   = f'{sim_dir}/simulate.csv' ,
      right_file  = f'{sim_dir}/data_sim.csv' ,
      result_file = f'{sim_dir}/data.csv'     ,
   )
   #
   # csv_table
   csv_table = dict()
   for name in csv_file :
      file_name       = f'{sim_dir}/{name}'
      csv_table[name] = at_cascade.csv.read_table( file_name )
   #
#
#
# Without this, the mac will try to execute main on each processor.
if __name__ == '__main__' :
   sim()
   print('csv_prevalence: Under Construction')
   sys.exit(0)
# END_SOURCE
