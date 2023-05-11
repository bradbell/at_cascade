# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-23 Bradley M. Bell
# ----------------------------------------------------------------------------
def set_truth(sim_dir, fit_node_database) :
   assert type(sim_dir) == str
   assert type(fit_node_database) == str
   #
   # fit_table
   connection = dismod_at.create_connection(
      fit_node_database, new = False, readonly = True
   )
   fit_table = dict()
   for table_name in [
      'age', 'covariate', 'integrand', 'node', 'rate', 'time', 'var'
   ] :
      fit_table[table_name] = dismod_at.get_table_dict(connection, table_name)
   connection.close()
   #
   # fit_node_name
   fit_node_name = at_cascade.get_parent_node(fit_node_database)
   fit_node_id   = at_cascade.table_name2id(
      table    = fit_table['node'] ,
      tbl_name = 'node'            ,
      row_name = fit_node_name     ,
   )
   #
   # sex_value
   sex_value = None
   for row in fit_table['covariate'] :
      if row['covariate_name'] == 'sex' :
         sex_value = float( row['reference'] )
   assert sex_value != None
   #
   # sex_name
   sex_name = None
   for key in at_cascade.csv.sex_name2value :
      if at_cascade.csv.sex_name2value[key] == sex_value :
         sex_name = key
   assert sex_name != None
   #
   # rate2integrand
   rate2integrand = {
      'pini'  : 'prevalence' ,
      'iota'  : 'Sincidence' ,
      'rho'   : 'remission'  ,
      'chi'   : 'mtexcess'   ,
      'omega' : 'mtother'    ,
   }
   #
   # simulation_table, var_id2simulation_id
   simulation_table        = list()
   var_id2simulation_id    = list()
   simulation_id           = -1
   for var_row in fit_table['var'] :
      #
      # var_type
      var_type  = var_row['var_type']
      assert not var_type.startswith('mulstd_')
      assert not var_type.startswith('mulcov_meas_')
      #
      if var_type != 'rate' :
         var_id2simulation_id.append( 'None' )
      else :
         # node_name
         node_name      = fit_table['node'][ var_row['node_id'] ]['node_name']
         if node_name != fit_node_name :
            var_id2simulation_id.append( 'None' )
         else :
            #
            # age, time, rate_name
            age       = fit_table['age'][  var_row['age_id']  ]['age']
            time      = fit_table['time'][ var_row['time_id'] ]['time']
            rate_name = fit_table['rate'][ var_row['rate_id'] ]['rate_name']
            #
            # age
            if rate_name == 'pini' :
               age = fit_table['age'][0]['age']
               # This is really OK, just want a heads up in this case
               assert age == 0.0
            #
            simulation_id += 1
            integrand_name = rate2integrand[ 'rate_name']
            sim_row = {
               'simulation_id'  : simulation_id  ,
               'integrand_name' : integrand_name ,
               'node_name'      : node_name      ,
               'sex'            : sex_name       ,
               'age_lower'      : age            ,
               'age_upper'      : age            ,
               'time_lower'     : time           ,
               'time_upper'     : time           ,
               'meas_std_cv'    : 0.0            ,
               'meas_std_min'   : 1.0            ,
            }
            simulation_table.append( sim_row )
            var_id2simulation_id.append( simulation_id )
   assert len( fit_table['var'] ) == len( var_id2simulation_id )
   #
   # save_list
   save_list = [ 'simulation', 'option_sim_out', 'random_effects', 'data_sim' ]
   #
   # save files
   for name in save_list :
         src = f'{sim_dir}/{name}.csv'
         dst = f'{sim_dir}/save.{name}.csv'
         os.rename(src, dst)
   #
   # simulation.csv
   at_cascade.csv.write_table(
      file_name = f'{sim_dir}/simulation.csv' ,
      table     = simulation_table
   )
   at_cascade.csv.simulate(sim_dir)
   #
   # sim_table
   sim_table = dict()
   for table_name in [ 'data_sim', 'multiplier_sim' ] :
      file_name             = f'{sim_dir}/{table_name}.csv'
      sim_table[table_name] = at_cascade.csv.read_table(file_name)
   #
   # turth_var_table
   truth_var_table = list()
   for (var_id, var_row) in enumerate( fit_table['var'] ) :
      #
      # truth_var_value
      truth_var_value = None
      #
      # simulation_id
      simulation_id = var_id2simulation_id[var_id]
      if simulation_id != None :
         # this is a fixed effect rate value
         truth_var_value = sim_table['data_sim'][simulation_id]['meas_mean']
      else :
         #
         # var_type, age_id, time_id
         var_type     = var_row['var_type']
         age_id       = var_row['age_id']
         time_id      = var_row['time_id']
         integrand_id = var_row['integrand_id']
         covariate_id = var_row['covariate_id']
         assert age_id == 0
         assert time_id == 0
         #
         if var_type == 'rate' :
            # this is a random effect rate value
            truth_var_value = 0.0
         elif var_type == 'mulcov_rate_value' :
            rate_name      = fit_table['rate'][rate_id]['rate_name']
            covariate_name = \
               fit_table['covariate'][covariate_id]['covariate_name']
            for row in sim_table['multiplier_sim'] :
               if row['rate_name'] == rate_name :
                  if row['covariate_or_sex'] == covariate_name :
                     truth_var_value = row['multiplier_truth']
      assert truth_var_value != None
      truth_var_table.append(truth_var_value)
   #
   # restore files
   for name in save_list :
         src = f'{sim_dir}/save.{name}.csv'
         dst = f'{sim_dir}/{name}.csv'
         os.remove(dst)
         os.rename(src, dst)
   #
   # fit_node_database
   # add the truth_var table
   connection = dismod_at.create_connection(
      fit_node_database, new = False, readonly = False
   )
   dismod_at.replace_table(
         connection, table_name = 'truth_var', table_dict = truth_var_table
   )
