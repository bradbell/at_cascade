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
import math
import dismod_at
# ----------------------------------------------------------------------------
def table_name2id(table, col_name, row_name) :
    for (row_id, row) in enumerate(table) :
        if row[col_name] == row_name :
            return row_id
    assert False
# ----------------------------------------------------------------------------
def null_row(table) :
    key_list = table[0].keys()
    row = dict()
    for key in key_list :
        row[key] = None
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
    all_node_database    = None ,
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
    fit_tables = dict()
    for name in [
        'nlist',
        'nlist_pair',
        'node_table',
        'option'
        'rate',
        'smooth',
        'smooth_grid',
    ] :
        fit_tables[name] = dismod_at.get_table_dict(connection, name)
    assert len( fit_tables['nlist'] ) == 0
    assert len( fit_tables['nlist_pair'] ) == 0
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
    parent_node_id = table_name2id(node_table, 'node_name', parent_node_name)
    #
    # mtall_node_list
    node_id2index = dict()
    for (mall_index_id, row) in enumerate( all_tables['mtall_index'] ) :
        node_id2index[ row['node_id'] ] = mtall_index_id
    #
    # ancestor_node_id
    ancestor_node_id = parent_node_id
    while not ancestor_node_id in node_id2index :
        ancestor_node_id = fit_tables['node'][ancestor_node_id]['parent']
        assert not ancestor_node_id is None
    #
    # parent_mtall
    mtall_index_id = node_id2index[ancestor_node_id]
    all_mtall_id   = all_tables['mtall_index'][mtall_index_id]['all_mtall_id']
    parent_mtall   = list()
    for i in range( n_omega_age * n_omega_time ) :
        parent_matall[i] = all_mtall[all_mtall_id + i ]
    #
    # parent_smooth_id
    parent_smooth_id  = len(fit_tables['smooth_table'])
    #
    # fit_tables['sooth_table']
    row           = null_row( fit_tables['smooth_table'] )
    row['n_age']  = n_omega_age
    row['n_time'] = n_omega_time
    fit_tables['smooth_table'].append( row )
    #
    # fit_tables['smooth_grid']
    for i in range( n_omega_age ) :
        for j in range( n_omega_time ) :
            row     = null_row( fit_tables['smooth_grid'] )
            age_id  = all_tables['omega_age'][i]['age_id']
            time_id = all_tables['omega_time'][j]['time_id']
            row['age_id']      = age_id
            row['time_id']     = time_id
            row['smooth_id']   = parent_smooth_id
            row['const_value'] = parent_mtall[i * n_omega_time + j]
            fit_tables['smooth_grid'].append( row )
    #
    # child_node_list
    child_node_list = child_node_id_list(fit_tables['node'], parent_node_id)
    #
    # child_nslist_id
    child_nslist_id = len( fit_tables['child_nslist'] )
    #
    # child_node_id
    for child_node_id in child_node_list :
        #
        # child_mtall
        if not child_node_id in node2index :
            child_mtall = parent_mtall
        else :
            mtall_index = node_id2index[child_node_id]
            all_mtall_id   = \
                all_tables['mtall_index'][mtall_index_id]['all_mtall_id']
            child_mtall   = list()
            for i in range( n_omega_age * n_omega_time ) :
               child_matall[i] = all_mtall[all_mtall_id + i ]
        #
        # random_effect
        random_effect = list()
        for i in range( n_omega_age * n_omega_time ) :
            random_effect = math.log( child_mtall[i] / parent_mtall[i] )
        #
        # smooth_id
        smooth_id = len( fit_tables['smooth_tables'] )
        #
        # fit_tables['nslist_pair']
        row              = null_row( fit_tables['nslist_pair'] )
        row['nslist_id'] = child_nslist_id
        row['node_id']   = child_node_id
        row['smooth_id'] = smooth_id
        fit_tables['nslist_pair'].append( row )
        #
        # fit_tables['smooth']
        row           = null_row( fit_tables['smooth_table'] )
        row['n_age']  = n_omega_age
        row['n_time'] = n_omega_time
        fit_tables['smooth_table'].append( row )
        #
        # fit_tables['smooth_grid']
        for i in range( n_omega_age ) :
            for j in range( n_omega_time ) :
                row     = null_row( fit_tables['smooth_grid'] )
                age_id  = all_tables['omega_age'][i]['age_id']
                time_id = all_tables['omega_time'][j]['time_id']
                row['age_id']      = age_id
                row['time_id']     = time_id
                row['smooth_id']   = smooth_id
                row['const_value'] = random_effect[i * n_omega_time + j]
                fit_tables['smooth_grid'].append( row )
    #
    # fit_tables['rate']
    for row in fit_tables['rate'] :
        if row['rate_name'] == 'omega' :
            row['parent_smooth_id'] = parent_smooth_id
            row['child_nslist_id']  = child_nslist_id
    #
    # replace these fit tables
    for name in [
        'nlist',
        'nlist_pair',
        'option'
        'rate',
        'smooth',
        'smooth_grid',
    ] :
        dismod_at.replace_table(connection, name, fit_tables[name])
    #
    connection.close()
