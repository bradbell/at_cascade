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
{xsrst_begin child_avgint_table}
{xsrst_spell
    integrands
    mulcov
}

Create avgint Table That Predicts Rates for Child Nodes
#######################################################

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
The avgint table will be placed in this database.
The previous avgint table in this database is lost.
This argument can't be ``None``.

parent_node
===========
We use *parent_node* to refer to the parent node in the
dismod_at option table in the *fit_node_database*.

integrand_table
===============
The integrand table in the *fit_node_database* must include the following:
:ref:`glossary.Sincidence`,
:ref:`glossary.remission`,
:ref:`glossary.mtexcess`.
Integrands corresponding to rates with null parent smoothing id
need not be included.
In addition, the integrand table must include all the covariate multipliers;
i.e., ``mulcov_``\ *mulcov_id* where *mulcov_id* is the id
for any covariate multiplier.
Integrands corresponding to covariate multipliers
with a null group smoothing id need not be included.

avgint Table
************
The new avgint table has all the standard dismod_at columns
plus the following extra columns:

c_age_id
========
This column identifies the age,
in the *fit_node_database*, that this prediction are for.

c_time_id
_========
This column identifies the time,
in the *fit_node_database*, that this prediction are for.

Rectangular Grid
================
For each rate (or covariate multiplier) that has a non-null
parent smoothing (group smoothing) in the *fit_node_database*,
all of the age time pairs in the smoothing are represented
in the new avgint table

