# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-23 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin copy_other_tbl}
{xrst_spell
   tbl
}

Copy Root Node Database
#######################

2DO
***
This routine should be moved
from at_cascade.copy_other_tbl to dismod_at.copy_other_tbl .

Prototype
*********
{xrst_literal
   # BEGIN_PROTOTYPE
   # END_PROTOTYPE
}

Purpose
*******
This routine copies all the dismod_at other tables from the other database
to the dismod_at *fit_node_database* .
In addition, it changes the option table in the *fit_node_database*
so that it does not require any tables in another database.

{xrst_end copy_other_tbl}
'''
import os
import shutil
import tempfile
import at_cascade
import dismod_at
#
# BEGIN_PROTOTYPE
# at_cascade.copy_root_db
def copy_other_tbl(fit_node_database) :
   assert type(fit_node_database) == str
   # END_PROTOTYPE
   #
   # fit_connection
   fit_connection = dismod_at.create_connection(
      fit_node_database, new = False, readonly = False
   )
   #
   # option_table
   option_table = dismod_at.get_table_dict(fit_connection, tbl_name = 'option')
   #
   # other_database, other_input_table, option_table
   other_database    = None
   other_input_table = None
   for row in option_table :
      if row['option_name'] == 'other_database' :
         other_database      = row['option_value']
         row['option_value'] = None
      if row['option_name'] == 'other_input_table' :
         other_input_table   = row['option_value']
         row['option_value'] = None
   #
   # other_table_list
   other_table_list = other_input_table.split()
   #
   # fit_database.option_table
   dismod_at.replace_table(fit_connection, 'option', option_table)
   #
   # other_database
   index = fit_node_database.rindex('/')
   if 0 <= index :
      fit_dir        = fit_node_database[0 : index]
      other_database = f'{fit_dir}/{other_database}'
   #
   # other_connection
   other_connection = dismod_at.create_connection(
      other_database, new = False, readonly = True
   )
   #
   # table_name
   for tbl_name in other_table_list :
      #
      table              = dismod_at.get_table_dict(other_connection, tbl_name)
      col_name, col_type = dismod_at.get_name_type(other_connection,  tbl_name)
      row_list           = list()
      primary_key        = f'{tbl_name}_id'
      assert col_name[0] == primary_key
      col_name.pop(0)
      col_type.pop(0)
      for row_in in table :
         row_out = list()
         for name in col_name :
            row_out.append( row_in[name] )
         row_list.append( row_out )
      dismod_at.create_table(
         fit_connection, tbl_name, col_name, col_type, row_list
      )
   #
   # fit_connection, other_connection
   fit_connection.close()
   other_connection.close()
