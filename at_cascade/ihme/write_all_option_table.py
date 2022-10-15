# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
import os
import csv
import at_cascade.ihme
# -----------------------------------------------------------------------------
#
# write_all_option_table
def write_all_option_table(
   result_dir                   = None,
   root_node_name               = None,
   shift_prior_std_factor       = None,
   perturb_optimization_scale   = None,
   perturb_optimization_start   = None,
   max_abs_effect               = None,
   max_fit                      = None,
   max_number_cpu               = None,
   shared_memory_prefix         = None,
) :
   assert type(result_dir)                   == str
   assert type(root_node_name)               == str
   assert type(max_abs_effect)               == float
   assert type(shift_prior_std_factor)       == float
   assert type(perturb_optimization_scale)   == float
   assert type(perturb_optimization_start)   == float
   assert type(max_fit)                      == int
   assert type(max_number_cpu)               == int
   assert type(shared_memory_prefix)         == str
   #
   # all_option_table_file
   all_option_table_file = at_cascade.ihme.csv_file['all_option']
   all_option_table_file = f'{result_dir}/{all_option_table_file}'
   print( f'Creating {all_option_table_file}' )
   #
   # balance_fit
   cov_name = 'sex'
   value_1  = at_cascade.ihme.sex_info_dict['Female']['covariate_value']
   value_2  = at_cascade.ihme.sex_info_dict['Male']['covariate_value']
   if value_2 < value_1 :
      Value_1, value_2 = value_2, value_1
   balance_fit = f'{cov_name} {value_1} {value_2}'
   #
   # all_option
   all_option = {
      'absolute_covariates'          : 'one',
      'split_covariate_name'         : 'sex',
      'root_split_reference_name'    : 'Both',
      'result_dir'                   : result_dir,
      'root_node_name'               : root_node_name,
      'max_abs_effect'               : max_abs_effect,
      'max_fit'                      : max_fit,
      'balance_fit'                  : balance_fit,
      'max_number_cpu'               : max_number_cpu,
      'shared_memory_prefix'         : shared_memory_prefix,
      'shift_prior_std_factor'       : shift_prior_std_factor,
      'perturb_optimization_scale'   : perturb_optimization_scale,
      'perturb_optimization_start'   : perturb_optimization_start,
   }
   #
   # all_option_table
   all_option_table = list()
   for key in all_option :
      row = { 'option_name' : key , 'option_value' : all_option[key] }
      all_option_table.append( row )
   #
   # all_option_table_file
   at_cascade.csv.write_table(all_option_table_file, all_option_table)
