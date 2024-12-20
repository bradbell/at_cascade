# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
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
   const
   dage
   delim
   dtime
   eps
   haqi
   meas
   sincidence
   std
   uniform uniform
}

Freeze Posterior With Continue Cascade
######################################

csv_file
********
This dictionary is used to hold the data corresponding to the
csv files for this example:
{xrst_code py}"""
csv_file = dict()
"""{xrst_code}

node.csv
********
For this example the root node, n0, has two children, n1 and n2. Node n1
has a single child node n3 which in turn has one child node n4
{xrst_code py}"""
csv_file['node.csv'] = \
'''node_name,parent_name
n0,
n1,n0
n2,n0
n3,n1
n4,n3
'''
"""{xrst_code}

option_fit.csv
**************
This example uses the default value for all the options in option_fit.csv
except for:

#. random_seed is chosen using the python time package
#. refit_split is set to false
#. max_number_cpu should be either 1 or None

{xrst_code py}"""
max_number_cpu = None
random_seed    = str( int( time.time() ) )
csv_file['option_fit.csv']  = 'name,value\n'
csv_file['option_fit.csv'] += f'random_seed,{random_seed}\n'
csv_file['option_fit.csv'] += 'refit_split,false\n'
csv_file['option_fit.csv'] += 'tolerance_fixed,1e-8\n'
csv_file['option_fit.csv'] += 'freeze_type,posterior\n'
if max_number_cpu == 1 :
   csv_file['option_fit.csv'] += f'max_number_cpu,1\n'
"""{xrst_code}

option_predict.csv
******************
This example uses the default value for all the options in option_predict.csv.
{xrst_code py}"""
csv_file['option_predict.csv']  = 'name,value\n'
csv_file['option_predict.csv'] += 'db2csv,true\n'
"""{xrst_code}

covariate.csv
*************
This example has one covariate called haqi.
Other cause mortality, omega, is constant and equal to 0.02.
The covariate only depends on the node and has values
1.0, 0.5, 1.5, 1.0, 1.0 for nodes n0, n1, n2, n3, n4 respectively.
{xrst_code py}"""
csv_file['covariate.csv'] = \
'''node_name,sex,age,time,omega,haqi
n0,female,50,2000,0.02,1.0
n1,female,50,2000,0.02,0.5
n2,female,50,2000,0.02,1.5
n3,female,50,2000,0.02,1.0
n4,female,50,2000,0.02,1.0
n0,male,50,2000,0.02,1.0
n1,male,50,2000,0.02,0.5
n2,male,50,2000,0.02,1.5
n3,male,50,2000,0.02,1.0
n4,male,50,2000,0.02,1.0
'''
"""{xrst_code}

fit_goal.csv
************
The goal is to fit the model for nodes n1 through n4
{xrst_code py}"""
csv_file['fit_goal.csv'] = \
'''node_name
n1
n2
n3
n4
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
   gauss_05, a mean 0.5 standard deviation 0.25 gaussian distribution for haqi

{xrst_code py}"""
csv_file['prior.csv'] = \
'''name,lower,upper,mean,std,density
uniform_-1_1,-1.0,1.0,0.5,1.0,uniform
uniform_eps_1,1e-6,1.0,0.5,1.0,uniform
gauss_01,,,0.0,1.0,gaussian
gauss_05,,,0.5,0.25,gaussian
'''
"""{xrst_code}

parent_rate.csv
***************
The only non-zero rates are omega and iota
(omega is known and specified by the covariate.csv file).
The model for iota is constant (with respect to age and time).
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
r"""{xrst_code}

mulcov.csv
**********
There is one covariate multiplier,
it multiplies haqi and affects iota.
The prior distribution for this multiplier is gaussian.
{xrst_code py}"""
csv_file['mulcov.csv'] = \
'''covariate,type,effected,value_prior,const_value
haqi,rate_value,iota,gauss_05,
'''
"""{xrst_code}



