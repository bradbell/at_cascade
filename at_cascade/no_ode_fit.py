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

all_node_database
*****************
is a python string containing the name of the :ref:`all_node_db`.
This argument can't be ``None``.

root_node_database
******************
is a python string specifying the location of the
:ref:`glossary.root_node_database`.
This argument can't be ``None``.

all_option_dict
***************
is a ``dict`` containing the values in the all_option table.
This dictionary has a key for each
:ref:`all_option_table.table_format.option_name`
and the corresponding value is
:ref:`all_option_table.table_format.option_value`.
If an option does not appear in the table, the corresponding key
does not appear in *all_option_dict*.

trace_fit
*********
if ``True``, ( ``False`` ) the dismod_at commands,
and the optimizer trace, are written to the file

    *results_dir*\ /\ *root_node_name*\ /no_ode/trace.out

otherwise, the dismod_at commands are written to standard output.

no_ode_database
***************
An intermediate database is stored in the file

    *results_dir*\ /\ *root_node_name*\ /no_ode/dismod.db

see :ref:`all_option_table.results_dir`
and :ref:`all_option_table.root_node_name`.
This contains the results of fitting without the ODE integrands
so they can be plotted and converted to csv files.
It has the :ref:`omega_constraint` so that the residuals for
the ODE integrands make sense.
The ODE integrands are not included (are included) for a fit using
the *no_ode_database* (*root_fit_database*).

root_fit_database
*****************
The return value *root_fit_database* is equal to

    *results_dir*\ /\ *root_node_name*\ /dismod.db

which can't be the same file name as *root_node_database*.
This is an input_node_database similar to *root_node_database*.
The difference is that the mean value in the priors for the fixed effects
have been replace by the optimal estimate for fitting with out the integrands
that use the ODE.
The last operation on this table is a dismod_at init command.

