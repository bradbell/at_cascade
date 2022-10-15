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
def write_mulcov_freeze_table(
   result_dir         = None,
   root_node_database = None,
   mulcov_list_dict   = None,
   mulcov_freeze_list = None,
) :
   assert type(result_dir) == str
   assert type(root_node_database) == str
   assert type(mulcov_list_dict) == list
   assert type(mulcov_freeze_list) == list
   #
   # mulcov_freeze_table_file
   mulcov_freeze_table_file = at_cascade.ihme.csv_file['mulcov_freeze']
   mulcov_freeze_table_file = f'{result_dir}/{mulcov_freeze_table_file}'
   print( f'Creating {mulcov_freeze_table_file}' )
   #
   # root_table
   new        = False
   connection = dismod_at.create_connection(root_node_database, new)
   root_table = dict()
   for tbl_name in [ 'covariate', 'mulcov', 'node', 'rate' ] :
      root_table[tbl_name] = dismod_at.get_table_dict(connection, tbl_name)
   connection.close()
   #
   # mulcov_freeze_table
   mulcov_freeze_table = list()
   for row_freeze in mulcov_freeze_list :
      #
      # node_name, sex_name
      node_name      = row_freeze['node']
      sex_name       = row_freeze['sex']
      #
      for row_mulcov in mulcov_list_dict :
         #
         # rate_name, covariate_name
         rate_name      = row_mulcov['effected']
         covariate_name = row_mulcov['covariate']
         #
         # rate_id
         rate_id        = at_cascade.table_name2id(
            root_table['rate'], 'rate', rate_name
         )
         # covariate_id
         covariate_id   = at_cascade.table_name2id(
            root_table['covariate'], 'covariate', covariate_name
         )
         # fit_node_id
         fit_node_id    = at_cascade.table_name2id(
            root_table['node'], 'node', node_name
         )
         #
         # mulcov_id
         mulcov_id = None
         for (row_id, row) in enumerate(root_table['mulcov']) :
            if row['mulcov_type'] == 'rate_value' :
               if row['rate_id'] == rate_id :
                  if row['covariate_id'] == covariate_id :
                     mulcov_id = row_id
         assert mulcov_id is not None
         #
         # split_reference_id
         sex_info_dict      = at_cascade.ihme.sex_info_dict
         split_reference_id = sex_info_dict[sex_name]['split_reference_id']
         #
         # row_out
         row_out = {
            'fit_node_id'        : fit_node_id ,
            'split_reference_id' : split_reference_id,
            'mulcov_id'          : mulcov_id,
         }
         mulcov_freeze_table.append( row_out )
   #
   #
   # mulcov_freeze_table_file
   fieldnames = [ 'fit_node_id', 'split_reference_id', 'mulcov_id' ]
   at_cascade.csv.write_table(
      file_name  = mulcov_freeze_table_file,
      table      = mulcov_freeze_table,
      columns    = fieldnames,
   )
