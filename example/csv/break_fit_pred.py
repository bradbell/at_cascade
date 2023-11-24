# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-23 Bradley M. Bell
# ----------------------------------------------------------------------------
import os
import sys
import time
import math
import shutil
import csv
import multiprocessing
# import at_cascade with a preference current directory version
current_directory = os.getcwd()
if os.path.isfile( current_directory + '/at_cascade/__init__.py' ) :
   sys.path.insert(0, current_directory)
import at_cascade
"""
{xrst_begin csv.break_fit_pred}
{xrst_spell
   haqi
   Sincidence
   eps
   std
   uniform uniform
   delim
   dage
   dtime
   const
   meas
}

Breakup Fitting and Prediction and Run in Parallel
##################################################

csv_file
********
This dictionary is used to hold the data corresponding to the
csv files for this example:
{xrst_code py}"""
csv_file = dict()
"""{xrst_code}

node.csv
********
For this example the root node, n0, has two children, n1 and n2.
{xrst_code py}"""
csv_file['node.csv'] = \
'''node_name,parent_name
n0,
n1,n0
n2,n0
'''
"""{xrst_code}

option_fit.csv
**************
This example uses the default value for all the options in option_fit.csv
except for the random seed which is chosen using the python time package,
max_number_cpu should be either 1 or None.
{xrst_code py}"""
max_number_cpu = None
random_seed    = str( int( time.time() ) )
csv_file['option_fit.csv']  = 'name,value\n'
csv_file['option_fit.csv'] += f'random_seed,{random_seed}\n'
if max_number_cpu == 1 :
   csv_file['option_fit.csv'] += f'max_number_cpu,1\n'
