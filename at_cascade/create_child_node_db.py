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
{xsrst_begin create_child_node_db}
{xsrst_spell
    var
    init
}

Create Child Database From Fit in Parent Database
#################################################

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

parent_node_database
********************
is a python string containing the name of a :ref:`glossary.fit_node_database`.
The two predict tables (mentioned below)
are used to create priors in the child node databases.
This argument can't be ``None``.

parent_node
===========
We use *parent_node* to refer to the parent node in the
dismod_at option table in the *parent_node_database*.

sample Table
============
The sample table contains
the results of a dismod_at sample command for both the fixed and random effects.

avgint Table
============
The avgint table predicts for the child nodes
and comes from :ref:`child_avgint_table`.

predict Table
=============
The predict table contains
The results of a predict command using the sample table
and the avgint table corresponding to :ref:`child_avgint_table`.

c_predict_fit_var Table
=======================
The c_predict_fit_var table contains
the results of a dismod_at sample command with the fit_var option
and then moving the predict table to c_predict and renaming the
column predict_id to c_predict_id.

c_avgint Table
==============
The c_avgint table contains the original version of the avgint table
that predicts for the parent node and is a version of the root node database
avgint table with only the node_id column modified.

child_node_databases
********************
is a python dictionary and if *child_name* is a key for *child_node_databases*,
*child_name* is a :ref:`glossary.node_name` and a child of the *parent_node*.

-   For each *child_name*, *child_node_databases[child_name]* is the name of
    *fit_node_database* that is created by this command.
-   In this database, *child_name* will be the parent node in
    the dismod_at option table.
-   The rate table is changed to have null priors for omega;
    see :ref:`omega_constraint` for properly setting these priors.
-   The difference priors are the same as in th parent node database.
-   The value priors are similar, the difference is that the mean
    and standard deviation are replaced using the predict tables in
    the *parent_node_database*.
-   Only the dismod_at input tables are significant in the child node databases;
    e.g., an init command should be executed before any other dismod_at
    commands (except possibly a set command).
-   The avgint table is a copy of the c_avgint table in the parent node
    database with the node_id replaced by the corresponding child node id.
-   The following tables are the same as in the parent node database:
    age, data, density, integrand, node, subgroup, time, weight, weight_grid.

This argument can't be ``None``.

