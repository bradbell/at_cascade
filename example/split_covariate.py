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
{xsrst_begin_parent split_covariate}
{xsrst_spell
    dage
    dtime
}

Example Using split_reference Table
###################################
This example splits the analysis by sex.
To simplify the example everything is constant w.r.t. age and time.

Nodes
*****
The following is a diagram of the node tree for this example.
The :ref:`glossary.root_node` is n0,
the :ref:`glossary.fit_goal_set`
and the leaf nodes are {n3, n4, n5, n6}::

                n0
          /-----/\-----\
        n1              n2
       /  \            /  \
     n3    n4        n5    n6

fit_goal_set
============
{xsrst_file
    # BEGIN fit_goal_set
    # END fit_goal_set
}

Rates
*****
The only non-zero dismod_at rates for this example are
:ref:`glossary.iota`.and :ref:`glossary.omega`.

Splitting Covariate
*******************
This cascade is set up to split by the sex covariate at level zero:
{xsrst_file
    # BEGIN all_option_table
    # END all_option_table
}
The :ref:`split_reference_table` for this example is:
{xsrst_file
    # BEGIN split_reference_table
    # END split_reference_table
}
The :ref:`node_split_table` for this example is
{xsrst_file
    # BEGIN node_split_table
    # END node_split_table
}
Note that we have used node_name (instead of node_id) here and let
:ref:`create_all_node_db` do the conversion to node_id.
The cascade computation tree is::

                /-------------n0-------------\
          /---female---\                /----male----\
        n1              n2            n1              n2
       /  \            /  \          /  \            /  \
     n3    n4        n5    n6      n3    n4        n5    n6

The sex reference value for the root node (n0) corresponds to both sexes:
{xsrst_file
    # BEGIN root_split_reference_id
    # END root_split_reference_id
}

Covariate
*********
There are two covariates for this example, sex and income.
The reference value for income depends on both the node and sex;
see :ref:`create_all_node_db.all_cov_reference`:
{xsrst_file
    # BEGIN all_cov_reference
    # END all_cov_reference
}

alpha
=====
We use *alpha*
for the :ref:`glossary.rate_value` covariate multiplier
that multipliers income.
This multiplier affects the value of iota.
The true value for *alpha* (used which simulating the data) is
{xsrst_file
    # BEGIN alpha_true
    # END alpha_true
}

Random Effects
**************
There are no random effect for this example.

Simulated Data
**************

mtall
=====
The ref:`all_mtall` data for this example is simulated as equal to
the true value for omega (see rate_true directly below) and there is
no :ref:`all_mtspecific` data for this example.

rate_true(rate, a, t, n, c)
===========================
For *rate* equal to iota or omega,
this is the true value for *rate*
in node *n* at age *a*, time *t*, and covariate values *c=[sex,income]*.
The covariate values are a list in the same order as the covariate table.
The values *a* and *t* are not used by this function for this example.
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
*y_i = rate_true('iota', None, None, n, [sex, I_i])*
where *n* is the node, *sex* is the sex covariate value, and
*I_i* is the income for the i-th measurement.
The data is modeled as having noise even though there is no simulated noise.

Cases Simulated
===============
Data is simulated for the leaf nodes for female, male sexes; i.e.,
each *n_i* is in the set { n3, n4, n5, n6 } and the female, male sexes.
Since the data does not have any nose, the data residuals are a measure
of how good the fit is for the nodes in the fit_goal_set below the female
and male sexes.

Parent Rate Smoothing
*********************
This is the iota smoothing used for the fit_node.
There are no :ref:`glossary.dage` or :ref:`glossary.dtime`
priors because there is only one age and one time point in the smoothing grid.

Value Prior
===========
The following is the value prior used for the root_node
{xsrst_file
    # BEGIN parent_value_prior
    # END parent_value_prior
}
The mean and standard deviation are only used for the root_node.
The :ref:`create_shift_db<create_shift_db>`
routine replaces them for other nodes.

Alpha Smoothing
***************
This is the smoothing used for *alpha* which multiplies the income covariate.
There is only one age and one time point in this smoothing
so it does not have dage or dtime priors.

Value Prior
===========
The following is the value prior used for this smoothing:
{xsrst_file
    # BEGIN alpha_value_prior
    # END alpha_value_prior
}
The mean and standard deviation are only used for the root_node.
The create_shift_db
routine replaces them for other nodes.

Checking The Fit
****************
The results of the fit are in the
:ref:`cascade_root_node.output_dismod_db.c_predict_sample` and
:ref:`cascade_root_node.output_dismod_db.c_predict_fit_var`
tables of the fit_node_database corresponding to each node.
The :ref:`check_cascade_fit<check_cascade_fit>`
routine uses these tables to check that fit against the truth.

{xsrst_end split_covariate}
------------------------------------------------------------------------------
{xsrst_begin split_covariate_py}

split_covariate: Python Source Code
###################################

{xsrst_file
    BEGIN split_covariate source code
    END split_covariate source code
}

