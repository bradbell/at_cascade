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
{xsrst_begin omega_constraint}
{xsrst_spell
    smoothings
    nslist
}

Set Omega Constraints in a Fit Node Database
############################################
This routine uses the *mtall* data for the closest ancestor of a node
and constrains *omega* to be equal to the *mtall* data.
If there is no such *mtall* data
for the :ref:`omega_constraint.fit_node_database.parent_node`,
no tables are changed by this routine.

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

fit_node_database
*****************
is a python string containing the name of a :ref:`glossary.fit_node_database`.
This argument can't be ``None``.

parent_node
===========
We use *parent_node* to refer to the parent node in the
dismod_at option table in the *fit_node_database*.

rate_table
==========
On input, the parent and child smoothing for omega must be null.
On return, they will be set to smoothings that yield the omega constraints.

smooth Table
============
Extra rows for the omega constraints will be added at the
end of the smooth table so that existing smoothings are preserved.

smooth_grid Table
=================
Extra rows for the omega constraints will be added at the
end of the smooth_grid table so existing smoothings are preserved.

nslist Table
============
On input, this table must be empty.
Upon return, it will contain entries that implement the omega constraints
for the children of the parent_node.

nslist_pair Table
=================
On input, this table must be empty.
Upon return, it will contain entries that implement the omega constraints
for the children of the parent_node.

Other Tables
============
None of the other tables in the database are modified.

