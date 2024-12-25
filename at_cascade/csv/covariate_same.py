# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2024 Bradley M. Bell
# ----------------------------------------------------------------------------
import copy
'''
{xrst_begin csv.covariate_same}

Determine Which Covariates in covariate.csv Are the Same
########################################################

Prototype
*********
{xrst_literal ,
   # BEGIN_PROTOTYPE, # END_PROTOTYPE
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

cov_name
========
We use *cov_name* for ``omega`` or one of the
:ref:`covariate_names <csv.simulate@Input Files@covariate.csv@covariate_name>`
that appear in this file.


cov_same
********
For a *node_name* , *sex*, and *cov_name* is *covariate_table*
{xrst_code py}
   (node_other, sex_other, cov_other) = cov_same[ (node_name, sex, cov_name) ]
{xrst_code}

#. If follows that *cov_other* == *cov_name*; i.e.,
   the covariate column for these two triples is the same.

#. For each age, time, the *cov_name* value corresponding to
   (node_name, sex, cov_name)
   is the same as the *cov_other* value corresponding to
   (node_other, sex_other, cov_other).

#. There is one and only one value of (node_other, sex_other, cov_other)
   for all the (node_name, sex, cov_name) triples
   that have the same *cov_name* value for each age and time.

Side Effects
************
This routine reports and error
if the age-time grid is not rectangular
and the same for each (node_name, sex) pair.

Example
*******
see :ref:`csv.cov_same_xam-name` .

{xrst_end csv.covariate_same}
'''
# BEGIN_PROTOTYPE
def covariate_same(covariate_table) :
   assert type(covariate_table) == list
   for row in covariate_table :
      for key in row :
         type_check = str if key in [ 'node_name' , 'sex' ] else float
         assert type( row[key] ) == type_check
   # END_PROTOTYPE
   #
   #
   # cov_list
   exclude    = { 'node_name', 'sex', 'age', 'time'}
   cov_list   = list( set( covariate_table[0].keys() ) - exclude )
   #
   # node_set, sex_set, age_set, time_set
   node_set   = set()
   sex_set    = set()
   age_set    = set()
   time_set   = set()
   for row in covariate_table :
      node_set.add( row['node_name'] )
      sex_set.add(  row['sex'] )
      age_set.add(  row['age'] )
      time_set.add( row['time'] )
   #
   # node_list, sex_list, age_list, time_list
   node_list = sorted( node_set )
   sex_list  = sorted( sex_set )
   age_list  = sorted( age_set )
   time_list = sorted( time_set )
   #
   # cov_subtable
   cov_subtable = dict()
   for node_name in node_list :
      for sex in sex_list :
         cov_subtable[ (node_name, sex) ] = list()
   #
   # cov_subtable
   for row in covariate_table :
      node_name = row['node_name']
      sex       = row['sex']
      cov_subtable[ (node_name, sex) ].append( row )
   #
   # cov_subtable
   for pair in cov_subtable :
      table = cov_subtable[pair]
      table = sorted(table, key = lambda row : (row['age'], row['time']) )
      cov_subtable[pair] = table
   #
   # check age-time grid
   n_age  = len(age_list)
   n_time = len(time_list)
   for pair in cov_subtable :
      table = cov_subtable[pair]
      for (i_age, age) in enumerate(age_list) :
         for (i_time, time) in enumerate(time_list) :
            index = i_age * n_time + i_time
            row   = table[index]
            age   = row['age']
            time  = row['time']
            if age != age_list[i_age] or time != time_list[i_time] :
               (node_name, sex) = pair
               msg  = 'covariate_spline: Error in covariate.csv\n'
               msg += f'node_name = {node_name}, sex = {sex} \n'
               msg += 'Expected following rectangular grid:\n'
               msg += f'age_grid  = {age_list}\n'
               msg += f'time_grid = {time_list}'
               assert False, msg
   #
   # cov_same
   cov_same = dict()
   for cov_name in cov_list :
      #
      # cov_value_dict
      cov_value_dict = dict()
      for pair in cov_subtable :
         cov_value = list()
         for row in cov_subtable[pair] :
            cov_value.append( row[cov_name] )
         cov_value_dict[pair] = cov_value
      #
      # cov_value_list
      cov_value_list = sorted(cov_value_dict.items(), key = lambda x : x[1])
      #
      # cov_same
      previous_value  = None
      previous_triple = None
      for (pair, cov_value) in cov_value_list :
         (node_name, sex) = pair
         triple           = (node_name, sex, cov_name)
         if cov_value == previous_value :
            other_triple           = cov_same[previous_triple]
            cov_same[triple]       = other_triple
            assert cov_same[other_triple] == other_triple
         else :
            cov_same[triple] = triple
         previous_value  = cov_value
         previous_triple = triple
   # BEGIN_RETURN
   #
   assert type(cov_same) == dict
   for triple in cov_same :
      assert type(triple) == tuple
      assert len(triple) == 3
   return cov_same
   # END_RETURN
