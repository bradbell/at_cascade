# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin csv.covariate_avg}

Compute Covariate Averages for One Node
#######################################

Syntax
******
{xrst_literal ,
   # BEGIN_SYNTAX, # END_SYNTAX
   # BEGIN_RETURN, # END_RETURN
}

covariate_table
***************
Is a ``list`` of ``dict`` representation of a
:ref:`csv.simulate@Input Files@covariate.csv` file.
All of the columns in this table have been converted to ``float``
except for *node_name* and *sex* which have type ``str`` .
In addition, *sex* equal to ``both`` may have been added; see
:ref:`csv.covariate_both-name` .

node_name
*********
is a str contain the name of the node that we are computing the average for.

covariate_average
*****************
This return is a dict where the keys are the covariates in covariate.csv
and the values are the average of the corresponding covariate.

sex
***
is the sex that this average is for.

{xrst_end csv.covariate_avg}
'''
# BEGIN_SYNTAX
# at_cascade.csv.covariate_avg
def covariate_avg(covariate_table, node_name, sex) :
   assert type(covariate_table) == list
   assert type(covariate_table[0]) == dict
   assert type(node_name) == str
   assert sex in [ 'female', 'male', 'both' ]
   # END_SYNTAX
   #
   # covariate_name_list
   covariate_name_list = list()
   for key in covariate_table[0].keys() :
      if key not in [ 'node_name', 'sex', 'age', 'time', 'omega' ] :
         covariate_name_list.append(key)
   #
   # covariate_sum, count
   covariate_sum = dict()
   for covariate_name in covariate_name_list :
      covariate_sum[covariate_name] = 0.0
   count = 0
   #
   # covariate_sum, count
   line_number = 0;
   for row in covariate_table :
      line_number += 1
      if row['sex'] not in  { 'female', 'male', 'both' } :
         sex  = row['sex']
         msg  = f'covariate.csv at line {line_number}\n'
         msg += 'sex = {sex} is not female or male'
         assert False, msg
      #
      if node_name == row['node_name'] and row['sex'] == sex :
         count += 1
         for covariate_name in covariate_name_list :
            covariate_sum[covariate_name] += float( row[covariate_name] )
   #
   if count == 0 :
      msg  = f'node "{node_name}" does not appear with sex "{sex}" '
      msg += 'covariate_table.'
      assert False, msg
   #
   # covariate_average
   covariate_average = dict()
   for covariate_name in covariate_name_list :
      covariate_average[covariate_name] = \
         covariate_sum[covariate_name] / count
   #
   # BEGIN_RETURN
   # ...
   assert type(covariate_average) == dict
   for value in covariate_average.values() :
      assert type(value) == float
   return covariate_average
   # END_RETURN