{xsrst_end create_child_node_db}
'''
# ----------------------------------------------------------------------------
import math
import copy
import shutil
import statistics
import dismod_at
# ----------------------------------------------------------------------------
def add_index_to_name(table, name_col) :
    row   = table[-1]
    name  = row[name_col]
    ch    = name[-1]
    while name != '' and name[-1] in '0123456789' :
        name = name[: -1]
    if name[-1] == '_' :
        name = name[: -1]
    row[name_col] = name + '_' + str( len(table) )
# ----------------------------------------------------------------------------
def table_name2id(tables, tbl_name, row_name) :
    col_name = f'{tbl_name}_name'
    for (row_id, row) in enumerate(tables[tbl_name]) :
        if row[col_name] == row_name :
            return row_id
    msg = f"Can't find {col_name} = {row_name} in table {tbl_name}"
    assert False, msg
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
# The smoothing for the new child_tables['smooth_grid'] row is the most
# recent smoothing added to child_tables['smooth']; i.e., its smoothing_id
# is len( child_tables['smooth'] ) - 1.
def add_child_grid_row(
    parent_fit_var,
    parent_sample,
    parent_tables,
    child_tables,
    parent_grid_row,
    integrand_id,
    child_node_id,
) :
    # -----------------------------------------------------------------------
    # value_prior
    # -----------------------------------------------------------------------
    #
    # parent_prior_id
    parent_prior_id    = parent_grid_row['value_prior_id']
    #
    # child_const_value
    # child_value_prior_id
    child_const_value    = parent_grid_row['const_value']
    child_value_prior_id = None
    if child_const_value is None :
        #
        # parent_prior_row
        parent_prior_row = parent_tables['prior'][parent_prior_id]
        #
        # child_const_value
        # child_value_prior_id
        if parent_prior_row['lower'] == parent_prior_row['upper'] :
            child_const_value = parent_prior_row['lower']
            assert child_value_prior_id is None
        else :
            assert child_const_value is None
            child_value_prior_id = len( child_tables['prior'] )
            #
            # child_prior_row
            child_prior_row  = copy.copy( parent_prior_row )
            #
            # key
            age_id    = parent_grid_row['age_id']
            time_id   = parent_grid_row['time_id']
            key       = (integrand_id, child_node_id, age_id, time_id)
            #
            # mean
            mean = parent_fit_var[key]
            #
            # std
            eta        = parent_prior_row['eta']
            if eta is None :
                std  = statistics.stdev(parent_sample[key], xbar=mean)
            else:
                # The asymptotic statistics were computed in log space
                # and then transformed to original space.
                #
                # log_sample
                log_sample = list()
                for sample in parent_sample[key] :
                    log_sample.append( math.log( sample + eta ) )
                #
                # log_std
                log_mean = math.log(mean + eta)
                log_std  = statistics.stdev(log_sample, xbar = log_mean)
                #
                # inverse log transformation
                std      = (math.exp(log_std) - 1) * (mean + eta)
            #
            # child_prior_row
            child_prior_row['mean']        = mean
            child_prior_row['std']         = std
            #
            # child_tables['prior']
            child_tables['prior'].append( child_prior_row )
            add_index_to_name( child_tables['prior'], 'prior_name' )
    # -----------------------------------------------------------------------
    # dage_prior
    # -----------------------------------------------------------------------
    parent_prior_id       = parent_grid_row['dage_prior_id']
    if parent_prior_id == None :
        child_dage_prior_id = None
    else :
        parent_prior_row      = parent_tables['prior'][parent_prior_id]
        child_prior_row       = copy.copy( parent_prior_row )
        child_dage_prior_id   = len( child_tables['prior'] )
        child_tables['prior'].append( child_prior_row )
        add_index_to_name( child_tables['prior'], 'prior_name' )
    # -----------------------------------------------------------------------
    # dtime_prior
    # -----------------------------------------------------------------------
    parent_prior_id       = parent_grid_row['dtime_prior_id']
    if parent_prior_id == None :
        child_dtime_prior_id = None
    else :
        parent_prior_row       = parent_tables['prior'][parent_prior_id]
        child_prior_row        = copy.copy( parent_prior_row )
        child_dtime_prior_id   = len( child_tables['prior'] )
        child_tables['prior'].append( child_prior_row )
        add_index_to_name( child_tables['prior'], 'prior_name' )
    # -----------------------------------------------------------------------
    # child_grid_row
    child_grid_row = copy.copy( parent_grid_row )
    child_grid_row['value_prior_id']  = child_value_prior_id
    child_grid_row['const_value']     = child_const_value
    child_grid_row['dage_prior_id']   = child_dage_prior_id
    child_grid_row['dtime_prior_id']  = child_dtime_prior_id
    #
    # child_tables['smooth_grid']
    child_grid_row['smooth_id']  = len( child_tables['smooth'] ) - 1
    child_tables['smooth_grid'].append( child_grid_row )
# ----------------------------------------------------------------------------
def create_child_node_db(
# BEGIN syntax
# at_cascade.create_child_node_db(
    all_node_database    = None ,
    parent_node_database = None ,
    child_node_databases = None ,
# )
# END syntax
) :
    # ------------------------------------------------------------------------
    # all_cov_reference_table
    new        = False
    connection = dismod_at.create_connection(all_node_database, new)
    all_cov_reference_table = dismod_at.get_table_dict(
        connection, 'all_cov_reference'
    )
    connection.close()
    #
    # parent_tables
    new           = False
    connection    = dismod_at.create_connection(parent_node_database, new)
    parent_tables = dict()
    for name in [
        'avgint',
        'c_avgint',
        'c_predict_fit_var',
        'covariate',
        'density',
        'fit_var',
        'integrand',
        'mulcov',
        'node',
        'option',
        'prior',
        'predict',
        'rate',
        'sample',
        'smooth',
        'smooth_grid',
        'var',
    ] :
        parent_tables[name] = dismod_at.get_table_dict(connection, name)
    connection.close()
    #
    # name_rate2integrand
    name_rate2integrand = {
        'pini'  : 'prevalence',
        'iota'  : 'Sincidence',
        'rho'   : 'remission',
        'chi'   : 'mtexcess',
    }
    #
    # parent_fit_var
    parent_fit_var = dict()
    for predict_row in parent_tables['c_predict_fit_var'] :
        avgint_id          = predict_row['avgint_id']
        avgint_row         = parent_tables['avgint'][avgint_id]
        integrand_id       = avgint_row['integrand_id']
        node_id            = avgint_row['node_id']
        age_id             = avgint_row['c_age_id']
        time_id            = avgint_row['c_time_id']
        key                = (integrand_id, node_id, age_id, time_id)
        assert not key in parent_fit_var
        parent_fit_var[key] = predict_row['avg_integrand']
    #
    # parent_sample
    parent_sample = dict()
    for predict_row in parent_tables['predict'] :
        avgint_id          = predict_row['avgint_id']
        avgint_row         = parent_tables['avgint'][avgint_id]
        integrand_id       = avgint_row['integrand_id']
        node_id            = avgint_row['node_id']
        age_id             = avgint_row['c_age_id']
        time_id            = avgint_row['c_time_id']
        key                = (integrand_id, node_id, age_id, time_id)
        if not key in parent_sample :
            parent_sample[key] = list()
        parent_sample[key].append( predict_row['avg_integrand'] )
    #
    # parent_node_name
    parent_node_name = None
    for row in parent_tables['option'] :
        assert row['option_name'] != 'parent_node_id'
        if row['option_name'] == 'parent_node_name' :
            parent_node_name = row['option_value']
    assert parent_node_name is not None
    #
    # parent_node_id
    parent_node_id = table_name2id(parent_tables, 'node', parent_node_name)
    #
    for child_name in child_node_databases :
        # ---------------------------------------------------------------------
        # create child_node_databases[child_name]
        # ---------------------------------------------------------------------
        #
        # child_node_tables
        child_tables = dict()
        for name in [
            'c_avgint',
            'covariate',
            'mulcov',
            'option',
            'rate',
        ] :
            child_tables[name] = copy.deepcopy(parent_tables[name])
        child_tables['prior']       = list()
        child_tables['smooth']      = list()
        child_tables['smooth_grid'] = list()
        child_tables['nslist']      = list()
        child_tables['nslist_pair'] = list()
        #
        # child_node_id
        child_node_id = table_name2id(parent_tables, 'node', child_name)
        assert parent_tables['node'][child_node_id]['parent'] == parent_node_id
        #
        # child_node_database = parent_node_database
        child_database = child_node_databases[child_name]
        shutil.copyfile(parent_node_database, child_database)
        #
        # child_connection
        new        = False
        child_connection = dismod_at.create_connection(child_database, new)
        #
        # child_tables['option']
        for row in child_tables['option'] :
            if row['option_name'] == 'parent_node_name' :
                row['option_value'] = child_name
        tbl_name = 'option'
        #
        # child_tables['covariate']
        for child_row in child_tables['covariate'] :
            child_row['reference'] = None
        for row in all_cov_reference_table :
            if row['node_id'] == child_node_id :
                covariate_id           = row['covariate_id']
                child_row              = child_tables['covariate'][covariate_id]
                child_row['reference'] = row['reference']
        for child_row in child_tables['covariate'] :
            assert not child_row['reference'] is None
        #
        # --------------------------------------------------------------------
        # child_tables['mulcov']
        # and corresponding entries in the following child tables:
        # smooth, smooth_grid, and prior
        for (mulcov_id, child_mulcov_row) in enumerate(child_tables['mulcov']) :
            assert child_mulcov_row['subgroup_smooth_id'] is None
            parent_smooth_id = child_mulcov_row['group_smooth_id']
            if not parent_smooth_id is None :
                #
                # integrand_id
                name         = 'mulcov_' + str(mulcov_id)
                integrand_id = table_name2id(parent_tables, 'integrand', name)
                #
                smooth_row = parent_tables['smooth'][parent_smooth_id]
                smooth_row = copy.copy(smooth_row)
                #
                # update: child_tables['smooth']
                assert smooth_row['mulstd_value_prior_id'] is None
                assert smooth_row['mulstd_dage_prior_id']  is None
                assert smooth_row['mulstd_dtime_prior_id'] is None
                #
                child_smooth_id = len(child_tables['smooth'])
                smooth_row['smooth_name'] += f'_{child_smooth_id}'
                child_tables['smooth'].append(smooth_row)
                #
                # change child_tables['mulcov'] to use the new smoothing
                child_mulcov_row['group_smooth_id'] = child_smooth_id
                #
                # add rows for this smoothing to
                # child_tables['smooth_grid']
                node_id = None
                for parent_grid_row in parent_tables['smooth_grid'] :
                    if parent_grid_row['smooth_id'] == parent_smooth_id :
                        add_child_grid_row(
                            parent_fit_var,
                            parent_sample,
                            parent_tables,
                            child_tables,
                            parent_grid_row,
                            integrand_id,
                            node_id,
                        )

        # --------------------------------------------------------------------
        # child_tables['rate']
        # and corresponding entries in the following child tables:
        # smooth, smooth_grid, and prior
        for child_rate_row in child_tables['rate'] :
            rate_name        = child_rate_row['rate_name']
            #
            # parent_smooth_id
            parent_smooth_id = None
            if rate_name in name_rate2integrand :
                assert child_rate_row['child_nslist_id'] is None
                parent_smooth_id = child_rate_row['parent_smooth_id']
            else :
                # proper priors for omega are set by omega_constraint routine
                assert rate_name == 'omega'
                child_rate_row['parent_smooth_id'] = None
                child_rate_row['child_smooth_id']  = None
                child_rate_row['child_nslist_id']  = None
            if not parent_smooth_id is None :
                #
                # integrand_id
                integrand_name  = name_rate2integrand[rate_name]
                integrand_id = table_name2id(
                    parent_tables, 'integrand', integrand_name
                )
                #
                smooth_row = parent_tables['smooth'][parent_smooth_id]
                smooth_row = copy.copy(smooth_row)
                #
                assert smooth_row['mulstd_value_prior_id'] is None
                assert smooth_row['mulstd_dage_prior_id']  is None
                assert smooth_row['mulstd_dtime_prior_id'] is None
                #
                # update: child_tables['smooth']
                # for case where its is the parent
                child_smooth_id = len(child_tables['smooth'])
                smooth_row['smooth_name'] += f'_{child_smooth_id}'
                child_tables['smooth'].append(smooth_row)
                #
                # change child_tables['rate'] to use the new smoothing
                child_rate_row['parent_smooth_id'] = child_smooth_id
                #
                # add rows for this smoothing to
                # child_tables['smooth_grid']
                for parent_grid_row in parent_tables['smooth_grid'] :
                    if parent_grid_row['smooth_id'] == parent_smooth_id :
                        add_child_grid_row(
                            parent_fit_var,
                            parent_sample,
                            parent_tables,
                            child_tables,
                            parent_grid_row,
                            integrand_id,
                            child_node_id,
                        )
            #
            # parent_smooth_id
            parent_smooth_id = None
            if rate_name in name_rate2integrand :
                parent_smooth_id = child_rate_row['child_smooth_id']
            if not parent_smooth_id is None :
                #
                smooth_row = parent_tables['smooth'][parent_smooth_id]
                smooth_row = copy.copy(smooth_row)
                #
                assert smooth_row['mulstd_value_prior_id'] is None
                assert smooth_row['mulstd_dage_prior_id']  is None
                assert smooth_row['mulstd_dtime_prior_id'] is None
                if rate_name == 'pini' :
                    assert smooth_row['n_age'] == 1
                #
                # update: child_tables['smooth']
                # for case where its is the parent
                child_smooth_id = len(child_tables['smooth'])
                smooth_row['smooth_name'] += f'_{child_smooth_id}'
                child_tables['smooth'].append(smooth_row)
                #
                # change child_tables['rate'] to use the new smoothing
                child_rate_row['child_smooth_id'] = child_smooth_id
                #
                # add rows for this smoothing to child_tables['smooth_grid']
                for parent_grid_row in parent_tables['smooth_grid'] :
                    if parent_grid_row['smooth_id'] == parent_smooth_id :
                        #
                        # update: child_tables['smooth_grid']
                        child_grid_row = copy.copy( parent_grid_row )
                        #
                        for ty in [
                            'value_prior_id', 'dage_prior_id', 'dtime_prior_id'
                         ] :
                            prior_id  = parent_grid_row[ty]
                            if prior_id is None :
                                child_grid_row[ty] = None
                            else :
                                prior_row = parent_tables['prior'][prior_id]
                                prior_row = copy.copy(prior_row)
                                prior_id  = len( child_tables['prior'] )
                                child_tables['prior'].append( prior_row )
                                add_index_to_name(
                                    child_tables['prior'], 'prior_name'
                                )
                                child_grid_row[ty] = prior_id
                        child_grid_row['smooth_id']      = child_smooth_id
                        child_tables['smooth_grid'].append( child_grid_row )
        #
        # child_tables['c_avgint']
        for row in child_tables['c_avgint'] :
            row['node_id'] = child_node_id
        #
        # replace child_tables
        for name in child_tables :
            dismod_at.replace_table(
                child_connection, name, child_tables[name]
            )
        #
        # move c_avgint -> avgint
        move_table(child_connection, 'c_avgint', 'avgint')
        #
        # child_connection
        child_connection.close()
