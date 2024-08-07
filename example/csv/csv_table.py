# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ----------------------------------------------------------------------------
import os
import sys
'''
{xrst_begin csv.table}

Example Reading and Writing CSV Files
#####################################

Example Source Code
*******************
{xrst_literal
   BEGIN_SOURCE
   END_SOURCE
}

{xrst_end csv.table}
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
   # result_dir
   result_dir = 'build/example/csv'
   at_cascade.empty_directory(result_dir)
   #
   # write_table
   write_table = [
      { 'age' : '40',  'time' : '2000', 'sex' : 'female' },
      { 'age' : '50',  'time' : '2000', 'sex' : 'female' },
      { 'age' : '60',  'time' : '2000', 'sex' : 'male'   },
   ]
   #
   # file_name
   file_name = 'build/example/csv/file.csv'
   #
   # csv.write_table
   at_cascade.csv.write_table(file_name, write_table)
   #
   # read_table
   read_table = at_cascade.csv.read_table(file_name)
   #
   # check
   assert write_table == read_table
#
# Without this, the mac will try to execute main on each processor.
if __name__ == '__main__' :
   main()
   print('cvs_table: OK')
# END_SOURCE
