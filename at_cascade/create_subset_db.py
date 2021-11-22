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
{xsrst_begin create_subset_db}
{xsrst_spell
    var
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

fit_node_database
********************
is a python string containing the name of a dismod_at database.
This is a :ref:`glossary.fit_node_database` which
has two predict tables (mentioned below).
These tables are used to create priors in the child node databases.
This argument can't be ``None``.

parent_node
===========
We use *parent_node* to refer to the parent node in the
dismod_at option table in the *fit_node_database*.

sample Table
============
The sample table contains
the results of a dismod_at sample command for both the fixed and random effects.

c_subset_avgint Table
=====================
This is the :ref:`avgint_parent_grid` table corresponding
to this fit_node_database.

c_subset_predict_sample Table
=============================
This table contains the predict table corresponding to a
predict sample command using the c_subset_avgint table.
Note that the predict_id column name was changed to c_subset_predict_sample_id
(which is not the same as sample_id).

c_subset_predict_fit_var Table
==============================
This table contains the predict table corresponding to a
predict fit_var command using the c_subset_avgint table.
Note that the predict_id column name was changed to c_subset_predict_fit_var_id
(which is not the same as var_id).

c_root_avgint Table
===================
The c_root_avgint table contains the original version of the
:ref:`glossary.root_node_database` avgint table
that predicts for the parent node.
Only the node_id column has been modified from the root_node_database version.

subset_databases
********************
is a python dictionary and if *subset_name* is a key for *subset_databases*,
*subset_name* is a :ref:`glossary.node_name` and a child of the *parent_node*.

-   For each *subset_name*, *subset_databases[subset_name]* is the name of
    a :ref:`glossary.input_node_database` that is created by this command.
-   In this database, *subset_name* will be the :ref:`glossary.fit_node` .
-   If the upper and lower limits are equal,
    the value priors are effectively the same.
    Otherwise the mean and standard deviation in the values priors
    are replaced using the predict, in the *fit_node_database*,
    for the child node. Note that if the value prior is uniform,
    the standard deviation is not used and the mean is only used to
    initialize the optimization.
-   The avgint table is a copy of the c_root_avgint table in the
    *fit_node_database* with the node_id replaced by the corresponding
    child node id.

This argument can't be ``None``.

{xsrst_end create_subset_db}
'''
# ----------------------------------------------------------------------------
import math
import copy
import shutil
import statistics
import dismod_at
import at_cascade
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
# The smoothing for the new subset_table['smooth_grid'] row is the most
# recent smoothing added to subset_table['smooth']; i.e., its smoothing_id
# is len( subset_table['smooth'] ) - 1.
def add_subset_grid_row(
    parent_fit_var,
    parent_sample,
    parent_table,
    subset_table,
    parent_grid_row,
    integrand_id,
    subset_node_id,
    child_prior_std_factor,
) :
    # -----------------------------------------------------------------------
    # value_prior
    # -----------------------------------------------------------------------
    #
    # parent_prior_id
    parent_prior_id    = parent_grid_row['value_prior_id']
    #
    # subset_const_value
    # subset_value_prior_id
    subset_const_value     = parent_grid_row['const_value']
    subset_value_prior_id  = None
    if subset_const_value is None :
        #
        # parent_prior_row
        parent_prior_row = parent_table['prior'][parent_prior_id]
        #
        # subset_const_value
        # subset_value_prior_id
        lower = parent_prior_row['lower']
        upper = parent_prior_row['upper']
        if lower is None :
            lower = - math.inf
        if upper is None :
            upper = + math.inf
        if lower == upper :
            subset_const_value  = lower
            assert subset_value_prior_id is None
        else :
            assert subset_const_value is None
            subset_value_prior_id  = len( subset_table['prior'] )
            #
            # subset_prior_row
            subset_prior_row = copy.copy( parent_prior_row )
            #
            # key
            age_id    = parent_grid_row['age_id']
            time_id   = parent_grid_row['time_id']
            key       = (integrand_id, subset_node_id, age_id, time_id)
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
            # subset_prior_row
            subset_prior_row['mean']        = mean
            subset_prior_row['std']         = child_prior_std_factor * std
            #
            # subset_table['prior']
            subset_table['prior'].append( subset_prior_row )
            add_index_to_name( subset_table['prior'], 'prior_name' )
    # -----------------------------------------------------------------------
    # dage_prior
    # -----------------------------------------------------------------------
    parent_prior_id       = parent_grid_row['dage_prior_id']
    if parent_prior_id == None :
        subset_dage_prior_id= None
    else :
        parent_prior_row      = parent_table['prior'][parent_prior_id]
        subset_prior_row      = copy.copy( parent_prior_row )
        subset_dage_prior_id  = len( subset_table['prior'] )
        subset_table['prior'].append( subset_prior_row )
        add_index_to_name( subset_table['prior'], 'prior_name' )
    # -----------------------------------------------------------------------
    # dtime_prior
    # -----------------------------------------------------------------------
    parent_prior_id       = parent_grid_row['dtime_prior_id']
    if parent_prior_id == None :
        subset_dtime_prior_id= None
    else :
        parent_prior_row       = parent_table['prior'][parent_prior_id]
        subset_prior_row       = copy.copy( parent_prior_row )
        subset_dtime_prior_id  = len( subset_table['prior'] )
        subset_table['prior'].append( subset_prior_row )
        add_index_to_name( subset_table['prior'], 'prior_name' )
    # -----------------------------------------------------------------------
    # subset_grid_row
    subset_grid_row = copy.copy( parent_grid_row )
    subset_grid_row['value_prior_id']  = subset_value_prior_id
    subset_grid_row['const_value']     = subset_const_value
    subset_grid_row['dage_prior_id']   = subset_dage_prior_id
    subset_grid_row['dtime_prior_id']  = subset_dtime_prior_id
    #
    # subset_table['smooth_grid']
    subset_grid_row['smooth_id']  = len( subset_table['smooth'] ) - 1
    subset_table['smooth_grid'].append( subset_grid_row )
# ----------------------------------------------------------------------------
def create_subset_db(
# BEGIN syntax
# at_cascade.create_subset_db(
    all_node_database    = None ,
    fit_node_database    = None ,
    subset_databases     = None ,
# )
# END syntax
) :
    # ------------------------------------------------------------------------
    # all_option_table, all_cov_reference_table
    new        = False
    connection = dismod_at.create_connection(all_node_database, new)
    all_option_table = dismod_at.get_table_dict( connection, 'all_option')
    all_cov_reference_table = dismod_at.get_table_dict(
        connection, 'all_cov_reference'
    )
    split_reference_table = dismod_at.get_table_dict(
        connection, 'split_reference'
    )
    connection.close()
    #
    # child_prior_std_factor
    child_prior_std_factor = 1.0
    for row in all_option_table :
        if row['option_name'] == 'child_prior_std_factor' :
            child_prior_std_factor = float( row['option_value'] )
    #
    # parent_table
    new           = False
    connection    = dismod_at.create_connection(fit_node_database, new)
    parent_table  = dict()
    for name in [
        'c_subset_avgint',
        'c_root_avgint',
        'c_subset_predict_fit_var',
        'c_subset_predict_sample',
        'covariate',
        'density',
        'fit_var',
        'integrand',
        'mulcov',
        'node',
        'option',
        'prior',
        'rate',
        'sample',
        'smooth',
        'smooth_grid',
        'var',
    ] :
        parent_table[name] = dismod_at.get_table_dict(connection, name)
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
    # fit_split_reference_id
    cov_info = at_cascade.get_cov_info(
        all_option_table, parent_table['covariate'], split_reference_table
    )
    if len(split_reference_table) == 0 :
        fit_split_reference_id = None
    else :
        fit_split_reference_id = cov_info['split_reference_id']
    #
    #
    # parent_fit_var
    parent_fit_var = dict()
    for predict_row in parent_table['c_subset_predict_fit_var'] :
        avgint_id          = predict_row['avgint_id']
        avgint_row         = parent_table['c_subset_avgint'][avgint_id]
        integrand_id       = avgint_row['integrand_id']
        node_id            = avgint_row['node_id']
        age_id             = avgint_row['c_age_id']
        time_id            = avgint_row['c_time_id']
        split_reference_id = avgint_row['c_split_reference_id']
        if split_reference_id == fit_split_reference_id :
            key  = (integrand_id, node_id, age_id, time_id)
            assert not key in parent_fit_var
            parent_fit_var[key] = predict_row['avg_integrand']
    #
    # parent_sample
    parent_sample = dict()
    for predict_row in parent_table['c_subset_predict_sample'] :
        avgint_id          = predict_row['avgint_id']
        avgint_row         = parent_table['c_subset_avgint'][avgint_id]
        integrand_id       = avgint_row['integrand_id']
        node_id            = avgint_row['node_id']
        age_id             = avgint_row['c_age_id']
        time_id            = avgint_row['c_time_id']
        split_reference_id = avgint_row['c_split_reference_id']
        if split_reference_id == fit_split_reference_id :
            key  = (integrand_id, node_id, age_id, time_id)
            if not key in parent_sample :
                parent_sample[key] = list()
            parent_sample[key].append( predict_row['avg_integrand'] )
    #
    # parent_node_name
    parent_node_name = None
    for row in parent_table['option'] :
        assert row['option_name'] != 'parent_node_id'
        if row['option_name'] == 'parent_node_name' :
            parent_node_name = row['option_value']
    assert parent_node_name is not None
    #
    # parent_node_id
    parent_node_id = at_cascade.table_name2id(
        parent_table['node'], 'node', parent_node_name
    )
    for subset_name in subset_databases :
        # ---------------------------------------------------------------------
        # create subset_databases[subset_name]
        # ---------------------------------------------------------------------
        #
        # subset_table
        subset_table = dict()
        for name in [
            'c_root_avgint',
            'covariate',
            'mulcov',
            'option',
            'rate',
        ] :
            subset_table[name] = copy.deepcopy(parent_table[name])
        subset_table['prior']       = list()
        subset_table['smooth']      = list()
        subset_table['smooth_grid'] = list()
        subset_table['nslist']      = list()
        subset_table['nslist_pair'] = list()
        #
        # subset_node_id
        subset_node_id  = at_cascade.table_name2id(
            parent_table['node'], 'node', subset_name
        )
        assert parent_table['node'][subset_node_id]['parent'] == parent_node_id
        #
        # subset_database     = fit_node_database
        subset_database= subset_databases[subset_name]
        shutil.copyfile(fit_node_database, subset_database)
        #
        # subset_table['option']
        for row in subset_table['option'] :
            if row['option_name'] == 'parent_node_name' :
                row['option_value'] = subset_name
        #
        # subset_table['covariate']
        for row in all_cov_reference_table :
            # Use fact that None == None is true
            if row['node_id'] == subset_node_id and \
                row['split_reference_id'] == split_reference_id :
                covariate_id  = row['covariate_id']
                subset_row    =subset_table['covariate'][covariate_id]
                subset_row['reference'] = row['reference']
        #
        # --------------------------------------------------------------------
        # subset_table['mulcov']
        # and corresponding entries in
        # smooth, smooth_grid, and prior
        for (mulcov_id, subset_mulcov_row) in enumerate(subset_table['mulcov']) :
            assert subset_mulcov_row['subgroup_smooth_id'] is None
            #
            # parent_smooth_id
            parent_smooth_id = subset_mulcov_row['group_smooth_id']
            if not parent_smooth_id is None :
                #
                # integrand_id
                name         = 'mulcov_' + str(mulcov_id)
                integrand_id = at_cascade.table_name2id(
                    parent_table['integrand'], 'integrand', name
                )
                #
                # smooth_row
                smooth_row = parent_table['smooth'][parent_smooth_id]
                smooth_row = copy.copy(smooth_row)
                assert smooth_row['mulstd_value_prior_id'] is None
                assert smooth_row['mulstd_dage_prior_id']  is None
                assert smooth_row['mulstd_dtime_prior_id'] is None
                #
                # subset_table['smooth'], subset_smooth_id
                subset_smooth_id = len(subset_table['smooth'])
                smooth_row['smooth_name'] += f'_{subset_smooth_id}'
                subset_table['smooth'].append(smooth_row)
                #
                # change subset_table['mulcov'] to use the new smoothing
                subset_mulcov_row['group_smooth_id'] = subset_smooth_id
                #
                # subset_table['smooth_grid']
                # add rows for this smoothing
                node_id = None
                for parent_grid_row in parent_table['smooth_grid'] :
                    if parent_grid_row['smooth_id'] == parent_smooth_id :
                        add_subset_grid_row(
                            parent_fit_var,
                            parent_sample,
                            parent_table,
                            subset_table,
                            parent_grid_row,
                            integrand_id,
                            node_id,
                            child_prior_std_factor,
                        )

        # --------------------------------------------------------------------
        # subset_table['rate']
        # and corresponding entries in the following child tables:
        # smooth, smooth_grid, and prior
        for subset_rate_row in subset_table['rate'] :
            # rate_name
            rate_name        = subset_rate_row['rate_name']
            # ----------------------------------------------------------------
            # parent_smooth_id
            parent_smooth_id = None
            if rate_name in name_rate2integrand :
                assert subset_rate_row['child_nslist_id'] is None
                parent_smooth_id = subset_rate_row['parent_smooth_id']
            else :
                # proper priors for omega are set by omega_constraint routine
                assert rate_name == 'omega'
                subset_rate_row['parent_smooth_id'] = None
                subset_rate_row['child_smooth_id']  = None
                subset_rate_row['child_nslist_id']  = None
            if not parent_smooth_id is None :
                #
                # integrand_id
                # only check for integrands that are used
                integrand_name  = name_rate2integrand[rate_name]
                integrand_id = at_cascade.table_name2id(
                    parent_table['integrand'], 'integrand', integrand_name
                )
                #
                # smooth_row
                smooth_row = parent_table['smooth'][parent_smooth_id]
                smooth_row = copy.copy(smooth_row)
                assert smooth_row['mulstd_value_prior_id'] is None
                assert smooth_row['mulstd_dage_prior_id']  is None
                assert smooth_row['mulstd_dtime_prior_id'] is None
                #
                # : subset_table['smooth'], subset_smooth_id
                subset_smooth_id = len(subset_table['smooth'])
                smooth_row['smooth_name'] += f'_{subset_smooth_id}'
                subset_table['smooth'].append(smooth_row)
                #
                # subset_table['rate']
                # use the new smoothing for this rate
                subset_rate_row['parent_smooth_id'] = subset_smooth_id
                #
                # subset_table['smooth_grid']
                # add rows for this smoothing
                for parent_grid_row in parent_table['smooth_grid'] :
                    if parent_grid_row['smooth_id'] == parent_smooth_id :
                        add_subset_grid_row(
                            parent_fit_var,
                            parent_sample,
                            parent_table,
                            subset_table,
                            parent_grid_row,
                            integrand_id,
                            subset_node_id,
                            child_prior_std_factor,
                        )
            # ----------------------------------------------------------------
            # parent_smooth_id
            parent_smooth_id = None
            if rate_name in name_rate2integrand :
                parent_smooth_id = subset_rate_row['child_smooth_id']
            if not parent_smooth_id is None :
                #
                smooth_row = parent_table['smooth'][parent_smooth_id]
                smooth_row = copy.copy(smooth_row)
                #
                assert smooth_row['mulstd_value_prior_id'] is None
                assert smooth_row['mulstd_dage_prior_id']  is None
                assert smooth_row['mulstd_dtime_prior_id'] is None
                if rate_name == 'pini' :
                    assert smooth_row['n_age'] == 1
                #
                # update: subset_table['smooth']
                # for case where its is the parent
                subset_smooth_id = len(subset_table['smooth'])
                smooth_row['smooth_name'] += f'_{subset_smooth_id}'
                subset_table['smooth'].append(smooth_row)
                #
                # change subset_table['rate'] to use the new smoothing
                subset_rate_row['child_smooth_id'] = subset_smooth_id
                #
                # add rows for this smoothing to subset_table['smooth_grid']
                for parent_grid_row in parent_table['smooth_grid'] :
                    if parent_grid_row['smooth_id'] == parent_smooth_id :
                        #
                        # update: subset_table['smooth_grid']
                        subset_grid_row = copy.copy( parent_grid_row )
                        #
                        for ty in [
                            'value_prior_id', 'dage_prior_id', 'dtime_prior_id'
                         ] :
                            prior_id  = parent_grid_row[ty]
                            if prior_id is None :
                                subset_grid_row[ty] = None
                            else :
                                prior_row = parent_table['prior'][prior_id]
                                prior_row = copy.copy(prior_row)
                                prior_id  = len( subset_table['prior'] )
                                subset_table['prior'].append( prior_row )
                                add_index_to_name(
                                    subset_table['prior'], 'prior_name'
                                )
                                subset_grid_row[ty] = prior_id
                        subset_grid_row['smooth_id']      = subset_smooth_id
                        subset_table['smooth_grid'].append( subset_grid_row )
        #
        # subset_table['c_root_avgint']
        for row in subset_table['c_root_avgint'] :
            row['node_id'] = subset_node_id
        #
        # subset_connection
        new        = False
        subset_connection = dismod_at.create_connection(subset_database, new)
        #
        # replace subset_table
        for name in subset_table :
            dismod_at.replace_table(
                subset_connection, name, subset_table[name]
            )
        # move c_root_avgint -> avgint
        move_table(subset_connection, 'c_root_avgint', 'avgint')
        #
        # drop the following tables:
        # c_subset_avgint, c_subset_predict_sample, c_subset_predict_fit_var
        command  = 'DROP TABLE c_subset_avgint'
        dismod_at.sql_command(subset_connection, command)
        command  = 'DROP TABLE c_subset_predict_sample'
        dismod_at.sql_command(subset_connection, command)
        command  = 'DROP TABLE c_subset_predict_fit_var'
        dismod_at.sql_command(subset_connection, command)
        #
        # subset_connection
        subset_connection.close()
