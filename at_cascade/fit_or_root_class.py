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
If it is a :ref:`constant table <module@constant_table_list>` ,
it is retrieved from the root node database.
Otherwise it is retrieved from the fit node database.

table
=====
This is a ``list`` of ``dict`` representation of the table.

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
   # close
   def close(self) :
      self.fit_connection.close()
      self.root_connection.close()
      self.open = False
