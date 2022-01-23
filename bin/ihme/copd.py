#! /usr/bin/python3
# -----------------------------------------------------------------------------
# at_cascade: Cascading Dismod_at Analysis From Parent To Child Regions
#           Copyright (C) 2021-22 University of Washington
#              (Bradley M. Bell bradbell@uw.edu)
#
# This program is distributed under the terms of the
#     GNU Affero General Public License version 3.0 or later
# see http://www.gnu.org/licenses/agpl.txt
# ----------------------------------------------------------------------------
import os
import sys
import statistics
import math
import copy
import time
import dismod_at
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
covariate_csv_file_dict = {
'log_sev_copd' :
    'ihme_db/DisMod_AT/covariates/gbd2019_SEV_scalar_COPD_age_std_log_transform_covariate.csv',
'elevation' :
    'ihme_db/DisMod_AT/covariates/gbd2019_elevation_over_1500m_covariate.csv',
'haqi' :
    'ihme_db/DisMod_AT/covariates/gbd2019_haqi_covariate.csv',
}
#
# log_scale_covariate_set
# log_sev_copd is already log scaled in
log_scale_covariate_set = set()
#
# input files
# Use None for csmr_inp_file if you do not want to include it in fit
data_dir        = 'ihme_db/DisMod_AT/testing/copd/data'
data_inp_file   = f'{data_dir}/gbd2019_copd_crosswalk_5528.csv'
csmr_inp_file   = f'{data_dir}/gbd2019_copd_csmr.csv'
#
# result_dir
result_dir = 'ihme_db/DisMod_AT/results/copd'
#
# root_node_database
root_node_database = f'{result_dir}/root_node.db'
#
# no_ode_fit
# This bool controls whether a no_ode fit is used to initial root level
no_ode_fit = True
#
# root_node_name
# name of the node where the cascade will start
# root_node_name      = '64_High-income'
root_node_name      = '1_Global'
#
# gamma_factor
# The gamma for each integrand is this factor times the median
# of the data for the integrand.
gamma_factor        = 1e-2
#
# random_seed
# If this seed is zero, the clock is used for the random seed.
# Otherwise this value is used. In either case the actual seed is reported.
random_seed = 0
#
# perturb_optimization_scaling
# amount to randomly move the optimization scaling point (in log space of
# a multiplier).
perturb_optimization_scaling = 0.2
#
# shift_prior_std_factor
# Factor that multipliers standard deviation that is passed down the cascade.
shift_prior_std_factor = 2.0
#
# max_number_cpu
# maximum number of processors, if one, run sequentally, otherwise
# run at most max_number_cpu jobs at at time.
max_number_cpu = max(1, multiprocessing.cpu_count() - 1)
#
# max_fit
# Maximum number of data rows per integrand to include in a f
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
# node_split_name_set
# Name of the nodes where we are splitting from Both to Female, Male
node_split_name_set = {'1_Global'}
#
# hold_out_nid_set
# set of nid values in data file for studies that are suspect (empty)
hold_out_nid_set = set()
#
# rate_case
# https://bradbell.github.io/dismod_at/doc/option_table.htm#rate_case
rate_case = 'iota_pos_rho_zero'
#
# model_rate_age_grid, model_rate_time_grid
# age and time grid points for the smoothing for non-zero rates except omega
model_rate_age_grid = [
    0.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0
]
model_rate_time_grid = [ 1990, 2000, 2005, 2010, 2015, 2020 ]
#
# prior_table
# https://bradbell.github.io/dismod_at/doc/create_database.htm#prior_table
prior_table = [
    {   'name'    :    'parent_rate_value',
        'density' :    'log_gaussian',
        'lower'   :    1e-7,
        'upper'   :    1.0,
        'mean'    :    1e-2,
        'std'     :    3.0,
        'eta'     :    1e-7,
    },
    {   'name'    :    'parent_chi_delta',
        'density' :    'log_gaussian',
        'mean'    :    0.0,
        'std'     :    1.0,
        'eta'     :    1e-7,
    },
    {   'name'    :    'parent_iota_dage',
        'density' :    'log_gaussian',
        'mean'    :    0.0,
        'std'     :    1.0,
        'eta'     :    1e-7,
    },
    {   'name'    :    'parent_iota_dtime',
        'density' :    'log_gaussian',
        'mean'    :    0.0,
        'std'     :    0.3,
        'eta'     :    1e-7,
    },
    {   'name'    :   'child_rate_value',
        'density' :   'gaussian',
        'mean'    :   0.0,
        'std'     :   0.3,
    },
    {   'name'    :   'alpha_value',
        'density' :   'gaussian',
        'mean'    :   0.0,
        'std'     :   1.0,
    },
]
#
# smooh_list_dict
smooth_list_dict = [
    {   'name'        : 'parent_chi',
        'value_prior' : 'parent_rate_value',
        'dage_prior'  : 'parent_chi_delta',
        'dtime_prior' : 'parent_chi_delta',
    },
    {   'name'        : 'parent_iota',
        'value_prior' : 'parent_rate_value',
        'dage_prior'  : 'parent_iota_dage',
        'dtime_prior' : 'parent_iota_dtime',
    },
    {   'name'        : 'child_smooth',
        'value_prior' : 'child_rate_value',
    },
    {   'name'        : 'alpha_smooth',
        'value_prior' : 'alpha_value',
    },
]
#
# rate_table
# https://bradbell.github.io/dismod_at/doc/create_database.htm#rate_table
rate_table = [
    {   'name':           'iota',
        'parent_smooth': 'parent_iota',
        'child_smooth':  'child_smooth',
    },
    {   'name':          'chi',
        'parent_smooth': 'parent_chi',
        'child_smooth':  'child_smooth',
    },
]
#
# multov_list_dict
# define covriate multipliers that effect rate values
mulcov_list_dict = [
    {   # alpha_iota_log_sev_copd
        'covariate': 'log_sev_copd',
        'effected':  'iota',
        'smooth':    'alpha_smooth',
    },
    {   # alpha_chi_elevation
        'covariate': 'elevation',
        'effected':  'chi',
        'smooth':    'alpha_smooth',
    },
    {   # alpha_chi_haqi
        'covariate': 'haqi',
        'effected':  'chi',
        'smooth':    'alpha_smooth',
    },
    {   # alpha_iota_sex
        'covariate': 'sex',
        'effected':  'iota',
        'smooth':    'alpha_smooth',
    },
    {   # alpha_chi_sex
        'covariate': 'sex',
        'effected':  'chi',
        'smooth':    'alpha_smooth',
    },
]
#
# mulcov_freeze_list
# Freeze the covariate multipliers  at the Global level after the sex split
mulcov_freeze_list = [
    {   'node'      : '1_Global',
        'sex'       : 'Male',
        'rate'      : 'iota',
        'covariate' : 'log_sev_copd',
    },
    {   'node'      : '1_Global',
        'sex'       : 'Female',
        'rate'      : 'iota',
        'covariate' : 'log_sev_copd',
    },
    {   'node'      : '1_Global',
        'sex'       : 'Male',
        'rate'      : 'chi',
        'covariate' : 'elevation',
    },
    {   'node'      : '1_Global',
        'sex'       : 'Female',
        'rate'      : 'chi',
        'covariate' : 'elevation',
    },
    {   'node'      : '1_Global',
        'sex'       : 'Male',
        'rate'      : 'chi',
        'covariate' : 'haqi',
    },
    {   'node'      : '1_Global',
        'sex'       : 'Female',
        'rate'      : 'chi',
        'covariate' : 'haqi',
    },
]
#
# fit_goal_set
# Name of the nodes that we are drilling to (must be below root_node).
# You can change this setting and then run
#   bin/ihme/diabetes.py continue database
# fit_goal_set = { '1_Global' }
# fit_goal_set = { '64_High-income' }
# fit_goal_set = { '81_Germany' }
# fit_goal_set = { '161_Bangladesh' }
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
if random_seed == 0 :
    random_seed = int( time.time() )
