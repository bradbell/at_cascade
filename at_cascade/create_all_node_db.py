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
    integrands
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

covariate_reference
*******************
This is a python dictionary with a key equal to the node name for
each node in the node table in *root_node_database*.
If *node* is a node name,
*covariate_reference[node]* is a python dictionary with a key equal to the
covariate name for each covariate in the *root_node_database*.
If *covariate* is an covariate name,
*covariate_reference[node][covariate]*
is the reference values for the specified node and covariate.
This argument can't be ``None``.

omega_grid
**********
is a dictionary with two keys ``age`` and ``time``.
The value *omega*\ [``age``] is a list containing the
age_id values for the :ref:``omega_grid``; i.e.,
These are indices in the root node database age table.
The value *omega*\ [``time``] is a list containing the
time_id values for the omega grid.
We use the notation *n_age* (*n_time*) for the length
of the age (time) list.

default
=======
If this argument in ``None``, *omega* will be constrained to zero.
In this case none of the integrands in the *root_node_database* can
be an :ref:`glossary.ode_integrand`.

mtall_data
**********
This is a python dictionary with a key for each node name
for the root node and its descendant.
The value *mtall_data[node_name]* is a list.
For *i* equal 0, ..., *n_age*-1 and *j* equal 0, ..., *n_time*-1,
*mtall_data[node_name][ i * n_time + j ]
is the value of *mtall* at the specified node,
the age corresponding to index *i* in *omega_grid*\ [``age``],
and time corresponding to index *j* in *omega_grid*\ [``time``].

default
=======
If this argument in ``None``, *omega* will be constrained to zero.

mtspecific_data
***************
Not yet specified.

default
=======
If this argument in ``None``, *omega* will be constrained to equal to
the *mtall_data*.

leaf_node_set
*************
This is a python set equal to the :ref:`glossary.leaf_node_set`
where each element is represented by its node name.

default
=======
If this argument is ``None``, all of the nodes from the *root_node*
down will be fit.

sex_level
*********
Not yet specified.

default
=======
If this argument is ``None``, there will be no sex split between
*root_node* and the leaf nodes.

in_parallel
***********
Not yet specified.

default
=======
If this argument is ``None``, the cascade will be run sequentially; i.e.,
not in parallel.

min_interval
************
Not yet specified.

default
=======
If this argument is ``None``, all age and time averages will
approximated by the value at the midpoint of the intervals.

{xsrst_end create_all_node_db}
'''
import dismod_at
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
    covariate_reference = None,
    omega_grid          = None,
    mtall_data          = None,
    mtspecific_data     = None,
    leaf_node_set       = None,
    sex_level           = None,
    in_parallel         = None,
    min_interval        = None,
# )
# END syntax
):
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
    # close
    root_connection.close()
    # -------------------------------------------------------------------------
    # Write all node database
    # -------------------------------------------------------------------------
    # all_connection
    new             = True
    all_connection  = dismod_at.create_connection(all_node_database, new)
    #
    # covariate_reference table
    tbl_name = 'covariate_reference'
    col_name = [ 'node_id',  'covariate_id', 'reference' ]
    col_type = [ 'integer',  'integer',       'real'      ]
    row_list = list()
    for node_id in range( len(node_table) ) :
        for covariate_id in range( len(covariate_table) ) :
            node_name      = node_table[node_id]['node_name']
            covariate_name = covariate_table[covariate_id]['covariate_name']
            reference      = covariate_reference[node_name][covariate_name]
            row            = [ node_id, covariate_id, reference ]
            row_list.append( row )
    dismod_at.create_table(
        all_connection, tbl_name, col_name, col_type, row_list
    )
    #
    # leaf_node table
    tbl_name = 'leaf_node'
    col_name = [ 'node_id' ]
    col_type = [ 'integer' ]
    row_list = list()
    if leaf_node_set is None :
        for node_id in range( len(node_table) ):
            if is_descendant(node_table, root_node_id, node_id) :
                row = [ node_id ]
                row_list.append( row )
    else :
        for node_name in leaf_node_set :
            node_id = node_name2id[node_name]
            row     = [ node_id ]
            row_list.append( row )
    dismod_at.create_table(
        all_connection, tbl_name, col_name, col_type, row_list
    )
    #
    # omega_age table
    tbl_name = 'omega_age'
    col_name = [ 'age_value'  ]
    col_type = [ 'real' ]
    row_list = list()
    n_age    = 0
    if not omega_grid is None :
        n_age = len( omega_grid['age'] )
        for age_id in omega_grid['age'] :
            assert age_id < len(age_table)
            assert 0 <= age_id
            row_list.append( [ age_id ] )
    dismod_at.create_table(
        all_connection, tbl_name, col_name, col_type, row_list
    );
    #
    # omega_time table
    tbl_name = 'omega_time'
    col_name = [ 'time_value'  ]
    col_type = [ 'real' ]
    row_list = list()
    n_time   = 0
    if not omega_grid is None :
        n_time = len( omega_grid['time'] )
        for time_id in omega_grid['time'] :
            assert time_id < len(time_table)
            assert 0 <= time_id
            row_list.append( [ time_id ] )
    dismod_at.create_table(
        all_connection, tbl_name, col_name, col_type, row_list
    );
    #
    # empty mtall table
    tbl_name = 'mtall'
    col_name = [
        'node_id', 'omega_age_id', 'omega_time_id', 'mtall_value'
    ]
    col_type = [ 'integer', 'integer', 'integer', 'real'     ]
    row_list = list()
    if not mtall_data is None :
        for node_name in mtall_data :
            node_id = table_name2id(node_table, 'node_name', node_name)
            assert len(mtall_data[node_name]) == n_age * n_time
            for i in range(n_age) :
                for i in range(n_time) :
                    omega_age_id  = i
                    omega_time_id = j
                    mtall_value   = mtall_data[node_name][ i * n_time + j]
                    row  = [node_id, omega_age_id, omega_time_id, mtall_vaule]
                    row_list.append( row )
    dismod_at.create_table(
        all_connection, tbl_name, col_name, col_type, row_list
    );
    #
    # empty mtspecific table
    tbl_name = 'mtspecific'
    col_name = [
        'node_id', 'omega_age_id', 'omega_time_id', 'mtspecific_value'
    ]
    col_type = [ 'integer', 'integer',  'integer', 'real' ]
    row_list = list()
    dismod_at.create_table(
        all_connection, tbl_name, col_name, col_type, row_list
    );
    #
    # close
    all_connection.close()
