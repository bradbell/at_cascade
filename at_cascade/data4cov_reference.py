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

connection
**********
This is a dismod_at connection to a dismod_at database.
Only the following tables are required:
option, data, node, covariate.

option Table
************
This table must have a row with option_value equal to parent_node_name.
Only this row of the option table is used.

data Table
**********
Only the following columns of this table are used:
data_id, node_id, x_0, ... x_n,
where n is the number of covariates minus one.

covariate_table
================
The ``reference`` column in the covariate table is replaced
by the average of the corresponding covariate in the data table.
Only the rows of the data table that satisfy the following conditions
are included:

1.  The node for the data table row is the parent node or a descendant of
    the parent node.

2.  The difference of each covariate value in the data table row
    from the corresponding reference in the covariate table is
    less than or equal the maximum difference for that covariate.

Only the reference values for covariates that satisfy the following conditions
are modified:

3.  There is at least one row of the data table that satisfies conditions
    1 and 2 for this covariate.

4.  This covariate has maximum difference equal to infinity (or null).

{xsrst_end data4cov_reference}}
'''
import at_cascade
import dismod_at
import math
#
# BEGIN syntax
# data4cov_reference(database)
# END syntax
def data4cov_reference(connection) :
    #
    # tables
    tables = dict()
    for tbl_name in [
        'option',
        'data',
        'node',
        'covariate',
    ] :
        tables[tbl_name] = dismod_at.get_table_dict(connection, tbl_name)
    #
    # parent_name_id
    parent_node_id = None
    for row in tables['option'] :
        if row['option_name'] == 'parent_node_name' :
            parent_node_name = row['option_value']
            parent_node_id   = at_cascade.table_name2id(
                tables['node'], 'node', parent_node_name
            )
    assert not parent_node_id is None
    #
    # is_decendant
    is_descendant = list()
    for (node_id, row) in enumerate(tables['node']) :
        this_is_descendant = node_id == parent_node_id
        ancestor_node_id   = row['parent']
        while not ancestor_node_id is None :
            if ancestor_node_id == parent_node_id :
                this_is_descendant = True
            ancestor_node_id = tables['node'][ancestor_node_id]['parent']
        is_descendant.append( this_is_descendant)
    #
    # n_covariate
    n_covariate = len( tables['covariate'] )
    #
    # covariate_label
    covariate_label = list()
    for covariate_id in range( n_covariate ) :
        covariate_label.append( f'x_{covariate_id}' )
    #
    # data_subset_list
    data_subset_list = list()
    for (data_id, data_row) in enumerate(tables['data']) :
        node_id = data_row['node_id']
        if is_descendant[node_id] :
            in_bounds = True
            for covariate_id in range( n_covariate ) :
                label               = covariate_label[covariate_id]
                covariate_value     = data_row[label]
                covariate_row       = tables['covariate'][covariate_id]
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
        data_row = tables['data'][data_id]
        for covariate_id in range( n_covariate ) :
            covariate_row  = tables['covariate'][covariate_id]
            max_difference = covariate_row['max_difference']
            cov_value      = data_row[ covariate_label[covariate_id] ]
            if not cov_value is None :
                if max_difference is None or max_difference == math.inf :
                    covariate_value[covariate_id].append(cov_value)
    #
    # covariate_avg
    covariate_avg = list()
    for covariate_id in range( n_covariate ) :
        cov_list = covariate_value[covariate_id]
        if len( cov_list ) == 0 :
            covariate_avg.append(None)
        else :
            covariate_avg.append( sum(cov_list) / len(cov_list) )
    #
    # tables['covariate']
    for (covariate_id, row) in enumerate(tables['covariate']) :
        avg = covariate_avg[covariate_id]
        if not avg is None :
            row['reference'] = avg
    dismod_at.replace_table(connection, 'covariate', tables['covariate'])
    #
    return
