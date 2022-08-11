# -----------------------------------------------------------------------------
# at_cascade: Cascading Dismod_at Analysis From Parent To Child Regions
#           Copyright (C) 2021-22 University of Washington
#              (Bradley M. Bell bradbell@uw.edu)
#
# This program is distributed under the terms of the
#     GNU Affero General Public License version 3.0 or later
# see http://www.gnu.org/licenses/agpl.txt
# -----------------------------------------------------------------------------
"""
{xrst_begin_parent csv_interface}
{xrst_spell
    dir
    csv
}

Simulate and Fit an AT Cascade Data Set
#######################################

Under Construction
******************

Syntax
**********

- ``at_cascade.csv_interface(`` *csv_dir* ``,`` *command* ``)``

Arguments
*********

csv_dir
=======
This string is the directory name where the csv files
are located.

command
=======
This string is either ``simulate``, ``fit`` , or ``predict``  .
{xrst_child_table}

Notation
********

Demographer
===========
None of the data is in demographer notation.
For example,
:ref:`csv_simulate@input_files@covariate.csv@time`
1990 means the beginning of 1990,
not the time interval from 1990 to 1991.

Rectangular Grid
================
A csv file is said to have a rectangular grid in columns
*name_a* , *name_b*, *name_c* if the following holds:

#.  The csv file has columns with the names
    *name_a*, *name_b*, *name_c*.

#.  :math:`( a_1 , \ldots , a_L )`
    is the vector of values in column *name_a* .

#.  :math:`( b_1 , \ldots , b_M )`
    is the vector of values in column *name_b* .

#.  :math:`( c_1 , \ldots , c_N )`
    is the vector of values in column *name_c* .

#.  For :math:`\ell = 1 , \ldots , L`,
    :math:`m = 1 , \ldots , M`,
    :math:`n = 1,  \ldots , N` ,
    there is one and only one row with
    *name_a* equal to :math:`a_\ell`,
    *name_b* equal to :math:`b_m`, and
    *name_c* equal to :math:`c_n`.

Covariates
==========
For these simulations, all the covariates are
:ref:`glossary@relative_covariate` (called country covariates at IHME).
Sex is the
:ref:`all_option_table@split_covariate_name` and is not
referred to as a covariate by the simulate routine.

Data Type
=========
The actual data type for each entry in a csv file is a string; i.e.,
an arbitrary sequence of characters. Certain columns have further
restrictions as described below

1.  An integer value is a string represents of an integer.
2.  A float value is a string that represents a floating point number.
3.  A sex value is either ``female`` , ``male`` or ``both`` .

Index Column
============
An index column for a csv file is an integer column
that has the row number corresponding to each row.
It starts with zero at the first row below the header row.
If a column name is an index column for two or more files,
rows with the same index value in the different files
correspond to each other.

Distributions
=============
Unless other wise specified, the mean and standard deviations that
simulate refers to are for a normal distribution.

{xrst_end csv_interface}

===============================================================================

{xrst_begin csv_simulate}
{xrst_spell
    csv
    std
    cv
    sim
    meas
    bilinear
}

Simulate A Cascade Data Set
###########################

Input Files
***********

option.csv
==========
This csv file has two columns,
one called ``name`` and the other called ``value``.
The rows are documented below by the name column:

std_random_effects
------------------
This is the standard deviation of the random effects.
All fo the effects are in log of rate space, so this standard deviation
is also in log of rate space.

-----------------------------------------------------------------------------

node.csv
========
This csv file defines the node tree.
It has the columns documented below.

node_name
---------
This string is a name describing the node in a way that is easy for a human to
remember. It be unique for each row.

parent_name
-----------
This string is the node name corresponding to the parent of this node.
The root node of the tree has an empty entry for this column.
If a node is a parent, it must have at least two children.
This avoids fitting the same location twice as one goes from parent
to child nodes.

-----------------------------------------------------------------------------

covariate.csv
=============
This csv file specifies the value of omega and the covariates.
It has a :ref:`csv_interface@notation@rectangular_grid` in the columns
``node_name``, ``sex``, ``age``, ``time`` .

node_name
---------
This string identifies the node, in node.csv, corresponding to this row.

sex
---
This identifies which sex this row corresponds to.

age
---
This float is the age, in years,  corresponding to this row.

time
----
This float is the time, in years, corresponding to this row.

omega
-----
This float is the value of omega (other cause mortality) for this row.
Often other cause mortality is approximated by all cause mortality.
Omega is a rate, not a covariate.

covariate_name
--------------
For each covariate that we are including in this simulation,
there is a column in the header that contains the *covariate_name*.
The other values in that column are float representations of the covariate.
All of these covariates are
:ref:`glossary@relative_covariate`; see
:ref:`csv_interface@notation@covariates`.

-----------------------------------------------------------------------------

multiplier_sim.csv
==================
This csv file provides information about the covariate multipliers.
Each row of this file, except the header row, corresponds to a
different multiplier. The multipliers are constant in age and time.

multiplier_id
-------------
is an :ref:`csv_interface@Notation@index_column` for multiplier_sim.csv.

rate_name
---------
This string is ``iota``, ``rho``, ``chi``, or ``pini`` and specifies
which rate this covariate multiplier is affecting.

covariate_or_sex
----------------
If this is ``sex`` it specifies that this multiplier multiples
the sex values where female = -0.5, male = +0.5, and both = 0.0.
Otherwise this is one of the covariate names in the covariate.csv file
and specifies which covariate is being multiplied.

multiplier_truth
----------------
This is the value of the covariate multiplier used to simulate the data.

-----------------------------------------------------------------------------

rate_sim.csv
============
This csv file specifies the grid points at which each rate is modeled
during a simulation. It has a
:ref:`csv_interface@notation@rectangular_grid` in the columns
``rate_name``, ``age``, ``time`` .
These are no-effect rates; i.e., the rates without
the random and covariate effects.
Covariate multipliers that are constrained to zero during the fitting
can be used to get variation between nodes in the
no-effect rates corresponding to the fit.

rate_sim_id
-----------
is an :ref:`csv_interface@Notation@index_column` for rate_sim.csv.

rate_name
---------
This string is ``iota``, ``rho``, ``chi``, or ``pini`` and specifies the rate.
If one of these rates does not appear, it is modeled as always zero.

age
---
This float is the age, in years,  corresponding to this row.

time
----
This float is the time, in years, corresponding to this row.

rate_truth
----------
This float is the no-effect rate value for all the nodes.
It is used to simulate the data.
As mentioned, above knocking out covariate multipliers can be
used to get variation in the no-effect rates that correspond to the fit.
If *rate_name* is ``pini``, *rate_truth*  should be constant w.r.t *age*
(because it is prevalence at age zero).

-----------------------------------------------------------------------------

simulate.csv
============
This csv file specifies the simulated data set
with each row corresponding to one data point.

simulate_id
-----------
is an :ref:`csv_interface@Notation@index_column` for simulate.csv.

integrand_name
--------------
This string is a dismod_at integrand; e.g. ``Sincidence``.

node_name
---------
This string identifies the node corresponding to this data point.

sex
---
is the sex for this data pont.

age_lower
---------
is the lower age limit for this data row.

age_upper
---------
is the upper age limit for this data row.

time_lower
----------
is the lower time limit for this data row.

time_upper
----------
is the upper time limit for this data row.

percent_cv
----------
is the coefficient of variation as a percent of the corresponding
average integrand; i.e., the model for the integrand
without any measurement noise.
The noise will be generated with a normal distribution
that has mean equal to the average integrand and
standard deviation equal to the mean times percent_cv / 100.
If the resulting measurement value would be less than zero,
the value zero is be used; i.e.,
a censored normal is used to simulate the data.

------------------------------------------------------------------------------

Output Files
************

data_sim.csv
============
This contains the simulated data.
It is created during a simulate command
and has the following columns:

simulate_id
-----------
This integer identifies the row in the simulate.csv
corresponding to this row in data_sim.csv.
This is an :ref:`csv_interface@Notation@index_column`
for simulate.csv and data_sim.csv.

meas_value
----------
This float is the simulated measured value.

meas_std
--------
This float is the measurement standard deviation for the simulated
data point. This standard deviation is before censoring.

covariate_name
--------------
For each :ref:`csv_simulate@input_files@covariate.csv@covariate_name`
there is a column in the simulate.csv header that contains the name.
In the other rows, this column  contain a float that is the
corresponding covariate value at the mid point of the ages and time
intervals for this data point. This value is obtained using
bilinear interpolation of the covariate values in covariate.csv.
The interpolate is extended as constant in age (time) for points
outside the age rage (time range) in the covariate.csv file.

{xrst_end csv_simulate}

===============================================================================

{xrst_begin csv_fit}
{xrst_spell
    csv
    meas
    std
    sim
}

Fit a Simulated Data Set
########################

Input Files
***********
All the csv_simulate :ref:`csv_simulate` input and output files
are inputs to the ``csv_fit`` command.
The files listed below are additional inputs:

data_subset.csv
===============
This file identifies which rows of data_sim.csv are
included during the next fit command.

simulate_id
-----------
This identifies a row in data_csv that is included during the next
file command.

------------------------------------------------------------------------------

multiplier_prior.csv
====================
This file adds prior information for the multipliers in
:ref:`csv_simulate@input_files@multiplier_sim.csv`.

multiplier_id
-------------
This integer identifies the row in multiplier_sim.csv that
corresponds to this row in multiplier_prior.csv.

prior_mean
----------
This is the prior mean used when fitting this multiplier.

prior_std
---------
This is the prior standard deviation used when fitting this multiplier.

lower
-----
is the lower limit (during fitting) for this covariate multiplier.

upper
-----
is the upper limit (during fitting) for this covariate multiplier.
If the lower and upper limits are zero and the true value is non-zero,
the multiplier will be included in the simulated data but not in the model fit.

------------------------------------------------------------------------------

rate_prior.csv
==============
This file adds prior information for the rates in
:ref:`csv_simulate@input_files@rate_sim.csv`.

rate_sim_id
-----------
is an :ref:`csv_interface@Notation@index_column` for rate_sim.csv
and rate_prior.csv.

prior_mean
----------
This float is the mean used in the prior for the rate
without covariate or random effects.

prior_std
---------
This float is the standard deviation used in the prior for the rate
without covariate or random effects

lower
-----
is the lower limit (during fitting) for this no-effect rate.

upper
-----
is the upper limit (during fitting) for this no-effect rate.

------------------------------------------------------------------------------

Output Files
************

data_fit.csv
============
This contains the fit results for the simulated data values.
It is created during a fit command and
has the following columns:

simulate_id
-----------
This integer identifies the row in the simulate.csv and data_sim.csv
corresponding to this data estimate.

estimate
--------
This float is the estimated value for the data

residual
--------
This float is the weighted residual corresponding to this data point.
This has a simple form because there are no noise covariates;
i.e., (meas_value - estimate) / meas_std.

------------------------------------------------------------------------------

rate_fit.csv
============
This contains the fit results for the rate values.
It is created during a fit command and
has the following columns:

rate_sim_id
-----------
is an :ref:`csv_interface@Notation@index_column` for rate_sim.csv,
rate_prior.csv and rate_fit.csv.

estimate
--------
This float is the estimated value for the rate.

std_error
---------
Is the asymptotic estimate for the accuracy of the estimate.

------------------------------------------------------------------------------

multiplier_fit.csv
==================
This contains the fit results for the multiplier values.
It is created during a fit command and
has the following columns:

multiplier_id
-------------
This integer identifies the row in the multiplier_sim.csv and
multiplier_prior.csv corresponding to this multiplier estimate.

estimate
--------
This float is the estimated value for the multiplier.

std_error
---------
Is the asymptotic estimate for the accuracy of the estimate.

{xrst_end csv_fit}

===============================================================================

{xrst_begin csv_predict}
{xrst_spell
    csv
}

Predictions
###########

Input Files
***********
All the csv_simulate :ref:`csv_simulate` and :ref:`csv_fit`
input and output files are inputs to the ``csv_predict`` command.
The files listed below are additional inputs:

case.csv
========
This csv file specifies the prediction cases.
with each row corresponding to one data point.

case_id
-------
is an :ref:`csv_interface@notation@index_column` for case.csv.

integrand_name
--------------
This string is a dismod_at integrand; e.g. ``Sincidence`` for this prediction.

node_name
---------
This string identifies the node corresponding to this prediction.

sex
---
is the sex for this prediction.

age_lower
---------
is the lower age limit for this prediction.

age_upper
---------
is the upper age limit for this prediction.

time_lower
----------
is the lower time limit for this prediction.

time_upper
----------
is the upper time limit for this prediction.

------------------------------------------------------------------------------

Output Files
************

predict.csv
===========

case_id
-------
is an :ref:`csv_interface@Notation@index_column` for
predict.csv and case.csv.

integrand_predict
-----------------
is the value of the predicted integrand value corresponding to this case_id,
the fit values for the variables, plus the covariate effect.
Note that the variables are the no-effect rates and the covariate multipliers.

integrand_truth
---------------
is the value of the predicted integrand value corresponding to this case_id,
truth values for the variables, plus the covariate effect.
Note that the variables are the no-effect rates and the covariate multipliers.


{xrst_end csv_predict}
"""
# -----------------------------------------------------------------------------
# option_dict['std_random_effect']:
# is a float that is greater than zero
#
# option_dict = option_table2dict(option_table)
def option_table2dict(option_table) :
    #
    # option_dict
    option_dict = dict()
    valid_name  = { 'std_random_effects' }
    line_number = 0
    for row in option_table :
        line_number += 1
        name         = row['name']
        value        = row['value']
        if name in option_dict :
            msg  = f'csv_interface: Error: line {line_number} in option.csv\n'
            msg += f'the name {name} appears twice in this table'
            assert False, msg
        if not name in valid_name :
            msg  = f'csv_interface: Error: line {line_number} in option.csv\n'
            msg += f'{name} is not a valid option name'
            assert False, msg
        option_dict[name] = value
    #
    # option_dict
    for name in valid_name :
        if not name in option_dict :
            msg  = 'csv_interface: Error: in option.csv\n'
            msg += f'the name {name} does not apper'
            assert False, msg
    #
    # option_dict['std_random_effects']
    std_random_effects = float( option_dict['std_random_effects'] )
    if std_random_effects <= 0.0 :
        msg  = 'csv_interface: Error: in option.csv\n'
        msg += f'std_random_effect = {std_random_effect} <= 0'
        assert False, msg
    #
    return option_dict
