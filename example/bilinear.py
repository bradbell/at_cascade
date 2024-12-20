# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ----------------------------------------------------------------------------
import os
import sys
import math
'''
{xrst_begin example_bilinear}

Example Bilinear Interpolation
##############################

Example Source Code
*******************
{xrst_literal
   BEGIN_SOURCE
   END_SOURCE
}

{xrst_end example_bilinear}
'''
# BEGIN_SOURCE
#
# import at_cascade with a preference current directory version
current_directory = os.getcwd()
if os.path.isfile( current_directory + '/at_cascade/__init__.py' ) :
   sys.path.insert(0, current_directory)
import at_cascade
#
def test_grid(n_age, n_time) :
   #
   # age_list
   age_list  = [ 80.0,   20.0   ]
   if n_age == 1 :
      age_list = [ 50.0 ]
   else :
      assert n_age == 2
   #
   # time_list
   time_list = [ 2200.0, 1980.0 ]
   if n_time == 1 :
      time_list = [ 2000.0 ]
   else :
      assert n_time == 2
   #
   # limit_age
   def limit_age(age) :
      age = min( max(age_list), age )
      age = max( min(age_list), age )
      return age
   #
   # limit_time
   def limit_time(time) :
      time = min( max(time_list), time )
      time = max( min(time_list), time )
      return time
   #
   # iota_fun
   def iota_fun(age) :
      age        = limit_age(age)
      age_ratio  = (age - 50.0) / 50.0
      iota       = 0.02 * age_ratio  + 0.05
      return iota
   #
   # rho_fun
   def rho_fun(time) :
      time       = limit_time(time)
      time_ratio = (time - 2000.0) / 20.0
      rho        = 0.02 * time_ratio + 0.04
      return rho
   #
   # chi_fun
   def chi_fun(age, time) :
      age        = limit_age(age)
      time       = limit_time(time)
      age_ratio  = (age - 50.0) / 50.0
      time_ratio = (time - 2000.0) / 20.0
      chi        = 0.01 * age_ratio + 0.02 * time_ratio + 0.03
      return chi
   #
   # table
   table = list()
   for age in age_list :
      for time in time_list :
         iota = iota_fun(age)
         rho  = rho_fun(time)
         chi  = chi_fun(age, time)
         row  = {
            'age'  : age ,
            'time' : time ,
            'iota' : iota ,
            'rho'  : rho ,
            'chi'  : chi ,
         }
         table.append(row)
   #
   # age_grid, time_grid, spline_dict
   age_grid, time_grid, spline_dict = at_cascade.bilinear(
      table     = table ,
      x_name    = 'age' ,
      y_name    = 'time' ,
      z_list    = [ 'iota', 'rho', 'chi' ]
   )
   #
   # age_grid, time_grid
   assert age_grid == sorted(age_list)
   assert time_grid == sorted(time_list)
   #
   # age_test, time_test
   age_test = age_list + [ 40.0, 100.0]
   time_test = time_list + [1970.0, 1990.0]
   #
   for age in age_test :
      for time in time_test :
         iota  = spline_dict['iota'](age, time)
         check = iota_fun(age)
         assert math.isclose(iota, check)
         #
         rho   = spline_dict['rho'](age, time)
         check = rho_fun(time)
         assert math.isclose(rho, check)
         #
         chi   = spline_dict['chi'](age, time)
         check = chi_fun(age, time)
         assert math.isclose(chi, check)
#
# Without this, the mac will try to execute main on each processor.
if __name__ == '__main__' :
   test_grid(2, 2)
   test_grid(1, 2)
   test_grid(2, 1)
   test_grid(1, 1)
   print('bilinear: OK')
# END_SOURCE
