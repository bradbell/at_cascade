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

Covariates
**********
There are two covariates in this example:

-   *one* : This covariate always has value one and reference value zero.

-   *income* : This covariate is the income for the corresponding data.
    Its reference value is the average income corresponding
    to the :ref:`glossary.fit_node`.

Multipliers
***********
There are two covariate multipliers in this example:

alpha
*****
We use *alpha* for the :ref:`glossary.rate_value` which multipliers *income*.
This multiplier affects the value of *iota*.

gamma
*****
We use *gamma* for the :ref:`glossary.meas_noise` which multiplies *one*.
This multiplier affects the noise level for
:ref:`glossary.Sincidence` measurements.


{xsrst_end xam_level2_leaf4}
'''
#
# avg_income
avg_income       = { 'n3':1.0, 'n4':2.0, 'n5':3.0, 'n6':4.0 }
avg_income['n2'] = ( avg_income['n5'] + avg_income['n6'] ) / 2.0
avg_income['n1'] = ( avg_income['n3'] + avg_income['n4'] ) / 2.0
avg_income['n0'] = ( avg_income['n1'] + avg_income['n2'] ) / 2.0
#
def root_node_db(file_name) :
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
