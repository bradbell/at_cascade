# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
#
import os
import sys
import copy
import dismod_at
#
# import at_cascade with a preference current directory version
current_directory = os.getcwd()
if os.path.isfile( current_directory + '/at_cascade/__init__.py' ) :
   sys.path.insert(0, current_directory)
import at_cascade
#
def main() :
   #
   # tbl_name
   tbl_name = 'data'
   #
   # col_name
   col_name = [
      'data_name',
      'integrand_id',
      'density_id',
      'node_id',
      'subgroup_id',
      'weight_id',
      'hold_out',
      'meas_value',
      'mwas_std',
      'eta',
      'nu',
      'age_lower',
      'age_upper',
      'time_lower',
      'time_upper',
   ]
   #
   # col_type
   col_type = [
      'text',    # data_name
      'integer', # integrand_id
      'integer', # density_id
      'integer', # node_id
      'integer', # subgroup_id
      'integer', # weight_id
      'integer', # hold_out
      'real',    # meas_value
      'real',    # mwas_std
      'real',    # eta
      'real',    # nu
      'real',    # age_lower
      'real',    # age_upper
      'real',    # time_lower
      'real',    # time_upper
   ]
   #
   # default
   default = [
      None,      # data_name
      None,      # integrand_id
      0,         # density_id
      0,         # node_id
      0,         # subgroup_id
      0,         # weight_id
      None,      # hold_out
      1.0,       # meas_value
      1.0,       # mwas_std
      1.0,       # eta
      3.0,       # nu
      50.0,      # age_lower
      50.0,      # age_upper
      50.0,      # time_lower
      50.0,      # time_upper
   ]
   #
   # row_list
   row_list = list()
   for data_id in range(100) :
      data_name    = str(data_id)
      integrand_id = data_id % 5
      hold_out     = 0
      if integrand_id == 3 :
         hold_out = 1
      row          = copy.copy( default )
      for j in range( len( col_name ) ) :
         if col_name[j] == 'data_name' :
            row[j] = data_name
         if col_name[j] == 'integrand_id' :
            row[j] = integrand_id
         if col_name[j] == 'hold_out' :
            row[j] = hold_out
      row_list.append(row)
   #
   # connection
   # create database
   database = 'temp.db'
   new        = True
   connection = dismod_at.create_connection(database, new)
   #
   # create data table
   dismod_at.create_table(connection, tbl_name, col_name, col_type, row_list)
   #
   # connection
   connection.close()
   #
   # fit_integrand
   fit_integrand = at_cascade.get_fit_integrand(database)
   #
   # check fit_integrand
   check = { 0, 1, 2, 4 }
   assert check == fit_integrand
main()
print('get_fit_integrand: OK')
sys.exit(0)
