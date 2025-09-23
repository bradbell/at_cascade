# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-25 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin job_descendant}

Check if A Job is a Descendant of Another
#########################################

Prototype
*********
{xrst_literal ,
   # BEGIN_DEF, # END_DEF
   # BEGIN_RETURN, # END_RETURN
}

job_table
*********
Is the :ref:`create_job_table@job_table` for this analysis.

ancestor_id
***********
is the :ref:`create_job_table@job_table@job_id` for the ancestor job.

descendant_id
*************
is the job_id for the descendant job.

generation
**********
If the job *descendant* is a descendant of job *ancestor_id* ,
the return value *generation* is the number of generations between them.
If the two job ids are the same, *generation* is zero.
If the job *descendant* is not a descendant of job *ancestor_id* ,
the return value is None.

Node Depth Versus Job Depth
***************************
We use ancestor and descendant node to denote the nodes
corresponding to:

   |  *job_table* [ *ancestor_id*] ['fit_node_id']
   |  *job_table* [ *descendant*] ['fit_node_id']

We use ancestor and descendant reference to denote the split reference
values corresponding to:

   |  *job_table* [ *ancestor_id*] ['split_reference_id']
   |  *job_table* [ *descendant*] ['split_reference_id']

If the ancestor reference is equal to the descendant reference,
or if :ref:`option_all_table@refit_split` is false,
*generation* is equal to the number of nodes between the
ancestor and descendant nodes.
Otherwise, *generation* is one more than the number of nodes between the
ancestor and descendant nodes.
(There can be at most one split between any two nodes.

{xrst_end job_descendant}
'''
# -----------------------------------------------------------------------------
# BEGIN_DEF
# at_cascade.job_descendant
def job_descendant(job_table, ancestor_id, descendant_id) :
   assert type(job_table)   == list
   assert type(ancestor_id)   == int
   assert type(descendant_id) == int
   # END_DEF
   #
   # generation
   generation = 0
   job_id     = descendant_id
   while job_id != None and job_id != ancestor_id :
      generation += 1
      job_id      = job_table[job_id]['parent_job_id']
   if job_id == None :
      generation = None
   #
   # BEGIN_RETURN
   assert generation == None or type(generation) == int
   return generation
   # END_RETURN