# ----------------------------------------------------------------------------
# node_dict:
# The keys in this dictionary are the values of node_name in the table.
# For each node_name,
# node_dict[node_name] is the corresponding parent_name.
#
# node_dict = node_table2dict(node_table)
def node_table2dict( node_table ) :
    #
    # node_dict, count_children
    line_number = 0
    node_dict   = dict()
    for row in node_table :
        line_number += 1
        node_name    = row['node_name']
        parent_name  = row['parent_name']
        if node_name in node_dict :
            msg  = f'csv_interface: Error: line {line_number} in node.csv\n'
            msg += f'node_name {node_name} appears twice'
            assert False, msg
        node_dict[node_name]      = parent_name
        count_children[node_name] = 0
    #
    # count_children
    line_number    = 0
    for row in node_table :
        line_number += 1
        node_name    = row['node_name']
        parent_name  = row['parent_name']
        if parent_name not in count_children :
            msg  = f'csv_interface: Error: line {line_number} in node.csv\n'
            msg += f'parent_name {parent_name} is not a valid node_name'
            assert False, msg
        else :
            count_children[parent_name] += 1
    #
    # count_children
    for parent_name in count_children :
        if count_children[parent_name] == 1 :
            msg  = 'csv_interface: Error in node.csv\n'
            msg += f'the parent_name {parent_name} apprears once and only once'
    #
    return
