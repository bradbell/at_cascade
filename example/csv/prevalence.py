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
}

Example Fitting iota From Just Prevalence Data
##############################################

Under Construction
******************

Shock in Incidence
******************
This example demonstrates inverting for a shock in true incidence (iota)
from just prevalence measurements.
To be specific, iota is constant and equal to 0.01
except for ages between 40 and 60 and times between 1990 and 2000.
During that special age time period, iota is equal to 0.1.

True Rates
**********
For this example, the true value for other case mortality (omega) is 0.01
and for excess mortality (chi) is 0.1.
The true value for incidence (iota) as a function of age (a) and time (t) is

.. math::

   \iota(a, t) = \begin{cases}
      0.1   & \R{if} \; a \in (40, 60) \; t \in (1990, 2000) \\
      0.01  & \R{otherwise}
   \end{cases}



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
# random_seed
random_seed = str( int( time.time() ) )
#
# age_grid, time_grid
age_set   = set( range(0, 120, 20) )     | set( range(35, 70, 5) )
time_set  = set( range(1980, 2030, 10) ) | set( range(1988, 2004, 2) )
age_grid  = sorted( list( age_set ) )
time_grid = sorted( list( time_set) )
#
# BEGIN_RATE_TRUTH
def rate_truth(rate_name, age, time) :
   if rate_name == 'omega' :
      return 0.01
   if rate_name == 'chi' :
      return 0.1
   if 40.0 < age and age < 60.0 and  1990 < time  and time < 2000 :
      return 0.1
   else :
      return 0.01
# END_RATE_TRUTH
# ----------------------------------------------------------------------------
# simulation files
# ----------------------------------------------------------------------------
#
# sim_file
sim_file = dict()
#
# option.csv
random_seed = str( int( time.time() ) )
sim_file['option.csv'] = \
'''name,value
absolute_tolerance,1e-5
float_precision,4
integrand_step_size,5
random_depend_sex,true
std_random_effects,.2
'''
sim_file['option.csv'] += f'random_seed,{random_seed}\n'
#
# node.csv
sim_file['node.csv'] = \
'''node_name,parent_name
n0,
n1,n0
n2,n0
'''
#
# covariate.csv
omega = rate_truth('omega', 0, 0)
sim_file['covariate.csv'] = 'node_name,sex,age,time,omega\n'
omega_truth = 0.01
for node_name in [ 'n0', 'n1', 'n2' ] :
   for sex in [ 'female', 'male' ] :
      for age in age_grid :
         for time in time_grid :
            row = f'{node_name},{sex},{age},{time},{omega}\n'
            sim_file['covariate.csv'] += row
#
# no_effect_rate.csv
chi = rate_truth('chi', 0, 0)
sim_file['no_effect_rate.csv'] = 'rate_name,age,time,rate_truth\n'
sim_file['no_effect_rate.csv'] += f'chi,0,0,{chi}\n'
for age in age_grid :
   for time in time_grid :
      iota = rate_truth('iota', age, time)
      sim_file['no_effect_rate.csv'] += f'iota,{age},{time},{iota}\n'
#
# multiplier_sim.csv
sim_file['multiplier_sim.csv'] = \
'multiplier_id,rate_name,covariate_or_sex,multiplier_truth\n'
#
# simulate.csv
header  = 'simulate_id,integrand_name,node_name,sex,age_lower,age_upper,'
header += 'time_lower,time_upper,percent_cv\n'
sim_file['simulate.csv'] = header
simulate_id     = -1
percent_cv      = 5.0
for integrand_name in [ 'Sincidence', 'prevalence' ] :
   for node_name in [ 'n0', 'n1', 'n2' ] :
      for sex in [ 'female', 'male' ] :
         for age in age_grid :
            for time in time_grid :
               simulate_id += 1
               row  = f'{simulate_id},{integrand_name},{node_name},{sex},'
               row += f'{age},{age},{time},{time},{percent_cv}\n'
               sim_file['simulate.csv'] += row
