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
{xsrst_begin cascade_root_node}
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
is a python string specifying the location of the dismod_at
:ref:`glossary.root_node` database relative to the current working directory.
It must *root_node_name*\ ``/dismod.db``; see
:ref:`all_option_table.root_node_name`.
On input, this is an :ref:`glossary.input_node_database`.
Upon return, it is a :ref:`glossary.fit_node_database` with the
extra properties listed under
:ref:`cascade_root_node.output_dismod_db` below.
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
Upon return,
the results for this fit are in the *fit_node_database.
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
fit_node_database except that values in the node_id column
has been replaced by the node_id for this fit_node.
Note that the predict_id column name was changed to c_predict_fit_var_id
(which is not the same as var_id).

c_predict_sample
================
The c_predict_sample table contains the predict table corresponding to the
predict sample command using the avgint table in the
fit_node_database except that values in the node_id column
has been replaced by the node_id for this fit_node.
Note that the predict_id column name was changed to c_predict_sample_id
(which is not the same as sample_id).

log
===
The log table contains a summary of the operations preformed on dismod.db
between it's input and output state.

Other Nodes and Splits
**********************
For each job in the :ref:`create_job_table.job_table` corresponding to
the root node, there is a corresponding database with the results of the
corresponding fit.

{xsrst_end cascade_root_node}
'''
# ----------------------------------------------------------------------------
import time
import os
import dismod_at
import at_cascade
# ----------------------------------------------------------------------------
def cascade_root_node(
# BEGIN syntax
# at_cascade.cascade_root_node(
    all_node_database       = None,
    fit_node_database       = None,
    fit_goal_set            = None,
    trace_fit               = False,
# )
# END syntax
) :
    assert all_node_database  is not None
    assert fit_node_database  is not None
    assert fit_goal_set       is not None
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
    # root_node_name
    root_node_name = None
    for row in all_option_table :
        if row['option_name'] == 'root_node_name' :
            root_node_name = row['option_value']
    assert root_node_name is not None
    #
    # check root_node_name
    parent_node_name = at_cascade.get_parent_node(fit_node_database)
    if parent_node_name != root_node_name :
        msg  = f'{fit_node_databse} parent_node_name = {parent_node_name}\n'
        msg  = f'{all_node_database} root_node_name = {root_node_name}'
        assert False, smg
    #
    # check fit_node_database
    check = f'{root_node_name}/dismod.db'
    if fit_node_database != check :
        msg  = f'fit_node_database = {fit_node_database}\n'
        msg += f'root_node_name/dismod.db = {check}\n'
        assert False, msg
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
