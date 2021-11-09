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
Only the following tables in this database are used:
option, data, node, covariate and only the covariate
table is modified.

option Table
============
This table must have a row with option_value equal to parent_node_name.
Only this row of the option table is used.

data Table
==========
Only the following columns of this table are used:
data_id, node_id, x_0, ... x_n,
where n is the number of covariates minus one.

covariate Table
===============
The covariate reference value for the
:ref:`relative covariates <glossary.relative_covariate>` is changed
to agree with the new value in the all_cov_reference table
(described below) for the :ref:`all_cov_reference_table.node_id`
and :ref:`all_cov_reference_table.split_reference_id` corresponding
to the *root_node_database*.

all_node_database
*****************
This argument can't be ``None`` and is the :ref:all_node_db`.
Only the :ref:`all_cov_reference_table`
and :ref:`all_option_table` are used.

all_option Table
================
The :ref:`all_option_table.split_list` and
:ref:`all_option_table.absolute_covariates` rows of this table
(if they exist) are the only rows of this table that are used.

trace_interval
**************
If *trace_interval* is ``None`` no tracking is printed.
Otherwise, a message will once per *trace_interval* nodes to indicate
the progress of this processing (because it can take a while).

all_cov_reference Table
=======================
The :ref:`all_cov_reference_table.reference` created
using the average of the covariates in the data table.
(The average is rounded off to and unspecified number of digits.
This makes it easier to set reference values
in the :ref:`glossary.root_node_database` to be the same.)

1.  If there is an all_cov_reference table on input,
    all its information is lost.

2.  The node_id for the data table row is the
    :ref:`all_cov_reference_table.node_id` for the new all_cov_reference row,
    or a descendant of all_cov_reference node.

3.  The difference of all the covariate values in the data table row
    from the corresponding reference in the covariate table is
    less than or equal the maximum difference for that covariate.

4.  If there is no row of the data table that satisfies conditions
    1 and 2 for this all_cov_reference row,
    the resulting reference value is zero.

{xsrst_end data4cov_reference}}
'''
import at_cascade
import dismod_at
import math
#
# data4cov_reference(
def data4cov_reference(
# BEGIN syntax
# at_cascade.data4cov_reference
    all_node_database  = None,
    root_node_database = None,
    trace_interval     = False,
# )
# END syntax
) :
    #
    # all_option_table
    new              = False
    connection       = dismod_at.create_connection(all_node_database, new)
    all_option_table = dismod_at.get_table_dict(connection, 'all_option')
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
    if not trace_interval is None :
        assert 0 < trace_interval
        n_node = len( root_table['node'] )
        print( 'data2cov_reference: n_node = ', n_node )
    #
    # cov_info
    cov_info = at_cascade.get_cov_info(
        all_option_table, root_table['covariate']
    )
    #
    # rel_covariate_id_set
    rel_covariate_id_set = cov_info['rel_covariate_id_set']
    #
    # check max_difference
    for covariate_id in rel_covariate_id_set :
        covariate_row  = root_table['covariate'][covariate_id]
        max_difference = covariate_row['max_difference']
        if not max_difference in [ None, math.inf ] :
            msg  = f'data4cov_reference: covariate_id = {covariate_id}\n'
            msg += 'is a relative covariate and '
            msg += f'max_difference = {max_difference}'
            assert False, msg
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
    # split_reference_list, split_covariate_id, n_split
    if 'split_list' in cov_info :
        split_reference_list  = cov_info['split_reference_list']
        split_covariate_id    = cov_info['split_covariate_id']
        n_split               = len(split_reference_list)
    else :
        split_reference_list  = None
        split_covariate_id    = None
        n_split               = 1
    #
    # -------------------------------------------------------------------------
    # row_list
    row_list = list()
    for avg_node_id in range( len(root_table['node'] ) ) :
        #
        if not trace_interval is None :
            if avg_node_id % trace_interval == 0 :
                print('node_id = ', avg_node_id)
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
        # split_reference_id, split_reference
        for k in range( n_split ) :
            if 'split_list' in cov_info :
                split_reference_id = k
                split_reference    = split_reference_list[k]
            else :
                row  = root_table['covariate'][split_covariate_id]
                split_reference    = row['reference']
                split_reference_id = None
            #
            # data_subset_list
            data_subset_list = list()
            for (data_id, data_row) in enumerate(root_table['data']) :
                node_id = data_row['node_id']
                if is_descendant[node_id] :
                    in_bnd = True
                    for covariate_id in range( n_covariate ) :
                        label           = covariate_label[covariate_id]
                        covariate_value = data_row[label]
                        covariate_row   = root_table['covariate'][covariate_id]
                        reference       = covariate_row['reference']
                        if covariate_id == split_covariate_id :
                            reference   = split_reference
                        max_difference  = covariate_row['max_difference']
                        if max_difference is None :
                            max_difference = math.inf
                        #
                        skip = covariate_value is None
                        skip = skip or max_difference == math.inf
                        if not skip :
                            abs_diff = abs( covariate_value - reference )
                            in_bnd   = in_bnd and abs_diff <= max_difference
                    if in_bnd :
                        data_subset_list.append( data_id )
            #
            # covariate_value
            covariate_value = dict()
            for covariate_id in rel_covariate_id_set :
                covariate_value[covariate_id] = list()
            for data_id in data_subset_list :
                data_row = root_table['data'][data_id]
                for covariate_id in rel_covariate_id_set :
                    covariate_row  = root_table['covariate'][covariate_id]
                    cov_value      = data_row[ covariate_label[covariate_id] ]
                    if not cov_value is None :
                        covariate_value[covariate_id].append(cov_value)
            #
            # all_cov_reference
            for covariate_id in rel_covariate_id_set :
                cov_list = covariate_value[covariate_id]
                if len( cov_list ) == 0 :
                    avg = 0.0
                else :
                    avg = sum(cov_list) / len(cov_list)
                #
                # row_list
                node_id   = avg_node_id
                reference = float( f'{avg:.4g}' )
                row = [ node_id, covariate_id, split_reference_id, reference ]
                row_list.append( row )
    # -------------------------------------------------------------------------
    # all_cov_reference table
    new        = False
    connection = dismod_at.create_connection(all_node_database, new)
    command    = 'DROP TABLE IF EXISTS all_cov_reference'
    dismod_at.sql_command(connection, command)
    tbl_name   = 'all_cov_reference'
    col_name   = ['node_id', 'covariate_id', 'split_reference_id', 'reference']
    col_type   = ['integer', 'integer',      'integer',            'real']
    dismod_at.create_table(
        connection, tbl_name, col_name, col_type, row_list
    )
    connection.close()
    # -------------------------------------------------------------------------
    # root_table['covariate']
    for row in row_list :
        (node_id, covariate_id, split_reference_id, reference) = row
        if split_reference_id == cov_info['split_reference_id'] \
            and node_id == parent_node_id :
                root_table['covariate'][covariate_id]['reference'] = reference
    new        = False
    connection = dismod_at.create_connection(root_node_database, new)
    dismod_at.replace_table(connection, 'covariate', root_table['covariate'])
    connection.close()
    # -------------------------------------------------------------------------
    #
    if not trace_interval is None :
        print('end: data4cov_reference')
    return
