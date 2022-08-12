# -----------------------------------------------------------------------------
# at_cascade: Cascading Dismod_at Analysis From Parent To Child Regions
#           Copyright (C) 2021-22 University of Washington
#              (Bradley M. Bell bradbell@uw.edu)
#
# This program is distributed under the terms of the
#     GNU Affero General Public License version 3.0 or later
# see http://www.gnu.org/licenses/agpl.txt
# -----------------------------------------------------------------------------
import at_cascade
import random
import time
import numpy
import scipy.interpolate
"""
{xrst_begin csv_simulate}
{xrst_spell
    avg
    csv
    std
    cv
    sim
    meas
    bilinear
}

Simulate A Cascade Data Set
###########################

option.csv
**********
This csv file has two columns,
one called ``name`` and the other called ``value``.
The rows are documented below by the name column:

std_random_effects
==================
This input float is the standard deviation of the random effects.
All fo the effects are in log of rate space, so this standard deviation
is also in log of rate space.

integrand_step_size
===================
This input float is the step size in age and time used to approximate
integrand averages from age_lower to age_upper
and time_lower to time_upper (in data_sim.csv).
It must be greater than zero.

random_seed
===========
This integer is used to seed the random number generator.
This row is optional in option.csv.
If it is not present, the system clock is used to choose *random_seed*
and the corresponding row is added to option.csv.


Input Files
***********

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
The sex value ``both`` does not appear in this table.

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

covariate_avg.csv
=================
This file contains the averages in covariate.csv for each sex and node.
These averages are used as reference values when determining the
covariate difference betwen the rate values in rate.csv and
a particular node and sex.

node_name
---------
This string identifies the node corresponding to the average.
The specified node and all its descendants are included in the average.

sex
---
This is ``male`` or ``female`` and
specifies wich sex, in covariate.csv, the average was for.

covariate_name
--------------
For each :ref:`csv_simulate@input_files@covariate.csv@covariate_name`
there is a colum that contains a float value equal to
the average for the corresponding sex and node.

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
Not that not all these row get included during fitting; see
:ref:`csv_fit@input_files@data_subset.csv@simulate_id`.

meas_mean
---------
This float is the mean value for the measurement.
This is the model value without any measurement noise.

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
"""
# -----------------------------------------------------------------------------
# Returns a dictionary verison of option_table.
# This routine will set random.seed to the value in the option.csv table.
#
# option_dict = option_table2dict(csv_dir, option_table)
def option_table2dict(csv_dir, option_table) :
    #
    # option_dict
    option_dict = dict()
    valid_name  = {
        'std_random_effects', 'integrand_step_size', 'random_seed'
    }
    required_name  = {
        'std_random_effects', 'integrand_step_size'
    }
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
    for name in required_name :
        if not name in option_dict :
            msg  = 'csv_interface: Error: in option.csv\n'
            msg += f'the name {name} does not apper'
            assert False, msg
    #
    # float options that must be greater than zero
    for name in ['std_random_effects', 'integrand_step_size'] :
        value = float( option_dict[name] )
        if value <= 0.0 :
            msg  = 'csv_interface: Error: in option.csv\n'
            msg += f'{name} = {value} <= 0'
            assert False, msg
    #
    # random_seed
    name = 'random_seed'
    if name not in option_dict :
        value = str( int( time.time() ) )
        row   = { 'name' : 'random_seed' ,  'value' : value }
        option_table.append(row)
        file_name = f'{csv_dir}/option.csv'
        at_cascade.write_csv_table(file_name, option_table)
        option_dict[name] = value
    #
    # set the random seed
    random.seed( int( option_dict['random_seed'] ) )
    #
    #
    return option_dict
