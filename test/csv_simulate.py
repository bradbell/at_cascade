# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
# Test the following:
# 1. if omega is not in no_effect_rate,
#    values for omega in covariate.csv do not matter
# 2. Prevalence data requires solving the ODE.
#
# For this test, rho and chi are zero, iota and omega are constant, and
# the dismod ODE is S(0) = 1, C(0) = 0,
#  S'(a) = - iota * S(a)
#  C'(a) = + iota * S(a) - omega * C(a)
#
# This corresponding solution is
#  S(a) = exp[ - (ometa + iota) * a ]
#  C(a) =  exp(-omega * a] - exp[ -(omega + iota) * a ]
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
# option.csv
random_seed = str( int( time.time() ) )
csv_file['option.csv'] = \
'''name,value
absolute_tolerance,1e-4
float_precision,4
std_random_effects,.1
integrand_step_size,1.0
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
n0,female,50,2000,.03,1.0
n0,male,50,2000,.03,1.0
n1,female,50,2000,.03,0.5
n1,male,50,2000,.03,0.5
n2,female,50,2000,.03,1.5
n2,male,50,2000,.03,1.5
'''
#
# no_effect_rate.csv
# Add chi, but set it to zero.
csv_file['no_effect_rate.csv'] = \
'''rate_name,age,time,rate_truth
iota,0.0,1980.0,0.01
chi,0.0,1980.0,0.00
'''
#
# multiplier_sim.csv
csv_file['multiplier_sim.csv'] = \
'''multiplier_id,rate_name,covariate_or_sex,multiplier_truth
0,iota,haqi,0.5
'''
#
# simulate.csv
header  = 'simulate_id,integrand_name,node_name,sex,age_lower,age_upper,'
header += 'time_lower,time_upper,percent_cv'
csv_file['simulate.csv'] = header + \
'''
0,withC,n0,female,20,30,1990,2000,0.2
1,withC,n1,male,30,40,2000,2010,0.2
2,withC,n2,female,10,50,2010,2020,0.2
'''
#
def run_test() :
   from math import exp
   #
   # eps99
   eps99 = 99.0 * numpy.finfo(float).eps
   #
   # sim_dir
   sim_dir = 'build/csv'
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
   for name in [ 'random_effect.csv', 'data_sim.csv' ] :
      file_name       = f'{sim_dir}/{name}'
      csv_table[name] = at_cascade.csv.read_table( file_name )
   #
   # random_effect.csv
   for sex in [ 'male', 'female' ] :
      sum_random = 0.0
      sum_abs    = 0.0
      for row in csv_table['random_effect.csv'] :
         if row['node_name'] == 'n0' :
            assert float( row['random_effect'] ) == 0.0
         if row['sex'] == sex :
            if row['rate_name'] == 'iota' :
               sum_abs    += abs( float( row['random_effect'] ) )
               sum_random += float( row['random_effect'] )
      assert abs( sum_random ) <= eps99 * sum_abs
   #
   # random_effect_node_sex
   random_effect_node_sex = dict()
   for node_name in [ 'n0', 'n1', 'n2' ] :
      random_effect_node_sex[node_name] = dict()
   for row in csv_table['random_effect.csv'] :
      node_name     = row['node_name']
      sex           = row['sex']
      rate_name     = row['rate_name']
      random_effect = row['random_effect']
      if rate_name == 'iota' :
         random_effect_node_sex[node_name][sex] = float( random_effect )
   #
   # no_effect_iota
   # one row for iota the other for chi
   assert len( csv_table['no_effect_rate.csv'] ) == 2
   for row in csv_table['no_effect_rate.csv'] :
      if row['rate_name'] == 'iota' :
         no_effect_iota = float( row['rate_truth'] )
   #
   # haqi_node_sex
   haqi_node_sex = dict()
   for node_name in ['n0', 'n1', 'n2'] :
      haqi_node_sex[node_name] = dict()
   for row in csv_table['covariate.csv'] :
      node_name  = row['node_name']
      sex        = row['sex']
      haqi_node_sex[node_name][sex] = row['haqi']
   #
   # omega
   omega = None
   for row in csv_table['covariate.csv'] :
      if omega == None :
         omega = float( row['omega'] )
      else :
         assert omega == float( row['omega'] )
   #
   # haqi_reference
   female = float( haqi_node_sex['n0']['female'] )
   male   = float( haqi_node_sex['n0']['male'] )
   haqi_reference = (female + male) / 2.0
   #
   # mul_haqi_iota
   assert len( csv_table['multiplier_sim.csv'] ) == 1
   for row in csv_table['multiplier_sim.csv'] :
      assert row['rate_name'] == 'iota'
      assert row['covariate_or_sex'] == 'haqi'
      mul_haqi_iota = float( row['multiplier_truth'] )
   #
   # data_row
   for data_row in csv_table['data_sim.csv'] :
      #
      # sim_row
      simulate_id    = int( data_row['simulate_id'] )
      sim_row        = csv_table['simulate.csv'][simulate_id]
      #
      # node_name, sex
      node_name      = sim_row['node_name']
      sex            = sim_row['sex']
      #
      # random_effect
      random_effect = random_effect_node_sex[node_name][sex]
      #
      # covariate effect
      haqi             = float( haqi_node_sex[node_name][sex] )
      covariate_effect = mul_haqi_iota * (haqi - haqi_reference)
      #
      # effect
      effect = random_effect + covariate_effect
      #
      # iota
      iota = exp(effect) * no_effect_iota
      #
      # age_lower, age_upper
      age_lower = float( sim_row['age_lower'] )
      age_upper = float( sim_row['age_upper'] )
      #
      # average_withC
      term_1 = exp(-omega * age_lower)  - exp(-omega * age_upper)
      term_1 = term_1 / ( omega * (age_upper - age_lower) )
      term_2 = exp(-(omega+iota) * age_lower)  \
            - exp(-(omega+iota) * age_upper)
      term_2 = term_2 / ( (omega+iota) * (age_upper - age_lower) )
      average_withC = term_1 - term_2
      #
      # meas_mean
      meas_mean = float( data_row['meas_mean'] )
      #
      assert abs( meas_mean / average_withC - 1.0 ) < 1e-3
#
run_test()
#
print('simulte_xam.py: OK')
sys.exit(0)
# END_PYTHON
