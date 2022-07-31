# -----------------------------------------------------------------------------
# at_cascade: Cascading Dismod_at Analysis From Parent To Child Regions
#           Copyright (C) 2021-22 University of Washington
#              (Bradley M. Bell bradbell@uw.edu)
#
# This program is distributed under the terms of the
#     GNU Affero General Public License version 3.0 or later
# see http://www.gnu.org/licenses/agpl.txt
# -----------------------------------------------------------------------------
'''
{xrst_begin move_table}
{xrst_spell
    src
    dst
}

Move Table
##########

Syntax
******
{xrst_file
    # BEGIN syntax
    # END syntax
}

Purpose
*******
Change the name of a table in the database.

connection
**********
Is a dismod_at open connection to the database.

src_name
********
is a ``str`` containing the name of the table before moving it.

dst_name
********
is a ``str`` containing the name of the table after moving it.

Log Table
*********
As row is added to the log table with the
ref:`add_log_entry.message` that says that table *src_name* was moved
to table *dst_name*.

1.  *log_id*: is the integer length of the log table before the message
2.  *message_type* is text ``at_cascade``
3.  *table_name* is null
4.  *row_id* is null
5.  *seconds* is the integer unit time
6.  *message* is the text message

{xrst_end   move_table}
'''
import dismod_at
import at_cascade
# ----------------------------------------------------------------------------
# BEGIN syntax
def move_table(
    connection, src_name, dst_name
) :
# END syntax
    #
    command     = 'DROP TABLE IF EXISTS ' + dst_name
    dismod_at.sql_command(connection, command)
    #
    command     = 'ALTER TABLE ' + src_name + ' RENAME COLUMN '
    command    += src_name + '_id TO ' + dst_name + '_id'
    dismod_at.sql_command(connection, command)
    #
    command     = 'ALTER TABLE ' + src_name + ' RENAME TO ' + dst_name
    dismod_at.sql_command(connection, command)
    #
    # log table
    message      = f'move table {src_name} to {dst_name}'
    at_cascade.add_log_entry(connection, message)
