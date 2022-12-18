# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
import os
import sys
import time
import shutil
# import at_cascade with a preference current directory version
current_directory = os.getcwd()
if os.path.isfile( current_directory + '/at_cascade/__init__.py' ) :
   sys.path.insert(0, current_directory)
import at_cascade
"""
{xrst_begin csv_sim_and_fit}
{xrst_spell
   Sincidence
   dage
   dtime
   iter
   meas
   std
}

Example Simulating and Fitting Incidence From Prevalence Data
#############################################################

Shock in Incidence
******************
This example demonstrates inverting for a shock in true incidence (iota)
from just prevalence measurements.
To be specific, iota is constant and equal to 0.01
except for ages between 40 and 60 and times between 1990 and 2000.
During that special age time period, iota is equal to 0.1.

Covariates
**********
There are no covariates in this example.

#. The covariate.csv file does not have any
   :ref:`csv_simulate@Input Files@covariate.csv@covariate_name` columns
   and is only used to set the value of omega and the covariate
   age time grid.

#. The :ref:`csv_simulate@Input Files@multiplier_sim.csv` file is empty; i.e.,
   it only has a header row.

Age Time Grid
*************
This example uses the age-time grid below for the
covariates, the data, and the iota rate.
The omega and chi rates are constant and hence they
are only specified at one age, time point.

age-grid
   0, 20, 35, 40, 45, 50, 55, 60, 65, 80, 100:
   Note that this is the union to two grids, one at a 20 year
   spacing and the other at 5 year spacing.
   The dage standard deviations priors are the same all grid points
   so a closer spacing allows for more change per year.

time-grid
   1980, 1988, 1990, 1992, 1994, 1996, 1998, 2000, 2002, 2010, 2020
   Note that this is the union to two grids, one at a 10 year
   spacing and the other at 2 year spacing.
   The dtime standard deviations priors are the same all time points
   so a closer spacing allows for more change per year.


Node Tree
*********
The node tree set by  :ref:`csv_simulate@Input Files@node.csv` is

::

                n0
          /-----/\-----\
        n1              n2

True Rates
**********
The true rates are the rate values used to simulate the data.
For this example, the true value for other case mortality (omega) is 0.01
and for excess mortality (chi) is 0.1.

n0
==
The incidence rate (iota) depends on the node.
The true value for node n0 as a function of age (a) and time (t) is

.. math::

   \iota_0 (a, t) = \begin{cases}
      0.1   & \R{if} \; a \in (40, 60) \; t \in (1990, 2000) \\
      0.01  & \R{otherwise}
   \end{cases}

There are no covariates and n0 is the root node,
hence this is the same as the rates in the
:ref:`csv_simulate@Input Files@no_effect_rate.csv` file.

Random Effects
==============
The random effect (e) depends on the node (but not sex).
Given a node,
the true value of iota at age (a) and time (t) is

.. math::

      \exp( e ) \iota_0 (a, t)

The value :ref:`csv_simulate@Input Files@option_sim.csv@std_random_effects`
specifies the corresponding standard deviation.
The simulated random effects are reported in
:ref:`csv_simulate@Output Files@random_effect.csv`.
Note that there are no random effects for node n0 (the root node).

Simulated Data
**************
There is a simulated data point for each of the following cases:
see the setting of :ref:`csv_simulate@Input Files@simulate.csv`:

#. For integrand_name equal to Sincidence and prevalence.
#. For node_name equal to n0, n1, and n2.
#. For sex equal to female and male.
#. For each age in the age-grid and each time in the time-grid.

Fit
***

option_fit.csv
==============
#. *refit_split* is set to false because the model does not
   depend on sex.
#. It seems that *quasi_fixed* runs to a better solution and faster
   when it is true.  A larger value for *max_num_iter_fixed*
   to is required for to converge for *quasi_fixed* true.
   (This calls for more investigation.)

fit_goal.csv
============
This was set to n1 and n2 so that all the nodes, n0, n1, and n2 are fit.
Fitting n0 takes most of the time because it has random effects.
The four cases n1, n2 for female, male fit in parallel and are
very fast because there are not random effects at that level.

parent_rate.csv
===============
#. The rate chi is constrained to be constant and equal to its true value.
   Note that omega is constrained to its ture value by its value
   in the covariate.csv file.
#. The prior for iota is specified on the age-time grid.
   At each grid point it has a uniform prior with a small positive
   lower limit and upper limit of one.
   The mean is constant and equal to 0.02 which
   is between its true inside the spike (0.1) and outside the spike (0.01).
   This mean is only used to initialize the optimization.

data_in.csv
===========
The data used during the fit is the same as the simulated data
with the following exceptions:

#. The :ref:`csv_simulate@Output Files@data_sim.csv@meas_mean`
   is used for the measurement value during the fit; i.e.,
   :ref:`csv_fit@Input Files@data_in.csv@meas_value` .
   In addition, :ref:`csv_fit@Input Files@data_in.csv@meas_std`
   is set to a small value.
   Not having any noise in the measurement, and a small standard deviation,
   yields the effect of a much larger data set without long running times.

#. The Sincidence data is held out, so only prevalence is included
   during the fit. Since both Sincidence and prevalence are using the
   true value, the fit residuals are difference from truth, not data.
   The weighted residuals can be multiplied by the
   meas_std to get the actual residuals.


Automated Correctness Test
**************************
We define inside_shock (outside_shock) to be when a grid point is not a
neighbor of the shock boundary and is inside (outside) the shock.
The shock boundary is the square formed by the following four (age, time)
pairs::

   (60, 1990)            (60, 2000)
      -----------------------
      |a                    |
      |g                    |
      |e                    |
      |        time         |
      -----------------------
   (40, 1990)            (40, 2000)

The automated correctness test checks the
minimum, maximum and average value for the
inside_shock and outside_shock grid points.
Note that the smoothing prior causes the height of the shock
to be underestimated (the prior is for there to be no shock).

Source Code
***********
{xrst_literal
   BEGIN_PYTHON
   END_PYTHON
}

{xrst_end csv_sim_and_fit}
"""
# BEGIN_PYTHON
# --------------------------------------------------------------------------
#
# random_seed
random_seed = str( int( time.time() ) )
#
# age_grid, time_grid
age_set   = set( range(0, 120, 20) )     | set( range(35, 70, 5) )
time_set  = set( range(1980, 2030, 10) ) | set( range(1988, 2004, 2) )
age_grid  = sorted( list( age_set ) )
time_grid = sorted( list( time_set) )
#
# rate_truth
def rate_truth(rate_name, age, time) :
   if rate_name == 'omega' :
      return 0.01
   if rate_name == 'chi' :
      return 0.1
   if 40.0 < age and age < 60.0 and  1990 < time  and time < 2000 :
      return 0.1
   else :
      return 0.01
