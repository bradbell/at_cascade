# -----------------------------------------------------------------------------
# at_cascade: Cascading Dismod_at Analysis From Parent To Child Regions
#           Copyright (C) 2021-21 University of Washington
#              (Bradley M. Bell bradbell@uw.edu)
#
# This program is distributed under the terms of the
#     GNU Affero General Public License version 3.0 or later
# see http://www.gnu.org/licenses/agpl.txt
# -----------------------------------------------------------------------------
'''
{xsrst_begin get_fit_children}

Determine the Set of Nodes to Fit
#################################

Syntax
******
{xsrst_file
    # BEGIN syntax
    # END syntax
}

root_node_id
************
This is the node_id in the node_table for the
:ref:`glossary.root_node`.

fit_goal_table
**************
This is python list of python dictionaries containing the
:ref:`fit_goal_table` .

node_table
**********
This is python list of python dictionaries
containing the dismod_at node table.

fit_children
************
The return value *fit_children* is a python list of python lists.
For each *node_id* in the node table,
*fit_children[node_id]* is a list of child_node_id.
Each child_node_id is a child of *node_id* and is between the
root_node and the :ref:`glossary.fit_goal_set` inclusive.
These are the children of node_id that must be fit to obtain
a fit for all the goal nodes.

{xsrst_end get_fit_children}
'''
# ----------------------------------------------------------------------------
import sys
# ----------------------------------------------------------------------------
def get_fit_children(
# BEGIN syntax
# fit_children = at_cascade.get_fit_children(
    root_node_id    = None ,
    fit_goal_table  = None ,
    node_table      = None ,
# )
# END syntax
) :
    # number of nodes
    n_node       = len( node_table )
    #
    # intialize return value
    fit_children = list()
    for i in range(n_node) :
        fit_children.append( list() )
    #
    # initialize which nodes need to be fit as a child
    done_fit_as_child = n_node * [False]
    #
    # root_node_id does not need to be fit as a child
    done_fit_as_child[root_node_id] = True
    #
    # row
    for row in fit_goal_table :
        # goal node_id, parent_id
        goal_node_id   = row['node_id']
        node_id        = goal_node_id
        parent_id      = node_table[node_id]['parent']
        while not done_fit_as_child[node_id] :
            if parent_id == None :
                node_id   = row['node_id']
                goal_name = node_table[goal_node_id]['node_name']
                msg       = 'get_fit_children: goal node = ' + goal_name
                msg      += '\nis not a descendant of the root node = '
                msg      += node_table[root_node_id]['node_name']
                sys.exit(msg)
            # fit_children
            fit_children[parent_id].append(node_id)
            done_fit_as_child[node_id] = True
            #
            # next node_id, parent_id
            node_id   = parent_id
            parent_id = node_table[node_id]['parent']

    return fit_children
