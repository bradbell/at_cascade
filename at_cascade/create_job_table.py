# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-23 Bradley M. Bell
# ----------------------------------------------------------------------------
r'''
{xrst_begin create_job_table}
{xrst_spell
   bool
}

Table of Jobs That Can Run in Parallel
######################################

Syntax
******
{xrst_literal ,
   # BEGIN DEF, END DEF
   # BEGIN RETURN, END RETURN
}

Purpose
*******
This routine returns a list of dict
that specify all the dismod_at fits that need to be run.
In addition, for each fit it specifies which job needs to run before,
and which jobs can be run after.

all_node_database
*****************
is a python string specifying the location of the
:ref:`all_node_db-name`
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
:ref:`split_reference_table-name` is empty.

fit_goal_set
************
This is the :ref:`glossary@fit_goal_set`.
Each such node must be the start node, or a descendant of the start node.
In addition, it must be in the :ref:`fit_goal_table-name` ,
or an ancestor of a node in the fit goal table.

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
If the :ref:`split_reference_table-name` is empty,
*job_name* is equal to *node_name*
where *node_name* is the node name corresponding to *node_id*.
Otherwise, *job_name* is equal to
*node_name*\ ``.``\ *split_reference_name*
where *split_reference_name* is the split reference name corresponding to
*split_reference_id*.

prior_only
==========
If this ``bool`` is false, this job should be run.
It will be false for if this is the start node;
see:ref:`create_job_table@start_node_id` .
If *prior_only* is true,
this job will not be run and this job will not have any children.
The priors for this job will be created if the parent job succeeds
(*prior_only* cannot be true for the parent job).
These priors are intended to be used by a subsequent call to
:ref:`continue_cascade-name` where *prior_only* for this job is false.

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
This first row of the job table has *parent_job_id* equal to None; i.e.,
there is not parent for the first job.

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
def ancestor_set(node_table, node_id) :
   result = { node_id }
   while node_table[node_id]['parent'] != None :
      node_id = node_table[node_id]['parent']
      result.add(node_id)
   return result
# -----------------------------------------------------------------------------
def get_child_job_table(
   job_id                     ,
   fit_node_id                ,
   refit_split                ,
   fit_split_reference_id     ,
   root_split_reference_id    ,
   split_reference_table      ,
   node_split_set             ,
   fit_children               ,
   prior_children             ,
   node_table                 ,
) :
   assert type(job_id) == int
   assert type(fit_node_id) == int
   assert type(refit_split) == bool
   assert type(fit_split_reference_id) ==int or fit_split_reference_id  == None
   assert type(root_split_reference_id)==int or root_split_reference_id == None
   assert type(node_split_set) == set
   assert type(fit_children) == list
   assert type(prior_children) == list
   if len(fit_children) > 0 :
      assert type( fit_children[0] ) == set
      assert type( prior_children[0] ) == set
   assert type(node_table) == list
   if len(node_table) > 0 :
      assert type( node_table[0] ) == dict
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
   # fit_node_set, shift_node_set
   if fit_node_id in node_split_set and not already_split and refit_split :
      shift_node_set = { fit_node_id }
      fit_node_set   = { fit_node_id }
   else :
      shift_node_set = prior_children[ fit_node_id ]
      fit_node_set   = fit_children[ fit_node_id ]
   #
   # child_job_table
   child_job_table = list()
   for shift_split_reference_id in shift_reference_set :
      for shift_node_id in shift_node_set :
         #
         # prior_only
         prior_only = shift_node_id not in fit_node_set
         #
         # job_name
         job_name = node_table[shift_node_id]['node_name']
         if shift_split_reference_id != None :
            row  = split_reference_table[shift_split_reference_id]
            split_reference_name = row['split_reference_name']
            job_name             = f'{job_name}.{split_reference_name}'
         #
         # child_job_table
         row = {
            'job_name'           : job_name,
            'prior_only'         : prior_only,
            'fit_node_id'        : shift_node_id,
            'split_reference_id' : shift_split_reference_id,
            'parent_job_id'      : job_id,
         }
         child_job_table.append( row )
   #
   return child_job_table
# -----------------------------------------------------------------------------
# BEGIN DEF
# at_cascade.create_job_table
def create_job_table(
   all_node_database          = None,
   node_table                 = None,
   start_node_id              = None,
   start_split_reference_id   = None,
   fit_goal_set               = None,
# )
) :
   assert type(all_node_database) == str
   assert type(node_table) == list
   if len(node_table) > 0 :
      assert type( node_table[0] ) == dict
   assert type(start_node_id) == int
   assert type(start_split_reference_id) == int or \
      start_split_reference_id == None
   assert type(fit_goal_set) == set
   # END DEF
   #
   # fit_goal_set
   temp = set()
   for node in fit_goal_set :
      if type(node) == str :
         node_id = at_cascade.table_name2id(node_table, 'node', node)
      else :
         assert type(node) == int
         node_id = node
      temp.add(node_id)
   fit_goal_set = temp
   #
   # all_table
   all_table = dict()
   connection = dismod_at.create_connection(
      all_node_database, new = False, readonly = True
   )
   tbl_list   =  [ 'option_all', 'split_reference', 'node_split', 'fit_goal' ]
   for name in tbl_list :
      all_table[name] = dismod_at.get_table_dict(connection, name)
   connection.close()
   #
   # prior_goal_set
   prior_goal_set = set()
   if len(all_table['fit_goal']) == 0 :
      prior_goal_set = set( range( len(node_table) ) )
   else :
      for row in all_table['fit_goal'] :
         prior_goal_set.add( row['node_id'] )
   #
   # fit_node_set
   fit_node_set = set()
   if len(all_table['fit_goal']) == 0 :
      fit_node_set = set( range( len(node_table) ) )
   else :
      for row in all_table['fit_goal'] :
         node_id = row['node_id']
         fit_node_set = fit_node_set.union(ancestor_set(node_table, node_id ))
   #
   for node_id in fit_goal_set :
      if start_node_id not in ancestor_set(node_table, node_id) :
         node_name       = node_table[node_id]['node_name']
         start_node_name = node_table[start_node_id]['node_name']
         msg  = f'create_job_table: node {node_name} is in fit_goal_set but\n'
         msg += 'it is not a descendant of the start node {start_node_name}'
         assert False, msg
      if node_id not in fit_node_set :
         node_name = node_table[node_id]['node_name']
         msg  = f'create_job_table: node {node_name} is in fit_goal_set\n'
         msg += 'but it is not in the fit_goal table or the ancestor of'
         msg += 'a node in the fit_goal table.'
         assert False, msg
   #
   # node_split_set
   node_split_set = set()
   for row in all_table['node_split'] :
      node_split_set.add( row['node_id'] )
   #
   # option_all_dict
   option_all_dict = dict()
   for row in all_table['option_all'] :
      option_all_dict[ row['option_name'] ] = row['option_value']
   #
   # refit_split
   if 'refit_split' in option_all_dict :
      refit_split = option_all_dict['refit_split']
      assert refit_split in [ 'true', 'false' ]
      refit_split = refit_split == 'true'
   else :
      refit_split = False
   #
   # root_node_name
   assert 'root_node_name' in option_all_dict
   root_node_name = option_all_dict['root_node_name']
   #
   # root_node_id
   root_node_id = at_cascade.table_name2id(node_table, 'node', root_node_name)
   #
   # fit_children
   fit_children = at_cascade.get_fit_children(
      root_node_id, fit_goal_set, node_table
   )
   #
   # prior_children
   prior_children = at_cascade.get_fit_children(
      root_node_id, prior_goal_set, node_table
   )
   #
   # root_split_reference_id
   if 'root_split_reference_name' in option_all_dict :
      root_split_reference_name = option_all_dict['root_split_reference_name']
      root_split_reference_id   = at_cascade.table_name2id(
         all_table['split_reference'],
         'split_reference',
         root_split_reference_name
      )
   else :
      root_split_reference_id   = None
      if refit_split :
         msg  = 'option_all_table: refit_split is true and '
         msg += ' root_split_reference_name does not appear'
         assert False, msg
   #
   # job_name
   job_name = node_table[start_node_id]['node_name']
   if start_split_reference_id != None :
      row       = all_table['split_reference'][start_split_reference_id]
      split_reference_name = row['split_reference_name']
      job_name             = f'{job_name}.{split_reference_name}'
   #
   # job_table
   job_table = [ {
      'job_name'           : job_name,
      'prior_only'         : False,
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
      child_job_table  = get_child_job_table(
         job_id,
         node_id,
         refit_split,
         split_reference_id,
         root_split_reference_id,
         all_table['split_reference'],
         node_split_set,
         fit_children,
         prior_children,
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
   # BEGIN RETURN
   # ...
   assert type(job_table)      == list
   assert type( job_table[0] ) == dict
   return job_table
   # END RETURN
