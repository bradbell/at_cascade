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
{xsrst_begin create_child_node_db}

Create Child Database From Fit in Parent Database
#################################################

Syntax
******
{xsrst_file
    # BEGIN syntax
    # END syntax
}

all_node_database
*****************
is a python string containing the name of the :ref:`all_node_db`.
This argument can't be ``None``.

root_node_database
******************
is a python string containing the name of the
:ref:`glossary.root_node_database`.
The option table in this database must have ``parent_node_name``
and must not have ``parent_node_id``.
This argument can't be ``None``.

parent_node_database
********************
is a python string containing the name of a :ref:`glossary.fit_node_database`
that has the results of a dismod_at sample command for both the fixed
and random effects. These will be used to create priors in the
child not databases.

parent_node
===========
We use *parent_node* to refer to the parent node in the
dismod_at option table in the *parent_node_database*.

child_node_database
*******************
is a python dictionary and if *child_name* is a key for *child_node_database*,
*child_name* is a :ref:`glossary.node_name` and a child of the *parent_node*.
The value *child_node_database[child_name]* is the name of
a *fit_node_database* that is created by this command.
In this database, *child_name* will be the parent node in
the dismod_at option table.
This database will only have the dismod_at input tables.
The value priors for the variables in the model will be constructed using
the fit for the parent node.
Other priors will be the same as in the *parent_node_database*

{xsrst_end create_child_node_db}
'''
create_child_node_db(
# BEGIN syntax
# at_cascade.create_child_node_db(
    all_node_database    = None ,
    root_node_database   = None ,
    parent_node_database = None ,
    child_node_database  = None ,
# )
# END syntax
) :
    #
    # root_option_table
    new               = False
    connection        = dismod_at.create_connection(root_node_database, new)
    root_option_table = dismod_at.get_table_dict(connection, 'option')
    #
    # parent_node_index
    parent_node_index = None
    for (option_id, row) in enumerate(root_option_table) {
        name = row['option_name']
        assert name != 'parent_node_id'
        if name == 'parent_node_name' :
            parent_node_index = option_id
    assert parent_node_index is not None
    #
    # covariate_reference_table
    new        = False
    connection = dismod_at.create_connection(all_node_database, new)
    covariate_reference_table = dismod_at.get_table_dict(
        connection, 'covariate_reference'
    )
    #
    # parent_table
    new        = False
    connection = dismod_at.create_connection(parent_node_database, new)
    parent_table = dict()
    for name in [ 'var', 'fit_var', 'sample' ] :
        parent_table[name] = dismod_at.get_table_dict(connection, name)
    #
    for child_name in child_node_database :
        # start with a copy of root_node_database
        src = root_node_database
        dst = child_node_database[child_name]
        shiutil.copyfile(src, dst)
        #
        # connection
        new        = False
        connection = dismod_at.create_connection(root_node_database, new)
        #
        # change option table to have child_node as the parent
        root_option_table[parent_node_index]['option_value'] = child_name
        tbl_name = 'option'
