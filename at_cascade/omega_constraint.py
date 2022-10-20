# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin omega_constraint}
{xrst_spell
   nslist
   smoothings
}

Set Omega Constraints in a Fit Node Database
############################################

Syntax
******
{xrst_literal
   # BEGIN syntax
   # END syntax
}

all_node_database
*****************
is a python string containing the name of the :ref:`all_node_db`.
This argument can't be ``None``.

Use
===
This routine builds the *omega* constraints using the
:ref:`glossary@omega` data in the *all_node_database* .
If a node does not have *omega* data,
the data for the closest ancestor is used.
If a node does not have an ancestor with *omega* data,
zero is used for the *omega* constraint for that node.

fit_node_database
*****************
is a python string containing the name of a :ref:`glossary@fit_node_database`.
This argument can't be ``None``.

parent_node
===========
We use *parent_node* to refer to the parent node in the
dismod_at option table in the *fit_node_database*; i.e.,
the :ref:`glossary@fit_node` .

rate_table
==========
On input, the parent and child smoothing for omega must be null.
On return, they will be set to smoothings that yield the omega constraints.

smooth Table
============
Extra rows for the omega constraints will be added at the
end of the smooth table so that existing smoothings are preserved.

smooth_grid Table
=================
Extra rows for the omega constraints will be added at the
end of the smooth_grid table so existing smoothings are preserved.

nslist Table
============
On input, this table must be empty.
Upon return, it will contain entries that implement the omega constraints
for the children of the *parent_node*.

nslist_pair Table
=================
On input, this table must be empty.
Upon return, it will contain entries that implement the omega constraints
for the children of the *parent_node*.

Other Tables
============
None of the other tables in the database are modified.

