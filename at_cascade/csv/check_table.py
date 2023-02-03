# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-23 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin csv_check_table}

Check Columns in a CSV File
###########################

Syntax
******
{xrst_literal
   BEGIN_SYNTAX
   END_SYNTAX
}

file_name
*********
is the name of the name of the csv file corresponding to the table.

table
*****
is the table corresponding to the csv file; i.e.,
{xrst_code py}
table  = at_cascade.csv.read(file_name)
{xrst_code}

{xrst_end csv_check_table}
'''
#
# BEGIN_SYNTAX
def check_table(file_name, table) :
   assert type(file_name) == str
   assert type(table) == list
   if len(table) > 0 :
      assert type( table[0] ) == dict
   # END_SYNTAX
   #
   # empty table case
   if len(table) == 0 :
      return
   #
   # table_name
   if '/' in file_name :
      index      = file_name.rfind('/')
      table_name = file_name[index+1 :]
   else :
      table_name = file_name
   index      = table_name.rfind('.csv')
   table_name = table_name[: index]
   #
   # table2keys
   table2keys = {
      #
      # simulate tables
      'option_sim'     : [ 'name', 'value' ],
      'node'           : [ 'node_name', 'parent_name' ],
      'no_effect_rate' : [ 'rate_name', 'age', 'time', 'rate_truth' ],
      'covariate' : [
            'node_name',
            'sex',
            'age',
            'time',
            'omega',
      ],
      'multiplier_sim' : [
         'multiplier_id',
         'rate_name',
         'covariate_or_sex',
         'multiplier_truth',
      ],
      'simulate' : [
         'simulate_id',
         'integrand_name',
         'node_name',
         'sex',
         'age_lower',
         'age_upper',
         'time_lower',
         'time_upper',
         'meas_std_min',
         'meas_std_cv',
      ],
      #
      # fit table that are not simulate tables
      'option_fit'        : [ 'name', 'value' ],
      'fit_goal'          : [ 'node_name' ],
      'predict_integrand' : [ 'integrand_name' ],
      'child_rate'        : [ 'rate_name', 'value_prior' ],
      'prior' : [
         'name',
         'lower',
         'upper',
         'mean',
         'std',
         'density',
      ],
      'parent_rate' : [
         'rate_name',
         'age',
         'time',
         'value_prior',
         'dage_prior',
         'dtime_prior',
         'const_value',
      ],
      'mulcov' : [
         'covariate',
         'type',
         'effected',
         'value_prior',
         'const_value',
      ],
      'data_in' : [
         'data_id',
         'integrand_name',
         'node_name',
         'sex',
         'age_lower',
         'age_upper',
         'time_lower',
         'time_upper',
         'meas_value',
         'meas_std',
         'hold_out',
      ],
   }
   #
   # key
   keys = table2keys[table_name]
   for key in keys :
         if key not in table[0] :
            msg       = f'The column name {key} does not appear in ths file\n'
            msg      += f'{file_name}'
            assert False, msg
   #
   return
