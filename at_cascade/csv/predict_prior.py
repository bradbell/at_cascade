# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2024-06 Nate Temiquel, Garland Culbreth
# ----------------------------------------------------------------------------
import os
import dismod_at
#
#
def predict_prior(fit_dir):
   # job_dir
   job_dirs = [f'{fit_dir}/n0',
               f'{fit_dir}/n0/male/n1',
               f'{fit_dir}/n0/male/n2',
               f'{fit_dir}/n0/female/n1',
               f'{fit_dir}/n0/female/n2']
   job_list = ['n0.both',
               'n1.male',
               'n2.male',
               'n1.female',
               'n2.female']
   #
   root_node_name = 'n0'
   max_node_depth = None
   for job_dir in job_dirs :
      # prior_pred.db
      command = [ 'cp', f'{job_dir}/dismod.db', f'{job_dir}/prior_pred.db' ]
      dismod_at.system_command_prc(command)
      # prior_connect
      prior_connect = dismod_at.create_connection(
         file_name = f'{job_dir}/prior_pred.db' ,
         new       = False ,
         readonly  = False ,
      )
      # option_table
      option_table = dismod_at.get_table_dict(prior_connect, tbl_name = 'option')
      for row in option_table :
         if row['option_name'] == 'other_input_table' :
            option_value = ' ' + row['option_value'] + ' '
            row['option_value'] = option_value.replace( ' data ', ' ' )
      # prior_pred.db: option_table
      dismod_at.replace_table(
         prior_connect,
         tbl_name   = 'option',
         table_dict = option_table,
      )
      # data_table
      connection = dismod_at.create_connection(
         file_name = f'{fit_dir}/root_node.db' ,
         new       = False ,
         readonly  = True  ,
      )
      data_table = dismod_at.get_table_dict(connection, tbl_name = 'data')
      connection.close()
      # col_name, col_type
      row      = data_table[0]
      col_name = list()
      col_type = list()
      for key in row :
         python_type = type( row[key] )
         sql_type = None
         if python_type == str :
            sql_type = 'text'
         elif python_type == int :
            sql_type = 'integer'
         elif python_type == float :
            sql_type = 'real'
         elif row[key] == None :
            if key in [ 'weight_id', 'sample_size' ] :
               sql_type = 'integer'
            elif key in [ 'eta', 'nu' ] :
               sql_type = 'real'
         if sql_type == None :
            assert False, f'key = {key}, python_type = {python_type}'
         #
         col_name.append(key)
         col_type.append(sql_type)
      # prior_pred.db: data_table
      dismod_at.create_table(
         connection = prior_connect ,
         tbl_name   = 'data'        ,
         col_name   = col_name      ,
         col_type   = col_type      ,
         row_list   = list()        ,
      )
      # prior_connect
      prior_connect.close()
      #
      # prior_pred.db: init
      command  = [ 'dismod_at', f'{job_dir}/prior_pred.db', 'init' ]
      sigma    = '.3'
      database = f'{job_dir}/prior_pred.db'
      dismod_at.system_command_prc(command)
      for tbl_name in [ 'scale_var', 'start_var' ] :
         command = [ 'dismodat.py', database, 'perturb', tbl_name, sigma ]
         dismod_at.system_command_prc(command)
      # prior_pred.db: fit
      command = [ 'dismod_at', database, 'fit' , 'both' ]
      dismod_at.system_command_prc(command)
      # prior_pred.db sample
      command = [ 'dismod_at', database, 'sample' , 'asymptotic', 'both', '20' ]
      dismod_at.system_command_prc(command)
   # ****************************************************************************
   # Prediction pipeline variables **********************************************
   # ****************************************************************************
   from at_cascade import create_job_table, table_name2id
   from at_cascade.csv import read_table, pre_one_job
   # covariate_table
   file_name       = f'{fit_dir}/covariate.csv'
   covariate_table = read_table(file_name)
   # 
   # all_node_db
   all_node_db = f'{fit_dir}/all_node.db'
   #
   # root_node_database
   root_node_database = f'{fit_dir}/root_node.db'
   #
   # node_table
   connection      = dismod_at.create_connection(
      root_node_database, new = False, readonly = True
   )
   node_table      = dismod_at.get_table_dict(connection, 'node')
   connection.close()
   #
   # root_node_id
   root_node_id = table_name2id(
      node_table, 'node', root_node_name
   )
   # 
   # root_split_reference_id
   root_split_reference_id = 0 # hardcode for test
   #
   # fit_goal_table
   file_name      = f'{fit_dir}/fit_goal.csv'
   fit_goal_table = read_table(file_name)
   for row in fit_goal_table :
      node_name = row['node_name']
      node_id   = table_name2id(node_table, 'node', node_name)
      row['node_id'] = node_id
   #
   # fit_goal_set
   fit_goal_set   = set()
   start_node_id  = \
      table_name2id(node_table, 'node', root_node_name)
   for row in fit_goal_table :
      node_id   = row['node_id']
      node_list = [ node_id ]
      while node_id != start_node_id and node_id != None :
         node_id   = node_table[node_id]['parent']
         if node_id != None :
            node_list.append( node_id )
      if node_id == start_node_id :
         if max_node_depth == None :
            node_id   = node_list[0]
         elif len(node_list) <= max_node_depth + 1 :
            node_id   = node_list[0]
         else :
            node_id  = node_list[-max_node_depth - 1]
         node_name = node_table[node_id]['node_name']
         fit_goal_set.add( node_name )
   #
   # job table
   job_table = create_job_table(
      all_node_database          = all_node_db              ,
      node_table                 = node_table               ,
      start_node_id              = root_node_id             ,
      start_split_reference_id   = root_split_reference_id  ,
      fit_goal_set               = fit_goal_set             ,
   )
   # 
   # predict for prior
   for i in range(len(job_table)) :
      # predict_job_name, predict_node_id, predict_sex_id
      predict_job_row         = job_table[i]
      predict_job_name        = predict_job_row['job_name']
      predict_node_id         = predict_job_row['fit_node_id']
      predict_sex_id          = predict_job_row['split_reference_id']
      #
      # predict_one
      pre_one_job(
         predict_job_name = predict_job_name,
         fit_dir = fit_dir,
         sim_dir = None,
         ancestor_node_database = f'{job_dirs[i]}/prior_pred.db',
         predict_node_id = predict_node_id,
         predict_sex_id = predict_sex_id,
         all_node_database = all_node_db,
         all_covariate_table = covariate_table,
         float_precision = 4,
         db2csv = True,
         plot = False,
         zero_meas_value = False,
      )
