# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ----------------------------------------------------------------------------
r'''
{xrst_begin create_all_node_db}

Create an All Node Database
###########################

Prototype
*********
{xrst_literal
   # BEGIN_DEF
   # END_DEF
}

all_node_database
*****************
is a python string containing the name of the
:ref:`all_node_db-name` that is created by this call.
This argument can't be ``None``.

option_all
**********
This argument can't be ``None``.
It is a ``dict`` with a key equal to each
:ref:`option_all_table@Table Format@option_name` that appears in the
option_all table.
The value corresponding to the key is the
:ref:`option_all_table@Table Format@option_value`
in the same row of the option_all_table.
Note that keys must have type ``str`` and all the values will be converted
to ``str``.

fit_goal_table
**************
This specifies the nodes in the :ref:`fit_goal_table-name`.
It must be a ``list`` of ``dict`` representation of the
:ref:`fit_goal_table-name` with one key for each ``dict``.
If the key is node_id (node_name) the corresponding value is
the ``int`` ( ``str`` ) representation of the node.
If this argument is ``None``, the fit_goal table is empty.

split_reference_table
*********************
This specifies the possible reference values for the splitting covariate.
It must be a ``list`` of ``dict`` representation of the
:ref:`split_reference_table-name`.
If this argument is ``None``, the split_reference table is empty.

node_split_table
****************
This specifies the nodes at which the cascade will split by the value
of the splitting covariate.
It must be a ``list`` of ``dict`` representation of the
:ref:`node_split_table-name` with one key for each ``dict``.
If the key is node_id (node_name) the corresponding value is
the ``int`` ( ``str`` ) representation of the node.
If this argument is ``None``, the node_split table is empty.

mulcov_freeze_table
*******************
This specifies the jobs at which the cascade will freeze specific
covariate multipliers.
If this argument is ``None``, the node_split table is empty.
Otherwise, it must be a ``list`` of ``dict`` representation of the
:ref:`mulcov_freeze_table-name` .
We use *row* below to refer to a ``dict`` that is an entry in this ``list`` .

fit_node_id, fit_node_name
==========================
#. If *row*\ ``["fit_node_id"]`` must be ``None``
   if and only if the :ref:`split_reference_table-name` is empty.
#. Otherwise if *row*\ ``["fit_node_id"]`` exists it must be an
   ``int`` representation of the fit_node_id for this job.
#. Otherwise *row*\ ``["fit_node_name"]`` is a
   ``str`` representation of the corresponding node name.

split_reference_id
==================
The value *row*\ ``["split_reference_id"]`` is an
``int`` representation of the split_reference_id for this job or
*row*\ ``["split_reference_name"]`` is a
``str`` representation of the corresponding split reference name.

mulcov_id
=========
The value *row*\ ``["mulcov_id"]`` is an
``int`` representation of the mulcov_id for the covariate multiplier
that is frozen.

omega_grid
**********
is a dictionary with two keys ``age`` and ``time``.
If this argument is ``None``,
the :ref:`omega_grid@omega_age_grid Table` and
the :ref:`omega_grid@omega_time_grid Table` are empty.

age
===
The value *omega_grid*\ [``age``] is a list containing the
age_id values for the omega_grid.
These are indices in the
:ref:`glossary@root_database` age table.
We use the notation *n_omega_age* for the length of the age list.

time
====
The value *omega_grid*\ [``time``] is a list containing the
time_id values for the omega_grid.
These are indices in the *root_database* time table.
We use the notation *n_omega_time* for the length of the time list.

omega_data
**********
This is a python dictionary with a key for each node name
for the :ref:`glossary@root_node` and its descendant.
The value *omega_data[node_name]* is a list.
For each *k*, *omega_data[node_name][k]* is a list.
For *i* equal 0, ..., *n_omega_age*-1
and *j* equal 0, ..., *n_omega_time*-1,

| |tab| *omega_data[node_name][k][ i * n_omega_time + j ]*

is the value of *omega* at the specified node,
the age corresponding to index *i* in *omega_grid*\ [``age``],
and time corresponding to index *j* in *omega_grid*\ [``time``].
If split_reference table is empty, *k* is zero.
Otherwise, let *n_split* be the length of the split_reference table.
For *k* equal 0, ... , *n_split*-1, it specifies the value of
:ref:`split_reference_table@split_reference_id` for the covariate value.

default
=======
The *omega_data* argument is ``None`` if and only if *omega_grid* is ``None``.
If *omega_data* is ``None`` the
:ref:`omega_all@omega_all Table` and
:ref:`omega_all@omega_index Table` will be empty.

cov_reference_table
*******************
This must be ``None`` or a ``list`` of ``dict`` representation of the
:ref:`cov_reference_table-name`.
If it `None``, the :ref:`com_cov_reference-name` routine
is used to create the cov_reference table.

{xrst_end create_all_node_db}
'''
import dismod_at
import at_cascade
# ----------------------------------------------------------------------------
# is_descendant
def is_descendant(node_table, ancestor_node_id, this_node_id) :
   if this_node_id == ancestor_node_id :
      return True
   while this_node_id is not None :
      this_node_id = node_table[this_node_id]['parent']
      if this_node_id == ancestor_node_id :
         return True
   return False
