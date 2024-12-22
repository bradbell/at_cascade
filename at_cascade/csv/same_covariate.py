# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2024 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin csv.same_covariate}

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

cov_name
========
We use *cov_name* for one of the
:ref:`covariate_names <csv.simulate@Input Files@covariate.csv@covariate_name>`
that appear in this file.

age, time, cov_name
===================
You may better detect covariates that are the same if
you convert the age, time, and covariate columns from
``str`` to ``float`` (or a similar type that can be sorted).
For example,
'0.1' is not equal to '0.10' but
'float(0.1)' is equal to 'float(0.10)' .


same_cov
********
For a *node_name* , *sex*, and *cov_name* is the covariate table, let
{xrst_code py}
   (node_other, sex_other, cov_other) = same_cov[ (node_name, sex, cov_name) ]
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

Example
*******
see :ref:`csv.same_cov_xam-name` .

{xrst_end csv.same_covariate}
'''
# BEGIN_PROTOTYPE
def same_covariate(covariate_table) :
   assert type(covariate_table) == list
   # END_PROTOTYPE
   #
   #
   # cov_list
   exclude    = { 'node_name', 'sex', 'age', 'time', 'omega'}
   cov_list   = list( set( covariate_table[0].keys() ) - exclude )
   #
   # node_list, sex_list
   node_set   = set()
   sex_set    = set()
   for row in covariate_table :
      node_set.add( row['node_name'] )
      sex_set.add(  row['sex'] )
   node_list = list( node_set )
   sex_list  = list( sex_set )
   if sex_set != { 'female' , 'male' } :
      msg  = 'covaraite.csv: expected sex to contain feamle and male\n'
      msg += 'It contains {sex_set}'
      assert False, msg
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
   # check_age_time
   check_age_time = None
   for pair in cov_subtable :
      age_time = list()
      for row in cov_subtable[pair] :
         age_time.append( (row['age'], row['time'] ) )
      if check_age_time == None :
         check_age_time = age_time
         check_pair     = pair
      else :
         if check_age_time != age_time :
            (node_1, sex_1) = pair
            (node_2, sex_2) = check_pair
            msg  = f'covariate.csv: age-time grid for ({node_1}, {sex_1})'
            msg += f' is different than for ({node_2}, {sex_2})'
            assert False, msg
   #
   # same_cov
   same_cov = dict()
   #
   # cov_name
   for cov_name in cov_list :
      #
      # cov_value_dict
      cov_value_dict = dict()
      for pair in cov_subtable :
         cov_value = list()
         for row in cov_subtable[pair] :
            cov_value.append( float(row[cov_name]) )
         cov_value_dict[pair] = cov_value
      #
      # cov_value_list
      cov_value_list = sorted(cov_value_dict.items(), key = lambda x : x[1])
      #
      # same_cov
      previous_value  = None
      previous_triple = None
      for (pair, cov_value) in cov_value_list :
         (node_name, sex) = pair
         triple           = (node_name, sex, cov_name)
         if cov_value == previous_value :
            other_triple           = same_cov[previous_triple]
            same_cov[triple]       = other_triple
            assert same_cov[other_triple] == other_triple
         else :
            same_cov[triple] = triple
         previous_value  = cov_value
         previous_triple = triple
   # BEGIN_RETURN
   #
   assert type(same_cov) == dict
   for triple in same_cov :
      assert type(triple) == tuple
      assert len(triple) == 3
   return same_cov
   # END_RETURN
