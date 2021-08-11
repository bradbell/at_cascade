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
{xsrst_begin xam_level2_leaf4}
{xsrst_spell
    avg
    dage
    dtime
}

Example with Two Random Effects Levels and Four Leaf Nodes
##########################################################

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
:ref:`glossary.iota`.
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
The only simulated integrand for this example is :ref:`glossary.sincidence`.
In addition, it is simulated with any noise; i.e.,
the i-th measurement is simulated as
*y_i = iota_true(a_i, n_i, I_i)*
where *a_i* is the age,
*n_i* is the node,
and *I_i* is the income for the i-th measurement.

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
This value prior is uniform with lower limit *-alpha_true*,
upper limit *+alpha_true* and mean zero.
(The mean is used to initialize the optimization.)


{xsrst_end xam_level2_leaf4}
'''
#
# BEGIN alpha_true
alpha_true = - 0.10
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
sum_random       = { 'n0':0.0, 'n1':0.0 + 0.2, 'n2':0.0 - 0.2 }
sum_random['n3'] = sum_random['n1'] + 0.2;
sum_random['n4'] = sum_random['n1'] - 0.2;
sum_random['n5'] = sum_random['n2'] + 0.2;
sum_random['n6'] = sum_random['n2'] - 0.2;
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
    (1 + a / 100) * 1e-2 * exp( s_n + alpha_true * ( I - r_0 ) )
# END iota_true
#
# BEGIN income_grid
income_grid = dict()
for node in [ 'n3', 'n4', 'n5', 'n6' ] :
    income_grid[node] = [ 2.0 * j * avg_income[node] / 5.0 for j in range(6) ]
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
        },{ # prior_iota_no_child
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
        'name':
        'parent_smooth':  'smooth_iota_n0'        ,
        'child_smooth':   'smooth_iota_n1_and_n2' ,
    } ]
    #
    # covariate_table
    covariate_table = [
        { 'name':'one',      'reference':0.0              },
        { 'name':'income',   'reference':avg_income['n0'] },
    ]
    #
    # mulcov_table
    mulcov_table = [
        { # alpha
        'covariate':  'income',
        'type':       'rate_value',
        'effected':   'Sincidence',
        'group':      'world',
        'smooth':     'smooth_alpha',
        },{ # gamma
        'covariate':  'one',
        'type':       'mes_noise',
        'effected':   'Sincidence',
        'group':      'world',
        'smooth':     'smooth_gamma'
    } ]
    #
    # prior_table
