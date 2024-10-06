# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ----------------------------------------------------------------------------
r'''
{xrst_begin csv.pre_user}
{xrst_spell
   tru
   sam
}

Convert Prediction Csv Files From dismod_at Notation to User csv.fit Notation
#############################################################################

Prototype
*********
{xrst_literal
   # BEGIN DEF
   # END DEF
}

fit_dir
*******
Same as the csv fit :ref:`csv.fit@fit_dir` .

sim_dir
*******
Same as :ref:`csv.predict@sim_dir` .

job_table
*********
is the :ref:`create_job_table@job_table` for this cascade.

start_job_name
**************
Is the name of the job (fit) that the predictions start at.
This is a node name, followed by a period, followed by a sex.
Only this fit, and its descendents, were included in the predictions.
If this argument is None, all of the jobs (fits) were be included.

predict_job_id_list
*******************
Each element of this list is an index in the *job_table*
of a job that was included in the predictions.

node_table
**********
is the dismod_at node table for this cascade.

root_node_id
************
is the node table id for the root node of the cascade.

root_split_reference_id
***********************
is the split_reference table id for the root job of the cascade

root_database
*************
specifies the location of the dismod_at
:ref:`glossary@root_database`.

Input Prediction Files
**********************
Each job in the *predict_job_id_list* has a corresponding directory.
For prefix equal to ``fit`` , ``sam`` ,
the file *prefix*\ _prior.csv or *prefix\ _posterior.csv
must exist in each of these directories
( see :ref:`pre_one_job@Csv Output Files` ).
In addition if *sim_dir* is not None,
the file tru_prior.csv or true_posterior.csv
must also exist. These files use dismod_at notation.

Output Prediction Files
***********************
The predictions get converted to csv.predict notation; see
:ref:`csv.predict@Output Files` .

{xrst_end csv.pre_user}
'''
import os
import dismod_at
import at_cascade
# ----------------------------------------------------------------------------
def assert_is_table(table) :
   assert type(table) == list
   if len(table) > 0 :
      assert type( table[0] ) == dict
# ----------------------------------------------------------------------------
# user_predict_table = predict_table_dismod2user( .. )
# Note that we are only using covarigte_table for the mapping from
# covariate indices to names so use any dismod covariate table works.
def predict_table_dismod2user(
   predict_table,
   node_table,
   integrand_table,
   covariate_table,
   split_reference_table,
   sex_value2name,
   fit_node_name,
   fit_sex_name,
   predict_node_id,
   predict_sex_id,
) :
   assert_is_table(predict_table)
   assert_is_table(node_table)
   assert_is_table(integrand_table)
   assert_is_table(covariate_table)
   assert_is_table(split_reference_table)
   assert type(sex_value2name) == dict
   assert type(fit_node_name) == str
   assert type(fit_sex_name) == str
   assert type(predict_node_id) == int
   assert type(predict_sex_id) == int
   #
   # user_predict_table
   user_predict_table = list()
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
      if 'sample_index' in row_in :
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
      assert node_id == predict_node_id
      #
      # fit_node_name
      row_out['fit_node_name'] = fit_node_name
      #
      # fit_sex
      row_out['fit_sex'] = fit_sex_name
      #
      # integrand_name
      integrand_id  = int( row_in['integrand_id'] )
      row_out['integrand_name'] = \
         integrand_table[integrand_id]['integrand_name']
      #
      # covariate_name
      # for each covariate in predict_table
      for (i_cov, cov_row) in enumerate( covariate_table ) :
         covariate_name = cov_row['covariate_name']
         covariate_key  = f'x_{i_cov}'
         cov_value      = float( row_in[covariate_key] )
         if covariate_name == 'sex' :
            row_tmp   = split_reference_table[predict_sex_id]
            assert cov_value == row_tmp['split_reference_value']
            cov_value = sex_value2name[cov_value]
         row_out[covariate_name] = cov_value
      #
      # user_predict_table
      user_predict_table.append(row_out)
   #
   return user_predict_table
