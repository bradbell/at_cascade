# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-25 Bradley M. Bell
# ----------------------------------------------------------------------------
r'''
{xrst_begin create_shift_db}
{xrst_spell
  dage
  dtime
  var
  std
  delim
}

Create Database With Shifted Covariate References
#################################################

Prototype
*********
{xrst_literal
   # BEGIN_DEF
   # END_DEF
}

Problem
*******
The value and difference priors are treated as independent.
Currently the standard deviations for the difference priors are fixed
at their value for the root level.
In addition, the standard deviations for the value priors are set
using the posterior samples predicted by the parent job fit.
The theory section below discusses the problem with this.
The following options provide a way to avoid this problem:
:ref:`csv.fit@Input Files@option_fit.csv@child_prior_dage` ,
:ref:`csv.fit@Input Files@option_fit.csv@child_prior_dtime` ,
:ref:`option_all_table@shift_prior_dage` ,
:ref:`option_all_table@shift_prior_dtime` .

Theory
******
For this discussion we start our indexing at one
(recall that python starts its indexing at zero).
Suppose that there is only on rate; e.g. iota,
no data, and all the priors are Gaussian.
We use the following notation for the rate's prior:
(The :ref:`fit_info_theory-name` page has a more general discussion
of the analysis below.)

.. csv-table::
   :header-rows: 1
   :delim: ;

   Notation; Meaning
   :math:`r_{i,j}` ; value of the rate at the i-th age and j-th time
   :math:`N`       ; number of age points in the rate grid
   :math:`M`       ; number of time points in the rate grid
   :math:`m_v`     ; mean for the rate values
   :math:`m_a`     ; mean for the rate age differences
   :math:`m_t`     ; mean for the rate time values
   :math:`s_v`     ; standard deviation (std) of the value prior for the rate
   :math:`s_a`     ; std of the age difference prior for the rate
   :math:`s_t`     ; std of the time difference prior for the rate
   :math:`L(r)`    ; the negative log-likelihood

Note that the means and standard deviations actually depend on
the age and time indices (i,j).
We have dropped these indices because they can be inferred from the (i,j)
indices of :math:`r` .

.. math::

   2 L(r) = &
      + \sum_{i,j}
      \left( \frac{ r_{i,j} - m_v } { s_v } \right)^2
      - \log ( 2 \pi s_v^2 )
   \\ &
      + \sum_{i < N , j}
      \left( \frac{ r_{i+1,j} - r_{i,j} - m_a } { s_a } \right)^2
      - \log ( 2 \pi s_a^2 )
   \\ &
      + \sum_{i, j < M}
      \left( \frac{ r_{i,j+1} - r_{i,j} - m_t } { s_t } \right)^2
      - \log ( 2 \pi s_t^2 )

The partial of :math:`L(r)` with respect to :math:`r_{N,M}` is

.. math::

   \frac{ \partial L}{\partial r_{N,M}}
   =
   \frac{ r_{N,M} - m_v } { s_v^2 }
   +
   \frac{ r_{N,M} - r_{N-1,M} - m_a } { s_a^2 }
   +
   \frac{ r_{N,M} - r_{N,M-1} - m_t } { s_t^2 }

The second partial of :math:`L(r)` with respect to :math:`r_{N,M}` is

.. math::

   \frac{ \partial^2 L}{\partial r_{N,M} \partial r_{N,M} }
   =
   s_v^{-2} + s_a^{-2} + s_t^{-2}

The inverse of the Hessian is the covariance matrix for the
estimate of :math:`r` .
Suppose that we want the standard deviation for :math:`r_{N,M}` to be
:math:`\sigma` .
If we approximation the diagonal of the inverse buy the inverse
of the diagonal, it follows that

.. math::

   \sigma^2    & = \left( s_v^{-2} + s_a^{-2} + s_t^{-2} \right)^{-1}
   \\
   \sigma^{-2} & =  s_v^{-2} + s_a^{-2} + s_t^{-2}


all_node_database
*****************
is a python string containing the name of the :ref:`all_node_db-name`.

fit_database
************
is a python string containing the name of a dismod_at database.
This is a :ref:`glossary@fit_database` which
has two predict tables (mentioned below).
These tables are used to create priors in the child node databases.
This argument can't be ``None``.

fit_node
========
We use *fit_node* to refer to the parent node in the
dismod_at option table in the *fit_database*.

sample Table
============
This table is not used if *no_ode_fit* is true.
If *no_ode_fit* is false,
it  contains the results of a dismod_at sample command
for both the fixed and random effects.

c_shift_avgint Table
====================
This is the :ref:`avgint_parent_grid-name` table corresponding
to this fit_database.

c_shift_predict_sample Table
============================
This table is not used if *no_ode_fit* is true.
If *no_ode_fit* is false, it contains the predict table corresponding to a
predict sample command using the c_shift_avgint table.
Note that the predict_id column name was changed to c_shift_predict_sample_id
(which is not the same as sample_id).

c_shift_predict_fit_var Table
=============================
This table contains the predict table corresponding to a
predict fit_var command using the c_shift_avgint table.
Note that the predict_id column name was changed to c_shift_predict_fit_var_id
(which is not the same as var_id).

shift_databases
***************
We use the notation *shift_name* for the keys in this ``dict``.

shift_name
==========
For each *shift_name*, *shift_databases[shift_name]* is the name of
a :ref:`glossary@input_node_database` that is created by this command.
The corresponding directory is assumed to already exist.

split_reference_name
====================
If *shift_name* is a :ref:`split_reference_table@split_reference_name`,
the node corresponding to this shift database is the fit_node.

Child Node
==========
If *shift_name* is the node name for a child of fit_node,
the child is the node corresponding to this shift database.

Fit Node
========
If *shift_name* is the name of the *fit_node*,
the node corresponding to this shift database is the fit_node.
This case is used by :ref:`no_ode_fit-name` to create priors without shifting
the covariate references.

Value Priors
============
If the upper and lower limits are equal,
the value priors in fit_database and the shift_databases
are effectively the same.
Otherwise the mean in the value priors
are replaced using the corresponding values in the
predict tables in the *fit_database*.
If *no_ode_fit* is true (false),
the standard deviations in the value priors are not replaced (are replaced).
Note that if the value prior is uniform,
the standard deviation is not used and the mean is only used to
initialize the optimization.

dage and dtime Priors
=====================
The mean of the dage and dtime priors
are replaced using the corresponding difference in the
predict tables in the *fit_database*.

Log Table
=========
There is no log table in the shifted databases.

no_ode_fit
**********
If this argument is true (false) if the *fit_database*
is (is not) the result of a :ref:`no_ode_fit-name` .
If *no_ode_fit* is false,
the sample table and the c_shift_predict_sample
table must be in the *fit_database*.
In this case both the means and standard deviations in the value priors
are replaced using the results of the fit.
Otherwise, only the means are replaced.

job_table
*********
If *no_ode_fit* is true this argument must be None.
Otherwise it is the :ref:`create_job_table@job_table` for this cascade.

{xrst_end create_shift_db}
'''
# ----------------------------------------------------------------------------
import os
import math
import copy
import shutil
import numpy
import dismod_at
import at_cascade
# ----------------------------------------------------------------------------
# cov_reference_list =
def get_cov_reference_list(
   n_covariate, cov_reference_table, node_id, split_reference_id
) :
   #
   #
   cov_reference_list = n_covariate * [None]
   for row in cov_reference_table :
      if row['node_id'] == node_id :
         if row['split_reference_id'] == split_reference_id :
            covariate_id = row['covariate_id']
            if covariate_id < len(cov_reference_list) :
               cov_reference_list[covariate_id] = row['reference_value']
   if None in cov_reference_list :
      covariate_id = cov_reference_list.index(None)
      msg  = 'all_node database: cov_reference table: '
      msg += 'No row has the following values:\n'
      msg += f'node_id = {node_id}, '
      msg += f'split_reference_id = {split_reference_id}, '
      msg += f'covariate_id = {covariate_id}'
      assert False, msg
   #
   return cov_reference_list
