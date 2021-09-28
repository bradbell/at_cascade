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
{xsrst_begin_parent max_fit_option}
{xsrst_spell
    dage
    dtime
}

Example Using max_fit Option
############################
For this example everything is constant in age and time.

Nodes
*****
The following is a diagram of the node tree for this example.
The :ref:`glossary.root_node` is n0,
the :ref:`glossary.fit_goal_set` is {n3, n4, n5, n6},
and the leaf nodes are {n3, n4, n5, n6}::

                n0
          /-----/\-----\
        n1             (n2)
       /  \            /  \
    (n3)  (n4)       n5    n6

fit_goal_set
============
{xsrst_file
    # BEGIN fit_goal_set
    # END fit_goal_set
}

Rates
*****
The only non-zero dismod_at rate for this example is
:ref:`glossary.iota`.

Covariate
*********
There are no covariates for this example.


Simulated Data
**************

Random Seed
===========
The random seed can be used to reproduce results.
If the original value of this setting is zero, the clock is used get
a random seed. The actual value or *random_seed* is always printed.
{xsrst_file
    # BEGIN random_seed
    # END random_seed
}


rate_true(rate, a, t, n, c)
===========================
For *rate* equal to iota,
this is the true value for *rate*
in node *n* at age *a*, time *t*, and covariate values *c*.
The values *a*, *t*. *c*, are not used by this function for this example.
{xsrst_file
    # BEGIN rate_true
    # END rate_true
}

y_i
===
The only simulated integrand for this example is :ref:`glossary.sincidence`
which is a direct measurement of iota.
This data is simulated without any noise; i.e.,
the i-th measurement is simulated as
*y_i = rate_true('iota', None, None, n_i, None)* where *n_i* is the node.
The data is modeled as having noise even though there is no simulated noise.

n_i
===
Data is only simulated for the leaf nodes; i.e.,
each *n_i* is in the set { n3, n4, n5, n6 }.
Since the data does not have any nose, the data residuals are a measure
of how good the fit is for the nodes in the fit_goal_set.

max_fit_option
==============
This is the value of the :ref:`all_option_table.max_fit` option.
It is also te number of data values per leaf.
Thus the leaf nodes fit all their data while the other nodes only fit
a randomly chosen subset of their data.
{xsrst_file
    # BEGIN max_fit_option
    # END max_fit_option
}

Parent Rate Smoothing
*********************
This is the iota smoothing used for the fit_node.
There are no :ref:`glossary.dage` or :ref:`glossary.dtime`
priors because there is only one age and one time point.

Value Prior
===========
The following is the value prior used for the root_node
{xsrst_file
    # BEGIN parent_value_prior
    # END parent_value_prior
}
The mean and standard deviation are only used for the root_node.
The :ref:`create_child_node_db<create_child_node_db>`
routine replaces them for other nodes.

Child Rate Smoothing
********************
This is the smoothing used for the
random effect for each child of the fit_node.
There are no dage or dtime
priors because there is only one age and one time point in this smoothing.

Value Prior
===========
The following is the value prior used for the children of the fit_node:
{xsrst_file
    # BEGIN child_value_prior
    # END child_value_prior
}

Checking The Fit
****************
The results of the fit are in the
:ref:`cascade_fit_node.output_dismod_db.predict` and
:ref:`cascade_fit_node.output_dismod_db.c_predict_fit_var`
tables of the fit_node_database corresponding to each node.
The :ref:`check_cascade_fit<check_cascade_fit>`
routine uses these tables to check that fit against the truth.

{xsrst_end max_fit_option}
------------------------------------------------------------------------------
{xsrst_begin max_fit_option_py}

max_fit_option: Python Source Code
###################################

{xsrst_file
    BEGIN source code
    END source code
}

