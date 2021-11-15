# -----------------------------------------------------------------------------
# at_cascade: Cascading Dismod_at Analysis From Parent To Child Regions
#           Copyright (C) 2021-21 University of Washington
#              (Bradley M. Bell bradbell@uw.edu)
#
# This program is distributed under the terms of the
#     GNU Affero General Public License version 3.0 or later
# see http://www.gnu.org/licenses/agpl.txt
# -----------------------------------------------------------------------------
'''
{xsrst_begin create_all_node_db}
{xsrst_spell
    bool
}

Create an All Node Database
###########################

Syntax
******
{xsrst_file
    # BEGIN syntax
    # END syntax
}

all_node_database
*****************
is a python string containing the name of the
:ref:`all_node_db` that is created by this call.
This argument can't be ``None``.

root_node_database
******************
is a python string containing the name of the name of the
:ref:`glossary.root_node_database`.
This argument can't be ``None``.

all_cov_reference
*****************
This argument can't be ``None``.
It is a python dictionary with a key equal to the node name for
each node in the node table in root_node_database.
If *node_name* is a node name,
*all_cov_reference[node_name]* is a python dictionary with a key equal to the
covariate name for each covariate in the root_node_database.
If *covariate_name* is an covariate name,

| |tab| *all_cov_reference[node_name][covariate_name]*

is a list of reference values for the specified node and covariate.

List
====
If :ref:`split_reference_table` is empty,
the length of the reference list is one and none of the
covariates depend on a splitting covariate.
Otherwise, the length of the list is the same as the length of
the split_reference table and
covariate reference can depend on the corresponding
split covariance reference value.

split_reference
***************
This argument can't be ``None`` and
specifies the possible reference values for the splitting covariate.
It must be a ``list`` of lists where each inner list has two elements.
If the length of the outter list is zero, there is no splitting covariate.
Otherwise th i-th inner list is *[name, value]*
where *name* is a ``str`` and ``value`` is a ``float``.
This specifies the :ref:`split_reference_table.split_reference_name`
and :ref:`split_reference_table.split_reference_value` for the
for the row with :ref:`split_reference_table.split_reference_id` equal to i.


all_option
**********
This argument can't be ``None``.
It is a dictionary with the possible keys below.  Note that
:ref:`all_option_table.root_node_name` is deduced from the
*root_node_database* and hence not included in the possible keys.

absolute_covariates
===================
If this key is present, it is a ``str`` specifying the
:ref:`all_option_table.absolute_covariates`.
Otherwise, there absolute_covariates does not appear in the all_option table.

split_level
===========
If this key is present, it is an ``int`` specifying the
:ref:`all_option_table.split_level`.
Otherwise, there is no split_level in the all_option table.

split_covariate_name
====================
If this key is present, it is a ``str`` specifying the
:ref:`all_option_table.split_covariate_name`.
Otherwise, there is no split_covariate_name in the all_option table.

in_parallel
===========
If this key is present, it is a ``bool`` specifying
:ref:`all_option_table.in_parallel`.
Otherwise, there is no in_parallel in the all_option table.

max_fit
=======
If this key is present, it is a ``int`` specifying the
:ref:`all_option_table.max_fit`.
Otherwise, there is no max_fit in the all_option table.

omega_grid
**********
is a dictionary with two keys ``age`` and ``time``.
If this argument is ``None``,
the :ref:`omega_grid.omega_age_grid_table` and
the :ref:`omega_grid.omega_time_grid_table` are empty.

age
===
The value *omega*\ [``age``] is a list containing the
age_id values for the omega_grid.
These are indices in the root_node_database age table.
We use the notation *n_omega_age* for the length of the age list.

time
====
The value *omega*\ [``time``] is a list containing the
time_id values for the omega_grid.
These are indices in the root_node_database time table.
We use the notation *n_omega_time* for the length of the time list.

mtall_data
**********
This is a python dictionary with a key for each node name
for the :ref:`glossary.root_node` and its descendant.
The value *mtall_data[node_name]* is a list.
For each *k*, *mtall_data[node_name][k]* is a list.
For *i* equal 0, ..., *n_omega_age*-1
and *j* equal 0, ..., *n_omega_time*-1,

| |tab| *mtall_data[node_name][k][ i * n_omega_time + j ]*

is the value of *mtall* at the specified node,
the age corresponding to index *i* in *omega_grid*\ [``age``],
and time corresponding to index *j* in *omega_grid*\ [``time``].
If split_reference table is empty, *k* is zero.
Otherwise, let *n_split* be the length of the split_reference table.
For *k* equal 0, ... , *n_split*-1, it specifies the value of
:ref:`split_reference_table.split_reference_id` for the covariate value.

default
=======
The *mtall_data* argument is ``None`` if and only if *omega_grid* is ``None``.
If *mtall_data* is ``None`` the
:ref:`all_mtall.all_mtall_table` and
:ref:`all_mtall.mtall_index_table` will be empty.


mtspecific_data
***************
This is a python dictionary with a key for each node name
for the :ref:`glossary.root_node` and its descendant.
The value *mtspecific_data[node_name]* is a list.
For each *k*, *mtspecific_data[node_name][k]* is a list.
For *i* equal 0, ..., *n_omega_age*-1
and *j* equal 0, ..., *n_omega_time*-1,

| |tab| *mtspecific_data[node_name][k][ i * n_omega_time + j ]*

is the value of *mtspecific* at the specified node,
the age corresponding to index *i* in *omega_grid*\ [``age``],
and time corresponding to index *j* in *omega_grid*\ [``time``].
If split_reference table is empty, *k* is zero.
Otherwise, let *n_split* be the length of the split_reference table.
For *k* equal 0, ... , *n_split*-1, it specifies the value of
:ref:`split_reference_table.split_reference_id` for the covariate value.

default
=======
If *omega_grid* is ``None``, *mtspecific_data* must also be ``None``.
If *mtspecific_data* is ``None`` the
:ref:`all_mtspecific.all_mtspecific_table` and
:ref:`all_mtspecific.mtspecific_index_table` will be empty.

{xsrst_end create_all_node_db}
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
def create_all_node_db(
# BEGIN syntax
# at_cascade.create_all_node_db(
    all_node_database   = None,
    root_node_database  = None,
    all_cov_reference   = None,
    split_reference     = None,
    all_option          = None,
    omega_grid          = None,
    mtall_data          = None,
    mtspecific_data     = None,
# )
# END syntax
):
    assert type(all_node_database)   is str
    assert type(root_node_database)  is str
    assert type(all_cov_reference)   is dict
    assert type(split_reference)     is list
    assert type(all_option)          is dict
    if omega_grid is None :
        assert mtall_data is None
        assert mtspecific_data is None
    else :
        assert type(omega_grid) is dict
        assert type(mtall_data) is dict
    #
    # n_split
    n_split = 1
    if len(split_reference) > 0 :
        n_split = len(split_reference)
    #
    # -------------------------------------------------------------------------
    # Read root node database
    # -------------------------------------------------------------------------
    # root_connection
    new             = False
    root_connection = dismod_at.create_connection(root_node_database, new)
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
    #
    # rel_covariate_id_set
    rel_covariate_id_set = set( range(len(covariate_table)) )
    if 'split_covariate_name' in all_option :
        split_covariate_name = all_option['split_covariate_name']
        split_covariate_id   = at_cascade.table_name2id(
            covariate_table, 'covariate', split_covariate_name
        )
        rel_covariate_id_set.remove(split_covariate_id)
    if 'absolute_covariates' in all_option :
        temp_list = all_option['absolute_covariates'].split()
        abs_covariate_id_set = set()
        for covariate_name in temp_list :
            covariate_id   = at_cascade.table_name2id(
                covariate_table, 'covariate', covariate_name
            )
        rel_covariate_id_set.remove(covariate_id)
    #
    # close
    root_connection.close()
    # -------------------------------------------------------------------------
    # Write all node database
    # -------------------------------------------------------------------------
    # all_connection
    new             = True
    all_connection  = dismod_at.create_connection(all_node_database, new)
    #
    # all_cov_reference table
    tbl_name = 'all_cov_reference'
    col_name = [ 'node_id', 'covariate_id', 'split_reference_id', 'reference']
    col_type = [ 'integer', 'integer',      'integer',            'real'     ]
    row_list = list()
    for node_id in range( len(node_table) ) :
        for covariate_id in rel_covariate_id_set :
            node_name      = node_table[node_id]['node_name']
            covariate_name = covariate_table[covariate_id]['covariate_name']
            reference_list = all_cov_reference[node_name][covariate_name]
            #
            if len(split_reference) == 0 :
                assert len(reference_list) == 1
                reference = reference_list[0]
                row       = [ node_id, covariate_id, None, reference ]
                row_list.append( row )
            else :
                assert len(reference_list) == n_split
                for (i, reference) in enumerate(reference_list) :
                    split_reference_id = i
                    row  = [
                        node_id,
                        covariate_id,
                        split_reference_id,
                        reference,
                    ]
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
    # all_mtall table
    tbl_name  = 'all_mtall'
    col_name  = [ 'all_mtall_value' ]
    col_type  = [  'real' ]
    row_list  = list()
    if not mtall_data is None :
        node_list = mtall_data.keys()
        for node_name in node_list :
            node_id = at_cascade.table_name2id(node_table, 'node', node_name)
            assert n_split == len( mtall_data[node_name] )
            for k in range(n_split) :
                mtall_list = mtall_data[node_name][k]
                assert len(mtall_list) == n_omega_age * n_omega_time
                for i in range(n_omega_age) :
                    for j in range(n_omega_time) :
                        value   = mtall_list[ i * n_omega_time + j]
                        row     = [ value ]
                        row_list.append( row )
    dismod_at.create_table(
        all_connection, tbl_name, col_name, col_type, row_list
    )
    #
    # mtall_index table
    tbl_name  = 'mtall_index'
    col_name  = [ 'node_id', 'split_reference_id', 'all_mtall_id' ]
    col_type  = [ 'integer', 'integer',             'integer' ]
    row_list  = list()
    if not mtall_data is None :
        all_mtall_id = 0
        for node_name in node_list :
            node_id = at_cascade.table_name2id(node_table, 'node', node_name)
            for k in range(n_split) :
                if len(split_reference) == 0 :
                    split_reference_id = None
                else :
                    split_reference_id = k
                row     = [ node_id, split_reference_id, all_mtall_id ]
                row_list.append( row )
                all_mtall_id += n_omega_age * n_omega_time
    dismod_at.create_table(
        all_connection, tbl_name, col_name, col_type, row_list
    )
    #
    # all_mtspecific table
    tbl_name  = 'all_mtspecific'
    col_name  = [ 'all_mtspecific_value' ]
    col_type  = [  'real' ]
    row_list  = list()
    if not mtspecific_data is None :
        node_list = mtspecific_data.keys()
        for node_name in node_list :
            node_id = at_cascade.table_name2id(node_table, 'node', node_name)
            assert n_split == len( mtall_data[node_name] )
            for k in range(n_split) :
                mtspecific_list = mtspecific_data[node_name][k]
                assert len(mtspecific_list) == n_omega_age * n_omega_time
                for i in range(n_omega_age) :
                    for j in range(n_omega_time) :
                        value   = mtspecific_list[i * n_omega_time + j]
                        row     = [ value ]
                        row_list.append( row )
    dismod_at.create_table(
        all_connection, tbl_name, col_name, col_type, row_list
    )
    #
    # mtspecific_index table
    tbl_name  = 'mtspecific_index'
    col_name  = [ 'node_id', 'split_reference_id', 'all_mtspecific_id' ]
    col_type  = [ 'integer', 'integer',            'integer' ]
    row_list  = list()
    if not mtspecific_data is None :
        all_mtspecific_id = 0
        for node_name in node_list :
            node_id = at_cascade.table_name2id(node_table, 'node', node_name)
            for k in range(n_split) :
                if len( split_reference) == 0 :
                    split_reference_id = None
                else :
                    split_reference_id = k
                row     = [ node_id, split_reference_id, all_mtspecific_id ]
                row_list.append( row )
                all_mtspecific_id += n_omega_age * n_omega_time
    dismod_at.create_table(
        all_connection, tbl_name, col_name, col_type, row_list
    )
    #
    # all_option table
    tbl_name = 'all_option'
    col_name = [ 'option_name', 'option_value' ]
    col_type = [ 'text',        'text']
    row_list = [
        ['root_node_name', root_node_name ]
    ]
    for key in all_option :
        option_name = key
        option_value = str( all_option[key] )
        row_list.append( [ option_name, option_value ] )
    dismod_at.create_table(
        all_connection, tbl_name, col_name, col_type, row_list
    )
    #
    # split_reference table
    tbl_name = 'split_reference'
    col_name = [ 'split_reference_name', 'split_reference_value' ]
    col_type = [ 'text',                 'real']
    row_list = split_reference
    dismod_at.create_table(
        all_connection, tbl_name, col_name, col_type, row_list
    )
    #
    # close
    all_connection.close()
