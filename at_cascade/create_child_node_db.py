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

parent_node_database
********************
is a python string containing the name of a :ref:`glossary.fit_node_database`
that has the results of a dismod_at fit both command.

parent_node
===========
We use *parent_node* to refer to the parent node in the
dismod_at option table in the *parent_node_database*.

child_node_database
*******************
is a python dictionary where each key is the :ref:`glossary.node_name`
for a child of the *parent_node*.
The value *child_node_database[node_name]* is the name of a *fit_node_database*
that is created by this command.
This database will only have the dismod_at input tables.
The value priors for the variables in the model will be constructed using
the fit for the parent node.
Other priors will be the same as in the :ref:`glossary.root_node_database`.

{xsrst_end create_child_node_db}
'''
create_child_node_db(
# BEGIN syntax
# at_cascade.create_child_node_db(
    all_node_database    = None ,
    fit_node_database    = None ,
    child_node_database  = None ,
# )
# END syntax
) :
