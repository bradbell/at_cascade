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
:ref`glossary.goal_node_set`;
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

Output dismod.db
****************
The results for this fit are in the
*fit_node_dir*\ ``/dismod.db`` dismod_at database.
The corresponding *fit_node_dir/\*.csv* , create by the
dismod_at db2csv command, are also the *fit_node_dir* directory.
Furthermore there is a sub-directory, for each child node of *fit_node_name*,
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
    # split_list
    split_list = None
    for row in all_option_table :
        if row['option_name'] == 'split_list' :
            split_list = row['option_value']
    #
    # check_reference
    check_reference = len(covariate_table) * [ False ]
    #
    # ------------------------------------------------------------------------
    if split_list is None :
        for row in all_cov_reference_table :
            assert row['split_reference'] is None
            if row['node_id'] == fit_node_id :
                covariate_id = row['covariate_id']
                #
                if check_reference[covariate_id] :
                    msg  = 'More than one row in all_cov_reference table has\n'
                    msg += f'node_id = {fit_node_id} '
                    msg += 'split_reference = null and '
                    msg += f'covariate_id = {covariate_id}'
                    assert False, msg
                #
                reference = covariate_table[covariate_id]['reference']
                if row['reference'] != reference :
                    msg  = 'Covariate references for '
                    msg += f'node_id = {fit_node_id} '
                    msg += 'split_reference = null and '
                    msg += f'covariate_id = {covariate_id} are different in\n'
                    msg += 'covariate and all_cov_reference tables'
                    assert False, msg
                #
                # check_reference
                check_reference[covariate_id] = True
        return
    # ------------------------------------------------------------------------
    #
    # split_covariate_name, split_reference_list
    tmp                  = split_list.split()
    split_covariate_name = tmp[1]
    split_reference_list = tmp[2:]
    for i in range( len(split_reference_list) ) :
        split_reference_list[i] = float( split_reference_list[i] )
    #
    # split_covariate_id
    split_covariate_id   = at_cascade.table_name2id(
        covariate_table, 'covariate', split_covariate_name
    )
    #
    # split_reference
    split_reference = covariate_table[split_covariate_id]['reference']
    #
    for row in all_cov_reference_table :
        assert not row['split_reference'] is None
        covariate_id = row['covariate_id']
        if row['node_id'] == fit_node_id and \
            row['split_reference'] == split_reference :
            #
            if check_reference[covariate_id] :
                msg  = 'More than one row in all_cov_reference table has\n'
                msg += f'node_id = {fit_node_id} '
                msg += 'split_reference = {split_reference} and '
                msg += f'covariate_id = {covariate_id}'
                assert False, msg
                #
            reference = covariate_table[covariate_id]['reference']
            if row['reference'] != reference :
                msg  = 'Covariate references for '
                msg += f'node_id = {fit_node_id} '
                msg += 'split_reference = {split_refernece} and '
                msg += f'covariate_id = {covariate_id} are different in\n'
                msg += 'covariate and all_cov_reference tables'
                assert False, msg
            #
            # check_reference
            check_reference[covariate_id] = True
    return
# ----------------------------------------------------------------------------
def cascade_fit_node(
# BEGIN syntax
# at_cascade.cascade_fit_node(
    all_node_database = None,
    fit_node_database = None,
    node_table        = None,
    fit_children      = None,
    fit_integrand     = None,
# )
# END syntax
) :
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
    implemented = [ 'root_node_name', 'max_fit', 'split_list' ]
    all_option  = dict()
    for key in implemented :
        all_option[key] = None
    for row in all_option_table :
        option_name  = row['option_name']
        option_value = row['option_value']
        assert option_name in implemented
        all_option[option_name] = option_value
    #
    # fit_children
    if fit_children is None :
        fit_goal_table   = dismod_at.get_table_dict(connection, 'fit_goal')
        root_node_name   = all_option['root_node_name']
        assert not root_node_name is None
        root_node_id = at_cascade.table_name2id(
            node_table, 'node', root_node_name
        )
        fit_children = at_cascade.get_fit_children(
            root_node_id, fit_goal_table, node_table
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
    at_cascade.child_avgint_table(all_node_database, fit_node_database)
    #
    # init
    dismod_at.system_command_prc( [ 'dismod_at', fit_node_database, 'init' ] )
    #
    # enforce max_fit
    max_fit = all_option['max_fit']
    if not max_fit is None :
        for integrand_id in fit_integrand :
            integrand_name = integrand_table[integrand_id]['integrand_name']
            dismod_at.system_command_prc([
                'dismod_at', fit_node_database,
                'hold_out', integrand_name, max_fit
            ])
    #
    # fit
    dismod_at.system_command_prc(
        [ 'dismod_at', fit_node_database, 'fit', 'both' ]
    )
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
    # predict sample using child_avgint_table version of avgint
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
    # db2csv
    dismod_at.system_command_prc(
        [ 'dismodat.py', fit_node_database, 'db2csv' ] )
    #
    # fit child node databases
    for node_name in child_node_databases :
        fit_node_database = child_node_databases[node_name]
        cascade_fit_node(
            all_node_database ,
            fit_node_database ,
            node_table        ,
            fit_children      ,
            fit_integrand     ,
        )
    #
    # connection
    connection.close()