# ----------------------------------------------------------------------------
# spline = covarite_dict[node_name][sex][interpolate_name] :
# 1. node_name is any of those in the covariate table
# 2. sex is any of the sexes in the covariate table
# 3. interpolate_name is any covariate_name or omega
# 4. spline(age, time, grid=False) evaluates the interpolant at (age, time)
#
# covariate_dict = interpolate_covariate_dict(covariate_table, node_set)
def interpolate_covariate_dict(covariate_table , node_set) :
    #
    # interpolate_name_list
    # this is the covariate names and omega
    interpolate_name_list = list()
    for key in covariate_table[0].keys() :
        if key not in [ 'node_name', 'sex', 'age', 'time' ]
            interpolate_name_list.append( key )
    #
    # covariate_row_list, age_set, time_set
    covariate_row_list  = dict()
    age_set             = set()
    time_set            = set()
    line_number         = 0
    for row in covariate_table :
        line_number += 1
        node_name    = row['node_name']
        sex          = row['sex']
        age          = float( row['age'] )
        time         = float( row['time'] )
        if node_name not in node_set :
            msg  = f'csv_interface: Error: '
            msg += f'line {line_number} in covariate.csv\n'
            msg += 'node_name {node_name} is not in node.csv'
            assert Flase, msg
        if sex not in ['male', 'female'] :
            msg  = f'csv_interface: Error: '
            msg += f'line {line_number} in covariate.csv\n'
            msg += 'sex {sex} is not male of female'
            assert Flase, msg
        #
        if node_name not in covariate_row_list :
            covariate_row_list[node_name] = dict()
        if sex not in covariate_row_list[node_name] :
            covariate_row_list[node_name][sex] = list()
        #
        # covariate_row_list, age_set, time_set
        covariate_row_list[node_name][sex].append( row )
        age_set.add( age )
        time_set.add( time )
    #
    # age_grid, time_grid
    age_grid  = sorted( age_set )
    time_grid = sorted( time_set)
    #
    # n_age, n_time
    n_age  = len(age_grid)
    n_time = len(time_grid)
    #
    # covariate_grid
    covariate_grid = numpy.empty( (n_age, n_time) )
    #
    # covariate_dict, node_name, sex
    covariate_dict = dict()
    for node_name in covariate_row_list :
        covariate_dict[node_name] = dict()
        for sex in covariate_row_list[node_name] :
            covariate_dict[node_name][sex] = dict()
            #
            # triple_list
            triple_list = list()
            for row in covariate_row_list[node_name][sex] :
                age    = float( row['age'] )
                time   = float( row['time'] )
                triple = (age, time, row)
                triple_list.append( triple )
            #
            # triple_list
            triple_list = sorted(triple_list)
            #
            # msg
            msg  = 'csv_interface: Error in covaraite.csv\n'
            msg += 'node_name = {node_name}, sex = {sex} \n'
            msg += 'Expected following rectangular grid:\n'
            msg += f'age_grid  = {age_grid}\n'
            msg += f'time_grid = {time_grid}'
            #
            if len(triple_list) != n_age * n_time
                assert False, msg
            #
            # interpolate_name
            for interpolate_name in interpolate_name_list :
                #
                # covariate_grid
                covariate_grid[:] = numpy.nan
                #
                # index, triple
                for (index, triple) in enumerate( tripe_list ) :
                    #
                    # age_index, time_index
                    age        = triple[0]
                    time       = triple[1]
                    age_index  = int( index / n_time )
                    time_index = index % n_time
                    if age != age_grid[age_index] :
                        assert False, msg
                    if time != time_grie[time_index] :
                        assert False, msg
                    #
                    # covariate_grid
                    row   = triple[2]
                    value = float( row[interpolate_name] )
                    covariate_grid[age_index][time_index] =  value
            #
            # covariate_dict
            spline= RectBivariateSpline(
                age_grid, time_grid, covariate_grid, kx=1, ky=1, s=0
            )
            covariate_dict[node_name][sex][interpolate_name] = spline
    return covariate_dict