print('random_seed = ', random_seed)
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
        log_scale_covariate_set = log_scale_covariate_set,
    )
    #
    # write_mtall_tables
    at_cascade.ihme.write_mtall_tables(result_dir)
    #
    # write_root_node_database
    at_cascade.ihme.write_root_node_database(
        result_dir              = result_dir,
        root_node_database      = root_node_database,
        hold_out_nid_set        = hold_out_nid_set,
        covariate_csv_file_dict = covariate_csv_file_dict,
        gamma_factor            = gamma_factor,
        root_node_name          = root_node_name,
        random_seed             = random_seed,
        model_rate_age_grid     = model_rate_age_grid,
        model_rate_time_grid    = model_rate_time_grid,
        prior_table             = prior_table,
        smooth_list_dict        = smooth_list_dict,
        rate_table              = rate_table,
        mulcov_list_dict        = mulcov_list_dict,
        rate_case               = rate_case,
    )
    #
    # write_all_option_table
    at_cascade.ihme.write_all_option_table(
        result_dir                   = result_dir,
        root_node_name               = root_node_name ,
        shift_prior_std_factor       = shift_prior_std_factor,
        perturb_optimization_scaling = perturb_optimization_scaling,
        max_abs_effect               = max_abs_effect,
        max_fit                      = max_fit,
        max_number_cpu               = max_number_cpu,
    )
    #
    # write_mulcov_freeze_table
    at_cascade.ihme.write_mulcov_freeze_table(
        result_dir, mulcov_freeze_list, root_node_database
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
        log_scale_covariate_set = log_scale_covariate_set,
        root_node_database      = root_node_database,
        no_ode_fit              = no_ode_fit,
    )
print('diabetes.py: OK')
sys.exit(0)
