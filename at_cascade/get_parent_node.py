# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin get_parent_node}

Get Parent Node Name From Option Table
######################################

Syntax
******
{xrst_literal
   # BEGIN syntax
   # END syntax
}

database
********
This is a dismod_at database.

parent_node_name
****************
The return value *parent_node_name* is the *database* option table
*option_value* for the row where *option_name* is ``parent_node_name``.
An assert will be generated if no such *option_name* is found in the
option table.


{xrst_end get_parent_node}
'''
import dismod_at
# ----------------------------------------------------------------------------
def get_parent_node(
# BEGIN syntax
# parent_node_name = at_cascade.get_parent_node(
   database = None
# )
# END syntax
) :
   # option_table
   new              = False
   connection       = dismod_at.create_connection(database, new)
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
   return parent_node_name
