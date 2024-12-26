# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin com_cov_reference}

Compute Covariate Reference Values
##################################
Compute covariate references by averaging values in the data table
for a specific node and split reference value.

Prototype
*********
{xrst_literal ,
   # BEGIN_DEF, # END_DEF
   # BEGIN_RETURN, # END_RETURN
}

option_all_table
****************
The :ref:`option_all_table@split_covariate_name` and
:ref:`option_all_table@absolute_covariates` rows of this table
(if they exist) are the only rows of this table that are used.

split_reference_table
*********************
is the :ref:`split_reference_table-name` as a ``list``
of ``dict`` .

node_table
**********
This is a list of dict representing the node table in the
:ref:`glossary@root_database` .

covariate_table
***************
This is the covariate table for any fit or the one in the
root node database.

shift_node_id
*************
This is the dismod_at node that the computed
covariate reference values correspond to.

split_reference_id
******************
This is the :ref:`split_reference_table@split_reference_id` that the
computed covariate reference values correspond to.

cov_reference_list
******************
1. The return value is a ``list`` with length equal to the
   length of the covariate table (in the root node database).
2. The :ref:`option_all_table@absolute_covariates` have the same
   reference value as in the :ref:`glossary@root_database` .
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
   in the root_database covariate table is used for that covariate.

{xrst_end com_cov_reference}
'''
import at_cascade
import dismod_at
import math
#
# BEGIN_DEF
# at_cascade.com_cov_reference
def com_cov_reference(
   option_all_table      ,
   split_reference_table ,
   node_table            ,
   covariate_table       ,
   shift_node_id         ,
   split_reference_id    = None,
   data_table            = None,
# )
) :
   assert type(option_all_table) == list
   assert type(split_reference_table) == list
   assert type(node_table) == list
   assert type(covariate_table) == list
   assert type(shift_node_id) == int
   assert type(split_reference_id) == int or split_reference_id == None
   assert type(data_table) == list or data_table == None
   # END_DEF
   #
   # root_database
   root_database      = None
   for row in option_all_table :
      if row['option_name'] == 'root_database' :
         root_database      = row['option_value']
   assert root_database != None
   #
   # check split_reference_id
   if len( split_reference_table ) == 0 :
      assert split_reference_id == None
   else :
      assert type(split_reference_id) == int
   #
   # data_table
   if data_table == None :
      connection = dismod_at.create_connection(
         root_database, new = False, readonly = True
      );
      data_table = dismod_at.get_table_dict(connection, 'data')
      connection.close()
   #
   # cov_info
   cov_info = at_cascade.get_cov_info(
      option_all_table,
      covariate_table,
      split_reference_table
   )
   #
   # rel_covariate_id_set
   rel_covariate_id_set = cov_info['rel_covariate_id_set']
   #
   # split_covariate_id
   split_covariate_id = None
   if len( split_reference_table ) > 0 :
      split_covariate_id = cov_info['split_covariate_id']
   #
   # check max_difference
   for covariate_id in rel_covariate_id_set :
      covariate_row  = covariate_table[covariate_id]
      max_difference = covariate_row['max_difference']
      if not max_difference in [ None, math.inf ] :
         msg  = f'com_cov_reference: covariate_id = {covariate_id}\n'
         msg += 'is a relative covariate and '
         msg += f'max_difference = {max_difference} is not None or infinity'
         assert False, msg
   #
   # n_covariate
   n_covariate = len( covariate_table )
   #
   # covariate_label
   covariate_label = list()
   for covariate_id in range( n_covariate ) :
      covariate_label.append( f'x_{covariate_id}' )
   #
   # is_decendant
   is_descendant = set()
   for (node_id, row) in enumerate(node_table) :
      this_is_descendant = node_id == shift_node_id
      ancestor_node_id   = row['parent']
      while not ancestor_node_id is None :
         if ancestor_node_id == shift_node_id :
            this_is_descendant = True
         ancestor_row     = node_table[ancestor_node_id]
         ancestor_node_id = ancestor_row['parent']
      if this_is_descendant :
         is_descendant.add( node_id )
   #
   # split_reference_value
   if len( split_reference_table ) > 0 :
      row  = split_reference_table[split_reference_id]
      split_reference_value = row['split_reference_value']
   #
   # data_subset_list
   data_subset_list = list()
   for (data_id, data_row) in enumerate(data_table) :
      #
      # node_id
      node_id = data_row['node_id']
      if node_id in is_descendant :
         #
         # in_bnd
         in_bnd = True
         for covariate_id in range( n_covariate ) :
            covariate_row   = covariate_table[covariate_id]
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
      reference = covariate_table[covariate_id]['reference']
      if covariate_id == split_covariate_id :
         reference = split_reference_value
      #
      if covariate_id in rel_covariate_id_set :
         #
         # covariate_list
         covariate_row  = covariate_table[covariate_id]
         covariate_list = list()
         for data_id in data_subset_list :
            data_row  = data_table[data_id]
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
   # BEGIN_RETURN
   # ...
   assert type(cov_reference_list) == list
   return cov_reference_list
   # END_RETURN