{xrst_end omega_constraint}
'''
# ----------------------------------------------------------------------------
import copy
import dismod_at
import at_cascade
from math import log
# ----------------------------------------------------------------------------
def null_row(connection, tbl_name) :
   (col_name, col_type) = dismod_at.get_name_type(connection, tbl_name)
   row = dict()
   for key in col_name :
      row[key] = None
   return row
# ----------------------------------------------------------------------------
def child_node_id_list(node_table, parent_node_id) :
   result = list()
   for (node_id, row) in enumerate(node_table) :
      if row['parent'] == parent_node_id :
         result.append(node_id)
   return result
# ----------------------------------------------------------------------------
def omega_constraint(
# BEGIN syntax
# at_cascade.omega_constraint(
   all_node_database = None ,
   fit_node_database = None ,
# )
) :
   assert type(all_node_database) == str
   assert type(fit_node_database) == str
   # END syntax
   #
   # all_tables
   new               = False
   connection        = dismod_at.create_connection(all_node_database, new)
   all_tables = dict()
   for name in [
      'all_option',
      'all_omega',
      'omega_index',
      'omega_age_grid',
      'omega_time_grid',
      'split_reference',
   ] :
      all_tables[name] = dismod_at.get_table_dict(connection, name)
   connection.close()
   #
   # case where omega constrained to zero
   if len( all_tables['omega_time_grid']) == 0 :
      assert len( all_tables['all_omega'] ) == 0
      assert len( all_tables['omega_index'] ) == 0
      assert len( all_tables['omega_age_grid'] ) == 0
      return
   #
   # n_omega_age, n_omega_time
   n_omega_age  = len( all_tables['omega_age_grid'] )
   n_omega_time = len( all_tables['omega_time_grid'] )
   #
   # connection
   new           = False
   connection    = dismod_at.create_connection(fit_node_database, new)
   #
   # fit_tables
   fit_tables   = dict()
   fit_null_row = dict()
   for name in [
      'age',
      'time',
      'covariate',
      'nslist',
      'nslist_pair',
      'node',
      'option',
      'rate',
      'smooth',
      'smooth_grid',
   ] :
      fit_tables[name]   = dismod_at.get_table_dict(connection, name)
      fit_null_row[name] = null_row(connection, name)
   #
   # check some fit_node_database assumptions
   assert len( fit_tables['nslist'] ) == 0
   assert len( fit_tables['nslist_pair'] ) == 0
   for row in fit_tables['rate'] :
      if row['rate_name'] == 'omega' :
         assert row['parent_smooth_id'] is None
         assert row['child_smooth_id'] is None
         assert row['child_nslist_id'] is None
   for row in all_tables['omega_age_grid'] :
      age_id = row['age_id']
      if age_id >= len( fit_tables['age'] ) :
         msg  = f'The age_id {age_id} not valid for the root_node_database'
         msg += f'\nbut it appears in the omega_age_grid table '
         msg += f'of the all_node_database'
         assert False, msg
   for row in all_tables['omega_time_grid'] :
      time_id = row['time_id']
      if time_id >= len( fit_tables['time'] ) :
         msg  = f'The time_id {time_id} not valid for the root_node_database'
         msg += f'\nbut it appears in the omega_time_grid table '
         msg += f'of the all_node_database'
         assert False, msg
   #
   # split_reference_id
   cov_info = at_cascade.get_cov_info(
      all_tables['all_option'],
      fit_tables['covariate'],
      all_tables['split_reference'],
   )
   if len( all_tables['split_reference'] )  == 0 :
      split_reference_id = None
   else :
      split_reference_id = cov_info['split_reference_id']
   #
   # parent_node_id
   parent_node_name = None
   for row in fit_tables['option'] :
      assert row['option_name'] != 'parent_node_id'
      if row['option_name'] == 'parent_node_name' :
         parent_node_name = row['option_value']
   assert parent_node_name is not None
   parent_node_id = at_cascade.table_name2id(
      fit_tables['node'], 'node', parent_node_name
   )
   #
   # node_id2all_omega_id
   node_id2all_omega_id = dict()
   for row in all_tables['omega_index'] :
      all_omega_id = row['all_omega_id']
      if all_omega_id % (n_omega_age * n_omega_time) != 0 :
         msg  = 'omega_index table: Expect all_omega_id to be a multipler '
         msg += 'of n_omega_age * n_omega_time\n'
         msg += f'all_omega_id = {all_omega_id} '
         msg += f'n_omega_age = {n_omega_age} '
         msg += f'n_omega_time = {n_omega_time} '
         assert False, msg
      if row['split_reference_id'] == split_reference_id :
         node_id2all_omega_id[ row['node_id'] ] = all_omega_id
   #
   # omega_ancestor_node_id
   node_id = parent_node_id
   while not node_id in node_id2all_omega_id :
      node_id = fit_tables['node'][node_id]['parent']
      if node_id is None :
         msg  = 'omega_constraint: no ancestor of ' + parent_node_name
         msg += ' has omega data'
         assert False, msg
   omega_ancestor_node_id = node_id
   assert not omega_ancestor_node_id is None
   #
   # parent_omega
   all_omega_id = node_id2all_omega_id[omega_ancestor_node_id]
   parent_omega   = list()
   for ij in range( n_omega_age * n_omega_time ) :
      row  = all_tables['all_omega'][all_omega_id + ij ]
      parent_omega.append( row['all_omega_value'] )
   #
   # parent_smooth_id
   parent_smooth_id  = len(fit_tables['smooth'])
   #
   # fit_tables['sooth_table']
   row           = copy.copy( fit_null_row['smooth'] )
   row['n_age']  = n_omega_age
   row['n_time'] = n_omega_time
   fit_tables['smooth'].append( row )
   #
   # fit_tables['smooth_grid']
   for i in range( n_omega_age ) :
      for j in range( n_omega_time ) :
         row     = copy.copy( fit_null_row['smooth_grid'] )
         age_id  = all_tables['omega_age_grid'][i]['age_id']
         time_id = all_tables['omega_time_grid'][j]['time_id']
         ij      = i * n_omega_time + j
         omega   = parent_omega[ij]
         row['age_id']      = age_id
         row['time_id']     = time_id
         row['smooth_id']   = parent_smooth_id
         row['const_value'] = omega
         fit_tables['smooth_grid'].append( row )
   #
   # child_node_list
   child_node_list = child_node_id_list(fit_tables['node'], parent_node_id)
   #
   # nslist_id
   nslist_id = len( fit_tables['nslist'] )
   #
   # child_node_id
   for child_node_id in child_node_list :
      #
      # child_omega
      if not child_node_id in node_id2all_omega_id :
         child_omega = parent_omega
      else :
         all_omega_id = node_id2all_omega_id[child_node_id]
         child_omega  = list()
         for ij in range( n_omega_age * n_omega_time ) :
               row  = all_tables['all_omega'][all_omega_id + ij ]
               child_omega.append( row['all_omega_value'] )
      #
      # random_effect
      random_effect = list()
      for ij in range( n_omega_age * n_omega_time ) :
         if parent_omega[ij] <= 0 :
            msg  = 'parent_omega <= 0\n'
            msg += f'parent_node_id = {parent_node_id}'
            msg += f', omega_ancestor_node_id = {omega_ancestor_node_id}'
            msg += f', parent_omega = {parent_omega[ij]}'
            assert False, msg
         if child_omega[ij] <= 0 :
            msg  = 'child_omega <= 0'
            msg += f', child_node_id = {child_node_id}'
            if child_node_id in node_id2all_omega_id :
               msg += f'\nomega_ancestor_node_id = {child_node_id}'
            else :
               msg += '\nomega_ancestor_node_id = '
               msg += str(omega_ancestor_node_id)
            msg += f', child_omega = {child_omega[ij]}'
            assert False, msg
         random_effect.append( log( child_omega[ij] / parent_omega[ij] ) )
      #
      # smooth_id
      smooth_id = len( fit_tables['smooth'] )
      #
      # fit_tables['nslist_pair']
      row              = copy.copy( fit_null_row['nslist_pair'] )
      row['nslist_id'] = nslist_id
      row['node_id']   = child_node_id
      row['smooth_id'] = smooth_id
      fit_tables['nslist_pair'].append( row )
      #
      # fit_tables['smooth']
      row           = copy.copy( fit_null_row['smooth'] )
      row['n_age']  = n_omega_age
      row['n_time'] = n_omega_time
      fit_tables['smooth'].append( row )
      #
      # fit_tables['smooth_grid']
      for i in range( n_omega_age ) :
         for j in range( n_omega_time ) :
            row     = copy.copy( fit_null_row['smooth_grid'] )
            age_id  = all_tables['omega_age_grid'][i]['age_id']
            time_id = all_tables['omega_time_grid'][j]['time_id']
            row['age_id']      = age_id
            row['time_id']     = time_id
            row['smooth_id']   = smooth_id
            row['const_value'] = random_effect[i * n_omega_time + j]
            fit_tables['smooth_grid'].append( row )
   #
   # fit_tables['nslist']
   row                = copy.copy( fit_null_row['nslist'] )
   row['nslist_name'] = 'child_omega'
   fit_tables['nslist'].append( row )
   #
   # fit_tables['rate']
   for row in fit_tables['rate'] :
      if row['rate_name'] == 'omega' :
         row['parent_smooth_id'] = parent_smooth_id
         row['child_nslist_id']  = nslist_id
   #
   # replace these fit tables
   for name in [
      'nslist',
      'nslist_pair',
      'option',
      'rate',
      'smooth',
      'smooth_grid',
   ] :
      dismod_at.replace_table(connection, name, fit_tables[name])
   #
   connection.close()
