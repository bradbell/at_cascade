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
{xsrst_begin run_one_job}
{xsrst_spell
    dir
    var
}

Run One Job
###########

Syntax
******
{xsrst_file
    # BEGIN syntax
    # END syntax
}

Default Value
*************
None of the arguments to this routine can be ``None``.

job_table
*********
This is a :ref:`create_job_table.job_table` containing the jobs
necessary to fit the :ref:`glossary.fit_goal_set`.

run_job_id
**********
This is the :ref:`create_job_table.job_table.job_id`
for the job that is run.

all_node_database
*****************
is a python string specifying the location of the
:ref:`all_node_db<all_node_db>`
relative to the current working directory.

node_table
**********
is a ``list`` of ``dict`` containing the node table for this cascade.

fit_integrand
*************
is a ``set`` of integrand_id values that occur in the data table; see
:ref:`get_fit_integrand`.

trace_fit
*********
if ``True``, ( ``False`` ) the progress of the dismod at fit commands
will be printed on standard output during the optimization.

fit_node_database
*****************
The :ref:`glossary.fit_node_database` for this fit is
*fit_node_dir*\ ``/dismod.db`` where *fit_node_dir*
is the :ref:`get_database_dir.database_dir` returned by
get_database_dir for the fit node and split_reference_id corresponding
to *run_job_id*.

Upon Input
==========
On input, *fit_node_database* is an :ref:`glossary.input_node_database`.

fit_var
=======
Upon return, the fit_var table correspond to the posterior
mean for the model variables for the fit_node.

sample
======
Upon return,
the sample table contains the corresponding samples from the posterior
distribution for the model variables for the fit_node.

c_predict_fit_var
=================
Upon return,
the c_predict_fit_var table contains the predict table corresponding to the
predict fit_var command using the avgint table in the
root_node_database except that values in the node_id column
has been replaced by the node_id for this fit_node.
Note that the predict_id column name was changed to c_predict_fit_var_id
(which is not the same as var_id).

c_predict_sample
================
Upon return,
the c_predict_sample table contains the predict table corresponding to the
predict sample command using the avgint table in the
root_node_database except that values in the node_id column
has been replaced by the node_id for this fit_node.
Note that the predict_id column name was changed to c_predict_sample_id
(which is not the same as sample_id).

log
===
Upon return,
the log table contains a summary of the operations preformed on dismod.db
between it's input and output state.

