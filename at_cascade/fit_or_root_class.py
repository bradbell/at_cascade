# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-23 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin fit_or_root_class}

Get Tables Corresponding to a Fit Node
######################################

fit_or_root_class
*****************
{xrst_code py}
fit_or_root = fit_or_root_class(fit_node_database, root_node_database)
{xrst_code}

fit_node_database
=================
This ``str`` is the name of a :ref:`glossary@fit_node_database` .

root_node_database
==================
This ``str`` is the name of a :ref:`glossary@root_node_database` .

get_table
*********
{xrst_code py}
table = fit_or_root.get_table(table_name)
{xrst_code}

table_name
==========
This ``str`` the name of the table that we are getting.

table
=====
This is a ``list`` of ``dict`` representation of the table.
If *table_name* is a
:ref:`constant table <module@at_cascade.constant_table_list>` ,
*table* is retrieved from the root node database.
Otherwise it is retrieved from the fit node database.

null_row
********
{xrst_code py}
row = fit_or_root.null_row(table_name)
{xrst_code}

table_name
==========
This ``str`` the name of the table that we getting a null row for.

row
===
is a ``dict`` with one key for every column in the table specified
by *table_name* and all the values equal to ``None`` .


close
*****
{xrst_code py}
fit_or_root.close()
{xrst_code}
This closes the database connection held by a fit_or_root.
The ``get_table`` function will no longer be available.

{xrst_end fit_or_root_class}
'''
import dismod_at
import at_cascade
#
class fit_or_root_class :
   #
   # __init__
   def __init__(self, fit_node_database, root_node_database) :
      assert type(fit_node_database) == str
      assert type(root_node_database) == str
      #
      self.fit_connection = dismod_at.create_connection(
         fit_node_database, new = False, readonly = True
      )
      self.root_connection = dismod_at.create_connection(
         root_node_database, new = False, readonly = True
      )
      self.open = True
   #
   # get_table
   def get_table(self, table_name) :
      assert type(table_name) == str
      assert self.open
      #
      if table_name in at_cascade.constant_table_list :
         table = dismod_at.get_table_dict(self.root_connection, table_name)
      else :
         table = dismod_at.get_table_dict(self.fit_connection, table_name)
      return table
   #
   # null_row
   def null_row(self, table_name) :
      if table_name in at_cascade.constant_table_list :
         connection = self.root_connection
      else :
         connection = self.fit_connection
      (col_name, col_type) = dismod_at.get_name_type(connection, table_name)
      row = dict()
      for key in col_name :
         row[key] = None
      return row
   #
   # close
   def close(self) :
      self.fit_connection.close()
      self.root_connection.close()
      self.open = False
