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
{xsrst_begin data4cov_reference}}

Use Data Table Average Covariates for Reference
###############################################

Syntax
******
{xsrst_file
    # BEGIN syntax
    # END syntax
}

root_node_database
*******************
This argument can't be ``None`` and
is the :ref:`glossary.root_node_database`.
This database is not modified and
only following tables are used:
option, data, node, covariate.

option Table
============
This table must have a row with option_value equal to parent_node_name.
Only this row of the option table is used.

data Table
==========
Only the following columns of this table are used:
data_id, node_id, x_0, ... x_n,
where n is the number of covariates minus one.

all_node_database
*****************
This argument can't be ``None`` and is the :ref:all_node_db`.
Only the :ref:`all_cov_reference_table`
and :ref:`all_option_table` are used.

all_option Table
================
The :ref:`all_option_table.split_list` row of this table
(if it exists) is the only row of this table that is used.

all_cov_reference Table
=======================
The :ref:`all_cov_reference_table.reference` column for some of the rows in
this table is replaced by the average of the corresponding covariate in the
data table.
Only the rows of the data table that satisfy the following conditions
are included when computing the average:

1.  The node_id for the data table row is the
    :ref:`all_cov_reference_table.node_id` for the all_cov_reference row,
    or a descendant of all_cov_reference node.

2.  The difference of all the covariate values in the data table row
    from the corresponding reference in the covariate table is
    less than or equal the maximum difference for that covariate.

Only the rows of the all_cov_reference table
that satisfy the following conditions are modified:

3.  There is at least one row of the data table that satisfies conditions
    1 and 2 for this all_cov_reference
    :ref:`all_cov_reference_table.covariate_id`.

4.  This all_cov_reference covariate has maximum difference equal to
    infinity (or null).

5.  The :ref:`all_cov_reference_table.split_reference_id` for this row
    corresponds to the covariate value for splitting covariate in the
    covariate table.
    (2DO: This should be extended to all values for the splitting covariate.)

{xsrst_end data4cov_reference}}
'''
import at_cascade
import dismod_at
import math
#
# data4cov_reference(
def data4cov_reference(
# BEGIN syntax
    all_node_database  = None,
    root_node_database = None
# END syntax
) :
    #
    # all_table
    new        = False
    connection = dismod_at.create_connection(all_node_database, new)
    all_table  = dict()
    for tbl_name in [
        'all_option',
        'all_cov_reference',
    ] :
        all_table[tbl_name] = dismod_at.get_table_dict(connection, tbl_name)
    connection.close()
    #
    # root_table
    new        = False
    connection = dismod_at.create_connection(root_node_database, new)
    root_table = dict()
    for tbl_name in [
        'option',
        'data',
        'node',
        'covariate',
    ] :
        root_table[tbl_name] = dismod_at.get_table_dict(connection, tbl_name)
    connection.close()
    #
    # split_reference_id
    cov_info = at_cascade.get_cov_info(
        all_table['all_option'], root_table['covariate']
    )
    if cov_info is None :
        split_reference_id = None
    else :
        split_reference_id = cov_info['split_reference_id']

    #
    # n_covariate
    n_covariate = len( root_table['covariate'] )
    #
    # covariate_label
    covariate_label = list()
    for covariate_id in range( n_covariate ) :
        covariate_label.append( f'x_{covariate_id}' )
    #
    # parent_name_id
    parent_node_id = None
    for row in root_table['option'] :
        if row['option_name'] == 'parent_node_name' :
            parent_node_name = row['option_value']
            parent_node_id   = at_cascade.table_name2id(
                root_table['node'], 'node', parent_node_name
            )
    assert not parent_node_id is None
    #
    # covariate_avg
    covariate_avg = list()
    for avg_node_id in range( len(root_table['node'] ) ) :
        assert len( covariate_avg ) == avg_node_id
        covariate_avg.append( None )
        #
        # is_decendant
        is_descendant = list()
        for (node_id, row) in enumerate(root_table['node']) :
            this_is_descendant = node_id == avg_node_id
            ancestor_node_id   = row['parent']
            while not ancestor_node_id is None :
                if ancestor_node_id == avg_node_id :
                    this_is_descendant = True
                ancestor_row     = root_table['node'][ancestor_node_id]
                ancestor_node_id = ancestor_row['parent']
            is_descendant.append( this_is_descendant)
        #
        # data_subset_list
        data_subset_list = list()
        for (data_id, data_row) in enumerate(root_table['data']) :
            node_id = data_row['node_id']
            if is_descendant[node_id] :
                in_bounds = True
                for covariate_id in range( n_covariate ) :
                    label               = covariate_label[covariate_id]
                    covariate_value     = data_row[label]
                    covariate_row       = root_table['covariate'][covariate_id]
                    reference           = covariate_row['reference']
                    max_difference      = covariate_row['max_difference']
                    assert not reference is None
                    #
                    if max_difference is None :
                        max_difference = math.inf
                    if covariate_value is None :
                        covariate_value = reference
                    abs_difference      = abs( covariate_value - reference )
                    in_bounds = in_bounds and abs_difference <= max_difference
                if in_bounds :
                    data_subset_list.append( data_id )
        #
        # covariate_value
        covariate_value = list()
        for covariate_id in range( n_covariate ) :
            covariate_value.append( list() )
        for data_id in data_subset_list :
            data_row = root_table['data'][data_id]
            for covariate_id in range( n_covariate ) :
                covariate_row  = root_table['covariate'][covariate_id]
                max_difference = covariate_row['max_difference']
                cov_value      = data_row[ covariate_label[covariate_id] ]
                if not cov_value is None :
                    if max_difference is None or max_difference == math.inf :
                        covariate_value[covariate_id].append(cov_value)
        #
        # covariate_avg[avg_node_id]
        covariate_avg[avg_node_id] = list()
        for covariate_id in range( n_covariate ) :
            cov_list = covariate_value[covariate_id]
            if len( cov_list ) == 0 :
                avg = None
            else :
                avg = sum(cov_list) / len(cov_list)
            covariate_avg[avg_node_id].append( avg )
    #
    # all_table['all_cov_reference']
    for row in all_table['all_cov_reference'] :
        if row['split_reference_id'] == split_reference_id :
            covariate_id = row['covariate_id']
            node_id      = row['node_id']
            avg          =  covariate_avg[node_id][covariate_id]
            if not avg is None :
                row['reference'] = avg
    new        = False
    connection = dismod_at.create_connection(all_node_database, new)
    dismod_at.replace_table(
        connection, 'all_cov_reference', all_table['all_cov_reference']
    )
    #
    return
