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
{xsrst_begin check_log}

Checks Logs For Warnings and Errors
###################################

Syntax
******
{xsrst_file
    # BEGIN syntax
    # END syntax
}

Purpose
*******
Read all the logs for a cascade and prints any warning or error messages.

all_node_database
*****************
is a python string specifying the location of the
:ref:`all_node_db<all_node_db>`
relative to the current working directory.
This argument can't be ``None``.

root_node_database
******************
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

{xsrst_end check_log}
'''
# ----------------------------------------------------------------------------
import time
import os
import multiprocessing
import dismod_at
import at_cascade
# ----------------------------------------------------------------------------
def check_log(
# BEGIN syntax
# at_cascade.check_log(
    all_node_database       = None,
    root_node_database      = None,
    fit_goal_set            = None,
# )
# END syntax
) :
    assert all_node_database   is not None
    assert root_node_database  is not None
    assert fit_goal_set        is not None
    #
    # node_table, covariate_table
    new             = False
    connection      = dismod_at.create_connection(root_node_database, new)
    node_table      = dismod_at.get_table_dict(connection, 'node')
    covariate_table = dismod_at.get_table_dict(connection, 'covariate')
    connection.close()
    #
    # split_reference_table, all_option_table, node_split_table
    new         = False
    connection  = dismod_at.create_connection(all_node_database, new)
    split_reference_table = dismod_at.get_table_dict(
        connection, 'split_reference'
    )
    all_option_table = dismod_at.get_table_dict(connection, 'all_option')
    node_split_table = dismod_at.get_table_dict(connection, 'node_split')
    connection.close()
    #
    # root_node_name, max_number_cpu
    root_node_name = None
    max_number_cpu = 1
    for row in all_option_table :
        if row['option_name'] == 'root_node_name' :
            root_node_name = row['option_value']
        if row['option_name'] == 'max_number_cpu' :
            max_number_cpu = int( row['option_value'] )
    assert root_node_name is not None
    #
    # check root_node_name
    check_node_name = at_cascade.get_parent_node(root_node_database)
    if check_node_name != root_node_name :
        msg  = f'{fit_node_databse} parent_node_name = {check_node_name}\n'
        msg  = f'{all_node_database} root_node_name = {root_node_name}'
        assert False, smg
    #
    # check root_node_database
    check_database = f'{root_node_name}/dismod.db'
    if root_node_database != check_database :
        msg  = f'root_node_database = {root_node_database}\n'
        msg += f'root_node_name/dismod.db = {check_database}\n'
        assert False, msg
    #
    # fit_integrand
    fit_integrand = at_cascade.get_fit_integrand(root_node_database)
    #
    # root_node_id
    root_node_id = at_cascade.table_name2id(node_table, 'node', root_node_name)
    #
    # root_split_reference_id
    if len(split_reference_table) == 0 :
        root_split_reference_id = None
    else :
        cov_info = at_cascade.get_cov_info(
            all_option_table, covariate_table, split_reference_table
        )
        root_split_reference_id = cov_info['split_reference_id']
    #
    # job_table
    job_table = at_cascade.create_job_table(
        all_node_database          = all_node_database,
        node_table                 = node_table,
        start_node_id              = root_node_id,
        start_split_reference_id   = root_split_reference_id,
        fit_goal_set               = fit_goal_set,
    )
    #
    # node_split_set
    node_split_set = set()
    for row in node_split_table :
        node_split_set.add( row['node_id'] )
    #
    # job_id
    for job_id in range( len(job_table) ) :
        #
        # fit_node_id
        fit_node_id = job_table[job_id]['fit_node_id']
        #
        # fit_split_reference_id
        fit_split_reference_id = job_table[job_id]['split_reference_id']
        #
        # fit_node_database
        fit_database_dir = at_cascade.get_database_dir(
            node_table              = node_table,
            split_reference_table   = split_reference_table,
            node_split_set          = node_split_set,
            root_node_id            = root_node_id,
            root_split_reference_id = root_split_reference_id,
            fit_node_id             = fit_node_id ,
            fit_split_reference_id  = fit_split_reference_id,
        )
        fit_node_database = f'{fit_database_dir}/dismod.db'
        #
        # node_name
        node_name = node_table[fit_node_id]['node_name']
        #
        # split_reference_name
        row                  = split_reference_table[fit_split_reference_id]
        split_reference_name = row['split_reference_name']
        #
        # log_table
        new        = False
        connection = dismod_at.create_connection(fit_node_database, new)
        log_table  = dismod_at.get_table_dict(connection, 'log')
        connection.close()
        #
        # printed_header
        printed_header = False
        #
        # row
        for row in log_table :
            #
            # message_type
            message_type = row['message_type']
            #
            if message_type in [ 'error', 'warning'] :
                #
                # printed_header
                if not printed_header :
                    print( f'\n{node_name}.{split_reference_name}' )
                    printed_header = True
                message = row['message']
                print( f'{message_type}: {message}' )
    return