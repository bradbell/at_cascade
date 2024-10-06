# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ----------------------------------------------------------------------------
r'''
{xrst_begin avgint_parent_grid}

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
is a python string containing the name of the :ref:`all_node_db-name`.
This argument can't be ``None``.

fit_database
************
is a python string containing the name of the :ref:`glossary@fit_database`.
A new avgint table will be placed in this database,
the previous avgint table in this database is lost,
and there are no other changes to the database.
This argument can't be ``None``.

job_table
*********
This is a :ref:`create_job_table@job_table` containing the jobs
necessary to fit the :ref:`glossary@fit_goal_set`.
If this is ``None`` , we are doing predictions for the same node and
split reference id a in *fit_database*
(This is used by :ref:`no_ode_fit-name` .)

fit_job_id
**********
This is the :ref:`create_job_table@job_table@job_id`
for the job fits the fit_database.
This is not used when *job_table* is ``None`` .

parent_node
===========
We use *parent_node* to refer to the parent node in the
dismod_at option table in the fit_database.

avgint Table
************
The new avgint table has all the standard dismod_at columns
plus the extra columns ( beginning with c\_ ) listed below.
This avgint table enables predictions for all the covariate multipliers
and all the rates. Note that the rates (covariate multipliers) depend
(do not depend) on the covariate reference value.

1. If *job_table* is ``None`` , the avgint table enables predictions
   at the same covariate reference values as for the parent_node
   in *fit_database* . Otherwise, see the cases below.

2. This avgint table enables predictions at the covariate reference values
   corresponding to each (node_id, split_reference_id) pair that are
   children of the fit job.

c_age_id
========
This column identifies a row in the age table of the
fit_database that this prediction is for.

c_time_id
=========
This column identifies a row in the time table of the
fit_database that this prediction is for.

c_split_reference_id
====================
This column identifies a row in the split_reference table of the
all_node_database that this prediction is for.
If the split_reference table is empty (non-empty) the value
will be (will not) be ``None``.
It is also ``None`` for the covariate multiplier predictions.

Rectangular Grid
================
For each covariate multiplier that has non-null group smoothing, all of the
age time pairs in the smoothing are represented in the new avgint table.
For each :ref:`child job<glossary@child jobs>` ,
each rate that has non-null parent smoothing,
and each age time pair in the smoothing,
there is a row in the new avgint table.

{xrst_end avgint_parent_grid}
'''
# ----------------------------------------------------------------------------
import copy
import dismod_at
import at_cascade
# ----------------------------------------------------------------------------
# This routine is very similar to get_child_job_table in create_job_table.
# Perhaps there is a good way to combine these two routines.
#
# child_job_list =
def possible_child_job_list(
   # all node database tables
   option_all_table      ,
   node_split_table      ,
   split_reference_table ,
   # fit node database tables
   fit_node_id           ,
   node_table            ,
   covariate_table       ,
) :
   assert type(fit_node_id) == int
   tables = (
      option_all_table      ,
      node_split_table      ,
      split_reference_table ,
      node_table            ,
      covariate_table       ,
   )
   for table in tables :
      assert type(table) == list
      if len(table) > 0 :
         assert type( table[0] == dict )
   #
   # option_all_dict
   option_all_dict = dict()
   for row in option_all_table :
      option_all_dict[ row['option_name'] ] = row['option_value']
   #
   # fit_node_children
   fit_node_children = list()
   for (node_id, row) in enumerate(node_table) :
      if row['parent'] == fit_node_id :
         fit_node_children.append(node_id)
   #
   # refit_split
   if 'refit_split' in option_all_dict :
      refit_split = option_all_dict['refit_split']
      assert refit_split in [ 'true', 'false' ]
      refit_split = refit_split == 'true'
   else :
      refit_split = False
   #
   # root_node_name
   assert 'root_node_name' in option_all_dict
   root_node_name = option_all_dict['root_node_name']
   #
   # root_node_id
   root_node_id = at_cascade.table_name2id(node_table, 'node', root_node_name)
   #
   # root_split_reference_id
   if 'root_split_reference_name' in option_all_dict :
      root_split_reference_name = option_all_dict['root_split_reference_name']
      root_split_reference_id   = at_cascade.table_name2id(
         split_reference_table,
         'split_reference',
         root_split_reference_name
      )
   else :
      root_split_reference_id   = None
      if refit_split :
         msg  = 'option_all_table: refit_split is true and '
         msg += ' root_split_reference_name does not appear'
         assert False, msg
   #
   # fit_split_reference_id
   cov_info = at_cascade.get_cov_info(
      option_all_table, covariate_table, split_reference_table
   )
   if 'split_reference_id' not in cov_info :
      fit_split_reference_id = None
   else :
      fit_split_reference_id = cov_info['split_reference_id']
   #
   # Special case where there is no splitting covariate
   if fit_split_reference_id == None :
      child_job_list = list()
      for shift_node_id in fit_node_children :
         child_job = (shift_node_id, None)
         child_job_list.append(child_job)
      return child_job_list
   #
   # already_split
   already_split = root_split_reference_id != fit_split_reference_id
   #
   # node_split_set
   node_split_set = set()
   for row in node_split_table :
      node_split_set.add( row['node_id'] )
   #
   # shift_reference_set
   if already_split or fit_node_id not in node_split_set :
      shift_reference_set = { fit_split_reference_id }
   else :
      shift_reference_set = set( range( len(split_reference_table) ) )
      shift_reference_set.remove( root_split_reference_id )
   #
   #
   # child_job_list
   child_job_list = list()
   if fit_node_id in node_split_set and not already_split and refit_split :
      for shift_split_reference_id in shift_reference_set :
         child_job = (fit_node_id, shift_split_reference_id)
         child_job_list.append(child_job)
   else :
      for shift_split_reference_id in shift_reference_set :
         for shift_node_id in fit_node_children :
            child_job = (shift_node_id, shift_split_reference_id)
            child_job_list.append(child_job)
   #
   return child_job_list
