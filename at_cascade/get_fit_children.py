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
This is the node_id in the *node_table* for the root node.

fit_leaf_table
**************
This is python list of python dictionaries.
The length of the list is the size of the
:ref:`glossary.fit_leaf_set`.
For each possible *fit_leaf_id*,
the value *fit_leaf_table[fit_leaf_id]['node_id']* is
the node_id for an element of the fit leaf set.
Each leaf node must be the root node or a descendant
of the root node.

node_table
**********
This is python list of python dictionaries
containing the dismod_at node table.

fit_children
************
The return value *fit_children* is a python list of pythons lists.
For each valid node_id, *fit_children[node_id]* is a list of child_node_id.
Each child_node_id is a child of node_id and is between the root node and the
fit leaf set inclusive.
These are the children of node_id that must be fit to get to the leaf nodes.

{xsrst_end get_fit_children}
'''
# ----------------------------------------------------------------------------
import sys
# ----------------------------------------------------------------------------
def get_fit_children(
# BEGIN syntax
# fit_children = at_cascade.get_fit_children(
    root_node_id    = None ,
    fit_leaf_table  = None ,
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
    for row in fit_leaf_table :
        # leaf node_id, parent_id
        leaf_node_id   = row['node_id']
        node_id        = leaf_node_id
        parent_id      = node_table[node_id]['parent']
        while not done_fit_as_child[node_id] :
            if parent_id == None :
                node_id   = row['node_id']
                leaf_name = node_table[leaf_node_id]['node_name']
                msg       = 'get_fit_children: leaf node = ' + leaf_name
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