data_in.csv
***********
The data_in.csv file has one point for each combination of node and sex.
The integrand is Sincidence (a direct measurement of iota.)
The age interval is [20, 30] and the time interval is [2000, 2010]
for each data point. (These do not really matter because the true iota
for this example is constant.)
The measurement standard deviation is 1e-5 (during the fitting) and
none of the data is held out.
The small standard deviation during the fitting makes checking the
posterior samples easier.
{xrst_code py}"""
header  = 'data_id, integrand_name, node_name, sex, age_lower, age_upper, '
header += 'time_lower, time_upper, meas_value, meas_std, hold_out, '
header += 'density_name, eta, nu'
csv_file['data_in.csv'] = header + \
'''
0, Sincidence, n0, female, 0,  10, 1990, 2000, 0.0000,  1e-4, 0, gaussian, ,
1, Sincidence, n0, male,   0,  10, 1990, 2000, 0.0000,  1e-4, 0, gaussian, ,
2, Sincidence, n1, female, 10, 20, 2000, 2010, 0.0000,  1e-4, 0, gaussian, ,
3, Sincidence, n1, male,   10, 20, 2000, 2010, 0.0000,  1e-4, 0, gaussian, ,
4, Sincidence, n2, female, 20, 30, 2010, 2020, 0.0000,  1e-4, 0, gaussian, ,
5, Sincidence, n2, male,   20, 30, 2010, 2020, 0.0000,  1e-4, 0, gaussian, ,
6, Sincidence, n3, female, 20, 30, 2010, 2020, 0.0000,  1e-4, 0, gaussian, ,
7, Sincidence, n3, male,   20, 30, 2010, 2020, 0.0000,  1e-4, 0, gaussian, ,
8, Sincidence, n4, female, 20, 30, 2010, 2020, 0.0000,  1e-4, 0, gaussian, ,
9, Sincidence, n4, male,   20, 30, 2010, 2020, 0.0000,  1e-4, 0, gaussian, ,
'''
csv_file['data_in.csv'] = csv_file['data_in.csv'].replace(' ', '')
"""{xrst_code}
The measurement value meas_value is 0.0000 above and gets replaced by
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
      # Since refit_split is false, this will only fit include n0.both.
      at_cascade.csv.fit(fit_dir, max_node_depth = 0)
      #
      # all_node_database
      all_node_database = f'{fit_dir}/all_node.db'
      #
      # Run two continues starting at n0.both.
      # If max_number_cpu != 1, run them in parallel.
      # p_fit
      p_fit = dict()
      fit_database      = f'{fit_dir}/n0/dismod.db'
      fit_type          = [ 'both', 'fixed']
      for node_name in [ 'n1' , 'n2' ] :
         fit_goal_set  = { node_name }
         shared_unique = '_' + node_name
         args          = (
            all_node_database,
            fit_database,
            fit_goal_set,
            fit_type,
            shared_unique,
         )
         if max_number_cpu == 1 :
            at_cascade.continue_cascade( *args )
         else :
            p_fit[node_name] = multiprocessing.Process(
               target = at_cascade.continue_cascade , args = args ,
            )
            p_fit[node_name].start()
      # If max_number_cpu != 1, wait for parent continue jobs to finish
      for key in p_fit :
         p_fit[key].join()
      # fit n3
      for node_name in [ 'n3', 'n4' ]:
         parent_node = 'n1' if node_name == 'n3' else 'n1/n3'
         for sex in ['male', 'female']:
            fit_database      = f'{fit_dir}/n0/{sex}/{parent_node}/dismod.db'
            fit_goal_set  = { node_name }
            shared_unique = '_' + node_name
            args          = (
               all_node_database,
               fit_database,
               fit_goal_set,
               fit_type,
               shared_unique,
            )
            if max_number_cpu == 1 :
                  at_cascade.continue_cascade( *args )
            else :
               p_fit[f"{node_name}_{sex}"] = multiprocessing.Process(
                  target = at_cascade.continue_cascade , args = args ,
               )
               p_fit[f"{node_name}_{sex}"].start()
         # If max_number_cpu != 1, wait for continue jobs to finish
         for key in p_fit :
            p_fit[key].join()
      #
      # Run one predict for n0.both using this process
      # If max_number_cpu != 1, this is in parallel with the continues above
      p_predict      = dict()
      sim_dir        = None
      start_job_name = 'n0.both'
      max_job_depth  = 0
      args            = (fit_dir, sim_dir, start_job_name, max_job_depth)
      at_cascade.csv.predict( *args )
      #

      #
      #
      # Run predict starting at
      # n1.female, n1.male, n2.female, n2.male.
      # If max_number_cpu != 1, run them in parallel.
      sim_dir       = None
      max_job_depth = 0
      for node_name in [ 'n1', 'n2', 'n3', 'n4' ] :
         for sex in [ 'female', 'male' ] :
            start_job_name = f'{node_name}.{sex}'
            args           = (fit_dir, sim_dir, start_job_name, max_job_depth)
            if max_number_cpu == 1 :
               at_cascade.csv.predict(*args)
            else :
               key            = (node_name, sex)
               p_predict[key] = multiprocessing.Process(
                  target = at_cascade.csv.predict, args = args,
                )
               p_predict[key].start()
      #
      # If max_number_cpu != 1, wait for predict jobs to finish
      for key in p_predict :
         p_predict[key].join()
   return
#
# main
def main() :
   #
   # fit_dir
   fit_dir = 'build/example/csv'
   at_cascade.empty_directory(fit_dir)
   #
   # write csv files
   for name in csv_file :
      file_name = f'{fit_dir}/{name}'
      file_ptr  = open(file_name, 'w')
      file_ptr.write( csv_file[name] )
      file_ptr.close()
   #
   # node2haqi, haqi_avg
   node2haqi  = { 'n0' : 1.0, 'n1' : 0.5, 'n2' : 1.5, 'n3' : 1.0, 'n4' : 1.0 }
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
   # check priors on haqi match
   variable_tables = dict()
   node_path = ['n0/male/n1','n0/male/n1/n3/n4']
   node_name = ['n1', 'n4']
   for i in range(len(node_name)):
      variable_tables[node_name[i]] = at_cascade.csv.read_table(
         file_name = f'{fit_dir}/{node_path[i]}/variable.csv'
      )
   haqi_priors = dict()
   for node, table in variable_tables.items():
      for row in table:
         if row['covariate'] == "haqi":
            std_v = row['std_v']
            mean_v = row['mean_v']
            haqi_priors[node] = {
               "std_v" : std_v,
               "mean_v" : mean_v
            }
   assert haqi_priors['n1']['std_v'] == haqi_priors['n4']['std_v']
   assert haqi_priors['n1']['mean_v'] == haqi_priors['n4']['mean_v']

   
#
if __name__ == '__main__' :
   main()
   print('posterior_freeze.py: OK')
# END_PROGRAM
