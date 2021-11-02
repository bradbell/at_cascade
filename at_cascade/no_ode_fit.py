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
    csv
}

Do A No Ode Fit For One Node
############################

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

max_fit
*******
is an ``int`` containing the value of :ref:`all_option_table.max_fit` in the
all option table.
If max_fit does not appear in the all option table,
*max_fit* should be None.

max_abs_effect
**************
is a ``float`` containing the value of :ref:`all_option_table.max_abs_effect`
in the all option table.
If max_abs_effect does not appear in the all option table,
*max_abs_effect* should be None.

trace_fit
*********
if ``True``, ( ``False`` ) the progress of the dismod at fit command
will be printed on standard output during the optimization.

no_ode_database
***************
An intermediate database is stored in the file

    *in_dir*\ /\ *fit_node*\ /no_ode.db

This contains the results of the no ODE fit so they
can be plotted and converted to csv files.

out_database
************
The return value *out_database* is equal to

    *in_dir*\ /\ *fit_node*\ /dismod.db

which can't be the same file name as *in_database*.
This is a fit_node_database similar to *in_database*.
The difference is that the mean value in the priors for the fixed effects
have been replace by the optimal estimate for fitting with the integrands
that do not used the ODE.
The last operation on this table is a dismod_at init command.

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
# The smoothing for the new out_table['smooth_grid'] row is the most
# recent smoothing added to out_table['smooth']; i.e., its smoothing_id
# is len( out_table['smooth'] ) - 1.
def add_out_grid_row(
    var_type,
    fit_node_id,
    rate_id,
    mulcov_id,
    in_table,
    out_table,
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
        in_prior_row = in_table['prior'][in_prior_id]
        #
        # out_const_value
        # out_value_prior_id
        if in_prior_row['lower'] == in_prior_row['upper'] :
            out_const_value = in_prior_row['lower']
            assert out_value_prior_id is None
        else :
            assert out_const_value is None
            out_value_prior_id = len( out_table['prior'] )
            #
            # out_prior_row
            out_prior_row  = copy.copy( in_prior_row )
            #
            # var_id
            age_id    = in_grid_row['age_id']
            time_id   = in_grid_row['time_id']
            var_table = out_table['var']
            var_id    = at_cascade.get_var_id(
                var_table   = var_table,
                var_type    = var_type,
                age_id      = age_id,
                time_id     = time_id,
                node_id     = fit_node_id,
                rate_id     = rate_id,
                mulcov_id   = mulcov_id,
                group_id    = 0,
            )
            #
            # out_prior_row['mean']
            fit_var_row           = out_table['fit_var'][var_id]
            fit_var_value         = fit_var_row['fit_var_value']
            assert fit_var_value <= out_prior_row['upper']
            assert out_prior_row['lower'] <= fit_var_value
            out_prior_row['mean'] = fit_var_value
            #
            # out_table['prior']
            out_table['prior'].append( out_prior_row )
            add_index_to_name( out_table['prior'], 'prior_name' )
    # -----------------------------------------------------------------------
    # dage_prior
    # -----------------------------------------------------------------------
    in_prior_id       = in_grid_row['dage_prior_id']
    if in_prior_id == None :
        out_dage_prior_id = None
    else :
        in_prior_row      = in_table['prior'][in_prior_id]
        out_prior_row       = copy.copy( in_prior_row )
        out_dage_prior_id   = len( out_table['prior'] )
        out_table['prior'].append( out_prior_row )
        add_index_to_name( out_table['prior'], 'prior_name' )
    # -----------------------------------------------------------------------
    # dtime_prior
    # -----------------------------------------------------------------------
    in_prior_id       = in_grid_row['dtime_prior_id']
    if in_prior_id == None :
        out_dtime_prior_id = None
    else :
        in_prior_row       = in_table['prior'][in_prior_id]
        out_prior_row        = copy.copy( in_prior_row )
        out_dtime_prior_id   = len( out_table['prior'] )
        out_table['prior'].append( out_prior_row )
        add_index_to_name( out_table['prior'], 'prior_name' )
    # -----------------------------------------------------------------------
    # out_grid_row
    out_grid_row = copy.copy( in_grid_row )
    out_grid_row['value_prior_id']  = out_value_prior_id
    out_grid_row['const_value']     = out_const_value
    out_grid_row['dage_prior_id']   = out_dage_prior_id
    out_grid_row['dtime_prior_id']  = out_dtime_prior_id
    #
    # out_table['smooth_grid']
    out_grid_row['smooth_id']  = len( out_table['smooth'] ) - 1
    out_table['smooth_grid'].append( out_grid_row )
# ----------------------------------------------------------------------------
def no_ode_fit(
# BEGIN syntax
# out_database = at_cascade.no_ode_fit(
    in_database    = None,
    max_fit        = None,
    max_abs_effect = None,
    trace_fit      = False,
# )
# END syntax
) :
    #
    # fit_integrand
    if not max_fit is None :
        fit_integrand = at_cascade.get_fit_integrand(in_database)
    #
    # in_table
    new        = False
    connection = dismod_at.create_connection(in_database, new)
    in_table = dict()
    for name in [
        'integrand',
        'mulcov',
        'node',
        'option',
        'prior',
        'rate',
        'smooth',
        'smooth_grid'
    ] :
        in_table[name] = dismod_at.get_table_dict(connection, name)
    connection.close()
    #
    # fit_node_name
    fit_node_name = at_cascade.get_parent_node(in_database)
    #
    # fit_node_id
    fit_node_id   = at_cascade.table_name2id(
        in_table['node'], 'node', fit_node_name
    )
    #
    # no_ode_daabase, out_database
    index = in_database.rfind('/')
    if 0 <= index :
        in_dir          = in_database[: index]
        out_database    = f'{in_dir}/{fit_node_name}/dismod.db'
        no_ode_database = f'{in_dir}/{fit_node_name}/no_ode.db'
    else :
        out_database    = f'{fit_node_name}/dismod.db'
        no_ode_database = f'{fit_node_name}/no_ode.db'
    #
    msg   = f'in_database and out_database are equal'
    assert not in_database == out_database, msg
    #
    # copy in_database to no_ode_database
    shutil.copyfile(in_database, no_ode_database)
    #
    # hold_out_integrand
    hold_out_integrand = list()
    use_ode = [
        'prevalence', 'Tincidence', 'mtspecific', 'mtall', 'mtstandard'
    ]
    for row in in_table['integrand'] :
        integrand_name = row['integrand_name']
        if integrand_name in use_ode :
            hold_out_integrand.append( integrand_name )
    name  = 'hold_out_integrand'
    value = ' '.join(hold_out_integrand)
    dismod_at.system_command_prc(
        [ 'dismod_at', no_ode_database, 'set', 'option', name, value ]
    )
    #
    # init
    dismod_at.system_command_prc([ 'dismod_at', no_ode_database, 'init' ])
    #
    # bnd_mulcov
    if not max_abs_effect is None :
        dismod_at.system_command_prc([
            'dismod_at', no_ode_database, 'bnd_mulcov', str(max_abs_effect)
        ])
    #
    # enforce max_fit
    if not max_fit is None :
        for integrand_id in fit_integrand :
            row            = in_table['integrand'][integrand_id]
            integrand_name = row['integrand_name']
            dismod_at.system_command_prc([
                'dismod_at',
                no_ode_database,
                'hold_out',
                integrand_name,
                str(max_fit),
            ])
    #
    # fit both
    command = [ 'dismod_at', no_ode_database, 'fit', 'both' ]
    dismod_at.system_command_prc(command, return_stdout = not trace_fit )
    #
    # copy no_ode_database to out_database
    shutil.copyfile(no_ode_database, out_database)
    #
    #
    # out_connection
    new            = False
    out_connection = dismod_at.create_connection(out_database, new)
    #
    # out_table
    out_table = dict()
    for name in [
        'fit_var',
        'var',
    ] :
        out_table[name] = dismod_at.get_table_dict(out_connection, name)
    for name in [
        'prior',
        'mulcov',
        'rate',
        'smooth',
        'smooth_grid',
    ] :
        out_table[name] = list()
    # ------------------------------------------------------------------------
    # out_table['mulcov']
    # and the corresponding entries in smooth, smooth_grid, and prior tables
    for (mulcov_id, in_mulcov_row) in enumerate( in_table['mulcov'] ) :
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
            smooth_row = in_table['smooth'][in_smooth_id]
            smooth_row = copy.copy(smooth_row)
            assert smooth_row['mulstd_value_prior_id'] is None
            assert smooth_row['mulstd_dage_prior_id']  is None
            assert smooth_row['mulstd_dtime_prior_id'] is None
            #
            # out_table['smooth']
            # out_smooth_id
            out_smooth_id = len(out_table['smooth'])
            smooth_row['smooth_name'] += f'_{out_smooth_id}'
            out_table['smooth'].append(smooth_row)
            #
            # out_mulcov_row
            out_mulcov_row['group_smooth_id'] = out_smooth_id
            #
            # out_table['smooth_grid']
            rate_id     = in_mulcov_row['rate_id']
            mulcov_type = in_mulcov_row['mulcov_type']
            var_type = 'mulcov_' + mulcov_type
            for in_grid_row in in_table['smooth_grid'] :
                if in_grid_row['smooth_id'] == in_smooth_id :
                    add_out_grid_row(
                        var_type,
                        fit_node_id,
                        rate_id,
                        mulcov_id,
                        in_table,
                        out_table,
                        in_grid_row
                    )
        #
        # out_table['mulcov_row']
        out_table['mulcov'].append( out_mulcov_row )
    # ------------------------------------------------------------------------
    # out_table['rate']
    # and the corresponding entries in smooth, smooth_grid, and prior tables
    for (rate_id, in_rate_row) in enumerate(in_table['rate']) :
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
            smooth_row = in_table['smooth'][in_smooth_id]
            smooth_row = copy.copy(smooth_row)
            assert smooth_row['mulstd_value_prior_id'] is None
            assert smooth_row['mulstd_dage_prior_id']  is None
            assert smooth_row['mulstd_dtime_prior_id'] is None
            #
            # out_table['smooth']
            # out_smooth_id
            out_smooth_id = len(out_table['smooth'])
            smooth_row['smooth_name'] += f'_{out_smooth_id}'
            out_table['smooth'].append(smooth_row)
            #
            # out_rate_row
            out_rate_row['parent_smooth_id'] = out_smooth_id
            #
            # out_table['smooth_grid']
            mulcov_id = None
            var_type  = 'rate'
            for in_grid_row in in_table['smooth_grid'] :
                if in_grid_row['smooth_id'] == in_smooth_id :
                    add_out_grid_row(
                        var_type,
                        fit_node_id,
                        rate_id,
                        mulcov_id,
                        in_table,
                        out_table,
                        in_grid_row
                    )
        #
        # out_table['rate_row']
        out_table['rate'].append( out_rate_row )
        #
        # in_smooth_id
        in_smooth_id = in_rate_row['child_smooth_id']
        if not in_smooth_id is None :
            #
            # smooth_row
            smooth_row = in_table['smooth'][in_smooth_id]
            smooth_row = copy.copy(smooth_row)
            assert smooth_row['mulstd_value_prior_id'] is None
            assert smooth_row['mulstd_dage_prior_id']  is None
            assert smooth_row['mulstd_dtime_prior_id'] is None
            #
            # out_table['smooth']
            # out_smooth_id
            out_smooth_id = len(out_table['smooth'])
            smooth_row['smooth_name'] += f'_{out_smooth_id}'
            out_table['smooth'].append(smooth_row)
            #
            # out_rate_row
            out_rate_row['child_smooth_id'] = out_smooth_id
            #
            # out_table['smooth_grid']
            for in_grid_row in in_table['smooth_grid'] :
                if in_grid_row['smooth_id'] == in_smooth_id :
                    #
                    # out_grid_row
                    out_grid_row = copy.copy( in_grid_row )
                    for ty in [
                        'value_prior_id', 'dage_prior_id', 'dtime_prior_id'
                    ] :
                        prior_id = in_grid_row[ty]
                        if not prior_id is None :
                            prior_row = in_table['prior'][prior_id]
                            prior_row = copy.copy( prior_row )
                            prior_id  = len( out_table['prior'] )
                            out_table['prior'].append( prior_row )
                            add_index_to_name(
                                out_table['prior'], 'prior_name'
                            )
                            out_grid_row[ty] = prior_id
                    out_grid_row['smooth_id'] = out_smooth_id
                    out_table['smooth_grid'].append( out_grid_row )
    #
    # replace out_table
    for name in out_table :
        if name not in [ 'var', 'fit_var' ] :
            dismod_at.replace_table(out_connection, name, out_table[name])
    #
    # restore hold_out_integrand
    hold_out_integrand = ''
    for row in in_table['option'] :
        if row['option_name'] == 'hold_out_integrand' :
            hold_out_integrand = row['option_value']
    name  = 'hold_out_integrand'
    value = hold_out_integrand
    dismod_at.system_command_prc(
        [ 'dismod_at', out_database, 'set', 'option', name, value ]
    )
    dismod_at.system_command_prc([ 'dismod_at', out_database, 'init' ])
    #
    # out_connection
    out_connection.close()
    #
    return out_database