#
# ----------------------------------------------------------------------------
# simulation files
# ----------------------------------------------------------------------------
#
# sim_file
sim_file = dict()
#
# option_sim.csv
random_seed = str( int( time.time() ) )
sim_file['option_sim.csv'] = \
'''name,value
absolute_tolerance,1e-5
float_precision,4
integrand_step_size,5
random_depend_sex,false
std_random_effects,.2
'''
sim_file['option_sim.csv'] += f'random_seed,{random_seed}\n'
#
# node.csv
sim_file['node.csv'] = \
'''node_name,parent_name
n0,
n1,n0
n2,n0
'''
#
# covariate.csv
omega = rate_truth('omega', 0, 0)
sim_file['covariate.csv'] = 'node_name,sex,age,time,omega\n'
for node_name in [ 'n0', 'n1', 'n2' ] :
   for sex in [ 'female', 'male' ] :
      for age in age_grid :
         for time in time_grid :
            row = f'{node_name},{sex},{age},{time},{omega}\n'
            sim_file['covariate.csv'] += row
#
# no_effect_rate.csv
chi = rate_truth('chi', 0, 0)
sim_file['no_effect_rate.csv'] = 'rate_name,age,time,rate_truth\n'
sim_file['no_effect_rate.csv'] += f'chi,0,0,{chi}\n'
for age in age_grid :
   for time in time_grid :
      iota = rate_truth('iota', age, time)
      sim_file['no_effect_rate.csv'] += f'iota,{age},{time},{iota}\n'
