# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ----------------------------------------------------------------------------
r'''
{xrst_begin csv.pre_one_job}
{xrst_spell
   pdf
   sam
   tru
   avgint
   avg
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

pre_database
************
The directory where *pre_database* is located identifies the
node and sex for this prediction.
The file *pre_database* is a copy of the fit database used for this prediction.
The node and sex for the fit is either the same as for the prediction,
or an ancestor of the node and ex for the prediction.

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

fit_same_as_predict
*******************
If true, the node and sex for this prediction is the same
as the node and sex for the fit.
Otherwise it is a fit for the closest ancestor that has a
successful cascade fit.
To be specific, ``sample: OK`` is in its
:ref:`fit_one_job@fit_database@log`.

db2csv
******
If fit_same_as_predict and db2csv,
the `db2csv_command`_ is used to generate the csv files
corresponding to the *pre_database* .

.. _db2csv_command: https://dismod-at.readthedocs.io/db2csv_command.html

plot
****
If fit_same_as_predict and plot,
``data_plot.pdf`` and ``rate_plot.pdf`` corresponding
to *pre_database* are generated, in the same directory as *pre_database* ;
i.e., the prediction directory

Csv Output Files
****************
#. The csv output files are located in the prediction directory; i.e.,
   the directory corresponding to the predictions for this location, sex.
#. The predictions are on the same age, time grid as the covariate file.
#. If *fit_same_as_predict* is true, the following files are created
   (the tru_posterior.csv file is not created when *sim_dir* is None):

   .. csv-table::

      fit_posterior.csv, uses optimal posterior variable values
      sam_posterior.csv, uses samples from the posterior
      tru_posterior.csv, uses simulation variable values for this location,sex

#. If *fit_same_as_predict* is false, the following files are created
   (the tru_prior.csv file is not created when *sim_dir* is None):

   .. csv-table::

      fit_prior.csv,     uses optimal prior variable values
      sam_prior.csv,     uses samples from the prior
      tru_prior.csv,     uses simulation variable values for an ancestor


#. The following columns are included in these files
   (the sample_index column is only included in the sample files):

   .. csv-table::
      :header-rows: 1

      Column,        Meaning
      avgint_id,     This index the value we are predicting
      sample_index,  This index the random samples for each value
      avg_integrand, This is the model value for the prediction
      age_lower,     Lower age limit for averaging this integrand
      age_upper,     Upper age limit for averaging (must equal lower).
      time_lower,    Lower time limit for averaging this integrand
      time_upper,    Upper time limit for averaging (must equal lower).
      node_id,       Identifies the node for this prediction.
      x_j,           Value of the j-th covariate

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
# pre_database
# ************
# This string is the location, relative to fit_dir, of the dismod_at
# database for a fit.
# It must be located in the pediction directory.
#
# fit_same_as_predict
# *******************
# if true, the the fit location,sex is same as prediction location,sex.
#
# db2csv
# ******
# If fit_same_as_predict and db2csv,
# the `db2csv_command`_ is used to generate the csv files
# corresponding to the *pre_database* .
#
# .. _db2csv_command: https://dismod-at.readthedocs.io/db2csv_command.html
#
# plot
# ****
# If fit_same_as_predict and plot,
# ``data_plot.pdf`` and ``rate_plot.pdf`` corresponding
# to *pre_database* are generated, in the same directory as the
# *pre_database* ; i.e., the prediction directory.
#
import dismod_at
import at_cascade
import copy

def diagonse_one(
   predict_job_name       ,
   fit_dir                ,
   pre_database           ,
   fit_same_as_predict    ,
   db2csv                 ,
   plot                   ,
) :
   assert type(predict_job_name) == str
   assert type(fit_dir) == str
   assert type(pre_database) == str
   assert type( fit_same_as_predict ) == bool
   assert type( db2csv ) == bool
   assert type( plot ) == bool
   #
   # predict_integrand_table
   predict_integrand_table = at_cascade.csv.read_table(
         f'{fit_dir}/predict_integrand.csv'
   )
   #
   # predict_node_dir
   index            = pre_database.rfind('/')
   predict_node_dir = pre_database[: index]
   #
   if fit_same_as_predict and db2csv :
      #
      # db2csv output files
      command = [ 'dismodat.py', pre_database, 'db2csv' ]
      dismod_at.system_command_prc(
         command, print_command = False, return_stdout = True
      )
   if fit_same_as_predict and plot :
      #
      # data_plot.pdf
      pdf_file       = f'{predict_node_dir}/data_plot.pdf'
      integrand_list = list()
      for row in predict_integrand_table :
         integrand_name = row['integrand_name']
         if not integrand_name.startswith('mulcov_') :
            integrand_list.append( integrand_name )
      dismod_at.plot_data_fit(
         database       = pre_database           ,
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
         database       = pre_database           ,
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
   pre_database          ,
   predict_node_id       ,
   predict_sex_id        ,
   all_node_database     ,
   all_covariate_table   ,
   float_precision       ,
   fit_same_as_predict   ,
   db2csv                ,
   plot                  ,
   zero_meas_value       ,
) :
   assert type(predict_job_name) == str
   assert type(fit_dir) == str
   assert sim_dir == None or type(sim_dir) == str
   assert type(pre_database) == str
   assert type(predict_node_id) == int
   assert type(all_node_database) == str
   assert type(all_covariate_table) == list
   assert type( all_covariate_table[0] ) == dict
   assert type( float_precision ) == int
   assert type( fit_same_as_predict ) == bool
   assert type( db2csv ) == bool
   assert type( plot ) == bool
   assert type( zero_meas_value) == bool
   # END_DEF
   #
   # option_all_table
   connection       = dismod_at.create_connection(
      all_node_database, new = False, readonly = True
   )
   option_all_table = dismod_at.get_table_dict(connection, 'option_all')
   connection.close()
   #
   # root_database
   root_database      = None
   for row in option_all_table :
      if row['option_name'] == 'root_database' :
         root_database      = row['option_value']
   assert root_database != None
   #
   # fit_covariate_table, integrand_table, node_table
   fit_or_root = at_cascade.fit_or_root_class(
      pre_database, root_database
   )
   fit_covariate_table      = fit_or_root.get_table('covariate')
   integrand_table          = fit_or_root.get_table('integrand')
   node_table               = fit_or_root.get_table('node')
   fit_or_root.close()
   #
   # pre_database
   # add the truth_var table to this database
   if type(sim_dir) == str :
      at_cascade.csv.set_truth(
         sim_dir, pre_database, root_database
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
   # predict_sex_value, predict_sex_name
   row               = split_reference_table[predict_sex_id]
   predict_sex_value = row['split_reference_value']
   predict_sex_name  = row['split_reference_name']
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
         for covariate_id in range( len(fit_covariate_table) ) :
            #
            # covariate_name
            covariate_name = \
               fit_covariate_table[covariate_id]['covariate_name']
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
      pre_database, new = False, readonly = False
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
   # suffix
   if fit_same_as_predict :
      suffix = 'posterior'
   else :
      suffix = 'prior'
   #
   # predict_node_dir
   index            = pre_database.rfind('/')
   predict_node_dir = pre_database[: index]
   #
   # float_format
   n_digits = str( float_precision )
   float_format = '{0:.' + n_digits + 'g}'
   #
   # prefix
   for prefix in prefix_list :
      #
      # command
      command = [ 'dismod_at', pre_database, 'predict' ]
      if prefix == 'fit' :
         command.append( 'fit_var' )
      elif prefix == 'tru' :
         command.append( 'truth_var' )
      else :
         assert prefix == 'sam'
         command.append( 'sample' )
      if zero_meas_value :
         command.append( 'zero_meas_value' )
      dismod_at.system_command_prc(command, print_command = False )
      #
      # predict_table, covariate_table
      connection    = dismod_at.create_connection(
            pre_database, new = False, readonly = True
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
      # prefix_suffix.csv
      file_name    = f'{predict_node_dir}/{prefix}_{suffix}.csv'
      at_cascade.csv.write_table(file_name, predict_table)
   #
   diagonse_one(
      predict_job_name     = predict_job_name ,
      fit_dir              = fit_dir ,
      pre_database         = pre_database ,
      fit_same_as_predict  = fit_same_as_predict ,
      db2csv               = db2csv ,
      plot                 = plot ,
   )
