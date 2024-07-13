# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ---------------------------------------------------------------------------
import os
import sys
#
# import at_cascade with a preference current directory version
current_directory = os.getcwd()
if os.path.isfile( current_directory + '/at_cascade/__init__.py' ) :
   sys.path.insert(0, current_directory)
import at_cascade
import dismod_at
#
def main() :
   #
   # wrok_dir
   work_dir = 'build/test'
   at_cascade.empty_directory(work_dir)
   os.chdir(work_dir)
   #
   # example.db
   file_name = 'example.db'
   connection     = dismod_at.create_connection(
      file_name, new = True, readonly = False
   )
   cursor         = connection.cursor()
   #
   # create table
   col_name = [ 'col_name'   ]
   col_type = [ 'text'       ]
   row_list = [
              [ 'row one'    ],
              [ 'row two'    ],
              [ 'row three'  ]
   ]
   tbl_name = 'temp'
   dismod_at.create_table(connection, tbl_name, col_name, col_type, row_list)
   #
   assert at_cascade.table_exists( connection, 'temp' ) == True
   assert at_cascade.table_exists( connection, 'other' ) == False
   #
   connection.close()
   return
#
if __name__ == '__main__' :
   main()
   print('table_exists: OK')
