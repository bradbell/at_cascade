# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin table_exists}

Check if A Database Table Exists
################################

Syntax
******
{xrst_literal
   # BEGIN_SYNTAX
   # END_SYNTAX
}
{xrst_literal
   # BEGIN_RETURN
   # END_RETURN
}

connection
**********
s a dismod_at connection to the database.


table_name
**********
is the name of the table.

result
******
is either True (table exists) or False (table does not exist).

{xrst_end table_exists}
'''
# -----------------------------------------------------------------------------
import dismod_at
def table_exists(
# BEGIN_SYNTAX
# exists = at_cascade.table_exists(
   connection,
   table_name
) :
   assert type(table_name) == str
   # END_SYNTAX
   command = f"SELECT name FROM sqlite_master WHERE name='{table_name}'"
   result  = dismod_at.sql_command(connection, command)
   exists  = len( result ) > 0
   # BEGIN_RETURN
   assert type(exists) == bool
   return exists
   # END_RETURN
