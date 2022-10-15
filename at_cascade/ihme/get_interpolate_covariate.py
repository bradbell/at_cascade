# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
import numpy
import csv
from scipy.interpolate import  UnivariateSpline
from scipy.interpolate import  RectBivariateSpline
import at_cascade.ihme
# -----------------------------------------------------------------------------
def check_rectangular_grid(covariate_file_path, covariate_table) :
   #
   # grid
   grid = dict()
   for row in covariate_table :
      location_id  = row['location_id']
      sex_name     = row['sex_name']
      age_group_id = row['age_group_id']
      year_id      = row['year_id']
      if location_id not in grid :
         grid[location_id] = dict()
      if sex_name not in grid[location_id] :
         grid[location_id][sex_name] = dict()
      if year_id not in grid[location_id][sex_name] :
         grid[location_id][sex_name][year_id] = set()
      if age_group_id in grid[location_id][sex_name][year_id] :
         msg  = f'Error in {covariate_file_path}\n'
         msg += f'For location_id = {location_id}, sex = {sex_name}, '
         msg += f'year_id = {year_id}.\n'
         msg += f'The age_group_id = {age_group_id} appears more than once'
      grid[location_id][sex_name][year_id].add( age_group_id )
   #
   for location_id in grid :
      for sex_name in grid[location_id] :
         previous_age_group_id_set  = None
         previous_year_id           = None
         for year_id in grid[location_id][sex_name] :
            age_group_id_set = grid[location_id][sex_name][year_id]
            if previous_age_group_id_set is None :
               previous_age_group_id_set  = age_group_id_set
               previous_year_id           = year_id
            elif previous_age_group_id_set != age_group_id_set :
               msg  = f'Error in {covariate_file_path}\n'
               msg += f'For location_id = {location_id}, '
               msg += f'sex = {sex_name}.\n'
               #
               msg += f'The set of age_group_id for year_id = '
               msg += f'{previous_year_id} is\n'
               msg += f'{previous_age_group_id_set}\n'
               #
               msg += f'The set of age_group_id for year_id = '
               msg += f'{year_id} is\n'
               msg += f'{age_group_id_set}\n'
               #
               assert False, msg
            previous_age_group_id_set  = age_group_id_set
            previous_year_id           = year_id
# -----------------------------------------------------------------------------
# (one_age_group, interpolate_covariate)  = get_interpolate_covariate(
#  covaraite_csv_file, scale, age_group_id_dict
# )
def get_interpolate_covariate(
      covariate_file_path, scale, age_group_id_dict
) :
   assert type(covariate_file_path) == str
   assert scale is None or callable(scale)
   assert type(age_group_id_dict) == dict
   #
   file_ptr   = open(covariate_file_path)
   reader     = csv.DictReader(file_ptr)
   #
   # covariate_table
   covariate_table = list()
   for row in reader :
      #
      # age_group_id
      age_group_id = int( row['age_group_id'] )
      #
      # location_id
      location_id  = int( row['location_id'] )
      #
      # year_id
      year_id  = int( row['year_id'] )
      #
      # sex_name
      sex_name = row['sex']
      #
      # mean_value
      mean_value = float( row['mean_value'] )
      if scale is not None :
         mean_value = scale( mean_value )
      #
      # covariate_table
      row = {
         'age_group_id' : age_group_id,
         'location_id' :  location_id,
         'year_id' :      year_id,
         'sex_name' :     sex_name,
         'mean_value' :   mean_value,
      }
      covariate_table.append(row)
   #
   # age_group_id_set
   age_group_id_set = set()
   for row in covariate_table :
      age_group_id_set.add( row['age_group_id'] )
   #
   # one_age_group
   one_age_group = len( age_group_id_set ) == 1
   if not one_age_group :
      aggregate_age_group_id_set = at_cascade.ihme.aggregate_age_group_id_set
      temp = age_group_id_set.intersection(aggregate_age_group_id_set)
      assert len( temp ) == 0
   #
   # triple_list
   triple_list = dict()
   for row in covariate_table :
      #
      # location_id
      location_id = row['location_id']
      if location_id not in triple_list :
         triple_list[location_id] = dict()
      #
      # sex_name
      sex_name = row['sex_name']
      if sex_name not in triple_list[location_id] :
         triple_list[location_id][sex_name] = list()
      #
      # age
      if one_age_group :
         age = 0.0
      else :
         age_group_id = row['age_group_id']
         age          = age_group_id_dict[age_group_id]['age_mid']
      #
      # time
      time = row['year_id'] + 0.5
      #
      # mean_value
      mean_value  = row['mean_value']
      #
      # triple_list
      triple = (age, time, mean_value)
      triple_list[location_id][sex_name].append( triple )
   #
   # interpolate_covariate
   interpolate_covariate = dict()
   #
   # location_id
   for location_id in triple_list :
      interpolate_covariate[location_id] = dict()
      #
      # sex_name
      for sex_name in triple_list[location_id] :
         #
         # triple_list
         this_list = triple_list[location_id][sex_name]
         this_list = sorted(this_list)
         triple_list[location_id][sex_name] = this_list
         #
         # age_grid, time_grid
         age_set  = set()
         time_set = set()
         for triple in this_list :
            age_set.add( triple[0] )
            time_set.add( triple[1] )
         age_grid  = sorted(age_set)
         time_grid = sorted(time_set)
         #
         # n_age, n_time
         n_age  = len(age_grid)
         n_time = len(time_grid)
         #
         # one_age_group
         if one_age_group :
            assert n_age == 1
            #
            # covariate_grid
            covariate_grid = list()
            for triple in this_list :
               covariate_grid.append( triple[2] )
            #
            # interpolate_covariate
            spline =  UnivariateSpline(
               time_grid, covariate_grid, k = 1, s = 0.0, ext = 3
            )
            interpolate_covariate[location_id][sex_name] = spline
         #
         else :
            assert n_age > 1
            #
            # covariate_grid
            covariate_grid    = numpy.empty( (n_age, n_time) )
            covariate_grid[:] = numpy.nan
            #
            # covariate_grid
            for (index, triple) in enumerate(this_list) :
               # age, time
               age        = triple[0]
               time       = triple[1]
               #
               # age_index, time_index
               age_index  = int( index / n_time )
               time_index = index % n_time
               #
               # check_rectangular_grid
               if age  != age_grid[age_index] \
               or time != time_grid[time_index ] :
                  check_rectangular_grid(
                     covariate_file_path,
                     covariate_table
                  )
                  assert False
               #
               covariate_grid[age_index][time_index] = triple[2]
            #
            # interpolate_covariate
            spline= RectBivariateSpline(
               age_grid, time_grid, covariate_grid, kx=1, ky=1, s=0
            )
            interpolate_covariate[location_id][sex_name] = spline
         #
   return (one_age_group, interpolate_covariate)
