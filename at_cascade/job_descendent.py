# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-23 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin job_descendent}

Check if A Job is a Descendant of Another
#########################################

Prototype
*********
{xrst_literal ,
   # BEGIN PROTOTYPE, # END PROTOTYPE
   # BEGIN RETURN, # END RETURN
}

job_table
*********
Is the :ref:`create_job_table@job_table` for this analysis.

ancestor_id
***********
is the :ref:`create_job_table@job_table@job_id` for the ancestor job.

descendent_id
*************
is the job_id for the descendant job.

generation
**********
If the job *descendent* is a descendant of job *ancestor_id* ,
the return value *generation* is the number of generations between them.
If the two job ids are the same, *generation* is zero.
If the job *descendent* is not a descendant of job *ancestor_id* ,
the return value is None.


{xrst_end job_descendent}
'''
# -----------------------------------------------------------------------------
# BEGIN PROTOTYPE
def job_descendent(job_table, ancestor_id, descendent_id) :
   assert type(job_table)   == list
   assert type(ancestor_id)   == int
   assert type(descendent_id) == int
   # END PROTOTYPE
   #
   # generation
   generation = 0
   job_id     = descendent_id
   while job_id != None and job_id != ancestor_id :
      generation += 1
      job_id      = job_table[job_id]['parent_job_id']
   if job_id == None :
      generation = None
   #
   # BEGIN RETURN
   assert generation == None or type(generation) == int
   return generation
   # END RETURN