# ----------------------------------------------------------------------------
# BEGIN DEF
# at_cascade.csv.pre_user
def pre_user(
   fit_dir,
   sim_dir,
   job_table,
   start_job_name,
   predict_job_id_list,
   node_table,
   root_node_id,
   root_split_reference_id,
   root_database,
) :
   assert type(fit_dir)                    == str
   assert None == sim_dir or \
           type(sim_dir)                   == str
   assert type(job_table)                  == list
   assert type( job_table[0] )             == dict
   assert None == start_job_name or \
          type( start_job_name )           == str
   assert type(predict_job_id_list)        == list
   assert type( predict_job_id_list[0] )   == int
   assert type(node_table)                 == list
   assert type( node_table[0] )            == dict
   assert type(root_node_id)               == int
   assert type(root_split_reference_id)    == int
   assert type(root_database)         == str
   # END DEF
   #
   # split_reference_table
   split_reference_table = at_cascade.csv.split_reference_table
   #
   # integrand_table
   assert 'integrand' in at_cascade.constant_table_list
   connection = dismod_at.create_connection(
      root_database, new = False, readonly = True
   )
   integrand_table = dismod_at.get_table_dict(connection, 'integrand')
   connection.close()
   #
   # sex_value2name
   sex_value2name = dict()
   for row in split_reference_table :
      name  = row['split_reference_name']
      value = row['split_reference_value']
      sex_value2name[value] = name
   #
   # prefix_predict_table
   prefix_predict_table = { 'tru':list(), 'fit':list(), 'sam':list() }
   #
   # prefix_list
   if sim_dir == None :
      prefix_list = [ 'fit', 'sam' ]
   else :
      prefix_list = [ 'tru', 'fit', 'sam' ]
   #
   # predict_job_id
   for predict_job_id in predict_job_id_list :
      #
      # predict_node_id, predict_sex_id
      predict_job_row   = job_table[predict_job_id]
      predict_node_id   = predict_job_row['fit_node_id']
      predict_sex_id    = predict_job_row['split_reference_id']
      #
      # predict_directory
      predict_job_dir = at_cascade.get_database_dir(
         node_table              = node_table                     ,
         split_reference_table   = split_reference_table          ,
         node_split_set          = { root_node_id }               ,
         root_node_id            = root_node_id                   ,
         root_split_reference_id = root_split_reference_id        ,
         fit_node_id             = predict_node_id                ,
         fit_split_reference_id  = predict_sex_id                 ,
      )
      predict_directory = f'{fit_dir}/{predict_job_dir}'
      #
      # suffix
      for suffix in [ 'prior', 'posterior' ] :
         if not os.path.isfile( f'{predict_directory}/sam_{suffix}.csv' ) :
            if suffix == 'prior' :
               assert predict_job_id == 0
            else :
               assert predict_job_id != 0
         else :
            if suffix == 'posterior' :
               fit_database = f'{predict_directory}/this.db'
            else :
               fit_database = f'{predict_directory}/ancestor.db'
            #
            # fit_covariate_table
            assert 'covariate' not in at_cascade.constant_table_list
            connection = dismod_at.create_connection(
               fit_database, new = False, readonly = True
            )
            fit_covariate_table = \
               dismod_at.get_table_dict(connection, 'covariate')
            connection.close()
            #
            # fit_node_name
            fit_node_name = at_cascade.get_parent_node(fit_database)
            #
            # fit_sex_name
            fit_sex_covariate_id = None
            for (covariate_id, row) in enumerate( fit_covariate_table ) :
               if row['covariate_name'] == 'sex' :
                  fit_sex_covariate_id = covariate_id
            row = fit_covariate_table[fit_sex_covariate_id]
            fit_sex_value = row['reference']
            fit_sex_name = None
            for sex_name in at_cascade.csv.sex_name2value :
               if at_cascade.csv.sex_name2value[sex_name] == fit_sex_value :
                  fit_sex_name = sex_name
            #
            # prefix
            for prefix in prefix_list :
               #
               # file_name
               file_name = f'{predict_directory}/{prefix}_{suffix}.csv'
               if not os.path.isfile(file_name) :
                  msg = f'csv.predict: Cannot find fild {file_name}'
                  assert False, msg
               #
               # predict_table
               predict_table =  at_cascade.csv.read_table(file_name)
               #
               # prefix_predict_table
               prefix_predict_table[prefix] += predict_table_dismod2user(
                  predict_table         = predict_table ,
                  node_table            = node_table ,
                  integrand_table       = integrand_table ,
                  covariate_table       = fit_covariate_table ,
                  split_reference_table = split_reference_table,
                  sex_value2name        = sex_value2name ,
                  fit_node_name         = fit_node_name ,
                  fit_sex_name          = fit_sex_name ,
                  predict_node_id       = predict_node_id ,
                  predict_sex_id        = predict_sex_id ,
               )
   #
   # fit_dir/predict
   if start_job_name != None :
      os.makedirs( f'{fit_dir}/predict', exist_ok = True )
   #
   # prefix_predict.csv
   for prefix in prefix_list :
      if start_job_name == None :
         file_name    = f'{fit_dir}/{prefix}_predict.csv'
      else :
         file_name    = f'{fit_dir}/predict/{prefix}_{start_job_name}.csv'
      at_cascade.csv.write_table(file_name, prefix_predict_table[prefix] )
