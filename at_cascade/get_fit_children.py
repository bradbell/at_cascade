# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin get_fit_children}
{xrst_spell
  len
}

Determine the Set of Nodes to Fit
#################################

Prototype
*********
{xrst_literal ,
   # BEGIN_DEF, # END_DEF
   # BEGIN_RETURN, # END_RETURN
}

root_node_id
************
This is the node_id in the node_table for the
:ref:`glossary@root_node`.

fit_goal_set
************
This is a ``set`` with elements of type ``int``
specifying the node_id for each element of the
:ref:`glossary@fit_goal_set` or :ref:`fit_goal_table-name` .

node_table
**********
This is python list of python dictionaries
containing the dismod_at node table.

fit_children
************
The return value *fit_children* is a python list of python sets.

For each *node_id*
*fit_children* [ *node_id* ] is a the set of node ids that
are children of *node_id* and must be fit in order to fit
all the nodes in *fit_goal_set*.

Note that there must be at least one *node_id* in *fit_goal_set* ,
that is not an ancestor of any node in *fit_goal_set* and hence
len( *fit_children* [ *node_id* ] ) = 0 .

{xrst_end get_fit_children}
'''
# ----------------------------------------------------------------------------
import sys
import at_cascade
# ----------------------------------------------------------------------------
# BEGIN_DEF
# at_cascade.get_fit_children
def get_fit_children(
   root_node_id  ,
   fit_goal_set  ,
   node_table    ,
) :
   assert type( root_node_id ) == int
   assert type( fit_goal_set ) == set
   assert type( node_table ) == list
   # END_DEF
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
   for goal_node_id in fit_goal_set :
      assert type(goal_node_id) == int
      #
      # parend_id_list
      parent_id_list = list()
      parent_id  = node_table[goal_node_id]['parent']
      while parent_id != root_node_id and parent_id != None :
         parent_id_list.append( parent_id )
         parent_id  = node_table[parent_id]['parent']
      #
      # fit_children
      if parent_id == root_node_id :
         node_id = goal_node_id
         for parent_id in parent_id_list :
            fit_children[parent_id].add( node_id )
            node_id = parent_id
         fit_children[root_node_id].add( node_id )
   #
   # BEGIN_RETURN
   # ...
   assert type(fit_children) == list
   ok = False
   for node_id in fit_goal_set :
      ok = ok or len( fit_children[node_id] ) == 0
   assert ok
   return fit_children
   # END_RETURN
