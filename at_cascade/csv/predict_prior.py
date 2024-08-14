# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2024-06 Nate Temiquel, Garland Culbreth
# ----------------------------------------------------------------------------
import os
import dismod_at
#
#
def predict_prior(fit_dir, job_dir, predict_job_name, max_node_depth = 0):
   root_node_name = 'n0'
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
   from csv import DictWriter as csvDictWriter
   from at_cascade import table_name2id, fit_or_root_class, get_parent_node
   from at_cascade import csv
   # covariate_table
   file_name       = f'{fit_dir}/covariate.csv'
   covariate_table = csv.read_table(file_name)
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
   # fit_goal_table
   file_name      = f'{fit_dir}/fit_goal.csv'
   fit_goal_table = csv.read_table(file_name)
   for row in fit_goal_table :
      node_name = row['node_name']
      node_id   = table_name2id(node_table, 'node', node_name)
      row['node_id'] = node_id
   #
   # fit_goal_set
   fit_goal_set   = set()
   pred_node_name = predict_job_name[:2]
   start_node_id  = \
      table_name2id(node_table, 'node', pred_node_name)
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
   # split reference table
   # node_table
   connection      = dismod_at.create_connection(
      all_node_db, new = False, readonly = True
   )
   split_ref_table      = dismod_at.get_table_dict(connection, 'split_reference')
   connection.close()
   #
   # split out sex from predict job name
   sex_name = predict_job_name[3:]
   # get id from split_ref_table
   predict_sex_id = table_name2id(split_ref_table, 'split_reference', sex_name)
   # 
   # predict_one
   csv.pre_one_job(
      predict_job_name = predict_job_name,
      fit_dir = fit_dir,
      sim_dir = None,
      ancestor_node_database = f'{job_dir}/prior_pred.db',
      predict_node_id = start_node_id,
      predict_sex_id = predict_sex_id,
      all_node_database = all_node_db,
      all_covariate_table = covariate_table,
      float_precision = 4,
      db2csv = True,
      plot = False,
      zero_meas_value = False,
   )
   #
   # pre_user
   # ancestor_database
   ancestor_database = f'{job_dir}/prior_pred.db'
   #
   # ancestor_covariate_table, integrand_table
   ancestor_or_root   = fit_or_root_class(
      ancestor_database, root_node_database
   )
   ancestor_covariate_table = ancestor_or_root.get_table('covariate')
   integrand_table          = ancestor_or_root.get_table('integrand')
   ancestor_or_root.close()
   #
   # ancestor_node_name
   ancestor_node_name = get_parent_node(ancestor_database)
   #
   # ancestor_sex_name
   ancestor_sex_covariate_id = None
   for (covariate_id, row) in enumerate( ancestor_covariate_table ) :
      if row['covariate_name'] == 'sex' :
         ancestor_sex_covariate_id = covariate_id
   row = ancestor_covariate_table[ancestor_sex_covariate_id]
   ancestor_sex_value = row['reference']
   ancestor_sex_name = None
   for sex_name in csv.sex_name2value :
      if csv.sex_name2value[sex_name] == ancestor_sex_value :
         ancestor_sex_name = sex_name
   #
   # split_reference_table
   split_reference_table = csv.split_reference_table
   #
   # sex_value2name
   sex_value2name = dict()
   for row in split_reference_table :
      name  = row['split_reference_name']
      value = row['split_reference_value']
      sex_value2name[value] = name
   #
   # prefix
   prefix_list = [ 'fit', 'sam' ]
   prefix_predict_table = { 'tru':list(), 'fit':list(), 'sam':list() }
   for prefix in prefix_list :
      #
      # file_name
      file_name     = f'{job_dir}/{prefix}_predict.csv'
      if not os.path.isfile(file_name) :
         msg = f'csv.predict: Cannot find {file_name}'
         assert False, msg
      else :
         # predict_table
         predict_table = csv.read_table(file_name)
         #
         # prefix_predict_table
         for row_in in predict_table :
            # row_out
            row_out = dict()
            #
            # avgint_id
            row_out['avgint_id'] = row_in['avgint_id']
            #
            # avg_integrand
            row_out['avg_integrand'] = row_in['avg_integrand']
            #
            # sample_index
            if prefix == 'sam' :
               row_out['sample_index'] = row_in['sample_index']
            #
            # age
            assert float(row_in['age_lower'])  == float(row_in['age_upper'])
            row_out['age']  = row_in['age_lower']
            #
            # time
            assert float(row_in['time_lower']) == float(row_in['time_upper'])
            row_out['time'] = row_in['time_lower']
            #
            # node_name
            node_id              = int( row_in['node_id'] )
            row_out['node_name'] = node_table[node_id]['node_name']
            assert node_id == start_node_id
            #
            # fit_node_name
            row_out['fit_node_name'] = ancestor_node_name
            #
            # fit_sex
            row_out['fit_sex'] = ancestor_sex_name
            #
            # integrand_name
            integrand_id  = int( row_in['integrand_id'] )
            row_out['integrand_name'] = \
               integrand_table[integrand_id]['integrand_name']
            #
            # covariate_name
            # for each covariate in predict_table
            for (i_cov, cov_row) in enumerate( ancestor_covariate_table ) :
               covariate_name = cov_row['covariate_name']
               covariate_key  = f'x_{i_cov}'
               cov_value      = float( row_in[covariate_key] )
               if covariate_name == 'sex' :
                  row_tmp   = split_reference_table[predict_sex_id]
                  assert cov_value == row_tmp['split_reference_value']
                  cov_value = sex_value2name[cov_value]
               row_out[covariate_name] = cov_value
            #
            # prefix_predict_table
            prefix_predict_table[prefix].append( row_out )
            #
   #
   # prefix_predict.csv
   for prefix in prefix_list :
      file_name    = f'{fit_dir}/{prefix}_predict.csv'
      if (os.path.exists(file_name)):
         new_file = False
      else:
         new_file = True
      file_out     = open(file_name, 'a')
      writer       = None
      for row in prefix_predict_table[prefix]:
         if writer == None :
            writer = csvDictWriter(file_out, fieldnames = row.keys() )
            if new_file:
               writer.writeheader()
         writer.writerow(row)
      file_out.close()
         



