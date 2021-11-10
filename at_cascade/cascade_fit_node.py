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
The *fit_node_database* must be *fit_node*\ ``/dismod.db``,
or end with the text ``/``\ *fit_node*\ ``/dismod.db``
where *fit_node* is the name of the :ref:`glossary.fit_node`
for this database.

fit_node_dir
============
is the directory where the *fit_node_database* is located.

fit_goal_set
************
This is a ``set`` with elements of type ``int`` (``str``)
specifying the node_id (node_name) for each element of the
:ref:`glossary.fit_goal_set` .

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
Furthermore, for each child node of *fit_node_name* that is in the
:ref:`glossary.fit_node_set`, there is a sub-directory
with the results for that child node.

fit_var
=======
The fit_var table correspond to the posterior
mean for the model variables for the fit_node.

sample
======
The sample table contains the corresponding samples from the posterior
distribution for the model variables for the fit_node.

predict
=======
The predict table contains predictions corresponding to the
sample table and the avgint table in the
:ref:`glossary.root_node_database` except that the values in the node_id
column has been replaced by the node_id for this fit_node.

c_predict_fit_var
=================
The c_predict_fit_var table contains predictions corresponding to the
fit_var table and the avgint table in the
root_node_database except that values in the node_id column
has been replaced by the node_id for this fit_node.

{xsrst_end cascade_fit_node}
'''
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
def move_table(connection, src_name, dst_name) :
    command     = 'DROP TABLE IF EXISTS ' + dst_name
    dismod_at.sql_command(connection, command)
    command     = 'ALTER TABLE ' + src_name + ' RENAME COLUMN '
    command    += src_name + '_id TO ' + dst_name + '_id'
    dismod_at.sql_command(connection, command)
    command     = 'ALTER TABLE ' + src_name + ' RENAME TO ' + dst_name
    dismod_at.sql_command(connection, command)
# ----------------------------------------------------------------------------
def set_avgint_node_id(connection, fit_node_id) :
    avgint_table = dismod_at.get_table_dict(connection, 'avgint')
    for row in avgint_table :
        row['node_id'] = fit_node_id
    dismod_at.replace_table(connection, 'avgint', avgint_table)
# ----------------------------------------------------------------------------
def check_covariate_reference(
    fit_node_id, covariate_table, all_option_table, all_cov_reference_table
) :
    #
    # cov_info
    cov_info = at_cascade.get_cov_info(all_option_table, covariate_table)
    #
    # rel_covariate_id_set
    rel_covariate_id_set = cov_info['rel_covariate_id_set']
    #
    # check_reference_set
    check_reference_set = set()
    # ------------------------------------------------------------------------
    if not 'split_list' in cov_info :
        for row in all_cov_reference_table :
            assert row['split_reference_id'] is None
            if row['node_id'] == fit_node_id :
                covariate_id = row['covariate_id']
                #
                if covariate_id in check_reference_set :
                    msg  = 'split_list is not in all_option table and '
                    msg += 'more than one row in all_cov_reference table has\n'
                    msg += f'node_id = {fit_node_id} '
                    msg += f'covariate_id = {covariate_id}'
                    assert False, msg
                #
                reference = covariate_table[covariate_id]['reference']
                if row['reference'] != reference :
                    msg  = 'split_list is not in all_option table and '
                    msg  = 'covariate references for '
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
    # all_option_table, all_cov_reference_table
    all_option_table = dismod_at.get_table_dict(connection, 'all_option')
    all_cov_reference_table = \
        dismod_at.get_table_dict(connection, 'all_cov_reference'
    )
    #
    # all_option
    valid = [
        'root_node_name',
        'max_fit',
        'max_abs_effect',
        'absolute_covariates',
        'split_list',
        'in_parallel',
    ]
    all_option  = dict()
    for row in all_option_table :
        option_name  = row['option_name']
        option_value = row['option_value']
        assert option_name in valid
        all_option[option_name] = option_value
    if 'split_list' in  all_option :
        split_list  = all_option['split_list'].split()
        split_level = split_list[0]
        if 0 <= int( split_level ) :
            msg  = '0 <= split_level not yet implemented'
            assert False, msg
    if 'in_parallel' in all_option :
        if all_option['in_parallel'] != 'false' :
            msg = f'all_option table: in_parallel = {in_parallel} '
            msg += 'not yet implemented'
            assert False, msg
    #
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
    # fit_node_name
    path_list = fit_node_database.split('/')
    assert len(path_list) >= 2
    assert path_list[-1] == 'dismod.db'
    fit_node_name = path_list[-2]
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
    # fit_node_dir, fit_node_database
    fit_node_dir = fit_node_database[ : - len('dismod.db') - 1 ]
    #
    # connection
    new        = False
    connection = dismod_at.create_connection(fit_node_database, new)
    #
    # check covariate references for this fit node
    covariate_table = dismod_at.get_table_dict(connection, 'covariate')
    check_covariate_reference(
        fit_node_id, covariate_table, all_option_table, all_cov_reference_table
    )
    #
    # integrand_table
    integrand_table = dismod_at.get_table_dict(connection, 'integrand')
    #
    # add omega to model
    at_cascade.omega_constraint(all_node_database, fit_node_database)
    #
    # move avgint -> c_avgint
    move_table(connection, 'avgint', 'c_avgint')
    #
    # avgint table for child predictions
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
    # c_predict_fit_var
    dismod_at.system_command_prc(
        [ 'dismod_at', fit_node_database, 'predict', 'fit_var' ]
    )
    move_table(connection, 'predict', 'c_predict_fit_var')
    #
    # predict sample using avgint_parent_grid version of avgint
    dismod_at.system_command_prc(
        [ 'dismod_at', fit_node_database, 'predict', 'sample' ]
    )
    #
    # child_node_list
    child_node_list = fit_children[fit_node_id]
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
    # move c_avgint -> avgint (original version of this table)
    move_table(connection, 'c_avgint', 'avgint')
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
    # predict
    dismod_at.system_command_prc(
        [ 'dismod_at', fit_node_database, 'predict', 'sample' ]
    )
    #
    # fit child node databases
    for node_name in child_node_databases :
        fit_node_database = child_node_databases[node_name]
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