{xsrst_end run_one_job}
'''
# ----------------------------------------------------------------------------
import datetime
import os
import time
import dismod_at
import at_cascade
# -----------------------------------------------------------------------------
def system_command(command, file_stdout) :
    if file_stdout is None :
        dismod_at.system_command_prc(
            command,
            print_command = True,
            return_stdout = False,
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
# ----------------------------------------------------------------------------
def set_avgint_node_id(connection, fit_node_id) :
    avgint_table = dismod_at.get_table_dict(connection, 'avgint')
    for row in avgint_table :
        row['node_id'] = fit_node_id
    dismod_at.replace_table(connection, 'avgint', avgint_table)
# ----------------------------------------------------------------------------
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
def run_one_job(
# BEGIN syntax
# run_one_job(
    job_table         = None,
    run_job_id        = None,
    all_node_database = None,
    node_table        = None,
    fit_integrand     = None,
    trace_fit         = None,
# )
# END syntax
) :
    assert job_table         is not None
    assert run_job_id        is not None
    assert all_node_database is not None
    assert node_table        is not None
    assert trace_fit         is not None
    #
    # fit_node_id
    fit_node_id = job_table[run_job_id]['fit_node_id']
    #
    # fit_split_reference_id
    fit_split_reference_id = job_table[run_job_id]['split_reference_id']
    #
    # start_child_job_id
    start_child_job_id = job_table[run_job_id]['start_child_job_id']
    #
    # end_child_job_id
    end_child_job_id = job_table[run_job_id]['end_child_job_id']
    #
    # all_table
    new         = False
    connection  = dismod_at.create_connection(all_node_database, new)
    all_table = dict()
    for tbl_name in [ 'all_option', 'split_reference', 'node_split' ] :
        all_table[tbl_name] = dismod_at.get_table_dict(connection, tbl_name)
    connection.close()
    #
    # all_option_dict
    all_option_dict = dict()
    for row in all_table['all_option'] :
        all_option_dict[ row['option_name']  ] = row['option_value']
    #
    # results_dir
    results_dir = all_option_dict['results_dir']
    #
    # root_node_id
    name         = all_option_dict['root_node_name']
    root_node_id = at_cascade.table_name2id(node_table, 'node', name)
    #
    # root_split_reference_id
    if 'root_split_reference_name' not in all_option_dict :
        root_split_reference_id = None
    else :
        name = all_option_dict['root_split_reference_name']
        root_split_reference_id   = at_cascade.table_name2id(
            all_table['split_reference'], 'split_reference', name
        )
    #
    # perturb_optimization_scaling
    key = 'perturb_optimization_scaling'
    if key in all_option_dict :
        perturb_optimization_scaling = all_option_dict[key]
        if float(perturb_optimization_scaling) < 0.0 :
            msg = 'run_one_job: perturb_optimization_scaling = '
            msg += perturb_optimization_scaling
            assert False, msg
    else :
        perturb_optimization_scaling = '0'
    #
    # node_split_set
    node_split_set = set()
    for row in all_table['node_split'] :
        node_split_set.add( row['node_id'] )
    #
    # fit_node_database
    database_dir = at_cascade.get_database_dir(
        node_table              = node_table,
        split_reference_table   = all_table['split_reference'],
        node_split_set          = node_split_set,
        root_node_id            = root_node_id,
        root_split_reference_id = root_split_reference_id,
        fit_node_id             = fit_node_id ,
        fit_split_reference_id  = fit_split_reference_id,
    )
    fit_node_database = f'{results_dir}/{database_dir}/dismod.db'
    #
    # trace_file_name, file_stdout
    trace_file_name = None
    file_stdout     = None
    if trace_fit :
        trace_file_name = f'{results_dir}/{database_dir}/trace.out'
        file_stdout    = open(trace_file_name, 'w')
        now            = datetime.datetime.now()
        current_time   = now.strftime("%H:%M:%S")
        print( f'Begin: {current_time}: {trace_file_name}' )
    #
    # check fit_node_database
    parent_node_name = at_cascade.get_parent_node(fit_node_database)
    assert parent_node_name == node_table[fit_node_id]['node_name']
    #
    # connection
    new        = False
    connection = dismod_at.create_connection(fit_node_database, new)
    #
    # integrand_table
    integrand_table = dismod_at.get_table_dict(connection, 'integrand')
    #
    # log table
    create_empty_log_table(connection)
    #
    # omega_constraint
    at_cascade.omega_constraint(all_node_database, fit_node_database)
    add_log_entry(connection, 'omega_constraint')
    #
    # init
    command = [ 'dismod_at', fit_node_database, 'init' ]
    system_command(command, file_stdout)
    #
    # max_fit
    if 'max_fit' in all_option_dict :
        max_fit = all_option_dict['max_fit']
        for integrand_id in fit_integrand :
            integrand_name = integrand_table[integrand_id]['integrand_name']
            command = [
                'dismod_at', fit_node_database,
                'hold_out', integrand_name, max_fit
            ]
            system_command(command, file_stdout)
    #
    # max_abs_effect
    if 'max_abs_effect' in all_option_dict:
        max_abs_effect = all_option_dict['max_abs_effect']
        command =[
            'dismod_at', fit_node_database, 'bnd_mulcov', max_abs_effect
        ]
        system_command(command, file_stdout)
    #
    # perturb_optimization_scaling
    if 0 < float( perturb_optimization_scaling ) :
        sigma = perturb_optimization_scaling
        command = [
            'dismodat.py', fit_node_database, 'perturb', 'scale_var', sigma
        ]
        system_command(command, file_stdout)
    #
    # fit
    command = [ 'dismod_at', fit_node_database, 'fit', 'both' ]
    system_command(command, file_stdout)
    #
    # sample
    command = [
        'dismod_at', fit_node_database, 'sample', 'asymptotic', 'both', '20'
    ]
    system_command(command, file_stdout)
    #
    # move avgint -> c_root_avgint
    move_table(connection, 'avgint', 'c_root_avgint')
    #
    # avgint_parent_grid
    at_cascade.avgint_parent_grid(all_node_database, fit_node_database)
    add_log_entry(connection, 'avgint_parent_grid')
    #
    # c_shift_predict_fit_var
    command = [ 'dismod_at', fit_node_database, 'predict', 'fit_var' ]
    system_command(command, file_stdout)
    move_table(connection, 'predict', 'c_shift_predict_fit_var')
    #
    # c_shift_predict_sample
    command = [ 'dismod_at', fit_node_database, 'predict', 'sample' ]
    system_command(command, file_stdout)
    move_table(connection, 'predict', 'c_shift_predict_sample')
    #
    # c_shift_avgint
    # is the table created by avgint_parent_grid
    move_table(connection, 'avgint', 'c_shift_avgint')
    #
    # shift_databases
    shift_databases = dict()
    for job_id in range(start_child_job_id, end_child_job_id) :
        #
        # shift_node_id
        shift_node_id = job_table[job_id]['fit_node_id']
        #
        # shift_split_reference_id
        shift_split_reference_id = job_table[job_id]['split_reference_id']
        #
        # shift_database_dir
        database_dir = at_cascade.get_database_dir(
            node_table              = node_table,
            split_reference_table   = all_table['split_reference'],
            node_split_set          = node_split_set,
            root_node_id            = root_node_id,
            root_split_reference_id = root_split_reference_id,
            fit_node_id             = shift_node_id ,
            fit_split_reference_id  = shift_split_reference_id,
        )
        shift_database_dir = f'{results_dir}/{database_dir}'
        if not os.path.exists(shift_database_dir) :
            os.makedirs(shift_database_dir)
        #
        # shift_node_database
        shift_node_database = f'{shift_database_dir}/dismod.db'
        #
        # shift_name
        shift_name = shift_database_dir.split('/')[-1]
        #
        # shfit_databases
        shift_databases[shift_name] = shift_node_database
    #
    # create shifted databases
    at_cascade.create_shift_db(
        all_node_database,
        fit_node_database,
        shift_databases,
    )
    #
    # move c_root_avgint -> avgint
    move_table(connection, 'c_root_avgint', 'avgint')
    #
    # node_id for predictions for fit_node
    set_avgint_node_id(connection, fit_node_id)
    #
    # c_predict_fit_var
    command = [ 'dismod_at', fit_node_database, 'predict', 'fit_var' ]
    system_command(command, file_stdout)
    move_table(connection, 'predict', 'c_predict_fit_var')
    #
    # c_predict_sample
    command = [ 'dismod_at', fit_node_database, 'predict', 'sample' ]
    system_command(command, file_stdout)
    move_table(connection, 'predict', 'c_predict_sample')
    #
    # connection
    connection.close()
    #
    if trace_fit :
        now            = datetime.datetime.now()
        current_time   = now.strftime("%H:%M:%S")
        print( f'End:   {current_time}: {trace_file_name}' )
