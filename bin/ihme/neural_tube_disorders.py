#! /usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
import os
import sys
import statistics
import math
import copy
import time
import dismod_at
import numpy
import multiprocessing
#
if os.path.isfile( os.getcwd() + '/at_cascade/__init__.py' ) :
   sys.path.insert(0, os.getcwd())
#
import at_cascade.ihme
# ----------------------------------------------------------------------------
# Begin settings that can be changed without understanding this program
# ----------------------------------------------------------------------------
# covariate_csv_file_dict
# The keys in this dictionary are the relative covariate names
# appear in the covariate table.
covariate_csv_file_dict = {
'log_folic_acid' :
   'ihme_db/DisMod_AT/covariates/gbd2019_folic_acid_covariate.csv',
'folic_fortified' :
   'ihme_db/DisMod_AT/covariates/gbd2019_composite_fortification_standard_and_folic_acid_inclusion_covariate.csv',
'haqi' :
   'ihme_db/DisMod_AT/covariates/gbd2019_haqi_covariate.csv',
}
#
# scale_covaraite_dict
# The keys in this dictionary are relative covariate names,
# the corresponding fuctions will be used to transform the covariates.
scale_covariate_dict = { 'log_folic_acid' : numpy.log10 }
#
# input files
# Use None for csmr_inp_file if you do not want to include it in fit
data_dir        = 'ihme_db/DisMod_AT/testing/neural_tube_disorders/data'
data_inp_file   = \
   f'{data_dir}/gbd2019_neural_tube_disorders_crosswalk_10061.csv'
csmr_inp_file   = \
   f'{data_dir}/gbd2019_neural_tube_disorders_csmr.csv'
