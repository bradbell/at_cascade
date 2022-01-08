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
def drill(result_dir, root_node_name, fit_goal_set, root_node_database) :
    #
    # all_node_database
    all_node_database = f'{result_dir}/all_node.db'
    #
    # cascade_root_node
    at_cascade.cascade_root_node(
        all_node_database  = all_node_database,
        root_node_database = root_node_database,
        fit_goal_set       = fit_goal_set,
        no_ode_fit         = True,
    )
# ----------------------------------------------------------------------------
def main(
    result_dir              = None,
    root_node_name          = None,
    fit_goal_set            = None,
    setup_function          = None,
    max_plot                = None,
    covariate_csv_file_dict = None,
    root_node_database      = None,
) :
    assert type(result_dir) == str
    assert type(root_node_name) == str
    assert type(fit_goal_set) == set
    assert setup_function is not None
    assert type(max_plot) == int
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
        msg +=  'display:  display results that are in database\n'
        msg +=  'continue: continue cascade starting at database\n'
        msg +=  'predict:  create the predict.csv files for each databse\n'
        msg +=  'summary:  create following files in results directory\n'
        msg +=  '          error, warning, predict.csv'
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
        if not os.path.exists( root_node_dir ) :
            msg  = f'cleanup: Cannot find {root_node_dir}'
            assert False, msg
        #
        # rmtree if dangerous so make sure result_dir is as expected
        if not root_node_dir.startswith('ihme_db/DisMod_AT/results/') :
            msg  = 'cleanup: result_dir in has changed in '
            msg += 'at_cascade/ihme/__init__.py\n'
            msg += 'You must also change this check in '
            msg += 'at_cascade/ihme/main.py'
            assert False, msg
        #
        print( f'removing {root_node_dir}' )
        if os.path.islink(root_node_dir) :
            os.remove(root_node_dir)
        else :
            shutil.rmtree( root_node_dir )
    #
    # drill
    elif command == 'drill' :
        if os.path.exists( root_node_dir ) :
            program = sys.argv[0]
            msg  = f'drill: {root_node_dir} exists. '
            msg += 'Use following to remove it\n'
            msg += f'{program} cleanup'
            assert False, msg
        print( f'creating {root_node_dir}' )
        drill( result_dir, root_node_name, fit_goal_set, root_node_database )
    #
    # display or continue
    elif command in [ 'display', 'continue'] :
        if not database.startswith( root_node_dir ) :
            msg  = f'{command}: database does not begin with\n'
            msg += root_node_dir
            assert False, msg
        if not database.endswith( '/dismod.db' ) :
            msg  = f'{command}: database does not end with /dismod.db'
            assert False, msg
        if command == 'display' :
            display(database, max_plot)
        else :
            all_node_database = f'{result_dir}/all_node.db'
            at_cascade.continue_cascade(
                all_node_database = all_node_database,
                fit_node_database = database,
                fit_goal_set      = fit_goal_set,
            )
    elif command == 'predict' :
        at_cascade.ihme.predict_csv(
            result_dir              = result_dir,
            covariate_csv_file_dict = covariate_csv_file_dict,
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
