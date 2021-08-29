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
{xsrst_begin_parent one_at_function}
{xsrst_spell
    avg
    dage
    dtime
}

Example That Directly Measures One Age Time Function
####################################################
For this example everything is constant in time so the
functions below do not depend on time.

Nodes
*****
The following is a diagram of the node tree for this example.
The :ref:`glossary.root_node` is n0,
the :ref:`glossary.fit_goal_set` is {n3, n4, n2},
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
:ref:`glossary.iota`; i.e.,
we choose iota to represent the function that we are estimating.
(We could have used
:ref:`glossary.rho` or :ref:`glossary.chi` but not :ref:`glossary.omega`
for this purpose.)
We use *iota_n(a, n, I)* to denote the value for iota
as a function of age *a* node number *n* and income *I*.

Covariate
*********
The only covariate for this example is income.
Its reference value is the average income corresponding
to the :ref:`glossary.fit_node`.

r_n
===
We use *r_n* for the reference value of income at node *n*.
The code below sets this reference using the name avg_income:
{xsrst_file
    # BEGIN avg_income
    # END avg_income
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
For each node, there is a random effect on iota that is constant
in age and time. Note that the leaf nodes have random effect for the node
above them as well as their own random effect.

s_n
===
We use *s_n* to denote the sum of the random effects for node *n*.
The code below sets this sum using the name sum_random:
{xsrst_file
    # BEGIN sum_random
    # END sum_random
}

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

iota_true(a, n, I)
==================
This is the true value for iota in node *n* at age *a* and income *I*:
{xsrst_file
    # BEGIN iota_true
    # END iota_true
}


y_i
===
The only simulated integrand for this example is :ref:`glossary.sincidence`
which is a direct measurement of iota.
(If we had used a different rate to represent the function we are estimating,
we would use the corresponding direct measurement of that rate.)
This data is simulated without any noise; i.e.,
the i-th measurement is simulated as
*y_i = iota_true(a_i, n_i, I_i)*
where *a_i* is the age,
*n_i* is the node,
and *I_i* is the income for the i-th measurement.
The data is modeled as having noise even though there is no simulated noise.

n_i
===
Data is only simulated for the leaf nodes; i.e.,
each *n_i* is in the set { n3, n4, n5, n6 }.
Since the data does not have any nose, the data residuals are a measure
of how good the fit is for the nodes in the fit_goal_set.

a_i
===
For each leaf node, data is generated on the following *age_grid*:
{xsrst_file
    # BEGIN age_grid
    # END age_grid
}

I_i
===
For each leaf node and each age in *age_grid*,
data is generated for the following *income_grid*:
{xsrst_file
    # BEGIN income_grid
    # END income_grid
}
Note that the check of the fit for the nodes in the fit_goal_set
expects much more accuracy when the income grid is not chosen randomly.

Parent Smoothing
****************
This is the iota smoothing used for the fit_node.
This smoothing uses the *age_gird* and one time point.
There are no :ref:`glossary.dtime`
priors because there is only one time point.

Value Prior
===========
The following is the value prior used for the fit_node
{xsrst_file
    # BEIGN parent_value_prior
    # END parent_value_prior
}
The mean and standard deviation are only used for the root_node.
The :ref:`create_child_node_db<create_child_node_db>`
routine replaces them for other nodes.

Dage Prior
==========
The prior for age differences is log Gaussian with mean zero,
standard deviation 3.0, and :ref:`glossary.eta` equal to
*iota_true(50)/1000* .

Child Smoothing
***************
This is the smoothing used in the model for the iota
random effect for each child of the fit_node.
The smoothing only has one age and one time point; i.e.,
the corresponding function is constant in age and time.
There are no :ref:`glossary.dage` or dtime
priors because there is only one age and one time point.

Value Prior
===========
This value prior is gaussian with mean zero and standard deviation 10.0.
There are no upper or lower limits in this prior.

Alpha Smoothing
***************
This is the smoothing used in the model for *alpha*.
There are no dage or dtime priors because there is only one
age and one time point in this smoothing.

Value Prior
===========
This value prior is uniform with lower limit *-10\*|alpha_true|*,
upper limit *+10\*|alpha_true|* and mean zero.
(The mean is used to initialize the optimization.)

Checking The Fit
****************
The results of the fit are in the
:ref:`cascade_fit_node.dismod_db.predict` and
:ref:`cascade_fit_node.dismod_db.c_predict_fit_var`
tables of the fit_node_database corresponding to each node.
The ``check_fit`` routine uses these tables to check that fit
against the truth.

{xsrst_end one_at_function}
------------------------------------------------------------------------------
{xsrst_begin one_at_function_py}

one_at_function: Python Source Code
###################################

{xsrst_file
    BEGIN one_at_function source code
    END one_at_function source code
}

{xsrst_end one_at_function_py}
'''
# BEGIN one_at_function source code
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
fit_goal_set = { 'n3', 'n4', 'n2' }
# END fit_goal_set
#
# BEGIN random_seed
random_seed = 0
if random_seed == 0 :
    random_seed = int( time.time() )
random.seed(random_seed)
print('one_at_function: random_seed = ', random_seed)
# END random_seed
#
# BEGIN alpha_true
alpha_true = - 0.2
# END alpha_true
#
# BEGIN avg_income
avg_income       = { 'n3':1.0, 'n4':2.0, 'n5':3.0, 'n6':4.0 }
avg_income['n2'] = ( avg_income['n5'] + avg_income['n6'] ) / 2.0
avg_income['n1'] = ( avg_income['n3'] + avg_income['n4'] ) / 2.0
avg_income['n0'] = ( avg_income['n1'] + avg_income['n2'] ) / 2.0
# END avg_income
#
# BEGIN sum_random_effect
size_level1      = 0.2
size_level2      = 0.2
sum_random       = { 'n0': 0.0, 'n1': size_level1, 'n2': -size_level1 }
sum_random['n3'] = sum_random['n1'] + size_level2;
sum_random['n4'] = sum_random['n1'] - size_level2;
sum_random['n5'] = sum_random['n2'] + size_level2;
sum_random['n6'] = sum_random['n2'] - size_level2;
# END sum_random_effect
#
# BEGIN age_grid
age_grid = [0.0, 20.0, 40.0, 60.0, 80.0, 100.0 ]
# END age_grid
#
# BEGIN income_grid
random_income = False
income_grid   = dict()
for node in [ 'n3', 'n4', 'n5', 'n6' ] :
    max_income  = 2.0 * avg_income[node]
    if random_income :
        n_income_grid = 10
        income_grid[node] = \
            [ random.uniform(0.0, max_income) for j in range(n_income_grid) ]
        income_grid[node] = sorted( income_grid[node] )
    else :
        n_income_grid = 3
        d_income_grid = max_income / (n_income_grid - 1)
        income_grid[node] = [ j * d_income_grid for j in range(n_income_grid) ]
# END income_grid
# ----------------------------------------------------------------------------
# functions
# ----------------------------------------------------------------------------
# BEGIN iota_true
def iota_true(a, n = 'n0', I = avg_income['n0'] ) :
    s_n = sum_random[n]
    r_0 = avg_income['n0']
    return (1 + a / 100) * 1e-2 * exp( s_n + alpha_true * ( I - r_0 ) )
# END iota_true
# ----------------------------------------------------------------------------
def root_node_db(file_name) :
    #
    # prior_table
    prior_table = list()
    prior_table.append(
        # BEIGN parent_value_prior
        {   'name':    'parent_value_prior',
            'density': 'gaussian',
            'lower':   iota_true(0) / 10.0,
            'upper':   iota_true(100) * 10.0,
            'mean':    iota_true(50),
            'std':     iota_true(50) * 10.0,
            'eta':     iota_true(50) * 1e-3
        }
        # END parent_value_prior
    )
    prior_table.append(
        { # prior_iota_dage
            'name':    'prior_iota_dage',
            'density': 'log_gaussian',
            'mean':    0.0,
            'std':     3.0,
            'eta':     iota_true(0) * 1e-3,
        }
    )
    prior_table.append(
        { # prior_child_value
            'name':    'prior_child_value',
            'density': 'gaussian',
            'mean':    0.0,
            'std':     10.0,
        }
    )
    prior_table.append(
        { # prior_alpha_n0_value
            'name':    'prior_alpha_n0_value',
            'density': 'gaussian',
            'lower':   - 10 * abs(alpha_true),
            'upper':   + 10 * abs(alpha_true),
            'std':     + 10 * abs(alpha_true),
            'mean':    0.0,
        }
    )
    #
    # smooth_table
    smooth_table = list()
    #
    # smooth_iota_n0
    fun = lambda a, t : ('parent_value_prior', 'prior_iota_dage', None)
    smooth_table.append({
        'name':       'smooth_iota_n0',
        'age_id':     range( len(age_grid) ),
        'time_id':    [0],
        'fun':        fun,
    })
    #
    # smooth_child
    fun = lambda a, t : ('prior_child_value', None, None)
    smooth_table.append({
        'name':       'smooth_child',
        'age_id':     [0],
        'time_id':    [0],
        'fun':        fun,
    })
    #
    # smooth_alpha_n0
    fun = lambda a, t : ('prior_alpha_n0_value', None, None)
    smooth_table.append({
        'name':       'smooth_alpha_n0',
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
        'parent_smooth':  'smooth_iota_n0',
        'child_smooth':   'smooth_child' ,
    } ]
    #
    # covariate_table
    covariate_table = [ { 'name':'income',   'reference':avg_income['n0'] } ]
    #
    # mulcov_table
    mulcov_table = [ {
        # alpha
        'covariate':  'income',
        'type':       'rate_value',
        'effected':   'iota',
        'group':      'world',
        'smooth':     'smooth_alpha_n0',
    } ]
    #
    # subgroup_table
    subgroup_table = [ {'subgroup': 'world', 'group':'world'} ]
    #
    # integrand_table
    integrand_table = [ {'name':'Sincidence'}, {'name':'mulcov_0'} ]
    #
    # avgint_table
    avgint_table = list()
    row = {
        'node':         'n0',
        'subgroup':     'world',
        'weight':       '',
        'time_lower':   2000.0,
        'time_upper':   2000.0,
        'income':       None,
        'integrand':    'Sincidence',
    }
    for age in age_grid :
        row['age_lower'] = age
        row['age_upper'] = age
        avgint_table.append( copy.copy(row) )
    #
    # data_table
    data_table  = list()
    leaf_set    = { 'n3', 'n4', 'n5', 'n6' }
    for (age_id, age) in enumerate( age_grid ) :
        row = {
            'subgroup':     'world',
            'weight':       '',
            'time_lower':   2000.0,
            'time_upper':   2000.0,
            'integrand':    'Sincidence',
            'density':      'gaussian',
            'hold_out':     False,
        }
        for node in leaf_set :
            for income in income_grid[node] :
                meas_value        = iota_true(age, node, income)
                row['node']       = node
                row['meas_value'] = meas_value
                row['age_lower']  = age
                row['age_upper']  = age
                row['income']     = income
                # The model for the measurement noise is small so a few
                # data points act like lots of real data points.
                # The actual measruement noise is zero.
                row['meas_std']   = meas_value / 10.0
                data_table.append( copy.copy(row) )
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
def check_fit(goal_database) :
    #
    # connection
    new        = False
    connection = dismod_at.create_connection(goal_database, new)
    #
    # goal_name
    path_list = goal_database.split('/')
    assert len(path_list) >= 2
    assert path_list[-1] == 'dismod.db'
    goal_name = path_list[-2]
    #
    # table
    table = dict()
    for name in [
        'avgint',
        'age',
        'integrand',
        'node',
        'predict',
        'c_predict_fit_var',
    ] :
        table[name] = dismod_at.get_table_dict(connection, name)
    #
    n_avgint  = len(table['avgint'])
    n_predict = len(table['predict'])
    n_sample  = int( n_predict / n_avgint )
    #
    assert n_avgint == len( table['c_predict_fit_var'] )
    assert n_predict % n_avgint == 0
    #
    # sumsq
    sumsq = n_avgint * [0.0]
    for (predict_id, predict_row) in enumerate( table['predict'] ) :
        # avgint_row
        avgint_id  = predict_row['avgint_id']
        avgint_row = table['avgint'][avgint_id]
        assert avgint_id == predict_id % n_avgint
        #
        # sample_index
        sample_index = predict_row['sample_index']
        assert sample_index * n_avgint + avgint_id == predict_id
        #
        # integrand_name
        integrand_id = avgint_row['integrand_id']
        integrand_name = table['integrand'][integrand_id]['integrand_name']
        assert integrand_name == 'Sincidence'
        #
        # node_name
        node_id   = avgint_row['node_id']
        node_name = table['node'][node_id]['node_name']
        assert node_name == goal_name
        #
        # age
        age = avgint_row['age_lower']
        assert age == avgint_row['age_upper']
        #
        # avg_integrand
        avg_integrand = table['c_predict_fit_var'][avgint_id]['avg_integrand']
        #
        # sample_value
        sample_value = predict_row['avg_integrand']
        #
        # sumsq
        sumsq[avgint_id] += (sample_value - avg_integrand)**2
    #
    # income
    income  = avg_income[goal_name]
    #
    # (avgint_id, row)
    for (avgint_id, row) in enumerate(table['c_predict_fit_var']) :
        assert avgint_id == row['avgint_id']
        #
        # avgint_row
        avgint_row = table['avgint'][avgint_id]
        #
        # age
        age = avgint_row['age_lower']
        #
        # avg_integrand
        avg_integrand = row['avg_integrand']
        #
        # sample_std
        sample_std = math.sqrt( sumsq[avgint_id] )
        #
        # check_value
        check_value = iota_true(age, goal_name, income)
        #
        rel_error   = 1.0 - avg_integrand / check_value
        #
        # check the fit
        # print(age, rel_error, check_value - avg_integrand, sample_std)
        if random_income :
            assert abs(rel_error) < 1e-2
        else :
            assert abs(rel_error) < 1e-3
        assert abs(avg_integrand - check_value) < 2.0 * sample_std
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
    covariate_name      = 'income'
    for node_name in [ 'n0', 'n1', 'n2', 'n3', 'n4', 'n5', 'n6' ] :
        all_cov_reference[node_name] = {
            covariate_name : avg_income[node_name]
        }
    #
    # Create all_node.db
    all_node_database = 'all_node.db'
    at_cascade.create_all_node_db(
        all_node_database   = all_node_database   ,
        root_node_database  = root_node_database  ,
        all_cov_reference   = all_cov_reference ,
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
    # check results
    for goal_dir in [ 'n0/n1/n3', 'n0/n1/n4', 'n0/n2' ] :
        goal_database = goal_dir + '/dismod.db'
        check_fit(goal_database)
    #
    # check that fits were not run for n5 and n6
    for not_fit_dir in [ 'n0/n2/n5', 'n0/n2/n6' ] :
        assert not os.path.exists( not_fit_dir )
#
main()
print('one_at_function: OK')
sys.exit(0)
# END one_at_function source code
