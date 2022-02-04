# -----------------------------------------------------------------------------
# at_cascade: Cascading Dismod_at Analysis From Parent To Child Regions
#           Copyright (C) 2021-22 University of Washington
#              (Bradley M. Bell bradbell@uw.edu)
#
# This program is distributed under the terms of the
#     GNU Affero General Public License version 3.0 or later
# see http://www.gnu.org/licenses/agpl.txt
# -----------------------------------------------------------------------------
'''
{xsrst_begin set_cov_reference}}

Set Relative Covariate Reference Values
#######################################

Syntax
******
{xsrst_file
    # BEGIN syntax
    # END syntax
}

fit_node_database
*******************
This argument can't be ``None`` and
is an :ref:`glossary.input_node_database`.
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
to the average value for the covariate in the data table.
Only non-null covariate values,
and covariate values within the max difference limit,
are included in the average.

all_node_database
*****************
This argument can't be ``None`` and is the :ref:all_node_db`.
Only the :ref:`all_option_table` is used.

all_option Table
================
The :ref:`all_option_table.split_covariate_name` and
:ref:`all_option_table.absolute_covariates` rows of this table
(if they exist) are the only rows of this table that are used.

2DO
***
This is a list of things to do before removing the all_cov_reference table
using this routine.

1.  Change all the examples to use this routine for covariate reference values.

2.  Remove :ref:`create_all_node_db.all_cov_reference` from
    create_all_node_db argument list.

2.  Change glossary entry fit_node_database
    :ref:`glossary.fit_node_database.covariate_table`.

{xsrst_end set_cov_reference}}
'''
import at_cascade
import dismod_at
import math
#
# set_cov_reference(
def set_cov_reference(
# BEGIN syntax
# at_cascade.set_cov_reference
    all_node_database  = None,
    fit_node_database  = None,
# )
# END syntax
) :
    #
    # all_option_table
    new              = False
    connection       = dismod_at.create_connection(all_node_database, new)
    all_option_table = dismod_at.get_table_dict(connection, 'all_option')
    split_reference_table = dismod_at.get_table_dict(
        connection, 'split_reference'
    )
    connection.close()
    #
    # fit_table
    new        = False
    connection = dismod_at.create_connection(fit_node_database, new)
    fit_table  = dict()
    for tbl_name in [
        'option',
        'data',
        'node',
        'covariate',
    ] :
        fit_table[tbl_name] = dismod_at.get_table_dict(connection, tbl_name)
    connection.close()
    #
    # cov_info
    cov_info = at_cascade.get_cov_info(
        all_option_table, fit_table['covariate'], split_reference_table
    )
    #
    # rel_covariate_id_set
    rel_covariate_id_set = cov_info['rel_covariate_id_set']
    #
    # check max_difference
    for covariate_id in rel_covariate_id_set :
        covariate_row  = fit_table['covariate'][covariate_id]
        max_difference = covariate_row['max_difference']
        if not max_difference in [ None, math.inf ] :
            msg  = f'set_cov_reference: covariate_id = {covariate_id}\n'
            msg += 'is a relative covariate and '
            msg += f'max_difference = {max_difference} is not None or infinity'
            assert False, msg
    #
    # n_covariate
    n_covariate = len( fit_table['covariate'] )
    #
    # covariate_label
    covariate_label = list()
    for covariate_id in range( n_covariate ) :
        covariate_label.append( f'x_{covariate_id}' )
    #
    # parent_name_id
    parent_node_id = None
    for row in fit_table['option'] :
        if row['option_name'] == 'parent_node_name' :
            parent_node_name = row['option_value']
            parent_node_id   = at_cascade.table_name2id(
                fit_table['node'], 'node', parent_node_name
            )
    assert not parent_node_id is None
    #
    # is_decendant
    is_descendant = set()
    for (node_id, row) in enumerate(fit_table['node']) :
        this_is_descendant = node_id == parent_node_id
        ancestor_node_id   = row['parent']
        while not ancestor_node_id is None :
            if ancestor_node_id == parent_node_id :
                this_is_descendant = True
            ancestor_row     = fit_table['node'][ancestor_node_id]
            ancestor_node_id = ancestor_row['parent']
        if this_is_descendant :
            is_descendant.add( node_id )
    #
    # data_subset_list
    data_subset_list = list()
    for (data_id, data_row) in enumerate(root_table['data']) :
        #
        # node_id
        node_id = data_row['node_id']
        if node_id in is_descendant :
            #
            # in_bnd
            in_bnd = True
            for covariate_id in range( n_covariate ) :
                covariate_row   = fit_table['covariate'][covariate_id]
                reference       = covariate_row['reference']
                max_difference  = covariate_row['max_difference']
                if max_difference is None :
                    max_difference = math.inf
                label           = covariate_label[covariate_id]
                covariate_value = data_row[label]
                #
                skip = covariate_value is None
                skip = skip or max_difference == math.inf
                if not skip :
                    abs_diff = abs( covariate_value - reference )
                    in_bnd   = in_bnd and abs_diff <= max_difference
            #
            # data_subset_list
            if in_bnd :
                data_subset_list.append( data_id )
    #
    # fit_table['covariate']
    for covariate_id in rel_covariate_id_set :
        covariate_row  = fit_table['covariate'][covariate_id]
        covariate_list = list()
        for data_id in data_subset_list :
            data_row  = fit_table['data'][data_id]
            cov_value = data_row[ covariate_label[covariate_id] ]
            if not cov_value is None :
                covariate_list.append(cov_value)
        if len( covariate_list ) == 0 :
            avg = 0.0
        else :
            avg = sum(covariate_list) / len(covariate_list)
        fit_table['covariate'][covariate_id]['reference'] = avg
    #
    # covariate table
    new        = False
    connection = dismod_at.create_connection(fit_node_database, new)
    dismod_at.replace_table(connection, tbl_name, fit_table['covariate'])
    # -------------------------------------------------------------------------
    return