"""{xrst_code}

option_predict.csv
******************
This example uses the default value for all the options in option_predict.csv.
{xrst_code py}"""
csv_file['option_predict.csv']  = 'name,value\n'
"""{xrst_code}

covariate.csv
*************
This example has one covariate called haqi.
Other cause mortality, omega, is constant and equal to 0.02.
The covariate only depends on the node and has values
1.0, 0.5, 1.5 for nodes n0, n1, n2 respectively.
{xrst_code py}"""
csv_file['covariate.csv'] = \
'''node_name,sex,age,time,omega,haqi
n0,female,50,2000,0.02,1.0
n1,female,50,2000,0.02,0.5
n2,female,50,2000,0.02,1.5
n0,male,50,2000,0.02,1.0
n1,male,50,2000,0.02,0.5
n2,male,50,2000,0.02,1.5
'''
"""{xrst_code}

fit_goal.csv
************
The goal is to fit the model for nodes n1 and n2.
{xrst_code py}"""
csv_file['fit_goal.csv'] = \
'''node_name
n1
n2
'''
"""{xrst_code}

predict_integrand.csv
*********************
For this example we want to know the values of Sincidence
and prevalence for each of the goal nodes.
(Note that Sincidence is a direct measurement of iota.)
{xrst_code py}"""
csv_file['predict_integrand.csv'] = \
'''integrand_name
Sincidence
prevalence
'''
"""{xrst_code}

prior.csv
*********
We define three priors:

.. csv-table::
   :widths: auto
   :delim: ;

   uniform_1_1; a uniform distribution on [ -1, 1 ]
   uniform_eps_1; a uniform distribution on [ 1e-6, 1 ]
   gauss_01; a mean 0 standard deviation 1 Gaussian distribution

{xrst_code py}"""
csv_file['prior.csv'] = \
'''name,lower,upper,mean,std,density
uniform_-1_1,-1.0,1.0,0.5,1.0,uniform
uniform_eps_1,1e-6,1.0,0.5,1.0,uniform
gauss_01,,,0.0,1.0,gaussian
'''
"""{xrst_code}

parent_rate.csv
***************
The only non-zero rates are omega and iota
(omega is known and specified by the covariate.csv file).
The mode for iota is constant (with respect to age and time).
Its value prior is uniform_eps_1.
It does not have any dage or dtime priors because it is constant
(so there are no age or time difference between grid values).
{xrst_code py}"""
csv_file['parent_rate.csv'] = \
'''rate_name,age,time,value_prior,dage_prior,dtime_prior,const_value
iota,0.0,0.0,uniform_eps_1,,,
'''
"""{xrst_code}

child_rate.csv
**************
The child rates are random effects that represent the difference
between the rate for a node being fit and the rate for one of its child nodes.
These random effects are different for each child node.
The are constant in age and time so age and time do not appear
in child_rate.csv.
In this example, when fitting n0, the child nodes are n1 and n2.
When fitting n1 and n2, there are no child nodes (no random effects).
Our prior for the random effects is gauss_01.
{xrst_code py}"""
csv_file['child_rate.csv'] = \
'''rate_name,value_prior
iota,gauss_01
'''
"""{xrst_code}

mulcov.csv
**********
There is one covariate multiplier,
it multiplies haqi and affects iota.
The prior distribution for this multiplier is uniform\_-1,1.
{xrst_code py}"""
csv_file['mulcov.csv'] = \
'''covariate,type,effected,value_prior,const_value
haqi,rate_value,iota,uniform_-1_1,
'''
"""{xrst_code}



data_in.csv
***********
The data_in.csv file has one point for each combination of node and sex.
The integrand is Sincidence (a direct measurement of iota.)
The age interval is [20, 30] and the time interval is [2000, 2010]
for each data point. (These do not really matter because the true iota
for this example is constant.)
The measurement standard deviation is 0.001 (during the fitting) and
none of the data is held out.
{xrst_code py}"""
header  = 'data_id, integrand_name, node_name, sex, age_lower, age_upper, '
header += 'time_lower, time_upper, meas_value, meas_std, hold_out, '
header += 'density_name, eta, nu'
csv_file['data_in.csv'] = header + \
'''
0, Sincidence, n0, female, 0,  10, 1990, 2000, 0.0000, 0.001, 0, gaussian, ,
1, Sincidence, n0, male,   0,  10, 1990, 2000, 0.0000, 0.001, 0, gaussian, ,
2, Sincidence, n1, female, 10, 20, 2000, 2010, 0.0000, 0.001, 0, gaussian, ,
3, Sincidence, n1, male,   10, 20, 2000, 2010, 0.0000, 0.001, 0, gaussian, ,
4, Sincidence, n2, female, 20, 30, 2010, 2020, 0.0000, 0.001, 0, gaussian, ,
5, Sincidence, n2, male,   20, 30, 2010, 2020, 0.0000, 0.001, 0, gaussian, ,
'''
csv_file['data_in.csv'] = csv_file['data_in.csv'].replace(' ', '')
"""{xrst_code}
The measurement value above is 0.0000 gets replaced by
the following code:
{xrst_literal
   # BEGIN_MEAS_VALUE
   # END_MEAS_VALUE
}

breakup_computation
*******************
Sometimes it is useful to fit some nodes, look at the results,
and if they are good, continue the computation to the entire
fit goal set. This will be done during if breakup_computation is true
(see source code below):
{xrst_code py}"""
breakup_computation = True
"""{xrst_code}

Source Code
***********
{xrst_literal
   BEGIN_PROGRAM
   END_PROGRAM
}

{xrst_end csv.break_fit_pred}
"""
# BEGIN_PROGRAM
#
# computation
def computation(fit_dir) :
   #
   # csv.fit, csv.predict
   if not breakup_computation:
      at_cascade.csv.fit(fit_dir)
      at_cascade.csv.predict(fit_dir)
   else :
      # csv.fit: Just fit the root node
      at_cascade.csv.fit(fit_dir, max_node_depth = 0)
      #
      # all_node_database, fit_goal_set
      all_node_database = f'{fit_dir}/all_node.db'
      fit_goal_set      = { 'n1', 'n2' }
      #
      # run prediict for n0, and fit for female, male in parallel
      #
      # p_fit
      p_fit = dict()
      for sex in [ 'female' , 'male' ] :
         fit_node_database = f'{fit_dir}/n0/{sex}/dismod.db'
         args   = (all_node_database, fit_node_database, fit_goal_set)
         if max_number_cpu == 1 :
            at_cascade.continue_cascade( *args )
         else :
            p_fit[sex] = multiprocessing.Process(
               target = at_cascade.continue_cascade , args = args ,
            )
            p_fit[sex].start()
      #
      # p_predict
      p_predict      = dict()
      sim_dir        = None
      start_job_name = 'n0.both'
      max_job_depth  = 0
      args            = (fit_dir, sim_dir, start_job_name, max_job_depth)
      if max_number_cpu == 1 :
         at_cascade.csv.predict( *args )
      else :
         p_predict['both'] = multiprocessing.Process(
            target = at_cascade.csv.predict , args = args
         )
         p_predict['both'].start()
      #
      # wait for the fit jobs to complete
      for sex in p_fit :
         p_fit[sex].join()
      #
      #
      # p_predict
      sim_dir       = None
      max_job_depth = None
      for sex in [ 'female', 'male' ] :
         start_job_name = f'n0.{sex}'
         args           = (fit_dir, sim_dir, start_job_name, max_job_depth)
         if max_number_cpu == 1 :
            at_cascade.csv.predict(*args)
         else :
            p_predict[sex] = multiprocessing.Process(
               target = at_cascade.csv.predict, args = args                   ,
            )
            p_predict[sex].start()
      #
      # wait for the predict jobs to complete
      for sex in p_predict :
         p_predict[sex].join()
      #
      # predict
      # fit_predict.csv, sam_predict.csv
      for prefix in [ 'fit' , 'sam' ] :
         file_name = f'{fit_dir}/{prefix}_predict.csv'
         file_out  = open(file_name, 'w')
         writer    = None
         for start_job_name in [ 'n0.both', 'n0.female', 'n0.male' ] :
            file_name = f'{fit_dir}/predict/{prefix}_{start_job_name}.csv'
            file_in   = open(file_name, 'r')
            reader    = csv.DictReader(file_in)
            for row in reader :
               if writer == None :
                  writer = csv.DictWriter(file_out, fieldnames = row.keys() )
                  writer.writeheader()
               writer.writerow(row)
         file_out.close()
   return
