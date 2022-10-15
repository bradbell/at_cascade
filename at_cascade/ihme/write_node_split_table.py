# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
import os
import csv
import dismod_at
import at_cascade.ihme
# -----------------------------------------------------------------------------
#
def write_node_split_table(
   results_dur, node_split_name_set, root_node_database
) :
   #
   # node_split_table_file
   node_split_table_file = at_cascade.ihme.csv_file['node_split']
   node_split_table_file = f'{results_dur}/{node_split_table_file}'
   print( f'Creating {node_split_table_file}' )
   #
   # root_table
   new        = False
   connection = dismod_at.create_connection(root_node_database, new)
   node_table = dismod_at.get_table_dict(connection, 'node')
   connection.close()
   #
   # node_split_table
   node_split_table = list()
   for node_name in node_split_name_set :
      node_id = at_cascade.table_name2id(node_table, 'node', node_name)
      #
      # row_out
      row_out = {
         'node_name'    : node_name ,
         'node_id'      : node_id,
      }
      node_split_table.append( row_out )
   #
   #
   # node_split_table_file
   fieldnames = [ 'node_name', 'node_id' ]
   at_cascade.csv.write_table(
       file_name   = node_split_table_file,
      table      = node_split_table,
      columns    = fieldnames,
   )