# ----------------------------------------------------------------------------
# fit files
# ----------------------------------------------------------------------------
#
# fit_file
fit_file = dict()
#
# option_in.csv
fit_file['option_in.csv']  =  \
'''name,value
refit_split,false
quasi_fixed,true
max_num_iter_fixed,300
'''
fit_file['option_in.csv'] += f'random_seed,{random_seed}\n'
#
# fit_goal.csv
fit_file['fit_goal.csv'] = \
'''node_name
n1
n2
'''
#
# predict_integrand.csv
fit_file['predict_integrand.csv'] = \
'''integrand_name
Sincidence
prevalence
'''
#
# prior.csv
fit_file['prior.csv'] = \
'''name,density,mean,std,eta,lower,upper
uniform_eps_1,uniform,0.01,,,1e-6,1.0
delta_prior,log_gaussian,0.0,0.05,1e-4,,
'''
#
# child_rate.csv
fit_file['child_rate.csv'] = \
'''rate_name,value_prior
iota,delta_prior
'''
#
# mulcov.csv
fit_file['mulcov.csv'] = 'covariate,type,effected,value_prior,const_value\n'
#
#
# -----------------------------------------------------------------------------
# sim
def sim(sim_dir) :
   #
   # write input csv files
   for name in sim_file :
      file_name = f'{sim_dir}/{name}'
      file_ptr  = open(file_name, 'w')
      file_ptr.write( sim_file[name] )
      file_ptr.close()
   #
   # csv.simulate
   at_cascade.csv.simulate(sim_dir)
   #
   # data_join.csv
   at_cascade.csv.join_file(
      left_file   = f'{sim_dir}/simulate.csv' ,
      right_file  = f'{sim_dir}/data_sim.csv' ,
      result_file = f'{sim_dir}/data_join.csv'     ,
   )
# -----------------------------------------------------------------------------
# fit
def fit(sim_dir, fit_dir) :
   #
   # node.csv, covarite.csv
   for file_name in [ 'node.csv', 'covariate.csv' ] :
      shutil.copyfile(
         src = f'{sim_dir}/{file_name}' ,
         dst = f'{fit_dir}/{file_name}' ,
      )
   #
   # fit_file['parent_rate.csv']
   chi   = rate_truth('chi', 0, 0)
   data  = 'rate_name,age,time,value_prior,dage_prior,dtime_prior,const_value\n'
   data  += f'chi,0.0,0.0,,,,{chi}\n'
   for age in age_grid :
      for time in time_grid :
         data  += f'iota,{age},{time},uniform_eps_1,delta_prior,delta_prior,\n'
   fit_file['parent_rate.csv'] = data
   #
   # csv files in fit_file
   for name in fit_file :
      file_name = f'{fit_dir}/{name}'
      file_ptr  = open(file_name, 'w')
      file_ptr.write( fit_file[name] )
      file_ptr.close()
   #
   # data_join_table
   # This is a join of simulate.csv and dats_sim.csv
   data_join_table = at_cascade.csv.read_table(
      file_name = f'{sim_dir}/data_join.csv'
   )
   #
   # data_in.csv
   table = list()
   for row_join in data_join_table :
      #
      # row_in
      row_in = dict()
      copy_list  = [ 'integrand_name', 'node_name', 'sex' ]
      copy_list += [ 'age_lower', 'age_upper', 'time_lower', 'time_upper' ]
      row_in['data_id']   = row_join['simulate_id']
      row_in['integrand'] = row_join['integrand_name']
      for key in copy_list :
         row_in[key] = row_join[key]
      row_in['meas_value'] = row_join['meas_mean']
      row_in['meas_std']   = 1e-3
      if row_join['integrand_name'] == 'Sincidence' :
         row_in['hold_out'] = '1'
      else :
         row_join['integrand_name'] == 'prevalence'
         row_in['hold_out'] = '0'
      #
      if float( row_in['meas_std'] ) != 0.0 :
         table.append( row_in )
   #
   at_cascade.csv.write_table(
         file_name = f'{fit_dir}/data_in.csv' ,
         table     = table ,
   )
   #
   # fit
   at_cascade.csv.fit(fit_dir)
   #
   # data
# -----------------------------------------------------------------------------
# Without this, the mac will try to execute main on each processor.
if __name__ == '__main__' :
   #
   # sim_dir
   sim_dir = 'build/example/csv/sim'
   if not os.path.exists(sim_dir) :
      os.makedirs(sim_dir)
   #
   # clear out a previous run
   if os.path.exists( 'build/example/csv/fit/n0' ) :
      shutil.rmtree( 'build/example/csv/fit/n0' )
   #
   # fit_dir
   fit_dir = 'build/example/csv/fit'
   if not os.path.exists(fit_dir) :
      os.mkdir(fit_dir)
   #
   sim(sim_dir)
   fit(sim_dir, fit_dir)
   #
   print('csv_prevalence: Under Construction')
   sys.exit(0)
# END_PYTHON
