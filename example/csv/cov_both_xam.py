# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2024 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin csv.cov_both_xam}
{xrst_spell
  haqi
}

Example and Test of covariate_both
##################################

Covariates
**********
This example has two covariates, haqi and income.

haqi
====
This covariate only depends on age and time; i.e.,
it is the same for all nodes and both sexes.

income
======
This covariate depends on age, time, and sex.
It is the same for all nodes.

covariate_table
***************
The covariate table is shuffled, after it is created,
to demonstrate the fact that the order of its rows does not matter.

haqi
====
This covariate is the same for all nodes and both sexes.

income
======
This covariate is different for each sex,
but given sex it is the same for all nodes.

Source
******
{xrst_literal
   # BEGIN_SOURCE
   # END_SOURCE
}

{xrst_end csv.cov_both_xam}
'''
# BEGIN_SOURCE
# at_cascade
# import at_cascade with a preference current directory version
import os
import sys
import random
current_directory = os.getcwd()
if os.path.isfile( current_directory + '/at_cascade/__init__.py' ) :
   sys.path.insert(0, current_directory)
import at_cascade
#
# haqi
def haqi(node, sex, age, time) :
   value = age / 100.0 + (time - 2000) / 20.0 + 0.01
   value = round(value, 4)
   return value
#
# income
def income(node, sex, age, time) :
   value = age / 100.0 + (2000 - time) / 20.0
   if sex == 'female' :
      value += 1.0
   else :
      value += 2.0
   value = round(value, 4)
   return value
#
# main
def main() :
   #
   age_list  = [ 20.0, 80.0 ]
   time_list = [ 1980.0, 2020.0 ]
   node_list = [ 'n0', 'n1', 'n2' ]
   sex_list  = [ 'female', 'male' ]
   cov_list  = [ 'haqi', 'income' ]
   omega     = 0.02
   #
   # covariate_table_in
   covariate_table_in = list()
   for node_name in node_list :
      for sex in sex_list :
         for age in age_list :
            for time in time_list :
               row = {
                  'node_name' : node_name ,
                  'sex'       : sex ,
                  'age'       : age ,
                  'time'      : time ,
                  'omega'     : omega ,
                  'haqi'      : haqi(  node_name, sex, age, time) ,
                  'income'    : income(node_name, sex, age, time) ,
               }
               covariate_table_in.append(row)
   random.shuffle(covariate_table_in)
   #
   # same cov
   covariate_table_out = at_cascade.csv.covariate_both(covariate_table_in)
   #
   # count
   count = { 'female' : 0, 'male' : 0 , 'both' : 0 }
   for row in covariate_table_out :
      count[ row['sex'] ] += 1
   #
   for sex in count :
      assert count[sex] == len(node_list) * len(age_list) * len(time_list)
   #
   print('cov_both_xam.py: OK')
#
if __name__ == '__main__' :
   main()
# END_SOURCE