#
# main
def main() :
   #
   # fit_dir
   fit_dir = 'build/example/csv'
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
   # node2haqi, haqi_avg
   node2haqi  = { 'n0' : 1.0, 'n1' : 0.5, 'n2' : 1.5 }
   file_name  = f'{fit_dir}/covariate.csv'
   table      = at_cascade.csv.read_table( file_name )
   haqi_sum   = 0.0
   for row in table :
      node_name = row['node_name']
      haqi      = float( row['haqi'] )
      haqi_sum += haqi
      assert haqi == node2haqi[node_name]
   haqi_avg = haqi_sum / len(table)
   #
   # data_in.csv
   float_format      = '{0:.5g}'
   true_mulcov_haqi  = 0.5
   no_effect_iota    = 0.1
   file_name         = f'{fit_dir}/data_in.csv'
   table             = at_cascade.csv.read_table( file_name )
   for row in table :
      node_name      = row['node_name']
      integrand_name = row['integrand_name']
      assert integrand_name == 'Sincidence'
      #
      # BEGIN_MEAS_VALUE
      haqi              = node2haqi[node_name]
      effect            = true_mulcov_haqi * (haqi - haqi_avg)
      iota              = math.exp(effect) * no_effect_iota
      row['meas_value'] = float_format.format( iota )
      # END_MEAS_VALUE
   at_cascade.csv.write_table(file_name, table)
   #
   # computation
   computation(fit_dir)
   #
   # prefix
   for prefix in [ 'fit' , 'sam' ] :
      #
      # all_predict_table
      file_name = f'{fit_dir}/{prefix}_predict.csv'
      predict_table = at_cascade.csv.read_table(file_name)
      #
      # node
      for node in [ 'n0', 'n1', 'n2' ] :
         # sex
         for sex in [ 'female', 'both', 'male' ] :
            #
            # sample
            sample_list = list()
            for row in predict_table :
               if row['integrand_name'] == 'Sincidence' and \
                     row['node_name'] == node and \
                        row['sex'] == sex :
                  #
                  sample_list.append(row)
            #
            if node == 'n0' or sex != 'both' :
               assert len(sample_list) > 0
               sum_avgint = 0.0
               for row in sample_list :
                  sum_avgint   += float( row['avg_integrand'] )
               avgint    = sum_avgint / len(sample_list)
               haqi      = float( row['haqi'] )
               effect    = true_mulcov_haqi * (haqi - haqi_avg)
               iota      = math.exp(effect) * no_effect_iota
               rel_error = (avgint - iota) / iota
               assert abs(rel_error) < 0.01
   print('fit_xam.py: OK')
#
main()
# END_PROGRAM