# ----------------------------------------------------------------------------
def add_index_to_name(table, name_col) :
   row   = table[-1]
   name  = row[name_col]
   ch    = name[-1]
   while name != '' and name[-1] in '0123456789' :
      name = name[: -1]
   if name[-1] == '_' :
      name = name[: -1]
   row[name_col] = name + '_' + str( len(table) )
# ---------------------------------------------------------------------------
def get_age_id_next_list(smooth_table, smooth_grid_table, age_table ) :
   #
   # age_id_set
   age_id_set  = dict()
   for row in smooth_grid_table :
      smooth_id = row['smooth_id']
      age_id    = row['age_id']
      time_id   = row['time_id']
      if smooth_id not in age_id_set :
         age_id_set[smooth_id]  = set()
      age_id_set[smooth_id].add(age_id)
   #
   # age_id_key, time_id_key
   age_id_key  = lambda age_id :  age_table[age_id]['age']
   #
   # age_id_next_list
   age_id_next_list  = list()
   for smooth_id in range( len(smooth_table) ) :
      n_age        = smooth_table[smooth_id]['n_age']
      age_id_list  = sorted(age_id_set[smooth_id], key = age_id_key )
      assert n_age == len(age_id_list)
      age_id_dict  = dict()
      for i in range(n_age) :
         age_id  = age_id_list[i]
         if i + 1 < n_age :
            next_age_id = age_id_list[i+1]
         else :
            next_age_id = None
         age_id_dict[age_id] = next_age_id
      age_id_next_list.append( age_id_dict )
   return age_id_next_list
