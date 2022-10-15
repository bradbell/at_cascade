# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin avgint_parent_grid}
{xrst_spell
   avgint
}

Predicts Rates and Covariate Multipliers on Parent Grid
#######################################################

Syntax
******
{xrst_literal
   # BEGIN syntax
   # END syntax
}

Purpose
*******
Create an avgint table that can be used to predict the rates and covariate
multipliers on the parent grid.
For child nodes, the predictions are for the
:ref:`split_reference_table@split_reference_value` for the parent node.
For the parent node, the predictions are for all the possible
split reference values.

all_node_database
*****************
is a python string containing the name of the :ref:`all_node_db`.
This argument can't be ``None``.

fit_node_database
*****************
is a python string containing the name of the :ref:`glossary@fit_node_database`.
A new avgint table will be placed in this database,
the previous avgint table in this database is lost,
and there are no other changes to the database.
This argument can't be ``None``.

parent_node
===========
We use *parent_node* to refer to the parent node in the
dismod_at option table in the fit_node_database.

avgint Table
************
The new avgint table has all the standard dismod_at columns
plus the columns listed below.
This avgint table enables the following predictions.

1. Predictions can be made for the covariate multipliers
   mean value (with node_id and split_reference_id null).
2. For the fit node and each possible child node,
   predictions can be made for each rate variable at splitting
   covariate value equal to the reference for the fit.
3. For each splitting covariate value,
   predictions can be make for each rate variable at the fit node.


c_age_id
========
This column identifies a row in the age table of the
fit_node_database that this prediction is for.

c_time_id
=========
This column identifies a row in the time table of the
fit_node_database that this prediction is for.

c_split_reference_id
====================
This column identifies a row in the split_reference table of the
all_node_database that this prediction is for.
If the split_reference table is empty (non-empty) the value
wiil be (will not) be ``None``.

Rectangular Grid
================
For each covariate multiplier that has non-null group smoothing, all of the
age time pairs in the smoothing are represented in the new avgint table.
For the parent node, each child of the parent node, and
each rate that has non-null parent smoothing, all of the
age time pairs in the smoothing are represented in the new avgint table.