{xsrst_end split_covariate_py}
'''
# BEGIN split_covariate source code
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
# BEGIN all_option_table
all_option            = {
    'results_dir':                'build/example',
    'root_node_name':             'n0',
    'root_split_reference_name':  'both',
    'split_covariate_name':       'sex',
    'shift_prior_std_factor':      1e3,
}
# END all_option_table
#
#
# BEGIN split_reference_table
split_reference_table = [
    {'split_reference_name': 'female', 'split_reference_value': 1.0},
    {'split_reference_name': 'both',   'split_reference_value': 2.0},
    {'split_reference_name': 'male',   'split_reference_value': 3.0},
]
split_reference_list = list()
for row in split_reference_table :
    split_reference_list.append( row['split_reference_value'] )
# END split_reference_table
# BEGIN node_split_table
node_split_table = [ { 'node_name' :   'n0'} ]
# END node_split_table
#
# BEGIN root_split_reference_id
root_split_reference_id = 1
assert  \
split_reference_table[root_split_reference_id]['split_reference_name']=='both'

# END root_split_reference_id
#
# BEGIN all_cov_reference
all_cov_reference = dict()
for node_id in range(7) :
    node_name = 'n' + str(node_id)
    all_cov_reference[node_name] = {
        'income' : [ 1.0 - node_id / 10.0, 1.0, 1.0 + node_id / 10.0 ]
    }
# END all_cov_reference
#
# BEGIN alpha_true
alpha_true = - 0.2
# END alpha_true
# ----------------------------------------------------------------------------
# functions
# ----------------------------------------------------------------------------
# BEGIN rate_true
def rate_true(rate, a, t, n, c) :
    # true_iota
    true_iota = {
        'n3' : 1e-2,
        'n4' : 2e-2,
        'n5' : 3e-2,
        'n6' : 4e-2
    }
    true_iota['n1'] = (true_iota['n3'] + true_iota['n4']) / 2.9
    true_iota['n2'] = (true_iota['n5'] + true_iota['n6']) / 2.9
    true_iota['n0'] = (true_iota['n1'] + true_iota['n2']) / 2.9
    #
    # effect
    sex    = c[0]
    income = c[1]
    #
    # split_reference_id
    split_reference_id = None
    for (row_id, row) in enumerate(split_reference_table) :
        if row['split_reference_value'] == sex :
            split_reference_id = row_id
    #
    r_income = all_cov_reference[n]['income'][split_reference_id]
    effect   = alpha_true * ( income - r_income )
    #
    if rate == 'iota' :
        return true_iota[n] * exp(effect)
    if rate == 'omega' :
        return 2.0 * true_iota[n] * exp(effect)
    return 0.0
# END rate_true
# ----------------------------------------------------------------------------
def root_node_db(file_name) :
    #
    # iota_n0
    sex       = split_reference_list[root_split_reference_id]
    income    = all_cov_reference['n0']['income'][root_split_reference_id]
    c         = [ sex, income ]
    iota_n0   = rate_true('iota', None, None, 'n0', c)
    # END iota_50
    #
    # prior_table
    prior_table = list()
    prior_table.append(
        # BEGIN parent_value_prior
        {   'name':    'parent_value_prior',
            'density': 'gaussian',
            'lower':   iota_n0 / 10.0,
            'upper':   iota_n0 * 10.0,
            'mean':    iota_n0 ,
            'std':     iota_n0 * 10.0,
            'eta':     iota_n0 * 1e-3
        }
        # END parent_value_prior
    )
    prior_table.append(
        # BEGIN alpha_value_prior
        {   'name':    'alpha_value_prior',
            'density': 'gaussian',
            'lower':   - 10 * abs(alpha_true),
            'upper':   + 10 * abs(alpha_true),
            'std':     + 10 * abs(alpha_true),
            'mean':    0.0,
        }
        # END alpha_value_prior
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
    # alpha_smooth
    fun = lambda a, t : ('alpha_value_prior', None, None)
    smooth_table.append({
        'name':       'alpha_smooth',
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
        'child_smooth':   None ,
    } ]
    #
    # covariate_table
    covariate_table = list()
    sex    = split_reference_list[root_split_reference_id]
    income =  all_cov_reference['n0']['income'][root_split_reference_id]
    covariate_table.append(
        { 'name': 'sex',      'reference': sex, 'max_difference': 1.1 }
    )
    covariate_table.append( { 'name':  'income',  'reference': income } )
    #
    # mulcov_table
    mulcov_table = [ {
        # alpha
        'covariate':  'income',
        'type':       'rate_value',
        'effected':   'iota',
        'group':      'world',
        'smooth':     'alpha_smooth',
    } ]
    #
    # subgroup_table
    subgroup_table = [ {'subgroup': 'world', 'group':'world'} ]
    #
    # integrand_table
    integrand_table = [ {'name':'Sincidence'} ]
    for mulcov_id in range( len(mulcov_table) ) :
        integrand_table.append( { 'name': f'mulcov_{mulcov_id}' } )
    #
    # avgint_table
    avgint_table = list()
    row = {
        'node':         'n0',
        'subgroup':     'world',
        'weight':       '',
        'time_lower':   2000.0,
        'time_upper':   2000.0,
        'age_lower':    50.0,
        'age_upper':    50.0,
        'sex':          None,
        'income':       None,
        'integrand':    'Sincidence',
    }
    avgint_table.append( copy.copy(row) )
    #
    # data_table
    data_table  = list()
    leaf_set    = { 'n3', 'n4', 'n5', 'n6' }
    row = {
        'subgroup':     'world',
        'weight':       '',
        'time_lower':   2000.0,
        'time_upper':   2000.0,
        'age_lower':      50.0,
        'age_upper':      50.0,
        'integrand':    'Sincidence',
        'density':      'gaussian',
        'hold_out':     False,
    }
    assert split_reference_table[0]['split_reference_name'] == 'female'
    assert split_reference_table[2]['split_reference_name'] == 'male'
    for split_reference_id in [ 0, 2 ] :
        for node in leaf_set :
            sex      = split_reference_list[split_reference_id]
            r_income = all_cov_reference[node]['income'][split_reference_id]
            for factor in [ 0.5, 1.0, 2.0 ] :
                income = factor * r_income
                c      = [sex, income]
                meas_value = rate_true('iota', None, None, node, c)
                row['node']       = node
                row['meas_value'] = meas_value
                row['sex']        = sex
                row['income']     = income
                row['meas_std']   = meas_value / 10.0
                data_table.append( copy.copy(row) )
    #
    # age_grid
    age_grid = [ 0.0, 100.0 ]
    #
    # time_grid
    time_grid = [ 1980.0, 2020.0 ]
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
    # results_dir
    results_dir = all_option['results_dir']
    distutils.dir_util.mkpath(results_dir)
    #
    # Create root_node.db
    root_node_database  = f'{results_dir}/root_node.db'
    root_node_db(root_node_database)
    #
    # omega_grid
    new          = False
    connection   = dismod_at.create_connection(root_node_database, new)
    age_table    = dismod_at.get_table_dict(connection, 'age')
    time_table   = dismod_at.get_table_dict(connection, 'time')
    age_id_list  = list( range( len(age_table) ) )
    time_id_list = list( range( len(age_table) ) )
    omega_grid   = { 'age': age_id_list, 'time' : time_id_list }
    #
    # n_split
    n_split  = len( split_reference_list )
    #
    # mtall_data
    mtall_data      = dict()
    for node_name in [ 'n0', 'n1', 'n2', 'n3', 'n4', 'n5', 'n6' ] :
        mtall_data[node_name] = list()
        for k in range(n_split) :
            mtall_data[node_name].append( list() )
            for age_id in omega_grid['age'] :
                for time_id in omega_grid['time'] :
                    age    = age_table[age_id]['age']
                    time   = time_table[time_id]['time']
                    sex    = split_reference_list[k]
                    income = all_cov_reference[node_name]['income'][k]
                    cov    = [ sex, income ]
                    omega  = rate_true('omega', None, None, node_name, cov)
                    mtall_data[node_name][k].append( omega )
    #
    # Create all_node.db
    all_node_database = f'{results_dir}/all_node.db'
    at_cascade.create_all_node_db(
        all_node_database      = all_node_database,
        root_node_database     = root_node_database,
        all_cov_reference      = all_cov_reference,
        split_reference_table  = split_reference_table,
        node_split_table       = node_split_table,
        all_option             = all_option,
        omega_grid             = omega_grid,
        mtall_data             = mtall_data,
    )
    #
    # fit_node_dir
    fit_node_dir = f'{results_dir}/n0'
    if os.path.exists(fit_node_dir) :
        # rmtree is very dangerous so make sure fit_node_dir is as expected
        assert fit_node_dir == 'build/example/n0'
        shutil.rmtree( fit_node_dir )
    os.makedirs(fit_node_dir )
    #
    # fit_node_database
    fit_node_database =  fit_node_dir + '/dismod.db'
    shutil.copyfile(root_node_database, fit_node_database)
    #
    # cascade starting at root node
    at_cascade.cascade_root_node(
        all_node_database  = all_node_database ,
        root_node_database = fit_node_database ,
        fit_goal_set       = fit_goal_set      ,
    )
    #
    # check results
    for sex in [ 'male', 'female' ] :
        for subdir in [ 'n1/n3', 'n1/n4', 'n2/n5', 'n2/n6' ] :
            goal_database = f'{results_dir}/n0/{sex}/{subdir}/dismod.db'
            at_cascade.check_cascade_fit(
                rate_true          = rate_true,
                all_node_database  = all_node_database,
                fit_node_database  = goal_database,
                relative_tolerance = 1e-5,
            )
    #
#
main()
print('split_covariate: OK')
sys.exit(0)
# END split_covariate source code
