# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
import re
import os
import csv
import at_cascade.ihme
# -----------------------------------------------------------------------------
#
# write_node_table()
# creates at_cascade.ihme.node_table_file
def write_node_table(result_dir) :
   #
   # map_locaiton_id
   map_location_id = at_cascade.ihme.map_location_id
   #
   # node_table_file
   node_table_file = at_cascade.ihme.csv_file['node']
   node_table_file = f'{result_dir}/{node_table_file}'
   print( f'Creating {node_table_file}' )
   #
   # location_table
   file_ptr         = open(at_cascade.ihme.location_inp_file)
   reader           = csv.DictReader(file_ptr)
   location_dict    = dict()
   location_id_list = list()
   for row_in in reader :
      #
      # location_id
      location_id   = int( row_in['location_id'] )
      #
      # location_name
      location_name = row_in['location_name']
      location_name = location_name.replace(' ',  '_')
      location_name = location_name.replace('\'', '_')
      pattern       = r'_[(][^)]*[)]'
      replace       = ''
      location_name = re.sub(pattern, replace, location_name)
      #
      # parent_id
      parent_id     = int( row_in['parent_id'] )
      #
      # location_dict
      row = {
         'location_name':  location_name,
         'parent_id':      parent_id,
         'child_list':     list(),
      }
      #
      location_dict[location_id] = row
      #
      # location_dict
      # assume parents come before children
      if parent_id != location_id :
         location_dict[parent_id]['child_list'].append(location_id)
      #
      # location_id_list
      assert location_id not in location_id_list
      if location_id not in map_location_id :
         location_id_list.append(location_id)
   file_ptr.close()
   #
   for location_id in location_id_list :
      child_list = location_dict[location_id]['child_list']
      if len(child_list) == 1 :
         child_id = child_list[0]
         msg  = f'{node_table_file}\n'
         msg += f'location_id = {location_id} has one child = {child_id}\n'
         msg += f'use map_location_id to map {location_id} t0 {child_id}'
         assert False, msg
   #
   # location_dict
   for from_location_id in map_location_id :
      to_location_id = map_location_id[from_location_id]
      #
      row_from       = location_dict[from_location_id]
      row_to         = location_dict[to_location_id]
      #
      parent_id      = row_to['parent_id']
      assert parent_id == from_location_id
      #
      from_name      = row_from['location_name']
      to_name        = row_to['location_name']
      assert from_name == to_name
      #
      # change to parent_id to grand parent id
      row_to['parent_id'] = row_from['parent_id']
   #
   # location_id2node_id
   location_id2node_id = dict()
   for (node_id, location_id) in enumerate( location_id_list ) :
      location_id2node_id[location_id] = node_id
   #
   # node_table
   node_table = list()
   for (node_id, location_id) in enumerate( location_id_list ) :
      row           = location_dict[location_id]
      parent_id     = row['parent_id']
      location_name = row['location_name']
      #
      node_name = f'{location_id}_{location_name}'
      if parent_id == location_id :
         parent_node_id = None
      else :
         parent_node_id = location_id2node_id[parent_id]
      #
      row_out = {
         'node_id':          node_id,
         'node_name':        node_name,
         'parent_node_id':   parent_node_id,
         'location_id':      location_id,
      }
      node_table.append(row_out)
   #
   at_cascade.csv.write_table(node_table_file, node_table)
