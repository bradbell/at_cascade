# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
import sys
import os
import shutil
import dismod_at
import at_cascade.ihme
# ----------------------------------------------------------------------------
def display(database, max_plot) :
   #
   # pdf_file
   index      = database.rfind('/')
   pdf_dir    = database[0:index]
   #
   # plot_title
   index      = pdf_dir.rfind('/')
   plot_title = pdf_dir[index+1:]
   #
   # integrand_table, rate_table
   new             = False
   connection      = dismod_at.create_connection(database, new)
   integrand_table = dismod_at.get_table_dict(connection, 'integrand')
   rate_table      = dismod_at.get_table_dict(connection, 'rate')
   #
   # data.pdf
   pdf_file = pdf_dir + '/data.pdf'
   n_point_list = dismod_at.plot_data_fit(
      database     = database,
      pdf_file     = pdf_file,
      plot_title   = plot_title,
      max_plot     = max_plot,
   )
   #
   # rate.pdf
   rate_set = set()
   for row in rate_table :
      if not row['parent_smooth_id'] is None :
         rate_set.add( row['rate_name'] )
   pdf_file = pdf_dir + '/rate.pdf'
   plot_set = dismod_at.plot_rate_fit(
      database, pdf_file, plot_title, rate_set
   )
   #
   # db2csv
   dismod_at.system_command_prc([ 'dismodat.py', database, 'db2csv' ])
# ----------------------------------------------------------------------------
def drill(
   result_dir,
   root_node_name,
   fit_goal_set,
   root_node_database,
   no_ode_fit,
   fit_type_list,
) :
   #
   # all_node_database
   all_node_database = f'{result_dir}/all_node.db'
   #
   # cascade_root_node
   at_cascade.cascade_root_node(
      all_node_database  = all_node_database,
      root_node_database = root_node_database,
      fit_goal_set       = fit_goal_set,
      no_ode_fit         = no_ode_fit,
      fit_type_list      = fit_type_list,
   )
# ----------------------------------------------------------------------------
def main(
   result_dir              = None,
   root_node_name          = None,
   fit_goal_set            = None,
   setup_function          = None,
   max_plot                = None,
   covariate_csv_file_dict = None,
   scale_covariate_dict    = None,
   root_node_database      = None,
   no_ode_fit              = None,
   fit_type_list           = None,
   random_seed             = None,
) :
   assert type(result_dir) == str
   assert type(root_node_name) == str
   assert type(fit_goal_set) == set
   assert setup_function is not None
   assert type(max_plot) == int
   assert type(covariate_csv_file_dict) == dict
   assert type(scale_covariate_dict) == dict
   assert type(root_node_database) == str
   assert type(no_ode_fit) == bool
   assert type(fit_type_list) == list
   assert type(random_seed) == int
   #
   # command
   command_set = {
      'setup',
      'cleanup',
      'shared',
      'drill',
      'display',
      'continue',
      'predict',
      'summary',
     }
   command     = None
   if len(sys.argv) == 2 :
      if sys.argv[1] not in [ 'display', 'continue' ] :
         command = sys.argv[1]
   if len(sys.argv) == 3 :
      if sys.argv[1] in [ 'display' , 'continue' ] :
         command  = sys.argv[1]
         database = sys.argv[2]
   if command not in command_set :
      program = sys.argv[0].split('/')[-1]
      msg  = f'usage: bin/ihme/{program} command\n'
      msg += f'       bin/ihme/{program} display  database\n'
      msg += f'       bin/ihme/{program} continue database\n'
      msg +=  'where command is one of the following:\n'
      msg +=  'setup:    create at_cascade input databases from csv files\n'
      msg +=  'shared:   clear shared memory pointers\n'
      msg += f'cleanup:  remove files (not directories) in {result_dir}\n'
      msg +=  'drill:    run cascade from root node to goal nodes\n'
      msg +=  'continue: continue cascade starting at database\n'
      msg +=  'display:  results for each database at referece covariates\n'
      msg +=  'predict:  results for each database at actual covariates\n'
      msg +=  'summary:  create following files in results directory\n'
      msg +=  '          error, warning, predict.csv, variable.csv'
      sys.exit(msg)
   #
   # result_dir
   if not os.path.exists(result_dir ) :
      os.makedirs( result_dir )
   #
   # root_node_dir
   root_node_dir = f'{result_dir}/{root_node_name}'
   #
   # setup
   if command == 'setup' :
      setup_function()
      return
   #
   # cleanup
   if command == 'cleanup' :
      for name in os.listdir(result_dir) :
         file_name = f'{result_dir}/{name}'
         if os.path.isfile(file_name) or os.path.islink(file_name) :
            print( f'remove {file_name}' )
            os.remove(file_name)
   #
   # shared
   elif command == 'shared' :
      all_node_database = f'{result_dir}/all_node.db'
      at_cascade.clear_shared(all_node_database)
   #
   # drill
   elif command == 'drill' :
      dismod_at.system_command_prc([
         'dismod_at', root_node_database,
         'set', 'option', 'random_seed', str(random_seed)
      ])
      if os.path.exists( root_node_dir ) :
         program = sys.argv[0]
         msg  = f'drill: {root_node_dir} exists.\n'
         msg += 'You could remove it using the following command:\n'
         msg += f'rm -r {root_node_dir}'
         assert False, msg
      print( f'creating {root_node_dir}' )
      os.mkdir( root_node_dir )
      drill(
         result_dir,
         root_node_name,
         fit_goal_set,
         root_node_database,
         no_ode_fit,
         fit_type_list,
         )
   #
   # display or continue
   elif command in [ 'display', 'continue'] :
      if not database.startswith( root_node_name ) :
         msg  = f'{command}: database does not begin with '
         msg += f'root_node_name = {root_node_name}'
         assert False, msg
      if not database.endswith( '/dismod.db' ) :
         msg  = f'{command}: database does not end with /dismod.db'
         assert False, msg
      fit_node_database = f'{result_dir}/{database}'
      if not os.path.exists(fit_node_database) :
         msg  = f'{command}: result_dir/database = {fit_node_database}'
         msg += f'\nfile does not exist'
         assert False, msg
      if command == 'display' :
         display(fit_node_database, max_plot)
      else :
         all_node_database = f'{result_dir}/all_node.db'
         at_cascade.continue_cascade(
            all_node_database = all_node_database,
            fit_node_database = fit_node_database,
            fit_goal_set      = fit_goal_set,
            fit_type_list     = fit_type_list,
         )
   elif command == 'predict' :
      at_cascade.ihme.predict_csv(
         result_dir              = result_dir,
         covariate_csv_file_dict = covariate_csv_file_dict,
         scale_covariate_dict    = scale_covariate_dict,
         fit_goal_set            = fit_goal_set,
         root_node_database      = root_node_database,
         max_plot                = max_plot,
      )
   elif command == 'summary' :
      at_cascade.ihme.summary(
         result_dir         = result_dir,
         fit_goal_set       = fit_goal_set,
         root_node_database = root_node_database
      )
   #
   else :
      assert False