{xrst_end avgint_parent_grid}
'''
# ----------------------------------------------------------------------------
import copy
import dismod_at
import at_cascade
# ----------------------------------------------------------------------------
def avgint_parent_grid(
# BEGIN syntax
# at_cascade.avgint_parent_grid(
   all_node_database    = None ,
   fit_node_database = None ,
# )
# END syntax
) :
   # all_option_table
   new        = False
   connection = dismod_at.create_connection(all_node_database, new)
   all_option_table        = dismod_at.get_table_dict(connection, 'all_option')
   split_reference_table   = dismod_at.get_table_dict(
      connection, 'split_reference'
   )
   connection.close()
   #
   # fit_tables
   new           = False
   connection    = dismod_at.create_connection(fit_node_database, new)
   fit_tables = dict()
   for name in [
      'age',
      'covariate',
      'integrand',
      'mulcov',
      'node',
      'option',
      'rate',
      'smooth_grid',
      'time',
   ] :
      fit_tables[name] = dismod_at.get_table_dict(connection, name)
   connection.close()
   #
   # split_covariate_id, fit_split_reference_id, fit_split_reference
   split_covariate_id     = None
   fit_split_reference_id = None
   fit_split_reference    = None
   cov_info = at_cascade.get_cov_info(
      all_option_table, fit_tables['covariate'], split_reference_table
   )
   if 'split_covariate_id' in cov_info :
      split_covariate_id     = cov_info['split_covariate_id']
      fit_split_reference_id = cov_info['split_reference_id']
      split_reference_list   = cov_info['split_reference_list']
      fit_split_reference    = split_reference_list[fit_split_reference_id]
   #
   # minimum_age_id
   minimum_age_id = 0
   minimum_age    = fit_tables['age'][minimum_age_id]['age']
   for (age_id, row) in enumerate(fit_tables['age']) :
      if row['age'] < minimum_age :
         minimum_age_id = age_id
         minimum_age    = row['age']
   #
   # n_covariate
   n_covariate = len( fit_tables['covariate'] )
   #
   # parent_node_id
   parent_node_name = None
   for row in fit_tables['option'] :
      assert row['option_name'] != 'parent_node_id'
      if row['option_name'] == 'parent_node_name' :
         parent_node_name = row['option_value']
   assert parent_node_name is not None
   parent_node_id = at_cascade.table_name2id(
      fit_tables['node'], 'node', parent_node_name
   )
   #
   # cov_reference_dict
   cov_reference_dict = dict()
   for (node_id, node_row) in enumerate(fit_tables['node']) :
      if node_id == parent_node_id or node_row['parent'] == parent_node_id :
         #
         # cov_reference_list
         cov_reference_list = at_cascade.get_cov_reference(
            all_node_database  = all_node_database,
            fit_node_database  = fit_node_database,
            shift_node_id      = node_id,
            split_reference_id = fit_split_reference_id,
         )
         #
         # cov_reference[ (node_id, fit_split_reference_id) ]
         key = (node_id, fit_split_reference_id)
         cov_reference_dict[key] = cov_reference_list
         #
         if split_covariate_id is not None and node_id == parent_node_id :
            for split_reference_id in range( len(split_reference_list) ) :
               if split_reference_id != fit_split_reference_id :
                  cov_reference_list = at_cascade.get_cov_reference(
                     all_node_database  = all_node_database,
                     fit_node_database  = fit_node_database,
                     shift_node_id      = node_id,
                     split_reference_id = split_reference_id,
                  )
                  key = (node_id, split_reference_id)
                  cov_reference_dict[key] = cov_reference_list
   #
   # tbl_name
   tbl_name = 'avgint'
   #
   # col_name
   col_name = [
      'integrand_id',
      'node_id',
      'subgroup_id',
      'weight_id',
      'age_lower',
      'age_upper',
      'time_lower',
      'time_upper',
   ]
   #
   # col_tyype
   col_type = [
      'integer',
      'integer',
      'integer',
      'integer',
      'real',
      'real',
      'real',
      'real',
   ]
   #
   # add covariates to col_name and col_type
   for covariate_id in range( n_covariate ) :
      col_name.append( 'x_' + str(covariate_id) )
      col_type.append( 'real' )
   #
   # add the smoothing grid columns to col_name and col_type
   col_name += [ 'c_age_id', 'c_time_id', 'c_split_reference_id' ]
   col_type += 3 * ['integer']
   #
   # name_rate2integrand
   name_rate2integrand = {
      'pini':   'prevalence',
      'iota':   'Sincidence',
      'rho':    'remission',
      'chi':    'mtexcess',
   }
   #
   # initialize row_list
   row_list = list()
   #
   # mulcov_id
   for mulcov_id in range( len( fit_tables['mulcov'] ) ) :
      #
      # mulcov_row
      mulcov_row = fit_tables['mulcov'][mulcov_id]
      #
      # group_smooth_id
      group_smooth_id = mulcov_row['group_smooth_id']
      if not group_smooth_id is None :
         #
         # integrand_id
         integrand_name  = 'mulcov_' + str(mulcov_id)
         integrand_id    = at_cascade.table_name2id(
            fit_tables['integrand'], 'integrand', integrand_name
         )
         #
         # grid_row
         for grid_row in fit_tables['smooth_grid'] :
            if grid_row['smooth_id'] == group_smooth_id :
               #
               # age_id
               age_id    = grid_row['age_id']
               age_lower = fit_tables['age'][age_id]['age']
               age_upper = age_lower
               #
               # time_id
               time_id    = grid_row['time_id']
               time_lower = fit_tables['time'][time_id]['time']
               time_upper = time_lower
               #
               # row
               node_id            = None
               subgroup_id        = 0
               weight_id          = None
               split_reference_id = None
               row = [
                  integrand_id,
                  node_id,
                  subgroup_id,
                  weight_id,
                  age_lower,
                  age_upper,
                  time_lower,
                  time_upper,
               ]
               row += n_covariate * [ None ]
               row += [ age_id, time_id, split_reference_id ]
               #
               # add to row_list
               row_list.append( row )
   #
   # rate_name
   for rate_name in name_rate2integrand :
      #
      # rate_id
      rate_id = at_cascade.table_name2id(
         fit_tables['rate'], 'rate', rate_name
      )
      #
      # parent_smooth_id
      parent_smooth_id = fit_tables['rate'][rate_id]['parent_smooth_id']
      if not parent_smooth_id is None :
         #
         # integrand_id
         integrand_name  = name_rate2integrand[rate_name]
         integrand_id    = at_cascade.table_name2id(
            fit_tables['integrand'], 'integrand', integrand_name
         )
         #
         # grid_row
         for grid_row in fit_tables['smooth_grid'] :
            if grid_row['smooth_id'] == parent_smooth_id :
               #
               # age_id
               age_id    = grid_row['age_id']
               age_lower = fit_tables['age'][age_id]['age']
               age_upper = age_lower
               #
               # prior for pini must use age index zero
               if rate_name == 'pini' :
                  assert age_id == minimum_age_id
               #
               # time_id
               time_id    = grid_row['time_id']
               time_lower = fit_tables['time'][time_id]['time']
               time_upper = time_lower
               #
               # key
               for key in cov_reference_dict :
                  #
                  # node_id
                  node_id = key[0]
                  #
                  # split_reference_id
                  split_reference_id = key[1]
                  #
                  # row
                  subgroup_id = 0
                  weight_id   = None
                  row = [
                     integrand_id,
                     node_id,
                     subgroup_id,
                     weight_id,
                     age_lower,
                     age_upper,
                     time_lower,
                     time_upper,
                  ]
                  row += cov_reference_dict[key]
                  row += [ age_id, time_id, split_reference_id ]
                  #
                  # add to row_list
                  row_list.append( row )
   #
   # put new avgint table in fit_node_database
   new           = False
   connection    = dismod_at.create_connection(fit_node_database, new)
   command       = 'DROP TABLE IF EXISTS ' + tbl_name
   dismod_at.sql_command(connection, command)
   dismod_at.create_table(connection, tbl_name, col_name, col_type, row_list)
   connection.close()