#
# result_dir
result_dir = 'ihme_db/DisMod_AT/results/neural_tube_disorders'
#
# root_node_database
root_node_database = f'{result_dir}/root_node.db'
#
# no_ode_fit
# This bool controls whether a no_ode fit is used to initialize root level
no_ode_fit = True
#
# root_node_name
# name of the node where the cascade will start
# root_node_name      = '64_High-income'
root_node_name      = '1_Global'
#
# gamma_factor
# gamma for each integrand is this factor times the median
# of the data for the integrand.
gamma_factor        = 1e-1
#
# random_seed
# If this seed is zero, the clock is used for the random seed.
# Otherwise this value is used. In either case the actual seed is reported.
random_seed = 0
#
# perturb_optimization_scale, perturb_optimization_start
# Amount to randomly move, in log space, the optimization scaling and
# starting points.
perturb_optimization_scale = 0.2
perturb_optimization_start = 0.2
#
# quasi_fixed
# if quasi_fixed is True (False),
# use a quasi-Newton (Newton) method for optimizing the fixed effects
quasi_fixed = True
#
# tolerance_fixed
# convergence criteria in the size of the derivative relative to the
# original derivative at the perturbed scalling point. This should work
# with much smaller values when quasi_fixed is False.
tolerance_fixed = 1e-4
#
# max_num_iter_fixed
# This is the maximum number of Ipopt iterations to try before giving
# up on satisfying the convergence tolerance. For example, 100 (40) if
# quasi_fixed is True (False). Note the each quasi-Newton iteration takes less
# work than a Newton iteration.
max_num_iter_fixed = 100
#
# shift_prior_std_factor
# Factor that multiplies standard deviation that is passed down the cascade.
shift_prior_std_factor = 2.0
#
# max_number_cpu
# maximum number of processors, if one, run sequentally, otherwise
# run at most max_number_cpu jobs at at time.
max_number_cpu = max(1, multiprocessing.cpu_count() - 1)
#
# shared_memory_prefix
# No two cascades can run with the same shared memory prefix
user                 = os.environ.get('USER').replace(' ', '_')
shared_memory_prefix = user + "_neural_tube_disorders"
#
# max_fit
# Maximum number of data rows per integrand to include in a fit
max_fit             = 250
#
# max_abs_effect
# Maximum absolute effect for any covriate multiplier.
max_abs_effect      = 2.0
#
# max_plot
# Maximum number of data points to plot per integrand.
max_plot            = 2000
#
# fit_type_list
# A list with one or two elemnts that specifies which type of fits
# to try and in what order. The possible types of fit are 'fixed',
# and 'both'.
fit_type_list = [ 'both', 'fixed' ]
#
# node_split_name_set
# Name of the nodes where we are splitting from Both to Female, Male
node_split_name_set = { root_node_name }
#
# hold_out_integrand
# space separated list of integrands that are held out
# (except during the no_ode fit)
hold_out_integrand = ''
#
# hold_out_nid_set
# set of nid values in data file for studies that are suspect
hold_out_nid_set = set()
#
# rate_case
# https://bradbell.github.io/dismod_at/doc/option_table.htm#rate_case
rate_case = 'iota_zero_rho_zero'
#
# zero_sum_child_rate
# space separate list of rates. The child random effects for each of these
# rates will be constrained to sum to zero. Use empty string for none.
zero_sum_child_rate = ''
#
# ode_step_size
# step size to use (in age and time) when approximationg intergals and
# solutions of the ODE.
ode_step_size = 5.0
#
# compress_interval_list
# A list with two elements containing the age and time interval sizes
# that get compressed. If a data table age or time interval is less than
# or equal its compression interval, the midpoint value of the interval
# is used for its computation. This reduces the amount of computation
# (and memory) for the corresponding data point.
compress_interval_list = [ 10.0, 10.0 ]
#
# age_avg_split_list
# An extra list of ages at which to split the interal and ODE approximation.
# It is usually used to get better resolution around age zero.
age_avg_split_list = [ 0.1, 0.5, 1.0, 3.0 ]
#
# model_rate_age_grid, model_rate_time_grid
# age and time grid points for the smoothing for non-zero rates except omega
model_rate_age_grid = [
   0.02,  0.1, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 40.0, 60.0, 80.0, 100.0
]
model_rate_time_grid = [ 1990, 1995, 2000, 2005, 2010, 2015, 2020 ]
#
# prior_table
# https://bradbell.github.io/dismod_at/doc/create_database.htm#prior_table
prior_table = [
   {   'name'    :    'parent_pini_value',
      'density' :    'gaussian',
      'lower'   :    0.0,
      'upper'   :    1.0,
      'mean'    :    1e-3,
      'std'     :    1.0,
      'eta'     :    1e-7,
   },
   {   'name'    :    'parent_chi_value',
      'density' :    'log_gaussian',
      'lower'   :    1e-7,
      'upper'   :    10.0,
      'mean'    :    1e-1,
      'std'     :    1.0,
      'eta'     :    1e-7,
   },
   {   'name'    :    'parent_chi_delta',
      'density' :    'log_gaussian',
      'mean'    :    0.0,
      'std'     :    0.5,
      'eta'     :    1e-7,
   },
   {   'name'    :    'parent_pini_dtime',
      'density' :    'log_gaussian',
      'mean'    :    0.0,
      'std'     :    0.3,
      'eta'     :    1e-7,
   },
   {   'name'    :    'child_value',
      'density' :    'gaussian',
      'mean'    :    0.0,
      'std'     :    1.0,
   },
   {   'name'    :   'alpha_folic_acid_value',
      'density' :   'gaussian',
      'mean'    :   0.0,
      'std'     :   0.7,

   },
   {   'name'    :   'alpha_folic_fortified_value',
      'density' :   'gaussian',
      'mean'    :   0.0,
      'std'     :   2.0,
      'lower'   : 0.0,
      'upper'   : 0.0,

   },
   {   'name'    :   'alpha_haqi_value',
      'density' :   'gaussian',
      'mean'    :   0.0,
      'std'     :   0.02,

   },
]
#
# smooth_list_dict
# https://bradbell.github.io/dismod_at/doc/create_database.htm#smooth_table
smooth_list_dict = [
   {   'name'         : 'parent_chi',
      'value_prior'  : 'parent_chi_value',
      'dage_prior'   : 'parent_chi_delta',
      'dtime_prior'  : 'parent_chi_delta',
   },
   {   'name'         : 'parent_pini',
      'value_prior'  : 'parent_pini_value',
      'dtime_prior'  : 'parent_pini_dtime',
   },
   {   'name'         : 'child_smooth',
      'value_prior'  : 'child_value',
   },
   {   'name'         : 'alpha_folic_acid_smooth',
      'value_prior'  : 'alpha_folic_acid_value',
   },
   {   'name'         : 'alpha_folic_fortified_smooth',
      'value_prior'  : 'alpha_folic_fortified_value',
   },
   {   'name'         : 'alpha_haqi_smooth',
      'value_prior'  : 'alpha_haqi_value',
   },
]
#
# rate_table
# https://bradbell.github.io/dismod_at/doc/create_database.htm#rate_table
rate_table = [
   {   'name':          'pini',
      'parent_smooth': 'parent_pini',
      'child_smooth':  'child_smooth',
   },
   {   'name':          'chi',
      'parent_smooth': 'parent_chi',
      'child_smooth':  'child_smooth',
   },
]
#
# mulcov_list_dict
# define the covariate multipliers that affect rate values
mulcov_list_dict = [
   {
      # alpha_pini_log_folic_acid
      'covariate': 'log_folic_acid',
      'effected':  'pini',
      'smooth':    'alpha_folic_acid_smooth',
   },{
      # alpha_pini_folic_fortified
      'covariate': 'folic_fortified',
      'effected':  'pini',
      'smooth':    'alpha_folic_fortified_smooth',
   },{
      # alpha_chi_haqi
      'covariate': 'haqi',
      'effected':  'chi',
      'smooth':    'alpha_haqi_smooth',
   }
]
#
# mulcov_freeze_list
# Freeze the covariate multipliers at the Global level after the sex split
mulcov_freeze_list = [
   {   'node'      :  root_node_name ,
      'sex'       : 'Male',
   },
   {   'node'      :  root_node_name ,
      'sex'       : 'Female',
   },
]
#
# fit_goal_set
# Name of the nodes that we are drilling to (must be below root_node).
# You can change this setting and then run
#  bin/ihme/neural_tube_disorders.py continue database
# fit_goal_set = { '1_Global' }
# fit_goal_set = { '64_High-income' }
# fit_goal_set = { '44758_Tower_Hamlets', '527_California' }
# fit_goal_set = {
#     '527_California', '547_Mississippi', '81_Germany', '84_Ireland'
# }
fit_goal_set = {
   '8_Taiwan',
   '514_Shanghai',
   '18_Thailand',
   '16_Philippines',
   '22_Fiji',
   '26_Papua_New_Guinea',
   '41_Uzbekistan',
   '38_Mongolia',
   '505_Inner_Mongolia',
   '61_Republic_of_Moldova',
   '44850_New_Zealand_Maori_population',
   '44851_New_Zealand_non-Maori_population',
   '35469_Kagoshima',
   '68_Republic_of_Korea',
   '7_Democratic_People_s_Republic_of_Korea',
   '349_Greenland',
   '527_California',
   '4644_Baja_California',
   '4645_Baja_California_Sur',
   '547_Mississippi',
   '97_Argentina',
   '99_Uruguay',
   '81_Germany',
   '84_Ireland',
   '433_Northern_Ireland',
   '44758_Tower_Hamlets',
   '123_Peru',
   '121_Bolivia',
   '107_Barbados',
   '116_Saint_Lucia',
   '129_Honduras',
   '4670_Tamaulipas',
   '136_Paraguay',
   '150_Oman',
   '44872_Golestan',
   '161_Bangladesh',
   '171_Democratic_Republic_of_the_Congo',
   '168_Angola',
   '185_Rwanda',
   '179_Ethiopia',
   '194_Lesotho',
   '482_Eastern_Cape',
   '218_Togo',
   '25329_Edo',
}
fit_goal_set = { '1_Global' }
# ----------------------------------------------------------------------------
# End settings that can be changed without understanding this program
# ----------------------------------------------------------------------------
#
# random.seed
if __name__ == '__main__' :
   if random_seed == 0 :
      random_seed = int( time.time() )
