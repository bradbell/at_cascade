# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ----------------------------------------------------------------------------
r'''
{xrst_begin create_job_table}
{xrst_spell
   bool
}

Table of Job Parent Child Relationships
#######################################

Syntax
******
{xrst_literal ,
   # BEGIN DEF, END DEF
   # BEGIN RETURN, END RETURN
}

Summary
*******
This routine returns a list where each element corresponds to a job:

#. A job is a combination of a node and split reference value.
   For example, if the node is n0 and we are splitting on
   sex some possible jobs are n0.female, n0.male.

#. All of the jobs that have
   :ref:`create_job_table@job_table@prior_only` false,
   must be fit to fit all the jobs for the nodes in the *fit_goal_set*.

#. Each job has a *parent_job_id* for the job that needs to be fit before it,
   except for the start job which corresponds to the start node
   and start split reference id.
   The *prior_only* field is false for any job that is a parent; i.e.,
   all the parent jobs are fit.

#. Each job also has a list of which jobs need be run after it
   (to fit the *fit_goal_set* ).

#. If a job has *prior_only* true,
   it does not need to be fit for this *fit_goal_set*, but its priors should
   be created (when the corresponding parent job is fit)
   so it could be the start job for a different *fit_goal_set* .



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
We assume that the priors for this fit have been created; see prior_only below.
The start node must be a descendant of the :ref:`glossary@root_node` .

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
This is the a :ref:`glossary@fit_goal_set`.
In addition,
each such node must be the start node, or a descendant of the start node.

job_table
*********
The return value *job_table* is a ``list`` of ``dict`` :

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
If this ``bool`` is false, 
this job must be run to fit all the nodes in *fit_goal_set* .
It will be false if this is the start job; i.e,
the start job must be fit to fit the nodes in *fit_goal_set*.

If *prior_only* is true,
*prior_only* cannot be true for the corresponding parent job.
The priors for this job will be created if the parent job succeeds,
but this job will not be run and it will not have any children.
These priors are intended to be used by a subsequent call to
:ref:`continue_cascade-name` where this job is the start job
( and *prior_only* is false because we have a different *fit_goal_set* ).

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
   all_node_database                 ,
   node_table                        ,
   start_node_id                     ,
   fit_goal_set                      ,
   start_split_reference_id   = None ,
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
   # fit_goal_ancestor
   fit_goal_ancestor = set()
   if len(all_table['fit_goal']) == 0 :
      fit_goal_ancestor = set( range( len(node_table) ) )
   else :
      for row in all_table['fit_goal'] :
         node_id = row['node_id']
         fit_goal_ancestor = \
            fit_goal_ancestor.union( ancestor_set(node_table, node_id ) )
   #
   for node_id in fit_goal_set :
      if start_node_id not in ancestor_set(node_table, node_id) :
         node_name       = node_table[node_id]['node_name']
         start_node_name = node_table[start_node_id]['node_name']
         msg  = f'create_job_table: node {node_name} is in fit_goal_set but\n'
         msg += 'it is not a descendant of the start node {start_node_name}'
         assert False, msg
      if node_id not in fit_goal_ancestor :
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
      # row, prior_only
      row                = job_table[job_id]
      prior_only         = row['prior_only']
      #
      if not prior_only :
         #
         # node_id, split_reference
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
         # job_table
         row['start_child_job_id'] = len(job_table)
         job_table                += child_job_table
         row['end_child_job_id']   = len(job_table)
      #
      # job_id
      job_id += 1
   #
   # BEGIN RETURN
   # ...
   assert type(job_table)      == list
   assert type( job_table[0] ) == dict
   assert job_table[0]['fit_node_id'] == start_node_id
   assert job_table[0]['split_reference_id'] == start_split_reference_id
   assert job_table[0]['prior_only'] == False
   for job_id in range(1, len(job_table) ) :
      parent_job_id = job_table[job_id]['parent_job_id']
      assert job_table[parent_job_id]['prior_only'] == False
   return job_table
   # END RETURN