{xsrst_end max_fit_option_py}
'''
# BEGIN source code
# ----------------------------------------------------------------------------
# imports
# ----------------------------------------------------------------------------
import math
import sys
import os
import copy
import time
import csv
import random
import shutil
import distutils.dir_util
import dismod_at
from math import exp
#
# import at_cascade with a preference current directory version
current_directory = os.getcwd()
if os.path.isfile( current_directory + '/at_cascade/__init__.py' ) :
    sys.path.insert(0, current_directory)
import at_cascade
# -----------------------------------------------------------------------------
# global varables
# -----------------------------------------------------------------------------
# BEGIN fit_goal_set
fit_goal_set = { 'n3', 'n4', 'n5', 'n6' }
# END fit_goal_set
#
# BEGIN random_seed
random_seed = 0
if random_seed == 0 :
    random_seed = int( time.time() )
random.seed(random_seed)
print('max_fit_option: random_seed = ', random_seed)
# END random_seed
#
# BEGIN max_fit_option
max_fit_option = 10
# END max_fit_option
#
# ----------------------------------------------------------------------------
# functions
# ----------------------------------------------------------------------------
# BEGIN rate_true
def rate_true(rate, a, t, n, c) :
    iota_true = {
        'n3' : 0.04,
        'n4' : 0.05,
        'n5' : 0.06,
        'n6' : 0.07,
    }
    iota_true['n1'] = (iota_true['n3'] + iota_true['n4']) / 2.0
    iota_true['n2'] = (iota_true['n5'] + iota_true['n6']) / 2.0
    iota_true['n0'] = (iota_true['n1'] + iota_true['n2']) / 2.0
    if rate == 'iota' :
        return iota_true[n]
    return 0.0
# END rate_true
# ----------------------------------------------------------------------------
def root_node_db(file_name) :
    #
    # BEGIN iota_mean
    iota_mean      = rate_true('iota', None, None, 'n0', None)
    # END iota_mean
    #
    # prior_table
    prior_table = list()
    prior_table.append(
        # BEGIN parent_value_prior
        {   'name':    'parent_value_prior',
            'density': 'gaussian',
            'lower':   iota_mean / 10.0,
            'upper':   iota_mean * 10.0,
            'mean':    iota_mean,
            'std':     iota_mean,
            'eta':     iota_mean * 1e-3
        }
        # END parent_value_prior
    )
    prior_table.append(
        # BEGIN child_value_prior
        {   'name':    'child_value_prior',
            'density': 'gaussian',
            'mean':    0.0,
            'std':     10.0,
        }
        # END child_value_prior
    )
    #
    # smooth_table
    smooth_table = list()
    #
    # parent_smooth
    fun = lambda a, t : ('parent_value_prior', None, None)
    smooth_table.append({
        'name':       'parent_smooth',
        'age_id':     [0],
        'time_id':    [0],
        'fun':        fun,
    })
    #
    # child_smooth
    fun = lambda a, t : ('child_value_prior', None, None)
    smooth_table.append({
        'name':       'child_smooth',
        'age_id':     [0],
        'time_id':    [0],
        'fun':        fun,
    })
    #
    # node_table
    node_table = [
        { 'name':'n0',        'parent':''   },
        { 'name':'n1',        'parent':'n0' },
        { 'name':'n2',        'parent':'n0' },
        { 'name':'n3',        'parent':'n1' },
        { 'name':'n4',        'parent':'n1' },
        { 'name':'n5',        'parent':'n2' },
        { 'name':'n6',        'parent':'n2' },
    ]
    #
    # rate_table
    rate_table = [ {
        'name':           'iota',
        'parent_smooth':  'parent_smooth',
        'child_smooth':   'child_smooth',
    } ]
    #
    # covariate_table
    covariate_table = list()
    #
    # mulcov_table
    mulcov_table = list()
    #
    # subgroup_table
    subgroup_table = [ {'subgroup': 'world', 'group':'world'} ]
    #
    # integrand_table
    integrand_table = [ {'name':'Sincidence'} ]
    #
    # avgint_table
    avgint_table = list()
    row = {
        'node':         'n0',
        'subgroup':     'world',
        'weight':       '',
        'age_lower':    50.0,
        'age_upper':    50.0,
        'time_lower':   2000.0,
        'time_upper':   2000.0,
        'income':       None,
        'integrand':    'Sincidence',
    }
    avgint_table.append( copy.copy(row) )
    #
    # data_table
    data_table  = list()
    leaf_set    = { 'n3', 'n4', 'n5', 'n6' }
    for j in range( max_fit_option ) :
        row = {
            'subgroup':     'world',
            'weight':       '',
            'age_lower':    50.0,
            'age_upper':    50.0,
            'time_lower':   2000.0,
            'time_upper':   2000.0,
            'integrand':    'Sincidence',
            'density':      'gaussian',
            'hold_out':     False,
        }
        for node in leaf_set :
                meas_value        = rate_true('iota', None, None, node, None)
                row['node']       = node
                row['meas_value'] = meas_value
                row['meas_std']   = meas_value / 10.0
                data_table.append( copy.copy(row) )
    #
    # time_grid
    age_grid = [ 0.0, 100.0 ]
    #
    # time_grid
    time_grid = [ 2000.0 ]
    #
    # weight table:
    weight_table = list()
    #
    # nslist_table
    nslist_table = dict()
    #
    # option_table
    option_table = [
        { 'name':'parent_node_name',      'value':'n0'},
        { 'name':'rate_case',             'value':'iota_pos_rho_zero'},
        { 'name': 'zero_sum_child_rate',  'value':'iota'},
        { 'name':'quasi_fixed',           'value':'false'},
        { 'name':'max_num_iter_fixed',    'value':'50'},
        { 'name':'tolerance_fixed',       'value':'1e-8'},
        { 'name':'random_seed',           'value':str(random_seed)},
    ]
    # ----------------------------------------------------------------------
    # create database
    dismod_at.create_database(
        file_name,
        age_grid,
        time_grid,
        integrand_table,
        node_table,
        subgroup_table,
        weight_table,
        covariate_table,
        avgint_table,
        data_table,
        prior_table,
        smooth_table,
        nslist_table,
        rate_table,
        mulcov_table,
        option_table
    )
# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------
def main() :
    # -------------------------------------------------------------------------
    # wrok_dir
    work_dir = 'build/example'
    distutils.dir_util.mkpath(work_dir)
    os.chdir(work_dir)
    #
    # Create root_node.db
    root_node_database  = 'root_node.db'
    root_node_db(root_node_database)
    #
    # all_cov_reference
    all_cov_reference = dict()
    for node_name in [ 'n0', 'n1', 'n2', 'n3', 'n4', 'n5', 'n6' ] :
        all_cov_reference[node_name] = dict()
    #
    # Create all_node.db
    all_node_database = 'all_node.db'
    all_option        = { 'max_fit' : max_fit_option }
    at_cascade.create_all_node_db(
        all_node_database   = all_node_database,
        root_node_database  = root_node_database,
        all_cov_reference   = all_cov_reference,
        all_option          = all_option,
        fit_goal_set        = fit_goal_set
    )
    #
    # node_table
    new        = False
    connection = dismod_at.create_connection(root_node_database, new)
    node_table = dismod_at.get_table_dict(connection, 'node')
    connection.close()
    #
    # fit_node_dir
    fit_node_dir = 'n0'
    if os.path.exists(fit_node_dir) :
        # rmtree is very dangerous so make sure fit_node_dir is as expected
        os.chdir('../..')
        assert work_dir == 'build/example'
        shutil.rmtree(work_dir + '/' + fit_node_dir)
        os.chdir(work_dir)
    os.makedirs(fit_node_dir )
    #
    # fit_node_database
    fit_node_database =  fit_node_dir + '/dismod.db'
    shutil.copyfile(root_node_database, fit_node_database)
    #
    # cascade starting at root node
    at_cascade.cascade_fit_node(
        all_node_database, fit_node_database, node_table
    )
    #
    # check leaf node results
    leaf_dir_list = [ 'n0/n1/n3', 'n0/n1/n4', 'n0/n2/n5', 'n0/n2/n6' ]
    for leaf_dir in leaf_dir_list :
        leaf_database = leaf_dir + '/dismod.db'
        at_cascade.check_cascade_fit(
            rate_true, all_node_database, leaf_database
        )
    #
    # check hold outs for all nodes
    for fit_dir in leaf_dir_list + [ 'n0', 'n0/n1', 'n0/n2' ] :
        #
        # data_subset
        fit_database = fit_dir + '/dismod.db'
        new          = False
        connection   = dismod_at.create_connection(fit_database, new)
        data_subset  = dismod_at.get_table_dict(connection, 'data_subset')
        if fit_dir == 'n0' :
            assert len(data_subset) == 4 * max_fit_option
        elif fit_dir in [ 'n0/n1', 'n0/n2' ] :
            assert len(data_subset) == 2 * max_fit_option
        else :
            assert fit_dir in leaf_dir_list
            assert len(data_subset) == max_fit_option
        #
        # count_hold_out
        count_hold_out = 0
        for row in data_subset :
            assert row['hold_out'] in [ 0, 1]
            count_hold_out += row['hold_out']
        #
        assert len(data_subset) - count_hold_out == max_fit_option
#
main()
print('max_fit_option: OK')
sys.exit(0)
# END source code