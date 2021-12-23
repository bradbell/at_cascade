# -----------------------------------------------------------------------------
# at_cascade: Cascading Dismod_at Analysis From Parent To Child Regions
#           Copyright (C) 2021-21 University of Washington
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
# ---------------------------------------------------------------------------
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
def drill(root_node_name, fit_goal_set, max_fit, max_abs_effect) :
    #
    # all_node_database
    all_node_database = at_cascade.ihme.all_node_database
    #
    # root_node_database
    root_node_database = at_cascade.ihme.root_node_database
    #
    # no_ode_fit
    fit_node_database = at_cascade.no_ode_fit(
        all_node_database = all_node_database,
        in_database       = root_node_database,
        max_fit           = max_fit,
        max_abs_effect    = max_abs_effect,
        trace_fit         = True,
    )
    results_dir = at_cascade.ihme.results_dir
    assert fit_node_database == f'{results_dir}/{root_node_name}/dismod.db'
    #
    # cascade_root_node
    at_cascade.cascade_root_node(
        all_node_database  = all_node_database,
        root_node_database = fit_node_database,
        fit_goal_set       = fit_goal_set,
        trace_fit         = True,
    )
# ----------------------------------------------------------------------------
def main(
    root_node_name   = None,
    fit_goal_set     = None,
    max_fit          = None,
    max_abs_effect   = None,
    max_plot         = None,
    setup_function   = None,
) :
    assert type(root_node_name) == str
    assert type(fit_goal_set) == set
    assert type(max_fit) == int
    assert type(max_abs_effect) == float
    assert type(max_plot) == int
    assert setup_function is not None
    #
    # results_dir
    results_dir = at_cascade.ihme.results_dir
    #
    # root_node_dir
    root_node_dir = f'{results_dir}/{root_node_name}'
    #
    # command
    command_set = { 'setup', 'cleanup', 'drill', 'display', 'continue' }
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
        msg += f'cleanup:  remove {root_node_dir}\n'
        msg +=  'drill:    run cascade from root node to goal nodes\n'
        msg +=  'display:  display results that are in database\n'
        msg +=  'continue: continue cascade starting at database\n'
        sys.exit(msg)
    #
    # setup
    if command == 'setup' :
        setup_function()
    #
    # cleanup
    elif command == 'cleanup' :
        if not os.path.exists( root_node_dir ) :
            msg  = f'cleanup: Cannot find {root_node_dir}'
            assert False, msg
        #
        # rmtree if dangerous so make sure results_dir is as expected
        if root_node_dir != f'ihme_db/DisMod_AT/results/{root_node_name}' :
            msg  = 'cleanup: results_dir in has changed in '
            msg += 'at_cascade/ihme/__init__.py\n'
            msg += 'You must also change this check in '
            msg += 'at_cascade/ihme/main.py'
            assert False, msg
        print( f'removing {root_node_dir}' )
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
        os.makedirs( root_node_dir )
        drill(root_node_name, fit_goal_set, max_fit, max_abs_effect)
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
            at_cascade.continue_cascade(
                all_node_database = at_cascade.ihme.all_node_database,
                fit_node_database = database,
                fit_goal_set      = fit_goal_set,
                trace_fit         = True,
            )
    #
    else :
        assert False
