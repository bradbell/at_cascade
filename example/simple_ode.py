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
{xsrst_begin_parent simple_ode}
{xsrst_spell
    avg
    dtime
    dage
}

Simple Case Where The ODE is Used to Model The Data
###################################################

Under Construction
******************
This test is not yet passing.

Nodes
*****
The following is a diagram of the node tree for this example::

                n0
          /-----/\-----\
        n1              n2
       /  \            /  \
     n3    n4        n5    n6

For this example the :ref:`glossary.root_node` is n0 and
{ n3, n4, n5, n6 } is the :ref:`glossary.leaf_node_set`.

Rates
*****
The only non-zero dismod_at rates for this example are
:ref:`glossary.iota` and :ref:`glossary.omega`.
We use :math:`\iota(a, n, I)` and *iota_n* to denote the value for *iota*
as a function of age *a*, node number *n*, and income *I*.
We use :math:`\omega(a, n)` and *iota_n* to denote the value for *omega*
as a function of age *a* and node number *n*.


Covariate
*********
The only covariate for this example is *income*.
Its reference value is the average income corresponding
to the :ref:`glossary.fit_node`.

r_n
===
We use *r_n* for the reference value of *income* at node *n*.
The code below sets this reference using the name avg_income:
{xsrst_file
    # BEGIN avg_income
    # END avg_income
}

alpha
=====
We use *alpha* and :math:`\alpha`
for the :ref:`glossary.rate_value` covariate multiplier
that multipliers *income*.
This multiplier affects the value of *iota*.
The true value for *alpha* (used which simulating the data) is
{xsrst_file
    # BEGIN alpha_true
    # END alpha_true
}


Random Effects
**************
For each node, there is a random effect on *iota* that is constant
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
For this example everything is constant in time so the
functions below do not depend on time.

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
This is the true value for *iota* in node *n* at age *a* and income *I*:
{xsrst_file
    # BEGIN iota_true
    # END iota_true
}

omega_true(a, n)
================
This is the true value for *omega* in node *n* and age *a*:
{xsrst_file
    # BEGIN omega_true
    # END omega_true
}


y_i
===
The only simulated integrand for this example is :ref:`glossary.prevalence`.
This data is simulated with any noise; i.e.,
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
of how good the fit is for the leaf nodes.

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
Note that the check of the fit for the leaf nodes expects much more accuracy
when the income grid is not chosen randomly.

Parent Smoothing
****************

omega
=====
The parent smoothing constrains *omega* to be equal to
:math:`\omega(a, n)` where  *a* is each value in the age grid and
*n* is the current node.

iota
====
This is the smoothing used in the *fit_node* model for *iota*.
(The :ref:`glossary.fit_node` is the parent node in dismod_at notation.)
This smoothing uses the *age_gird* and one time point.
There are no dtime priors because there is only one time point.

Value Prior
-----------
The *fit_node* value prior is uniform with lower limit
*iota_true(0)/10* and upper limit *iota_true(100)\*10*.
The mean is *iota_true(50)*
(which is used to initialize the optimization.)

Dage Prior
-----------
The prior for age differences is log Gaussian with mean zero,
standard deviation 3.0, and :ref:`glossary.eta` equal to
*iota_true(50)/1000* .

Child Smoothing
***************

omega
=====
The child smoothing constrains *omega* to be equal to
:math:`\omega(a, n)` where  *a* is each value in the age grid and
*n* is the current node.

iota
====
This is the smoothing used in the model for the *iota*
random effect for each child of the *fit_node*.
The smoothing only has one age and one time point; i.e.,
the corresponding function is constant in age and time.
There are no dage or dtime priors because there is only one
age and one time point.

Value Prior
-----------
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

{xsrst_end simple_ode}
------------------------------------------------------------------------------
{xsrst_begin simple_ode_py}

simple_ode: Python Source Code
##############################

{xsrst_file
    BEGIN simple_ode source code
    END simple_ode source code
}

