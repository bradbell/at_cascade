# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ----------------------------------------------------------------------------
import os
import sys
import time
import math
import shutil
import numpy
import copy
# import at_cascade with a preference current directory version
current_directory = os.getcwd()
if os.path.isfile( current_directory + '/at_cascade/__init__.py' ) :
   sys.path.insert(0, current_directory)
import at_cascade
# --------------------------------------------------------------------------
# {xrst_begin csv.binomial}
# {xrst_spell
#     const
#     dage
#     def
#     dtime
#     eps
#     iter
#     num
#     numpy
#     sincidence
#     std
# }
# {xrst_comment_ch #}
#
# Example Using Binomial Density
# ##############################
#
# binomial_rate
# *************
# This function scales binomial data so that its mean
# is the success rate in the binomial distribution:
# {xrst_code py}
def binomial_rate(sample_size, mean_rate) :
   count = numpy.random.binomial(n = sample_size, p = mean_rate)
   rate  = count / sample_size
   return rate
# {xrst_code}
#
# random_seed
# ***********
# We us the current time in seconds to seed the random number generator:
# {xrst_code py}
random_seed = str( int( time.time() ) )
# {xrst_code}
#
# age_grid, time_grid
# *******************
# We use one age and time grid for the, covariates, rate model, and the data:
# {xrst_code py}
age_grid   = list( range(0, 101, 5) )
time_grid  = [1980.0, 2020.0]
# {xrst_code}
#
# no_effect_iota
# **************
# The iota value used to simulate the data is constant and equal to
no_effect_iota   = 0.02
#
#
# fit_file
# ********
# This dictionary will contain all the files that are written to the
# :ref:`csv.fit@fit_dir` :
fit_file = dict()
#
# option_fit.csv
# ==============
# {xrst_code py}
fit_file['option_fit.csv']  =  \
'''name,value
hold_out_integrand,Sincidence
refit_split,false
ode_step_size,5.0
quasi_fixed,false
max_num_iter_fixed,50
tolerance_fixed,1e-8
'''
fit_file['option_fit.csv'] += f'random_seed,{random_seed}\n'
# {xrst_code}
#
# option_predict.csv
# ==================
# {xrst_code py}
fit_file['option_predict.csv']  =  \
'''name,value
plot,true
db2csv,true
'''
# {xrst_code}
#
# node.csv
# ========
# There is just one node, n0, in this example.
# {xrst_code py}
fit_file['node.csv'] = \
'''node_name,parent_name
n0,
'''
# {xrst_code}
#
# fit_goal.csv
# ============
# {xrst_code py}
fit_file['fit_goal.csv'] = \
'''node_name
n0
'''
# {xrst_code}
#
# covariate.csv
# =============
# There are no covariates and omega is constant in this example.
# {xrst_code py}
omega_truth = 0.01
fit_file['covariate.csv'] = 'node_name,sex,age,time,omega\n'
for sex in [ 'female', 'male' ] :
   for age in age_grid :
      for time in time_grid :
         row   = f'n0,{sex},{age},{time},{omega_truth}\n'
         fit_file['covariate.csv'] += row
# {xrst_code}
#
# prior.csv
# =========
# #. uniform_eps_0.1 is uniform on the interval [eps,.1] where eps = 1e-6
# #. delta_prior is log Gaussian with mean 0, std 0.03, and eta=1e-5
# {xrst_code py}
fit_file['prior.csv'] = \
'''name,density,mean,std,eta,lower,upper
uniform_eps_0.1,uniform,0.02,,,1e-6,0.1
delta_prior,log_gaussian,0.0,0.03,1e-5,,
'''
# {xrst_code}
#
# parent_rate.csv
# ===============
# The parent rate model using the age-time grid and the uniform_eps_0.1
# prior
# {xrst_code py}
data = 'rate_name,age,time,value_prior,dage_prior,dtime_prior,const_value\n'
for age in age_grid :
   for time in time_grid :
      data += f'iota,{age},{time},uniform_eps_0.1,delta_prior,delta_prior,\n'
