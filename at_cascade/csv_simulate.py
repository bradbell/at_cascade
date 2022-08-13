# -----------------------------------------------------------------------------
# at_cascade: Cascading Dismod_at Analysis From Parent To Child Regions
#           Copyright (C) 2021-22 University of Washington
#              (Bradley M. Bell bradbell@uw.edu)
#
# This program is distributed under the terms of the
#     GNU Affero General Public License version 3.0 or later
# see http://www.gnu.org/licenses/agpl.txt
# -----------------------------------------------------------------------------
import math
import random
import numpy
import scipy.interpolate
import dismod_at
import at_cascade
"""
{xrst_begin csv_simulate}
{xrst_spell
    avg
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
This input float is the standard deviation of the random effects.
All fo the effects are in log of rate space, so this standard deviation
is also in log of rate space.

integrand_step_size
-------------------
This input float is the step size in age and time used to approximate
integrand averages from age_lower to age_upper
and time_lower to time_upper (in data_sim.csv).
It must be greater than zero.

random_seed
-----------
This integer is used to seed the random number generator.

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

no_effect_rate.csv
==================
This csv file specifies the grid points at which each rate is modeled
during a simulation. It has a
:ref:`csv_interface@notation@rectangular_grid` in the columns
``rate_name``, ``age``, ``time`` .
These are no-effect rates; i.e., the rates without
the random and covariate effects.
Covariate multipliers that are constrained to zero during the fitting
can be used to get variation between nodes in the
no-effect rates corresponding to the fit.

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
#
# option_value[name] :
# for is the value of the option corresponding to name.
# Here name is a string and value
# has been coverted to its corresponding type; e.g.
# option_value['random_seed'] is an ``int``.
#
# Side Effects:
# The random.seed fucntion is called with the seed value
# option_value['random_seed']
#
# option_value =
def option_table2dict(csv_dir, option_table) :
    #
    # option_value
    option_value = dict()
    valid_name  = {
        'std_random_effects', 'integrand_step_size', 'random_seed'
    }
    line_number = 0
    for row in option_table :
        line_number += 1
        name         = row['name']
        value        = row['value']
        if name in option_value :
            msg  = f'csv_interface: Error: line {line_number} in option.csv\n'
            msg += f'the name {name} appears twice in this table'
            assert False, msg
        if not name in valid_name :
            msg  = f'csv_interface: Error: line {line_number} in option.csv\n'
            msg += f'{name} is not a valid option name'
            assert False, msg
        option_value[name] = value
    #
    # option_value
    for name in valid_name :
        if not name in option_value :
            msg  = 'csv_interface: Error: in option.csv\n'
            msg += f'the name {name} does not apper'
            assert False, msg
    #
    # float options that must be greater than zero
    for name in ['std_random_effects', 'integrand_step_size'] :
        value = float( option_value[name] )
        if value <= 0.0 :
            msg  = 'csv_interface: Error: in option.csv\n'
            msg += f'{name} = {value} <= 0'
            assert False, msg
        option_value[name] = value
    #
    # random_seed
    value = int( option_value['random_seed'] )
    option_value['random_seed'] = value
    random.seed(value)
    #
    return option_value
# ----------------------------------------------------------------------------
# node2parent:
#
# node2parent[node_name]:
# The is the name of the node that is the parent of node_node.
# The keys and values in this dictionary are strings.
#
# node2parent =
def node_table2dict( node_table ) :
    #
    # node2parent, count_children
    line_number = 0
    node2parent    = dict()
    count_children = dict()
    for row in node_table :
        line_number += 1
        node_name    = row['node_name']
        parent_name  = row['parent_name']
        if node_name in node2parent :
            msg  = f'csv_interface: Error: line {line_number} in node.csv\n'
            msg += f'node_name {node_name} appears twice'
            assert False, msg
        node2parent[node_name]      = parent_name
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
    return node2parent
# ----------------------------------------------------------------------------
#
# spline = spline_node_sex_cov[node_name][sex][cov] :
# 1. node_name is any of the nodes in the covariate table (string)
# 2. sex is any of the sexes in the covariate table (string)
# 3. cov is any covariate_name or omega (string)
# 4. value = spline(age, time) evaluates the interpolant at (age, time)
#    where age, time, and value are floats.
#
# covariate_table:
# is the table corresponding to covariate_csv.
#
# node_set
# is the set of node_name that appear in node.csv.
#
#
# spline_node_sex_cov =
def get_spline_node_sex_cov(covariate_table , node_set) :
    #
    # cov_name_list
    # this is the covariate names and omega
    cov_name_list = list()
    for key in covariate_table[0].keys() :
        if key not in [ 'node_name', 'sex', 'age', 'time' ] :
            cov_name_list.append( key )
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
    # spline_node_sex_cov
    spline_node_sex_cov = dict()
    #
    # node_name
    for node_name in covariate_row_list :
        spline_node_sex_cov[node_name] = dict()
        #
        # sex
        for sex in covariate_row_list[node_name] :
            spline_node_sex_cov[node_name][sex] = dict()
            #
            # age_grid, time_grid, spline_dict
            age_grid, time_grid, spline_dict = at_cascade.bilinear(
                table  = covariate_row_list[node_name][sex] ,
                x_name = 'age',
                y_name = 'time',
                z_list = cov_name_list
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
            # spline_node_sex_cov
            spline_node_sex_cov[node_name][sex] = spline_dict
    return spline_node_sex_cov
# ----------------------------------------------------------------------------
# spline = spline_no_effect_rate[rate_name] :
# 1. rate_name is any of the rate names in the no_effect_rate table.
# 2. value = spline(age, time) evaluates the no_effect spline
#    for rate_name at the specified age and time where age, time, value
#    are all floats.
#
# no_effect_rate_table:
# is the table correspnding to no_effect_rate.csv
#
# spline_no_effect_rate =
def get_spline_no_effect_rate(no_effect_rate_table) :
    #
    # age_set, time_set
    rate_row_list   = dict()
    for row in no_effect_rate_table :
        rate_name    = row['rate_name']
        age          = float( row['age'] )
        time         = float( row['time'] )
        rate_truth   = float( row['rate_truth'] )
        #
        if rate_name not in rate_row_list :
            rate_row_list[rate_name] = list()
        rate_row_list[rate_name].append( row )
    #
    # spline_no_effect_rate
    spline_no_effect_rate = dict()
    #
    # rate_name
    for rate_name in rate_row_list :
        #
        # age_grid, time_grid, spline_dict
        age_grid, time_grid, spline_dict = at_cascade.bilinear(
            table  = rate_row_list[rate_name],
            x_name = 'age',
            y_name = 'time',
            z_list = [ 'rate_truth' ]
        )
        #
        if spline_dict == None :
            msg  = 'csv_interface: Error in no_effect_rate.csv\n'
            msg += 'rate_name = {rate_name}\n'
            msg += 'Expected following rectangular grid:\n'
            msg += f'age_grid  = {age_grid}\n'
            msg += f'time_grid = {time_grid}'
            assert False, msg
        #
        # spline_no_effect_rate
        spline_no_effect_rate[rate_name]= spline_dict['rate_truth']
    #
    return spline_no_effect_rate
# ----------------------------------------------------------------------------
# multiplier_list_rate[rate_name]:
# list of rows in multiplier_sim_table that have the specified rate name
# were rate_name is a string.
#
# multiplier_sim_table:
# is the table corresponding to multiplier_sim.csv.
#
# multiplier_list_rate =
def get_multiplier_list_rate(multiplier_sim_table) :
    #
    # multiplier_list_rate
    multiplier_list_rate = dict()
    for rate_name in [ 'pini', 'iota', 'rho', 'chi' ] :
        multiplier_list_rate[rate_name] = list()
    for row in multiplier_sim_table :
        rate_name = row['rate_name']
        multiplier_list_rate[rate_name].append(row)
    return multiplier_list_rate
# ----------------------------------------------------------------------------
# avg_node_sex_covariate[node_name][sex][covariate_name]:
# is average covariate value for the specified node, sex and covaraite name.
#
# covaraite_avg_table;
# is the table corresponding to covariate_avg.csv.
#
# covariate_table:
# is the table corresponding to covariate.csv
#
# covariate_name_list:
# is a list of the covariate names
#
# avg_node_sex_covariate, covariate_avg_table =
def get_covariate_avg_table( covariate_table, covariate_name_list) :
    #
    # covariate_avg_table, avg_node_sex_covariate
    covariate_avg_table     = list()
    avg_node_sex_covariate  = dict()
    #
    # node_name_set, sex_set
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
    # avg_node_sex_covariate[node_name]
    for node_name in node_name_set :
        avg_node_sex_covariate[node_name] = dict()
    #
    # sex
    for sex in sex_set :
        #
        # covariate_sum, node_count
        covariate_sum   = dict()
        node_count      = dict()
        for node_name in node_name_set :
            node_count[node_name]      = 0
            covariate_sum[node_name]   = list()
            for covariate_name in covariate_name_list :
                covariate_sum[node_name].append(0.0)
        #
        # covariate_sum, node_count
        for row in covariate_table :
            if row['sex'] == sex :
                node_name              = row['node_name']
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
            # avg_node_sex_covariate
            row = { 'sex' : sex, 'node_name' : node_name }
            for (i, covariate_name) in enumerate(covariate_name_list) :
                average = covariate_sum[node_name][i] / node_count[node_name]
                row[covariate_name] = average
            covariate_avg_table.append(row)
            avg_node_sex_covariate[node_name][sex] = row
            #
    return avg_node_sex_covariate, covariate_avg_table
# ----------------------------------------------------------------------------
def average_integrand_rate(
    node2parent             ,
    spline_no_effect_rate   ,
    random_effect_node_rate ,
    covariate_name_list     ,
    spline_node_sex_cov     ,
    avg_node_sex_covariate  ,
    multiplier_list_rate    ,
    node_name               ,
    sex                     ,
) :
    def fun(age, time, rate_name) :
        #
        # no_effect_rage
        spline         = spline_no_effect_rate[rate_name]
        no_effect_rate = spline(age, time)
        #
        # effect = random effects
        effect         = 0.0
        parent_node    = node2parent[node_name]
        while parent_node != '' :
            effect     += random_effect_node_rate[node_name][rate_name]
            parent_node = node2parent[parent_node]
        #
        # effect
        # covariate effects: 2DO: add sex covariate effect
        for row in multiplier_list_rate[rate_name] :
            assert row['rate_name'] == rate_name
            covariate_or_sex = row['covariate_or_sex']
            if covariate_or_sex != 'sex' :
                covariate_name = covariate_or_sex
                spline     = spline_node_sex_cov[node_name][sex][covariate_name]
                covariate  = spline(age, time)
                average    = \
                    avg_node_sex_covariate[node_name][sex][covariate_name]
                difference = covariate - average
                effect += float( row['multiplier_truth'] ) * difference
        rate = math.exp(effect) * no_effect_rate
        return rate
    result = dict()
    for rate_name in spline_no_effect_rate :
        result[rate_name]  = lambda age, time : fun(age, time, rate_name)
    return result
# ----------------------------------------------------------------------------
def average_integrand_grid(
    integrand_step_size, age_lower, age_upper, time_lower, time_upper
) :
    #
    # age_grid
    if age_lower == age_upper :
        age_grid = [ age_lower ]
    else :
        n_age    = int( (age_upper - age_lower) / integrand_step_size) + 1
        dage     = (age_upper - age_lower) / n_age
        age_grid = [ age_lower + i * dage for i in range(n_age+1) ]
    #
    # time_grid
    if time_lower == time_upper :
        time_grid = [ time_lower ]
    else :
        n_time    = int( (time_upper - time_lower) / integrand_step_size) + 1
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
        'no_effect_rate',
        'simulate',
    ]
    for name in input_list :
        file_name         = f'{csv_dir}/{name}.csv'
        input_table[name] = at_cascade.read_csv_table(file_name)
    #
    # option_value
    option_value = option_table2dict(csv_dir, input_table['option'] )
    #
    # node2parent
    node2parent = node_table2dict( input_table['node'] )
    #
    # spline_node_sex_cov
    node_set = set( node2parent.keys() )
    spline_node_sex_cov = get_spline_node_sex_cov(
        input_table['covariate'], node_set
    )
    #
    # covariate_name_list
    covariate_name_list = list()
    for key in input_table['covariate'][0].keys() :
        if key not in [ 'node_name', 'sex', 'age', 'time', 'omega' ] :
            covariate_name_list.append(key)
    #
    # avg_node_sex_covariate, covariate_avg_table
    avg_node_sex_covariate, covariate_avg_table = get_covariate_avg_table(
        input_table['covariate'] , covariate_name_list
    )
    #
    # spline_no_effect_rate
    spline_no_effect_rate = get_spline_no_effect_rate(
        input_table['no_effect_rate']
    )
    #
    # random_effect_node_rate
    std_random_effects  = option_value['std_random_effects']
    random_effect_node_rate  = dict()
    for node_name in node2parent :
        random_effect_node_rate[node_name] = dict()
        for rate_name in spline_no_effect_rate :
            random_effect_node_rate[node_name][rate_name] = random.gauss(
                0.0, std_random_effects
            )
    #
    # multiplier_list_rate
    multiplier_list_rate = get_multiplier_list_rate(
        input_table['multiplier_sim']
    )
    #
    # data_sim_table
    data_sim_table = list()
    for (simulate_id, row_sim) in enumerate( input_table['simulate'] ) :
        line_nmber = simulate_id + 1
        #
        # simulate_id
        if simulate_id != int( row_sim['simulate_id'] ) :
            msg  = f'csv_interface: Error at line {line_number} '
            msg += f' in simulate.csv\n'
            msg += f'simulate_id = ' + row_sim['simulate_id']
            msg += ' is not equal line number minus one'
            assert False, msg
        #
        # integrand_name
        integrand_name = row_sim['integrand_name']
        if integrand_name not in valid_integrand_name :
            msg  = f'csv_interface: Error at line {line_number} '
            msg += f' in simulate.csv\n'
            msg += f'integrand_name = ' + integrand_name
            msg += ' is not a valid integrand name'
            assert False, msg
        #
        # node_name
        node_name = row_sim['node_name']
        if node_name not in node_set :
            msg  = f'csv_interface: Error at line {line_number} '
            msg += f' in simulate.csv\n'
            msg += f'node_name = ' + node_name
            msg += ' is not in node.csv'
            assert False, msg
        #
        # sex
        sex = row_sim['sex']
        if sex not in [ 'male', 'female', 'both' ] :
            msg  = f'csv_interface: Error at line {line_number} '
            msg += f' in simulate.csv\n'
            msg += f'sex = ' + sex
            msg += ' is not male, feamle, or both'
            assert False, msg
        #
        # age_lower, age_upper, time_lower, time_upper
        age_lower  = float( row_sim['age_lower'] )
        age_upper  = float( row_sim['age_upper'] )
        time_lower = float( row_sim['time_lower'] )
        time_upper = float( row_sim['time_upper'] )
        #
        #
        # age_mid, time_mid
        age_mid  = ( age_lower  + age_upper )  / 2.0
        time_mid = ( time_lower + time_upper ) / 2.0
        #
        # covariate_value_list
        covariate_value_list = list()
        for (index, covariate_name) in enumerate( covariate_name_list ) :
            spline = spline_node_sex_cov[node_name][sex][covariate_name]
            value  =  spline(age_mid, time_mid)
            covariate_value_list.append(value )
        #
        # row_data
        row_data = dict( zip(covariate_name_list, covariate_value_list) )
        row_data['simulate_id'] = simulate_id
        #
        # rate_fun_dict
        rate_fun_dict = average_integrand_rate(
            node2parent             ,
            spline_no_effect_rate   ,
            random_effect_node_rate ,
            covariate_name_list     ,
            spline_node_sex_cov     ,
            avg_node_sex_covariate  ,
            multiplier_list_rate    ,
            node_name               ,
            sex
        )
        #
        # grid
        integrand_step_size = option_value['integrand_step_size']
        grid = average_integrand_grid(
            integrand_step_size, age_lower, age_upper, time_lower, time_upper
        )
        #
        # avg_integrand
        abs_tol = 1e-5
        avg_integrand = dismod_at.average_integrand(
            rate_fun_dict, integrand_name, grid, abs_tol
        )
        #
        # row_data['meas_mean']
        meas_mean             = avg_integrand
        row_data['meas_mean'] = meas_mean
        #
        # row_data['meas_std']
        percent_cv           = float( row_sim['percent_cv'] )
        meas_std             = percent_cv * meas_mean / 100.0
        row_data['meas_std'] = meas_std
        #
        # row_data['meas_value']
        meas_noise             = random.gauss(meas_mean, meas_std )
        meas_value             = meas_mean + meas_noise
        meas_value             = max(meas_value, 0.0)
        row_data['meas_value'] = meas_value
        #
        # data_sim_table
        data_sim_table.append( row_data )
    #
    # data.csv
    file_name = f'{csv_dir}/data_sim.csv'
    at_cascade.write_csv_table(file_name, data_sim_table)
    #
    # covariate_avg.csv
    file_name = f'{csv_dir}/covariate_avg.csv'
    at_cascade.write_csv_table(file_name, covariate_avg_table)