#
# multiplier_sim.csv
sim_file['multiplier_sim.csv'] = \
'multiplier_id,rate_name,covariate_or_sex,multiplier_truth\n'
#
# simulate.csv
header  = 'simulate_id,integrand_name,node_name,sex,age_lower,age_upper,'
header += 'time_lower,time_upper,percent_cv\n'
sim_file['simulate.csv'] = header
simulate_id     = -1
percent_cv      = 5.0
for integrand_name in [ 'Sincidence', 'prevalence' ] :
   for node_name in [ 'n0', 'n1', 'n2' ] :
      for sex in [ 'female', 'male' ] :
         for age in age_grid :
            for time in time_grid :
               simulate_id += 1
               row  = f'{simulate_id},{integrand_name},{node_name},{sex},'
               row += f'{age},{age},{time},{time},{percent_cv}\n'
               sim_file['simulate.csv'] += row
# ----------------------------------------------------------------------------
# fit files
# ----------------------------------------------------------------------------
#
# fit_file
fit_file = dict()
#
# option_fit.csv
fit_file['option_fit.csv']  =  \
'''name,value
refit_split,false
quasi_fixed,true
max_num_iter_fixed,300
plot,true
db2csv,true
'''
fit_file['option_fit.csv'] += f'random_seed,{random_seed}\n'
#
# fit_goal.csv
fit_file['fit_goal.csv'] = \
'''node_name
n1
n2
'''
#
# predict_integrand.csv
fit_file['predict_integrand.csv'] = \
'''integrand_name
Sincidence
prevalence
'''
#
# prior.csv
fit_file['prior.csv'] = \
'''name,density,mean,std,eta,lower,upper
uniform_eps_1,uniform,0.02,,,1e-6,1.0
delta_prior,log_gaussian,0.0,0.05,1e-4,,
random_prior,gaussian,0.0,0.2,,,,
'''
#
# child_rate.csv
fit_file['child_rate.csv'] = \
'''rate_name,value_prior
iota,random_prior
'''
#
# mulcov.csv
fit_file['mulcov.csv'] = 'covariate,type,effected,value_prior,const_value\n'
#
#
# -----------------------------------------------------------------------------
# sim
def sim(sim_dir) :
   #
   # write input csv files
   for name in sim_file :
      file_name = f'{sim_dir}/{name}'
      file_ptr  = open(file_name, 'w')
      file_ptr.write( sim_file[name] )
      file_ptr.close()
   #
   # csv.simulate
   at_cascade.csv.simulate(sim_dir)
   #
   # data_join.csv
   at_cascade.csv.join_file(
      left_file   = f'{sim_dir}/simulate.csv' ,
      right_file  = f'{sim_dir}/data_sim.csv' ,
      result_file = f'{sim_dir}/data_join.csv'     ,
   )
