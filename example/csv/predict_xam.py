# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-23 Bradley M. Bell
# ----------------------------------------------------------------------------
import os
import sys
import time
import shutil
import math
import copy
# import at_cascade with a preference current directory version
current_directory = os.getcwd()
if os.path.isfile( current_directory + '/at_cascade/__init__.py' ) :
   sys.path.insert(0, current_directory)
import at_cascade
"""
{xrst_begin csv_predict_xam}
{xrst_spell
   Sincidence
   iter
   std
   pdf
   exp
   sim
}

Example Simulating and Fitting Incidence From Prevalence Data
#############################################################

Covariates
**********
There are no covariates in this example.

#. The covariate.csv file does not have any
   :ref:`csv_simulate@Input Files@covariate.csv@covariate_name` columns
   and is only used to set the value of omega and the covariate
   age time grid.

#. The :ref:`csv_simulate@Input Files@multiplier_sim.csv` file is empty; i.e.,
   it only has a header row.

Age Time Grid
*************
{xrst_code py}"""
age_grid   = [ 0.0,  20.0, 50.0, 80.0, 100.0]
time_grid  = [ 1980, 2000, 2020]
"""{xrst_code}

Node Tree
*********
{xrst_literal
   # BEGIN_NODE_FILE
   # END_NODE_FILE
}

True Rates
**********
The only non-zero rates in this example are omega and iota.
The true values for iota at node n0 and omega for all nodes are:
{xrst_code py}"""
true_iota_n0   = 0.01
true_omega_all = 0.02
"""{xrst_code}

True Prevalence
***************
Note that iota does not depend on age or time,
and prevalence does not depend on omega.
If *true_iota* is the true iota for a node, the corresponding
true prevalence is the following function of age:

   1 - exp( - *iota* * *age* )

random_seed
***********
{xrst_code py}"""
random_seed = str( int( time.time() ) )
"""{xrst_code}

Random Effects
==============
The random effect depends on the node (but not sex).
Given an node and its random_effect,
the true value of iota for that node is
::

   exp( random_effect ) * true_iota_n0

The value std_random_effects_iota
specifies the corresponding standard deviation; see
:ref:`csv_simulate@Input Files@option_sim.csv@std_random_effects_rate`
The simulated random effects are reported in
:ref:`csv_simulate@random_effect.csv`.
Note that there are no random effects for node n0 (the root node).

Simulated Data
**************
There is a simulated data point for each of the following cases:
see the setting of :ref:`csv_simulate@Input Files@simulate.csv`:

#. For integrand_name equal to Sincidence and prevalence.
#. For node_name equal to n0, n1, and n2.
#. For sex equal to female and male.
#. For each age in the age grid and each time in the time grid.

Fit
***

option_fit.csv
==============
#. *refit_split* is set to false because the model does not depend on sex.
#. *quasi_fixed* is false which means a full Newton method is used.
#. *tolerance_fixed* is 1e-8 because the Newton method gets more accuracy.
#. *max_num_iter_fixed* is 50 because the Newton method requires fewer
   iterations (but more work for each iteration).

option_predict.csv
==================
#. *plot* is true, so the plot files (pdf files) are generated for each fit.
#. *db2csv* is true, so the csv files are generated for each fit.
#. *float_precision* is 12 so that tru_predict.csv is very close to the truth.
   Note that we use the same value for *float_precision* , and a small value
   for *absolute_tolerance* in option_sim.csv ,
   so that the simulated values are accurate.

fit_goal.csv
============
This was set to n1 and n2 so that all the nodes, n0, n1, and n2 are fit.
Fitting n0 takes most of the time because it has random effects.
The four cases n1, n2 for female, male fit in parallel and are
very fast because there are not random effects at that level.

parent_rate.csv
===============
The rate iota in constant w.r.t age and time
(because there is only one prior for it in this file).

data_in.csv
===========
The data used during the fit is the same as the simulated data
with the following exceptions:

#. The :ref:`csv_simulate@Output Files@data_sim.csv@meas_mean`
   is used for the measurement value during the fit; i.e.,
   :ref:`csv_fit@Input Files@data_in.csv@meas_value` .
   In addition, :ref:`csv_fit@Input Files@data_in.csv@meas_std`
   is set to a small value.
   Not having any noise in the measurement, and a small standard deviation,
   yields the effect of a much larger data set without long running times.

#. The :ref:`csv_fit@Input Files@data_in.csv@density_name` is set
   to gaussian and eta, nu are set to the empty string; i.e., null.


Prediction Files
****************
The files
:ref:`csv_predict@Output Files@fit_predict.csv` ,
:ref:`csv_predict@Output Files@tru_predict.csv` , and
:ref:`csv_predict@Output Files@sam_predict.csv`
are created by this example.

Source Code
***********
{xrst_literal
   BEGIN_PYTHON
   END_PYTHON
}

{xrst_end csv_predict_xam}
"""
# BEGIN_PYTHON
#
# ----------------------------------------------------------------------------
# simulation files
# ----------------------------------------------------------------------------
#
# sim_file
sim_file = dict()
#
# option_sim.csv
random_seed = str( int( time.time() ) )
sim_file['option_sim.csv'] = \
'''name,value
absolute_tolerance,1e-10
float_precision,12
integrand_step_size,5
random_depend_sex,false
std_random_effects_iota,.2
'''
sim_file['option_sim.csv'] += f'random_seed,{random_seed}\n'
#
# BEGIN_NODE_FILE
sim_file['node.csv'] = \
'''node_name,parent_name
n0,
n1,n0
n2,n0
'''
# END_NODE_FILE
#
# covariate.csv
sim_file['covariate.csv'] = 'node_name,sex,age,time,omega\n'
for node_name in [ 'n0', 'n1', 'n2' ] :
   for sex in [ 'female', 'male' ] :
      for age in age_grid :
         for time in time_grid :
            row = f'{node_name},{sex},{age},{time},{true_omega_all}\n'
            sim_file['covariate.csv'] += row
