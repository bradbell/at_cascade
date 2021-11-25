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

in_database
***********
is a python string specifying the location of a
:ref:`glossary.input_node_database`
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

    *in_dir*\ /\ *fit_node*\ /no_ode/dismod.db

This contains the results of fitting without the ODE integrands
so they can be plotted and converted to csv files.
It has the :ref:`omega_constraint` so that the residuals for
the ODE integrands make sense.
The ODE integrands are not included (are included) for a fit using
the *no_ode_database* (*out_database*).

out_database
************
The return value *out_database* is equal to

    *in_dir*\ /\ *fit_node*\ /dismod.db

which can't be the same file name as *in_database*.
This is an input_node_database similar to *in_database*.
The difference is that the mean value in the priors for the fixed effects
have been replace by the optimal estimate for fitting with out the integrands
that use the ODE.
The last operation on this table is a dismod_at init command.

{xsrst_end no_ode_fit}
'''
import time
import math
import sys
import os
import shutil
import copy
import dismod_at
import at_cascade
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
# out_database = at_cascade.no_ode_fit(
    all_node_database = None,
    in_database       = None,
    max_fit           = None,
    max_abs_effect    = None,
    trace_fit         = False,
# )
# END syntax
) :

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
        fit_integrand = at_cascade.get_fit_integrand(in_database)
    #
    # in_table
    new        = False
    connection = dismod_at.create_connection(in_database, new)
    in_table = dict()
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
    # fit_split_reference_id
    new               = False
    connection        = dismod_at.create_connection(all_node_database, new)
    all_option_table  = dismod_at.get_table_dict(connection, 'all_option')
    split_reference_table = \
        dismod_at.get_table_dict(connection, 'split_reference')
    cov_info = at_cascade.get_cov_info(
        all_option_table, in_table['covariate'], split_reference_table
    )
    fit_split_reference_id = None
    if 'split_reference_id' in cov_info :
        fit_split_reference_id = cov_info['split_reference_id']
    fit_split_reference_id = None
    if 'split_reference_id' in cov_info :
        fit_split_reference_id = cov_info['split_reference_id']
    #
    # no_ode_daabase, out_database
    index = in_database.rfind('/')
    if 0 <= index :
        in_dir          = in_database[: index]
        out_database    = f'{in_dir}/{fit_node_name}/dismod.db'
        no_ode_database = f'{in_dir}/{fit_node_name}/no_ode/dismod.db'
        os.makedirs(f'{in_dir}/{fit_node_name}/no_ode')
    else :
        out_database    = f'{fit_node_name}/dismod.db'
        no_ode_database = f'{fit_node_name}/no_ode/dismod.db'
        os.makedirs(f'{fit_node_name}/no_ode')
    #
    msg   = f'in_database and out_database are equal'
    assert not in_database == out_database, msg
    # ------------------------------------------------------------------------
    # no_ode_database
    # ------------------------------------------------------------------------
    shutil.copyfile(in_database, no_ode_database)
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
    # max_num_iter_fixed
    command  = [ 'dismod_at', no_ode_database ]
    command += [ 'set', 'option', 'max_num_iter_fixed', '150' ]
    dismod_at.system_command_prc(command )
    #
    # fit both
    command = [ 'dismod_at', no_ode_database, 'fit', 'both' ]
    dismod_at.system_command_prc(command, return_stdout = not trace_fit )
    #
    # c_shift_predict_fit_var
    command = [ 'dismod_at', no_ode_database, 'predict', 'fit_var' ]
    dismod_at.system_command_prc(command)
    move_table(connection, 'predict', 'c_shift_predict_fit_var')
    #
    # c_shift_avgint
    move_table(connection, 'avgint', 'c_shift_avgint')
    #
    # out_database
    shift_databases = { fit_node_name : out_database }
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
    return out_database
