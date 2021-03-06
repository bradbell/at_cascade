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
{xsrst_begin add_log_entry}

Add Log Table Entry
###################

Syntax
******
{xsrst_file
    # BEGIN syntax
    # END syntax
}

Purpose
*******
Change the name of a table in the database.

connection
**********
is a dismod_at open connection to the database.

message
*******
is a ``str`` containing the message that is added at
the end of the log table

Log Table
*********
As row is added at the end of the log table with the
following columns values:

1.  *log_id* : is the integer length of the log table before the message
2.  *message_type* : is the text ``at_cascade``
3.  *table_name* : is null
4.  *row_id* : is null
5.  *unix_time* : is the integer unit time
6.  *message* : is the text message

{xsrst_end   add_log_entry}
'''
import time
import dismod_at
# ----------------------------------------------------------------------------
# BEGIN syntax
def add_log_entry(connection, message) :
# END syntax
    #
    # cmd
    cmd  = 'create table if not exists log('
    cmd += 'log_id       integer primary key,'
    cmd += 'message_type text,'
    cmd += 'table_name   text,'
    cmd += 'row_id       integer,'
    cmd += 'unix_time    integer,'
    cmd += 'message      text)'
    dismod_at.sql_command(connection, cmd)
    #
    # log_table
    log_table = dismod_at.get_table_dict(connection, 'log')
    #
    # seconds
    seconds   = int( time.time() )
    #
    # message_type
    message_type = 'at_cascade'
    #
    # cmd
    cmd = 'insert into log'
    cmd += ' (log_id,message_type,table_name,row_id,unix_time,message) values('
    cmd += str( len(log_table) ) + ','     # log_id
    cmd += f'"{message_type}",'            # message_type
    cmd += 'null,'                         # table_name
    cmd += 'null,'                         # row_id
    cmd += str(seconds) + ','              # unix_time
    cmd += f'"{message}")'                 # message
    dismod_at.sql_command(connection, cmd)
