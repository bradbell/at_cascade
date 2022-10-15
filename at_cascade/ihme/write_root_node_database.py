# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
import copy
import math
import statistics
import dismod_at
import at_cascade.ihme
# -----------------------------------------------------------------------------
def get_file_path(csv_file_key, result_dir) :
   csv_file  = at_cascade.ihme.csv_file
   file_name = csv_file[csv_file_key]
   file_name = f'{result_dir}/{file_name}'
   return file_name
# -----------------------------------------------------------------------------
def write_root_node_database(
   result_dir              = None,
   root_node_database      = None,
   hold_out_integrand      = None,
   hold_out_nid_set        = None,
   covariate_csv_file_dict = None,
   gamma_factor            = None,
   root_node_name          = None,
   model_rate_age_grid     = None,
   model_rate_time_grid    = None,
   prior_table             = None,
   smooth_list_dict        = None,
   rate_table              = None,
   mulcov_list_dict        = None,
   rate_case               = None,
   zero_sum_child_rate     = None,
   ode_step_size           = None,
   age_avg_split_list      = None,
   compress_interval_list  = None,
   quasi_fixed             = None,
   tolerance_fixed         = None,
   max_num_iter_fixed      = None,
) :
   assert type(result_dir) == str
   assert type(root_node_database) == str
   assert type(hold_out_integrand) == str
   assert type(hold_out_nid_set) == set
   assert type(covariate_csv_file_dict) == dict
   assert type(root_node_name) == str
   assert type(model_rate_age_grid) == list
   assert type(model_rate_time_grid) == list
   assert type(prior_table) == list
   assert type(rate_table) == list
   assert type(mulcov_list_dict) == list
   assert type(rate_case) == str
   assert type(zero_sum_child_rate) == str
   assert type(ode_step_size) == float
   assert type(age_avg_split_list) == list
   assert type(compress_interval_list) == list
   assert len(compress_interval_list) == 2
   assert type(quasi_fixed) == bool
   assert type(tolerance_fixed) == float
   assert type(max_num_iter_fixed) == int
   #
   print( 'Creating ' + root_node_database )
   #
   data_table_file       = get_file_path('data', result_dir)
   node_table_file       = get_file_path('node', result_dir)
   omega_age_table_file  = get_file_path('omega_age', result_dir)
   omega_time_table_file = get_file_path('omega_time', result_dir)
   #
   # table_in
   table_in = dict()
   table_in['data']      = at_cascade.csv.read_table(data_table_file )
   table_in['node']      = at_cascade.csv.read_table(node_table_file )
   table_in['omega_age'] = at_cascade.csv.read_table(omega_age_table_file)
   table_in['omega_time'] = \
      at_cascade.csv.read_table(omega_time_table_file)
   # sex_name2covariate_value
   sex_name2covariate_value = dict()
   sex_info_dict            = at_cascade.ihme.sex_info_dict
   for sex_name in sex_info_dict :
      sex_name2covariate_value[sex_name] = \
         sex_info_dict[sex_name]['covariate_value']
   #
   # integrand_median
   # do not include zero values in computation of the median
   integrand_list = dict()
   for row in table_in['data'] :
      integrand = row['integrand_name']
      if integrand not in integrand_list :
         integrand_list[integrand] = list()
      meas_value = float( row['meas_value'] )
      if meas_value != 0.0 :
         integrand_list[integrand].append( meas_value )
   integrand_median = dict()
   for integrand in integrand_list :
      if len( integrand_list[integrand] ) == 0 :
         integrand_median[integrand] = 0.0
      else :
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
   if 0.0 in model_rate_age_grid :
      age_list         = copy.copy( model_rate_age_grid )
      age_grid_id_list = list( range(0, len(model_rate_age_grid) ) )
   else :
      age_list         = [ 0.0 ] + model_rate_age_grid
      age_grid_id_list = list( range(1, len(model_rate_age_grid) ) )
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
   # , time_grid_id_list
   time_list   = copy.copy( model_rate_time_grid )
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
   mulcov_table = copy.copy( mulcov_list_dict )
   for row in mulcov_table :
      row['group'] = 'world'
      row['type']  = 'rate_value'
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
   # splitting covariate (sex) and absolute covariate (one)
   covariate_table = [
      { 'name':'sex',     'reference':0.0, 'max_difference':0.6},
      { 'name':'one',     'reference':0.0 },
   ]
   #
   # covariate_table
   # Becasue we are using data4cov_reference, the reference for the
   # relative covariates will get replaced.
   for covariate_name in covariate_csv_file_dict.keys() :
      covariate_table.append(
         { 'name' : covariate_name,  'reference':0.0}
      )
   #
   # data_table
   data_table = list()
   for row_in in table_in['data'] :
      location_id = int( row_in['location_id'] )
      is_outlier  = int( row_in['is_outlier'] )
      sex_name    = row_in['sex_name']
      #
      if row_in['nid'] == '' :
         nid = None
      else :
         nid = int( row_in['nid'] )
      #
      if row_in['seq'] == '' :
         c_seq = None
      else :
         c_seq = int( row_in['seq'] )
      #
      if row_in['nid'] == '' :
         c_nid = None
      else :
         c_nid = int( row_in['nid'] )
      #
      hold_out    = is_outlier
      if nid in hold_out_nid_set :
         hold_out = 1
      #
      node_id     = location_id2node_id[location_id]
      node_name   = node_table[node_id]['name']
      sex         = sex_name2covariate_value[ row_in['sex_name'] ]
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
         'hold_out'        : hold_out,
         'density'         : 'gaussian',
         'meas_value'      : float( row_in['meas_value'] ),
         'meas_std'        : float( row_in['meas_std'] ),
         'nu'              : 5,
         'c_seq'           : c_seq,
         'c_nid'           : c_nid,
      }
      for cov_name in covariate_csv_file_dict.keys() :
         if row_in[cov_name] == '' :
            cov_value = None
         else :
            cov_value = float( row_in[cov_name] )
         row_out[cov_name] = cov_value
      data_table.append( row_out )
   #
   prior_table_copy = copy.copy(prior_table)
   for integrand in integrand_median :
      gamma = gamma_factor * integrand_median[integrand]
      prior_table_copy.append(
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
   # entries that come from smooth_list_dict
   smooth_table = list()
   for smooth in smooth_list_dict :
      # name
      name        = smooth['name']
      #
      # value_prior
      value_prior = smooth['value_prior']
      value_prior = f'\'{value_prior}\''
      #
      # dage_prior, age_grid
      if 'dage_prior' in smooth :
         dage_prior = smooth['dage_prior']
         dage_prior = f'\'{dage_prior}\''
         age_grid   = age_grid_id_list
      else :
         dage_prior = None
         age_grid   = [ 0 ]
      #
      # dtime_prior, time_grid
      if 'dtime_prior' in smooth :
         dtime_prior = smooth['dtime_prior']
         dtime_prior = f'\'{dtime_prior}\''
         time_grid   = time_grid_id_list
      else :
         dtime_prior = None
         time_grid   = [ 0 ]
      #
      # fun
      fun = eval(
         f'lambda a, t : ( {value_prior}, {dage_prior}, {dtime_prior} )'
      )
      #
      smooth_table.append({
         'name':     name,
         'age_id':   age_grid,
         'time_id':  time_grid,
         'fun':      copy.copy(fun),
      })
   #
   # smooth_table
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
   # age_avg_split
   age_avg_split = None
   for age in age_avg_split_list :
      if age_avg_split == None :
         age_avg_split = str(age)
      else :
         age_avg_split += f' {age}'
   #
   # compress_interval
   compress_interval = None
   for size in compress_interval_list :
      if compress_interval == None :
         compress_interval = str(size)
      else :
         compress_interval += f' {size}'
   #
   # zero_sum_child_rate
   if len( zero_sum_child_rate.split() ) == 0 :
      zero_sum_child_rate = None
   #
   # hold_out_integrand
   if len( hold_out_integrand ) == 0 :
      hold_out_integrand = None
   #
   # option_table
   quasi_fixed        = str(quasi_fixed).lower()
   tolerance_fixed    = str(tolerance_fixed)
   max_num_iter_fixed = str(max_num_iter_fixed)
   option_table = [
      { 'name':'parent_node_name',     'value':root_node_name},
      { 'name':'rate_case',            'value':rate_case},
      { 'name':'zero_sum_child_rate',  'value':zero_sum_child_rate},
      { 'name':'ode_step_size',        'value':str(ode_step_size)},
      { 'name':'age_avg_split',        'value':age_avg_split},
      { 'name':'compress_interval',    'value':compress_interval},
      { 'name':'hold_out_integrand',   'value':hold_out_integrand},
      #
      { 'name':'trace_init_fit_model', 'value':'true'},
      { 'name':'data_extra_columns',   'value':'c_seq c_nid'},
      { 'name':'meas_noise_effect',    'value':'add_std_scale_none'},
      #
      { 'name':'quasi_fixed',                  'value':quasi_fixed},
      { 'name':'tolerance_fixed',              'value':tolerance_fixed},
      { 'name':'max_num_iter_fixed',           'value':max_num_iter_fixed},
      { 'name':'print_level_fixed',            'value':'5'},
      { 'name':'accept_after_max_steps_fixed', 'value':'10'},
   ]
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
         prior_table_copy,
         smooth_table,
         nslist_table,
         rate_table,
         mulcov_table,
         option_table
   )
# ----------------------------------------------------------------------------
