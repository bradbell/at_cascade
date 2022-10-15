# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin get_cov_info}
{xrst_spell
   cov
   rel
}

Get Covariate Information
#########################

Syntax
******
{xrst_literal
   # BEGIN syntax
   # END syntax
}

all_option_table
****************
This is the :ref:`all_option_table` as a python list
of python dictionaries.
This argument can't be ``None``.

covariate_table
***************
This is the dismod_at covariate table as a python list
of python dictionaries.
This argument can't be ``None``.

split_reference_table
*********************
This is the :ref:`split_reference_table` as a python list
of python dictionaries.
This argument can't be ``None``.

cov_info
********
The return value *cov_info* is a `dict` with the following keys:

abs_covariate_id_set
====================
if *key* is abs_covariate_id_set, *cov_info[key]* is a ``set`` of ``int``.
A covariate_id is in this set if and only if the corresponding
covariate name is in :ref:`all_option_table@absolute_covariates`.
If absolute_covariates does not appear in the all_option table,
*cov_info[key]* is the empty set.
The reference value for these absolute covariates is the same
for all nodes and all values of the splitting covariate.

rel_covariate_id_set
====================
if *key* is rel_covariate_id_set, *cov_info[key]* is a set of ``int``.
This is the set of covariate_id values corresponding to the
:ref:`relative covariates<glossary@Relative Covariate>`.

split_covariate_id
==================
If :ref:`split_reference_table` is empty, this key is not present.
Otherwise, for *key* equal to split_covariate_id, *cov_info[key]* is an ``int``
equal to the covariate_id corresponding to the
:ref:`all_option_table@split_covariate_name`.

split_reference_list
====================
If :ref:`split_reference_table` is empty, this key is not present.
Otherwise, for *key* equal to split_reference_list, *cov_info[key]* is a
``list`` of ``float`` representation of
:ref:`split_reference_table@split_reference_value` in the
same order as they appear in the table.

split_reference_id
==================
If :ref:`split_reference_table` is empty, this key is not present.
Otherwise, for *key* equal to split_reference_id, *cov_info[key]* is an ``int``
containing an index in the split_reference_list.
The corresponding value in split_reference_list is equal to
the reference value for split_covariate_name in the covariate table.

{xrst_end get_cov_info}
'''
import at_cascade
#
def get_cov_info(
# BEGIN syntax
# cov_info = at_cascade.get_cov_info(
   all_option_table      = None ,
   covariate_table       = None ,
   split_reference_table = None,
# )
# END syntax
) :
   assert not all_option_table      is None
   assert not covariate_table       is None
   assert not split_reference_table is None
   #
   # all_option
   all_option = dict()
   for row in all_option_table :
      all_option[ row['option_name'] ] = row['option_value']
   #
   # check split_covariate_name
   if len(split_reference_table) == 0 :
      assert not 'split_covariate_name' in all_option
   else :
      assert 'split_covariate_name' in all_option
   #
   # split_reference_list
   split_reference_list = list()
   for row in split_reference_table :
      split_reference_list.append( row['split_reference_value'] )
   #
   # abs_covariate_id_set
   abs_covariate_id_set = set()
   if 'absolute_covariates' in all_option :
      absolute_covariate_list = all_option['absolute_covariates'].split()
      for covariate_name in absolute_covariate_list :
         covariate_id = at_cascade.table_name2id(
            covariate_table, 'covariate', covariate_name
         )
         abs_covariate_id_set.add(covariate_id)
   #
   # rel_covariate_id_set
   rel_covariate_id_set = set()
   for covariate_id in range( len(covariate_table) ) :
      if not covariate_id in abs_covariate_id_set :
         rel_covariate_id_set.add( covariate_id )
   #
   # case where no splitting covariate
   if len(split_reference_table) == 0 :
      cov_info = {
         'abs_covariate_id_set':  abs_covariate_id_set,
         'rel_covariate_id_set':  rel_covariate_id_set,
      }
      return cov_info
   #
   # split_covarate_name
   split_covariate_name = all_option['split_covariate_name']
   #
   # split_covariate_id
   split_covariate_id   = at_cascade.table_name2id(
      covariate_table, 'covariate', split_covariate_name
   )
   #
   # rel_covariate_id_set
   rel_covariate_id_set.discard( split_covariate_id )
   #
   # split_reference
   split_reference = covariate_table[split_covariate_id]['reference']
   #
   # split_reference_id
   if not split_reference in split_reference_list :
      msg  = 'Cannot find covariate table value for splitting covariate '
      msg += 'in split_reference table\n'
      msg += f'split_reference_value = {split_reference_list}, '
      msg += f'split_covariate_id = {split_covariate_id}, '
      msg += f'covariate table reference value = {split_reference}'
      assert False, msg
   split_reference_id = split_reference_list.index( split_reference )
   #
   cov_info = {
      'abs_covariate_id_set':  abs_covariate_id_set,
      'rel_covariate_id_set':  rel_covariate_id_set,
      'split_covariate_id':    split_covariate_id,
      'split_reference_list':  split_reference_list,
      'split_reference_id':    split_reference_id,
   }
   #
   return cov_info
