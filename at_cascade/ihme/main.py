# -----------------------------------------------------------------------------
# at_cascade: Cascading Dismod_at Analysis From Parent To Child Regions
#           Copyright (C) 2021-22 University of Washington
#              (Bradley M. Bell bradbell@uw.edu)
#
# This program is distributed under the terms of the
#     GNU Affero General Public License version 3.0 or later
# see http://www.gnu.org/licenses/agpl.txt
# -----------------------------------------------------------------------------
import sys
import os
import shutil
import dismod_at
import at_cascade.ihme
# ----------------------------------------------------------------------------
def display(database, max_plot) :
    #
    # pdf_file
    index      = database.rfind('/')
    pdf_dir    = database[0:index]
    #
    # plot_title
    index      = pdf_dir.rfind('/')
    plot_title = pdf_dir[index+1:]
    #
    # integrand_table, rate_table
    new             = False
    connection      = dismod_at.create_connection(database, new)
    integrand_table = dismod_at.get_table_dict(connection, 'integrand')
    rate_table      = dismod_at.get_table_dict(connection, 'rate')
    #
    # data.pdf
    pdf_file = pdf_dir + '/data.pdf'
    n_point_list = dismod_at.plot_data_fit(
        database     = database,
        pdf_file     = pdf_file,
        plot_title   = plot_title,
        max_plot     = max_plot,
    )
    #
    # rate.pdf
    rate_set = set()
    for row in rate_table :
        if not row['parent_smooth_id'] is None :
            rate_set.add( row['rate_name'] )
    pdf_file = pdf_dir + '/rate.pdf'
    plot_set = dismod_at.plot_rate_fit(
        database, pdf_file, plot_title, rate_set
    )
    #
    # db2csv
    dismod_at.system_command_prc([ 'dismodat.py', database, 'db2csv' ])
# ----------------------------------------------------------------------------
def drill(
    result_dir, root_node_name, fit_goal_set, root_node_database, no_ode_fit
) :
    #
    # all_node_database
    all_node_database = f'{result_dir}/all_node.db'
    #
    # cascade_root_node
    at_cascade.cascade_root_node(
        all_node_database  = all_node_database,
        root_node_database = root_node_database,
        fit_goal_set       = fit_goal_set,
        no_ode_fit         = no_ode_fit,
    )
# ----------------------------------------------------------------------------
def main(
    result_dir              = None,
    root_node_name          = None,
    fit_goal_set            = None,
    setup_function          = None,
    max_plot                = None,
    covariate_csv_file_dict = None,
    log_scale_covariate_set = None,
    root_node_database      = None,
    no_ode_fit              = None,
) :
    assert type(result_dir) == str
    assert type(root_node_name) == str
    assert type(fit_goal_set) == set
    assert setup_function is not None
    assert type(max_plot) == int
    assert type(covariate_csv_file_dict) == dict
    assert type(log_scale_covariate_set) == set
    assert type(root_node_database) == str
    assert type(no_ode_fit) == bool
    #
    # command
    command_set = {
        'setup',
        'cleanup',
        'drill',
        'display',
        'continue',
        'predict',
        'summary',
     }
    command     = None
    if len(sys.argv) == 2 :
        if sys.argv[1] not in [ 'display', 'continue' ] :
            command = sys.argv[1]
    if len(sys.argv) == 3 :
        if sys.argv[1] in [ 'display' , 'continue' ] :
            command  = sys.argv[1]
            database = sys.argv[2]
    if command not in command_set :
        program = sys.argv[0].split('/')[-1]
        msg  = f'usage: bin/ihme/{program} command\n'
        msg += f'       bin/ihme/{program} display  database\n'
        msg += f'       bin/ihme/{program} continue database\n'
        msg +=  'where command is one of the following:\n'
        msg +=  'setup:    create at_cascade input databases from csv files\n'
        msg += f'cleanup:  remove root_node_dir\n'
        msg +=  'drill:    run cascade from root node to goal nodes\n'
        msg +=  'continue: continue cascade starting at database\n'
        msg +=  'display:  results for each database at referece covariates\n'
        msg +=  'predict:  results for each database at actual covariates\n'
        msg +=  'summary:  create following files in results directory\n'
        msg +=  '          error, warning, predict.csv, variable.csv'
        sys.exit(msg)
    #
    # result_dir
    if not os.path.exists(result_dir ) :
        os.makedirs( result_dir )
    #
    # root_node_dir
    root_node_dir = f'{result_dir}/{root_node_name}'
    #
    # setup
    if command == 'setup' :
        setup_function()
        return
    #
    # cleanup
    if command == 'cleanup' :
        for name in os.listdir(result_dir) :
            file_name = f'{result_dir}/{name}'
            if os.path.isfile(file_name) or os.path.islink(file_name) :
                print( f'remove {file_name}' )
                os.remove(file_name)
    #
    # drill
    elif command == 'drill' :
        if os.path.exists( root_node_dir ) :
            program = sys.argv[0]
            msg  = f'drill: {root_node_dir} exists. '
            msg += 'You must first move or remove it'
            assert False, msg
        print( f'creating {root_node_dir}' )
        os.mkdir( root_node_dir )
        drill(
            result_dir,
            root_node_name,
            fit_goal_set,
            root_node_database,
            no_ode_fit
         )
    #
    # display or continue
    elif command in [ 'display', 'continue'] :
        if not database.startswith( root_node_name ) :
            msg  = f'{command}: database does not begin with '
            msg += f'root_node_name = {root_node_name}'
            assert False, msg
        if not database.endswith( '/dismod.db' ) :
            msg  = f'{command}: database does not end with /dismod.db'
            assert False, msg
        fit_node_database = f'{result_dir}/{database}'
        if not os.path.exists(fit_node_database) :
            msg  = f'{command}: result_dir/database = {fit_node_database}'
            msg += f'\nfile does not exist'
            assert False, msg
        if command == 'display' :
            display(fit_node_database, max_plot)
        else :
            all_node_database = f'{result_dir}/all_node.db'
            at_cascade.continue_cascade(
                all_node_database = all_node_database,
                fit_node_database = fit_node_database,
                fit_goal_set      = fit_goal_set,
            )
    elif command == 'predict' :
        at_cascade.ihme.predict_csv(
            result_dir              = result_dir,
            covariate_csv_file_dict = covariate_csv_file_dict,
            log_scale_covariate_set = log_scale_covariate_set,
            fit_goal_set            = fit_goal_set,
            root_node_database      = root_node_database,
            max_plot                = max_plot,
        )
    elif command == 'summary' :
        at_cascade.ihme.summary(
            result_dir         = result_dir,
            fit_goal_set       = fit_goal_set,
            root_node_database = root_node_database
        )
    #
    else :
        assert False
