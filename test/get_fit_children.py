# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
#
# Below is a diagram of the node tree for this example.
# The fit goal nodes have absolute value bars around them.
#
#                 n0
#        /-----/\-----\
#         n1             |n2|
#        /  \            /  \
#     |n3|  |n4|       n5    n6
# ---------------------------------------------------------------------------
import os
import sys
#
# import at_cascade with a preference current directory version
current_directory = os.getcwd()
if os.path.isfile( current_directory + '/at_cascade/__init__.py' ) :
   sys.path.insert(0, current_directory)
import at_cascade
#
def main() :
   #
   # node_table
   node_table = [
      { 'node_name':'n0',   'parent':None   },
      { 'node_name':'n1',   'parent':0      },
      { 'node_name':'n2',   'parent':0      },
      { 'node_name':'n3',   'parent':1      },
      { 'node_name':'n4',   'parent':1      },
      { 'node_name':'n5',   'parent':2      },
      { 'node_name':'n6',   'parent':2      },
   ]
   #
   # fit_goal_table
   fit_goal_set = {3, 4, 2}
   #
   # root_node_id
   root_node_id = 0
   #
   # fit_children
   fit_children = at_cascade.get_fit_children(
      root_node_id, fit_goal_set, node_table,
   )
   #
   # expected result
   expected = 7 * [set()]
   expected[0] = {1, 2} # fit children of n0
   expected[1] = {3, 4} # fit children of n1
   #
   assert fit_children == expected
main()
print('get_fit_children: OK')
sys.exit(0)
