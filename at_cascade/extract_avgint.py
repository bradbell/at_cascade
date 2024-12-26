# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin extract_avgint}

Create an Empty Directory
#########################

Prototype
*********
{xrst_literal ,
   # BEGIN_DEF ,    # END_DEF
   # BEGIN_RETURN , # END_RETURN
}

root_database
*************
On input this database contains a non-empty avgint table.
Upon return the avgint table in this database is empty.

avgint_table
************
This is the avgint table that was in the root_database on input.


{xrst_end extract_avgint}
'''
# -----------------------------------------------------------------------------
import dismod_at
import at_cascade
#
# BEGIN_DEF
# at_cascade.extract_avgint
def extract_avgint(root_database) :
   assert type(root_database) == str
   # END_DEF
   #
   # connection
   connection = dismod_at.create_connection(
      root_database, new = False, readonly = False
   )
   #
   # avgint_table
   avgint_table = dismod_at.get_table_dict(connection, 'avgint')
   #
   # root_database
   empty_table = list()
   message     = 'erase avgint table'
   tbl_name    = 'avgint'
   dismod_at.replace_table(connection, tbl_name, empty_table)
   at_cascade.add_log_entry(connection, message)
   #
   # connection
   connection.close
   #
   # BEGIN_RETURN
   #
   assert type( avgint_table ) == list
   assert type( avgint_table[0] ) == dict
   return avgint_table
   # END_RETURN