fit_file['parent_rate.csv'] = data
# {xrst_code}
#
# predict_integrand.csv
# =====================
# This example will predict for incidence and prevalence using the
# optimal estimates of iota
# {xrst_code py}
fit_file['predict_integrand.csv'] = \
'''integrand_name
Sincidence
prevalence
'''
# {xrst_code}
#
# child_rate.csv
# ==============
# There are no child rates
# {xrst_code py}
fit_file['child_rate.csv'] = \
'''rate_name,value_prior
'''
# {xrst_code}
#
# mulcov.csv
# ==========
# There are no covariate multipliers
# {xrst_code py}
fit_file['mulcov.csv'] = \
'covariate,type,effected,value_prior,const_value\n'
# {xrst_code}
#
# Rest of Source Code
# *******************
# {xrst_literal
#  # BEGIN_REST_OF_SOURCE
#  # END_REST_OF_SOURCE
# }
#
# {xrst_end csv.binomial}
# -----------------------------------------------------------------------------
# BEGIN_REST_OF_SOURCE
# fit
def fit(fit_dir) :
   #
   # csv files in fit_file
   for name in fit_file :
      file_name = f'{fit_dir}/{name}'
      file_ptr  = open(file_name, 'w')
      file_ptr.write( fit_file[name] )
      file_ptr.close()
   #
   # row
   row = dict()
   row['node_name']       = 'n0'
   row['integrand_name']  = 'prevalence'
   row['hold_out']        = 0
   row['density_name']    = 'binomial'
   #
   # table
   table   = list()
   data_id = -1
   for sex in [ 'female', 'male' ] :
      for age in age_grid[1:] :
         for time in time_grid :
            data_id += 1
            #
            # row
            row['sex']          = sex
            row['age_lower']    = age
            row['age_upper']    = age
            row['time_lower']   = time
            row['time_upper']   = time
            row['data_id']      = data_id
            relative_age        = age / age_grid[2]
            prevalence          = 1.0 - math.exp( -no_effect_iota * age )
            sample_size         =  relative_age**2 / prevalence
            meas_value          = binomial_rate(sample_size, prevalence)
            row['meas_value']   = meas_value
            row['sample_size']  = sample_size
            row['eta']          = None
            row['nu']           = None
            row['meas_std']     = None
            #
            table.append( copy.copy(row) )
   #
   # data_in.csv
   at_cascade.csv.write_table(
         file_name = f'{fit_dir}/data_in.csv' ,
         table     = table ,
   )
   #
   # fit, predict
   at_cascade.csv.fit(fit_dir)
   at_cascade.csv.predict(fit_dir)
   #
   # fit_predict_dict
   fit_predict_table = at_cascade.csv.read_table(
      file_name = f'{fit_dir}/fit_predict.csv'
   )
   #
   # row
   max_error  = 0.0
   predict_node_set = set()
   for row in fit_predict_table :
      node_name = row['node_name']
      assert node_name == 'n0'
      sex            = row['sex']
      age            = float( row['age'] )
      integrand_name = row['integrand_name']
      if integrand_name == 'Sincidence' :
         node_name     = row['node_name']
         time          = float( row['time'] )
         avg_integrand = float( row['avg_integrand'] )
         iota          = no_effect_iota
         rel_error     = (1.0 - avg_integrand / iota )
         max_error     = max(max_error, abs(rel_error) )
   if max_error > 1e-1 :
      msg  = f'max_error = {max_error}\n'
      msg += 'binomial.py: Relative error is to large (see above)'
      assert False, msg
# -----------------------------------------------------------------------------
# Without this, the mac will try to execute main on each processor.
if __name__ == '__main__' :
   #
   # fit_dir
   fit_dir = 'build/example/csv/fit'
   at_cascade.empty_directory(fit_dir)
   #
   # fit
   fit(fit_dir)
   #
   print('binomial.py: OK')
   sys.exit(0)
# END_REST_OF_SOURCE