{xsrst_end simple_ode_py}
'''
# BEGIN simple_ode source code
# ----------------------------------------------------------------------------
# imports
# ----------------------------------------------------------------------------
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
# global variables
# -----------------------------------------------------------------------------
# BEGIN random_seed
# random_seed = 1629371067
random_seed = 0
if random_seed == 0 :
    random_seed = int( time.time() )
    random.seed(random_seed)
print('simple_ode: random_seed = ', random_seed)
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
random_income = True
number_income = 3
income_grid   = dict()
for node in [ 'n3', 'n4', 'n5', 'n6' ] :
    max_income  = 2.0 * avg_income[node]
    income_grid[node] = list()
    for j in range(number_income) :
        if random_income :
            income = random.uniform(0.0, max_income)
        else :
            income = j * max_income / (number_income - 1)
        income_grid[node].append(income)
    income_grid[node] = sorted( income_grid[node] )
# END income_grid
# ----------------------------------------------------------------------------
# functions
# ----------------------------------------------------------------------------
# BEGIN iota_true
def iota_true(a, n = 'n0', I = avg_income['n0'] ) :
    s_n = sum_random[n]
    r_0 = avg_income['n0']
    return (1 + a / 100) * 1e-3 * exp( s_n + alpha_true * ( I - r_0 ) )
# END iota_true
# ----------------------------------------------------------------------------
# BEGIN omega_true
def omega_true(a, n = 'n0' ) :
    r_0 = avg_income['n0']
    r_n = avg_income[n]
    return (1 + a / 100) * 1e-2 * exp( alpha_true * ( r_n - r_0 ) )
# END omega_true
# ----------------------------------------------------------------------------
def average_integrand(integrand_name, age, node_name, income) :
    def iota(a, t) :
        return iota_true(a, node_name, income)
    def omega(a, t) :
        return omega_true(a, node_name)
    rate           = { 'iota' : iota  ,             'omega' : omega }
    grid           = { 'age' : age_grid ,           'time' : [2000.0] }
    noise          = { 'density_name' : 'gaussian', 'meas_std' : 0.0  }
    abs_tol        = 1e-5
    avg_integrand   = dismod_at.average_integrand(
        rate, integrand_name, grid,  abs_tol
    )
    return avg_integrand
# ----------------------------------------------------------------------------
def root_node_db(file_name) :
    #
    # prior_table
    prior_table = [
        {   # prior_iota_n0_value
            'name':    'prior_iota_n0_value',
            'density': 'uniform',
            'lower':   iota_true(0) / 10.0,
            'upper':   iota_true(100) * 10.0,
            'mean':    iota_true(50),
        },{ # prior_iota_dage
            'name':    'prior_iota_dage',
            'density': 'log_gaussian',
            'mean':    0.0,
            'std':     3.0,
            'eta':     iota_true(0) * 1e-3,
        },{ # prior_iota_child
            'name':    'prior_iota_child',
            'density': 'gaussian',
            'mean':    0.0,
            'std':     10.0,
        },{ # prior_alpha_n0
            'name':    'prior_alpha_n0',
            'density': 'uniform',
            'lower':   - 10 * abs(alpha_true),
            'upper':   + 10 * abs(alpha_true),
            'mean':    0.0,
        },
    ]
    #
    # smooth_table
    smooth_table = list()
    #
    # smooth_iota_n0_value
    fun = lambda a, t : ('prior_iota_n0_value', 'prior_iota_dage', None)
    smooth_table.append({
        'name':       'smooth_iota_n0_value',
        'age_id':     range( len(age_grid) ),
        'time_id':    [0],
        'fun':        fun,
    })
    #
    # smooth_iota_child
    fun = lambda a, t : ('prior_iota_child', None, None)
    smooth_table.append({
        'name':       'smooth_iota_child',
        'age_id':     [0],
        'time_id':    [0],
        'fun':        fun,
    })
    #
    # smooth_alpha_n0
    fun = lambda a, t : ('prior_alpha_n0', None, None)
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
        'parent_smooth':  'smooth_iota_n0_value',
        'child_smooth':   'smooth_iota_child' ,
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
    integrand_table = [
        {'name': 'Sincidence'},
        {'name': 'prevalence'},
        {'name': 'mulcov_0'}
    ]
    #
    # avgint_table
    avgint_table = list()
    #
    # data_table
    data_table     = list()
    leaf_node_set  = { 'n3', 'n4', 'n5', 'n6' }
    integrand_name = 'prevalence'
    row = {
        'subgroup':     'world',
        'weight':       '',
        'time_lower':   2000.0,
        'time_upper':   2000.0,
        'income':       None,
        'integrand':    'prevalence',
        'density':      'gaussian',
        'hold_out':     False,
    }
    for (age_id, age) in enumerate( age_grid ) :
        for node in leaf_node_set :
            for income in income_grid[node] :
                meas_value = average_integrand(
                    integrand_name, age, node, income
                )
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
def child_node_id_list(node_table, parent_node_id) :
    result = list()
    for (node_id, row) in enumerate(node_table) :
        if row['parent'] == parent_node_id :
            result.append(node_id)
    return result
# ----------------------------------------------------------------------------
def node_table_name2id(node_table, row_name) :
    for (node_id, row) in enumerate(node_table) :
        if row['node_name'] == row_name :
            return node_id
    assert False
# ----------------------------------------------------------------------------
def cascade_fit_node(all_node_database, fit_node_database, node_table) :
    #
    # fit_node_name
    path_list = fit_node_database.split('/')
    assert len(path_list) >= 2
    assert path_list[-1] == 'dismod.db'
    fit_node_name = path_list[-2]
    #
    # fit_node_id
    fit_node_id = node_table_name2id(node_table, fit_node_name)
    #
    # fit_node_dir
    fit_node_dir = fit_node_database[ : - len('dismod.db') - 1 ]
    #
    # add omega to model
    at_cascade.omega_constraint(all_node_database, fit_node_database)
    #
    # replace avgint table
    at_cascade.child_avgint_table(all_node_database, fit_node_database)
    #
    # init
    dismod_at.system_command_prc( [ 'dismod_at', fit_node_database, 'init' ] )
    #
    # fit
    dismod_at.system_command_prc(
        [ 'dismod_at', fit_node_database, 'fit', 'both' ]
    )
    #
    # sample
    dismod_at.system_command_prc(
        [ 'dismod_at', fit_node_database, 'sample', 'asymptotic', 'both', '20' ]
    )
    # predict fit_var
    dismod_at.system_command_prc(
        [ 'dismod_at', fit_node_database, 'predict', 'fit_var' ]
    )
    # move predict -> c_predict
    new        = False
    connection = dismod_at.create_connection(fit_node_database, new)
    command     = 'DROP TABLE IF EXISTS c_predict'
    dismod_at.sql_command(connection, command)
    command     = 'ALTER TABLE predict RENAME COLUMN '
    command    += 'predict_id TO c_predict_id'
    dismod_at.sql_command(connection, command)
    command     = 'ALTER TABLE predict RENAME TO c_predict'
    dismod_at.sql_command(connection, command)
    connection.close()
    #
    # predict sample
    dismod_at.system_command_prc(
        [ 'dismod_at', fit_node_database, 'predict', 'sample' ]
    )
    # db2csv
    dismod_at.system_command_prc(
        [ 'dismodat.py', fit_node_database, 'db2csv' ] )
    #
    # child_node_list
    child_node_list = child_node_id_list(node_table, fit_node_id)
    #
    # child_node_databases
    child_node_databases = dict()
    for node_id in child_node_list :
        node_name = node_table[node_id]['node_name']
        subdir    = fit_node_dir + '/' + node_name
        if not os.path.exists(subdir) :
            os.makedirs(subdir)
        child_node_databases[node_name] = subdir + '/dismod.db'
    #
    # create child node databases
    at_cascade.create_child_node_db(
        all_node_database,
        fit_node_database,
        child_node_databases
    )
    #
    # fit child node databases
    for node_name in child_node_databases :
        fit_node_database = child_node_databases[node_name]
        cascade_fit_node(all_node_database, fit_node_database, node_table)
# ----------------------------------------------------------------------------
def check_fit(leaf_node_database) :
    #
    # leaf_node_name
    path_list = leaf_node_database.split('/')
    assert len(path_list) >= 2
    assert path_list[-1] == 'dismod.db'
    leaf_node_name = path_list[-2]
    #
    # leaf_node_dir
    leaf_node_dir = leaf_node_database[ : - len('dismod.db') - 1 ]
    #
    # variable_csv
    fp     = open( leaf_node_dir + '/variable.csv' )
    reader = csv.DictReader(fp)
    variable_csv = list()
    for row in reader :
        variable_csv.append( row )
    #
    # check value of iota
    for row in variable_csv :
        if row['var_type'] == 'rate' :
            assert row['rate'] == 'iota'
            assert row['node'] == leaf_node_name
            assert row['fixed'] == 'true'
            income      = avg_income[leaf_node_name]
            age         = float(row['age'])
            fit_value   = float(row['fit_value'])
            sam_std     = float(row['sam_std'])
            check_value = iota_true(age, leaf_node_name, income)
            rel_error   = 1.0 - fit_value / check_value
            print(leaf_node_name, fit_value, check_value, rel_err)
            if random_income :
                assert abs(rel_error) < 1e-1
            else :
                assert abs(rel_error) < 1e-3
            assert abs(fit_value - check_value) < 2.0 * sam_std
        else :
            assert row['var_type'] == 'mulcov_rate_value'
# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------
def main() :
    # -------------------------------------------------------------------------
    # change into the build/example directory
    distutils.dir_util.mkpath('build/example')
    os.chdir('build/example')
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
    # omega_grid
    omega_grid = dict()
    omega_grid['age']  = range( len(age_grid) )
    omega_grid['time'] = [ 0 ]
    #
    # mtall_data
    integrand_name = 'mtall'
    mtall_data = dict()
    for node_name in [ 'n0', 'n1', 'n2', 'n3', 'n4', 'n5', 'n6' ] :
        mtall_data[node_name] = list()
        income                = avg_income[node_name]
        for age_id in omega_grid['age'] :
            age  = age_grid[age_id]
            time = 2000.0
            mtall = average_integrand(integrand_name, age, node_name, income)
            mtall_data[node_name].append(mtall)
    #
    # Create all_node.db
    # We could get all_cov_reference from here, but we do not need to
    all_node_database = 'all_node.db'
    at_cascade.create_all_node_db(
        all_node_database   = all_node_database   ,
        root_node_database  = root_node_database  ,
        all_cov_reference   = all_cov_reference ,
        omega_grid          = omega_grid,
        mtall_data          = mtall_data,
    )
    #
    # node_table
    new        = False
    connection = dismod_at.create_connection(root_node_database, new)
    node_table = dismod_at.get_table_dict(connection, 'node')
    connection.close()
    #
    # cascade starting at n0
    fit_node_name = 'n0'
    if not os.path.exists(fit_node_name) :
        os.makedirs(fit_node_name )
    fit_node_database =  fit_node_name + '/dismod.db'
    shutil.copyfile(root_node_database, fit_node_database)
    cascade_fit_node(all_node_database, fit_node_database, node_table)
    #
    # check results
    for leaf_node_database in [
        'n0/n1/n3/dismod.db',
        'n0/n1/n4/dismod.db',
        'n0/n2/n5/dismod.db',
        'n0/n2/n6/dismod.db',
    ] :
        check_fit(leaf_node_database)

#
main()
print('simple_ode: OK')
sys.exit(0)
# END simple_ode source code