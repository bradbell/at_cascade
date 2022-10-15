# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin get_cov_reference}}
{xrst_spell
   cov
}

Get Covariate Reference Values
##############################

Syntax
******
{xrst_literal
   # BEGIN syntax
   # END syntax
}

fit_node_database
*****************
This argument can't be ``None`` and
is an :ref:`glossary@input_node_database`.
Only the following tables in this database are used:
option, data, node, and covariate.
None of the tables are modified.

option Table
============
This table must have a row with option_value equal to parent_node_name.
Only this row of the option table is used.
The parent node must be the shift node, or the parent of the shift node.

data Table
==========
Only the following columns of this table are used:
data_id, node_id, x_0, ... x_n,
where n is the number of covariates minus one.


all_node_database
*****************
This argument can't be ``None`` and is the :ref:all_node_db`.
Only the :ref:`all_option_table` and :ref:`split_reference_table` are used.

all_option Table
================
The :ref:`all_option_table@split_covariate_name` and
:ref:`all_option_table@absolute_covariates` rows of this table
(if they exist) are the only rows of this table that are used.

shift_node_id
*************
This is the dismod_at parent node that the covariate reference values
correspond to.

split_reference_id
******************
This is the :ref:`split_reference_table@split_reference_id` that the
covariate reference values correspond to.

cov_reference_list
******************
1. The return value is a ``list`` with length equal to the
   length of the covariate table.
2. The :ref:`all_option_table@absolute_covariates` have the same
   reference value as in the *fit_node_database* covariate table.
3. The splitting covariate has reference value corresponding to
   *split_reference_id* in the split_reference table.
4. The :ref:`glossary@Relative Covariate` reference values are equal to
   the average of the corresponding covariates in the data table.
5. Only rows of the data table that get included when *shift_node_id*
   is the parent node are included in the average.
6. Only rows of the data that are within the max difference for the splitting
   covariate for this *split_reference_id* are included in the average.
7. null values for a covariate are not included in the average.
8. If there are no values to average for a relative covariate, the reference
   in the *fit_node_database* covariate table is used for that covariate.



