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
{xsrst_begin get_parent_node}

Get Parent Node Name From Option Table
######################################

Syntax
******
{xsrst_file
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


{xsrst_end get_parent_node}
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
