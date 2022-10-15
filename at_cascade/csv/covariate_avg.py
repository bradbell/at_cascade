# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin csv_covariate_avg}
{xrst_spell
   avg
}

Compute Covariate Averages for One Node
#######################################

Syntax
******
{xrst_literal
   # BEGIN_SYNTAX
   # END_SYNTAX
}
{xrst_literal
   # BEGIN_RETURN
   # END_RETURN
}

covariate_table
***************
Is a table (i.e., list of dict) containing the information in
:ref:`csv_simulate@Input Files@covariate.csv` .

node_name
*********
is a str contain the name of the node that we are computing the average for.

covariate_avg
*************
This return is a dict where the keys are the covariates in covariate.csv
and the values are the average of the corresponding covariate.

{xrst_end csv_covariate_avg}
'''
# BEGIN_SYNTAX
# covariate_average =
def covariate_avg(covariate_table, node_name) :
   assert type(covariate_table) == list
   assert type(covariate_table[0]) == dict
   assert type(node_name) == str
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
      sex          = row['sex']
      #
      if sex not in  { 'female', 'male' } :
         msg  = f'covariate.csv at line {line_number}\n'
         msg += 'sex = {sex} is not female or male'
         assert False, msg
      #
      if node_name == row['node_name'] :
         count += 1
         for covariate_name in covariate_name_list :
            covariate_sum[covariate_name] += float( row[covariate_name] )
   #
   if count == 0 :
      msg  = f'node "{node_name}" does not appear in covariate.csv'
      assert False, msg
   #
   # covariate_average
   covariate_average = dict()
   for covariate_name in covariate_name_list :
      covariate_average[covariate_name] = \
         covariate_sum[covariate_name] / count
   #
   # BEGIN_RETURN
   assert type(covariate_average) == dict
   for value in covariate_average.values() :
      assert type(value) == float
   return covariate_average
   # END_RETURN
