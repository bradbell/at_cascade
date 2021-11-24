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

fit_node
========
The *fit_node_database* must be one of the following cases,
where *fit_node* is the name of the :ref:`glossary.fit_node`
for this database:

1. *fit_node*\ ``/dismod.db`` (in this case
   :ref:`glossary.fit_node` is also the :ref:`glossary.root_node`).

2. It ends with ``/``\ *fit_node*\ ``/dismod.db``

3. It ends with ``/``\ *fit_node*\ ``/``\ *split_name*\ ``/dismod.db``,
   where *split_name* is a value in the
   :ref:`split_reference_table.split_reference_name` column of the
   split_reference table.

fit_node_dir
============
is the directory where the *fit_node_database* is located.

fit_goal_set
************
This is a ``set`` with elements of type ``int`` (``str``)
specifying the node_id (node_name) for each element of the
:ref:`glossary.fit_goal_set` .
This argument can't be ``None``.

node_table
**********
This is a python list where
*node_table[node_id]* is a python dictionary representation of the
corresponding row of the dismod_at node table.
(The primary key is not included because it is equal to the list index.)
This node table is the same as the node table in *fit_node_database*.
It is the same for all the fits and
passing it as an argument avoids reading it each time.

default
=======
If *node_table* is ``None``, it will be read by ``cascade_fit_node``
and reused by recursive calls to this routine.

fit_children
************
is the python list of python lists.
For each valid *node_id*, *fit_children[node_id]* is the list of
children of *node* that must be fit in order to fit the
:ref`glossary.fit_goal_set`;
see :ref:`get_fit_children.fit_children` .

default
=======
If *fit_children* is ``None``, it will be computed by ``cascade_fit_node``
and reused by recursive calls to this routine.

fit_integrand
*************
is the python set.
Each integrand_id in *fit_integrand* appears in the data table in
*fit_node_database*.
Furthermore all such integrand_id that appear in the a row of the data table
that has hold_out equal to zero are included.

default
=======
If *fit_integrand* is ``None``, it will be computed by ``cascade_fit_node``
and reused by recursive calls to this routine.

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

1. If the level of the *fit_node_dir* below the root_node is equal to
   :ref:`all_option_table.split_level`, the sub-directories will be
   *fit_node_dir*\ ``/``\ *split_name* where *split_name* is a value in
   in the split_reference_name column of the split_reference table.
   The *split_name* corresponding to the *fit_node* will not be included
   in this splitting.

2. If the level of the *fit_node_dir* is not equal to the split level,
   the sub-directories will be
   *fit_node_dir*\ ``/``\ *child_name* where *child_name* is the name of
   a child of *fit_node_name* that is in the :ref:`glossary.fit_node_set`,

