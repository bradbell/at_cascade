# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin get_cov_info}
{xrst_spell
   rel
}

Get Covariate Information
#########################

Prototype
*********
{xrst_literal ,
   # BEGIN_DEF, # END_DEF
   # BEGIN_RETURN, # END_RETURN
}

option_all_table
****************
This is the :ref:`option_all_table-name` as a python list
of python dictionaries.
This argument can't be ``None``.

covariate_table
***************
This is the dismod_at covariate table as a python list
of python dictionaries.
This argument can't be ``None``.

split_reference_table
*********************
This is the :ref:`split_reference_table-name` as a python list
of python dictionaries.
This argument can't be ``None``.

cov_info
********
The return value *cov_info* is a `dict` with the following keys:

abs_covariate_id_set
====================
if *key* is abs_covariate_id_set, *cov_info[key]* is a ``set`` of ``int``.
A covariate_id is in this set if and only if the corresponding
covariate name is in :ref:`option_all_table@absolute_covariates`.
If absolute_covariates does not appear in the option_all table,
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
If :ref:`split_reference_table-name` is empty, this key is not present.
Otherwise, for *key* equal to split_covariate_id, *cov_info[key]* is an ``int``
equal to the covariate_id corresponding to the
:ref:`option_all_table@split_covariate_name`.

split_reference_list
====================
If :ref:`split_reference_table-name` is empty, this key is not present.
Otherwise, for *key* equal to split_reference_list, *cov_info[key]* is a
``list`` of ``float`` representation of
:ref:`split_reference_table@split_reference_value` in the
same order as they appear in the table.

split_reference_id
==================
If :ref:`split_reference_table-name` is empty, this key is not present.
Otherwise, for *key* equal to split_reference_id, *cov_info[key]* is an ``int``
containing an index in the split_reference_list.
The corresponding value in split_reference_list is equal to
the reference value for split_covariate_name in the covariate table.

{xrst_end get_cov_info}
'''
import at_cascade
# BEGIN_DEF
# at_cascade.get_cov_info(
def get_cov_info(
   option_all_table      ,
   covariate_table       ,
   split_reference_table ,
) :
   assert type(option_all_table) == list
   assert type(covariate_table) == list
   assert type(split_reference_table) == list
   # END_DEF
   #
   # option_all
   option_all = dict()
   for row in option_all_table :
      option_all[ row['option_name'] ] = row['option_value']
   #
   # check split_covariate_name
   if len(split_reference_table) == 0 :
      assert not 'split_covariate_name' in option_all
   else :
      assert 'split_covariate_name' in option_all
   #
   # split_reference_list
   split_reference_list = list()
   for row in split_reference_table :
      split_reference_list.append( row['split_reference_value'] )
   #
   # abs_covariate_id_set
   abs_covariate_id_set = set()
   if 'absolute_covariates' in option_all :
      absolute_covariate_list = option_all['absolute_covariates'].split()
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
   split_covariate_name = option_all['split_covariate_name']
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
   # BEGIN_RETURN
   # ...
   assert type(cov_info) == dict
   return cov_info
   # END_RETURN
