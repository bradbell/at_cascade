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
import at_cascade.ihme
# ----------------------------------------------------------------------------
def drill(root_node_name, max_fit, max_abs_effect) :
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
# ----------------------------------------------------------------------------
def main(
    root_node_name   = None,
    max_fit          = None,
    max_abs_effect   = None,
    setup_function   = None,
) :
    assert type(root_node_name) == str
    assert type(max_fit) == int
    assert type(max_abs_effect) == float
    assert setup_function is not None
    #
    # results_dir
    results_dir = at_cascade.ihme.results_dir
    #
    # root_node_dir
    root_node_dir = f'{results_dir}/{root_node_name}'
    #
    # command
    command_set = { 'setup', 'cleanup', 'drill' }
    command     = None
    if len(sys.argv) == 2 :
        command = sys.argv[1]
    if command not in command_set :
        program = sys.argv[0].split('/')[-1]
        msg  =  f'usage: bin/ihme/{program} command\n'
        msg +=  '       where command is one of the following:\n'
        msg +=  'setup:   create at_cascade input databases from csv files\n'
        msg += f'cleanup: remove {root_node_dir}\n'
        msg +=  'drill:   run cascade from root node to goal nodes\n'
        sys.exit(msg)
    if command == 'setup' :
        setup_function()
    elif command == 'cleanup' :
        if not os.path.exists( root_node_dir ) :
            msg  = f'cleanup: Cannot find {root_node_dir}'
            sys.exit(msg)
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
    elif command == 'drill' :
        if os.path.exists( root_node_dir ) :
            program = sys.argv[0]
            msg  = f'drill: {root_node_dir} exists. '
            msg += 'Use following to remove it\n'
            msg += f'{program} cleanup'
            sys.exit(msg)
        print( f'creating {root_node_dir}' )
        os.makedirs( root_node_dir )
        drill(root_node_name, max_fit, max_abs_effect)
    else :
        assert False
