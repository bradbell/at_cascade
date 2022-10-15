# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin move_table}
{xrst_spell
   dst
   src
}

Move Table
##########

Syntax
******
{xrst_literal
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

1. *log_id*: is the integer length of the log table before the message
2. *message_type* is text ``at_cascade``
3. *table_name* is null
4. *row_id* is null
5. *seconds* is the integer unit time
6. *message* is the text message

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
