# -----------------------------------------------------------------------------
# at_cascade: Cascading Dismod_at Analysis From Parent To Child Regions
#           Copyright (C) 2021-22 University of Washington
#              (Bradley M. Bell bradbell@uw.edu)
#
# This program is distributed under the terms of the
#     GNU Affero General Public License version 3.0 or later
# see http://www.gnu.org/licenses/agpl.txt
# -----------------------------------------------------------------------------
import os
import sys
'''
{xrst_begin csv_table}

Example Reading and Writing CSV Files
#####################################

Example Source Code
*******************
{xrst_literal
   BEGIN_SOURCE
   END_SOURCE
}

{xrst_end csv_table}
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
   # write_table
   write_table = [
      { 'age' : '40',  'time' : '2000', 'sex' : 'female' },
      { 'age' : '50',  'time' : '2000', 'sex' : 'female' },
      { 'age' : '60',  'time' : '2000', 'sex' : 'male'   },
   ]
   #
   # file_name
   file_name = 'build/file.csv'
   #
   # write_csv_table
   at_cascade.write_csv_table(file_name, write_table)
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
   sys.exit(0)
# END_SOURCE
