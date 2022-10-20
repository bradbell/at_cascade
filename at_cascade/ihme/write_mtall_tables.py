# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
import os
import csv
import at_cascade.ihme
#
# -----------------------------------------------------------------------------
def get_file_path(result_dir, csv_file_key) :
   csv_file  = at_cascade.ihme.csv_file
   file_name = csv_file[csv_file_key]
   file_name = f'{result_dir}/{file_name}'
   return file_name
# -----------------------------------------------------------------------------
#
# write_node_tables(result_dir)
# all_omega_table_file, omega_index_table_file, omega_age_table_file,
# omega_time_table_file.
def write_mtall_tables(result_dir) :
   #
   # global constants
   map_location_id         = at_cascade.ihme.map_location_id
   age_group_inp_file      = at_cascade.ihme.age_group_inp_file
   mtall_inp_file          = at_cascade.ihme.mtall_inp_file
   all_omega_table_file    = get_file_path(result_dir, 'all_omega')
   omega_index_table_file  = get_file_path(result_dir, 'omega_index')
   node_table_file         = get_file_path(result_dir, 'node')
   omega_age_table_file    = get_file_path(result_dir, 'omega_age')
   omega_time_table_file   = get_file_path(result_dir, 'omega_time')
   sex_info_dict           = at_cascade.ihme.sex_info_dict
   #
   # output_file_list
   output_file_list = [
      all_omega_table_file,
      omega_index_table_file,
      omega_age_table_file,
      omega_time_table_file,
   ]
   #
   # done
   print( f'Createing mtall_tables:')
   for file in output_file_list :
      print( '    ' + file )
   #
   # age_group_id_set, age_group_id_dict
   age_group_id_table = at_cascade.ihme.get_age_group_id_table()
   age_group_id_set   = set()
   age_group_id_dict  = dict()
   for row in age_group_id_table :
      age_group_id = row[ 'age_group_id' ]
      age_group_id_set.add( age_group_id )
      age_group_id_dict[age_group_id] = row
   #
   # sex_id2split_reference_id
   sex_id2split_reference_id = dict()
   for sex_name in sex_info_dict :
      sex_id             = sex_info_dict[sex_name]['sex_id']
      split_reference_id = sex_info_dict[sex_name]['split_reference_id']
      sex_id2split_reference_id[sex_id] = split_reference_id
   #
   # location_id2node_id
   file_ptr            = open(node_table_file)
   reader              = csv.DictReader(file_ptr)
   location_id2node_id = dict()
   node_id             = 0
   for row in reader :
      assert node_id == int( row['node_id'] )
      location_id = int( row['location_id'] )
      location_id2node_id[location_id] = node_id
      node_id += 1
   file_ptr.close()
   #
   # mtall_dict, age_group_id_subset
   file_ptr            = open(mtall_inp_file)
   reader              = csv.DictReader(file_ptr)
   mtall_dict          = dict()
   age_group_id_subset = set()
   for row in reader :
      age_group_id = int( row['age_group_id'] )
      if age_group_id in age_group_id_set :
         #
         # age_group_id_set
         age_group_id_subset.add( age_group_id )
         #
         # mtall_dict
         location_id  = int( row['location_id'] )
         sex_id       = int( row['sex_id'] )
         year_id      = int( row['year_id'] )
         val          = float( row['val'] )
         if location_id not in mtall_dict :
            mtall_dict[location_id] = dict()
         if sex_id not in mtall_dict[location_id] :
            mtall_dict[location_id][sex_id] = dict()
         if year_id not in mtall_dict[location_id][sex_id] :
            mtall_dict[location_id][sex_id][year_id] = dict()
         if age_group_id in mtall_dict[location_id][sex_id][year_id] :
            msg  = f'file = {mtall_inp_file}, with '
            msg += f'location_id = {location_id}, '
            msg += f'sex_id = {sex_id}, and '
            msg += f'year_id = {year_id}.\n'
            msg += f'The age_group_id {age_group_id} '
            msg += 'appears more than once.'
            assert False, msg
         mtall_dict[location_id][sex_id][year_id][age_group_id] = val
   #
   # age_group_id_set
   previous_location_id      = None
   previous_sex_id           = None
   previous_year_id          = None
   previous_age_group_id_set = None
   for location_id in mtall_dict :
      for sex_id in mtall_dict[location_id] :
         for year_id in mtall_dict[location_id][sex_id] :
            keys = mtall_dict[location_id][sex_id][year_id].keys()
            age_group_id_set = set(keys)
            if previous_age_group_id_set != age_group_id_set \
            and previous_age_group_id_set is not None :
               msg  = f'file = {mtall_inp_file}, '
               msg += f'location_id = {location_id}, '
               msg += f'sex_id = {sex_id}, '
               msg += f'year_id = {year_id}, '
               msg += f'age_group_id_set =\n{age_group_set}\n'
               msg += f'location_id = {previous_location_id}, '
               msg += f'sex_id = {previous_sex_id}, '
               msg += f'year_id = {previous_year_id}, '
               msg += f'age_group_id_set =\n {previous_age_group_set}'
               assert False, msg
            previous_location_id      = location_id
            previous_sex_id           = sex_id
            previous_year_id          = year_id
            previous_age_group_id_set = age_group_id_set
   assert age_group_id_set == age_group_id_subset
   #
   #
   # check year_id_set
   previous_location_id = None
   previous_sex_id      = None
   previous_year_id_set = None
   for location_id in mtall_dict :
      for sex_id in mtall_dict[location_id] :
         keys = mtall_dict[location_id][sex_id].keys()
         year_id_set = set( keys )
         if previous_year_id_set != year_id_set \
         and previous_year_id_set is not None :
            msg  = f'file = {mtall_inp_file}, '
            msg += f'location_id = {location_id}, '
            msg += f'sex_id = {sex_id}, '
            msg += f'year_id_set =\n{year_id_set}\n'
            msg += f'location_id = {previous_location_id}, '
            msg += f'sex_id = {previous_sex_id}, '
            msg += f'year_id_set = {previous_year_id_set}, '
            assert False, msg
         previous_location_id      = location_id
         previous_sex_id           = sex_id
         previous_year_id_set      = year_id_set
   #
   # year_id_list
   year_id_list = sorted( year_id_set )
   #
   # age_group_id_list
   fun = lambda age_group_id : age_group_id_dict[age_group_id]['age_mid']
   age_group_id_list = sorted( age_group_id_set, key = fun )
   #
   # omega_age_table
   omega_age_table  = list()
   for age_group_id in age_group_id_list :
      age_mid = age_group_id_dict[age_group_id]['age_mid']
      # used so can match after converting to ascii and back
      age_mid = round(age_mid, at_cascade.ihme.age_grid_n_digits)
      row = {
         'age_group_id' : age_group_id,
         'age'          : age_mid,
      }
      omega_age_table.append( row )
   #
   # omega_time_table
   omega_time_table  = list()
   for year_id in year_id_list :
      time = year_id + 0.5
      row = { 'time' : time }
      omega_time_table.append( row )
   #
   # mtall_dict
   for from_location_id in map_location_id :
      del mtall_dict[from_location_id]
   #
   # all_omega_table
   # omega_index_table
   all_omega_table   = list()
   omega_index_table = list()
   all_omega_id      = 0
   for location_id in mtall_dict :
      node_id = location_id2node_id[location_id]
      for sex_id in mtall_dict[location_id] :
         split_reference_id = sex_id2split_reference_id[sex_id]
         row = {
            'all_omega_id'       : all_omega_id,
            'node_id'            : node_id,
            'split_reference_id' : split_reference_id
         }
         omega_index_table.append(row)
         for age_group_id in age_group_id_list :
            for year_id in year_id_list :
               all_omega_value = \
                  mtall_dict[location_id][sex_id][year_id][age_group_id]
               row = {
                  'all_omega_id'    : all_omega_id,
                  'location_id'     : location_id,
                  'node_id'         : node_id,
                  'sex_id'          : sex_id,
                  'year_id'         : year_id,
                  'age_group_id'    : age_group_id,
                  'all_omega_value' : all_omega_value ,
               }
               all_omega_table.append(row)
               all_omega_id += 1
   #
   # all_omega_table_file
   at_cascade.csv.write_table(all_omega_table_file, all_omega_table)
   #
   # omega_index_table_file
   at_cascade.csv.write_table(omega_index_table_file, omega_index_table)
   #
   # omega_age_table_file
   at_cascade.csv.write_table(omega_age_table_file, omega_age_table)
   #
   # omega_time_table_file
   at_cascade.csv.write_table(omega_time_table_file, omega_time_table)
