# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin get_fit_children}

Determine the Set of Nodes to Fit
#################################

Syntax
******
{xrst_literal
   # BEGIN syntax
   # END syntax
}

root_node_id
************
This is the node_id in the node_table for the
:ref:`glossary@root_node`.

fit_goal_set
************
This is a ``set`` with elements of type ``int`` (``str``)
specifying the node_id (node_name) for each element of the
:ref:`glossary@fit_goal_set` .

node_table
**********
This is python list of python dictionaries
containing the dismod_at node table.

fit_children
************
The return value *fit_children* is a python list of python sets.
For each *node_id* in the node table,
*fit_children[node_id]* is a the set of child_node_id.
A child_node_id is in this set if and only if
it is a child of *node_id* and is in the :ref:`glossary@fit_node_set`.
These are the children of node_id that must be fit to obtain
a fit for the :ref:`glossary@fit_goal_set`.

{xrst_end get_fit_children}
'''
# ----------------------------------------------------------------------------
import sys
import at_cascade
# ----------------------------------------------------------------------------
def get_fit_children(
# BEGIN syntax
# fit_children = at_cascade.get_fit_children(
   root_node_id  = None ,
   fit_goal_set  = None ,
   node_table    = None ,
# )
# END syntax
) :
   assert type( root_node_id ) == int
   assert type( fit_goal_set ) == set
   assert type( node_table ) == list
   #
   # number of nodes
   n_node       = len( node_table )
   #
   # fit_chiledren
   fit_children = list()
   for i in range(n_node) :
      fit_children.append( set() )
   #
   # goal_node_id
   for node in fit_goal_set :
      if type(node) == str :
         goal_node_id = at_cascade.table_name2id(node_table, 'node', node)
      else :
         assert type(node) == int
         goal_node_id = node
      #
      # node_id, parent_id
      node_id    = goal_node_id
      parent_id  = node_table[node_id]['parent']
      #
      while node_id != root_node_id :
         #
         if parent_id == None :
            goal_name = node_table[goal_node_id]['node_name']
            msg       = 'get_fit_children: goal node = ' + goal_name
            msg      += '\nis not a descendant of the root node = '
            msg      += node_table[root_node_id]['node_name']
            sys.exit(msg)
         #
         # fit_children
         fit_children[parent_id].add(node_id)
         #
         # next node_id, parent_id
         node_id   = parent_id
         parent_id = node_table[node_id]['parent']
   #
   return fit_children
