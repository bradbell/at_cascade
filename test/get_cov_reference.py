# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
# imports
# ----------------------------------------------------------------------------
import sys
import os
import dismod_at
#
# import at_cascade with a preference current directory version
current_directory = os.getcwd()
if os.path.isfile( current_directory + '/at_cascade/__init__.py' ) :
   sys.path.insert(0, current_directory)
import at_cascade
#
# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------
def main() :
   # -------------------------------------------------------------------------
   # change into the build/test directory
   if not os.path.exists('build/test') :
      os.makedirs('build/test')
   os.chdir('build/test')
   # ------------------------------------------------------------------------
   # all_node_database
   all_node_database = 'all_node.db'
   #
   # connection
   new        = True
   connection = dismod_at.create_connection(all_node_database, new)
   #
   # split_reference_list
   split_reference_list = [ -0.5, 0.0, 0.5 ]
   #
   # absolute_covariates
   absolute_covariates = 'vaccine'
   #
   # all_option table
   tbl_name = 'all_option'
   col_name = [ 'option_name', 'option_value' ]
   col_type = [ 'text',        'text'         ]
   split_covariate_name = 'sex'
   row_list = [
      [ 'result_dir',           '.'  ],
      [ 'root_node_name',       'n0' ],
      [ 'split_covariate_name', split_covariate_name ],
      [ 'absolute_covariates',  absolute_covariates ],
   ]
   dismod_at.create_table(
      connection, tbl_name, col_name, col_type, row_list
   )
   #
   # split_reference table
   tbl_name = 'split_reference'
   col_name = [ 'split_reference_name', 'split_reference_value' ]
   col_type = [ 'text',                 'real']
   row_list = [ ['female', -0.5], ['both', 0.0], ['male', 0.5] ]
   dismod_at.create_table(connection, tbl_name, col_name, col_type, row_list)
   #
   # connection
   connection.close()
   #
   # ------------------------------------------------------------------------
   # root_node_database
   root_node_database  = 'root_node.db'
   #
   # connection
   connection.close()
   new        = True
   connection = dismod_at.create_connection(root_node_database, new)
   #
   # option table
   tbl_name = 'option'
   col_name = [ 'option_name', 'option_value' ]
   col_type = [ 'text',        'text'         ]
   row_list = [
      [ 'parent_node_name', 'n1' ]
   ]
   dismod_at.create_table(
      connection, tbl_name, col_name, col_type, row_list
   )
   #
   # node table
   tbl_name = 'node'
   col_name = [ 'node_name', 'parent'  ]
   col_type = [ 'text',      'integer' ]
   row_list = [
      [ 'n0', None ] ,
      [ 'n1', 0    ] ,
      [ 'n2', 1    ] ,
      [ 'n3', 2    ] ,
   ]
   dismod_at.create_table(
      connection, tbl_name, col_name, col_type, row_list
   )
   #
   # covariate table
   tbl_name = 'covariate'
   col_name = [ 'covariate_name', 'reference', 'max_difference' ]
   col_type = [ 'text',           'real',      'real'           ]
   row_list = [
      [ 'sex',    -0.5,   0.6 ],
      [ 'vaccine', 0.0,   None],
      [ 'bmi',     10.0,  None ],
   ]
   dismod_at.create_table(
      connection, tbl_name, col_name, col_type, row_list
   )
   #
   # row_list
   row_list = [
      # values included in average for split_reference_id in [0, 1]
      [ 0, -0.5, 0.0, 0.0 ], # included in average for node_id >= 0
      [ 1, -0.5, 0.0, 1.0 ], # included in average for node_id >= 1
      [ 2, -0.5, 0.0, 2.0 ], # included in average for node_id >= 2
      [ 3, -0.5, 0.0, 3.0 ], # included in average for node_id >= 3
      # values included in average for split_reference_id in [1, 2]
      [ 0,  0.5, 1.0, 4.0 ], # included in average for node_id >= 0
      [ 1,  0.5, 1.0, 5.0 ], # included in average for node_id >= 1
      [ 2,  0.5, 1.0, 6.0 ], # included in average for node_id >= 2
      [ 3,  0.5, 1.0, 7.0 ], # included in average for node_id >= 3
   ]
   #
   # data table
   tbl_name = 'data'
   col_name = [ 'node_id', 'x_0',  'x_1',   'x_2'  ]
   col_type = [ 'integer', 'real', 'real', 'real' ]
   dismod_at.create_table(
      connection, tbl_name, col_name, col_type, row_list
   )
   # ------------------------------------------------------------------------
   #
   # option_table
   option_table = dismod_at.get_table_dict(connection, 'option')
   assert len( option_table ) == 1
   assert option_table[0]['option_name'] == 'parent_node_name'
   #
   # bmi_covariate_id
   # bmi is the only relative covariate
   bmi_covariate_id = 2
   #
   # node_id
   for node_id in range(4) :
      #
      # option_table
      option_table[0]['option_value'] = f'n{node_id}'
      dismod_at.replace_table(connection, 'option', option_table)
      #
      # split_reference_id
      for split_reference_id in range(3) :
         #
         # cov_reference_list
         cov_reference_list = at_cascade.get_cov_reference(
            all_node_database  = all_node_database,
            fit_node_database  = root_node_database,
            shift_node_id      = node_id,
            split_reference_id = split_reference_id,
         )
         sex      = split_reference_list[split_reference_id]
         bmi_list = list()
         for row in row_list :
            row_node_id = row[0]
            row_sex     = row[1]
            row_vaccine = row[2]
            row_bmi     = row[3]
            include     = row_node_id >= node_id
            include     = include and abs(row_sex - sex) <= 0.6
            if include :
               bmi_list.append( row_bmi )
         avg = sum( bmi_list ) / len(bmi_list)
         #
         assert cov_reference_list[bmi_covariate_id] == avg
main()
print('get_cov_rererence: OK')
sys.exit(0)
