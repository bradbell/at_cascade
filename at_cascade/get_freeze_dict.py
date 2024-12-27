# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin get_freeze_dict}

Get Set of Covariate Multipliers That are Frozen
################################################

{xrst_literal ,
   # BEGIN_DEF , # END_DEF
}


node_table
**********
is a ``list`` of ``dict`` containing the node table for this cascade.

fit_node_id
***********
is the :ref:`create_job_table@job_table@fit_node_id` for this fit.

fit_split_reference_id
**********************
is the :ref:`create_job_table@job_table@split_reference_id` for this fit.
If this is an ``int`` ( ``None`` ),
the :ref:`option_all_table@split_covariate_name` does is (is not)
in the option_all table.

mulcov_freeze_table
*******************
is the :ref:`mulcov_freeze_table-name` for this cascade.

mulcov_freeze_dict
******************

keys
====
The keys in this dictionary is the
set of :ref:`mulcov_freeze_table@mulcov_id` for covariates
that should be frozen for jobs that are children of this fit.
In other words, if this fit job, and any parent of this fit job,
is in the mulcov_freeze table,
the corresponding *mulcov_id* is in *mulcov_freeze_dict* .

values
======
#. If this fit job is in the mulcov_freeze table with this *mulcov_id* ,
   *mulcov_freeze_dict* [ *mulcov_id* ] is 'posterior' .

#. If a parent of this fit job is in the mulcov_freeze table  with this
   *mulcov_id* , *mulcov_freeze_dict* [ *mulcov_id* ] is 'prior' .

{xrst_end get_freeze_dict}
'''
# BEGIN_DEF
# at_cascade.get_freeze_dict
def get_freeze_dict(
   node_table,
   fit_node_id,
   fit_split_reference_id,
   mulcov_freeze_table,
) :
   assert type(node_table) == list
   assert type(fit_node_id) == int
   assert type(fit_split_reference_id) == int or fit_split_reference_id == None
   assert type(mulcov_freeze_table) == list
   # END_DEF
   #
   # mulcov_freeze_dict
   mulcov_freeze_dict = dict()
   #
   # freeze_row
   for freeze_row in mulcov_freeze_table :
      #
      # freeze_split_reference_id
      freeze_split_reference_id = freeze_row['split_reference_id']
      if freeze_split_reference_id == fit_split_reference_id :
         #
         # freeze_node_id, mulcov_id
         freeze_node_id    = freeze_row['fit_node_id']
         freeze_mulcov_id  = freeze_row['mulcov_id']
         #
         # node_id
         node_id = fit_node_id
         while node_id != None :
            if freeze_node_id == node_id :
               if node_id == fit_node_id :
                  mulcov_freeze_dict[freeze_mulcov_id] = 'posterior'
               else :
                  mulcov_freeze_dict[freeze_mulcov_id] = 'prior'
            #
            # node_id
            node_id = node_table[node_id]['parent']
   #
   # BEGIN_RETURN
   assert type(mulcov_freeze_dict) == dict
   return mulcov_freeze_dict
   # END_RETURN
