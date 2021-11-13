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
import os
import sys
import time
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
# continue_cascade(
    all_node_database = None ,
    fit_node_database = None ,
    fit_goal_set      = None ,
    trace_fit         = False,
# )
# END syntax
) :
    #
    # fit_node_dir
    fit_node_dir = fit_node_database[ : - len('dismod.db') - 1 ]
    #
    # connection
    new        = False
    connection = dismod_at.create_connection(fit_node_database, new)
    #
    # log_table, node_table
    log_table  = dismod_at.get_table_dict(connection, 'log')
    node_table = dismod_at.get_table_dict(connection, 'node')
    #
    # move avgint -> c_root_avgint
    move_table(connection, 'avgint', 'c_root_avgint')
    #
    # connection
    connection.close()
    #
    # fit_ok, sample_ok
    fit_ok    = False
    sample_ok = False
    for log_id in range(len( log_table) ) :
        message_type = log_table[log_id]['message_type']
        message      = log_table[log_id]['message']
        if message_type == 'command' and message.startswith('begin fit both') :
            #
            # fit_ok
            message_type = log_table[log_id + 1]['message_type']
            message      = log_table[log_id + 1]['message']
            fit_ok       =  message_type == 'command' and message == 'end fit'
            #
            # sample_ok
            message_type = log_table[log_id + 3]['message_type']
            message      = log_table[log_id + 3]['message']
            sample_ok    =  message_type=='command' and message=='end sample'
    msg  =  'Cannot find successful fit and sample at end of log table in\n'
    msg += fit_node_database
    assert fit_ok and sample_ok, msg
    #
    # root_node_id
    new              = False
    connection       = dismod_at.create_connection(all_node_database, new)
    all_option_table = dismod_at.get_table_dict(connection, 'all_option')
    root_node_name   = None
    for row in all_option_table :
        if row['option_name'] == 'root_node_name' :
            root_node_name = row['option_value']
    connection.close()
    msg = 'Cannot find root_node_name in all_option_table'
    assert not root_node_name is None, msg
    root_node_id = at_cascade.table_name2id(node_table, 'node', root_node_name)
    #
    # parent_node_id
    parent_node_name = at_cascade.get_parent_node(fit_node_database)
    parent_node_id   = at_cascade.table_name2id(
        node_table, 'node', parent_node_name
    )
    #
    # fit_children
    fit_children= at_cascade.get_fit_children(
        root_node_id, fit_goal_set, node_table
    )
    #
    # child_node_list
    child_node_list = fit_children[parent_node_id]
    #
    # child_node_databases
    child_node_databases = dict()
    for node_id in child_node_list :
        node_name = node_table[node_id]['node_name']
        subdir    = fit_node_dir + '/' + node_name
        if not os.path.exists(subdir) :
            os.makedirs(subdir)
        child_node_databases[node_name] = subdir + '/dismod.db'
    #
    # create child node databases
    at_cascade.create_child_node_db(
        all_node_database,
        fit_node_database,
        child_node_databases
    )
    #
    # move c_root_avgint table -> avgint table
    # creae_child_node_db expects this
    new        = False
    connection = dismod_at.create_connection(fit_node_database, new)
    move_table(connection, 'c_root_avgint', 'avgint')
    connection.close()
    #
    # fit_integrand
    fit_integrand = at_cascade.get_fit_integrand(fit_node_database)
    #
    # fit child node databases
    for node_name in child_node_databases :
        fit_node_database = child_node_databases[node_name]
        at_cascade.cascade_fit_node(
            all_node_database ,
            fit_node_database ,
            fit_goal_set      ,
            node_table        ,
            fit_children      ,
            fit_integrand     ,
            trace_fit         ,
        )