# ----------------------------------------------------------------------------
# spline = rate_truth_dict[rate_name] :
# 1. rate_name is any of the rates in the ; table
# 4. spline(age, time, grid=False) evaluates the interpolant at (age, time)
#
# rate_truth_dict = interpolate_rate_truth(rate_sim_table)
def interpolate_rate_truth_dict(rate_sim_table) :
    #
    # valid_rate_name
    valid_rate_name = [ 'iota', 'rho', 'chi', 'pini' ]
    #
    # age_set, time_set
    rate_row_list   = dict()
    age_set         = set()
    time_set        = set()
    line_number     = 0
    for row in rate_sim_table :
        line_number += 1
        rate_name    = row['rate_name']
        age          = float( row['age'] )
        time         = float( row['time'] )
        rate_truth   = float( row['rate_truth'] )
        #
        if rate_name not in rate_row_list :
            rate_row_list[rate_name] = list()
        rate_row_list[rate_name].append( row )
        age_set.add( age )
        time_set.add( time )
    #
    # age_grid, time_grid
    age_grid  = sorted( age_set )
    time_grid = sorted( time_set)
    #
    # n_age, n_time
    n_age  = len(age_grid)
    n_time = len(time_grid)
    #
    # covariate_grid
    rate_grid = numpy.empty( (n_age, n_time) )
    #
    # rate_truth_dict, rate_name
    rate_truth_dict = dict()
    for rate_name in rate_row_list :
        #
        # triple_list
        triple_list = list()
        for row in rate_row_list[rate_name] :
            age    = float( row['age'] )
            time   = float( row['time'] )
            triple = (age, time, row)
            triple_list.append( triple )
        #
        # triple_list
        triple_list = sorted(triple_list)
        #
        # msg
        msg  = 'csv_interface: Error in rate_sim.csv\n'
        msg += 'rate_name = {rate_name}\n'
        msg += 'Expected following rectangular grid:\n'
        msg += f'age_grid  = {age_grid}\n'
        msg += f'time_grid = {time_grid}'
        #
        if len(triple_list) != n_age * n_time
            assert False, msg
        #
        # rate_grid
        rate_grid[:] = numpy.nan
        #
        # index, triple
        for (index, triple) in enumerate( tripe_list ) :
            #
            # age_index, time_index
            age        = triple[0]
            time       = triple[1]
            age_index  = int( index / n_time )
            time_index = index % n_time
            if age != age_grid[age_index] :
                assert False, msg
            if time != time_grie[time_index] :
                assert False, msg
            #
            # covariate_grid
            row   = triple[2]
            value = float( row['rate_truth'] )
            rate_grid[age_index][time_index] =  value
            #
            # rate_truth_dict
            spline= RectBivariateSpline(
                age_grid, time_grid, covariate_grid, kx=1, ky=1, s=0
            )
            rate_truth_dict[rate_name]= spline
    return rate_truth_dict
