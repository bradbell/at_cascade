# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin get_database_dir}
{xrst_spell
   dir
}

Get Database Directory Corresponding To a Fit
#############################################

Syntax
******
{xrst_literal
   # BEGIN syntax
   # END syntax
}

node_table
**********
is the node_table for this cascade as a ``list'' of ``dict``.
It can't be ``None``.

split_reference_table
*********************
is the :ref:`split_reference_table` as a ``list`` of ``dict``.
It can't be ``None``.
If the list has length zero,
we say that the table is empty.

node_split_set
**************
If :ref:`split_reference_table` is empty,
this argument must be None.
Otherwise it is a ``set`` of ``int`` containing the
:ref:`node_split_table@node_id` values that appear in the
node_spit table.

root_node_id
************
is the node_id for the :ref:`glossary@root_node`.

root_split_reference_id
***********************
If :ref:`split_reference_table` is empty,
this argument must be None.
Otherwise it is an ``int`` specifying the
:ref:`split_reference_table@split_reference_id`
that the root node corresponds to.

fit_node_id
***********
This argument is an ``int`` is the node_id for the  :ref:`glossary@fit_node`.
It can't be ``None``.

fit_split_reference_id
**********************
If :ref:`split_reference_table` is empty,
this argument must be None.
Otherwise it is an ``int`` specifying the
:ref:`split_reference_table@split_reference_id`
that the fit corresponds to.

database_dir
************
The return value is a ``str`` containing the directory,
relative to the :ref:`all_option_table@result_dir`,
where the database corresponding to the fit is (or will be) located.
In other words, the fit database has the following path:

   *result_dir*\ ``/`` *database_dir*\ ``/dismod.db``


{xrst_end get_database_dir}
'''
import dismod_at
# ----------------------------------------------------------------------------
def get_database_dir(
# BEGIN syntax
# database_dir = at_cascade.get_database_dir(
   node_table              = None,
   split_reference_table   = None,
   node_split_set          = None,
   root_node_id            = None,
   root_split_reference_id = None,
   fit_node_id             = None,
   fit_split_reference_id  = None,
# )
# END syntax
) :
   #
   # fit_split_reference_name
   if 0 < len(split_reference_table) :
      row = split_reference_table[fit_split_reference_id]
      fit_split_reference_name = row['split_reference_name']
   #
   # database_dir
   database_dir = ''
   #
   # node_id, split_reference_id
   node_id            = fit_node_id
   split_reference_id = fit_split_reference_id
   #
   while node_id not in [ None, root_node_id ] :
      #
      # split
      split = root_split_reference_id != split_reference_id \
         and node_id in node_split_set
      #
      # next node_id, split_reference_id pair
      if split :
         assert 0 < len(split_reference_table)
         #
         # database_dir
         database_dir      = f'{fit_split_reference_name}/{database_dir}'
         #
         # split_reference_id
         split_reference_id = root_split_reference_id
      else :
         #
         # database_dir
         node_name     = node_table[node_id]['node_name']
         database_dir = f'{node_name}/{database_dir}'
         #
         # node_id
         node_id       = node_table[node_id]['parent']
   if node_id is None :
      fit_node_name  = node_table[fit_node_id]['node_name']
      root_node_name = node_table[root_node_id]['node_name']
      msg  = f'{fit_node_name} is not a descendent of the root node '
      msg += root_node_name
      assert False, msg
   #
   split =  root_split_reference_id != split_reference_id \
      and root_node_id in node_split_set
   if split :
      assert 0 < len(split_reference_table)
      #
      # database_dir
      database_dir = f'{fit_split_reference_name}/{database_dir}'
   #
   root_node_name = node_table[root_node_id]['node_name']
   database_dir = f'{root_node_name}/{database_dir}'
   #
   # database_dir
   database_dir = database_dir[:-1]
   return database_dir
