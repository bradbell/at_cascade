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
{xsrst_begin create_shift_db}
{xsrst_spell
    var
}

Create Database With Shifted Covariate References
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
*****************
is a python string containing the name of a dismod_at database.
This is a :ref:`glossary.fit_node_database` which
has two predict tables (mentioned below).
These tables are used to create priors in the child node databases.
This argument can't be ``None``.

fit_node
========
We use *fit_node* to refer to the parent node in the
dismod_at option table in the *fit_node_database*.

sample Table
============
The sample table contains
the results of a dismod_at sample command for both the fixed and random effects.

c_shift_avgint Table
====================
This is the :ref:`avgint_parent_grid` table corresponding
to this fit_node_database.

c_shift_predict_sample Table
============================
This table contains the predict table corresponding to a
predict sample command using the c_shift_avgint table.
Note that the predict_id column name was changed to c_shift_predict_sample_id
(which is not the same as sample_id).

c_shift_predict_fit_var Table
=============================
This table contains the predict table corresponding to a
predict fit_var command using the c_shift_avgint table.
Note that the predict_id column name was changed to c_shift_predict_fit_var_id
(which is not the same as var_id).

c_root_avgint Table
===================
The c_root_avgint table contains the original version of the
:ref:`glossary.root_node_database` avgint table
that predicts for the parent node.
Only the node_id column has been modified from the root_node_database version.

shift_databases
***************
is a python dictionary, we use the notation *shift_name* for the
keys in this database ``dict``.
If *shift_name* is a :ref:`split_reference_table.split_reference_name`,
the node is the *fit_node*.

-   For each *shift_name*, *shift_databases[shift_name]* is the name of
    a :ref:`glossary.input_node_database` that is created by this command.
-   If *shift_name* is a :ref:`split_reference_table.split_reference_name`,
    the node corresponding to this shift database is the fit_node.
    Otherwise *shift_name* is a child node of the fit_name
    and is the node corresponding to this shift database.
-   If the upper and lower limits are equal,
    the value priors are effectively the same.
    Otherwise the mean and standard deviation in the values priors
    are replaced using the predict, in the *fit_node_database*,
    that corresponds to this shift database.
    Note that if the value prior is uniform,
    the standard deviation is not used and the mean is only used to
    initialize the optimization.
-   The avgint table is a copy of the c_root_avgint table in the
    *fit_node_database* with the node_id replaced by the corresponding
    shift node id.

This argument can't be ``None``.

