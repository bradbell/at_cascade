# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
import os
import sys
'''
{xrst_begin csv_join_file_xam}

Example Joining Two CSV Tables
##############################

Example Source Code
*******************
{xrst_literal
   BEGIN_SOURCE
   END_SOURCE
}

{xrst_end csv_join_file_xam}
'''
# BEGIN_SOURCE
#
# import at_cascade with a preference current directory version
current_directory = os.getcwd()
if os.path.isfile( current_directory + '/at_cascade/__init__.py' ) :
   sys.path.insert(0, current_directory)
import at_cascade
#
def main() :
   #
   # left_file
   left_file = 'build/csv/left_file.csv'
   left_table = [
      { 'age' : '40',  'time' : '2000', 'sex' : 'female' },
      { 'age' : '50',  'time' : '2000', 'sex' : 'female' },
      { 'age' : '60',  'time' : '2000', 'sex' : 'female' },
   ]
   at_cascade.csv.write_table(left_file, left_table)
   #
   # right_file
   right_file = 'build/csv/right_file.csv'
   right_table = [
      { 'meas_value' : '1.0', 'sex' : 'female' },
      { 'meas_value' : '2.0', 'sex' : 'both' },
      { 'meas_value' : '2.0', 'sex' : 'male' },
   ]
   at_cascade.csv.write_table(right_file, right_table)
   #
   # result_file
   result_file = 'build/csv/result_file.csv'
   at_cascade.csv.join_file(left_file, right_file, result_file)
   #
   # result_table
   result_table = at_cascade.csv.read_table(result_file)
   #
   # check
   assert len(result_table) == len(left_table)
   assert list( result_table[0].keys() ) == \
      [ 'age', 'time', 'sex', 'meas_value' ]
   for index in range( len(left_table) ) :
      left_row   = left_table[index]
      right_row  = right_table[index]
      result_row = result_table[index]
      for key in result_row :
         if key in right_row :
            assert result_row[key] == right_row[key]
         else :
            assert result_row[key] == left_row[key]
   #
#
# Without this, the mac will try to execute main on each processor.
if __name__ == '__main__' :
   main()
   print('csv_join_file_xam: OK')
   sys.exit(0)
# END_SOURCE
