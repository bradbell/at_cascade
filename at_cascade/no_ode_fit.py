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
{xsrst_begin no_ode_fit}
{xsrst_spell
    dir
    integrands
}

Do A No Ode Fit For One Node
############################

Under Construction
******************

Syntax
******
{xsrst_file
    # BEGIN syntax
    # END syntax
}

in_database
***********
is a python string specifying the location of a
:ref:`glossary.fit_node_database`
relative to the current working directory.
This argument can't be ``None``.

in_dir
======
is the directory where the *in_database* is located.

fit_node
========
This is the name of the
:ref:`glossary.fit_node` for the *in_database* and *out_database*.

out_database
************
The return value *out_database* is equal to

    *in_dir*\ /\ *fit_node*\ /dismod.db

which can't be the same file name as *in_database*.
This is a fit_node_database similar to *in_database*.
The difference is that the mean value in the priors for the fixed effects
has been replace by the optimal estimate for fitting with the integrands
that do not used the ODE.

{xsrst_end no_ode_fit}
'''
import sys
import os
import shutil
import copy
import dismod_at
import at_cascade
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
def get_var_id(var_table, rate_id, mulcov_id, age_id, time_id) :
    for (var_id, row) in enumerate(var_table) :
        match =  row['rate_id'] == rate_id
        match = match and row['mulcov_id'] == mulcov_id
        match = match and row['age_id'] == age_id
        match = match and row['time_id'] == time_id
        if match :
            return var_id
    assert False
# ----------------------------------------------------------------------------
# The smoothing for the new out_tables['smooth_grid'] row is the most
# recent smoothing added to out_tables['smooth']; i.e., its smoothing_id
# is len( out_tables['smooth'] ) - 1.
def add_out_grid_row(
    rate_id,
    mulcov_id,
    in_tables,
    out_tables,
    in_grid_row,
) :
    # -----------------------------------------------------------------------
    # value_prior
    # -----------------------------------------------------------------------
    #
    # in_prior_id
    in_prior_id    = in_grid_row['value_prior_id']
    #
    # out_const_value
    # out_value_prior_id
    out_const_value    = in_grid_row['const_value']
    out_value_prior_id = None
    if out_const_value is None :
        #
        # in_prior_row
        in_prior_row = in_tables['prior'][in_prior_id]
        #
        # out_const_value
        # out_value_prior_id
        if in_prior_row['lower'] == in_prior_row['upper'] :
            out_const_value = in_prior_row['lower']
            assert out_value_prior_id is None
        else :
            assert out_const_value is None
            out_value_prior_id = len( out_tables['prior'] )
            #
            # out_prior_row
            out_prior_row  = copy.copy( in_prior_row )
            #
            # var_id
            age_id    = in_grid_row['age_id']
            time_id   = in_grid_row['time_id']
            var_table = out_tables['var']
            var_id    = get_var_id(
                var_table, rate_id, mulcov_id, age_id, time_id
            )
            #
            # out_prior_row['mean']
            fit_var_row           = out_tables['fit_var'][var_id]
            fit_var_value         = fit_var_row['fit_var_value']
            out_prior_row['mean'] = fit_var_value
            #
            # out_tables['prior']
            out_tables['prior'].append( out_prior_row )
            add_index_to_name( out_tables['prior'], 'prior_name' )
    # -----------------------------------------------------------------------
    # dage_prior
    # -----------------------------------------------------------------------
    in_prior_id       = in_grid_row['dage_prior_id']
    if in_prior_id == None :
        out_dage_prior_id = None
    else :
        in_prior_row      = in_tables['prior'][in_prior_id]
        out_prior_row       = copy.copy( in_prior_row )
        out_dage_prior_id   = len( out_tables['prior'] )
        out_tables['prior'].append( out_prior_row )
        add_index_to_name( out_tables['prior'], 'prior_name' )
    # -----------------------------------------------------------------------
    # dtime_prior
    # -----------------------------------------------------------------------
    in_prior_id       = in_grid_row['dtime_prior_id']
    if in_prior_id == None :
        out_dtime_prior_id = None
    else :
        in_prior_row       = in_tables['prior'][in_prior_id]
        out_prior_row        = copy.copy( in_prior_row )
        out_dtime_prior_id   = len( out_tables['prior'] )
        out_tables['prior'].append( out_prior_row )
        add_index_to_name( out_tables['prior'], 'prior_name' )
    # -----------------------------------------------------------------------
    # out_grid_row
    out_grid_row = copy.copy( in_grid_row )
    out_grid_row['value_prior_id']  = out_value_prior_id
    out_grid_row['const_value']     = out_const_value
    out_grid_row['dage_prior_id']   = out_dage_prior_id
    out_grid_row['dtime_prior_id']  = out_dtime_prior_id
    #
    # out_tables['smooth_grid']
    out_grid_row['smooth_id']  = len( out_tables['smooth'] ) - 1
    out_tables['smooth_grid'].append( out_grid_row )
# ----------------------------------------------------------------------------
def no_ode_fit(
# BEGIN syntax
# out_database = at_cascade.no_ode_fit(
    in_database = None,
# )
# END syntax
) :
    #
    # in_tables
    new        = False
    connection = dismod_at.create_connection(in_database, new)
    in_tables = dict()
    for name in [
        'integrand',
        'mulcov',
        'option',
        'prior',
        'rate',
        'smooth',
        'smooth_grid'
    ] :
        in_tables[name] = dismod_at.get_table_dict(connection, name)
    connection.close()
    #
    # fit_node
    fit_node = at_cascade.get_parent_node(in_database)
    #
    # out_database
    index = in_database.rfind('/')
    if 0 <= index :
        in_dir       = in_database[: index]
        out_database = f'{in_dir}/{fit_node}/dismod.db'
    else :
        out_database = f'{fit_node}/dismod.db'
    #
    msg   = f'in_database and out_database are equal'
    assert not in_database == out_database, msg
    #
    # copy in_database to out_database
    shutil.copyfile(in_database, out_database)
    #
    # hold_out_integrand
    hold_out_integrand = list()
    use_ode = [
        'prevalence', 'Tincidence', 'mtspecific', 'mtall', 'mtstandard'
    ]
    for row in in_tables['integrand'] :
        integrand_name = row['integrand_name']
        if integrand_name in use_ode :
            hold_out_integrand.append( integrand_name )
    name  = 'hold_out_integrand'
    value = ' '.join(hold_out_integrand)
    dismod_at.system_command_prc(
        [ 'dismod_at', out_database, 'set', 'option', name, value ]
    )
    #
    # init
    dismod_at.system_command_prc([ 'dismod_at', out_database, 'init' ])
    #
    # fit both
    dismod_at.system_command_prc([ 'dismod_at', out_database, 'fit', 'both' ])
    #
    # out_connection
    new            = False
    out_connection = dismod_at.create_connection(out_database, new)
    #
    # out_tables
    out_tables = dict()
    for name in [
        'fit_var',
        'var',
    ] :
        out_tables[name] = dismod_at.get_table_dict(out_connection, name)
    for name in [
        'prior',
        'mulcov',
        'rate',
        'smooth',
        'smooth_grid',
    ] :
        out_tables[name] = list()
    # ------------------------------------------------------------------------
    # out_tables['mulcov']
    # and the corresponding entries in smooth, smooth_grid, and prior tables
    for (mulcov_id, in_mulcov_row) in enumerate( in_tables['mulcov'] ) :
        #
        # in_smooth_id
        assert in_mulcov_row['subgroup_smooth_id'] is None
        in_smooth_id = in_mulcov_row['group_smooth_id']
        #
        # out_mulcov_row
        out_mulcov_row = copy.copy( in_mulcov_row )
        #
        if not in_smooth_id is None :
            #
            # smooth_row
            smooth_row = in_tables['smooth'][in_smooth_id]
            smooth_row = copy.copy(smooth_row)
            assert smooth_row['mulstd_value_prior_id'] is None
            assert smooth_row['mulstd_dage_prior_id']  is None
            assert smooth_row['mulstd_dtime_prior_id'] is None
            #
            # out_tables['smooth']
            # out_smooth_id
            out_smooth_id = len(out_tables['smooth'])
            smooth_row['smooth_name'] += f'_{out_smooth_id}'
            out_tables['smooth'].append(smooth_row)
            #
            # out_mulcov_row
            out_mulcov_row['group_smooth_id'] = out_smooth_id
            #
            # out_tables['smooth_grid']
            rate_id = in_mulcov_row['rate_id']
            for in_grid_row in in_tables['smooth_grid'] :
                if in_grid_row['smooth_id'] == in_smooth_id :
                    add_out_grid_row(
                        rate_id,
                        mulcov_id,
                        in_tables,
                        out_tables,
                        in_grid_row
                    )
        #
        # out_tables['mulcov_row']
        out_tables['mulcov'].append( out_mulcov_row )
    # ------------------------------------------------------------------------
    # out_tables['rate']
    # and the corresponding entries in smooth, smooth_grid, and prior tables
    for (rate_id, in_rate_row) in enumerate(in_tables['rate']) :
        #
        # in_smooth_id
        assert in_rate_row['child_nslist_id'] is None
        in_smooth_id = in_rate_row['parent_smooth_id']
        #
        # out_rate_row
        out_rate_row = copy.copy( in_rate_row )
        #
        if not in_smooth_id is None :
            #
            # smooth_row
            smooth_row = in_tables['smooth'][in_smooth_id]
            smooth_row = copy.copy(smooth_row)
            assert smooth_row['mulstd_value_prior_id'] is None
            assert smooth_row['mulstd_dage_prior_id']  is None
            assert smooth_row['mulstd_dtime_prior_id'] is None
            #
            # out_tables['smooth']
            # out_smooth_id
            out_smooth_id = len(out_tables['smooth'])
            smooth_row['smooth_name'] += f'_{out_smooth_id}'
            out_tables['smooth'].append(smooth_row)
            #
            # out_rate_row
            out_rate_row['parent_smooth_id'] = out_smooth_id
            #
            # out_tables['smooth_grid']
            mulcov_id = None
            for in_grid_row in in_tables['smooth_grid'] :
                if in_grid_row['smooth_id'] == in_smooth_id :
                    add_out_grid_row(
                        rate_id,
                        mulcov_id,
                        in_tables,
                        out_tables,
                        in_grid_row
                    )
        #
        # out_tables['rate_row']
        out_tables['rate'].append( out_rate_row )
        #
        # in_smooth_id
        in_smooth_id = in_rate_row['child_smooth_id']
        if not in_smooth_id is None :
            #
            # smooth_row
            smooth_row = in_tables['smooth'][in_smooth_id]
            smooth_row = copy.copy(smooth_row)
            assert smooth_row['mulstd_value_prior_id'] is None
            assert smooth_row['mulstd_dage_prior_id']  is None
            assert smooth_row['mulstd_dtime_prior_id'] is None
            #
            # out_tables['smooth']
            # out_smooth_id
            out_smooth_id = len(out_tables['smooth'])
            smooth_row['smooth_name'] += f'_{out_smooth_id}'
            out_tables['smooth'].append(smooth_row)
            #
            # out_rate_row
            out_rate_row['child_smooth_id'] = out_smooth_id
            #
            # out_tables['smooth_grid']
            for in_grid_row in in_tables['smooth_grid'] :
                if in_grid_row['smooth_id'] == in_smooth_id :
                    #
                    # out_grid_row
                    out_grid_row = copy.copy( in_grid_row )
                    for ty in [
                        'value_prior_id', 'dage_prior_id', 'dtime_prior_id'
                    ] :
                        prior_id = in_grid_row[ty]
                        if not prior_id is None :
                            prior_row = in_tables['prior'][prior_id]
                            prior_row = copy.copy( prior_row )
                            prior_id  = len( out_tables['prior'] )
                            out_tables['prior'].append( prior_row )
                            add_index_to_name(
                                out_tables['prior'], 'prior_name'
                            )
                            out_grid_row[ty] = prior_id
                    out_grid_row['smooth_id'] = out_smooth_id
                    out_tables['smooth_grid'].append( out_grid_row )
    #
    # replace out_tables
    for name in out_tables :
        if name not in [ 'var', 'fit_var' ] :
            dismod_at.replace_table(out_connection, name, out_tables[name])
    #
    # restore hold_out_integrand
    hold_out_integrand = ''
    for row in in_tables['option'] :
        if row['option_name'] == 'hold_out_integrand' :
            hold_out_integrand = row['option_value']
    name  = 'hold_out_integrand'
    value = hold_out_integrand
    dismod_at.system_command_prc(
        [ 'dismod_at', out_database, 'set', 'option', name, value ]
    )
    #
    # out_connection
    out_connection.close()
    #
    return out_database