{xsrst_end create_shift_db}
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
# The smoothing for the new shift_table['smooth_grid'] row is the most
# recent smoothing added to shift_table['smooth']; i.e., its smoothing_id
# is len( shift_table['smooth'] ) - 1.
def add_shift_grid_row(
    fit_fit_var,
    fit_sample,
    fit_table,
    shift_table,
    fit_grid_row,
    integrand_id,
    shift_node_id,
    child_prior_std_factor,
) :
    # -----------------------------------------------------------------------
    # value_prior
    # -----------------------------------------------------------------------
    #
    # fit_prior_id
    fit_prior_id    = fit_grid_row['value_prior_id']
    #
    # shift_const_value
    # shift_value_prior_id
    shift_const_value     = fit_grid_row['const_value']
    shift_value_prior_id  = None
    if shift_const_value is None :
        #
        # fit_prior_row
        fit_prior_row = fit_table['prior'][fit_prior_id]
        #
        # shift_const_value
        # shift_value_prior_id
        lower = fit_prior_row['lower']
        upper = fit_prior_row['upper']
        if lower is None :
            lower = - math.inf
        if upper is None :
            upper = + math.inf
        if lower == upper :
            shift_const_value  = lower
            assert shift_value_prior_id is None
        else :
            assert shift_const_value is None
            shift_value_prior_id  = len( shift_table['prior'] )
            #
            # shift_prior_row
            shift_prior_row = copy.copy( fit_prior_row )
            #
            # key
            age_id    = fit_grid_row['age_id']
            time_id   = fit_grid_row['time_id']
            key       = (integrand_id, shift_node_id, age_id, time_id)
            #
            # mean
            mean = fit_fit_var[key]
            #
            # std
            eta        = fit_prior_row['eta']
            if eta is None :
                std  = statistics.stdev(fit_sample[key], xbar=mean)
            else:
                # The asymptotic statistics were computed in log space
                # and then transformed to original space.
                #
                # log_sample
                log_sample = list()
                for sample in fit_sample[key] :
                    log_sample.append( math.log( sample + eta ) )
                #
                # log_std
                log_mean = math.log(mean + eta)
                log_std  = statistics.stdev(log_sample, xbar = log_mean)
                #
                # inverse log transformation
                std      = (math.exp(log_std) - 1) * (mean + eta)
            #
            # shift_prior_row
            shift_prior_row['mean']        = mean
            shift_prior_row['std']         = child_prior_std_factor * std
            #
            # shift_table['prior']
            shift_table['prior'].append( shift_prior_row )
            add_index_to_name( shift_table['prior'], 'prior_name' )
    # -----------------------------------------------------------------------
    # dage_prior
    # -----------------------------------------------------------------------
    fit_prior_id       = fit_grid_row['dage_prior_id']
    if fit_prior_id == None :
        shift_dage_prior_id= None
    else :
        fit_prior_row      = fit_table['prior'][fit_prior_id]
        shift_prior_row      = copy.copy( fit_prior_row )
        shift_dage_prior_id  = len( shift_table['prior'] )
        shift_table['prior'].append( shift_prior_row )
        add_index_to_name( shift_table['prior'], 'prior_name' )
    # -----------------------------------------------------------------------
    # dtime_prior
    # -----------------------------------------------------------------------
    fit_prior_id       = fit_grid_row['dtime_prior_id']
    if fit_prior_id == None :
        shift_dtime_prior_id= None
    else :
        fit_prior_row       = fit_table['prior'][fit_prior_id]
        shift_prior_row       = copy.copy( fit_prior_row )
        shift_dtime_prior_id  = len( shift_table['prior'] )
        shift_table['prior'].append( shift_prior_row )
        add_index_to_name( shift_table['prior'], 'prior_name' )
    # -----------------------------------------------------------------------
    # shift_grid_row
    shift_grid_row = copy.copy( fit_grid_row )
    shift_grid_row['value_prior_id']  = shift_value_prior_id
    shift_grid_row['const_value']     = shift_const_value
    shift_grid_row['dage_prior_id']   = shift_dage_prior_id
    shift_grid_row['dtime_prior_id']  = shift_dtime_prior_id
    #
    # shift_table['smooth_grid']
    shift_grid_row['smooth_id']  = len( shift_table['smooth'] ) - 1
    shift_table['smooth_grid'].append( shift_grid_row )
