# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin create_job_table}

Table of Jobs That Can Run in Parallel
######################################

Syntax
******
{xrst_literal
   # BEGIN syntax
   # END syntax
}

Purpose
*******
This routine returns a list of (fit_node_id, split_reference_id) pairs
that define a dismod_at fit.
In addition, it specifies which job needs to run before this job,
and which jobs can be run after this job.

all_node_database
*****************
is a python string specifying the location of the
:ref:`all_node_db`
relative to the current working directory.
This argument can't be ``None``.

node_table
**********
is a ``list`` of ``dict`` containing the node table for this cascade.
This argument can't be ``None``.

start_node_id
*************
This, together with *start_split_reference_id*
corresponds to a completed fit that we are starting from.

start_split_reference_id
************************
This, together with *start_node_id*
corresponds to a completed fit that we are starting from.
Only jobs that depend on the start jobs completion will be included in
the job table.
This is ``None`` if and only if
:ref:`split_reference_table` is empty.

fit_goal_set
************
This is the :ref:`glossary@fit_goal_set`.

job_table
*********
The return value *job_table* is a ``list``.

job_id
======
We use *this_job_id* to denote the index of a row in the job_table list.
The value *job_table[job_id]* is a ``dict`` with the following keys:

job_name
========
This is a ``str`` containing the job name.
If the :ref:`split_reference_table` is empty,
*job_name* is equal to *node_name*
where *node_name* is the node name corresponding to *node_id*.
Otherwise, *job_name* is equal to
*node_name*\ ``.``\ *split_reference_name*
where *split_reference_name* is the split reference name corresponding to
*split_reference_id*.

fit_node_id
===========
This is an ``int`` containing the node_id for the
:ref:`glossary@fit_node` for this *this_job_id*.

split_reference_id
==================
If the split_reference table is empty, this is ``None``.
Otherwise it is an ``int`` containing the
:ref:`split_reference_table@split_reference_id`
for this *this_job_id*; i.e. the splitting covariate has this reference
value.

parent_job_id
=============
This is an ``int`` containing the job_id corresponding to the parent job
which must be greater than the job_id for this row of the job table.
The parent job (and only the parent job)
must have completed before this job can be run.

start_child_job_id
==================
This is the job_id for the first job that can run as soon as this job
is completed. The start_child_job_id is always greater than the job_id
for the current row. The simplest way to run the jobs is in job table
order (not in parallel).

end_child_job_id
================
This is the job_id plus one for the last job that can run as soon as
this job is completed. If end_child_job_id is equal to start_child_job_id,
there are no jobs that require the results of this job.
Note that this job is the parent of each job between the start and end,


{xrst_end create_job_table}
'''
# -----------------------------------------------------------------------------
import dismod_at
import at_cascade
# -----------------------------------------------------------------------------
def get_child_job_table(
   job_id                     ,
   fit_node_id                ,
   fit_split_reference_id     ,
   root_split_reference_id    ,
   split_reference_table      ,
   node_split_set             ,
   fit_children               ,
   node_table                 ,
) :
   #
   # already_split
   already_split = root_split_reference_id != fit_split_reference_id
   #
   # shift_reference_set
   if already_split or fit_node_id not in node_split_set :
      shift_reference_set = { fit_split_reference_id }
   else :
      shift_reference_set = set( range( len(split_reference_table) ) )
      shift_reference_set.remove( root_split_reference_id )
   #
   # shift_node_set
   if fit_node_id in node_split_set and not already_split :
      shift_node_set = { fit_node_id }
   else :
      shift_node_set = fit_children[ fit_node_id ]
   #
   # child_job_table
   child_job_table = list()
   for shift_split_reference_id in shift_reference_set :
      for shift_node_id in shift_node_set :
         #
         # job_name
         job_name = node_table[shift_node_id]['node_name']
         if shift_split_reference_id is not None :
            row       = split_reference_table[shift_split_reference_id]
            split_reference_name = row['split_reference_name']
            job_name             = f'{job_name}.{split_reference_name}'
         #
         # child_job_table
         row = {
            'job_name'           : job_name,
            'fit_node_id'        : shift_node_id,
            'split_reference_id' : shift_split_reference_id,
            'parent_job_id'      : job_id,
         }
         child_job_table.append( row )
   #
   return child_job_table
# -----------------------------------------------------------------------------
def create_job_table(
# BEGIN syntax
# job_table = at_cascade.create_job_table(
   all_node_database          = None,
   node_table                 = None,
   start_node_id              = None,
   start_split_reference_id   = None,
   fit_goal_set               = None,
# )
# END syntax
) :
   #
   # all_table
   all_table = dict()
   new        = False
   connection = dismod_at.create_connection(all_node_database, new)
   tbl_list   =  [ 'all_option', 'split_reference', 'node_split' ]
   for name in tbl_list :
      all_table[name] = dismod_at.get_table_dict(connection, name)
   connection.close()
   #
   # node_split_set
   node_split_set = set()
   for row in all_table['node_split'] :
      node_split_set.add( row['node_id'] )
   #
   # root_node_name
   root_node_name = None
   for row in all_table['all_option'] :
      if row['option_name'] == 'root_node_name' :
         root_node_name = row['option_value']
   assert root_node_name is not None
   #
   # root_node_id
   root_node_id = at_cascade.table_name2id(node_table, 'node', root_node_name)
   #
   # fit_children
   fit_children = at_cascade.get_fit_children(
      root_node_id, fit_goal_set, node_table
   )
   #
   # root_split_reference_id
   root_split_reference_name = None
   for row in all_table['all_option'] :
      if row['option_name'] == 'root_split_reference_name' :
         root_split_reference_name = row['option_value']
   if root_split_reference_name is None :
      root_split_reference_id = None
   else :
      root_split_reference_id = at_cascade.table_name2id(
         all_table['split_reference'],
         'split_reference',
         root_split_reference_name
      )
   #
   # job_name
   job_name = node_table[start_node_id]['node_name']
   if start_split_reference_id is not None :
      row       = all_table['split_reference'][start_split_reference_id]
      split_reference_name = row['split_reference_name']
      job_name             = f'{job_name}.{split_reference_name}'
   #
   # job_table
   job_table = [ {
      'job_name'           : job_name,
      'fit_node_id'        : start_node_id,
      'split_reference_id' : start_split_reference_id,
      'parent_job_id'      : None,
   } ]
   #
   # job_id
   job_id = 0
   #
   while job_id < len(job_table) :
      #
      # node_id, split_reference
      row                = job_table[job_id]
      node_id            = row['fit_node_id']
      split_reference_id = row['split_reference_id']
      #
      # child_job_table
      child_job_table    = get_child_job_table(
         job_id,
         node_id,
         split_reference_id,
         root_split_reference_id,
         all_table['split_reference'],
         node_split_set,
         fit_children,
         node_table,
      )
      #
      # table[job_id]['start_child_job_id']
      row['start_child_job_id'] = len(job_table)
      #
      # job_table
      job_table += child_job_table
      #
      # table[job_id]['end_child_job_id']
      row['end_child_job_id'] = len(job_table)
      #
      # job_id
      job_id += 1
   #
   return job_table