# ----------------------------------------------------------------------------
# parent_dict:
# The keys in this dictionary are the values of node_name in the table.
# For each node_name,
# parent_dict[node_name] is the corresponding parent_name.
#
# parent_dict = node_table2dict(node_table)
def node_table2dict( node_table ) :
    #
    # parent_dict, count_children
    line_number = 0
    parent_dict    = dict()
    count_children = dict()
    for row in node_table :
        line_number += 1
        node_name    = row['node_name']
        parent_name  = row['parent_name']
        if node_name in parent_dict :
            msg  = f'csv_interface: Error: line {line_number} in node.csv\n'
            msg += f'node_name {node_name} appears twice'
            assert False, msg
        parent_dict[node_name]      = parent_name
        count_children[node_name] = 0
    #
    # count_children
    line_number    = 0
    for row in node_table :
        line_number += 1
        node_name    = row['node_name']
        parent_name  = row['parent_name']
        if parent_name != '' :
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
    return parent_dict
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
        if key not in [ 'node_name', 'sex', 'age', 'time' ] :
            interpolate_name_list.append( key )
    #
    # covariate_row_list
    covariate_row_list  = dict()
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
        # covariate_row_list
        if node_name not in covariate_row_list :
            covariate_row_list[node_name] = dict()
        if sex not in covariate_row_list[node_name] :
            covariate_row_list[node_name][sex] = list()
        covariate_row_list[node_name][sex].append( row )
    #
    # covariate_dict, node_name, sex
    covariate_dict = dict()
    for node_name in covariate_row_list :
        covariate_dict[node_name] = dict()
        for sex in covariate_row_list[node_name] :
            covariate_dict[node_name][sex] = dict()
            #
            # age_grid, time_grid, spline_dict
            age_grid, time_grid, spline_dict = at_cascade.bilinear(
                table  = covariate_row_list[node_name][sex] ,
                x_name = 'age',
                y_name = 'time',
                z_list = interpolate_name_list
            )
            #
            if spline_dict == None :
                msg  = 'csv_interface: Error in covariate.csv\n'
                msg += 'node_name = {node_name}, sex = {sex} \n'
                msg += 'Expected following rectangular grid:\n'
                msg += f'age_grid  = {age_grid}\n'
                msg += f'time_grid = {time_grid}'
                assert False, msg
            #
            # covariate_dict
            covariate_dict[node_name][sex] = spline_dict
    return covariate_dict
# ----------------------------------------------------------------------------
# spline = rate_truth_dict[rate_name] :
# 1. rate_name is any of the rates in the rate_sim table.
# 2. spline(age, time, grid=False) evaluates the interpolant at (age, time)
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
        if len(triple_list) != n_age * n_time :
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
            if time != time_grid[time_index] :
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
# covarite_avg_table:
# is the table corresponding to covariate_avg.csv
#
# covariate_avg_dict[node_name][sex][covariate_name]
# is the average corresponding to the specified node, sex, and covariate
#
# covariate_table:
# is the table corresponding to covariate.csv
#
# covariate_name_list:
# is a list of the covariate names
#
# covariate_avg_dict, covariate_avg_table = get_covariate_sim_table(
#   covariate_table, covariate_name_list
# )
def get_covariate_avg_table( covariate_table, covariate_name_list) :
    #
    # covariate_avg_table
    covariate_avg_table = list()
    covariate_avg_dict  = dict()
    #
    # node_name_set
    # sex_set
    node_name_set = set()
    sex_set       = set()
    for row in covariate_table :
        node_name_set.add( row['node_name'] )
        sex_set.add( row['sex'] )
    #
    if 'both' in sex_set :
        msg = 'csv_interface: sex = both can not appear in covariate.csv'
        assert False, msg
    #
    # sex
    for sex in set_sex :
        #
        # covariate_sum, node_count
        covariate_sum   = dict()
        for node_name in node_name_set :
            node_count[node_name]      = 0
            covariate_sum[node_name]   = list()
            for covariate_name in covariate_name_list :
                covariate_sum[node_name].append(0.0)
        #
        # covariate_sum,
        for row in covariate_table :
            if row['sex'] == sex :
                node_name = covariate_table['node_name']
                node_count[node_name] += 1
                for (i, covariate_name) in enumerate( covariate_name_list ) :
                    covariate_sum[node_name][i] += float(row[covariate_name])
        #
        # covariate_avg_table
        previous_count = None
        previous_node  = None
        for node_name in node_name_set :
            if previous_count != None :
                if node_count[node_name] != previous_count :
                    count = node_count[node_name]
                    msg   = 'csv_interface: covariate.csv: '
                    msg  += 'number of covariates depends on node\n'
                    msg  += f'sex = {sex}, node_name = {node_name}, '
                    msg  += f'count = {count}\n'
                    msg  += f'sex = {sex}, node_name = {previous_node_name}, '
                    msg  += f'count = {previous_count}\n'
                    assert False, msg
            #
            # covariate_avg_table
            # covariate_avg_dict
            covariate_avg_dict[node_name][sex] = dict()
            row = { 'sex' : sex, 'node_name' : node_name }
            for (i, covariate_name) in enumerate(covariate_name_list) :
                average = covariate_sum[node_name][i] / node_count[node_name]
                row[covariate_name] = average
            covariate_avg_table.append(row)
            covariate_avg_dict[node_name][sex] = row
            #
