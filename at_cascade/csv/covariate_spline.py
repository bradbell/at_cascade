# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ----------------------------------------------------------------------------
import at_cascade
'''
{xrst_begin csv.covariate_spline}
{xrst_spell
   cov
}

Create Spline Functions For Covariates
######################################

Prototype
*********
{xrst_literal ,
   BEGIN_DEF, END_DEF
   BEGIN_RETURN, END_RETURN
}

covariate_table
***************
Is a ``list`` of ``dict`` representation of a
:ref:`csv.simulate@Input Files@covariate.csv` file.
All of the keys in this ``dict`` are covariate names except for
``node_name`` , ``sex``, ``age`` , ``time`` and ``omega`` .
All of the columns have been converted to type ``float`` except
for *node_name* and *sex* which have type ``str`` .

node_set
********
This is the set of nodes in :ref:`csv.simulate@Input Files@node.csv`

age_grid
********
This is a sorted list of float containing the age values
that are present for each node_name and sex.

time_grid
*********
This is a sorted list of float containing the time values
that are present for each node_name and sex.

spline_cov
**********
This is a dict of dict of dict.
Let spline be defined by

   for node_name in covariate_table
      for sex in covariate_table
         for cov_name a covariate name or omega
            spline = spline_cov[node_name][sex][cov_name]

Then spline is the corresponding function of age and time; i.e.,
{xrst_code py}
   z = spline(age, time)
{xrst_code}
sets *z* to the value of the covariate or omega
for the specified age, time, node_name, and sex where
*age*, *time*, and *z* are floats.

Side Effects
************
This routine aborts with an assert if covariate.csv does not have the
same rectangular grid in age and time for each (node_name, sex) pair.

{xrst_end csv.covariate_spline}
'''
# BEGIN_DEF
# at_cascade.csv.covariate_spline
def covariate_spline(covariate_table , node_set) :
   assert type( covariate_table ) == list
   assert type( covariate_table[0] ) == dict
   assert type( node_set ) == set
   # END_DEF
   #
   # cov_name_list
   exclude       = {  'node_name', 'sex', 'age', 'time' }
   cov_name_set  = set( covariate_table[0].keys() ) - exclude
   cov_name_list = list( cov_name_set )
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
         msg  = f'covariate_spline: Error: '
         msg += f'line {line_number} in covariate.csv\n'
         msg += f'node_name {node_name} is not in node.csv'
         assert False, msg
      if sex not in ['female', 'male', 'both'] :
         msg  = f'covariate_spline: Error: '
         msg += f'line {line_number} in covariate.csv\n'
         msg += f'sex {sex} is not female or male'
         assert False, msg
      #
      # covariate_row_list
      if node_name not in covariate_row_list :
         covariate_row_list[node_name] = dict()
      if sex not in covariate_row_list[node_name] :
         covariate_row_list[node_name][sex] = list()
      covariate_row_list[node_name][sex].append( row )
   #
   # cov_same
   cov_same = at_cascade.csv.covariate_same(covariate_table)
   #
   # spline_cov
   spline_cov = dict()
   previous   = dict()
   for node_name in covariate_row_list :
      #
      # spline_cov[node_name]
      spline_cov[node_name] = dict()
      #
      for sex in covariate_row_list[node_name] :
         #
         # spline_cov[node_name][sex]
         spline_cov[node_name][sex] = dict()
         #
         # z_list
         # only compuite splines that are needed
         z_list = list()
         for cov_name in cov_name_list :
            triple = (node_name, sex, cov_name)
            if cov_same[triple] == triple :
               z_list.append( cov_name )
         if 0 < len(z_list) :
            #
            # age_grid, time_grid, spline_dict
            age_grid, time_grid, spline_dict = at_cascade.bilinear(
               table  = covariate_row_list[node_name][sex] ,
               x_name = 'age',
               y_name = 'time',
               z_list = cov_name_list
            )
            # covariate_same should have checked rectangular grid
            assert spline_dict != None
            if len( previous ) != 0 :
               same_grid = previous['age_grid'] == age_grid
               same_grid = same_grid and previous['time_grid'] == time_grid
               assert same_grid
            #
            # spline_cov[node_name][sex]
            for cov_name in z_list :
               triple = (node_name, sex, cov_name)
               spline_cov[node_name][sex][cov_name] = spline_dict[cov_name]
            #
            previous['node_name'] = node_name
            previous['sex']       = sex
            previous['age_grid']  = age_grid
            previous['time_grid'] = time_grid
   #
   # spline_cov
   # link from splines that are not needed to corresponding same spline
   for node_name in covariate_row_list :
      for sex in covariate_row_list[node_name] :
         for cov_name in cov_name_list :
            triple = (node_name, sex, cov_name)
            if cov_same[triple] != triple :
               (node_other, sex_other, cov_other) = cov_same[triple]
               assert cov_other == cov_name
               spline_cov[node_name][sex][cov_name] = \
                  spline_cov[node_other][sex_other][cov_other]

   # BEGIN_RETURN
   # ...
   assert type(age_grid) == list
   assert type(time_grid) == list
   assert type(spline_cov) == dict
   return age_grid, time_grid, spline_cov
   # END_RETURN
