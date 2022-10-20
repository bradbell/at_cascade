# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin check_cascade_node}
{xrst_spell
   avgint
}

Check the Cascade Results for a Node
####################################

Syntax
******
{xrst_literal
   # BEGIN syntax
   # END syntax
}

rate_true
*********
This argument
is a function with the following syntax
```
rate = rate_true(rate_name, a, t, n, c)
```

rate_name
=========
The argument *rate_name* is one of the following:
:ref:`glossary@iota`,
:ref:`glossary@rho`,
:ref:`glossary@chi`, or
:ref:`glossary@omega`.

a, t
====
The argument *a* ( *t* ) is the age ( time ) at which we
are evaluating the rate.

n
=
The argument *n* is the :ref:`glossary@node_name` for the
node where we are evaluating the rate.

c
=
The argument *c* is a list of covariate values
in the same order as the covariate table.

rate
====
The result *rate* is the corresponding value for the rate.

all_node_database
*****************
is a python string specifying the location of the
:ref:`all_node_db`
relative to the current working directory.

fit_node_database
*****************
is a python string specifying the location of a
dismod_at database relative to the current working directory.
It is a :ref:`glossary@fit_node_database` with the
extra properties listed under
:ref:`cascade_root_node@Output dismod.db`
in the cascade_root_node documentation.

avgint_table
************
This an avgint table specifying the predictions to check.
The node_id in this table does not matter because the parent node
in the fit_node_database is used in its place.
The avgint table in the *fit_node_database* is replaced using this argument.

relative_tolerance
******************
Is an upper bound for the relative error in the predictions
corresponding to the avgint table.
The error is the prediction using the true rates
minus the prediction using the estimated rates.
If this argument is ``None``, the maximum relative error is printed.
This is intended as an aid in setting the relative tolerance.

