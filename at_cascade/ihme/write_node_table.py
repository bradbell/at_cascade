# -----------------------------------------------------------------------------
# at_cascade: Cascading Dismod_at Analysis From Parent To Child Regions
#           Copyright (C) 2021-21 University of Washington
#              (Bradley M. Bell bradbell@uw.edu)
#
# This program is distributed under the terms of the
#     GNU Affero General Public License version 3.0 or later
# see http://www.gnu.org/licenses/agpl.txt
# -----------------------------------------------------------------------------
import os
import csv
import at_cascade.ihme
# -----------------------------------------------------------------------------
#
# write_node_table()
def write_node_table() :
    node_table_file = at_cascade.ihme.node_table_file
    if os.path.exists(node_table_file) :
        print( f'Using existing {node_table_file}' )
        return
    else :
        print( f'Creating {node_table_file}' )
    #
    # location_table
    file_ptr        = open(at_cascade.ihme.location_csv_file)
    reader          = csv.DictReader(file_ptr)
    location_table  = list()
    location_id_set = set()
    for row_in in reader :
        #
        location_id   = int( row_in['location_id'] )
        assert location_id not in location_id_set
        location_id_set.add(location_id)
        #
        location_name = row_in['location_name']
        location_name = location_name.replace(' ',  '_')
        location_name = location_name.replace('\'', '_')
        #
        parent_id     = int( row_in['parent_id'] )
        #
        row_out = {
            'location_id':    location_id,
            'location_name':  location_name,
            'parent_id':      parent_id,
        }
        #
        location_table.append( row_out )
    file_ptr.close()
    #
    # location_id2node_id
    location_id2node_id = dict()
    for (node_id, row_in) in enumerate( location_table ) :
        location_id   = row_in['location_id']
        location_id2node_id[location_id] = node_id
    #
    # node_table
    node_table = list()
    for (node_id, row_in) in enumerate( location_table ) :
        location_id   = row_in['location_id']
        parent_id     = row_in['parent_id']
        location_name = row_in['location_name']
        #
        node_name = f'{location_id}_{location_name}'
        if parent_id == location_id :
            parent = None
        else :
            parent = location_id2node_id[parent_id]
        #
        row_out = {
            'node_id':       node_id,
            'node_name':     node_name,
            'parent':        parent,
            'location_id':   location_id,
        }
        node_table.append(row_out)
    #
    at_cascade.ihme.write_csv(node_table_file, node_table)