{xsrst_end no_ode_fit}
'''
import datetime
import time
import math
import sys
import os
import shutil
import copy
import dismod_at
import at_cascade
# -----------------------------------------------------------------------------
def system_command(command, file_stdout) :
    if file_stdout is None :
        dismod_at.system_command_prc(
            command,
            print_command = True,
            return_stdout = True,
            return_stderr = False,
            file_stdout   = None,
            file_stderr   = None,
            write_command = False,
        )
    else :
        dismod_at.system_command_prc(
            command,
            print_command = False,
            return_stdout = False,
            return_stderr = False,
            file_stdout   = file_stdout,
            file_stderr   = None,
            write_command = True,
        )
# -----------------------------------------------------------------------------
def create_empty_log_table(connection) :
    #
    cmd  = 'create table if not exists log('
    cmd += ' log_id        integer primary key,'
    cmd += ' message_type  text               ,'
    cmd += ' table_name    text               ,'
    cmd += ' row_id        integer            ,'
    cmd += ' unix_time     integer            ,'
    cmd += ' message       text               )'
    dismod_at.sql_command(connection, cmd)
    #
    # log table
    empty_list = list()
    dismod_at.replace_table(connection, 'log', empty_list)
# ----------------------------------------------------------------------------
def add_log_entry(connection, message) :
    #
    # log_table
    log_table = dismod_at.get_table_dict(connection, 'log')
    #
    # seconds
    seconds   = int( time.time() )
    #
    # message_type
    message_type = 'at_cascade'
    #
    # cmd
    cmd = 'insert into log'
    cmd += ' (log_id,message_type,table_name,row_id,unix_time,message) values('
    cmd += str( len(log_table) ) + ','     # log_id
    cmd += f'"{message_type}",'            # message_type
    cmd += 'null,'                         # table_name
    cmd += 'null,'                         # row_id
    cmd += str(seconds) + ','              # unix_time
    cmd += f'"{message}")'                 # message
    dismod_at.sql_command(connection, cmd)
# ----------------------------------------------------------------------------
def move_table(connection, src_name, dst_name) :
    #
    command     = 'DROP TABLE IF EXISTS ' + dst_name
    dismod_at.sql_command(connection, command)
    #
    command     = 'ALTER TABLE ' + src_name + ' RENAME COLUMN '
    command    += src_name + '_id TO ' + dst_name + '_id'
    dismod_at.sql_command(connection, command)
    #
    command     = 'ALTER TABLE ' + src_name + ' RENAME TO ' + dst_name
    dismod_at.sql_command(connection, command)
    #
    # log table
    message      = f'move table {src_name} to {dst_name}'
    add_log_entry(connection, message)
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
def no_ode_fit(
# BEGIN syntax
# root_fit_database = at_cascade.no_ode_fit(
    all_node_database   = None,
    root_node_database  = None,
    all_option_dict     = None,
    trace_fit           = False,
# )
# END syntax
) :
    assert type(all_node_database) == str
    assert type(root_node_database) == str
    assert type(all_option_dict) == dict
    assert type(trace_fit) == bool
    #
    # results_dir, max_fit, max_abs_effect
    results_dir    = None
    max_fit        = None
    max_abs_effect = None
    if 'results_dir' in all_option_dict :
        results_dir =  all_option_dict['results_dir']
    if 'max_fit' in all_option_dict :
        max_fit = int( all_option_dict['max_fit'] )
    if 'max_abs_effect' in all_option_dict :
        max_abs_effect = float( all_option_dict['max_abs_effect'] )
    assert results_dir is not None
    #
    # name_rate2integrand
    name_rate2integrand = {
        'pini'  : 'prevalence',
        'iota'  : 'Sincidence',
        'rho'   : 'remission',
        'chi'   : 'mtexcess',
    }
    #
    # fit_integrand
    if not max_fit is None :
        fit_integrand = at_cascade.get_fit_integrand(root_node_database)
    #
    # root_table
    new        = False
    connection = dismod_at.create_connection(root_node_database, new)
    root_table = dict()
    for name in [
        'covariate',
        'integrand',
        'mulcov',
        'node',
        'option',
        'prior',
        'rate',
        'smooth',
        'smooth_grid'
    ] :
        root_table[name] = dismod_at.get_table_dict(connection, name)
    connection.close()
    #
    # root_node_name
    root_node_name = at_cascade.get_parent_node(root_node_database)
    #
    # root_node_id
    root_node_id   = at_cascade.table_name2id(
        root_table['node'], 'node', root_node_name
    )
    #
    # root_split_reference_id
    new               = False
    connection        = dismod_at.create_connection(all_node_database, new)
    all_option_table  = dismod_at.get_table_dict(connection, 'all_option')
    split_reference_table = \
        dismod_at.get_table_dict(connection, 'split_reference')
    cov_info = at_cascade.get_cov_info(
        all_option_table, root_table['covariate'], split_reference_table
    )
    root_split_reference_id = None
    if 'split_reference_id' in cov_info :
        root_split_reference_id = cov_info['split_reference_id']
    root_split_reference_id = None
    if 'split_reference_id' in cov_info :
        root_split_reference_id = cov_info['split_reference_id']
    #
    # no_ode_daabase, root_fit_database
    root_fit_database    = f'{results_dir}/{root_node_name}/dismod.db'
    no_ode_database      = f'{results_dir}/{root_node_name}/no_ode/dismod.db'
    os.makedirs(f'{results_dir}/{root_node_name}/no_ode')
    if root_node_database == root_fit_database :
        msg   = f'root_node_database and root_fit_database are equal'
        assert False, msg
    #
    # trace_file_name, file_stdout
    trace_file_name = None
    file_stdout     = None
    if trace_fit :
        trace_file_name = f'{results_dir}/{root_node_name}/no_ode/trace.out'
        file_stdout    = open(trace_file_name, 'w')
        now            = datetime.datetime.now()
        current_time   = now.strftime("%H:%M:%S")
        print( f'Begin: {current_time}: {trace_file_name}' )
    # ------------------------------------------------------------------------
    # no_ode_database
    # ------------------------------------------------------------------------
    shutil.copyfile(root_node_database, no_ode_database)
    #
    # connection
    new        = False
    connection = dismod_at.create_connection(no_ode_database, new)
    #
    # log table
    create_empty_log_table(connection)
    #
    # omega_constraint
    at_cascade.omega_constraint(all_node_database, no_ode_database)
    add_log_entry(connection, 'omega_constraint')
    #
    # move avgint -> c_root_avgint
    move_table(connection, 'avgint', 'c_root_avgint')
    #
    # avgint_parent_grid
    at_cascade.avgint_parent_grid(all_node_database, no_ode_database)
    add_log_entry(connection, 'avgint_parent_grid')
    #
    # hold_out_integrand
    hold_out_integrand = list()
    use_ode = [
        'susceptible',
        'withC',
        'prevalence',
        'Tincidence',
        'mtspecific',
        'mtall',
        'mtstandard',
    ]
    for row in root_table['integrand'] :
        integrand_name = row['integrand_name']
        if integrand_name in use_ode :
            hold_out_integrand.append( integrand_name )
    name  = 'hold_out_integrand'
    value = ' '.join(hold_out_integrand)
    command = [
        'dismod_at', no_ode_database, 'set', 'option', name, value
    ]
    system_command(command, file_stdout)
    #
    # init
    command = [ 'dismod_at', no_ode_database, 'init' ]
    system_command(command, file_stdout)
    #
    # bnd_mulcov
    if not max_abs_effect is None :
        command = [
            'dismod_at', no_ode_database, 'bnd_mulcov', str(max_abs_effect)
        ]
        system_command(command, file_stdout)
    #
    # enforce max_fit
    if not max_fit is None :
        for integrand_id in fit_integrand :
            row            = root_table['integrand'][integrand_id]
            integrand_name = row['integrand_name']
            command = [
                'dismod_at',
                no_ode_database,
                'hold_out',
                integrand_name,
                str(max_fit),
            ]
            system_command(command, file_stdout)
    #
    # max_num_iter_fixed
    # Pass max_num_iter_fixed as an argument to no_ode and then restore
    # value in database.
    # command  = [ 'dismod_at', no_ode_database ]
    # command += [ 'set', 'option', 'max_num_iter_fixed', '100' ]
    # dismod_at.system_command_prc(command )
    #
    # fit both
    command = [ 'dismod_at', no_ode_database, 'fit', 'both' ]
    system_command(command, file_stdout)
    #
    # c_shift_predict_fit_var
    command = [ 'dismod_at', no_ode_database, 'predict', 'fit_var' ]
    system_command(command, file_stdout)
    move_table(connection, 'predict', 'c_shift_predict_fit_var')
    #
    # c_shift_avgint
    move_table(connection, 'avgint', 'c_shift_avgint')
    #
    # root_fit_database
    shift_databases = { root_node_name : root_fit_database }
    at_cascade.create_shift_db(
        all_node_database = all_node_database ,
        fit_node_database = no_ode_database   ,
        shift_databases   = shift_databases   ,
        predict_sample    = False             ,
    )
    #
    # move c_root_avgint -> avgint
    move_table(connection, 'c_root_avgint', 'avgint')
    #
    # restore hold_out_integrand
    hold_out_integrand = ''
    for row in root_table['option'] :
        if row['option_name'] == 'hold_out_integrand' :
            hold_out_integrand = row['option_value']
    name  = 'hold_out_integrand'
    value = hold_out_integrand
    command = [
        'dismod_at', root_fit_database, 'set', 'option', name, value
    ]
    system_command(command, file_stdout)
    #
    if trace_fit :
        now            = datetime.datetime.now()
        current_time   = now.strftime("%H:%M:%S")
        print( f'End:   {current_time}: {trace_file_name}' )
    #
    return root_fit_database
