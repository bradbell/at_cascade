# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2024 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin csv.same_cov_xam}
{xrst_spell
   haqi
}

Example and Test of same_covariate
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

same_cov
********
same_cov is checked to see that it detects the following:

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

{xrst_end csv.same_cov_xam}
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
   time_list = [ 1980, 2020 ]
   node_list = [ 'n0', 'n1', 'n2' ]
   sex_list  = [ 'female', 'male' ]
   cov_list  = [ 'haqi', 'income' ]
   omega     = 0.02
   #
   # covariate_table
   covariate_table = list()
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
               covariate_table.append(row)
   random.shuffle(covariate_table)
   #
   # same cov
   same_cov = at_cascade.csv.same_covariate(covariate_table)
   #
   # check that haqi is same for all nodes and all sexes
   triple_other = None
   for node_name in node_list :
      for sex in sex_list :
         triple = (node_name, sex, 'haqi')
         if same_cov[triple] == triple :
               assert triple_other == None
               triple_other = triple
   for node_name in node_list :
      for sex in sex_list :
         assert same_cov[ (node_name, sex, 'haqi') ] == triple_other
   #
   # income
   # same for all nodes, different for each sex
   triple_other = dict()
   for node_name in node_list :
      for sex in sex_list :
         triple = (node_name, sex, 'income')
         if same_cov[triple] == triple :
               assert sex not in triple_other
               triple_other[sex] = triple
   for node_name in node_list :
      for sex in sex_list :
         assert same_cov[ (node_name, sex, 'income') ] == triple_other[sex]
   print('same_cov_xam: OK')
#
if __name__ == '__main__' :
   main()
# END_SOURCE
