# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
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
"""
{xrst_begin csv_simulate_xam}
{xrst_spell
   dir
   sim
}

Example Using csv.simulate
##########################

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
   *  -  sim_dir
      -  :ref:`csv_simulate@sim_dir`
   *  -  csv_file['option.csv']
      -  :ref:`csv_simulate@Input Files@option.csv`
   *  -  csv_file['node.csv']
      -  :ref:`csv_simulate@Input Files@node.csv`
   *  -  csv_file['covariate.csv']
      -  :ref:`csv_simulate@Input Files@covariate.csv`
   *  -  csv_file['no_effect_rate.csv']
      -  :ref:`csv_simulate@Input Files@no_effect_rate.csv`
   *  -  csv_file['multiplier_sim.csv']
      -  :ref:`csv_simulate@Input Files@multiplier_sim.csv`
   *  -  csv_file['simulate.csv']
      -  :ref:`csv_simulate@Input Files@simulate.csv`
   *  -  csv_file['random_effect.csv']
      -  :ref:`csv_simulate@Output Files@random_effect.csv`
   *  -  csv_file['data_sim.csv']
      -  :ref:`csv_simulate@Output Files@data_sim.csv`


{xrst_literal
   BEGIN_PYTHON
   END_PYTHON
}


{xrst_end csv_simulate_xam}
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
absolute_tolerance,1e-5
float_precision,4
integrand_step_size,5
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
csv_file['no_effect_rate.csv'] = \
'''rate_name,age,time,rate_truth
iota,0.0,1980.0,0.01
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
0,Sincidence,n0,female,0,10,1990,2000,0.2
1,Sincidence,n1,male,10,20,2000,2010,0.2
2,Sincidence,n2,female,20,30,2010,2020,0.2
'''
#
def main() :
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
   # float_precision
   float_precision = None
   for row in csv_table['option.csv'] :
      if row['name'] == 'float_precision' :
         float_precision = int( row['value'] )
   eps10 = 10 * 10.0 ** (- float_precision )
   #
   # random_effect.csv
   for sex in [ 'male', 'female' ] :
      sum_random = 0.0
      sum_abs    = 0.0
      for row in csv_table['random_effect.csv'] :
         if row['node_name'] == 'n0' :
            assert float( row['random_effect'] ) == 0.0
         if row['sex'] == sex :
            assert row['rate_name'] == 'iota'
            sum_abs    += abs( float( row['random_effect'] ) )
            sum_random += float( row['random_effect'] )
      assert abs( sum_random ) <= eps10 * sum_abs
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
      assert rate_name == 'iota'
      random_effect_node_sex[node_name][sex] = float( random_effect )
   #
   # no_effect_iota
   assert len( csv_table['no_effect_rate.csv'] ) == 1
   for row in csv_table['no_effect_rate.csv'] :
      assert row['rate_name'] == 'iota'
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
   # data_sim.csv
   for data_row in csv_table['data_sim.csv'] :
      #
      # node_name, meas_mean
      simulate_id    = int( data_row['simulate_id'] )
      sim_row        = csv_table['simulate.csv'][simulate_id]
      integrand_name = sim_row['integrand_name']
      node_name      = sim_row['node_name']
      sex            = sim_row['sex']
      meas_mean      = float( data_row['meas_mean'] )
      assert integrand_name == 'Sincidence'
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
      # check_mean
      check_mean = math.exp(effect) * no_effect_iota
      assert abs( check_mean - meas_mean ) <= eps10 * meas_mean
   #
   print('simulte_xam.py: OK')
   sys.exit(0)
#
main()
# END_PYTHON
