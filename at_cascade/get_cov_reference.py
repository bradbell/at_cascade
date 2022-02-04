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
{xsrst_begin get_cov_reference}}

Get Covariate Reference Values
##############################

Syntax
******
{xsrst_file
    # BEGIN syntax
    # END syntax
}

fit_node_database
*****************
This argument can't be ``None`` and
is an :ref:`glossary.input_node_database`.
Only the following tables in this database are used:
option, data, node, and covariate.
Note of the tables are modified.

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
Only the

all_node_database
*****************
This argument can't be ``None`` and is the :ref:all_node_db`.
Only the :ref:`all_option_table` and :ref:`split_reference_table` are used.

all_option Table
================
The :ref:`all_option_table.split_covariate_name` and
:ref:`all_option_table.absolute_covariates` rows of this table
(if they exist) are the only rows of this table that are used.

parent_node_id
**************
This is the dismod_at parent node that the covariate reference values
correspond to.

split_reference_id
******************
This is the :ref:`split_reference_table.split_reference_id` that the
covariate reference values correspond to.

cov_reference_list
******************
This return value is a ``list`` with length equal to the
length of the covariate table.
The :ref:`all_option_table.absolute_covariates` have the same reference value
as in the covariate table.
The splitting covariate has reference value corresponding to
*split_reference_id*.
The :ref:`relative covariates<glossary.relative_covariate>`
have reference value equal to
the average of the covariates int the data table.
Only rows of the data table that get included in the fit for
this *parent_node_id* and *split_reference_id* are included in the average.
In addition, null values for a covariate are not included in the average.
If there are no values to average, None is returned as the reference.


2DO
***
This is a list of things to do before removing the all_cov_reference table
using this routine.

1.  Change all the examples to use this routine for covariate reference values.

2.  Remove :ref:`create_all_node_db.all_cov_reference` from
    create_all_node_db argument list.

3.  Change glossary entry for fit_node_database
    :ref:`glossary.fit_node_database.covariate_table`.
    Change all_option entry for :ref:`all_option_table.absolute_covariates`.

4.  Add assumption that covariate reference values have been replaced using
    this routine in :ref:`check_cascade_node<check_cascade_node>`.

{xsrst_end get_cov_reference}}
'''
import at_cascade
import dismod_at
import math
#
# get_cov_reference(
def get_cov_reference(
# BEGIN syntax
# cov_reference_list = at_cascade.get_cov_reference
    all_node_database  = None,
    fit_node_database  = None,
    parent_node_id     = None,
    split_reference_id = None,
# )
# END syntax
) :
    assert type(all_node_database) == str
    assert type(fit_node_database) == str
    assert type(parent_node_id) == int
    #
    # all_table
    new              = False
    connection       = dismod_at.create_connection(all_node_database, new)
    all_table        = dict()
    for tbl_name in [ 'all_option', 'split_reference' ] :
        all_table[tbl_name] = dismod_at.get_table_dict(connection, tbl_name)
    connection.close()
    #
    # chekc split_reference_id
    if len( all_table['split_reference'] ) == 0 :
        assert split_reference_id == None
    else :
        assert type(split_reference_id) == int
    #
    # root_table
    new        = False
    connection = dismod_at.create_connection(fit_node_database, new)
    root_table = dict()
    for tbl_name in [ 'option', 'data', 'node', 'covariate', ] :
        root_table[tbl_name] = dismod_at.get_table_dict(connection, tbl_name)
    connection.close()
    #
    # cov_info
    cov_info = at_cascade.get_cov_info(
        all_table['all_option'],
        root_table['covariate'],
        all_table['split_reference']
    )
    #
    # rel_covariate_id_set
    rel_covariate_id_set = cov_info['rel_covariate_id_set']
    #
    # split_covariate_id
    split_covariate_id = None
    if len( all_table['split_reference'] ) > 0 :
        split_covariate_id = cov_info['split_covariate_id']
    #
    # check max_difference
    for covariate_id in rel_covariate_id_set :
        covariate_row  = root_table['covariate'][covariate_id]
        max_difference = covariate_row['max_difference']
        if not max_difference in [ None, math.inf ] :
            msg  = f'get_cov_reference: covariate_id = {covariate_id}\n'
            msg += 'is a relative covariate and '
            msg += f'max_difference = {max_difference} is not None or infinity'
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
    # is_decendant
    is_descendant = set()
    for (node_id, row) in enumerate(root_table['node']) :
        this_is_descendant = node_id == parent_node_id
        ancestor_node_id   = row['parent']
        while not ancestor_node_id is None :
            if ancestor_node_id == parent_node_id :
                this_is_descendant = True
            ancestor_row     = root_table['node'][ancestor_node_id]
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
                covariate_row   = root_table['covariate'][covariate_id]
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
    # cov_reference_list
    cov_reference_list = list()
    for covariate_id in range( n_covariate) :
        #
        # reference
        reference = root_table['covariate'][covariate_id]['reference']
        if covariate_id == split_covariate_id :
            #
            # reference
            row       = all_table['split_reference'][split_reference_id]
            reference = row['split_reference_value']
        if covariate_id in rel_covariate_id_set :
            #
            # covariate_list
            covariate_row  = root_table['covariate'][covariate_id]
            covariate_list = list()
            for data_id in data_subset_list :
                data_row  = root_table['data'][data_id]
                cov_value = data_row[ covariate_label[covariate_id] ]
                if not cov_value is None :
                    covariate_list.append(cov_value)
            #
            # reference
            if len( covariate_list ) == 0 :
                reference = None
            else :
                reference = sum(covariate_list) / len(covariate_list)
        #
        # cov_reference_list
        cov_reference_list.append(reference)
    # -------------------------------------------------------------------------
    return cov_reference_list