#
# true_iota_n0, no_effect_rate.csv
sim_file['no_effect_rate.csv'] = 'rate_name,age,time,rate_truth\n'
sim_file['no_effect_rate.csv'] += f'iota,0.0,1980.0,{true_iota_n0}\n'
#
# multiplier_sim.csv
sim_file['multiplier_sim.csv'] = \
'multiplier_id,rate_name,covariate_or_sex,multiplier_truth\n'
#
# simulate.csv
header  = 'simulate_id,integrand_name,node_name,sex,age_lower,age_upper,'
header += 'time_lower,time_upper,meas_std_cv,meas_std_min\n'
sim_file['simulate.csv'] = header
simulate_id     = -1
meas_std_cv     = 0.2
meas_std_min    = 0.0
for integrand_name in [ 'Sincidence', 'prevalence' ] :
   for node_name in [ 'n0', 'n1', 'n2' ] :
      for sex in [ 'female', 'male' ] :
         for age in age_grid :
            for time in time_grid :
               simulate_id += 1
               row  = f'{simulate_id},{integrand_name},{node_name},{sex},'
               row += f'{age},{age},{time},{time},'
               row += f'{meas_std_cv},{meas_std_min}\n'
               sim_file['simulate.csv'] += row
# ----------------------------------------------------------------------------
# fit files
# ----------------------------------------------------------------------------
#
# fit_file
fit_file = dict()
#
# option_fit.csv
fit_file['option_fit.csv']  =  \
'''name,value
refit_split,false
quasi_fixed,false
tolerance_fixed,1e-8
max_num_iter_fixed,50
'''
fit_file['option_fit.csv'] += f'random_seed,{random_seed}\n'
#
# option_predict.csv
fit_file['option_predict.csv']  =  \
'''name,value
plot,true
db2csv,true
float_precision,12
'''
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
uniform_eps_1,uniform,0.02,,,1e-6,1.0
random_prior,gaussian,0.0,0.2,,,,
'''
#
# child_rate.csv
fit_file['child_rate.csv'] = \
'''rate_name,value_prior
iota,random_prior
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
      result_file = f'{sim_dir}/data_join.csv',
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
   data = 'rate_name,age,time,value_prior,dage_prior,dtime_prior,const_value\n'
   data  += f'iota,50.0,2000.0,uniform_eps_1,,,\n'
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
      for key in copy_list :
         row_in[key] = row_join[key]
      row_in['meas_value'] = row_join['meas_mean']
      row_in['meas_std']   = 1e-3
      if row_join['integrand_name'] == 'Sincidence' :
         row_in['hold_out'] = '1'
      else :
         row_join['integrand_name'] == 'prevalence'
         row_in['hold_out'] = '0'
      row_in[ 'density_name' ] = 'gaussian'
      row_in[ 'eta' ]          = ''
      row_in[ 'nu' ]           = ''
      #
      table.append( row_in )
   at_cascade.csv.write_table(
         file_name = f'{fit_dir}/data_in.csv' ,
         table     = table ,
   )
   #
   # fit, predict
   at_cascade.csv.fit(fit_dir)
   at_cascade.csv.predict(fit_dir, sim_dir)
   #
   # random_effect_node
   random_effect_table = at_cascade.csv.read_table(
      file_name = f'{sim_dir}/random_effect.csv'
   )
   random_effect_node = dict()
   for row in random_effect_table :
      random_effect = float( row['random_effect'] )
      node_name     = row['node_name']
      if node_name not in random_effect_node :
         random_effect_node[node_name] = random_effect
      else :
         assert  random_effect_node[node_name] == random_effect
   #
   # predict_table
   predict_table = dict()
   for prefix in [ 'tru', 'fit', 'sam' ] :
      table = at_cascade.csv.read_table(
         file_name = f'{fit_dir}/{prefix}_predict.csv'
      )
      key = lambda row : ( row['node_name'] , row['avgint_id'] )
      predict_table[prefix] = sorted(table, key = key )
   #
   # max_error
   check_epsilon = { 'tru':1e-10, 'fit':1e-4 }
   for prefix in [ 'tru', 'fit' ] :
      #
      # check table
      max_error     = 0.0
      for row in predict_table[prefix] :
         node      = row['node_name']
         integrand = row['integrand_name']
         sex       = row['sex']
         age       = float( row['age'] )
         time      = float( row['time'] )
         estimate  = float( row['avg_integrand'] )
         effect    = random_effect_node[node]
         true_iota = math.exp(effect) * true_iota_n0
         true_p    = 1.0 - math.exp( - true_iota * age )
         if integrand == 'Sincidence' :
            error = (true_iota - estimate) / true_iota
         else :
            error = (true_p - estimate) / 1.0
         max_error = max(max_error, abs(error) )
         if max_error > check_epsilon[prefix] :
            print(prefix, max_error, check_epsilon[prefix])
            assert False
   #
   #
   # n_predict, n_sample
   n_predict = len(predict_table['tru'])
   n_sample  = int( len(predict_table['sam']) / n_predict )
   assert len(predict_table['sam']) == n_predict * n_sample
   #
   # Check correspondence between prediction files
   for i_predict in range(n_predict) :
      fit_row = copy.copy( predict_table['fit'][i_predict] )
      tru_row = copy.copy( predict_table['tru'][i_predict] )
      #
      del fit_row['avg_integrand']
      del tru_row['avg_integrand']
      assert fit_row == tru_row
      #
      for i_sample in range(n_sample) :
         j_sample = i_predict * n_sample + i_sample
         sam_row  = copy.copy( predict_table['sam'][j_sample] )
         del sam_row['avg_integrand']
         del sam_row['sample_index']
         assert sam_row == fit_row
   #
   # Check coverage
   covered = 0
   for i_predict in range(n_predict) :
      fit_value = float( predict_table['fit'][i_predict]['avg_integrand'] )
      tru_value = float( predict_table['tru'][i_predict]['avg_integrand'] )
      #
      std       = 0.0
      for i_sample in range(n_sample) :
         j_sample  = i_predict * n_sample + i_sample
         sam_value = float( predict_table['sam'][j_sample]['avg_integrand'] )
         std      += (sam_value - fit_value)**2
      std = math.sqrt(std / n_sample)
      #
      lower = fit_value - 2.0 * std
      upper = fit_value + 2.0 * std
      if lower <= tru_value and tru_value <= upper :
         covered += 1
   #
   # using meas_mean for meas_value so covered should equal n_predict
   assert covered == n_predict
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
   # sim
   sim(sim_dir)
   #
   # fit
   fit(sim_dir, fit_dir)
   #
   print('csv_predict_xam: OK')
   sys.exit(0)
# END_PYTHON
