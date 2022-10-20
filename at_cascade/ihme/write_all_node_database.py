# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
import os
import csv
import dismod_at
import at_cascade.ihme
# -----------------------------------------------------------------------------
def get_file_path(result_dir, csv_file_key) :
   csv_file  = at_cascade.ihme.csv_file
   file_name = csv_file[csv_file_key]
   file_name = f'{result_dir}/{file_name}'
   return file_name
# -----------------------------------------------------------------------------
def write_table(connection, table, tbl_name, col_list) :
   col_name_list = list()
   col_type_list = list()
   for (col_name, col_type) in col_list :
      col_name_list.append( col_name )
      col_type_list.append( col_type )
   #
   row_list = list()
   for row_in in table :
      row_out = list()
      for col_name in col_name_list :
         row_out.append( row_in[col_name] )
      row_list.append( row_out )
   dismod_at.create_table(
      connection, tbl_name, col_name_list, col_type_list, row_list
   )
# -----------------------------------------------------------------------------
# write_all_node_database
def write_all_node_database(result_dir, root_node_database) :
   #
   # all_node_database
   all_node_database = f'{result_dir}/all_node.db'
   print( f'Begin: creating {all_node_database}' )
   #
   # intermediate files
   # BEGIN_SORT_THIS_LINE_PLUS_1
   all_omega_table_file     = get_file_path(result_dir, 'all_omega')
   all_option_table_file    = get_file_path(result_dir, 'all_option')
   omega_index_table_file   = get_file_path(result_dir, 'omega_index')
   mulcov_freeze_table_file = get_file_path(result_dir, 'mulcov_freeze')
   node_split_table_file    = get_file_path(result_dir, 'node_split')
   omega_age_table_file     = get_file_path(result_dir, 'omega_age')
   omega_time_table_file    = get_file_path(result_dir, 'omega_time')
   # END_SORT_THIS_LINE_MINUS_1
   #
   # root_table
   root_table = dict()
   new        = False
   connection = dismod_at.create_connection(root_node_database, new)
   root_table['covariate'] = dismod_at.get_table_dict(connection, 'covariate')
   root_table['node']      = dismod_at.get_table_dict(connection, 'node')
   root_table['age']       = dismod_at.get_table_dict(connection, 'age')
   root_table['time']      = dismod_at.get_table_dict(connection, 'time')
   connection.close()
   #
   # connection
   new        = True
   connection = dismod_at.create_connection(all_node_database, new)
   #
   # all_option
   all_option_table = at_cascade.csv.read_table(all_option_table_file)
   tbl_name = 'all_option'
   col_list = [ ('option_name', 'text'), ('option_value', 'text') ]
   write_table(connection, all_option_table, tbl_name, col_list)
   #
   # split_refererence_table
   split_reference_table = list()
   sex_info_dict         = at_cascade.ihme.sex_info_dict
   for sex_name in sex_info_dict :
      row                = sex_info_dict[sex_name]
      covariate_value    = row['covariate_value']
      split_reference_id = row['split_reference_id']
      row_out = {
         'split_reference_name'  : sex_name,
         'split_reference_value' : covariate_value,
         'split_reference_id'    : split_reference_id,
      }
      split_reference_table.append( row_out )
   fun = lambda row : row['split_reference_id']
   split_reference_table = sorted(split_reference_table, key = fun)
   tbl_name = 'split_reference'
   col_list = [
      ('split_reference_name', 'text'),
      ('split_reference_value', 'real'),
   ]
   write_table(connection, split_reference_table, tbl_name, col_list)
   #
   # all_option
   all_option = dict()
   for row in all_option_table :
      option_name  = row['option_name']
      option_value = row['option_value']
      all_option[option_name] = option_value
   #
   # node_split_table
   node_split_table = at_cascade.csv.read_table( node_split_table_file )
   for row in node_split_table :
      row['node_id'] = int( row['node_id'] )
   tbl_name = 'node_split'
   col_list = [ ('node_id', 'integer') ]
   write_table(connection, node_split_table, tbl_name, col_list)
   #
   # mulcov_freeze_table
   mulcov_freeze_table = at_cascade.csv.read_table(
      mulcov_freeze_table_file
   )
   for row in mulcov_freeze_table :
      row['fit_node_id']        = int( row['fit_node_id'] )
      row['split_reference_id'] = int( row['split_reference_id'] )
      row['mulcov_id']          = int( row['mulcov_id'] )
   tbl_name = 'mulcov_freeze'
   col_list = [
      ('fit_node_id', 'integer'),
      ('split_reference_id', 'integer'),
      ('mulcov_id', 'integer'),
   ]
   write_table(connection, mulcov_freeze_table, tbl_name, col_list)
   #
   # omega_age_grid_table
   omega_age_table  = at_cascade.csv.read_table(omega_age_table_file)
   age_list         = list()
   for row in root_table['age'] :
      age_list.append( row['age'] )
   omega_age_grid_table = list()
   for row in omega_age_table :
      age    = float( row['age'] )
      age_id = age_list.index( age )
      omega_age_grid_table.append( { 'age_id' : age_id } )
   tbl_name = 'omega_age_grid'
   col_list = [ ('age_id', 'integer') ]
   write_table(connection, omega_age_grid_table, tbl_name, col_list)
   #
   # omega_time_grid_table
   omega_time_table  = at_cascade.csv.read_table(omega_time_table_file)
   time_list         = list()
   for row in root_table['time'] :
      time_list.append( row['time'] )
   omega_time_grid_table = list()
   for row in omega_time_table :
      time    = float( row['time'] )
      time_id = time_list.index( time )
      omega_time_grid_table.append( { 'time_id' : time_id } )
   tbl_name = 'omega_time_grid'
   col_list = [ ('time_id', 'integer') ]
   write_table(connection, omega_time_grid_table, tbl_name, col_list)
   #
   # omega_index_table
   omega_index_table = at_cascade.csv.read_table(omega_index_table_file)
   tbl_name = 'omega_index'
   col_list = [
      ('node_id', 'integer'),
      ('split_reference_id', 'integer'),
      ('all_omega_id', 'integer'),
   ]
   write_table(connection, omega_index_table, tbl_name, col_list)
   #
   # all_omega_table
   all_omega_table   = at_cascade.csv.read_table(all_omega_table_file)
   tbl_name = 'all_omega'
   col_list = [ ('all_omega_value', 'real') ]
   write_table(connection, all_omega_table, tbl_name, col_list)
   #
   # mtspecific_index_table
   mtspecific_index_table = list()
   tbl_name = 'mtspecific_index'
   col_list = [
      ('node_id', 'integer'),
      ('split_reference_id', 'integer'),
      ('all_mtspecific_id', 'integer'),
   ]
   write_table(connection, mtspecific_index_table, tbl_name, col_list)
   #
   # all_mtspecific_table
   all_mtspecific_table   = list()
   tbl_name = 'all_mtspecific'
   col_list = [ ('all_mtspecific_value', 'real') ]
   write_table(connection, all_mtspecific_table, tbl_name, col_list)
   #
   # connection
   connection.close()
   #
   print( f'End: creating {all_node_database}' )
