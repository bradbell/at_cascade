# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-23 Bradley M. Bell
# ----------------------------------------------------------------------------
r'''
{xrst_begin csv.predict_one}
{xrst_spell
   boolean
   pdf
}

Calculate the predictions for One Fit
#####################################

Prototype
*********
{xrst_literal
   # BEGIN_DEF
   # END_DEF
}

predict_job_name
****************
This string specifies the node and sex corresponding to this prediction.

fit_dir
*******
This string is the directory name where the input and output csv files
are located.

sim_dir
*******
is the directory name where the csv simulation files are located.

predict_node_database
*********************
This string is the location, relative to fit_dir, of the dismod_at
database for a fit.

predict_node_id
***************
This int is the node_id in the node we are predicting for.

all_node_database
*****************
This string is the all node database for this fit.

all_covariate_table
*******************
The list of dict is the in memory representation of the
covariate.csv file

float_precision
***************
This is the number of decimal digits of precision to include for
float values in the fit_predict.csv file.

db2csv
******
If true, the `db2csv_command`_ is used to generate the csv files
corresponding to the *predict_node_database* .

.. _db2csv_command: https://dismod-at.readthedocs.io/db2csv_command.html

plot
****
If this boolean is true, ``data_plot.pdf`` and ``rate_plot.pdf`` corresponding
to *predict_node_database* are generated (in the same directory as the
*predict_node_database* ).

fit_predict.csv
***************
This output file is located in the same directory as
the *predict_node_database* .
It contains the predictions for this fit node at the age and time
specified by the covariate.csv file.
The predictions are done using the optimal variable values
for the parent node and sex reference in the predict_node_database.


{xrst_end csv.predict_one}
r'''
import dismod_at
import at_cascade
import copy
#
# ----------------------------------------------------------------------------
# Create Diagonsitcs for One Fit
# ##############################
#
# predict_job_name
# ****************
# This string specifies the node and sex corresponding to this fit.
#
# fit_dir
# *******
# This string is the directory name where the input and output csv files
# are located.
#
# predict_node_database
# *********************
# This string is the location, relative to fit_dir, of the dismod_at
# database for a fit.
#
# db2csv
# ******
# If true, the `db2csv_command`_ is used to generate the csv files
# corresponding to the *predict_node_database* .
#
# .. _db2csv_command: https://dismod-at.readthedocs.io/db2csv_command.html
#
# plot
# ****
# If this boolean is true, ``data_plot.pdf`` and ``rate_plot.pdf`` corresponding
# to *predict_node_database* are generated (in the same directory as the
# *predict_node_database* ).
#
import dismod_at
import at_cascade
import copy

def diagonse_one(
   predict_job_name      ,
   fit_dir               ,
   predict_node_database ,
   db2csv                ,
   plot                  ,
) :
   assert type(predict_job_name) == str
   assert type(fit_dir) == str
   assert type(predict_node_database) == str
   #
   # predict_integrand_table
   predict_integrand_table = at_cascade.csv.read_table(
         f'{fit_dir}/predict_integrand.csv'
   )
   #
   # predict_node_dir
   index            = predict_node_database.rfind('/')
   predict_node_dir = predict_node_database[: index]
   #
   if db2csv :
      #
      # db2csv output files
      command = [ 'dismodat.py', predict_node_database, 'db2csv' ]
      dismod_at.system_command_prc(
         command, print_command = False, return_stdout = True
      )
   #
   if plot :
      #
      # data_plot.pdf
      pdf_file       = f'{predict_node_dir}/data_plot.pdf'
      integrand_list = list()
      for row in predict_integrand_table :
         integrand_name = row['integrand_name']
         if not integrand_name.startswith('mulcov_') :
            integrand_list.append( integrand_name )
      dismod_at.plot_data_fit(
         database       = predict_node_database  ,
         pdf_file       = pdf_file               ,
         plot_title     = predict_job_name       ,
         max_plot       = 1000                   ,
         integrand_list = integrand_list         ,
      )
      #
      # rate_plot.pdf
      pdf_file = f'{predict_node_dir}/rate_plot.pdf'
      rate_set = { 'pini', 'iota', 'chi', 'omega' }
      dismod_at.plot_rate_fit(
         database       = predict_node_database  ,
         pdf_file       = pdf_file               ,
         plot_title     = predict_job_name       ,
         rate_set       = rate_set               ,
      )
# ----------------------------------------------------------------------------

