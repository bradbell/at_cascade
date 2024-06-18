import os
import dismod_at


def predict_prior(fit_dir):
   # job_dir
   job_dir = f'{fit_dir}/n0'
   
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
   
   # finish with success message
   print('predict_prior.py: OK')
