# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
import shutil
import datetime
import csv
import os
import dismod_at
import at_cascade.ihme
# ------------------------------------------------------------------------------
def write_message_type_file(
   summary_dir, result_dir, message_type, fit_goal_set, root_node_database
) :
   #
   # all_node_database
   all_node_database = f'{result_dir}/all_node.db'
   #
   # message_dict
   message_dict = at_cascade.check_log(
      message_type       = message_type,
      all_node_database  = all_node_database,
      root_node_database = root_node_database,
      fit_goal_set       = fit_goal_set,
   )
   #
   # message_type file
   file_name = f'{summary_dir}/{message_type}'
   #
   # file_ptr
   file_ptr = open(file_name, 'w')
   #
   first_key = True
   for key in message_dict :
      #
      # first_key
      if not first_key :
         file_ptr.write('\n')
      first_key = False
      #
      file_ptr.write( f'{key}\n' )
      for message in message_dict[key] :
         file_ptr.write( f'{message}\n' )
   #
   file_ptr.close()
# ------------------------------------------------------------------------------
def get_path_table_to_file_name(
   file_name, result_dir, fit_goal_set, root_node_database
) :
   #
   # all_node_database
   all_node_database = f'{result_dir}/all_node.db'
   #
   #
   # node_table, covariate_table
   new        = False
   connection      = dismod_at.create_connection(root_node_database, new)
   node_table      = dismod_at.get_table_dict(connection, 'node')
   covariate_table = dismod_at.get_table_dict(connection, 'covariate')
   connection.close()
   #
   # all_option_table, node_split_table, split_reference_table
   new              = False
   connection       = dismod_at.create_connection(all_node_database, new)
   all_option_table =  dismod_at.get_table_dict(connection, 'all_option')
   node_split_table =  dismod_at.get_table_dict(connection, 'node_split')
   split_reference_table = \
      dismod_at.get_table_dict(connection, 'split_reference')
   connection.close()
   #
   # node_split_set
   node_split_set = set()
   for row in node_split_table :
      node_split_set.add( row['node_id'] )
   #
   # root_node_id
   root_node_name = at_cascade.get_parent_node(root_node_database)
   root_node_id   = at_cascade.table_name2id(
         node_table, 'node', root_node_name
   )
   #
   # root_split_reference_id
   if len(split_reference_table) == 0 :
      root_split_refernence_id = None
   else :
      cov_info = at_cascade.get_cov_info(
         all_option_table      = all_option_table ,
         covariate_table       = covariate_table ,
         split_reference_table = split_reference_table,
      )
      root_split_reference_id = cov_info['split_reference_id']
   #
   # job_table
   job_table = at_cascade.create_job_table(
      all_node_database          = all_node_database       ,
      node_table                 = node_table              ,
      start_node_id              = root_node_id            ,
      start_split_reference_id   = root_split_reference_id ,
      fit_goal_set               = fit_goal_set            ,
   )
   #
   # path_table
   path_table = list()
   #
   # job_id, job_row
   for (job_id, job_row) in enumerate(job_table) :
      #
      # job_name, fit_node_id, fit_split_reference_id
      job_name               = job_row['job_name']
      fit_node_id            = job_row['fit_node_id']
      fit_split_reference_id = job_row['split_reference_id']
      #
      # database_dir
      database_dir           = at_cascade.get_database_dir(
         node_table              = node_table               ,
         split_reference_table   = split_reference_table    ,
         node_split_set          = node_split_set           ,
         root_node_id            = root_node_id             ,
         root_split_reference_id = root_split_reference_id  ,
         fit_node_id             = fit_node_id              ,
         fit_split_reference_id  = fit_split_reference_id   ,
      )
      #
      # file_path
      file_path = f'{result_dir}/{database_dir}/{file_name}'
      #
      # predict_csv_file_list
      if os.path.exists(file_path) :
         row = {
            'path' :               file_path,
            'node_id' :            fit_node_id,
            'split_reference_id' : fit_split_reference_id
         }
         path_table.append(row)
   return path_table