# -----------------------------------------------------------------------------
# fit
def fit(sim_dir, fit_dir) :
   #
   # node.csv, covarite.csv
   for file_name in [ 'node.csv', 'covariate.csv' ] :
      shutil.copyfile(
         src = f'{sim_dir}/{file_name}' ,
         dst = f'{fit_dir}/{file_name}' ,
      )
   #
   # fit_file['parent_rate.csv']
   chi   = rate_truth('chi', 0, 0)
   data  = 'rate_name,age,time,value_prior,dage_prior,dtime_prior,const_value\n'
   data  += f'chi,0.0,0.0,,,,{chi}\n'
   for age in age_grid :
      for time in time_grid :
         data  += f'iota,{age},{time},uniform_eps_1,delta_prior,delta_prior,\n'
   fit_file['parent_rate.csv'] = data
   #
   # csv files in fit_file
   for name in fit_file :
      file_name = f'{fit_dir}/{name}'
      file_ptr  = open(file_name, 'w')
      file_ptr.write( fit_file[name] )
      file_ptr.close()
   #
   # data_join_table
   # This is a join of simulate.csv and dats_sim.csv
   data_join_table = at_cascade.csv.read_table(
      file_name = f'{sim_dir}/data_join.csv'
   )
   #
   # data_in.csv
   table = list()
   for row_join in data_join_table :
      #
      # row_in
      row_in = dict()
      copy_list  = [ 'integrand_name', 'node_name', 'sex' ]
      copy_list += [ 'age_lower', 'age_upper', 'time_lower', 'time_upper' ]
      row_in['data_id']   = row_join['simulate_id']
      for key in copy_list :
         row_in[key] = row_join[key]
      row_in['meas_value'] = row_join['meas_mean']
      row_in['meas_std']   = 1e-3
      if row_join['integrand_name'] == 'Sincidence' :
         row_in['hold_out'] = '1'
      else :
         row_join['integrand_name'] == 'prevalence'
         row_in['hold_out'] = '0'
      #
      table.append( row_in )
   at_cascade.csv.write_table(
         file_name = f'{fit_dir}/data_in.csv' ,
         table     = table ,
   )
   #
   # fit
   at_cascade.csv.fit(fit_dir)
   #
   # fit_predict_table
   fit_predict_table = at_cascade.csv.read_table(
      file_name = f'{fit_dir}/fit_predict.csv'
   )
   #
   # inside_shock, outside_shock
   inside_shock  = list()
   outside_shock = list()
   for row in fit_predict_table :
      match = True
      match = match and row['node_name'] == 'n0'
      match = match and row['sex'] == 'both'
      match = match and row['integrand_name'] == 'Sincidence'
      if match :
         #
         # age, time, iota
         age   = float( row['age'] )
         time  = float( row['time'] )
         iota  = float( row['avg_integrand'] )
         #
         # inside_shock
         inside = 1992 <= time and time <= 1998
         inside = inside and 45 <= age and age <= 55
         if inside :
            inside_shock.append(iota)
         #
         # outside_shock
         outside = time < 1990 <= time and time <= 1998
         outside = outside or age < 40 or 60 < age
         if outside :
            outside_shock.append(iota)
   #
   # inside_shock
   avg =  sum(inside_shock) / len(inside_shock)
   #
   if min(inside_shock) <= 0.03 :
      print('min inside_shock =',  min(inside_shock) )
   assert 0.03 < min(inside_shock)
   #
   if 0.15 <= max(inside_shock) :
      print('max inside_shock =',  max(inside_shock) )
   assert max(inside_shock) < 0.15
   #
   if avg <= 0.07 or 0.1 <= avg :
      print('avg inside_shock =',  avg )
   assert 0.07 < avg and avg < 0.1
   #
   # outside_shock
   avg =  sum(outside_shock) / len(outside_shock)
   #
   if min(outside_shock) <= 0.001 :
      print('min outside_shock =',  min(outside_shock) )
   assert 0.001 < min(outside_shock)
   #
   if 0.02 <= max(outside_shock) :
      print('max outside_shock =',  max(outside_shock) )
   assert max(outside_shock) < 0.02
   #
   if avg <= 0.009 or 0.012 <= avg :
      print('avg outside_shock =',  avg )
   assert 0.009 < avg and avg < 0.012

# -----------------------------------------------------------------------------
# Without this, the mac will try to execute main on each processor.
if __name__ == '__main__' :
   #
   # sim_dir
   sim_dir = 'build/example/csv/sim'
   if not os.path.exists(sim_dir) :
      os.makedirs(sim_dir)
   #
   # clear out a previous run
   if os.path.exists( 'build/example/csv/fit/n0' ) :
      shutil.rmtree( 'build/example/csv/fit/n0' )
   #
   # fit_dir
   fit_dir = 'build/example/csv/fit'
   if not os.path.exists(fit_dir) :
      os.mkdir(fit_dir)
   #
   # sim
   sim(sim_dir)
   #
   # fit
   fit(sim_dir, fit_dir)
   #
   print('csv_sim_and_fit: OK')
   sys.exit(0)
# END_PYTHON