# ---------------------------------------------------------------------------
def get_time_id_next_list(smooth_table, smooth_grid_table, time_table ) :
   #
   # time_id_set
   time_id_set  = dict()
   for row in smooth_grid_table :
      smooth_id = row['smooth_id']
      time_id    = row['time_id']
      time_id   = row['time_id']
      if smooth_id not in time_id_set :
         time_id_set[smooth_id]  = set()
      time_id_set[smooth_id].add(time_id)
   #
   # time_id_key, time_id_key
   time_id_key  = lambda time_id :  time_table[time_id]['time']
   #
   # time_id_next_list
   time_id_next_list  = list()
   for smooth_id in range( len(smooth_table) ) :
      n_time        = smooth_table[smooth_id]['n_time']
      time_id_list  = sorted(time_id_set[smooth_id], key = time_id_key )
      assert n_time == len(time_id_list)
      time_id_dict  = dict()
      for i in range(n_time) :
         time_id  = time_id_list[i]
         if i + 1 < n_time :
            next_time_id = time_id_list[i+1]
         else :
            next_time_id = None
         time_id_dict[time_id] = next_time_id
      time_id_next_list.append( time_id_dict )
   return time_id_next_list
# ----------------------------------------------------------------------------
# The smoothing for the new shift_table['smooth_grid'] row is the most
# recent smoothing added to shift_table['smooth']; i.e., its smoothing_id
# is len( shift_table['smooth'] ) - 1.
def add_shift_grid_row(
   fit_fit_var,
   fit_sample,
   fit_table,
   shift_table,
   fit_grid_row,
   integrand_id,
   shift_node_id,
   shift_split_reference_id,
   shift_prior_std_factor,
   shift_prior_dage,
   shift_prior_dtime,
   freeze,
   copy_row,
   age_id_next,
   time_id_next,
) :
   assert freeze in { 'prior', 'mean', 'no' }
   if freeze == 'prior' :
      assert copy_row == True
   # -----------------------------------------------------------------------
   # value_prior
   # -----------------------------------------------------------------------
   #
   # split_id
   split_id = shift_split_reference_id
   #
   # fit_prior_id
   fit_prior_id    = fit_grid_row['value_prior_id']
   #
   # shift_const_value
   # shift_value_prior_id
   shift_const_value     = fit_grid_row['const_value']
   shift_value_prior_id  = None
   dage_fit_var          = None
   dtime_fit_var         = None
   if shift_const_value is None :
      #
      # fit_prior_row
      fit_prior_row = fit_table['prior'][fit_prior_id]
      #
      # key
      age_id    = fit_grid_row['age_id']
      time_id   = fit_grid_row['time_id']
      key       = (integrand_id, shift_node_id, split_id, age_id, time_id)
      #
      # lower, upper
      if freeze == 'mean' :
         lower = fit_fit_var[key]
         upper = fit_fit_var[key]
      else :
         lower = fit_prior_row['lower']
         upper = fit_prior_row['upper']
      if lower is None :
         lower = - math.inf
      if upper is None :
         upper = + math.inf
      #
      # shift_const_value, shift_value_prior_id, shift_table['prior']
      if lower == upper :
         shift_const_value  = lower
         assert shift_value_prior_id is None
      else :
         assert shift_const_value is None
         #
         # shift_value_prior_id, shift_prior_row
         shift_value_prior_id  = len( shift_table['prior'] )
         shift_prior_row = copy.copy( fit_prior_row )
         if not copy_row :
            #
            # fit_var, dage_fit_var, dtime_fit_var
            fit_var = fit_fit_var[key]
            if age_id_next[age_id] != None :
               next_age_id = age_id_next[age_id]
               key = (
                  integrand_id, shift_node_id, split_id, next_age_id, time_id
               )
               dage_fit_var = fit_fit_var[key] - fit_var
            if time_id_next[time_id] != None :
               next_time_id = time_id_next[time_id]
               key = (
                  integrand_id, shift_node_id, split_id, age_id, next_time_id
               )
               dtime_fit_var = fit_fit_var[key] - fit_var
            #
            # shift_prior_row['mean']
            mean                     = fit_var
            mean                     = min(mean, upper)
            mean                     = max(mean, lower)
            shift_prior_row['mean']  = mean
            #
            # if no_ode_fit then len(fit_sample) is zero
            if len(fit_sample) > 0 :
               #
               # std
               eta        = fit_prior_row['eta']
               if eta is None :
                  std  = numpy.std(fit_sample[key], mean=mean)
               else:
                  # There is a log trasnformation of this variable before
                  # passing it to cppad_mixed. Hence its value are gaussian
                  # in log space.
                  #
                  # log_sample
                  log_sample = list()
                  for sample in fit_sample[key] :
                     sample = max( - eta / 5.0 , sample )
                     log_sample.append( math.log( sample + eta ) )
                  #
                  # log_std
                  log_mean = math.log(mean + eta)
                  log_std  = numpy.std(log_sample, mean = log_mean, ddof = 0)
                  #
                  # inverse log transformation
                  std      = (math.exp(log_std) - 1) * (mean + eta)
               #
               # shift_prior_row['std']
               shift_prior_row['std']         = shift_prior_std_factor * std
         #
         # shift_table['prior']
         shift_table['prior'].append( shift_prior_row )
         add_index_to_name( shift_table['prior'], 'prior_name' )
   # -----------------------------------------------------------------------
   # dage_prior
   # -----------------------------------------------------------------------
   if not shift_prior_dage :
      shift_dage_prior_id = None
   else :
      fit_prior_id       = fit_grid_row['dage_prior_id']
      if fit_prior_id == None :
         shift_dage_prior_id = None
      else :
         fit_prior_row      = fit_table['prior'][fit_prior_id]
         shift_prior_row    = copy.copy( fit_prior_row )
         if dage_fit_var is not None :
            mean = dage_fit_var
            if shift_prior_row['lower'] != None :
               if mean < shift_prior_row['lower']  :
                  mean = shift_prior_row['lower']
            if shift_prior_row['upper'] != None :
               if shift_prior_row['lower'] < mean :
                  mean = shift_prior_row['upper']
            shift_prior_row['mean'] = mean
         shift_dage_prior_id  = len( shift_table['prior'] )
         shift_table['prior'].append( shift_prior_row )
         add_index_to_name( shift_table['prior'], 'prior_name' )
   # -----------------------------------------------------------------------
   # dtime_prior
   # -----------------------------------------------------------------------
   if not shift_prior_dtime :
      shift_dtime_prior_id = None
   else :
      fit_prior_id       = fit_grid_row['dtime_prior_id']
      if fit_prior_id == None :
         shift_dtime_prior_id = None
      else :
         fit_prior_row       = fit_table['prior'][fit_prior_id]
         shift_prior_row       = copy.copy( fit_prior_row )
         shift_dtime_prior_id  = len( shift_table['prior'] )
         if dtime_fit_var is not None :
            mean = dtime_fit_var
            if shift_prior_row['lower'] != None :
               if mean < shift_prior_row['lower']  :
                  mean = shift_prior_row['lower']
            if shift_prior_row['upper'] != None :
               if shift_prior_row['lower'] < mean :
                  mean = shift_prior_row['upper']
            shift_prior_row['mean'] = mean
         shift_table['prior'].append( shift_prior_row )
         add_index_to_name( shift_table['prior'], 'prior_name' )
   # -----------------------------------------------------------------------
   # shift_grid_row
   shift_grid_row = copy.copy( fit_grid_row )
   shift_grid_row['value_prior_id']  = shift_value_prior_id
   shift_grid_row['const_value']     = shift_const_value
   shift_grid_row['dage_prior_id']   = shift_dage_prior_id
   shift_grid_row['dtime_prior_id']  = shift_dtime_prior_id
   #
   # shift_table['smooth_grid']
   shift_grid_row['smooth_id']  = len( shift_table['smooth'] ) - 1
   shift_table['smooth_grid'].append( shift_grid_row )
