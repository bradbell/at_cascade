# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ----------------------------------------------------------------------------
r'''
{xrst_begin pre_user_csv}

Convert Prediction Csv Files to User Format
###########################################

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

root_node_database
******************
specifies the location of the dismod_at
:ref:`glossary@root_node_database`.

{xrst_end pre_user_csv}
'''
import os
import at_cascade

# BEGIN DEF
def pre_user_csv(
   fit_dir,
   sim_dir,
   job_table,
   start_job_name,
   predict_job_id_list,
   node_table,
   root_node_id,
   root_node_database,
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
   assert type(root_node_database)         == str
   # END DEF
   #
   # split_reference_table
   split_reference_table = at_cascade.csv.split_reference_table
   # root_split_reference_id
   root_split_reference_id = 1
   assert 'both' == split_reference_table[1]['split_reference_name']
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
      # predict_job_dir
      predict_job_dir = at_cascade.get_database_dir(
         node_table              = node_table                     ,
         split_reference_table   = split_reference_table          ,
         node_split_set          = { root_node_id }               ,
         root_node_id            = root_node_id                   ,
         root_split_reference_id = root_split_reference_id        ,
         fit_node_id             = predict_node_id                ,
         fit_split_reference_id  = predict_sex_id                 ,
      )
      #
      # ancestor_database
      ancestor_database = f'{fit_dir}/{predict_job_dir}/ancestor.db'
      #
      # ancestor_covariate_table, integrand_table
      ancestor_or_root   = at_cascade.fit_or_root_class(
         ancestor_database, root_node_database
      )
      ancestor_covariate_table = ancestor_or_root.get_table('covariate')
      integrand_table          = ancestor_or_root.get_table('integrand')
      ancestor_or_root.close()
      #
      # ancestor_node_naem
      ancestor_node_name = at_cascade.get_parent_node(ancestor_database)
      #
      # ancestor_sex_name
      ancestor_sex_covariate_id = None
      for (covariate_id, row) in enumerate( ancestor_covariate_table ) :
         if row['covariate_name'] == 'sex' :
            ancestor_sex_covariate_id = covariate_id
      row = ancestor_covariate_table[ancestor_sex_covariate_id]
      ancestor_sex_value = row['reference']
      ancestor_sex_name = None
      for sex_name in at_cascade.csv.sex_name2value :
         if at_cascade.csv.sex_name2value[sex_name] == ancestor_sex_value :
            ancestor_sex_name = sex_name
      #
      # prefix
      for prefix in prefix_list :
         #
         # file_name
         file_name     = f'{fit_dir}/{predict_job_dir}/{prefix}_predict.csv'
         if not os.path.isfile(file_name) :
            msg = f'csv.predict: Cannot find {file_name}'
            assert False, msg
         else :
            # predict_table
            predict_table =  at_cascade.csv.read_table(file_name)
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
               assert node_id == predict_node_id
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