{xsrst_end child_avgint_table}
'''
# ----------------------------------------------------------------------------
import dismod_at
# ----------------------------------------------------------------------------
def table_name2id(table, col_name, row_name) :
    for (row_id, row) in enumerate(table) :
        if row[col_name] == row_name :
            return row_id
    assert False
# ----------------------------------------------------------------------------
def child_avgint_table(
# BEGIN syntax
# at_cascade.child_avgint_table(
    all_node_database    = None ,
    fit_node_database = None ,
# )
# END syntax
) :
    # all_cov_reference_table
    new        = False
    connection = dismod_at.create_connection(all_node_database, new)
    all_cov_reference_table = dismod_at.get_table_dict(
        connection, 'all_cov_reference'
    )
    connection.close()
    #
    # fit_tables
    new           = False
    connection    = dismod_at.create_connection(fit_node_database, new)
    fit_tables = dict()
    for name in [
        'age',
        'covariate',
        'integrand',
        'mulcov',
        'node',
        'option',
        'rate',
        'smooth_grid',
        'time',
    ] :
        fit_tables[name] = dismod_at.get_table_dict(connection, name)
    connection.close()
    #
    # minimum_age_id
    minimum_age_id = 0
    minimum_age    = fit_tables['age'][minimum_age_id]['age']
    for (age_id, row) in enumerate(fit_tables['age']) :
        if row['age'] < minimum_age :
            minimum_age_id = age_id
            minimum_age    = row['age']
    #
    # rate_table
    rate_table = fit_tables['rate']
    #
    # node_table
    node_table = fit_tables['node']
    #
    # n_covariate
    n_covariate = len( fit_tables['covariate'] )
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
    # child_all_cov_reference
    child_all_cov_reference = dict()
    for (node_id, row) in enumerate(node_table) :
        if row['parent'] == parent_node_id :
            reference = n_covariate * [0.0]
            for row in all_cov_reference_table :
                if row['node_id'] == node_id :
                    covariate_id = row['covariate_id']
                    reference[covariate_id] = row['reference']
            child_all_cov_reference[node_id] = reference
    #
    # tbl_name
    tbl_name = 'avgint'
    #
    # col_name
    col_name = [
        'integrand_id',
        'node_id',
        'subgroup_id',
        'weight_id',
        'age_lower',
        'age_upper',
        'time_lower',
        'time_upper',
    ]
    #
    # col_tyype
    col_type = [
        'integer',
        'integer',
        'integer',
        'integer',
        'real',
        'real',
        'real',
        'real',
    ]
    #
    # add covariates to col_name and col_type
    for covariate_id in range( n_covariate ) :
        col_name.append( 'x_' + str(covariate_id) )
        col_type.append( 'real' )
    #
    # add the smoothing grid columns to col_name and col_type
    col_name += [ 'c_age_id', 'c_time_id' ]
    col_type += 2 * ['integer']
    #
    # name_rate2integrand
    name_rate2integrand = {
        'pini':   'prevalence',
        'iota':   'Sincidence',
        'rho':    'remission',
        'chi':    'mtexcess',
    }
    #
    # initialize row_list
    row_list = list()
    #
    # mulcov_id
    for mulcov_id in range( len( fit_tables['mulcov'] ) ) :
        #
        # mulcov_row
        mulcov_row = fit_tables['mulcov'][mulcov_id]
        #
        # group_smooth_id
        group_smooth_id = mulcov_row['group_smooth_id']
        if not group_smooth_id is None :
            #
            # integrand_id
            integrand_name  = 'mulcov_' + str(mulcov_id)
            integrand_table = fit_tables['integrand']
            integrand_id    = table_name2id(
                integrand_table, 'integrand_name', integrand_name
            )
            #
            # grid_row
            for grid_row in fit_tables['smooth_grid'] :
                if grid_row['smooth_id'] == group_smooth_id :
                    #
                    # age_id
                    age_id    = grid_row['age_id']
                    age_lower = fit_tables['age'][age_id]['age']
                    age_upper = age_lower
                    #
                    # time_id
                    time_id    = grid_row['time_id']
                    time_lower = fit_tables['time'][time_id]['time']
                    time_upper = time_lower
                    #
                    # row
                    node_id     = None
                    subgroup_id = 0
                    weight_id   = None
                    row = [
                        integrand_id,
                        node_id,
                        subgroup_id,
                        weight_id,
                        age_lower,
                        age_upper,
                        time_lower,
                        time_upper,
                    ]
                    row += n_covariate * [ None ]
                    row += [ age_id, time_id, ]
                    #
                    # add to row_list
                    row_list.append( row )
    #
    # rate_name
    for rate_name in name_rate2integrand :
        #
        # rate_id
        rate_id = table_name2id(rate_table, 'rate_name', rate_name)
        #
        # parent_smooth_id
        parent_smooth_id = rate_table[rate_id]['parent_smooth_id']
        if not parent_smooth_id is None :
            #
            # integrand_id
            integrand_name  = name_rate2integrand[rate_name]
            integrand_table = fit_tables['integrand']
            integrand_id    = table_name2id(
                integrand_table, 'integrand_name', integrand_name
            )
            #
            # grid_row
            for grid_row in fit_tables['smooth_grid'] :
                if grid_row['smooth_id'] == parent_smooth_id :
                    #
                    # age_id
                    age_id    = grid_row['age_id']
                    age_lower = fit_tables['age'][age_id]['age']
                    age_upper = age_lower
                    #
                    # prior for pini must use age index zero
                    if rate_name == 'pini' :
                        assert age_id == minimum_age_id
                    #
                    # time_id
                    time_id    = grid_row['time_id']
                    time_lower = fit_tables['time'][time_id]['time']
                    time_upper = time_lower
                    #
                    # node_id
                    for node_id in child_all_cov_reference :
                        #
                        # row
                        subgroup_id = 0
                        weight_id   = None
                        row = [
                            integrand_id,
                            node_id,
                            subgroup_id,
                            weight_id,
                            age_lower,
                            age_upper,
                            time_lower,
                            time_upper,
                        ]
                        row += child_all_cov_reference[node_id]
                        row += [ age_id, time_id, ]
                        #
                        # add to row_list
                        row_list.append( row )
    #
    # put new avgint table in fit_node_database
    new           = False
    connection    = dismod_at.create_connection(fit_node_database, new)
    command       = 'DROP TABLE IF EXISTS ' + tbl_name
    dismod_at.sql_command(connection, command)
    dismod_at.create_table(connection, tbl_name, col_name, col_type, row_list)
    connection.close()