# ----------------------------------------------------------------------------
# BEGIN_DEF
# at_cascade.create_shift_db
def create_shift_db(
   all_node_database    ,
   fit_database         ,
   shift_databases      ,
   no_ode_fit           = False,
   job_table            = None,
) :
   assert type(all_node_database) == str
   assert type(fit_database) == str
   assert type(shift_databases) == dict
   assert type(no_ode_fit) == bool
   if no_ode_fit :
      assert job_table == None
   else :
      assert type(job_table) == list
   # END_DEF
   #
   # predict_sample
   predict_sample = not no_ode_fit
   #
   # all_table
   connection = dismod_at.create_connection(
      all_node_database, new = False, readonly = True
   )
   all_table  = dict()
   for name in [
      'option_all',
      'split_reference',
      'mulcov_freeze',
      'cov_reference',
   ] :
      all_table[name] =  dismod_at.get_table_dict(connection, name)
   connection.close()
   #
   # root_database
   root_database      = None
   for row in all_table['option_all'] :
      if row['option_name'] == 'root_database' :
         root_database      = row['option_value']
   assert root_database != None
   #
   # shift_prior_std_factor, shift_prior_dage, shift_prior_dtime
   shift_prior_std_factor = 1.0
   shift_prior_dage       = True
   shift_prior_dtime      = True
   for row in all_table['option_all'] :
      if row['option_name'] == 'shift_prior_std_factor' :
         shift_prior_std_factor = float( row['option_value'] )
      if row['option_name'] == 'shift_prior_dage' :
         shift_prior_dage = row['option_value'].strip()
         if shift_prior_dage not in [ 'true', 'false' ] :
            msg  = f'option_all table: shift_prior_dage = {shift_prior_dage} '
            msg += 'is not true or false'
            assert False, msg
         shift_prior_dage = shift_prior_dage == 'true'
      if row['option_name'] == 'shift_prior_dtime' :
         shift_prior_dtime = row['option_value'].strip()
         if shift_prior_dtime not in [ 'true', 'false' ] :
            msg  = f'option_all table: shift_prior_dtime = {shift_prior_dtime} '
            msg += 'is not true or false'
            assert False, msg
         shift_prior_dtime = shift_prior_dtime == 'true'
   #
   # shift_prior_std_factor_mulcov
   shift_prior_std_factor_mulcov = shift_prior_std_factor
   for row in all_table['option_all'] :
      if row['option_name'] == 'shift_prior_std_factor_mulcov' :
         shift_prior_std_factor_mulcov = float( row['option_value'] )
   #
   # no_ode_ignore
   no_ode_ignore = ''
   for row in all_table['option_all'] :
      if row['option_name'] == 'no_ode_ignore' :
         no_ode_ignore = row['option_value'].strip()
   #
   # freeze_type
   freeze_type = 'mean'
   for row in all_table['option_all'] :
      if row['option_name'] == 'freeze_type' :
         freeze_type = row['option_value'].strip()
   if freeze_type not in [ 'mean', 'posterior' ] :
      msg  = f'option_all table: freeze_type = {freeze_type} '
      msg += 'is not "mean" or "posterior"'
      assert False, msg
   #
   # fit_table
   fit_or_root = at_cascade.fit_or_root_class(
      fit_database, root_database
   )
   fit_table  = dict()
   for name in [
      'age',
      'c_shift_avgint',
      'c_shift_predict_fit_var',
      'covariate',
      'density',
      'fit_var',
      'integrand',
      'mulcov',
      'node',
      'option',
      'prior',
      'rate',
      'smooth',
      'smooth_grid',
      'time',
      'var',
   ] :
      fit_table[name] = fit_or_root.get_table(name)
   if predict_sample :
      for name in [ 'c_shift_predict_sample', 'sample' ] :
         fit_table[name] = fit_or_root.get_table(name)
   fit_or_root.close()
   #
   # age_id_next_list
   age_id_next_list = get_age_id_next_list(
      fit_table['smooth'], fit_table['smooth_grid'], fit_table['age']
   )
   #
   # time_id_next_list
   time_id_next_list = get_time_id_next_list(
      fit_table['smooth'], fit_table['smooth_grid'], fit_table['time']
   )
   #
   # name_rate2integrand
   name_rate2integrand = {
      'pini'  : 'prevalence',
      'iota'  : 'Sincidence',
      'rho'   : 'remission',
      'chi'   : 'mtexcess',
   }
   #
   # fit_split_reference_id, split_covariate_id
   cov_info = at_cascade.get_cov_info(
      all_table['option_all'],
      fit_table['covariate'],
      all_table['split_reference']
   )
   if len(all_table['split_reference']) == 0 :
      fit_split_reference_id = None
      split_covaraite_id     = None
   else :
      fit_split_reference_id = cov_info['split_reference_id']
      split_covariate_id     = cov_info['split_covariate_id']
   #
   # fit_fit_var
   fit_fit_var = dict()
   for predict_row in fit_table['c_shift_predict_fit_var'] :
      avgint_id          = predict_row['avgint_id']
      avgint_row         = fit_table['c_shift_avgint'][avgint_id]
      integrand_id       = avgint_row['integrand_id']
      node_id            = avgint_row['node_id']
      age_id             = avgint_row['c_age_id']
      time_id            = avgint_row['c_time_id']
      split_id           = avgint_row['c_split_reference_id']
      key           = (integrand_id, node_id, split_id, age_id, time_id)
      assert not key in fit_fit_var
      fit_fit_var[key] = predict_row['avg_integrand']
   #
   # fit_sample
   fit_sample = dict()
   if predict_sample :
      for predict_row in fit_table['c_shift_predict_sample'] :
         avgint_id          = predict_row['avgint_id']
         avgint_row         = fit_table['c_shift_avgint'][avgint_id]
         integrand_id       = avgint_row['integrand_id']
         node_id            = avgint_row['node_id']
         age_id             = avgint_row['c_age_id']
         time_id            = avgint_row['c_time_id']
         split_id           = avgint_row['c_split_reference_id']
         key           = (integrand_id, node_id, split_id, age_id, time_id)
         if not key in fit_sample :
            fit_sample[key] = list()
         fit_sample[key].append( predict_row['avg_integrand'] )
   #
   # fit_node_name
   fit_node_name = None
   for row in fit_table['option'] :
      assert row['option_name'] != 'fit_node_id'
      if row['option_name'] == 'parent_node_name' :
         fit_node_name = row['option_value']
   assert fit_node_name is not None
   #
   # fit_node_id
   fit_node_id = at_cascade.table_name2id(
      fit_table['node'], 'node', fit_node_name
   )
   for shift_name in shift_databases :
      # ---------------------------------------------------------------------
      # create shift_databases[shift_name]
      # ---------------------------------------------------------------------
      #
      # shift_table
      shift_table = dict()
      for name in [
         'covariate',
         'mulcov',
         'option',
         'rate',
      ] :
         if name not in at_cascade.constant_table_list :
            shift_table[name] = copy.deepcopy(fit_table[name])
      shift_table['prior']       = list()
      shift_table['smooth']      = list()
      shift_table['smooth_grid'] = list()
      shift_table['nslist']      = list()
      shift_table['nslist_pair'] = list()
      #
      # shift_node_name, shift_split_reference_name
      shift_node_name            = None
      shift_split_reference_name = None
      if shift_name.find('/') < 0 :
         for row in all_table['split_reference'] :
            if row['split_reference_name'] == shift_name :
               if shift_node_name != None :
                  msg  = f'{shift_name} is both a split_reference_name '
                  msg += 'and a node_name'
                  assert False, msg
               shift_split_reference_name = shift_name
               shift_node_name            = fit_node_name
         if shift_split_reference_name == None :
            shift_node_name = shift_name
      else :
         shift_split_reference_name = shift_name.split('/')[0]
         shift_node_name            = shift_name.split('/')[1]
      #
      # shift_split_reference_id
      if shift_split_reference_name == None :
         shift_split_reference_id = fit_split_reference_id
      else :
         shift_split_reference_id = at_cascade.table_name2id(
            all_table['split_reference'],
            'split_reference',
            shift_split_reference_name
         )
      #
      # shift_node_id
      shift_node_id  = at_cascade.table_name2id(
         fit_table['node'], 'node', shift_node_name
      )
      #
      # mulcov_freeze_dict
      if no_ode_fit :
         mulcov_freeze_dict = dict()
      else :
         mulcov_freeze_dict = at_cascade.get_freeze_dict(
            fit_table['node'],
            fit_node_id,
            fit_split_reference_id,
            all_table['mulcov_freeze'],
         )
      #
      # shift_database     = fit_database
      shift_database = shift_databases[shift_name]
      shutil.copyfile(fit_database, shift_database)
      #
      # shift_table['option']
      # Set value for parent_node_name and other_database
      for row in shift_table['option'] :
         if row['option_name'] == 'parent_node_name' :
            row['option_value'] = shift_node_name
         if row['option_name'] == 'other_database' :
            if os.path.isabs( root_database ) :
               row['option_value'] = root_database
            else :
               dirname       = os.path.dirname( shift_database )
               relative_path = os.path.relpath( root_database, dirname)
               row['option_value'] = str( relative_path )
         #
      # cov_reference_list
      node_id = fit_table['node'][shift_node_id]['parent']
      assert shift_node_id == fit_node_id or node_id == fit_node_id
      n_covariate = len( fit_table['covariate'] )
      cov_reference_list = get_cov_reference_list(
         n_covariate,
         all_table['cov_reference'],
         shift_node_id,
         shift_split_reference_id
      )
      #
      # shift_table['covariate']
      # set relative covariate values so correspond to shift node
      for (covariate_id, shift_row) in enumerate(shift_table['covariate']) :
            shift_row['reference'] =  cov_reference_list[covariate_id]

      #
      # shift_table['covariate']
      # set shift covaraite value
      if shift_split_reference_id is not None :
         split_row  = all_table['split_reference'][shift_split_reference_id]
         reference  = split_row['split_reference_value']
         shift_row  = shift_table['covariate'][split_covariate_id]
         shift_row['reference'] = reference
      #
      # --------------------------------------------------------------------
      # shift_table['mulcov']
      # and corresponding entries in
      # smooth, smooth_grid, and prior
      for (mulcov_id, shift_mulcov_row) in enumerate(shift_table['mulcov']) :
         assert shift_mulcov_row['subgroup_smooth_id'] is None
         #
         # fit_smooth_id
         fit_smooth_id = shift_mulcov_row['group_smooth_id']
         if not fit_smooth_id is None :
            #
            # integrand_id
            # This is the integrand_id corresponding to this mulcov value.
            # The integrand_id that is affected by the mulcov is called
            # affected_id below.
            name         = 'mulcov_' + str(mulcov_id)
            integrand_id = at_cascade.table_name2id(
               fit_table['integrand'], 'integrand', name
            )
            #
            # smooth_row
            smooth_row = fit_table['smooth'][fit_smooth_id]
            smooth_row = copy.copy(smooth_row)
            assert smooth_row['mulstd_value_prior_id'] is None
            assert smooth_row['mulstd_dage_prior_id']  is None
            assert smooth_row['mulstd_dtime_prior_id'] is None
            #
            # shift_table['smooth'], shift_smooth_id
            shift_smooth_id = len(shift_table['smooth'])
            smooth_row['smooth_name'] += f'_{shift_smooth_id}'
            shift_table['smooth'].append(smooth_row)
            #
            # change shift_table['mulcov'] to use the new smoothing
            shift_mulcov_row['group_smooth_id'] = shift_smooth_id
            #
            # freeze
            assert len(mulcov_freeze_dict) == 0 or not no_ode_fit
            if mulcov_id in mulcov_freeze_dict :
               if freeze_type == 'mean' :
                  freeze = 'mean'
               elif mulcov_freeze_dict[mulcov_id] == 'posterior' :
                  freeze = 'no'
               else :
                  assert mulcov_freeze_dict[mulcov_id] == 'prior'
                  freeze = 'prior'
            else :
               freeze = 'no'
            #
            # copy_row
            copy_row = freeze == 'prior'
            if no_ode_fit :
               mulcov_type = shift_mulcov_row['mulcov_type']
               if mulcov_type == 'rate_value' :
                  rate_id   = shift_mulcov_row['rate_id']
                  rate_name = shift_table['rate'][rate_id]['rate_name']
                  if rate_name in no_ode_ignore.split() :
                     copy_row = True
               if mulcov_type == 'meas_value' :
                  affected_id    = shift_mulcov_row['integrand_id']
                  integrand_row  = fit_table['integrand'][affected_id]
                  integrand_name = integrand_row['integrand_name']
                  if integrand_name in no_ode_ignore.split() :
                     copy_row = True
            #
            # shift_table['smooth_grid']
            # add rows for this smoothing
            node_id  = None
            split_id = None
            for fit_grid_row in fit_table['smooth_grid'] :
               if fit_grid_row['smooth_id'] == fit_smooth_id :
                  add_shift_grid_row(
                     fit_fit_var,
                     fit_sample,
                     fit_table,
                     shift_table,
                     fit_grid_row,
                     integrand_id,
                     node_id,
                     split_id,
                     shift_prior_std_factor_mulcov,
                     shift_prior_dage,
                     shift_prior_dtime,
                     freeze,
                     copy_row,
                     age_id_next_list[fit_smooth_id],
                     time_id_next_list[fit_smooth_id],
                  )

      # --------------------------------------------------------------------
      # shift_table['rate']
      # and corresponding entries in the following child tables:
      # smooth, smooth_grid, and prior
      for shift_rate_row in shift_table['rate'] :
         # rate_name
         rate_name        = shift_rate_row['rate_name']
         # ----------------------------------------------------------------
         # fit_smooth_id
         fit_smooth_id = None
         if rate_name in name_rate2integrand :
            assert shift_rate_row['child_nslist_id'] is None
            fit_smooth_id = shift_rate_row['parent_smooth_id']
         else :
            # proper priors for omega are set by omega_constraint routine
            assert rate_name == 'omega'
            shift_rate_row['parent_smooth_id'] = None
            shift_rate_row['child_smooth_id']  = None
            shift_rate_row['child_nslist_id']  = None
         if not fit_smooth_id is None :
            #
            # integrand_id
            # only check for integrands that are used
            integrand_name  = name_rate2integrand[rate_name]
            integrand_id = at_cascade.table_name2id(
               fit_table['integrand'], 'integrand', integrand_name
            )
            #
            # smooth_row
            smooth_row = fit_table['smooth'][fit_smooth_id]
            smooth_row = copy.copy(smooth_row)
            assert smooth_row['mulstd_value_prior_id'] is None
            assert smooth_row['mulstd_dage_prior_id']  is None
            assert smooth_row['mulstd_dtime_prior_id'] is None
            #
            # : shift_table['smooth'], shift_smooth_id
            shift_smooth_id = len(shift_table['smooth'])
            smooth_row['smooth_name'] += f'_{shift_smooth_id}'
            shift_table['smooth'].append(smooth_row)
            #
            # shift_table['rate']
            # use the new smoothing for this rate
            shift_rate_row['parent_smooth_id'] = shift_smooth_id
            #
            # freeze
            freeze = 'no'
            #
            # copy_row
            copy_row = False
            if no_ode_fit :
               if rate_name in no_ode_ignore.split() :
                  copy_row = True
            #
            # shift_table['smooth_grid']
            # add rows for this smoothing
            for fit_grid_row in fit_table['smooth_grid'] :
               if fit_grid_row['smooth_id'] == fit_smooth_id :
                  add_shift_grid_row(
                     fit_fit_var,
                     fit_sample,
                     fit_table,
                     shift_table,
                     fit_grid_row,
                     integrand_id,
                     shift_node_id,
                     shift_split_reference_id,
                     shift_prior_std_factor,
                     shift_prior_dage,
                     shift_prior_dtime,
                     freeze,
                     copy_row,
                     age_id_next_list[fit_smooth_id],
                     time_id_next_list[fit_smooth_id],
                  )
         # ----------------------------------------------------------------
         # fit_smooth_id
         fit_smooth_id = None
         if rate_name in name_rate2integrand :
            fit_smooth_id = shift_rate_row['child_smooth_id']
         if not fit_smooth_id is None :
            #
            smooth_row = fit_table['smooth'][fit_smooth_id]
            smooth_row = copy.copy(smooth_row)
            #
            assert smooth_row['mulstd_value_prior_id'] is None
            assert smooth_row['mulstd_dage_prior_id']  is None
            assert smooth_row['mulstd_dtime_prior_id'] is None
            if rate_name == 'pini' :
               assert smooth_row['n_age'] == 1
            #
            # update: shift_table['smooth']
            # for case where its is the parent
            shift_smooth_id = len(shift_table['smooth'])
            smooth_row['smooth_name'] += f'_{shift_smooth_id}'
            shift_table['smooth'].append(smooth_row)
            #
            # change shift_table['rate'] to use the new smoothing
            shift_rate_row['child_smooth_id'] = shift_smooth_id
            #
            # add rows for this smoothing to shift_table['smooth_grid']
            for fit_grid_row in fit_table['smooth_grid'] :
               if fit_grid_row['smooth_id'] == fit_smooth_id :
                  #
                  # update: shift_table['smooth_grid']
                  shift_grid_row = copy.copy( fit_grid_row )
                  #
                  for ty in [
                     'value_prior_id', 'dage_prior_id', 'dtime_prior_id'
                         ] :
                     prior_id  = fit_grid_row[ty]
                     if prior_id is None :
                        shift_grid_row[ty] = None
                     else :
                        prior_row = fit_table['prior'][prior_id]
                        prior_row = copy.copy(prior_row)
                        prior_id  = len( shift_table['prior'] )
                        shift_table['prior'].append( prior_row )
                        add_index_to_name(
                           shift_table['prior'], 'prior_name'
                        )
                        shift_grid_row[ty] = prior_id
                  shift_grid_row['smooth_id']      = shift_smooth_id
                  shift_table['smooth_grid'].append( shift_grid_row )
      #
      # shift_connection
      new        = False
      shift_connection = dismod_at.create_connection(shift_database, new)
      #
      # replace shift_table
      for name in shift_table :
         dismod_at.replace_table(
            shift_connection, name, shift_table[name]
         )
      #
      # empty_avgint_table
      at_cascade.empty_avgint_table(shift_connection)
      #
      # drop the following tables:
      # log, c_shift_avgint, c_shift_predict_sample, c_shift_predict_fit_var
      drop_list = [ 'log', 'c_shift_avgint' , 'c_shift_predict_fit_var' ]
      if predict_sample :
         drop_list.append(  'c_shift_predict_sample' )
      for table_name in drop_list :
         command  = f'DROP TABLE {table_name}'
         dismod_at.sql_command(shift_connection, command)
      #
      # shift_connection
      shift_connection.close()
      #
      # shift_database
      at_cascade.omega_constraint(all_node_database, shift_database)