# ----------------------------------------------------------------------------
def average_integrand_rate(
    rate_truth_dict      ,
    covariate_name_list  ,
    covariate_dict       ,
    covariate_avg_dict   ,
    multiplier_dict      ,
    node_name            ,
    sex                  ,
) :
    def fun(age, time, rate_name) :
        spline         = rate_truth_dict[rate_name]
        no_effect_rate = spline(age, time, grid = False)
        effect         = 0.0
        for row in multiplier_dict[rate_name] :
            assert row['rate_name'] == rate_name
            covariate_or_sex = row['covariate_or_sex']
            if covariate_or_sex != 'sex' :
                covariate_name = covariate_or_sex
                spline     = covariate_dict[node_name][sex][covariate_name]
                covariate  = spline(age, time, grid = False)
                average    = covariate_avg_dict[node_name][sex][covariate_name]
                difference = covariate - average
                effect += float( row['multiplir_truth'] ) * difference
        rate = math.exp(effect) * no_effect_rate
        return rate
    result = dict()
    result['pini']  = lambda age, time : fun(age, time, 'pini')
    result['iota']  = lambda age, time : fun(age, time, 'iota')
    result['rho']   = lambda age, time : fun(age, time, 'rho')
    result['chi']   = lambda age, time : fun(age, time, 'chi')
    result['omega'] = lambda age, time : fun(age, time, 'omega')
    return rate_fun
# ----------------------------------------------------------------------------
def avgerage_integrand_grid(
    integrand_step_size, age_lower, age_upper, time_lower, time_upper
) :
    #
    # age_grid
    if age_lower == age_upper :
        age_grid = [ age_lower ]
    else :
        n_age    = int( (age_upper - age_lower) / intgrand_step_size) + 1
        dage     = (age_upper - age_lower) / n_age
        age_grid = [ age_lower + i * dage for i in range(n_age+1) ]
    #
    # time_grid
    if time_lower == time_upper :
        time_grid = [ time_lower ]
    else :
        n_time    = int( (time_upper - time_lower) / intgrand_step_size) + 1
        dtime     = (time_upper - time_lower) / n_time
        time_grid = [ time_lower + i * dtime for i in range(n_time+1) ]
    # grid
    grid = { 'age' : age_grid , 'time' : time_grid }
    #
    return grid

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
    input_list = [ 'option', 'node', 'covariate' ]
    for name in input_list :
        file_name         = f'{csv_dir}/{name}.csv'
        input_table[name] = at_cascade.read_csv_table(file_name)
    #
    # option_dict
    option_dict = option_table2dict(csv_dir, input_table['option'] )
    #
    # parent_dict
    parent_dict = node_table2dict( input_table['node'] )
    #
    # covariate_dict
    node_set = set( parent_dict.keys() )
    covariate_dict = interpolate_covariate_dict(
        input_table['covariate'], node_set
    )
    #
    # Testing stopped here
    return
    #
    # covariate_name_list
    covariate_name_list = list()
    covariate_sum_list = list()
    for key in input_table['covariate'][0].keys() :
        if key not in [ 'node_name', 'sex', 'age', 'time', 'omega' ] :
            covariate_name_list.append(key)
    #
    # covariate_avg_dict, covariate_avg_table
    covariate_avg_dit, covariate_avg_table = get_covariate_avg_table(
        input_table['covariate'] , covariate_list
    )
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
        age_mid  = ( float(row['age_lower']) + float(row['age_upper']) ) / 2.0
        time_mid = ( float(row['time_lower']) + float(row['time_upper']) ) / 2.0
        #
        # covariate_value_list
        # covariate_sum_list
        covariate_value_list = list()
        for (index, covariate_name) in enumerate( covariate_name_list ) :
            spline = covariate_dict[node_name][sex][covariate_name]
            value  =  spline(age_mid, time_mid, grid = False)
            covariate_value_list.append(value )
            covariate_sum_list[index] += value
        #
        # row
        row = dict( zip(covariate_name_list, covariate_value_list) )
        row['simulate_id'] = simulate_id
        #
        # rate_fun_dict
        rate_fun_dict = average_integrand_rate(
            rate_truth_dict      ,
            covariate_name_list  ,
            covariate_dict       ,
            covariate_avg_dict   ,
            multiplier_dict      ,
            node_name            ,
            sex
        )
        #
        # grid
        integrand_step_size = option_dict['integrand_step_size']
        grid = averate_integrand_grid(
            integrand_step_size, age_lower, age_upper, time_lower, time_upper
        )
        #
        # avg_integrand
        avg_integrand = dismod_at.average_integrand(
            rate_fun_dict, integrand_name, grid, abs_tol
        )
        #
        # row['meas_mean']
        row['meas_mean'] = avg_integrand
        #
        # row['meas_std']
        row['meas_std'] = float( row_sim['precent_cv'] ) * average / 100.0
        #
        # row['meas_value']
        meas_noise        = random.gauss(row['meas_mean'], row['meas_std'] )
        meas_value        = row['meas_mean'] + mean_noise
        meas_value        = max(meas_value, 0.0)
        row['meas_value'] = meas_value
        #
        # data_sim_table
        data_sim_table.append( row )
    #
    # data.csv
    file_name = f'{csv_dir}/data_sim.csv'
    at_cascade.write_csv_table(file_name, data_sim_table)
    #
    # covariate_avg.csv
    file_name = f'{csr_dir}/covariate_avg.csv'
    at_cascade.write_csv_table(file_name, covariate_avg_table)
