# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ----------------------------------------------------------------------------
# Test the following:
# 1. Prevalence data requires solving the ODE.
# 2. std_random_effect_pini works.
#
# For this test, rho and chi are zero, iota and omega are constant, and
# the dismod ODE is S(0) = 1-pini, C(0) = pini,
#  S'(a) = - iota * S(a)
#  C'(a) = + iota * S(a)
#
# This corresponding solution is
#  S(a) =       (1 - pini) * exp(-iota * a)
#  C(a) =  1  - (1 - pini) * exp(-iota * a)
# see ode_iota_omega in doucmentation.
#
# The average of exp( -lambda * a) from a = low to a = up is
#  [ exp( -lambda * low) - exp( -lambda * up) ] / [ lambda * (up - low) ]
#
import os
import sys
import time
import math
import numpy
# import at_cascade with a preference current directory version
current_directory = os.getcwd()
if os.path.isfile( current_directory + '/at_cascade/__init__.py' ) :
   sys.path.insert(0, current_directory)
import at_cascade
# BEGIN_PYTHON
#
# csv_file
csv_file = dict()
#
# option_sim.csv
random_seed = str( int( time.time() ) )
csv_file['option_sim.csv'] = \
'''name,value
absolute_tolerance,1e-4
float_precision,4
std_random_effects_pini,.1
std_random_effects_iota,.1
std_random_effects_chi,.1
integrand_step_size,1.0
random_depend_sex,false
'''
csv_file['option_sim.csv'] += f'random_seed,{random_seed}\n'
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
# omega = 0.0
csv_file['covariate.csv'] = \
'''node_name,sex,age,time,omega,haqi
n0,female,50,2000,0.0,1.0
n0,male,50,2000,0.0,1.0
n1,female,50,2000,0.0,0.5
n1,male,50,2000,0.0,0.5
n2,female,50,2000,0.0,1.5
n2,male,50,2000,0.0,1.5
'''
#
# no_effect_rate.csv
# Add chi, and pini, but set them to zero.
# iota = 0.01, chi = 0.0, pini = 0.02
csv_file['no_effect_rate.csv'] = \
'''rate_name,age,time,rate_truth
iota,0.0,1980.0,0.01
chi,0.0,1980.0,0.00
pini,0.0,1980.0,0.02
'''
#
# multiplier_sim.csv
csv_file['multiplier_sim.csv'] = \
'''multiplier_id,rate_name,covariate_or_sex,multiplier_truth
'''
#
# simulate.csv
header  = 'simulate_id,integrand_name,node_name,sex,age_lower,age_upper,'
header += 'time_lower,time_upper,meas_std_cv,meas_std_min'
csv_file['simulate.csv'] = header + \
'''
0,withC,n0,female,0.0,0.0,1990,2000,0.2,0.0
1,withC,n0,female,20,30,1990,2000,0.2,0.0
'''
#
def run_test() :
   from math import exp
   #
   # eps99
   eps99 = 99.0 * numpy.finfo(float).eps
   #
   # sim_dir
   sim_dir = 'build/test'
   if not os.path.exists(sim_dir) :
      os.mkdir(sim_dir)
   #
   # write csv files
   for name in csv_file :
      file_name = f'{sim_dir}/{name}'
      file_ptr  = open(file_name, 'w')
      file_ptr.write( csv_file[name] )
      file_ptr.close()
   #
   # simulate command
   command = 'simulate'
   at_cascade.csv.simulate(sim_dir)
   #
   # csv_table
   csv_table = dict()
   for name in csv_file :
      file_name       = f'{sim_dir}/{name}'
      csv_table[name] = at_cascade.csv.read_table( file_name )
   #
   name            = 'data_sim.csv'
   file_name       = f'{sim_dir}/{name}'
   csv_table[name] = at_cascade.csv.read_table( file_name )
   #
   # no_effect_iota, no_effect_pini
   for row in csv_table['no_effect_rate.csv'] :
      if row['rate_name'] == 'iota' :
         no_effect_iota = float( row['rate_truth'] )
      if row['rate_name'] == 'pini' :
         no_effect_pini = float( row['rate_truth'] )
   #
   # data_row
   for data_row in csv_table['data_sim.csv'] :
      #
      # sim_row
      simulate_id    = int( data_row['simulate_id'] )
      sim_row        = csv_table['simulate.csv'][simulate_id]
      #
      # iota, pini
      iota = no_effect_iota
      pini = no_effect_pini
      #
      # age_lower, age_upper
      age_lower = float( sim_row['age_lower'] )
      age_upper = float( sim_row['age_upper'] )
      #
      # average_withC
      if age_lower == age_upper :
         average_withC = 1.0 - (1.0 - pini) * exp(-iota * age_lower)
      else :
         term = exp(-iota * age_lower) - exp(-iota * age_upper)
         term =  term / (iota * (age_upper - age_lower) )
         average_withC = 1 - (1 - pini) * term
      #
      # meas_mean
      meas_mean = float( data_row['meas_mean'] )
      #
      rel_error = meas_mean / average_withC - 1.0
      assert abs( rel_error ) < 1e-3
#
if __name__ == '__main__' :
   run_test()
   print('simulte_xam.py: OK')
# END_PYTHON