# ------------------------------------------------------------------------------
def combine_predict_files(
   summary_dir, result_dir, fit_goal_set, root_node_database
) :
   #
   # path_table
   file_name = 'predict.csv'
   path_table = get_path_table_to_file_name(
      file_name, result_dir, fit_goal_set, root_node_database
   )
   #
   # precict file
   file_out_name = f'{summary_dir}/predict.csv'
   file_obj_out  = open(file_out_name, "w")
   writer        = None
   for row in path_table :
      file_in_name  = row['path']
      file_obj_in   = open(file_in_name, 'r')
      reader     = csv.DictReader(file_obj_in)
      for row in reader :
         if writer is None :
            keys   = row.keys()
            writer = csv.DictWriter(file_obj_out, columns=keys)
            writer.writeheader()
         writer.writerow(row)
      file_obj_in.close()
   file_obj_out.close()
# ------------------------------------------------------------------------------
def combine_variable_files(
   summary_dir, result_dir, fit_goal_set, root_node_database
) :
   #
   # node_table
   file_path = f'{result_dir}/node_table.csv'
   node_table = at_cascade.csv.read_table(file_path)
   #
   # path_table
   file_name = 'variable.csv'
   path_table = get_path_table_to_file_name(
      file_name, result_dir, fit_goal_set, root_node_database
   )
   #
   # variable file
   file_out_name = f'{summary_dir}/variable.csv'
   file_obj_out  = open(file_out_name, "w")
   writer        = None
   for row in path_table :
      file_in_name       = row['path']
      node_id            = row['node_id']
      split_reference_id = row['split_reference_id']
      #
      sex_id = None
      for sex_name in at_cascade.ihme.sex_info_dict :
         sex_row = at_cascade.ihme.sex_info_dict[sex_name]
         if sex_row['split_reference_id'] == split_reference_id :
               sex_id = sex_row['sex_id']
      assert sex_id is not None
      #
      location_id   = int( node_table[node_id]['location_id'] )
      file_obj_in   = open(file_in_name, 'r')
      reader     = csv.DictReader(file_obj_in)
      for row in reader :
         if writer is None :
            fieldnames = list( row.keys() )
            assert 'location_id' not in fieldnames
            assert 'sex_id' not in fieldnames
            fieldnames = [ 'location_id', 'sex_id' ] + fieldnames
            writer = csv.DictWriter(file_obj_out, columns=fieldnames)
            writer.writeheader()
         row['location_id'] = location_id
         row['sex_id']      = sex_id
         writer.writerow(row)
      file_obj_in.close()
   file_obj_out.close()
# ------------------------------------------------------------------------------
def summary(
   result_dir         = None,
   root_node_database = None,
   fit_goal_set       = None
) :
   assert type(result_dir) == str
   assert type(root_node_database) == str
   assert type(fit_goal_set) == set
   #
   # summary_dir
   now        = datetime.datetime.now()
   month_day  = now.strftime("%m.%d")

   summary_dir = f'{result_dir}/summary/{month_day}'
   if os.path.exists(summary_dir) :
      msg  = 'The directory {summary_dir} already exists'
      msg += 'You must remove it to run another summary command today'
      assert msg, False
   else :
      os.makedirs(summary_dir)
   # error
   message_type = 'error'
   write_message_type_file(
      summary_dir, result_dir, message_type, fit_goal_set, root_node_database
   )
   #
   # warning
   message_type = 'warning'
   write_message_type_file(
      summary_dir, result_dir, message_type, fit_goal_set, root_node_database
   )
   #
   # data.csv
   root_node_name = at_cascade.get_parent_node(root_node_database)
   src = f'{result_dir}/{root_node_name}/data.csv'
   dst = f'{summary_dir}/data.csv'
   shutil.copyfile(src, dst)
   #
   # predict.csv
   combine_predict_files(
      summary_dir, result_dir, fit_goal_set, root_node_database
   )
   #
   # variable.csv
   combine_variable_files(
      summary_dir, result_dir, fit_goal_set, root_node_database
   )
