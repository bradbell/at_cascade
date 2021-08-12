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
{xsrst_begin one_at_function_py}
{xsrst_spell
    avg
    dage
    dtime
}

Example That Directly Measures One Age Time Function
####################################################

Under Construction
******************
This example is under construction.

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
The only non-zero dismod_at rate for this example is
:ref:`glossary.iota`; i.e.,
we choose *iota* to represent the function that we are estimating.
(We could have used any of the dismod_at rates.)
We use :math:`\iota_n(a, t)` and *iota_n* to denote the value for *iota*
as a function of age and time at node number *n*.

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
for the :ref:`glossary.rate_value` that multipliers *income*.
This multiplier affects the value of *iota*.
The true value for *alpha* (used which simulating the data) is
{xsrst_file
    # BEGIN alpha_true
    # END alpha_true
}


Random Effects
**************
For each node, there is a random effect on *iota* that is constant
in age and time. Note leaf nodes have the random effect for the node
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

iota_true(a, n, I)
==================
This is the true value for *iota* in node *n* at age *a* and income *I*:
{xsrst_file
    # BEGIN iota_true
    # END iota_true
}


y_i
===
The only simulated integrand for this example is :ref:`glossary.sincidence`
which is a direct measurement of *iota*.
(If we had used a different rate to represent the fucntion we are estimating,
we would use the corresponding direct measurement of that rate.)
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

Parent Smoothing
****************
This is the smoothing used in the *fit_node* model for *iota*.
(The :ref:`glossary.fit_node` is the parent node in dismod_at notation.)
This smoothing uses the *age_gird* and one time point.
There are no dtime priors because there is only one time point.

Value Prior
===========
The *fit_node* value prior is uniform with lower limit
*iota_true(0)/10* and upper limit *iota_true(100)\*10*.
The mean is *iota_true(50)*
(which is used to initialize the optimization.)

Dage Prior
==========
The prior for age differences is log Gaussian with mean zero,
standard deviation one, and :ref:`glossary.eta` equal to
*iota_true(50)/1000* .

Child Smoothing
***************
This is the smoothing used in the model for the *iota*
random effect for each child of the *fit_node*.
The smoothing only has one age and one time point; i.e.,
the corresponding function is constant in age and time.
There are no dage or dtime priors because there is only one
age and one time point.

Value Prior
===========
This value prior is gaussian with mean zero and standard deviation one.
There are no upper or lower limits in this prior.

Alpha Smoothing
***************
This is the smoothing used in the model for *alpha*.
There are no dage or dtime priors because there is only one
age and one time point in this smoothing.

Value Prior
===========
This value prior is uniform with lower limit *-|alpha_true|*,
upper limit *+|alpha_true|* and mean zero.
(The mean is used to initialize the optimization.)


{xsrst_end one_at_function_py}
'''
import sys
import os
import copy
import distutils.dir_util
import dismod_at
from math import exp
#
# BEGIN alpha_true
alpha_true = - 0.1
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
# BEGIN iota_true
def iota_true(a, n = 'n0', I = avg_income['n0'] ) :
    s_n = sum_random[n]
    r_0 = avg_income['n0']
    return (1 + a / 100) * 1e-2 * exp( s_n + alpha_true * ( I - r_0 ) )
# END iota_true
#
# BEGIN income_grid
number_income = 5
income_grid   = dict()
for node in [ 'n3', 'n4', 'n5', 'n6' ] :
    delta_income      = 2.0 * avg_income[node] / (number_income - 1)
    income_grid[node] = [ j * delta_income for j in range(number_income) ]
# END income_grid
#
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
            'std':     1.0,
            'eta':     iota_true(0) * 1e-3,
        },{ # prior_iota_child
            'name':    'prior_iota_child',
            'density': 'gaussian',
            'mean':    0.0,
            'std':     1.0,
        },{ # prior_alpha_n0
            'name':    'prior_alpha_n0',
            'density': 'uniform',
            'lower':   -abs(alpha_true) * 10,
            'upper':   +abs(alpha_true) * 10,
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
    }
    for age_id in range( len(age_grid) ) :
        row['integrand'] = 'Sincidence'
        age = age_grid[age_id]
        row['age_lower'] = age
        row['age_upper'] = age
        avgint_table.append( copy.copy(row) )
    #
    # data_table
    data_table    = list()
    leaf_node_set = { 'n3', 'n4', 'n5', 'n6' }
    row = {
        'node':         'n0',
        'subgroup':     'world',
        'weight':       '',
        'time_lower':   2000.0,
        'time_upper':   2000.0,
        'income':       None,
        'integrand':    'Sincidence',
        'density':      'gaussian',
        'hold_out':     False,
    }
    for (age_id, age) in enumerate( age_grid ) :
        for node in leaf_node_set :
            for income in income_grid[node] :
                meas_value = iota_true(age, node, income)
                row['node'] = node
                row['meas_value'] = meas_value
                row['age_lower']  = age
                row['age_upper']  = age
                row['income']     = income
                # model for the measurement noise
                # actual measruement noise is zero
                row['meas_std']   = meas_value / 2.0
                data_table.append( copy.copy(row) )
    #
    # time_grid
    time_grid = [ 2000.0 ]
    #
    # weight table:
    weight_table = list()
    #
    # nslist_table
    #
    nslist_table = dict()
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
# ---------------------------------------------------------------------------
# change into the build/example directory
distutils.dir_util.mkpath('build/example')
os.chdir('build/example')
#
# Create root_node.db
file_name  = 'root_node.db'
root_node_db(file_name)
#
# init root_node.db
dismod_at.system_command_prc( [ 'dismod_at', file_name, 'init' ] )
#
# fit root_node.db
dismod_at.system_command_prc( [ 'dismod_at', file_name, 'fit', 'both' ] )
#
dismod_at.system_command_prc( [ 'dismodat.py', file_name, 'db2csv' ] )
#
print('level2_leaf4: OK')
sys.exit(0)
