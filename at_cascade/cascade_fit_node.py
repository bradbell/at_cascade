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
{xsrst_begin cascade_fit_node}
{xsrst_spell
    dir
    csv
    var
}

Cascade a Fit Starting at a Node
################################

Syntax
******
{xsrst_file
    # BEGIN syntax
    # END syntax
}

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
On input, this is an :ref:`glossary.input_node_database`.
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

Output dismod.db
****************
The results for this fit are in the
*fit_node_dir*\ ``/dismod.db`` dismod_at database.
The *.csv* files in *fit_node_dir* can be created using the
dismod_at db2csv command.
The dismod_at function ``plot_rate_fit`` and ``plot_data_fit``
can be used to crate the corresponding plots.

fit_var
=======
The fit_var table correspond to the posterior
mean for the model variables for the fit_node.

sample
======
The sample table contains the corresponding samples from the posterior
distribution for the model variables for the fit_node.

c_predict_fit_var
=================
The c_predict_fit_var table contains the predict table corresponding to the
predict fit_var command using the avgint table in the
root_node_database except that values in the node_id column
has been replaced by the node_id for this fit_node.
Note that the predict_id column name was changed to c_predict_fit_var_id
(which is not the same as var_id).

c_predict_sample
================
The c_predict_sample table contains the predict table corresponding to the
predict sample command using the avgint table in the
root_node_database except that values in the node_id column
has been replaced by the node_id for this fit_node.
Note that the predict_id column name was changed to c_predict_sample_id
(which is not the same as sample_id).


log
===
The log table contains a summary of the operations preformed on dismod.db
between it's input and output state.

Output Directories
******************
The results of the fits for the following cases
are also computed by cascade_fit with *fit_node_database* corresponding
to the sub-directories:

1. If the *fit_node_dir* ends with a node name in the
   :ref:`glossary.node_split_set`, the sub-directories will be
   *fit_node_dir*\ ``/``\ *split_name* where *split_name* is a value in
   in the split_reference_name column of the split_reference table.
   The split_reference_name corresponding to the *fit_node_database* will not
   be included in this splitting.

2. If the *fit_node_dir* does not end with a node name in the
   :ref:`glossary.node_split_set`, the sub-directories will be
   *fit_node_dir*\ ``/``\ *child_name* where *child_name* is the name of
   a child of *fit_node_name* that is in the :ref:`glossary.fit_node_set`,

{xsrst_end cascade_fit_node}
'''
# ----------------------------------------------------------------------------
import time
import os
import dismod_at
import at_cascade
# ----------------------------------------------------------------------------
def cascade_fit_node(
# BEGIN syntax
# at_cascade.cascade_fit_node(
    all_node_database       = None,
    fit_node_database       = None,
    fit_goal_set            = None,
    trace_fit               = False,
# )
# END syntax
) :
    assert all_node_database is not None
    assert fit_node_database is not None
    assert fit_goal_set      is not None
    #
    # node_table, covariate_table
    new             = False
    connection      = dismod_at.create_connection(fit_node_database, new)
    node_table      = dismod_at.get_table_dict(connection, 'node')
    covariate_table = dismod_at.get_table_dict(connection, 'covariate')
    connection.close()
    #
    # split_reference_table, all_option_table
    new         = False
    connection  = dismod_at.create_connection(all_node_database, new)
    split_reference_table = dismod_at.get_table_dict(
        connection, 'split_reference'
    )
    all_option_table = dismod_at.get_table_dict(connection, 'all_option')
    connection.close()
    #
    # fit_integrand
    fit_integrand = at_cascade.get_fit_integrand(fit_node_database)
    #
    # fit_node_id
    fit_node_name = at_cascade.get_parent_node(fit_node_database)
    fit_node_id   = at_cascade.table_name2id(node_table, 'node', fit_node_name)
    #
    # fit_split_reference_id
    if len(split_reference_table) == 0 :
        fit_split_reference_id = None
    else :
        cov_info = at_cascade.get_cov_info(
            all_option_table, covariate_table, split_reference_table
        )
        fit_split_reference_id = cov_info['split_reference_id']
    #
    # job_table
    job_table = at_cascade.create_job_table(
        all_node_database          = all_node_database,
        node_table                 = node_table,
        start_node_id              = fit_node_id,
        start_split_reference_id   = fit_split_reference_id,
        fit_goal_set               = fit_goal_set,
    )
    #
    # job_id
    for job_id in range( len(job_table) ) :
        #
        # run_job
        at_cascade.run_one_job(
            job_table         = job_table ,
            run_job_id        = job_id ,
            all_node_database = all_node_database,
            node_table        = node_table,
            fit_integrand     = fit_integrand,
            trace_fit         = trace_fit,
        )
