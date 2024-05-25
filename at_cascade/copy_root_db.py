# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
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

root_node_database
******************
This is the :ref:`glossary@root_node_database` .
It must exist when this routine is called.

fit_node_database
*****************
This is a :ref:`glossary@fit_node_database` that
can be used to fit the root node.
The directory where the *fit_node_database* will be located must exist
when this routine is called.
This database is created as follows:

#. Copy the root node database to the fit node database.

#. Drop all of the constant tables from the fit node database; see
   :ref:`module@at_cascade.constant_table_list` .

#. Change the fit node database option table so that is uses the
   root node database for all the constant tables; i.e.,
   set the other_database and other_input_table options to do this.

#. Create an empty log table in the fit node database.


{xrst_end copy_root_db}
'''
import os
import shutil
import at_cascade
import dismod_at
# -----------------------------------------------------------------------------
def create_empty_log_table(connection) :
   #
   cmd  = 'create table if not exists log('
   cmd += ' log_id        integer primary key,'
   cmd += ' message_type  text               ,'
   cmd += ' table_name    text               ,'
   cmd += ' row_id        integer            ,'
   cmd += ' unix_time     integer            ,'
   cmd += ' message       text               )'
   dismod_at.sql_command(connection, cmd)
   #
   # log table
   empty_list = list()
   dismod_at.replace_table(connection, 'log', empty_list)
# -----------------------------------------------------------------------------
# BEGIN_COPY_ROOT_DB
# at_cascade.copy_root_db
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
   #
   # log table
   create_empty_log_table(connection)
   #
   # connection
   connection.close()