{xsrst_end omega_constraint}
'''
# ----------------------------------------------------------------------------
import copy
import dismod_at
from math import log
# ----------------------------------------------------------------------------
def table_name2id(table, col_name, row_name) :
    for (row_id, row) in enumerate(table) :
        if row[col_name] == row_name :
            return row_id
    assert False
# ----------------------------------------------------------------------------
def null_row(connection, tbl_name) :
    (col_name, col_type) = dismod_at.get_name_type(connection, tbl_name)
    row = dict()
    for key in col_name :
        row[key] = None
    return row
# ----------------------------------------------------------------------------
def child_node_id_list(node_table, parent_node_id) :
    result = list()
    for (node_id, row) in enumerate(node_table) :
        if row['parent'] == parent_node_id :
            result.append(node_id)
    return result
# ----------------------------------------------------------------------------
def omega_constraint(
# BEGIN syntax
# at_cascade.omega_constraint(
    all_node_database = None ,
    fit_node_database = None ,
# )
# END syntax
) :
    # all_tables
    new               = False
    connection        = dismod_at.create_connection(all_node_database, new)
    all_tables = dict()
    for name in [
        'all_mtall',
        'mtall_index',
        'omega_age_grid',
        'omega_time_grid'
    ] :
        all_tables[name] = dismod_at.get_table_dict(connection, name)
    connection.close()
    #
    # n_omega_age, n_omega_time
    n_omega_age  = len( all_tables['omega_age_grid'] )
    n_omega_time = len( all_tables['omega_time_grid'] )
    #
    # connection
    new           = False
    connection    = dismod_at.create_connection(fit_node_database, new)
    #
    # fit_tables
    fit_tables   = dict()
    fit_null_row = dict()
    for name in [
        'nslist',
        'nslist_pair',
        'node',
        'option',
        'rate',
        'smooth',
        'smooth_grid',
    ] :
        fit_tables[name]   = dismod_at.get_table_dict(connection, name)
        fit_null_row[name] = null_row(connection, name)
    assert len( fit_tables['nslist'] ) == 0
    assert len( fit_tables['nslist_pair'] ) == 0
    for row in fit_tables['rate'] :
        if row['rate_name'] == 'omega' :
            assert row['parent_smooth_id'] is None
            assert row['child_smooth_id'] is None
            assert row['child_nslist_id'] is None
    #
    # parent_node_id
    parent_node_name = None
    for row in fit_tables['option'] :
        assert row['option_name'] != 'parent_node_id'
        if row['option_name'] == 'parent_node_name' :
            parent_node_name = row['option_value']
    assert parent_node_name is not None
    parent_node_id = table_name2id(
        fit_tables['node'], 'node_name', parent_node_name
    )
    #
    # node_id2all_mtall_id
    node_id2all_mtall_id = dict()
    for row in all_tables['mtall_index'] :
        node_id2all_mtall_id[ row['node_id'] ] = row['all_mtall_id']
    #
    # ancestor_node_id
    ancestor_node_id = parent_node_id
    while not ancestor_node_id in node_id2all_mtall_id :
        ancestor_node_id = fit_tables['node'][ancestor_node_id]['parent']
        if ancestor_node_id is None :
            return
    #
    # parent_mtall
    all_mtall_id = node_id2all_mtall_id[ancestor_node_id]
    parent_mtall   = list()
    for i in range( n_omega_age * n_omega_time ) :
        row             = all_tables['all_mtall'][all_mtall_id + i ]
        parent_mtall.append( row['all_mtall_value'] )
    #
    # parent_smooth_id
    parent_smooth_id  = len(fit_tables['smooth'])
    #
    # fit_tables['sooth_table']
    row           = copy.copy( fit_null_row['smooth'] )
    row['n_age']  = n_omega_age
    row['n_time'] = n_omega_time
    fit_tables['smooth'].append( row )
    #
    # fit_tables['smooth_grid']
    for i in range( n_omega_age ) :
        for j in range( n_omega_time ) :
            row     = copy.copy( fit_null_row['smooth_grid'] )
            age_id  = all_tables['omega_age_grid'][i]['age_id']
            time_id = all_tables['omega_time_grid'][j]['time_id']
            row['age_id']      = age_id
            row['time_id']     = time_id
            row['smooth_id']   = parent_smooth_id
            row['const_value'] = parent_mtall[i * n_omega_time + j]
            fit_tables['smooth_grid'].append( row )
    #
    # child_node_list
    child_node_list = child_node_id_list(fit_tables['node'], parent_node_id)
    #
    # nslist_id
    nslist_id = len( fit_tables['nslist'] )
    #
    # child_node_id
    for child_node_id in child_node_list :
        #
        # child_mtall
        if not child_node_id in node_id2all_mtall_id :
            child_mtall = parent_mtall
        else :
            all_mtall_id = node_id2all_mtall_id[child_node_id]
            child_mtall  = list()
            for i in range( n_omega_age * n_omega_time ) :
               row             = all_tables['all_mtall'][all_mtall_id + i ]
               child_mtall.append( row['all_mtall_value'] )
        #
        # random_effect
        random_effect = list()
        for i in range( n_omega_age * n_omega_time ) :
            random_effect.append( log( child_mtall[i] / parent_mtall[i] ) )
        #
        # smooth_id
        smooth_id = len( fit_tables['smooth'] )
        #
        # fit_tables['nslist_pair']
        row              = copy.copy( fit_null_row['nslist_pair'] )
        row['nslist_id'] = nslist_id
        row['node_id']   = child_node_id
        row['smooth_id'] = smooth_id
        fit_tables['nslist_pair'].append( row )
        #
        # fit_tables['smooth']
        row           = copy.copy( fit_null_row['smooth'] )
        row['n_age']  = n_omega_age
        row['n_time'] = n_omega_time
        fit_tables['smooth'].append( row )
        #
        # fit_tables['smooth_grid']
        for i in range( n_omega_age ) :
            for j in range( n_omega_time ) :
                row     = copy.copy( fit_null_row['smooth_grid'] )
                age_id  = all_tables['omega_age_grid'][i]['age_id']
                time_id = all_tables['omega_time_grid'][j]['time_id']
                row['age_id']      = age_id
                row['time_id']     = time_id
                row['smooth_id']   = smooth_id
                row['const_value'] = random_effect[i * n_omega_time + j]
                fit_tables['smooth_grid'].append( row )
    #
    # fit_tables['nslist']
    row                = copy.copy( fit_null_row['nslist'] )
    row['nslist_name'] = 'child_omega'
    fit_tables['nslist'].append( row )
    #
    # fit_tables['rate']
    for row in fit_tables['rate'] :
        if row['rate_name'] == 'omega' :
            row['parent_smooth_id'] = parent_smooth_id
            row['child_nslist_id']  = nslist_id
    #
    # replace these fit tables
    for name in [
        'nslist',
        'nslist_pair',
        'option',
        'rate',
        'smooth',
        'smooth_grid',
    ] :
        dismod_at.replace_table(connection, name, fit_tables[name])
    #
    connection.close()
