# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ----------------------------------------------------------------------------
# BEGIN no_ode_xam source code
# ----------------------------------------------------------------------------
# imports
# ----------------------------------------------------------------------------
import sys
import os
import copy
import time
import csv
import random
import numpy
import shutil
import dismod_at
import math
#
# import at_cascade with a preference current directory version
current_directory = os.getcwd()
if os.path.isfile( current_directory + '/at_cascade/__init__.py' ) :
   sys.path.insert(0, current_directory)
import at_cascade
# -----------------------------------------------------------------------------
# global variables
# -----------------------------------------------------------------------------
#
# fit_goal_set
fit_goal_set = { 'n0' }
#
# random_seed
random_seed = 0
if random_seed == 0 :
   random_seed = int( time.time() )
random.seed(random_seed)
#
# iota_no_effect, chi_no_effect
iota_no_effect    = 0.015
chi_no_effect     = 0.025
rho_no_effect     = 0.035
#
# alpha_true, alpha_true_max_abs
alpha_true         = { 'iota':- 0.25, 'chi':-0.15, 'rho' :-0.10 }
alpha_true_max_abs = 0.25
#
# avg_income
avg_income       = 1.5
#
# income_grid
income_grid   =  [ 0.5, 1.0, 1.5, 2.0,  2.5]
# ----------------------------------------------------------------------------
# functions
# ----------------------------------------------------------------------------
#
# rate_true
def rate_true(rate, income) :
   if rate in [ 'pini' ] :
      return 0.0
   effect   = alpha_true[rate] * ( income - avg_income )
   if rate == 'iota' :
      return iota_no_effect * math.exp( effect  )
   if rate == 'chi' :
      return chi_no_effect * math.exp( effect  )
   if rate == 'rho' :
      return rho_no_effect * math.exp( effect  )
   assert False
