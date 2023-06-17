# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-23 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin fit_or_root}

Get Tables Corresponding to a Fit Node
######################################

Constructor
***********
{xrst_literal
   # BEGIN_CTOR
   # END_CTOR
}

fit_node_database
=================
is the name of a :ref:`glossary@fit_node_database` .

root_node_database
==================
is the name of a :ref:`glossary@root_node_database` .

get_table
*********
{xrst_literal
   # BEGIN_GET_TABLE
   # END_GET_TABLE
}

table_name
==========
If the name of the table that we are getting.
If it is a :ref:`constant table <module@constant_table_list>` ,
it is retrieved from the root node database.
Otherwise it is retrieved from the fit node database.

table
=====
This is a list of dict representation of the table.

{xrst_end fit_or_root}
'''
import dismod_at
import at_cascade
#
class fit_or_root :
   #
   # BEGIN_CTOR
   # fit_or_root_obj = fit_or_root(fit_node_database, root_node_database)
   def __init__(self, fit_node_database, root_node_database) :
      assert type(fit_node_database) == str
      assert type(root_node_database) == str
      # END_CTOR
      #
      self.fit_connection = dismod_at.create_connection(
         fit_node_database, new = False, readonly = True
      )
      self.root_connection = dismod_at.create_connection(
         root_node_database, new = False, readonly = True
      )
   #
   # BEGIN_GET_TABLE
   # table = fit_or_root_obj.get_table(table_name)
   def get_table(self, table_name) :
      assert type(table_name) == str
      # END_GET_TABLE
      #
      if table_name in at_cascade.constant_table_list :
         table = dismod_at.get_table_dict(self.root_connection, table_name)
      else :
         table = dismod_at.get_table_dict(self.fit_connection, table_name)
      return table