{xrst_end get_cov_reference}}
'''
import at_cascade
import dismod_at
import math
#
# get_cov_reference(
def get_cov_reference(
# BEGIN syntax
# cov_reference_list = at_cascade.get_cov_reference
   all_node_database  = None,
   fit_node_database  = None,
   shift_node_id     = None,
   split_reference_id = None,
# )
# END syntax
) :
   assert type(all_node_database) == str
   assert type(fit_node_database) == str
   assert type(shift_node_id) == int
   #
   # all_table
   new              = False
   connection       = dismod_at.create_connection(all_node_database, new)
   all_table        = dict()
   for tbl_name in [ 'all_option', 'split_reference' ] :
      all_table[tbl_name] = dismod_at.get_table_dict(connection, tbl_name)
   connection.close()
   #
   # check split_reference_id
   if len( all_table['split_reference'] ) == 0 :
      assert split_reference_id == None
   else :
      assert type(split_reference_id) == int
   #
   # fit_table
   new        = False
   connection = dismod_at.create_connection(fit_node_database, new)
   fit_table = dict()
   for tbl_name in [ 'option', 'data', 'node', 'covariate', ] :
      fit_table[tbl_name] = dismod_at.get_table_dict(connection, tbl_name)
   connection.close()
   #
   # parent_node_id
   parent_node_name = None
   for row in fit_table['option'] :
      assert row['option_name'] != 'parent_node_id'
      if row['option_name'] == 'parent_node_name' :
         parent_node_name = row['option_value']
   assert parent_node_name is not None
   parent_node_id = at_cascade.table_name2id(
      fit_table['node'], 'node', parent_node_name
   )
   #
   # shift_node_ok
   shift_node_ok = parent_node_id == shift_node_id
   if fit_table['node'][shift_node_id]['parent'] == parent_node_id :
      shift_node_ok = True
   if not shift_node_ok :
      shift_node_name = fit_table['node'][shift_node_id]['node_name']
      msg  = f'get_cov_reference: shit node = {shift_node_name}\n'
      msg += f'is not the parent node = {parent_node_name}\n'
      msg += 'nor a child of the parent node'
      assert False, msg

   #
   # cov_info
   cov_info = at_cascade.get_cov_info(
      all_table['all_option'],
      fit_table['covariate'],
      all_table['split_reference']
   )
   #
   # rel_covariate_id_set
   rel_covariate_id_set = cov_info['rel_covariate_id_set']
   #
   # split_covariate_id
   split_covariate_id = None
   if len( all_table['split_reference'] ) > 0 :
      split_covariate_id = cov_info['split_covariate_id']
   #
   # check max_difference
   for covariate_id in rel_covariate_id_set :
      covariate_row  = fit_table['covariate'][covariate_id]
      max_difference = covariate_row['max_difference']
      if not max_difference in [ None, math.inf ] :
         msg  = f'get_cov_reference: covariate_id = {covariate_id}\n'
         msg += 'is a relative covariate and '
         msg += f'max_difference = {max_difference} is not None or infinity'
         assert False, msg
   #
   # n_covariate
   n_covariate = len( fit_table['covariate'] )
   #
   # covariate_label
   covariate_label = list()
   for covariate_id in range( n_covariate ) :
      covariate_label.append( f'x_{covariate_id}' )
   #
   # is_decendant
   is_descendant = set()
   for (node_id, row) in enumerate(fit_table['node']) :
      this_is_descendant = node_id == shift_node_id
      ancestor_node_id   = row['parent']
      while not ancestor_node_id is None :
         if ancestor_node_id == shift_node_id :
            this_is_descendant = True
         ancestor_row     = fit_table['node'][ancestor_node_id]
         ancestor_node_id = ancestor_row['parent']
      if this_is_descendant :
         is_descendant.add( node_id )
   #
   # split_reference_value
   if len( all_table['split_reference'] ) > 0 :
      row  = all_table['split_reference'][split_reference_id]
      split_reference_value = row['split_reference_value']
   #
   # data_subset_list
   data_subset_list = list()
   for (data_id, data_row) in enumerate(fit_table['data']) :
      #
      # node_id
      node_id = data_row['node_id']
      if node_id in is_descendant :
         #
         # in_bnd
         in_bnd = True
         for covariate_id in range( n_covariate ) :
            covariate_row   = fit_table['covariate'][covariate_id]
            reference       = covariate_row['reference']
            if covariate_id == split_covariate_id :
               reference = split_reference_value
            max_difference  = covariate_row['max_difference']
            if max_difference is None :
               max_difference = math.inf
            label           = covariate_label[covariate_id]
            covariate_value = data_row[label]
            #
            skip = covariate_value is None
            skip = skip or max_difference == math.inf
            if not skip :
               abs_diff = abs( covariate_value - reference )
               in_bnd   = in_bnd and abs_diff <= max_difference
         #
         # data_subset_list
         if in_bnd :
            data_subset_list.append( data_id )
   #
   # cov_reference_list
   cov_reference_list = list()
   for covariate_id in range( n_covariate) :
      #
      # reference
      reference = fit_table['covariate'][covariate_id]['reference']
      if covariate_id == split_covariate_id :
         reference = split_reference_value
      #
      if covariate_id in rel_covariate_id_set :
         #
         # covariate_list
         covariate_row  = fit_table['covariate'][covariate_id]
         covariate_list = list()
         for data_id in data_subset_list :
            data_row  = fit_table['data'][data_id]
            cov_value = data_row[ covariate_label[covariate_id] ]
            if not cov_value is None :
               covariate_list.append(cov_value)
         #
         # reference
         if len( covariate_list ) > 0 :
            reference = sum(covariate_list) / len(covariate_list)
      #
      # cov_reference_list
      cov_reference_list.append(reference)
   # -------------------------------------------------------------------------
   return cov_reference_list