# ----------------------------------------------------------------------------
def setup_function() :
   #
   # write_node_table
   at_cascade.ihme.write_node_table(result_dir)
   #
   # write_data_table
   at_cascade.ihme.write_data_table(
      result_dir              = result_dir,
      data_inp_file           = data_inp_file,
      csmr_inp_file           = csmr_inp_file,
      covariate_csv_file_dict = covariate_csv_file_dict,
      scale_covariate_dict    = scale_covariate_dict,
   )
   #
   # write_mtall_tables
   at_cascade.ihme.write_mtall_tables(result_dir)
   #
   # write_root_node_database
   at_cascade.ihme.write_root_node_database(
      result_dir              = result_dir,
      root_node_database      = root_node_database,
      hold_out_integrand      = hold_out_integrand,
      hold_out_nid_set        = hold_out_nid_set,
      covariate_csv_file_dict = covariate_csv_file_dict,
      gamma_factor            = gamma_factor,
      root_node_name          = root_node_name,
      model_rate_age_grid     = model_rate_age_grid,
      model_rate_time_grid    = model_rate_time_grid,
      prior_table             = prior_table,
      smooth_list_dict        = smooth_list_dict,
      rate_table              = rate_table,
      mulcov_list_dict        = mulcov_list_dict,
      rate_case               = rate_case,
      zero_sum_child_rate     = zero_sum_child_rate,
      ode_step_size           = ode_step_size,
      age_avg_split_list      = age_avg_split_list,
      compress_interval_list  = compress_interval_list,
      quasi_fixed             = quasi_fixed,
      tolerance_fixed         = tolerance_fixed,
      max_num_iter_fixed      = max_num_iter_fixed,

   )
   #
   # write_all_option_table
   at_cascade.ihme.write_all_option_table(
      result_dir                   = result_dir,
      root_node_name               = root_node_name ,
      shift_prior_std_factor       = shift_prior_std_factor,
      perturb_optimization_scale   = perturb_optimization_scale,
      perturb_optimization_start   = perturb_optimization_start,
      max_abs_effect               = max_abs_effect,
      max_fit                      = max_fit,
      max_number_cpu               = max_number_cpu,
      shared_memory_prefix         = shared_memory_prefix,
   )
   #
   # write_mulcov_freeze_table
   at_cascade.ihme.write_mulcov_freeze_table(
      result_dir, root_node_database, mulcov_list_dict, mulcov_freeze_list
   )
   #
   # write_node_split_table
   at_cascade.ihme.write_node_split_table(
      result_dir, node_split_name_set, root_node_database
   )
   #
   # write_all_node_database
   at_cascade.ihme.write_all_node_database(result_dir, root_node_database)
# ----------------------------------------------------------------------------
# Without this, the mac will try to execute main on each processor.
if __name__ == '__main__' :
   at_cascade.ihme.main(
      result_dir              = result_dir,
      root_node_name          = root_node_name,
      fit_goal_set            = fit_goal_set,
      setup_function          = setup_function,
      max_plot                = max_plot,
      covariate_csv_file_dict = covariate_csv_file_dict,
      scale_covariate_dict    = scale_covariate_dict,
      root_node_database      = root_node_database,
      no_ode_fit              = no_ode_fit,
      fit_type_list           = fit_type_list,
      random_seed             = random_seed,
   )
   print('neural_tube_disorders.py: OK')
