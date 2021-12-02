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
This is a :ref:`glossary.fit_node_database` with the
final state after running :ref:`cascade_fit_node` on this database.
The necessary state of *fit_node_database* is reached before
cascade_fit_node starts runs on any of its child nodes.

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
import time
import os
import dismod_at
import at_cascade
# ----------------------------------------------------------------------------
def add_log_entry(connection, message) :
    #
    # log_table
    log_table = dismod_at.get_table_dict(connection, 'log')
    #
    # seconds
    seconds   = int( time.time() )
    #
    # message_type
    message_type = 'at_cascade'
    #
    # cmd
    cmd = 'insert into log'
    cmd += ' (log_id,message_type,table_name,row_id,unix_time,message) values('
    cmd += str( len(log_table) ) + ','     # log_id
    cmd += f'"{message_type}",'            # message_type
    cmd += 'null,'                         # table_name
    cmd += 'null,'                         # row_id
    cmd += str(seconds) + ','              # unix_time
    cmd += f'"{message}")'                 # message
    dismod_at.sql_command(connection, cmd)
# ----------------------------------------------------------------------------
def move_table(connection, src_name, dst_name) :
    #
    command     = 'DROP TABLE IF EXISTS ' + dst_name
    dismod_at.sql_command(connection, command)
    #
    command     = 'ALTER TABLE ' + src_name + ' RENAME COLUMN '
    command    += src_name + '_id TO ' + dst_name + '_id'
    dismod_at.sql_command(connection, command)
    #
    command     = 'ALTER TABLE ' + src_name + ' RENAME TO ' + dst_name
    dismod_at.sql_command(connection, command)
    #
    # log table
    message      = f'move table {src_name} to {dst_name}'
    add_log_entry(connection, message)
# ----------------------------------------------------------------------------
def continue_cascade(
# BEGIN syntax
# at_cascade.continue_cascade(
    all_node_database = None,
    fit_node_database = None,
    fit_goal_set      = None,
    trace_fit         = False,
# )
# END syntax
) :
    assert not all_node_database is None
    assert not fit_node_database is None
    assert not fit_goal_set is None
    #
    # node_table, covariate_table
    new             = False
    connection      = dismod_at.create_connection(fit_node_database, new)
    node_table      = dismod_at.get_table_dict(connection, 'node')
    covariate_table = dismod_at.get_table_dict(connection, 'covariate')
    connection.close()
    #
    # all_option_table, split_reference_table, node_split_set
    new              = False
    connection       = dismod_at.create_connection(all_node_database, new)
    all_option_table = dismod_at.get_table_dict(connection, 'all_option')
    split_reference_table = dismod_at.get_table_dict(
        connection, 'split_reference'
    )
    node_split_table = dismod_at.get_table_dict(connection, 'node_split')
    node_split_set = set()
    for row in node_split_table :
        node_split_set.add( row['node_id'] )
    connection.close()
    #
    # root_node_name
    root_node_name   = None
    for row in all_option_table :
        if row['option_name'] == 'root_node_name' :
            root_node_name = row['option_value']
    #
    # fit_children
    root_node_id = at_cascade.table_name2id(
        node_table, 'node', root_node_name
    )
    fit_children = at_cascade.get_fit_children(
        root_node_id, fit_goal_set, node_table
    )
    #
    # path_list
    if not fit_node_database.endswith('/dismod.db') :
        msg  = f'fit_node_database = {fit_node_database} '
        msg += 'does not end with /dismod.db'
        assert False, msg
    path_list = fit_node_database.split('/')
    path_list = path_list[:-1]
    if root_node_name not in path_list :
        msg  = f'fit_node_database = {fit_node_database}\n'
        msg += f'does not contain root_node_name = {root_node_name}'
        assert False, msg
    #
    # fit_node_name, split_fit_level
    shift_name = path_list[-1]
    split_fit_level = False
    for row in split_reference_table :
        if row['split_reference_name'] == shift_name :
            split_fit_level = True
    if split_fit_level :
        fit_node_name = path_list[-2]
    else :
        fit_node_name = path_list[-1]
    #
    # fit_level
    root_index = path_list.index( root_node_name )
    fit_level  = len(path_list) - root_index - 1
    #
    # check fit_node_name
    parent_node_name = at_cascade.get_parent_node(fit_node_database)
    msg  = f'last directory in fit_node_database = {fit_node_database}\n'
    msg += 'is not a split_reference_name and is not '
    msg += f'fit_node_name = {parent_node_name}'
    assert fit_node_name == parent_node_name, msg
    #
    # fit_node_id
    fit_node_id = at_cascade.table_name2id(node_table, 'node', fit_node_name)
    #
    # fit_node_dir
    fit_node_dir = fit_node_database[ : - len('dismod.db') - 1 ]
    #
    # connection
    new        = False
    connection = dismod_at.create_connection(fit_node_database, new)
    #
    # move avgint -> c_root_avgint
    move_table(connection, 'avgint', 'c_root_avgint')
    #
    # shift_name_list
    shift_name_list = list()
    split_next_level = fit_node_id in node_split_set and not split_fit_level
    if split_next_level :
        cov_info = at_cascade.get_cov_info(
            all_option_table, covariate_table, split_reference_table
        )
        fit_split_reference_id = cov_info['split_reference_id']
        for (row_id, row) in enumerate(split_reference_table) :
            if row_id != fit_split_reference_id :
                shift_name_list.append( row['split_reference_name'] )
    else :
        for node_id in fit_children[fit_node_id] :
            node_name = node_table[node_id]['node_name']
            shift_name_list.append( node_name )
    #
    # shift_databases
    shift_databases = dict()
    for shift_name in shift_name_list :
        subdir    = fit_node_dir + '/' + shift_name
        if not os.path.exists(subdir) :
            os.makedirs(subdir)
        shift_databases[shift_name] = subdir + '/dismod.db'
    #
    # create shifted databases
    at_cascade.create_shift_db(
        all_node_database,
        fit_node_database,
        shift_databases
    )
    #
    # move c_root_avgint -> avgint
    move_table(connection, 'c_root_avgint', 'avgint')
    #
    # fit_integrand
    fit_integrand = at_cascade.get_fit_integrand(fit_node_database)
    #
    # fit shifted databases
    for shift_name in shift_databases :
        fit_node_database = shift_databases[shift_name]
        at_cascade.cascade_fit_node(
            all_node_database      ,
            fit_node_database      ,
            fit_goal_set           ,
            trace_fit              ,
        )
    #
    # connection
    connection.close()
