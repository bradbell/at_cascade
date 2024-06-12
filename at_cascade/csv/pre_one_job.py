# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ----------------------------------------------------------------------------
r'''
{xrst_begin csv.pre_one_job}
{xrst_spell
   boolean
   pdf
   sam
   tru
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

ancestor_node_database
**********************
This string is the location, relative to fit_dir, of the dismod_at
database for the closest ancestor fit (for this prediction).
It has been copied from the original ancestor fit directory
to the prediction directory.

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
float values in fit_predict.csv, sam_predict.csv, and tru_predict.csv;
see below.

db2csv
******
If true, the `db2csv_command`_ is used to generate the csv files
corresponding to the *ancestor_node_database* .

.. _db2csv_command: https://dismod-at.readthedocs.io/db2csv_command.html

plot
****
If this boolean is true, ``data_plot.pdf`` and ``rate_plot.pdf`` corresponding
to *ancestor_node_database* are generated (in the same directory as the
*ancestor_node_database* ).

fit_predict.csv
***************
This output file is located in the same directory as
the *ancestor_node_database* .
It contains the predictions for this prediction node at the age and time
specified by the covariate.csv file.
The predictions are done using the optimal variable values
for the parent node and sex reference in the ancestor_node_database.

sam_predict.csv
***************
This is the predictions corresponding to the posterior samples of the
variable values for the parent node and sex reference in the
ancestor_node_database.

tru_predict.csv
***************
This is the predictions corresponding to the true (simulation) values for
variable values for the prediction node and sex reference.


{xrst_end csv.pre_one_job}
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
# ancestor_node_database
# **********************
# This string is the location, relative to fit_dir, of the dismod_at
# database for an ancestor fit.
# It has been copied from the original ancestor directory
# to the pediction directory.
#
# db2csv
# ******
# If true, the `db2csv_command`_ is used to generate the csv files
# corresponding to the *ancestor_node_database* .
#
# .. _db2csv_command: https://dismod-at.readthedocs.io/db2csv_command.html
#
# plot
# ****
# If true, ``data_plot.pdf`` and ``rate_plot.pdf`` corresponding
# to *ancestor_node_database* are generated (in the same directory as the
# *ancestor_node_database* ).
#
import dismod_at
import at_cascade
import copy

def diagonse_one(
   predict_job_name       ,
   fit_dir                ,
   ancestor_node_database ,
   db2csv                 ,
   plot                   ,
) :
   assert type(predict_job_name) == str
   assert type(fit_dir) == str
   assert type(ancestor_node_database) == str
   assert type( db2csv ) == bool
   assert type( plot ) == bool
   #
   # predict_integrand_table
   predict_integrand_table = at_cascade.csv.read_table(
         f'{fit_dir}/predict_integrand.csv'
   )
   #
   # predict_node_dir
   index            = ancestor_node_database.rfind('/')
   predict_node_dir = ancestor_node_database[: index]
   #
   if db2csv :
      #
      # db2csv output files
      command = [ 'dismodat.py', ancestor_node_database, 'db2csv' ]
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
         database       = ancestor_node_database ,
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
         database       = ancestor_node_database ,
         pdf_file       = pdf_file               ,
         plot_title     = predict_job_name       ,
         rate_set       = rate_set               ,
      )
# ----------------------------------------------------------------------------

# BEGIN_DEF
# at_cascade.csv.pre_one_job
def pre_one_job(
   predict_job_name      ,
   fit_dir               ,
   sim_dir               ,
   ancestor_node_database,
   predict_node_id       ,
   predict_sex_id        ,
   all_node_database     ,
   all_covariate_table   ,
   float_precision       ,
   db2csv                ,
   plot                  ,
) :
   assert type(predict_job_name) == str
   assert type(fit_dir) == str
   assert sim_dir == None or type(sim_dir) == str
   assert type(ancestor_node_database) == str
   assert type(predict_node_id) == int
   assert type(all_node_database) == str
   assert type(all_covariate_table) == list
   assert type( all_covariate_table[0] ) == dict
   assert type( float_precision ) == int
   assert type( db2csv ) == bool
   assert type( plot ) == bool
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
   # ancestor_covariate_table, integrand_table, node_table
   ancestor_or_root = at_cascade.fit_or_root_class(
      ancestor_node_database, root_node_database
   )
   ancestor_covariate_table = ancestor_or_root.get_table('covariate')
   integrand_table          = ancestor_or_root.get_table('integrand')
   node_table               = ancestor_or_root.get_table('node')
   ancestor_or_root.close()
   #
   # ancestor_node_database
   # add the truth_var table to this database
   if type(sim_dir) == str :
      at_cascade.csv.set_truth(
         sim_dir, ancestor_node_database, root_node_database
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
   # ancestor_sex_id
   cov_info = at_cascade.get_cov_info(
      option_all_table, ancestor_covariate_table, split_reference_table
   )
   ancestor_sex_id  = cov_info['split_reference_id']
   #
   # predict_sex_value, predict_sex_name
   row               = split_reference_table[predict_sex_id]
   predict_sex_value = row['split_reference_value']
   predict_sex_name  = row['split_reference_name']
   #
   # ancestor_sex_value, ancestor_sex_name
   row            = split_reference_table[ancestor_sex_id]
   ancestor_value = row['split_reference_value']
   ancestor_name  = row['split_reference_name']
   #
   # avgint_table
   avgint_table = list()
   #
   # male_index_dict
   male_index_dict = dict()
   if predict_sex_name == 'both' :
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
      if cov_row['sex'] == predict_sex_name :
         select = True
      elif cov_row['sex'] == 'female' and predict_sex_name == 'both' :
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
         for covariate_id in range( len(ancestor_covariate_table) ) :
            #
            # covariate_name
            covariate_name = \
               ancestor_covariate_table[covariate_id]['covariate_name']
            #
            # covariate_value
            if covariate_name == 'one' :
               covariate_value = 1.0
            elif covariate_name == 'sex' :
               covariate_value = predict_sex_value
            else :
               covariate_value = float( cov_row[covariate_name] )
               if predict_sex_name == 'both' :
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
      ancestor_node_database, new = False, readonly = False
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
   index            = ancestor_node_database.rfind('/')
   predict_node_dir = ancestor_node_database[: index]
   #
   # float_format
   n_digits = str( float_precision )
   float_format = '{0:.' + n_digits + 'g}'
   #
   # prefix
   for prefix in prefix_list :
      #
      # command
      command = [ 'dismod_at', ancestor_node_database, 'predict' ]
      if prefix == 'fit' :
         command.append( 'fit_var' )
      elif prefix == 'tru' :
         command.append( 'truth_var' )
      else :
         assert prefix == 'sam'
         command.append( 'sample' )
      dismod_at.system_command_prc(command, print_command = False )
      #
      # predict_table, covariate_table
      connection    = dismod_at.create_connection(
            ancestor_node_database, new = False, readonly = True
      )
      predict_table   = dismod_at.get_table_dict(connection, 'predict')
      covariate_table = dismod_at.get_table_dict(connection, 'covariate')
      connection.close()
      #
      # sex_covariate_id
      sex_covariate_id = None
      for (covariate_id, row) in enumerate( covariate_table ) :
         if row['covariate_name'] == 'sex' :
            sex_covariate_id = covariate_id
      #
      # predict_table
      for pred_row in predict_table :
         #
         # avgint_row
         avgint_id  = pred_row['avgint_id']
         avgint_row = avgint_table[avgint_id]
         assert avgint_row['node_id'] == predict_node_id
         assert avgint_row[ f'x_{sex_covariate_id}' ] == predict_sex_value
         #
         # predict_table
         for key in avgint_row.keys() :
            pred_row[key] = avgint_row[key]
         avg_integrand             = pred_row['avg_integrand']
         pred_row['avg_integrand'] = float_format.format(avg_integrand)
         if prefix in [ 'fit', 'tru' ] :
            assert pred_row['sample_index'] == None
            del pred_row['sample_index']
         #
      #
      # prefix_predict.csv
      file_name    = f'{predict_node_dir}/{prefix}_predict.csv'
      at_cascade.csv.write_table(file_name, predict_table)
   #
   diagonse_one(
      predict_job_name  = predict_job_name ,
      fit_dir           = fit_dir ,
      ancestor_node_database = ancestor_node_database ,
      db2csv            = db2csv ,
      plot              = plot ,
   )