# ----------------------------------------------------------------------------
def create_shift_db(
# BEGIN syntax
# at_cascade.create_shift_db(
    all_node_database    = None ,
    fit_node_database    = None ,
    shift_databases     = None ,
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
    # fit_table
    new           = False
    connection    = dismod_at.create_connection(fit_node_database, new)
    fit_table  = dict()
    for name in [
        'c_shift_avgint',
        'c_root_avgint',
        'c_shift_predict_fit_var',
        'c_shift_predict_sample',
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
        fit_table[name] = dismod_at.get_table_dict(connection, name)
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
    # fit_split_reference_id, split_covariate_id
    cov_info = at_cascade.get_cov_info(
        all_option_table, fit_table['covariate'], split_reference_table
    )
    if len(split_reference_table) == 0 :
        fit_split_reference_id = None
        split_covaraite_id     = None
    else :
        fit_split_reference_id = cov_info['split_reference_id']
        split_covariate_id     = cov_info['split_covariate_id']
    #
    #
    # fit_fit_var
    fit_fit_var = dict()
    for predict_row in fit_table['c_shift_predict_fit_var'] :
        avgint_id          = predict_row['avgint_id']
        avgint_row         = fit_table['c_shift_avgint'][avgint_id]
        integrand_id       = avgint_row['integrand_id']
        node_id            = avgint_row['node_id']
        age_id             = avgint_row['c_age_id']
        time_id            = avgint_row['c_time_id']
        split_reference_id = avgint_row['c_split_reference_id']
        if split_reference_id == fit_split_reference_id :
            key  = (integrand_id, node_id, age_id, time_id)
            assert not key in fit_fit_var
            fit_fit_var[key] = predict_row['avg_integrand']
    #
    # fit_sample
    fit_sample = dict()
    for predict_row in fit_table['c_shift_predict_sample'] :
        avgint_id          = predict_row['avgint_id']
        avgint_row         = fit_table['c_shift_avgint'][avgint_id]
        integrand_id       = avgint_row['integrand_id']
        node_id            = avgint_row['node_id']
        age_id             = avgint_row['c_age_id']
        time_id            = avgint_row['c_time_id']
        split_reference_id = avgint_row['c_split_reference_id']
        if split_reference_id == fit_split_reference_id :
            key  = (integrand_id, node_id, age_id, time_id)
            if not key in fit_sample :
                fit_sample[key] = list()
            fit_sample[key].append( predict_row['avg_integrand'] )
    #
    # fit_node_name
    fit_node_name = None
    for row in fit_table['option'] :
        assert row['option_name'] != 'fit_node_id'
        if row['option_name'] == 'parent_node_name' :
            fit_node_name = row['option_value']
    assert fit_node_name is not None
    #
    # fit_node_id
    fit_node_id = at_cascade.table_name2id(
        fit_table['node'], 'node', fit_node_name
    )
    for shift_name in shift_databases :
        # ---------------------------------------------------------------------
        # create shift_databases[shift_name]
        # ---------------------------------------------------------------------
        #
        # shift_table
        shift_table = dict()
        for name in [
            'c_root_avgint',
            'covariate',
            'mulcov',
            'option',
            'rate',
        ] :
            shift_table[name] = copy.deepcopy(fit_table[name])
        shift_table['prior']       = list()
        shift_table['smooth']      = list()
        shift_table['smooth_grid'] = list()
        shift_table['nslist']      = list()
        shift_table['nslist_pair'] = list()
        #
        # shift_node_name, shift_split_reference_id
        shift_node_name = None
        for (row_id, row) in enumerate(split_reference_table) :
            if row['split_reference_name'] == shift_name :
                shift_node_name          = fit_node_name
                shift_split_reference_id = row_id
        for row in fit_table['node'] :
            if row['node_name'] == shift_name :
                if shift_node_name is not None :
                    msg  = f'{shift_name} is both a split_reference_name '
                    msg += 'and a node_name'
                    assert False, msg
                if row['parent'] != fit_node_id :
                    msg  = f'shift_name = {shift_name} is node name\n'
                    msg += f'and its parent is not the fit node '
                    msg += fit_node_name
                    assert False, msg
                #
                shift_node_name          = shift_name
                shift_split_reference_id = fit_split_reference_id
        #
        # shift_node_id
        shift_node_id  = at_cascade.table_name2id(
            fit_table['node'], 'node', shift_node_name
        )
        #
        # shift_database     = fit_node_database
        shift_database= shift_databases[shift_name]
        shutil.copyfile(fit_node_database, shift_database)
        #
        # shift_table['option']
        # set parent_node_name to shift_node_name
        for row in shift_table['option'] :
            if row['option_name'] == 'parent_node_name' :
                row['option_value'] = shift_node_name
        #
        # shift_table['covariate']
        # set relative covariate values so correspond to shift node
        for row in all_cov_reference_table :
            # use fact that None == None is true
            if row['node_id'] == shift_node_id \
            and row['split_reference_id'] == shift_split_reference_id :
                covariate_id  = row['covariate_id']
                shift_row     = shift_table['covariate'][covariate_id]
                shift_row['reference'] = row['reference']
        #
        # shift_table['covariate']
        # set shift covaraite value
        if shift_split_reference_id is not None :
            split_row  = split_reference_table[shift_split_reference_id]
            reference  = split_row['split_reference_value']
            shift_row  = shift_table['covariate'][split_covariate_id]
            shift_row['reference'] = reference
        #
        # --------------------------------------------------------------------
        # shift_table['mulcov']
        # and corresponding entries in
        # smooth, smooth_grid, and prior
        for (mulcov_id, shift_mulcov_row) in enumerate(shift_table['mulcov']) :
            assert shift_mulcov_row['subgroup_smooth_id'] is None
            #
            # fit_smooth_id
            fit_smooth_id = shift_mulcov_row['group_smooth_id']
            if not fit_smooth_id is None :
                #
                # integrand_id
                name         = 'mulcov_' + str(mulcov_id)
                integrand_id = at_cascade.table_name2id(
                    fit_table['integrand'], 'integrand', name
                )
                #
                # smooth_row
                smooth_row = fit_table['smooth'][fit_smooth_id]
                smooth_row = copy.copy(smooth_row)
                assert smooth_row['mulstd_value_prior_id'] is None
                assert smooth_row['mulstd_dage_prior_id']  is None
                assert smooth_row['mulstd_dtime_prior_id'] is None
                #
                # shift_table['smooth'], shift_smooth_id
                shift_smooth_id = len(shift_table['smooth'])
                smooth_row['smooth_name'] += f'_{shift_smooth_id}'
                shift_table['smooth'].append(smooth_row)
                #
                # change shift_table['mulcov'] to use the new smoothing
                shift_mulcov_row['group_smooth_id'] = shift_smooth_id
                #
                # shift_table['smooth_grid']
                # add rows for this smoothing
                node_id = None
                for fit_grid_row in fit_table['smooth_grid'] :
                    if fit_grid_row['smooth_id'] == fit_smooth_id :
                        add_shift_grid_row(
                            fit_fit_var,
                            fit_sample,
                            fit_table,
                            shift_table,
                            fit_grid_row,
                            integrand_id,
                            node_id,
                            child_prior_std_factor,
                        )

        # --------------------------------------------------------------------
        # shift_table['rate']
        # and corresponding entries in the following child tables:
        # smooth, smooth_grid, and prior
        for shift_rate_row in shift_table['rate'] :
            # rate_name
            rate_name        = shift_rate_row['rate_name']
            # ----------------------------------------------------------------
            # fit_smooth_id
            fit_smooth_id = None
            if rate_name in name_rate2integrand :
                assert shift_rate_row['child_nslist_id'] is None
                fit_smooth_id = shift_rate_row['parent_smooth_id']
            else :
                # proper priors for omega are set by omega_constraint routine
                assert rate_name == 'omega'
                shift_rate_row['parent_smooth_id'] = None
                shift_rate_row['child_smooth_id']  = None
                shift_rate_row['child_nslist_id']  = None
            if not fit_smooth_id is None :
                #
                # integrand_id
                # only check for integrands that are used
                integrand_name  = name_rate2integrand[rate_name]
                integrand_id = at_cascade.table_name2id(
                    fit_table['integrand'], 'integrand', integrand_name
                )
                #
                # smooth_row
                smooth_row = fit_table['smooth'][fit_smooth_id]
                smooth_row = copy.copy(smooth_row)
                assert smooth_row['mulstd_value_prior_id'] is None
                assert smooth_row['mulstd_dage_prior_id']  is None
                assert smooth_row['mulstd_dtime_prior_id'] is None
                #
                # : shift_table['smooth'], shift_smooth_id
                shift_smooth_id = len(shift_table['smooth'])
                smooth_row['smooth_name'] += f'_{shift_smooth_id}'
                shift_table['smooth'].append(smooth_row)
                #
                # shift_table['rate']
                # use the new smoothing for this rate
                shift_rate_row['parent_smooth_id'] = shift_smooth_id
                #
                # shift_table['smooth_grid']
                # add rows for this smoothing
                for fit_grid_row in fit_table['smooth_grid'] :
                    if fit_grid_row['smooth_id'] == fit_smooth_id :
                        add_shift_grid_row(
                            fit_fit_var,
                            fit_sample,
                            fit_table,
                            shift_table,
                            fit_grid_row,
                            integrand_id,
                            shift_node_id,
                            child_prior_std_factor,
                        )
            # ----------------------------------------------------------------
            # fit_smooth_id
            fit_smooth_id = None
            if rate_name in name_rate2integrand :
                fit_smooth_id = shift_rate_row['child_smooth_id']
            if not fit_smooth_id is None :
                #
                smooth_row = fit_table['smooth'][fit_smooth_id]
                smooth_row = copy.copy(smooth_row)
                #
                assert smooth_row['mulstd_value_prior_id'] is None
                assert smooth_row['mulstd_dage_prior_id']  is None
                assert smooth_row['mulstd_dtime_prior_id'] is None
                if rate_name == 'pini' :
                    assert smooth_row['n_age'] == 1
                #
                # update: shift_table['smooth']
                # for case where its is the parent
                shift_smooth_id = len(shift_table['smooth'])
                smooth_row['smooth_name'] += f'_{shift_smooth_id}'
                shift_table['smooth'].append(smooth_row)
                #
                # change shift_table['rate'] to use the new smoothing
                shift_rate_row['child_smooth_id'] = shift_smooth_id
                #
                # add rows for this smoothing to shift_table['smooth_grid']
                for fit_grid_row in fit_table['smooth_grid'] :
                    if fit_grid_row['smooth_id'] == fit_smooth_id :
                        #
                        # update: shift_table['smooth_grid']
                        shift_grid_row = copy.copy( fit_grid_row )
                        #
                        for ty in [
                            'value_prior_id', 'dage_prior_id', 'dtime_prior_id'
                         ] :
                            prior_id  = fit_grid_row[ty]
                            if prior_id is None :
                                shift_grid_row[ty] = None
                            else :
                                prior_row = fit_table['prior'][prior_id]
                                prior_row = copy.copy(prior_row)
                                prior_id  = len( shift_table['prior'] )
                                shift_table['prior'].append( prior_row )
                                add_index_to_name(
                                    shift_table['prior'], 'prior_name'
                                )
                                shift_grid_row[ty] = prior_id
                        shift_grid_row['smooth_id']      = shift_smooth_id
                        shift_table['smooth_grid'].append( shift_grid_row )
        #
        # shift_table['c_root_avgint']
        for row in shift_table['c_root_avgint'] :
            row['node_id'] = shift_node_id
        #
        # shift_connection
        new        = False
        shift_connection = dismod_at.create_connection(shift_database, new)
        #
        # replace shift_table
        for name in shift_table :
            dismod_at.replace_table(
                shift_connection, name, shift_table[name]
            )
        # move c_root_avgint -> avgint
        move_table(shift_connection, 'c_root_avgint', 'avgint')
        #
        # drop the following tables:
        # c_shift_avgint, c_shift_predict_sample, c_shift_predict_fit_var
        command  = 'DROP TABLE c_shift_avgint'
        dismod_at.sql_command(shift_connection, command)
        command  = 'DROP TABLE c_shift_predict_sample'
        dismod_at.sql_command(shift_connection, command)
        command  = 'DROP TABLE c_shift_predict_fit_var'
        dismod_at.sql_command(shift_connection, command)
        #
        # shift_connection
        shift_connection.close()