{xsrst_end cascade_fit_node}
'''
import time
import os
import dismod_at
import at_cascade
# ----------------------------------------------------------------------------
def child_node_id_list(node_table, parent_node_id) :
    result = list()
    for (node_id, row) in enumerate(node_table) :
        if row['parent'] == parent_node_id :
            result.append(node_id)
    return result
# ----------------------------------------------------------------------------
def create_empty_log_table(connection) :
    #
    cmd  = 'create table if not exists log('
    cmd += ' log_id        integer primary key,'
    cmd += ' message_type  text               ,'
    cmd += ' table_name    text               ,'
    cmd += ' row_id        integer            ,'
    cmd += ' unix_time     integer            ,'
    cmd += ' message       text               )'
    dismod_at.sql_command(connection, cmd)
    #
    # log table
    empty_list = list()
    dismod_at.replace_table(connection, 'log', empty_list)
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
def set_avgint_node_id(connection, fit_node_id) :
    avgint_table = dismod_at.get_table_dict(connection, 'avgint')
    for row in avgint_table :
        row['node_id'] = fit_node_id
    dismod_at.replace_table(connection, 'avgint', avgint_table)
# ----------------------------------------------------------------------------
def check_covariate_reference(
    fit_node_id,
    covariate_table,
    all_option_table,
    all_cov_reference_table,
    split_reference_table
) :
    #
    # cov_info
    cov_info = at_cascade.get_cov_info(
        all_option_table, covariate_table, split_reference_table
    )
    #
    # rel_covariate_id_set
    rel_covariate_id_set = cov_info['rel_covariate_id_set']
    #
    # check_reference_set
    check_reference_set = set()
    # ------------------------------------------------------------------------
    if len( split_reference_table ) == 0 :
        for row in all_cov_reference_table :
            assert row['split_reference_id'] is None
            if row['node_id'] == fit_node_id :
                covariate_id = row['covariate_id']
                #
                if covariate_id in check_reference_set :
                    msg  = 'split_reference_table is empty and '
                    msg += 'more than one row in all_cov_reference table has\n'
                    msg += f'node_id = {fit_node_id} '
                    msg += f'covariate_id = {covariate_id}'
                    assert False, msg
                #
                reference = covariate_table[covariate_id]['reference']
                if row['reference'] != reference :
                    msg  = 'split_reference_table is empty and '
                    msg += 'covariate references for '
                    msg += f'node_id = {fit_node_id} '
                    msg += f'covariate_id = {covariate_id} are different in\n'
                    msg += 'covariate and all_cov_reference tables'
                    assert False, msg
                #
                # check_reference_set
                check_reference_set.add(covariate_id)
        #
        if check_reference_set != rel_covariate_id_set :
            msg  = f'node_id = {fit_node_id} all_cov_reference_table has '
            msg += 'reference values for following set of covaraite_id\n'
            msg += f'{check_reference_set}\n'
            msg += 'but this is not equal to the set of relative covariates\n'
            msg += f'{rel_covariate_id_set}'
            assert False, msg
        return
    # ------------------------------------------------------------------------
    #
    # split_reference_id
    split_reference_id = cov_info['split_reference_id']
    #
    for row in all_cov_reference_table :
        assert not row['split_reference_id'] is None
        covariate_id = row['covariate_id']
        if row['node_id'] == fit_node_id and \
            row['split_reference_id'] == split_reference_id :
            #
            if covariate_id in check_reference_set :
                msg  = 'More than one row in all_cov_reference table has\n'
                msg += f'node_id = {fit_node_id} '
                msg += f'split_reference_id = {split_reference_id} and '
                msg += f'covariate_id = {covariate_id}'
                assert False, msg
                #
            reference = covariate_table[covariate_id]['reference']
            if row['reference'] != reference :
                row_reference = row['reference']
                covariate_name = covariate_table[covariate_id]['covariate_name']
                msg  = f'Covariate references for {covariate_name} '
                msg += f'at node_id {fit_node_id} '
                msg += f' and split_reference_id {split_reference_id}:\n'
                msg += f'covariate_id = {covariate_id}:\n'
                msg += f'is {reference} in covariate table and '
                msg += f'{row_reference} in all_cov_reference table'
                assert False, msg
            #
            # check_reference_set
            check_reference_set.add(covariate_id)
    #
    if check_reference_set != rel_covariate_id_set :
        msg  = f'node_id = {fit_node_id}, '
        msg += f'split_reference_id = {split_reference_id}\n'
        msg += 'all_cov_reference_table has reference values '
        msg += 'for following set of covaraite_id\n'
        msg += f'{check_reference_set}\n'
        msg += 'but this is not equal to the set of relative covariates\n'
        msg += f'{rel_covariate_id_set}'
        assert False, msg
    return
# ----------------------------------------------------------------------------
def cascade_fit_node(
# BEGIN syntax
# at_cascade.cascade_fit_node(
    all_node_database = None,
    fit_node_database = None,
    fit_goal_set      = None,
    node_table        = None,
    fit_children      = None,
    fit_integrand     = None,
    trace_fit         = False,
# )
# END syntax
) :
    assert not all_node_database is None
    assert not fit_node_database is None
    assert not fit_goal_set is None
    #
    # node_table
    if node_table is None :
        new         = False
        connection  = dismod_at.create_connection(fit_node_database, new)
        node_table  = dismod_at.get_table_dict(connection, 'node')
        connection.close()
    # connection
    new         = False
    connection  = dismod_at.create_connection(all_node_database, new)
    #
    # all_option_table, all_cov_reference_table, split_refrence_table
    all_option_table = dismod_at.get_table_dict(connection, 'all_option')
    all_cov_reference_table = dismod_at.get_table_dict(
        connection, 'all_cov_reference'
    )
    split_reference_table = dismod_at.get_table_dict(
        connection, 'split_reference'
    )
    #
    # all_option
    valid = [
        'absolute_covariates',
        'shift_prior_std_factor',
        'in_parallel',
        'max_abs_effect',
        'max_fit',
        'split_list',
        'root_node_name',
        'split_covariate_name',
        'split_level',
    ]
    all_option  = dict()
    for row in all_option_table :
        option_name  = row['option_name']
        option_value = row['option_value']
        assert option_name in valid
        all_option[option_name] = option_value
    if 'in_parallel' in all_option :
        if all_option['in_parallel'] != 'false' :
            msg = f'all_option table: in_parallel = {in_parallel} '
            msg += 'not yet implemented'
            assert False, msg
    if 'root_node_name' not in all_option :
        msg = 'all_option_table; root_node_name does not appear'
        assert False, msg
    #
    # fit_children
    if fit_children is None :
        #
        # root_node_id
        root_node_name   = all_option['root_node_name']
        assert not root_node_name is None
        root_node_id = at_cascade.table_name2id(
            node_table, 'node', root_node_name
        )
        #
        # fit_children
        fit_children = at_cascade.get_fit_children(
            root_node_id, fit_goal_set, node_table
        )
    #
    # connection
    connection.close()
    #
    # fit_integrand
    if fit_integrand is None :
        fit_integrand = at_cascade.get_fit_integrand(fit_node_database)
    #
    # path_list
    if not fit_node_database.endswith('/dismod.db') :
        msg  = f'fit_node_database = {fit_node_database} '
        msg += 'does not end with /dismod.db'
        assert False, msg
    path_list = fit_node_database.split('/')
    path_list = path_list[:-1]
    if all_option['root_node_name'] not in path_list :
        msg  = f'fit_node_database = {fit_node_database}\n'
        msg += 'does not contain root_node_name = {root_node_name}'
        assert False, msg
    #
    # fit_node_name
    shift_name = path_list[-1]
    is_split_reference_name = False
    for row in split_reference_table :
        if row['split_reference_name'] == shift_name :
            is_split_reference_name = True
    if is_split_reference_name :
        fit_node_name = path_list[-2]
    else :
        fit_node_name = path_list[-1]
    #
    # fit_level
    root_index = path_list.index( all_option['root_node_name'] )
    fit_level  = len(path_list) - root_index - 1
    #
    # check fit_node_name
    msg  = f'last directory in fit_node_database = {fit_node_database}\n'
    msg += 'is not the same as parent_node_name in its option table'
    parent_node_name = at_cascade.get_parent_node(fit_node_database)
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
    # log table
    create_empty_log_table(connection)
    #
    # check covariate references for this fit node
    covariate_table = dismod_at.get_table_dict(connection, 'covariate')
    check_covariate_reference(
        fit_node_id,
        covariate_table,
        all_option_table,
        all_cov_reference_table,
        split_reference_table
    )
    #
    # integrand_table
    integrand_table = dismod_at.get_table_dict(connection, 'integrand')
    #
    # add omega to model
    at_cascade.omega_constraint(all_node_database, fit_node_database)
    message       = 'omege_contraint'
    add_log_entry(connection, message)
    #
    # move avgint -> c_root_avgint
    move_table(connection, 'avgint', 'c_root_avgint')
    #
    # avgint_parent_grid
    add_log_entry(connection, 'avgint_parent_grid')
    at_cascade.avgint_parent_grid(all_node_database, fit_node_database)
    #
    # init
    dismod_at.system_command_prc( [ 'dismod_at', fit_node_database, 'init' ] )
    #
    # enforce max_fit
    if 'max_fit' in all_option :
        max_fit = all_option['max_fit']
        for integrand_id in fit_integrand :
            integrand_name = integrand_table[integrand_id]['integrand_name']
            dismod_at.system_command_prc([
                'dismod_at', fit_node_database,
                'hold_out', integrand_name, max_fit
            ])
    #
    # enforce max_abs_effect
    if 'max_abs_effect' in all_option:
        max_abs_effect = all_option['max_abs_effect']
        dismod_at.system_command_prc([
            'dismod_at', fit_node_database, 'bnd_mulcov', max_abs_effect
        ])
    #
    # fit
    command = [ 'dismod_at', fit_node_database, 'fit', 'both' ]
    dismod_at.system_command_prc(command, return_stdout = not trace_fit )
    #
    # sample
    dismod_at.system_command_prc(
        [ 'dismod_at', fit_node_database, 'sample', 'asymptotic', 'both', '20' ]
    )
    # c_shift_predict_fit_var
    dismod_at.system_command_prc(
        [ 'dismod_at', fit_node_database, 'predict', 'fit_var' ]
    )
    move_table(connection, 'predict', 'c_shift_predict_fit_var')
    #
    # c_shift_predict_sample
    dismod_at.system_command_prc(
        [ 'dismod_at', fit_node_database, 'predict', 'sample' ]
    )
    move_table(connection, 'predict', 'c_shift_predict_sample')
    #
    # c_shift_avgint
    move_table(connection, 'avgint', 'c_shift_avgint')
    #
    # shift_name_list
    shift_name_list = list()
    split_level     = -1
    if 'split_level' in all_option :
        split_level = int( all_option['split_level'] )
    if fit_level == split_level :
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
    # node_id for predictions for fit_node
    set_avgint_node_id(connection, fit_node_id)
    #
    # c_predict_fit_var
    dismod_at.system_command_prc(
        [ 'dismod_at', fit_node_database, 'predict', 'fit_var' ]
    )
    move_table(connection, 'predict', 'c_predict_fit_var')
    #
    # c_predict_sample
    dismod_at.system_command_prc(
        [ 'dismod_at', fit_node_database, 'predict', 'sample' ]
    )
    move_table(connection, 'predict', 'c_predict_sample')
    #
    # fit shifted databases
    for shift_name in shift_databases :
        fit_node_database = shift_databases[shift_name]
        cascade_fit_node(
            all_node_database ,
            fit_node_database ,
            fit_goal_set      ,
            node_table        ,
            fit_children      ,
            fit_integrand     ,
            trace_fit         ,
        )
    #
    # connection
    connection.close()
