# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin get_var_id}
{xrst_spell
   dage
   dtime
   meas
   mulstd
   subgroup
   var
}

Map Var Table Values to its Primary Key
#######################################

Syntax
******
{xrst_literal
   # BEGIN syntax
   # END syntax
}

var_table
*********
This is a ``list`` of ``dict`` representation of the
a dismod_at var table.

var_type
********
This is a ``str`` that specifies the type of variable
for the corresponding row of the var table.
It must have one of the values in the table below
(and cannot be ``None``).


Other Arguments
***************
All of the arguments, other than *var_type*, are ``int`` values.
Depending on the value of *var_type* only certain of the
other arguments matter:

.. csv-table:: **Other Arguments That Matter by Variable Type**
   :header: var_type,     Other Arguments
   :widths: 30, 70

   mulstd_value,          *smooth_id*
   mulstd_dage,           *smooth_id*
   mulstd_dtime,          *smooth_id*
   rate,                  "age_id, time_id, node_id, rate_id"
   mulcov_rate_value,     "age_id, time_id, mulcov_id, group_id, subgroup_id"
   mulcov_meas_value,     "age_id, time_id, mulcov_id, group_id, subgroup_id"
   mulcov_meas_noise,     "age_id, time_id, mulcov_id, group_id"


{xrst_end get_var_id}
'''
def get_var_id(
# BEGIN syntax
# var_id = at_cascade.get_var_id(
   var_table    = None,
   var_type     = None,
   smooth_id    = None,
   age_id       = None,
   time_id      = None,
   node_id      = None,
   rate_id      = None,
   mulcov_id    = None,
   group_id     = None,
   subgroup_id  = None,
# )
# END syntax
) :
   # var_id
   var_id       = None
   #
   # double_match
   double_match = False
   #
   # mulstd_value, mulstd_dage, mulstd_dtime
   if var_type in [ 'mulstd_value', 'mulstd_dage', 'mulstd_dtime' ] :
      for (row_id, row) in enumerate(var_table) :
         match = True
         match = match and row['var_type']  == var_type
         match = match and row['smooth_id'] == smooth_id
         if match :
            # double_match
            if not var_id is None :
               double_match = True
            # var_id
            var_id = row_id
   # rate
   elif var_type == 'rate' :
      for (row_id, row) in enumerate(var_table) :
         match = True
         match = match and row['var_type']  == var_type
         match = match and row['age_id']    == age_id
         match = match and row['time_id']   == time_id
         match = match and row['node_id']   == node_id
         match = match and row['rate_id']   == rate_id
         if match :
            # double_match
            if not var_id is None :
               double_match = True
            # var_id
            var_id = row_id
   # mulcov_rate_value, mulcov_meas_value
   elif var_type in [ 'mulcov_rate_value', 'mulcov_meas_value' ] :
      for (row_id, row) in enumerate(var_table) :
         match = True
         match = match and row['var_type']    == var_type
         match = match and row['age_id']      == age_id
         match = match and row['time_id']     == time_id
         match = match and row['mulcov_id']   == mulcov_id
         match = match and row['group_id']    == group_id
         match = match and row['subgroup_id'] == subgroup_id
         if match :
            # double_match
            if not var_id is None :
               double_match = True
            # var_id
            var_id = row_id
   # mulcov_meas_noise
   else :
      assert var_type == 'mulcov_meas_noise'
      for (row_id, row) in enumerate(var_table) :
         match = True
         match = match and row['var_type']    == var_type
         match = match and row['age_id']      == age_id
         match = match and row['time_id']     == time_id
         match = match and row['mulcov_id']   == mulcov_id
         match = match and row['group_id']    == group_id
         if match :
            # double_match
            if not var_id is None :
               double_match = True
            # var_id
            var_id = row_id
   # double_match
   if double_match :
      for row in var_table :
         print(row)
      msg  = 'get_var_id: Something is wrong with this var_table'
      assert False, msg
   #
   return var_id