# ----------------------------------------------------------------------------
def csv_simulate(csv_dir) :
    valid_integrand_name = {
        'Sincidence',
        'remission',
        'mtexcess',
        'mtother',
        'mtwith',
        'susceptible',
        'withC',
        'prevalence',
        'Tincidence',
        'mtspecific',
        'mtall',
        'mtstandard',
        'relrisk',
    }
    #
    # input_table
    input_table = dict()
    input_list  = [
        'option',
        'node',
        'covariate',
        'multiplier_sim',
        'rate_sim',
        'simulate',
    ]
    for name in input_list :
        file_name         = f'{csv_dir}/{name}.csv'
        input_table[name] = at_cascade.read_csv_file(file_name)
    #
    # option_dict
    option_dict = option_table2dict( input_table['option'] )
    #
    # node_table_dict
    node_table_dict = node_table2dict( input_table['node'] )
    #
    # covariate_dict
    node_set = set( node_table_dict.keys() )
    covariate_dict = interpolate_covaraite_dict(
        input_table['covariate'], node_set
    )
    #
    # covariate_name_list
    covariate_name_list = list()
    covariate_sum_list = list()
    for key in input_table['covariate'][0].keys() :
        if key not in [ 'node_name', 'sex', 'age', 'time', 'omega' ] :
            covariate_name_list.append(key)
            covariate_sum_list.append( 0.0 )
    #
    # rate_truth_dict
    rate_truth_dict = ineterpolate_rate_truth_dict( input_table['rate_sim'] )
    #
    # multiplier_dict
    multiplier_dict = dict()
    for rate_name in rate_truth_dict :
        multiplier_dict[rate_name] = list()
    for row in input_file['multiplier_sim'] :
        rate_name = row['rate_name']
        if rate_name in multiplier_dict :
                multiplier_dict[rate_name].append(row)
    #
    # data_sim_table
    data_sim_table = list()
    for (simulate_id, row) in enumerate( input_table['simlate'] ) :
        line_nmber = simulate_id + 1
        #
        # simulate_id
        if simulate_id != int( row['simulate_id'] ) :
            msg  = f'csv_interface: Error at line {line_number} '
            msg += f' in simulate.csv\n'
            msg += f'simulate_id = ' + row['simulate_id']
            msg += ' is not equal line number minus one'
            assert False, msg
        #
        # integrand_name
        integrand_name = row['integrand_name']
        if integrand_name not in valid_intergrand_name :
            msg  = f'csv_interface: Error at line {line_number} '
            msg += f' in simulate.csv\n'
            msg += f'integrand_name = ' + integrand_name
            msg += ' is not a valid integrand name'
            assert False, msg
        #
        # node_name
        node_name = row['node_name']
        if node_name not in node_set :
            msg  = f'csv_interface: Error at line {line_number} '
            msg += f' in simulate.csv\n'
            msg += f'node_name = ' + node_name
            msg += ' is not in node.csv'
            assert False, msg
        #
        # sex
        sex = row['sex']
        if sex not in [ 'male', 'female', 'both' ] :
            msg  = f'csv_interface: Error at line {line_number} '
            msg += f' in simulate.csv\n'
            msg += f'sex = ' + sex
            msg += ' is not male, feamle, or both'
            assert False, msg
        #
        # age_mid, time_mid
        age_mid  = (float(row['age_lower']  + float(row['age_upper']))  / 2.0
        time_mid = (float(row['time_lower'] + float(row['time_upper'])) / 2.0
        #
        # covariate_value_list
        # covaraite_sum_list
        covariate_value_list = list()
        for (index, covariate_name) in enumerate( covariate_name_list ) :
            spline = covariate_dict[node_name][sex][[covariate_name]
            value  =  spline(age_mid, time_mid, grid = False)
            covariate_value_list.append(value )
            covariate_sum_list[index] += value
        #
        # row
        row = dict( zip(covariate_name_list, covariate_value_list) )
        row['simulate_id'] = simulate_id
        data_sim_table.append( row )
# ----------------------------------------------------------------------------
def csv_interface(csv_dir, command) :
    #
    # command_dict
    command_dict = {
        'simulate' : csv_simulate,
    }
    if command not in command_dict :
        msg  = f'csv_interface: Error: command {command} is not implemented'
        assert False, msg
    #
    # execute the command
    command_dict[command](csv_dir)
    #
    print('No errors detected')