# BEGIN_DEF
def predict_one(
   predict_job_name      ,
   fit_dir               ,
   sim_dir               ,
   predict_node_database ,
   predict_node_id       ,
   all_node_database     ,
   all_covariate_table   ,
   float_precision       ,
   db2csv                ,
   plot                  ,
) :
   assert type(predict_job_name) == str
   assert type(fit_dir) == str
   assert sim_dir == None or type(sim_dir) == str
   assert type(predict_node_database) == str
   assert type(predict_node_id) == int
   assert type(all_node_database) == str
   assert type(all_covariate_table) == list
   assert type( all_covariate_table[0] ) == dict
   assert type( float_precision ) == int
   # END_DEF
   #
   # option_all_table
   connection       = dismod_at.create_connection(
      all_node_database, new = False, readonly = True
   )
   option_all_table = dismod_at.get_table_dict(connection, 'option_all')
   connection.close()
   #
   # root_node_database
   root_node_database = None
   for row in option_all_table :
      if row['option_name'] == 'root_node_database' :
         root_node_database = row['option_value']
   assert root_node_database != None
   #
   # predict_covariate_table, integrand_table, node_table
   pedict_or_root = at_cascade.fit_or_root_class(
      predict_node_database, root_node_database
   )
   predict_covariate_table = pedict_or_root.get_table('covariate')
   integrand_table         = pedict_or_root.get_table('integrand')
   node_table              = pedict_or_root.get_table('node')
   pedict_or_root.close()
   #
   # predict_node_database
   # add the truth_var table to this database
   if type(sim_dir) == str :
      at_cascade.csv.set_truth(
         sim_dir, predict_node_database, root_node_database
      )
   #
   # integrand_id_list
   predict_integrand_table = at_cascade.csv.read_table(
         f'{fit_dir}/predict_integrand.csv'
   )
   integrand_id_list = list()
   for row in predict_integrand_table :
      integrand_id = at_cascade.table_name2id(
         integrand_table, 'integrand', row['integrand_name']
      )
      integrand_id_list.append( integrand_id )
   #
   # predict_node_name
   predict_node_name = node_table[predict_node_id]['node_name']
   #
   # split_reference_table
   split_reference_table = at_cascade.csv.split_reference_table
   #
   # fit_split_reference_id
   cov_info = at_cascade.get_cov_info(
      option_all_table, predict_covariate_table, split_reference_table
   )
   fit_split_reference_id  = cov_info['split_reference_id']
   #
   # sex_value
   row       = split_reference_table[fit_split_reference_id]
   sex_value = row['split_reference_value']
   sex_name  = row['split_reference_name']
   #
   # avgint_table
   avgint_table = list()
   #
   # male_index_dict
   male_index_dict = dict()
   if sex_name == 'both' :
      for (i_row, row) in enumerate(all_covariate_table) :
         if row['node_name'] == predict_node_name :
            sex  = row['sex']
            age  = float( row['age'] )
            time = float( row['time'] )
            if sex == 'male' :
               if age not in male_index_dict :
                  male_index_dict[age] = dict()
               if time not in male_index_dict[age] :
                  male_index_dict[age][time] = i_row
   #
   # cov_row
   for cov_row in all_covariate_table :
      #
      # select
      if cov_row['sex'] == sex_name :
         select = True
      elif cov_row['sex'] == 'female' and sex_name == 'both' :
         select = True
      else :
         select = False
      select = select and cov_row['node_name'] == predict_node_name
      if select :
         #
         # avgint_row
         age  = float( cov_row['age'] )
         time = float( cov_row['time'] )
         avgint_row = {
            'node_id'         : predict_node_id,
            'subgroup_id'     : 0,
            'weight_id'       : None,
            'age_lower'       : age,
            'age_upper'       : age,
            'time_lower'      : time,
            'time_upper'      : time,
         }
         #
         # covariate_id
         for covariate_id in range( len(predict_covariate_table) ) :
            #
            # covariate_name
            covariate_name = \
               predict_covariate_table[covariate_id]['covariate_name']
            #
            # covariate_value
            if covariate_name == 'one' :
               covariate_value = 1.0
            elif covariate_name == 'sex' :
               covariate_value = sex_value
            else :
               covariate_value = float( cov_row[covariate_name] )
               if sex_name == 'both' :
                  male_row  = all_covariate_table[ male_index_dict[age][time] ]
                  assert male_row['sex'] == 'male'
                  assert cov_row['sex']  == 'female'
                  covariate_value += float( male_row[covariate_name] )
                  covariate_value /= 2.0
            #
            # avgint_row
            key = f'x_{covariate_id}'
            avgint_row[key] = covariate_value
         #
         # integrand_id
         for integrand_id in integrand_id_list :
            avgint_row['integrand_id'] = integrand_id
            avgint_table.append( copy.copy( avgint_row ) )
   #
   # connection
   connection = dismod_at.create_connection(
      predict_node_database, new = False, readonly = False
   )
   #
   # avgint table
   dismod_at.replace_table(connection, 'avgint', avgint_table)
   #
   # prefix_list
   prefix_list = list()
   if at_cascade.table_exists(connection, 'fit_var') :
      prefix_list.append( 'fit' )
   if at_cascade.table_exists(connection, 'sample') :
      prefix_list.append( 'sam' )
   if sim_dir != None :
      prefix_list.append( 'tru' )
   connection.close()
   #
   # predict_node_dir
   index            = predict_node_database.rfind('/')
   predict_node_dir = predict_node_database[: index]
   #
   # float_format
   n_digits = str( float_precision )
   float_format = '{0:.' + n_digits + 'g}'
   #
   # prefix
   for prefix in prefix_list :
      #
      # command
      command = [ 'dismod_at', predict_node_database, 'predict' ]
      if prefix == 'fit' :
         command.append( 'fit_var' )
      elif prefix == 'tru' :
         command.append( 'truth_var' )
      else :
         assert prefix == 'sam'
         command.append( 'sample' )
      dismod_at.system_command_prc(command, print_command = False )
      #
      # predict_table
      connection    = dismod_at.create_connection(
            predict_node_database, new = False, readonly = True
      )
      predict_table = dismod_at.get_table_dict(connection, 'predict')
      connection.close()
      for pred_row in predict_table :
         avgint_id  = pred_row['avgint_id']
         avgint_row = avgint_table[avgint_id]
         for key in avgint_row.keys() :
            pred_row[key] = avgint_row[key]
         avg_integrand             = pred_row['avg_integrand']
         pred_row['avg_integrand'] = float_format.format(avg_integrand)
         if prefix in [ 'fit', 'tru' ] :
            assert pred_row['sample_index'] == None
            del pred_row['sample_index']
      #
      # prefix_predict.csv
      file_name    = f'{predict_node_dir}/{prefix}_predict.csv'
      at_cascade.csv.write_table(file_name, predict_table)
   #
   diagonse_one(
      predict_job_name  = predict_job_name ,
      fit_dir           = fit_dir ,
      predict_node_database = predict_node_database ,
      db2csv            = db2csv ,
      plot              = plot ,
   )
