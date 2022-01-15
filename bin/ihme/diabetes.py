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
# The keys in this dictionary are the relative covariate names and must
# appear in the covariate table.
covariate_csv_file_dict = {
'log_ldi' :
    'ihme_db/DisMod_AT/covariates/gbd2019_ldi_log_transformed_covariate.csv',
'obesity' :
    'ihme_db/DisMod_AT/covariates/gbd2019_obesity_prevalence_covariate.csv',
}
#
# input files
data_dir        = 'ihme_db/DisMod_AT/testing/diabetes/data'
data_inp_file   = f'{data_dir}/gbd2019_diabetes_crosswalk_12437.csv'
csmr_inp_file   = f'{data_dir}/gbd2019_diabetes_csmr.csv'
#
# result_dir
result_dir = 'ihme_db/DisMod_AT/results/diabetes'
#
# root_node_database
root_node_database = f'{result_dir}/root_node.db'
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
# set of nid values in data file for studies that are suspect
# 249201 is Schottker B, et.al., ... A1c and fasting ...,  2011; 26(10) 779-87
hold_out_nid_set = { 249201 }
#
# mulcov_freeze_list
# Freeze the covariate multiplier on obesity that affects iota and do the
# freeze at United_States_of_America and Western_Europe.
mulcov_freeze_list = [
    {   'node'      : '1_Global',
        'sex'       : 'Male',
        'rate'      : 'iota',
        'covariate' : 'obesity',
    },
    {   'node'      : '1_Global',
        'sex'       : 'Female',
        'rate'      : 'iota',
        'covariate' : 'obesity',
    },
    {   'node'      : '1_Global',
        'sex'       : 'Male',
        'rate'      : 'chi',
        'covariate' : 'log_ldi',
    },
    {   'node'      : '1_Global',
        'sex'       : 'Female',
        'rate'      : 'chi',
        'covariate' : 'log_ldi',
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
# ----------------------------------------------------------------------------
# End settings that can be changed without understanding this program
# ----------------------------------------------------------------------------
#
# random.seed
if random_seed == 0 :
    random_seed = int( time.time() )
print('random_seed = ', random_seed)
# -----------------------------------------------------------------------------
def get_file_path(csv_file_key) :
    csv_file  = at_cascade.ihme.csv_file
    file_name = csv_file[csv_file_key]
    file_name = f'{result_dir}/{file_name}'
    return file_name
# ----------------------------------------------------------------------------
# write_root_node_database
# data_table_file, node_tble_file, omega_age_table_file, omega_time_table_file
def write_root_node_database() :
    #
    print( 'Creating ' + root_node_database )
    #
    data_table_file       = get_file_path('data')
    node_table_file       = get_file_path('node')
    omega_age_table_file  = get_file_path('omega_age')
    omega_time_table_file = get_file_path('omega_time')
    #
    # table_in
    table_in = dict()
    table_in['data']      = at_cascade.ihme.get_table_csv(data_table_file )
    table_in['node']      = at_cascade.ihme.get_table_csv(node_table_file )
    table_in['omega_age'] = at_cascade.ihme.get_table_csv(omega_age_table_file)
    table_in['omega_time'] = \
        at_cascade.ihme.get_table_csv(omega_time_table_file)
    # sex_name2covariate_value
    sex_name2covariate_value = dict()
    sex_info_dict            = at_cascade.ihme.sex_info_dict
    for sex_name in sex_info_dict :
        sex_name2covariate_value[sex_name] = \
            sex_info_dict[sex_name]['covariate_value']
    #
    # integrand_median
    integrand_list = dict()
    for row in table_in['data'] :
        integrand = row['integrand_name']
        if integrand not in integrand_list :
            integrand_list[integrand] = list()
        integrand_list[integrand].append( float(row['meas_value']) )
    integrand_median = dict()
    for integrand in integrand_list :
        integrand_median[integrand] = \
            statistics.median( integrand_list[integrand] )
    #
    # subgroup_table
    subgroup_table = [ {'subgroup': 'world', 'group':'world'} ]
    #
    # age_min, age_max, time_min, time_max
    age_min =   math.inf
    age_max =   125.0        # maximum age in get_age_group_id_table
    time_min =  math.inf
    time_max =  2021         # year after last year_id in predict_csv
    for row in table_in['data'] :
        age_min  = min(age_min,  float( row['age_lower'] ) )
        time_min = min(time_min, float( row['time_lower'] ) )
        age_max  = max(age_max,  float( row['age_upper'] ) )
        time_max = max(time_max, float( row['time_upper'] ) )
    #
    # age_list, age_grid_id_list
    age_list    = [
        0.0, 5.0, 10.0, 15.0, 20.0,
        30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0
    ]
    age_grid_id_list = list( range(0, len(age_list) ) )
    for row in table_in['omega_age'] :
        age = float( row['age'] )
        age = round(age, at_cascade.ihme.age_grid_n_digits)
        if age not in age_list :
            age_list.append(age)
    if age_min < min( age_list ) :
        age_list.append(age_min)
    if age_max > max( age_list ) :
        age_list.append( age_max)
    #
    # time_list, time_grid_id_list
    time_list   = [ 1960, 1975, 1990, 1995, 2000, 2005, 2010, 2015, 2020 ]
    time_grid_id_list = list( range(0, len(time_list) ) )
    for row in table_in['omega_time'] :
        time = float( row['time'] )
        if time not in time_list :
            time_list.append(time)
    if time_min < min( time_list ) :
        time_list.append(time_min)
    if time_max > max( time_list ) :
        time_list.append( time_max)
    #
    # mulcov_table
    mulcov_table = [
        {   # alpha_iota_obesity
            'covariate': 'obesity',
            'type':      'rate_value',
            'effected':  'iota',
            'group':     'world',
            'smooth':    'alpha_smooth',
        },
        {   # alpha_chi_log_ldi
            'covariate': 'log_ldi',
            'type':      'rate_value',
            'effected':  'chi',
            'group':     'world',
            'smooth':    'alpha_smooth',
        },
        {   # alpha_iota_sex
            'covariate': 'sex',
            'type':      'rate_value',
            'effected':  'iota',
            'group':     'world',
            'smooth':    'alpha_smooth',
        },
        {   # alpha_chi_sex
            'covariate': 'sex',
            'type':      'rate_value',
            'effected':  'chi',
            'group':     'world',
            'smooth':    'alpha_smooth',
        },
    ]
    for integrand in integrand_median :
        mulcov_table.append(
            {   # gamma_integrand
                'covariate':  'one',
                'type':       'meas_noise',
                'effected':   integrand,
                'group':      'world',
                'smooth':     f'gamma_{integrand}',
            }
        )
    #
    # integrand_table
    integrand_table = list()
    for integrand_name in at_cascade.ihme.integrand_name2measure_id :
        row = { 'name' : integrand_name, 'minimum_meas_cv' : '0.1' }
        integrand_table.append( row )
    for j in range( len(mulcov_table) ) :
        integrand_table.append( { 'name' : f'mulcov_{j}' } )
    #
    # node_table, location_id2node_id
    node_table          = list()
    location_id2node_id = dict()
    node_id    = 0
    for row_in in table_in['node'] :
        location_id    = int( row_in['location_id'] )
        node_name      = row_in['node_name']
        if row_in['parent_node_id'] == '' :
            parent_node_name = ''
        else :
            parent_node_id   = int( row_in['parent_node_id'] )
            parent_node_name = table_in['node'][parent_node_id]['node_name']
        row_out = { 'name' : node_name, 'parent' : parent_node_name }
        node_table.append( row_out )
        location_id2node_id[location_id] = node_id
        #
        assert node_id == int( row_in['node_id'] )
        node_id += 1
    #
    # covarite_table
    # Becasue we are using data4cov_reference, the reference for the relative
    # covariates obesity and log_ldi will get replaced.
    # The names in this table must be 'sex', 'one', and the keys in the
    # covariate_csv_file_dict.
    covariate_table = [
        { 'name':'sex',     'reference':0.0, 'max_difference':0.6},
        { 'name':'one',     'reference':0.0 },
        { 'name':'obesity', 'reference':0.0},
        { 'name':'log_ldi', 'reference':0.0},
    ]
    #
    # data_table
    data_table = list()
    for row_in in table_in['data'] :
        location_id = int( row_in['location_id'] )
        is_outlier  = int( row_in['is_outlier'] )
        nid         = int( row_in['nid'] )
        sex_name    = row_in['sex_name']
        #
        hold_out    = is_outlier
        if nid in hold_out_nid_set :
            hold_out = 1
        #
        node_id     = location_id2node_id[location_id]
        node_name   = node_table[node_id]['name']
        sex         = sex_name2covariate_value[ row_in['sex_name'] ]
        #
        if row_in['obesity'] == '' :
            obesity = None
        else :
            obesity = float( row_in['obesity'] )
        if row_in['log_ldi'] == '' :
            log_ldi = None
        else :
            log_ldi = float( row_in['log_ldi'] )
        #
        row_out  = {
            'integrand'       : row_in['integrand_name'],
            'node'            : node_name,
            'subgroup'        : 'world',
            'weight'          : '',
            'age_lower'       : float( row_in['age_lower'] ),
            'age_upper'       : float( row_in['age_upper'] ),
            'time_lower'      : float( row_in['time_lower'] ),
            'time_upper'      : float( row_in['time_upper'] ),
            'sex'             : sex,
            'one'             : 1.0,
            'obesity'         : obesity,
            'log_ldi'         : log_ldi,
            'hold_out'        : hold_out,
            'density'         : 'gaussian',
            'meas_value'      : float( row_in['meas_value'] ),
            'meas_std'        : float( row_in['meas_std'] ),
            'c_seq'           : int( row_in['c_seq'] ),
        }
        data_table.append( row_out )
    #
    # prior_table
    prior_table = [
        {
            'name'    :    'parent_rate_value',
            'density' :    'log_gaussian',
            'lower'   :    1e-7,
            'upper'   :    1.0,
            'mean'    :    1e-2,
            'std'     :    3.0,
            'eta'     :    1e-7,
        },{
            'name'    :    'parent_pini_value',
            'density' :    'gaussian',
            'lower'   :    0.0,
            'upper'   :    1e-4,
            'mean'    :    1e-5,
            'std'     :    1.0,
        },{
            'name'    :    'parent_chi_delta',
            'density' :    'log_gaussian',
            'lower'   :    None,
            'upper'   :    None,
            'mean'    :    0.0,
            'std'     :    1.0,
            'eta'     :    1e-7,
        },{
            'name'    :    'parent_iota_dage',
            'density' :    'log_gaussian',
            'lower'   :    None,
            'upper'   :    None,
            'mean'    :    0.0,
            'std'     :    1.0,
            'eta'     :    1e-7,
        },{
            'name'    :    'parent_iota_dtime',
            'density' :    'log_gaussian',
            'lower'   :    None,
            'upper'   :    None,
            'mean'    :    0.0,
            'std'     :    0.3,
            'eta'     :    1e-7,
        },{
            'name'    :   'child_rate_value',
            'density' :   'gaussian',
            'lower'   :   None,
            'upper'   :   None,
            'mean'    :   0.0,
            'std'     :   .1,
        },{
            'name'    :   'alpha_value',
            'density' :   'gaussian',
            'lower'   :   None,
            'upper'   :   None,
            'mean'    :   0.0,
            'std'     :   1.0,
        }
    ]
    for integrand in integrand_median :
        gamma = gamma_factor * integrand_median[integrand]
        prior_table.append(
            {
                'name'    :   f'gamma_{integrand}',
                'density' :   'uniform',
                'lower'   :   gamma,
                'upper'   :   gamma,
                'mean'    :   gamma,
            }
        )
    # ------------------------------------------------------------------------
    # smooth_table
    smooth_table = list()
    #
    # parrent_chi
    fun = lambda a, t :  \
        ('parent_rate_value', 'parent_chi_delta', 'parent_chi_delta')
    smooth_table.append({
        'name':     'parent_chi',
        'age_id':   age_grid_id_list,
        'time_id':  time_grid_id_list,
        'fun':      fun
    })
    #
    # parrent_iota
    fun = lambda a, t :  \
        ('parent_rate_value', 'parent_iota_dage', 'parent_iota_dtime')
    smooth_table.append({
        'name':     'parent_iota',
        'age_id':   age_grid_id_list,
        'time_id':  time_grid_id_list,
        'fun':      fun
    })
    #
    # parent_pini
    fun = lambda a, t :  \
        ('parent_pini_value', None, None)
    smooth_table.append({
        'name':     'parent_pini',
        'age_id':   [0],
        'time_id':  [0],
        'fun':      fun
    })
    #
    # child_smooth
    fun = lambda a, t : ('child_rate_value', None, None)
    smooth_table.append({
         'name':    'child_smooth',
        'age_id':    [0],
        'time_id':   [0],
        'fun':       fun
    })
    #
    # alpha_smooth
    fun = lambda a, t : ('alpha_value', None, None)
    smooth_table.append({
        'name':    'alpha_smooth',
        'age_id':    [0],
        'time_id':   [0],
        'fun':       fun
    })
    #
    # gamma_integrand
    for integrand in integrand_median :
        # fun = lambda a, t : ('gamma_{integrand}', None, None) )
        fun = eval( f"lambda a, t : ( 'gamma_{integrand}', None, None)" )
        smooth_table.append({
            'name':    f'gamma_{integrand}',
            'age_id':   [0],
            'time_id':  [0],
            'fun':      copy.copy(fun)
        })
    #
    # rate_table
    rate_table = [
        {
            'name':          'pini',
            'parent_smooth': 'parent_pini',
            'child_smooth':  None,
        },{
            'name':           'iota',
            'parent_smooth': 'parent_iota',
            'child_smooth':  'child_smooth',
        },{
            'name':           'chi',
            'parent_smooth': 'parent_chi',
            'child_smooth':  'child_smooth',
        }
    ]
    #
    # option_table
    option_table = [
        { 'name':'parent_node_name',     'value':root_node_name},
        { 'name':'zero_sum_child_rate',  'value':'iota chi'},
        { 'name':'random_seed',          'value':str(random_seed)},
        { 'name':'trace_init_fit_model', 'value':'true'},
        { 'name':'data_extra_columns',   'value':'c_seq'},
        { 'name':'meas_noise_effect',    'value':'add_std_scale_none'},
        { 'name':'age_avg_split',        'value':'0.1 1.0'},
        #
        { 'name':'quasi_fixed',                  'value':'false' },
        { 'name':'tolerance_fixed',              'value':'1e-8'},
        { 'name':'max_num_iter_fixed',           'value':'40'},
        { 'name':'print_level_fixed',            'value':'5'},
        { 'name':'accept_after_max_steps_fixed', 'value':'10'},
    ]
    # Diabetes does not have enough incidence data to estimate
    # both iota and chi without mtexcess. Also see the minimum_cv setting
    # for mtexcess in the integand table.
    # { 'name':'hold_out_integrand',   'value':'mtexcess'},
    #
    # create_database
    file_name      = root_node_database
    nslist_table   = list()
    avgint_table   = list()
    weight_table   = list()
    dismod_at.create_database(
         file_name,
         age_list,
         time_list,
         integrand_table,
         node_table,
         subgroup_table,
         weight_table,
         covariate_table,
         avgint_table,
         data_table,
         prior_table,
         smooth_table,
         nslist_table,
         rate_table,
         mulcov_table,
         option_table
    )
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
    )
    #
    # write_mtall_tables
    at_cascade.ihme.write_mtall_tables(result_dir)
    #
    # write_root_node_database
    # This routine is in this file so not necessary to pass result_dir
    write_root_node_database()
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
        root_node_database      = root_node_database,
    )
print('diabetes.py: OK')
sys.exit(0)
