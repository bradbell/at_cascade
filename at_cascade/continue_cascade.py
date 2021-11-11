# -----------------------------------------------------------------------------
# at_cascade: Cascading Dismod_at Analysis From Parent To Child Regions
#           Copyright (C) 2021-21 University of Washington
#              (Bradley M. Bell bradbell@uw.edu)
#
# This program is distributed under the terms of the
#     GNU Affero General Public License version 3.0 or later
# see http://www.gnu.org/licenses/agpl.txt
# -----------------------------------------------------------------------------
import os
import sys
import dismod_at
import at_cascade
# -----------------------------------------------------------------------------
'''
{xsrst_begin continue_cascade}

Continue Cascade From a Fit Node
################################

Syntax
******
{xsrst_file
    # BEGIN syntax
    # END syntax
}

Purpose
*******
Sometimes when running the cascade, the fit or statistics for a node fails.
This may be becasue of something that happend on the system,
or becasue of some of the settings in the :ref:`glossary.root_node_database`.
This routine enables you to continue the cascade from such a node.

all_node_database
*****************
is a python string specifying the location of the
:ref:`all_node_db<all_node_db>`
relative to the current working directory.
This argument can't be ``None``.

fit_node_database
*****************
is a python string specifying the location of a dismod_at database
relative to the current working directory.
On input, this is an :ref:`glossary.fit_node_database`.
Upon return, it is a :ref:`glossary.fit_node_database` with the
extra properties listed under
:ref:`cascade_fit_node.output_dismod_db` below.
This argument can't be ``None``.

fit_goal_set
************
This is a ``set`` with elements of type ``int`` (``str``)
specifying the node_id (node_name) for each element of the
:ref:`glossary.fit_goal_set` .
This argument can't be ``None``.

trace_fit
*********
if ``True``, ( ``False`` ) the progress of the dismod at fit commands
will be printed on standard output during the optimization.

{xsrst_end   continue_cascade}
'''
def continue_cascade(
# BEGIN syntax
# continue_cascade(
    all_node_database = None ,
    fit_node_database = None ,
    fit_goal_set      = None ,
    trace_fit         = False,
# )
# END syntax
) :
    #
    # connection
    new        = False
    connection = dismod_at.create_connection(fit_node_database, new)
    #
    # empty_list
    empty_list = list()
    #
    # nslist table
    dismod_at.replace_table(connection, 'nslist', empty_list)
    #
    # nslist_pair table
    dismod_at.replace_table(connection, 'nslist_pair', empty_list)
    #
    # rate_table
    rate_table = dismod_at.get_table_dict(connection, 'rate')
    for row in rate_table :
        if row['rate_name'] == 'omega' :
            row['parent_smooth_id'] = None
            row['child_smooth_id']  = None
            row['child_nslist_id']  = None
    dismod_at.replace_table(connection, 'rate', rate_table)
    #
    # connection
    connection.close()
    #
    # cascade_fit
    at_cascade.cascade_fit_node(
        all_node_database = all_node_database,
        fit_node_database = fit_node_database,
        fit_goal_set      = fit_goal_set,
        trace_fit         = trace_fit,
    )
