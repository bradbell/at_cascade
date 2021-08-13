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
{xsrst_begin_parent all_node_database}

The All Node DataBase
#####################

covariate_reference_table
*************************
This table specifies the reference value for every covariate
and node in the *root_node_database*.
It has the following columns:

covariate_reference_id
======================
This column has type ``integer`` and is the primary key for this table.
Its initial value is zero and it increments by one for each row.

node_id
=======
This column has type ``integer`` and is specifies
the node for this reference
by the primary key in the *root_node_database* node table

covariate_id
============
This column has type ``integer`` and is specifies
the covariate, for this reference,
by the primary key in the *root_node_database* covariate table

reference
=========
This column has type ``real`` and it specifies the reference value
for this covariate and node.

leaf_node_table
***************
This table specifies the *leaf_node_set*.
It the following columns:

leaf_node_id
============
This column has type ``integer`` and is the primary key for this table.
Its initial value is zero and it increments by one for each row.

node_id
=======
This column has type ``integer`` and is specifies
a node by the primary key in the *root_node_database* node table

option_table
************
This table specifies certain at_cascade options

Table Format
============

option_id
---------
This column of the option table has type ``integer`` and is the primary key.
Its initial value is zero and it increments by one for each row.

option_name
-----------
This column of the option table has type ``text``.
It specifies a name that is attached to each option value.

option_value
------------
This column of the option table has type ``text``.
It specifies a value that is attached to each option name.

Options
=======

sex_level
---------
If this *option_name* appears, the corresponding *option_value*
is not yet specified.
Otherwise, there will be no sex split in this cascade.

in_parallel
-----------
If this *option_name* appears, the corresponding *option_value*
is not yet specified.
Otherwise, the cascade will be run sequentially.

min_interval
------------
If this *option_name* appears, the corresponding *option_value*
is not yet specified.
Otherwise, all age and time averages will
approximated by the value at the midpoint of the intervals.


{xsrst_end all_node_database}
-------------------------------------------------------------------------------
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
is a ``str`` containing the name of the
:ref:`glossary.all_node_database` that is created by this call.
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
Not yet specified.

default
=======
If this argument in ``None``, *omega* will be constrained to zero.
In this case none of the integrands in the *root_node_database* can
be an :ref:`glossary.ode_integrand`.

mtall_data
**********
Not yet specified.

default
=======
If this argument in ``None``, *omega* will be constrained to zero.
In this case none of the integrands in the *root_node_database* can
be an :ref:`glossary.ode_integrand`.

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
    # close
    all_connection.close()
