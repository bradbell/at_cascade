# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-23 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin copy_root_db}

Copy Root Node Database
#######################

Prototype
*********
{xrst_literal
   # BEGIN_COPY_ROOT_DB
   # END_COPY_ROOT_DB
}

Purpose
*******
This routine does the following:

#. Copy the :ref:`glossary@root_node_database` to the *fit_node_database* .
#. Drop all of the constant tables from the fit node database; see
   :ref:`module@constant_table_list` .
#. Change the fit node database option table so that is uses the
   root node database for all the constant tables; i.e.,
   set the other_database and other_input_table options to do this.


{xrst_end copy_root_db}
'''
import os
import shutil
import at_cascade
import dismod_at
#
# BEGIN_COPY_ROOT_DB
def copy_root_db(root_node_database, fit_node_database) :
   assert type(root_node_database) == str
   assert type(fit_node_database) == str
# END_COPY_ROOT_DB
   #
   # fit_node_database
   shutil.copyfile(root_node_database, fit_node_database)
   #
   # connection
   connection = dismod_at.create_connection(
      fit_node_database, new = False, readonly = False
   )
   #
   # fit_node_database
   for table_name in at_cascade.constant_table_list :
      if table_name == 'rate_eff_cov' :
         command = f'DROP TABLE IF EXISTS {table_name}'
      else :
         command = f'DROP TABLE {table_name}'
      dismod_at.sql_command(connection, command)
   command = 'VACUUM;'
   dismod_at.sql_command(connection, command)
   #
   # other_input_table
   other_input_table = ' '.join(at_cascade.constant_table_list)
   if other_input_table == '' :
      other_input_table = None
   #
   # option_table
   option_table = dismod_at.get_table_dict(connection, tbl_name = 'option')
   for row in option_table :
      assert row['option_name'] != 'other_database'
      assert row['option_name'] != 'other_input_table'
   row = dict()
   row['option_name']  = 'other_database'
   if os.path.isabs( root_node_database ) :
      row['option_value'] = root_node_database
   else :
      fit_node_dirname = os.path.dirname( fit_node_database )
      relative_path    = os.path.relpath(root_node_database, fit_node_dirname)
      row['option_value'] = str( relative_path )
   option_table.append(row)
   row = dict()
   row['option_name']  = 'other_input_table'
   row['option_value'] = other_input_table
   option_table.append(row)
   #
   # fit_node_database
   dismod_at.replace_table(
      connection, tbl_name = 'option', table_dict = option_table
   )
