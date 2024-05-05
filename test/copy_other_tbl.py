# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-23 Bradley M. Bell
# ----------------------------------------------------------------------------
# test copy_root_db and copy_other_tbl.py
# ----------------------------------------------------------------------------
# iota_mean
iota_mean = 0.003
#
# import
import os
import csv
import sys
import copy
import dismod_at
#
# import at_cascade with a preference current directory version
current_directory = os.getcwd()
if os.path.isfile( current_directory + '/at_cascade/__init__.py' ) :
   sys.path.insert(0, current_directory)
import at_cascade
# ----------------------------------------------------------------------------
def root_node_db(file_name) :
   #
   # age_grid, time_grid
   age_grid  = [ 0.0, 100.0 ]
   time_grid = [ 2000.0 ]
   #
   # prior_table
   prior_table = list()
   prior_table.append(
      # parent_iota_value_prior
      {  'name':    'parent_iota_value_prior',
         'density': 'gaussian',
         'lower':   iota_mean / 10.0,
         'upper':   iota_mean * 10.0,
         'mean':    iota_mean,
         'std' :    iota_mean * 10,
      }
   )
   prior_table.append(
      # parent_dage_prior
      {  'name':    'parent_dage_prior',
         'density': 'gaussian',
         'mean':    0.0,
         'std':     1.0,
      }
   )
   #
   # smooth_table
   smooth_table = list()
   fun = lambda a, t : ('parent_iota_value_prior', 'parent_dage_prior', None)
   smooth_table.append({
      'name':       'parent_iota_smooth',
      'age_id':     [0],
      'time_id':    [0],
      'fun':        fun,
   })
   #
   # node_table
   node_table = [ { 'name':'n0',        'parent':''   } ]
   #
   # rate_table
   rate_table = [ { 'name': 'iota', 'parent_smooth':  'parent_iota_smooth' } ]
   #
   # covariate_table
   covariate_table = list()
   #
   # mulcov_table
   mulcov_table = list()
   #
   # subgroup_table
   subgroup_table = [ {'subgroup': 'world', 'group':'world'} ]
   #
   # integrand_table
   integrand_table = [ {'name': 'Sincidence'} ]
   #
   # avgint_table
   avgint_table = list()
   #
   # data_table
   data_table = list()
   row = {
      'subgroup':     'world',
      'weight':       '',
      'time_lower':   2000.0,
      'time_upper':   2000.0,
      'density':      'gaussian',
      'hold_out':     False,
      'integrand':    'Sincidence',
      'meas_std':     iota_mean * 1e-3,
      'node':         'n0',
   }
   for age in age_grid :
      row['age_lower']  = age
      row['age_upper']  = age
      row['meas_value'] = iota_mean
      row['meas_std']   = row['meas_value'] * 1e-2
      #
      data_table.append( copy.copy(row) )
   #
   # weight table:
   weight_table = list()
   #
   # nslist_table
   nslist_table = dict()
   #
   # option_table
   option_table = [
      { 'name':'parent_node_name',      'value':'n0'},
      { 'name':'rate_case',             'value':'iota_pos_rho_zero'},
   ]
   # ----------------------------------------------------------------------
   # create database
   dismod_at.create_database(
      file_name,
      age_grid,
      time_grid,
      integrand_table,
      node_table,
      subgroup_table,
      weight_table,
      covariate_table,
      avgint_table,
      data_table,
      prior_table,
      smooth_table,
      nslist_table,
      rate_table,
      mulcov_table,
      option_table
   )
# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------
def main() :
   # -------------------------------------------------------------------------
   # result_dir
   result_dir = 'build/test'
   at_cascade.empty_directory(result_dir)
   #
   # root_node_database
   root_node_database  = f'{result_dir}/root_node.db'
   root_node_db(root_node_database)
   #
   # fit_node_database
   fit_node_database  = f'{result_dir}/fit_node.db'
   at_cascade.copy_root_db(root_node_database, fit_node_database)
   #
   # fit_node_database
   at_cascade.copy_other_tbl(fit_node_database)
   #
   # root_node_database
   os.remove( root_node_database )
   #
   # fit_node_database
   command = [ 'dismod_at' , fit_node_database, 'init' ]
   dismod_at.system_command_prc( command, print_command = False )
   #
   # db2csv_command
   dismod_at.db2csv_command( fit_node_database )
   #
   # data_table
   file_obj   = open( f'{result_dir}/data.csv' , 'r' )
   reader     = csv.DictReader( file_obj )
   data_table = list()
   for row in reader :
      data_table.append(row)
   file_obj.close()
   #
   assert len( data_table ) == 2
   assert row['integrand'] == 'Sincidence'
   assert float( row['meas_value'] ) == iota_mean

#
main()
print('copy_other_tbl: OK')
sys.exit(0)
# END no_ode_xam source code
