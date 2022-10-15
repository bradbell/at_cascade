# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
import os
import sys
#
# import at_cascade with a preference current directory version
current_directory = os.getcwd()
if os.path.isfile( current_directory + '/at_cascade/__init__.py' ) :
   sys.path.insert(0, current_directory)
import at_cascade
#
# node_table
node_table = [
   { 'node_name' : 'n0',  'parent' : None },
   { 'node_name' : 'n1',  'parent' : 0    },
   { 'node_name' : 'n2',  'parent' : 0    },
   { 'node_name' : 'n3',  'parent' : 1    },
   { 'node_name' : 'n4',  'parent' : 1    },
   { 'node_name' : 'n5',  'parent' : 2    },
   { 'node_name' : 'n6',  'parent' : 2    },
]
# split_reference_table
split_reference_table = [
   { 'split_reference_name' : 'female', 'split_reference_value' : -1.0 },
   { 'split_reference_name' : 'both',   'split_reference_value' : 0.0 },
   { 'split_reference_name' : 'male',   'split_reference_value' : +1.0 },
]
# node_split_set
node_split_set = { 1, 2 }  # n1, n2
#
# root_node_id, root_split_reference_id
root_node_id            = 0      # n0
root_split_reference_id = 1     # both
#
# node n1 before splitting by sex
database_dir = at_cascade.get_database_dir(
   node_table              = node_table ,
   split_reference_table   = split_reference_table,
   node_split_set          = node_split_set,
   root_node_id            = root_node_id,
   root_split_reference_id = root_split_reference_id,
   fit_node_id             = 1,                       # n1
   fit_split_reference_id  = root_split_reference_id, # both
)
assert database_dir == 'n0/n1'
#
# node n1 after splitting by sex
database_dir = at_cascade.get_database_dir(
   node_table              = node_table ,
   split_reference_table   = split_reference_table,
   node_split_set          = node_split_set,
   root_node_id            = root_node_id,
   root_split_reference_id = root_split_reference_id,
   fit_node_id             = 1, # n1
   fit_split_reference_id  = 0, # female
)
assert database_dir == 'n0/n1/female'
#
# node n5
database_dir = at_cascade.get_database_dir(
   node_table              = node_table ,
   split_reference_table   = split_reference_table,
   node_split_set          = node_split_set,
   root_node_id            = root_node_id,
   root_split_reference_id = root_split_reference_id,
   fit_node_id             = 5, # n5
   fit_split_reference_id  = 2, # male
)
assert database_dir == 'n0/n2/male/n5'
#
print('get_database_dir: OK')
sys.exit(0)
