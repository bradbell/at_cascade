# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ----------------------------------------------------------------------------
r'''
{xrst_begin csv.ancestor_fit}

Determine Closet Ancestor With Fit and Samples
##############################################

Prototype
*********
{xrst_literal ,
   # BEGIN_DEF, # END_DEF
   # BEGIN_RETURN, # END_RETURN
}

fit_dir
*******
is the directory where the csv files are located.

job_table
*********
is the :ref:`create_job_table@job_table` for this cascade.

predict_job_id
**************
is the :ref:`create_job_table@job_table@job_id` for this prediction.

node_table
**********
is the list of dict corresponding to the node table for this cascade.

root_node_id
************
is the node_id in the node table for the root node for this cascade.
Note that csv version of the cascade does its sex split at this node.

root_split_reference_id
***********************
is the split_reference_id (sex id) for the root node of the cascade.
The cascade can begin at female, both, or male.

at_cascade_log_dict
*******************
is a dictionary, with keys equal to job names, containing
the log messages that have type ``at_cascade`` .
The messages for each key are in the log table for the corresponding job.

allow_same_job
**************
If this is true (false) the a job corresponding to the ancestor fit
can be the same as the job for the prediction; i.e., the predict job
is the closest ancestor job. Otherwise, the parent of the predict job
is the closest ancestor job.

predict_job_dir
***************
This is the directory, relative to the *fit_dir*,
that corresponds to the *predict_job_id* .
See :ref:`get_database_dir-name` .

ancestor_job_dir
****************
This is the directory, relative to the *fit_dir*,
that corresponds to the closest ancestor of *predict_job_id*
that had a successful fit and posterior sampling.


{xrst_end csv.ancestor_fit}
'''
import os
import at_cascade

# BEGIN_DEF
# at_cascade.csv.ancestor_fit
def ancestor_fit(
   fit_dir,
   job_table,
   predict_job_id,
   node_table,
   root_node_id,
   split_reference_table,
   root_split_reference_id,
   at_cascade_log_dict,
   allow_same_job,
) :
   assert type(fit_dir) == str
   assert type(job_table) == list
   assert type(predict_job_id) == int
   assert type(node_table) == list
   assert type( root_node_id ) == int
   assert type(split_reference_table) == list
   assert type( root_split_reference_id) == int
   assert type( at_cascade_log_dict ) == dict
   assert type( allow_same_job ) == bool
   # END_DEF
   #
   # node_split_set
   node_split_set = { root_node_id }
   #
   # job_name, predict_node_id, predict_split_reference_id
   job_row                     = job_table[predict_job_id]
   job_name                    = job_row['job_name']
   predict_node_id             = job_row['fit_node_id']
   predict_split_reference_id  = job_row['split_reference_id']
   #
   # predict_job_dir, ancestor_job_dir
   predict_job_dir = at_cascade.get_database_dir(
      node_table              = node_table                     ,
      split_reference_table   = split_reference_table          ,
      node_split_set          = node_split_set                 ,
      root_node_id            = root_node_id                   ,
      root_split_reference_id = root_split_reference_id        ,
      fit_node_id             = predict_node_id                ,
      fit_split_reference_id  = predict_split_reference_id     ,
   )
   #
   # sample_ok
   predict_node_database = f'{fit_dir}/{predict_job_dir}/dismod.db'
   sample_ok = False
   if os.path.exists( predict_node_database ) :
      messages  = at_cascade_log_dict[job_name]
      sample_ok  = 'sample: OK' in messages
   if sample_ok and allow_same_job :
      ancestor_job_dir = predict_job_dir
      return predict_job_dir, ancestor_job_dir
   sample_ok = False
   #
   # job_id, ancestor_job_dir
   job_id            = predict_job_id
   while not sample_ok :
      #
      # job_id
      job_id = job_table[job_id]['parent_job_id']
      if job_id == None :
         ancestor_job_dir = None
         assert type(predict_job_dir) == str
         return predict_job_dir, ancestor_job_dir
      #
      # job_name, ancestor_node_id, ancestor_split_reference_id
      job_row                      = job_table[job_id]
      job_name                     = job_row['job_name']
      ancestor_node_id             = job_row['fit_node_id']
      ancestor_split_reference_id  = job_row['split_reference_id']
      #
      # ancestor_job_dir
      ancestor_job_dir = at_cascade.get_database_dir(
         node_table              = node_table                     ,
         split_reference_table   = split_reference_table          ,
         node_split_set          = node_split_set                 ,
         root_node_id            = root_node_id                   ,
         root_split_reference_id = root_split_reference_id        ,
         fit_node_id             = ancestor_node_id               ,
         fit_split_reference_id  = ancestor_split_reference_id     ,
      )
      #
      # sample_ok
      ancestor_job_database = f'{fit_dir}/{ancestor_job_dir}/dismod.db'
      if os.path.exists( ancestor_job_database ) :
         messages   = at_cascade_log_dict[job_name]
         sample_ok  = 'sample: OK' in messages
   #
   # BEGIN_RETURN
   assert type(predict_job_dir) == str
   if type(ancestor_job_dir) == str :
      assert predict_job_dir.startswith(ancestor_job_dir)
   else :
      assert ancestor_job_dir == None
   #
   return predict_job_dir, ancestor_job_dir
   # END_RETURN
