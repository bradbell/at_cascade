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

cov_name
========
We use *cov_name* for ``omega`` or one of the
:ref:`covariate_names <csv.simulate@Input Files@covariate.csv@covariate_name>`
that appear in this file.


both
====
For each node_name, age, time,
the covariate table value for *sex* equal both
is the average of its value for females and males.
To be specific, if female_value, male_value, both_value
are the corresponding values for a specific (node_name, age, time) then:
{xrst_code py}
   if female_value == male_value :
      both_value = female_value
   else :
      both_value = ( float( female_value ) + float( male_value ) ) / 2.0
{xrst_code}

cov_same
********
We include the *sex* value both even though it is not actually in the
covariate table.
For a *node_name* , *sex*, and *cov_name* is the covariate table, let
{xrst_code py}
   (node_other, sex_other, cov_other) = cov_same[ (node_name, sex, cov_name) ]
{xrst_code}

#. If follows that *cov_other* == *cov_name*; i.e.,
   the covariate column for these two triples is the same.

#. The (age , time , covariate) values
   corresponding to (node_name , sex) are the same as
   the (age , time , covariate) values
   corresponding to (node_other , sex_other) .

#. There is only one (node_other, sex_other) value
   for all the (node_name, sex) values that have the same
   the (age , time , covariate) values.

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
         if key in { 'node_name' , 'sex' } :
            assert type( row[key] ) == str
         else :
            assert type( row[key] ) == float
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
   if sex_set != { 'female' , 'male' } :
      msg  = 'covaraite.csv: expected sex to contain feamle and male\n'
      msg += 'It contains {sex_set}'
      assert False, msg
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
   # cov_subtable
   for node_name in node_list :
      cov_subtable[ (node_name, 'both') ] = list()
      for (i_age, age) in enumerate(age_list) :
         for (i_time, time) in enumerate(time_list) :
            index = i_age * n_time + i_time
            row_female = cov_subtable[ (node_name, 'female')][index]
            row_male   = cov_subtable[ (node_name, 'male')][index]
            assert row_female['age'] == row_male['age']
            assert row_female['time'] == row_male['time']
            row_both   = copy.copy( row_female )
            for cov_name in cov_list :
               if row_female[key] != row_male[key] :
                  row_both[key] = (row_female[key] + row_male[key]) / 2.0
            cov_subtable[ (node_name, 'both') ].append(row_both)
   #
   # cov_same
   cov_same = dict()
   #
   # cov_name
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
