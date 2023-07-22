# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-23 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin get_parent_node}

Get Parent Node Name From Option Table
######################################

PROTOTYPE
*********
{xrst_literal ,
   # BEGIN_PROTOTYPE, # END_PROTOTYPE
   # BEGIN_RETURN,  # END_RETURN
}

database
********
This is a dismod_at database.

parent_node_name
****************
is the *database* option table
*option_value* for the row where *option_name* is ``parent_node_name``.
An assert will be generated if no such *option_name* is found in the
option table.


{xrst_end get_parent_node}
'''
import dismod_at
# ----------------------------------------------------------------------------
# BEGIN_PROTOTYPE
def get_parent_node(database = None) :
   assert type(database) == str
   # END_PROTOTYPE
   #
   # option_table
   connection       = dismod_at.create_connection(
      database, new = False, readonly = True
   )
   option_table     = dismod_at.get_table_dict(connection, 'option')
   connection.close()
   #
   # parent_node_name
   parent_node_name = None
   for row in option_table :
      if row['option_name'] == 'parent_node_name' :
         parent_node_name = row['option_value']
   msg = 'Cannot find parent_node_name row in option table in ' + database
   assert not parent_node_name is None, msg
   #
   # BEGIN_RETURN
   # ..
   assert type(parent_node_name) == str
   return parent_node_name
   # END_RETURN