# ----------------------------------------------------------------------------
# BEGIN_DEF
# at_cascade.create_all_node_db
def create_all_node_db(
   all_node_database         = None,
   option_all                = None,
   fit_goal_table            = None,
   split_reference_table     = None,
   node_split_table          = None,
   mulcov_freeze_table       = None,
   omega_grid                = None,
   omega_data                = None,
   cov_reference_table       = None,
) :
   if fit_goal_table is None :
      fit_goal_table = list()
   if split_reference_table is None :
      split_reference_table = list()
   if node_split_table is None :
      node_split_table = list()
   if mulcov_freeze_table is None :
      mulcov_freeze_table = list()
   #
   assert type(all_node_database)      == str
   assert type(option_all)             == dict
   assert type(fit_goal_table)         == list
   assert type(split_reference_table)  == list
   assert type(node_split_table)       == list
   assert type(mulcov_freeze_table)    == list
   assert type(cov_reference_table)    == list or cov_reference_table == None
   # END_DEF
   #
   # some asserts
   if omega_grid is None :
      assert omega_data is None
   else :
      assert type(omega_grid) is dict
      assert type(omega_data) is dict
   #
   assert 'root_database'      in option_all
   assert 'root_node_name'     in option_all
   assert 'result_dir'         in option_all
   #
   # n_split
   n_split = 1
   if len(split_reference_table) > 0 :
      n_split = len(split_reference_table)
   #
   # -------------------------------------------------------------------------
   # Read root node database
   # -------------------------------------------------------------------------
   # root_connection
   new                = False
   root_database      = option_all['root_database']
   root_connection    = dismod_at.create_connection(root_database, new)
   #
   # age_table
   tbl_name  = 'age'
   age_table = dismod_at.get_table_dict(root_connection, tbl_name)
   #
   # time_table
   tbl_name   = 'time'
   time_table = dismod_at.get_table_dict(root_connection, tbl_name)
   #
   # covariate_table
   tbl_name        = 'covariate'
   covariate_table = dismod_at.get_table_dict(root_connection, tbl_name)
   #
   # node table
   tbl_name   = 'node'
   node_table = dismod_at.get_table_dict(root_connection, tbl_name)
   #
   # option table
   tbl_name     = 'option'
   option_table = dismod_at.get_table_dict(root_connection, tbl_name)
   #
   # data_table
   if cov_reference_table == None :
      tbl_name   = 'data'
      data_table = dismod_at.get_table_dict(root_connection, tbl_name)

   #
   # root_connection
   root_connection.close()
   #
   # node_name2id
   node_name2id = dict()
   for (node_id, row) in enumerate(node_table) :
      node_name2id[ row['node_name'] ] = node_id
   #
   # root_node_id
   root_node_id = None
   for row in option_table :
      if row['option_name'] == 'parent_node_id' :
         root_node_id = row['option_value']
      elif row['option_name'] == 'parent_node_name' :
         root_node_id = node_name2id[ row['option_value'] ]
   assert root_node_id is not None
   #
   # root_node_name
   root_node_name = node_table[root_node_id]['node_name']
   if root_node_name != option_all['root_node_name' ] :
      tmp  = option_all['root_node_name']
      msg  = f'root_node_name in option_all is {tmp} '
      msg += f'while in the option table it is {root_node_name}'
      assert False, msg
   #
   # rel_covariate_id_set
   rel_covariate_id_set = set( range(len(covariate_table)) )
   if 'split_covariate_name' in option_all :
      split_covariate_name = option_all['split_covariate_name']
      split_covariate_id   = at_cascade.table_name2id(
         covariate_table, 'covariate', split_covariate_name
      )
      rel_covariate_id_set.remove(split_covariate_id)
   if 'absolute_covariates' in option_all :
      temp_list = option_all['absolute_covariates'].split()
      abs_covariate_id_set = set()
      for covariate_name in temp_list :
         covariate_id   = at_cascade.table_name2id(
            covariate_table, 'covariate', covariate_name
         )
      rel_covariate_id_set.remove(covariate_id)
   #
   # option_all_table
   option_all_table = list()
   for key in option_all :
      value = option_all[key]
      row   = { 'option_name' : key , 'option_value' : value }
      option_all_table.append( row )
   #
   # cov_reference_table
   if cov_reference_table == None :
      cov_reference_table = list()
      for node_id in range( len(node_table) ) :
         ancestor      = node_id
         while ancestor != root_node_id and ancestor != None :
            ancestor = node_table[ancestor]['parent']
         if ancestor == root_node_id :
            if len(split_reference_table) == 0 :
               split_reference_list = [ None ]
            else :
               split_reference_list = range( len(split_reference_table) )
            for split_reference_id in split_reference_list :
               reference_list = at_cascade.com_cov_reference(
                  option_all_table      = option_all_table,
                  split_reference_table = split_reference_table,
                  node_table            = node_table,
                  covariate_table       = covariate_table,
                  shift_node_id         = node_id,
                  split_reference_id    = split_reference_id,
                  data_table            = data_table,
               )
               for (covariate_id, reference) in enumerate(reference_list) :
                  row = {
                     'node_id'            : node_id ,
                     'split_reference_id' : split_reference_id,
                     'covariate_id'       : covariate_id,
                     'reference_value'    : reference_list[covariate_id],
                  }
                  cov_reference_table.append(row)
   # -------------------------------------------------------------------------
   # Write all node database
   # -------------------------------------------------------------------------
   # all_connection
   new             = True
   all_connection  = dismod_at.create_connection(all_node_database, new)
   #
   # cov_reference table
   tbl_name  = 'cov_reference'
   col_name  = [ 'node_id', 'split_reference_id', 'covariate_id' ]
   col_name += [ 'reference_value' ]
   col_type  = [ 'integer',            'integer',      'integer', 'real' ]
   row_list  = list()
   for row_table in cov_reference_table :
      row    = list()
      for key in col_name :
         row.append( row_table[key] )
      row_list.append( row )
   dismod_at.create_table(
      all_connection, tbl_name, col_name, col_type, row_list
   )
   #
   # omega_age_grid table
   tbl_name    = 'omega_age_grid'
   col_name    = [ 'age_id'  ]
   col_type    = [ 'integer' ]
   row_list    = list()
   n_omega_age = None
   if not omega_grid is None :
      n_omega_age = len( omega_grid['age'] )
      for age_id in omega_grid['age'] :
         assert age_id < len(age_table)
         assert 0 <= age_id
         row_list.append( [ age_id ] )
   dismod_at.create_table(
      all_connection, tbl_name, col_name, col_type, row_list
   )
   #
   # omega_time_grid table
   tbl_name     = 'omega_time_grid'
   col_name     = [ 'time_id'  ]
   col_type     = [ 'integer' ]
   row_list     = list()
   n_omega_time = None
   if not omega_grid is None :
      n_omega_time = len( omega_grid['time'] )
      for time_id in omega_grid['time'] :
         assert time_id < len(time_table)
         assert 0 <= time_id
         row_list.append( [ time_id ] )
   dismod_at.create_table(
      all_connection, tbl_name, col_name, col_type, row_list
   )
   #
   # omega_all table
   tbl_name  = 'omega_all'
   col_name  = [ 'omega_all_value' ]
   col_type  = [  'real' ]
   row_list  = list()
   if not omega_data is None :
      node_list = omega_data.keys()
      for node_name in node_list :
         node_id = at_cascade.table_name2id(node_table, 'node', node_name)
         assert n_split == len( omega_data[node_name] )
         for k in range(n_split) :
            omega_list = omega_data[node_name][k]
            assert len(omega_list) == n_omega_age * n_omega_time
            for i in range(n_omega_age) :
               for j in range(n_omega_time) :
                  value   = omega_list[ i * n_omega_time + j]
                  row     = [ value ]
                  row_list.append( row )
   dismod_at.create_table(
      all_connection, tbl_name, col_name, col_type, row_list
   )
   #
   # omega_index table
   tbl_name  = 'omega_index'
   col_name  = [ 'node_id', 'split_reference_id', 'omega_all_id' ]
   col_type  = [ 'integer', 'integer',             'integer' ]
   row_list  = list()
   if not omega_data is None :
      omega_all_id = 0
      for node_name in node_list :
         node_id = at_cascade.table_name2id(node_table, 'node', node_name)
         for k in range(n_split) :
            if len(split_reference_table) == 0 :
               split_reference_id = None
            else :
               split_reference_id = k
            row     = [ node_id, split_reference_id, omega_all_id ]
            row_list.append( row )
            omega_all_id += n_omega_age * n_omega_time
   dismod_at.create_table(
      all_connection, tbl_name, col_name, col_type, row_list
   )
   #
   # option_all table
   tbl_name = 'option_all'
   col_name = [ 'option_name', 'option_value' ]
   col_type = [ 'text',        'text']
   row_list = list()
   for key in option_all :
      option_name = key
      option_value = str( option_all[key] )
      row_list.append( [ option_name, option_value ] )
   dismod_at.create_table(
      all_connection, tbl_name, col_name, col_type, row_list
   )
   #
   # split_reference table
   tbl_name = 'split_reference'
   col_name = [ 'split_reference_name', 'split_reference_value' ]
   col_type = [ 'text',                 'real']
   row_list = list()
   for row in split_reference_table :
      name  = row['split_reference_name']
      value = row['split_reference_value']
      row_list.append( [ name, value ] )
   dismod_at.create_table(
      all_connection, tbl_name, col_name, col_type, row_list
   )
   #
   # fit_goal table
   tbl_name = 'fit_goal'
   col_name = [ 'node_id' ]
   col_type = [ 'integer' ]
   row_list = list()
   for row in fit_goal_table :
      if 'node_id' in row :
         node_id = row['node_id']
      else :
         node_name = row['node_name']
         node_id   = at_cascade.table_name2id(node_table, 'node', node_name)
      row_list.append( [ node_id ] )
   dismod_at.create_table(
      all_connection, tbl_name, col_name, col_type, row_list
   )
   #
   # node_split table
   tbl_name = 'node_split'
   col_name = [ 'node_id' ]
   col_type = [ 'integer' ]
   row_list = list()
   for row in node_split_table :
      if 'node_id' in row :
         node_id = row['node_id']
      else :
         node_name = row['node_name']
         node_id   = at_cascade.table_name2id(node_table, 'node', node_name)
      row_list.append( [ node_id ] )
   dismod_at.create_table(
      all_connection, tbl_name, col_name, col_type, row_list
   )
   #
   # mulcov_freeze table
   tbl_name = 'mulcov_freeze'
   col_name = [ 'fit_node_id', 'split_reference_id', 'mulcov_id' ]
   col_type = [ 'integer',     'integer',            'integer'   ]
   row_list = list()
   for row in mulcov_freeze_table :
      #
      # fit_node_id
      if 'fit_node_id' in row :
         fit_node_id = row['fit_node_id']
      else :
         fit_node_name = row['fit_node_name']
         fit_node_id   = at_cascade.table_name2id(
            node_table, 'node', fit_node_name
         )
      #
      # split_reference_id
      if 'split_reference_id' in row :
         split_reference_id = row['split_reference_id']
      else :
         split_reference_name = row['split_reference_name']
         if split_reference_name is None :
            split_reference_id = None
         else :
            split_reference_id   = at_cascade.table_name2id(
               split_reference_table,
               'split_reference',
               split_reference_name
         )
      #
      # mulcov_id
      mulcov_id = row['mulcov_id']
      #
      # row_list
      row_list.append( [ fit_node_id, split_reference_id, mulcov_id ] )
   dismod_at.create_table(
      all_connection, tbl_name, col_name, col_type, row_list
   )
   #
   # close
   all_connection.close()