# ----------------------------------------------------------------------------
# BEGIN syntax
# at_cascade.avgint_parent_grid
def avgint_parent_grid(
   all_node_database = None ,
   fit_database      = None ,
   job_table         = None ,
   fit_job_id        = None ,
# )
) :
   assert type(all_node_database)  == str
   assert type(fit_database) == str
   assert type(job_table) == list or job_table == None
   assert type(fit_job_id) == int or fit_job_id == None
   # END syntax
   #
   # option_all_table
   connection = dismod_at.create_connection(
      all_node_database, new = False, readonly = True
   )
   option_all_table       = dismod_at.get_table_dict(connection, 'option_all')
   node_split_table       = dismod_at.get_table_dict(connection, 'node_split')
   split_reference_table  = dismod_at.get_table_dict(
      connection, 'split_reference'
   )
   connection.close()
   #
   # root_database
   root_database      = None
   for row in option_all_table :
      if row['option_name'] == 'root_database' :
         root_database      = row['option_value']
   assert root_database != None
   #
   # fit_tables
   fit_or_root = at_cascade.fit_or_root_class(
      fit_database, root_database
   )
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
      fit_tables[name] = fit_or_root.get_table(name)
   fit_or_root.close()
   #
   # split_covariate_id, fit_split_reference_id, fit_split_reference
   split_covariate_id     = None
   fit_split_reference_id = None
   fit_split_reference    = None
   cov_info = at_cascade.get_cov_info(
      option_all_table, fit_tables['covariate'], split_reference_table
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
   # child_job_list
   child_job_list = possible_child_job_list(
      option_all_table       = option_all_table,
      node_split_table       = node_split_table ,
      split_reference_table  = split_reference_table ,
      fit_node_id            = parent_node_id,
      node_table             = fit_tables['node'],
      covariate_table        = fit_tables['covariate'],
   )
   #
   # cov_reference_dict
   cov_reference_dict = dict()
   if job_table == None :
      #
      # cov_reference_list
      cov_reference_list = at_cascade.get_cov_reference(
         all_node_database  = all_node_database,
         fit_database       = fit_database,
         shift_node_id      = parent_node_id,
         split_reference_id = fit_split_reference_id,
      )
      # cov_reference[ (parent_node_id, fit_split_reference_id) ]
      key                     = (parent_node_id, fit_split_reference_id)
      cov_reference_dict[key] = cov_reference_list
   else :
      #
      # (shift_node_id, shift_split_reference_id)
      for child_job in child_job_list :
         (shift_node_id, shift_split_reference_id) = child_job
         #
         # cov_reference_list
         cov_reference_list = at_cascade.get_cov_reference(
            all_node_database  = all_node_database,
            fit_database       = fit_database,
            shift_node_id      = shift_node_id,
            split_reference_id = shift_split_reference_id,
         )
         #
         # cov_reference[ (shift_node_id, shift_split_reference_id) ]
         key                     = child_job
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
   # put new avgint table in fit_database
   connection    = dismod_at.create_connection(
      fit_database, new = False, readonly = False
   )
   command       = 'DROP TABLE IF EXISTS ' + tbl_name
   dismod_at.sql_command(connection, command)
   dismod_at.create_table(connection, tbl_name, col_name, col_type, row_list)
   connection.close()