# ----------------------------------------------------------------------------
def root_node_db(file_name) :
   #
   # age_grid, time_grid
   age_grid = [ 0.0, 20.0, 40.0, 60.0, 80.0, 100.0 ]
   time_grid = [ 2000.0, 2020.0 ]
   #
   # prior_table
   prior_table = list()
   #
   prior_table.append(
      # parent_iota_value_prior
      {   'name':    'parent_iota_value_prior',
         'density': 'gaussian',
         'lower':   iota_no_effect / 10.0,
         'upper':   iota_no_effect * 10.0,
         'mean':    iota_no_effect * 2.0,
         'std' :    iota_no_effect * 10.0,
      }
   )
   prior_table.append(
      # parent_chi_value_prior
      {   'name':    'parent_chi_value_prior',
         'density': 'gaussian',
         'lower':   chi_no_effect / 10.0,
         'upper':   chi_no_effect * 10.0,
         'mean':    chi_no_effect * 2.0,
         'std':     chi_no_effect * 10.0,
      }
   )
   prior_table.append(
      # parent_rho_value_prior
      {   'name':    'parent_rho_value_prior',
         'density': 'gaussian',
         'lower':   rho_no_effect / 10.0,
         'upper':   rho_no_effect * 10.0,
         'mean':    rho_no_effect * 2.0,
         'std':     rho_no_effect * 10.0,
      }
   )
   prior_table.append(
      # alpha_value_prior
      {   'name':    'alpha_value_prior',
         'density': 'gaussian',
         'lower':   - 10 * alpha_true_max_abs,
         'upper':   + 10 * alpha_true_max_abs,
         'std'  :   10 * alpha_true_max_abs,
         'mean':    0.0,
      }
   )
   #
   # smooth_table
   smooth_table = list()
   #
   # parent_iota_smooth
   fun = lambda a, t : ('parent_iota_value_prior', None, None)
   smooth_table.append({
      'name':       'parent_iota_smooth',
      'age_id':     [0],
      'time_id':    [0],
      'fun':        fun,
   })
   #
   # parent_chi_smooth
   fun = lambda a, t : ('parent_chi_value_prior', None, None)
   smooth_table.append({
      'name':       'parent_chi_smooth',
      'age_id':     [0],
      'time_id':    [0],
      'fun':        fun,
   })
   #
   # parent_rho_smooth
   fun = lambda a, t : ('parent_rho_value_prior', None, None)
   smooth_table.append({
      'name':       'parent_rho_smooth',
      'age_id':     [0],
      'time_id':    [0],
      'fun':        fun,
   })
   #
   # alpha_smooth
   fun = lambda a, t : ('alpha_value_prior', None, None)
   smooth_table.append({
      'name':       'alpha_smooth',
      'age_id':     [0],
      'time_id':    [0],
      'fun':        fun,
   })
   #
   # node_table
   node_table = [ { 'name':'n0',        'parent':''   } ]
   #
   # rate_table
   rate_table = [ {
         'name':           'iota',
         'parent_smooth':  'parent_iota_smooth',
      },{
         'name':           'chi',
         'parent_smooth':  'parent_chi_smooth',
      },{
         'name':           'rho',
         'parent_smooth':  'parent_rho_smooth',
   } ]
   #
   # covariate_table
   covariate_table = [
      { 'name':'income',   'reference':avg_income },
   ]
   #
   # mulcov_table
   mulcov_table = [
      {   # alpha_iota
         'covariate':  'income',
         'type':       'rate_value',
         'effected':   'iota',
         'group':      'world',
         'smooth':     'alpha_smooth',
      },{ # alpha_chi
         'covariate':  'income',
         'type':       'meas_value',
         'effected':   'mtexcess',
         'group':      'world',
         'smooth':     'alpha_smooth',
      },{ # alpha_rho
         'covariate':  'income',
         'type':       'meas_value',
         'effected':   'remission',
         'group':      'world',
         'smooth':     'alpha_smooth',
      },
   ]
   #
   # subgroup_table
   subgroup_table = [ {'subgroup': 'world', 'group':'world'} ]
   #
   # integrand_table
   integrand_table = [
      {'name': 'Sincidence'},
      {'name': 'mtexcess' },
      {'name': 'remission' },
   ]
   for mulcov_id in range( len(mulcov_table) ) :
      integrand_table.append( { 'name': f'mulcov_{mulcov_id}' } )
   #
   # data_table
   avgint_table = list()
   row = {
      'node':         'n0',
      'subgroup':     'world',
      'weight':       '',
      'time_lower':   2000.0,
      'time_upper':   2000.0,
      'subgroup':     'world',
      'weight':       '',
      'time_lower':   2000.0,
      'time_upper':   2000.0,
      'density':      'gaussian',
      'hold_out':     False,
   }
   # data_table
   data_table = list()
   for (age_id, age) in enumerate( age_grid ) :
      for income in income_grid :
         row['age_lower']  = age
         row['age_upper']  = age
         row['income']     = income
         #
         row['integrand']  = 'Sincidence'
         row['meas_value'] = rate_true( 'iota', income )
         row['meas_std']   = row['meas_value'] / 5.0
         data_table.append( copy.copy(row) )
         #
         row['integrand']  = 'mtexcess'
         row['meas_value'] = rate_true( 'chi', income )
         row['meas_std']   = row['meas_value'] / 5.0
         data_table.append( copy.copy(row) )
         #
         row['integrand']  = 'remission'
         row['meas_value'] = rate_true( 'rho', income )
         row['meas_std']   = row['meas_value'] / 5.0
         data_table.append( copy.copy(row) )
   #
   # option_table
   option_table = [
      { 'name':'parent_node_name',      'value':'n0'},
      { 'name':'rate_case',             'value':'iota_pos_rho_pos'},
   ]
   # ----------------------------------------------------------------------
   # create database
   dismod_at.create_database(
      file_name        = file_name,
      age_list         = age_grid,
      time_list        = time_grid,
      integrand_table  = integrand_table,
      node_table       = node_table,
      subgroup_table   = subgroup_table,
      weight_table     = list(),
      covariate_table  = covariate_table,
      avgint_table     = list(),
      data_table       = data_table,
      prior_table      = prior_table,
      smooth_table     = smooth_table,
      nslist_dict      = dict(),
      rate_table       = rate_table,
      mulcov_table     = mulcov_table,
      option_table     = option_table
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
   # Create root.db
   root_database       = f'{result_dir}/root.db'
   root_node_db(root_database)
   #
   # no_ode_ignore
   no_ode_ignore = 'iota mtexcess'
   #
   # Create all_node.db
   all_node_database = f'{result_dir}/all_node.db'
   option_all        = {
      'result_dir'         : result_dir,
      'root_node_name'     : 'n0',
      'root_database' : root_database,
      'no_ode_ignore'      : no_ode_ignore,
   }
   at_cascade.create_all_node_db(
      all_node_database       = all_node_database,
      option_all              = option_all,
   )
   #
   # root_node_dir
   root_node_dir = f'{result_dir}/n0'
   os.mkdir(root_node_dir)
   #
   # no_ode_fit
   at_cascade.no_ode_fit(
      all_node_database  = all_node_database ,
      root_database      = root_database,
      option_all_dict    = option_all,
      fit_type           = 'fixed',
   )
   #
   # n0_database, no_ode_database
   no_ode_database  = f'{result_dir}/n0/no_ode/dismod.db'
   n0_database      = f'{result_dir}/n0/dismod.db'
   #
   # n0_database
   command = [ 'dismod_at', n0_database, 'init' ]
   dismod_at.system_command_prc(command)
   #
   # no_ode_variable
   dismod_at.db2csv_command(no_ode_database)
   file_name             = f'{result_dir}/n0/no_ode/variable.csv'
   file_obj              = open(file_name, 'r')
   reader                = csv.DictReader(file_obj)
   no_ode_variable = list()
   for row in reader :
      no_ode_variable.append(row)
   file_obj.close()
   #
   # n0_variable
   dismod_at.db2csv_command(n0_database)
   file_name             = f'{result_dir}/n0/variable.csv'
   file_obj              = open(file_name, 'r')
   reader                = csv.DictReader(file_obj)
   n0_variable = list()
   for row in reader :
      n0_variable.append(row)
   file_obj.close()
   #
   # check
   assert len(no_ode_variable) == len(n0_variable)
   for var_id in range( len(no_ode_variable) ) :
      no_ode_row = no_ode_variable[var_id]
      n0_row     = n0_variable[var_id]
      assert no_ode_row.keys() == n0_row.keys()
      #
      assert int( no_ode_row['var_id'] ) == var_id
      for key in n0_row :
         if key == 'mean_v' :
            #
            # ignore
            ignore = False
            if n0_row['var_type'] == 'rate' :
               ignore = n0_row['rate'] in no_ode_ignore.split()
            if n0_row['var_type'] == 'mulcov_rate_value' :
               ignore = n0_row['rate'] in no_ode_ignore.split()
            if n0_row['var_type'] == 'mulcov_meas_value' :
               ignore = n0_row['integrand'] in no_ode_ignore.split()
            #
            if ignore :
               assert n0_row['mean_v'] ==  no_ode_row['mean_v']
            else :
               assert n0_row['mean_v'] ==  no_ode_row['fit_value']
         elif key in [ 's_id' , 'start', 'scale' ] :
            pass
         else :
            assert n0_row[key] == '' or n0_row[key] == no_ode_row[key]
   #
if __name__ == '__main__' :
   main()
   print('no_ode_xam: OK')
# END no_ode_xam source code
