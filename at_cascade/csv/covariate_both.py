# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2024 Bradley M. Bell
# ----------------------------------------------------------------------------
import copy
'''
{xrst_begin csv.covariate_both}

Add both Sex to csv Covariate Table
###################################

Prototype
*********
{xrst_literal ,
   # BEGIN_DEF, # END_DEF
   # BEGIN_RETURN, # END_RETURN
}

covariate_table_in
******************
Is a ``list`` of ``dict`` representation of a
:ref:`csv.simulate@Input Files@covariate.csv` file.

covariate_table_out
*******************
Is a ``list`` of ``dict`` representation of
:ref:`csv.simulate@Input Files@covariate.csv` file.
This has all the rows that are in *covariate_table_in*
plus rows with *sex* equal to *both* .

both
====
For each node_name, age, time,
the covariate table value for *sex* equal ``both``
is the average of its value for ``female`` and ``male`` .
To be specific, if female_value, male_value, both_value
are a covariate's values for a specific (node_name, age, time) then:
{xrst_code py}
   if female_value == male_value :
      both_value = female_value
   else :
      both_value = ( float( female_value ) + float( male_value ) ) / 2.0
{xrst_code}

Example
*******
see :ref:`csv.cov_both_xam-name` .

{xrst_end csv.covariate_both}
'''
# BEGIN_DEF
# at_cascade.csv.covariate_both
def covariate_both(covariate_table_in) :
   assert type(covariate_table_in) == list
   for row in covariate_table_in :
      for key in row :
         type_check = str if key in [ 'node_name' , 'sex' ] else float
         assert type( row[key] ) == type_check
   # END_DEF
   #
   # covariate_dict
   covariate_dict = dict()
   covariate_dict['female'] = dict()
   covariate_dict['male']   = dict()
   for row in covariate_table_in :
      sex = row['sex']
      if sex not in [ 'female', 'male' ] :
         msg = 'covariate_both: covariate.csv: sex is not female or male'
         assert False, msg
      triple  = ( row['node_name'], row['age'], row['time'] )
      covariate_dict[sex][triple] = row
   for triple in covariate_dict['female'] :
      if triple not in covariate_dict['male'] :
         (node_name, age, time) = triple
         msg  = f'covariate_both: covariate.csv: found '
         msg += f'node_name = {node_name}, age = {age}, time = {time}\n'
         msg += 'for sex = female but not for sex = male'
         assert False, msg
   for triple in covariate_dict['male'] :
      if triple not in covariate_dict['female'] :
         (node_name, age, time) = triple
         msg  = f'covariate_both: covariate.csv: found '
         msg += f'node_name = {node_name}, age = {age}, time = {time}\n'
         msg += 'for sex = male but not for sex = female'
         assert False, msg
   #
   # cov_list
   exclude    = { 'node_name', 'sex', 'age', 'time'}
   cov_list   = list( set( covariate_table_in[0].keys() ) - exclude )
   #
   # covariate_table_out
   covariate_table_out = copy.deepcopy(covariate_table_in)
   for triple in covariate_dict['female'] :
      (node_name, age, time) = triple
      row_female  = covariate_dict['female'][triple]
      row_male       = covariate_dict['male'][triple]
      #
      assert row_female['sex'] == 'female'
      assert row_male['sex']   == 'male'
      #
      assert row_female['node_name'] == node_name
      assert row_male['node_name']   == node_name
      #
      assert row_female['age'] == age
      assert row_male['age']   == age
      #
      assert row_female['time'] == time
      assert row_male['time']   == time
      #
      row_out        = copy.copy( row_female )
      row_out['sex'] = 'both'
      for key in cov_list :
         if row_male[key] != row_female[key] :
            row_out[key] = (row_female[key] + row_male[key]) / 2.0
      covariate_table_out.append( row_out )
   # BEGIN_RETURN
   #
   assert type(covariate_table_out) == list
   for row in covariate_table_out :
      for key in row :
         type_check = str if key in [ 'node_name' , 'sex' ] else float
         assert type( row[key] ) == type_check
   return covariate_table_out
   # END_RETURN