{xrst_end check_cascade_node}
'''
# ----------------------------------------------------------------------------
import copy
import math
import dismod_at
import at_cascade
# ----------------------------------------------------------------------------
def check_cascade_node(
# BEGIN syntax
# at_cascade.check_cascade_node(
         rate_true          ,
         all_node_database  ,
         fit_node_database  ,
         avgint_table       ,
         relative_tolerance = None,
# )
) :
   assert type(all_node_database) == str
   assert type(fit_node_database) == str
   assert type(avgint_table) == list
   assert relative_tolerance == None or type(relative_tolerance) == float
   # END syntax
   #
   # tables
   new        = False
   connection = dismod_at.create_connection(fit_node_database, new)
   tables = dict()
   for name in [
      'age',
      'covariate',
      'time',
      'integrand',
      'node',
   ] :
      tables[name] = dismod_at.get_table_dict(connection, name)
   connection.close()
   #
   # fit_node_id
   fit_node_name = at_cascade.get_parent_node( fit_node_database )
   fit_node_id   = at_cascade.table_name2id(
      tables['node'], 'node', fit_node_name
   )
   #
   # avgint table
   new        = False
   connection = dismod_at.create_connection(fit_node_database, new)
   message         = 'check_cascade_node: replace avgint table'
   tbl_name        = 'avgint'
   avgint_copy     = copy.copy( avgint_table )
   for row in avgint_copy :
      row['node_id'] = fit_node_id
   dismod_at.replace_table(connection, tbl_name, avgint_copy)
   at_cascade.add_log_entry(connection, message)
   connection.close()
   #
   # predict_fit_var_table
   command = [ 'dismod_at', fit_node_database, 'predict', 'fit_var' ]
   dismod_at.system_command_prc(command)
   new        = False
   connection = dismod_at.create_connection(fit_node_database, new)
   predict_fit_var_table = dismod_at.get_table_dict(connection, 'predict')
   connection.close()
   #
   # predict_sample_table
   command = [ 'dismod_at', fit_node_database, 'predict', 'sample' ]
   dismod_at.system_command_prc(command)
   new        = False
   connection = dismod_at.create_connection(fit_node_database, new)
   predict_sample_table = dismod_at.get_table_dict(connection, 'predict')
   connection.close()
   #
   # n_covariate n_avgint, n_predict, n_sample
   n_covariate = len(tables['covariate'])
   n_avgint    = len(avgint_table)
   n_predict   = len(predict_sample_table)
   n_sample    = int( n_predict / n_avgint )
   #
   assert n_avgint == len( predict_fit_var_table )
   assert n_predict % n_avgint == 0
   #
   # cov_reference_list
   cov_reference_list = list()
   for (covariate_id, row) in enumerate( tables['covariate'] ) :
      reference = row['reference']
      assert reference is not None
      cov_reference_list.append( reference )
   #
   # rate_fun
   rate_fun = dict()
   rate_fun['iota'] = lambda a, t :  \
         rate_true('iota', a, t, fit_node_name, cov_reference_list)
   rate_fun['rho'] = lambda a, t :  \
         rate_true('rho', a, t, fit_node_name, cov_reference_list)
   rate_fun['chi'] = lambda a, t :  \
         rate_true('chi', a, t, fit_node_name, cov_reference_list)
   rate_fun['omega'] = lambda a, t :  \
         rate_true('omega', a, t, fit_node_name, cov_reference_list)
   #
   # sumsq
   sumsq = n_avgint * [0.0]
   #
   # predict_id, predict_row
   max_rel_error    = 0.0
   for (predict_id, predict_row) in enumerate(predict_sample_table ) :
      #
      # avgint_row
      avgint_id  = predict_row['avgint_id']
      avgint_row = avgint_copy[avgint_id]
      assert avgint_id == predict_id % n_avgint
      #
      # sample_index
      sample_index = predict_row['sample_index']
      assert sample_index * n_avgint + avgint_id == predict_id
      #
      # integrand_name
      integrand_id = avgint_row['integrand_id']
      integrand_name = tables['integrand'][integrand_id]['integrand_name']
      #
      # node_name
      node_id   = avgint_row['node_id']
      node_name = tables['node'][node_id]['node_name']
      assert node_name == fit_node_name
      #
      # avg_integrand
      avg_integrand = predict_fit_var_table[avgint_id]['avg_integrand']
      #
      # sample_value
      sample_value = predict_row['avg_integrand']
      #
      # sumsq
      sumsq[avgint_id] += (sample_value - avg_integrand)**2
   #
   # avgint_id, row
   for (avgint_id, row) in enumerate(predict_fit_var_table) :
      assert avgint_id == row['avgint_id']
      #
      # avgint_row
      avgint_row = avgint_copy[avgint_id]
      #
      # integrand_name
      integrand_id   = avgint_row['integrand_id']
      integrand_name = tables['integrand'][integrand_id]['integrand_name']
      #
      # age
      age = avgint_row['age_lower']
      assert age == avgint_row['age_upper']
      #
      # time
      time = avgint_row['time_lower']
      assert time == avgint_row['time_upper']
      #
      # avg_integrand
      avg_integrand = row['avg_integrand']
      #
      # sample_std
      sample_std = math.sqrt( sumsq[avgint_id] )
      #
      # check_value
      grid        = { 'age' : [age], 'time' : [time] }
      abs_tol     = 1e-8
      check_value = dismod_at.average_integrand(
         rate_fun, integrand_name, grid, abs_tol
      )
      #
      # check
      if check_value == 0.0 :
         assert avg_integrand == 0.0
      else :
         error            = check_value - avg_integrand
         rel_error        = 1.0 - avg_integrand / check_value
         max_rel_error    = max(max_rel_error, abs(rel_error) )
         if not relative_tolerance is None :
            if abs(rel_error) >= relative_tolerance :
               print(rel_error, relative_tolerance)
            assert abs(rel_error) < relative_tolerance
            assert abs(error) < 2.0 * sample_std
   if relative_tolerance is None :
      print('check_cascade: max_rel_error = ', max_rel_error)
