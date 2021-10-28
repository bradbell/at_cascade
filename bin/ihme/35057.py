#! /usr/bin/python3
# -----------------------------------------------------------------------------
# at_cascade: Cascading Dismod_at Analysis From Parent To Child Regions
#           Copyright (C) 2021-21 University of Washington
#              (Bradley M. Bell bradbell@uw.edu)
#
# This program is distributed under the terms of the
#     GNU Affero General Public License version 3.0 or later
# see http://www.gnu.org/licenses/agpl.txt
# -----------------------------------------------------------------------------
root_node_database = '../475876/dismod.db'
all_node_database  = '../475876/all_node.db'
new_data_csv       = '../csv/35057/data.csv'
new_node_csv       = '../csv/35057/node.csv'
# -----------------------------------------------------------------------------
import csv
import sys
import os
import distutils.dir_util
import shutil
import dismod_at
# -----------------------------------------------------------------------------
def get_table_csv(file_name) :
    file_ptr   = open(file_name)
    reader     = csv.DictReader(file_ptr)
    table      = list()
    for row in reader :
        table.append(row)
    return table
# -----------------------------------------------------------------------------
#
# import at_cascade with a preference current directory version
current_directory = os.getcwd()
if os.path.isfile( current_directory + '/at_cascade/__init__.py' ) :
    sys.path.insert(0, current_directory)
import at_cascade
#
# work_dir
work_dir = 'ihme_db/35057'
distutils.dir_util.mkpath(work_dir)
os.chdir(work_dir)
#
# create data_cvs and node_cvs
if not ( os.path.exists(new_data_csv) and os.path.exists(new_node_csv) ) :
    os.chdir('../../')
    dismod_at.system_command_prc( [ 'bin/ihme/csv/35057.py' ] )
    os.chdir(work_dir)
#
# max_fit
max_fit = 250
#
# all_node_copy
all_node_copy = 'all_node_copy.db'
shutil.copyfile(all_node_database, all_node_copy)
#
# root_node_copy
root_node_copy =  'root_node_copy.db'
shutil.copyfile(root_node_database, root_node_copy)
#
# root_node_dir
root_node_dir = 'Global'
if os.path.exists(root_node_dir) :
    # rmtree is very dangerous so make sure root_node_dir is as expected
    os.chdir('../..')
    assert work_dir == 'ihme_db/35057'
    shutil.rmtree(work_dir + '/' + root_node_dir)
    os.chdir(work_dir)
os.makedirs(root_node_dir )
#
# connect_all, connect_root
new          = False
connect_all  = dismod_at.create_connection(all_node_copy, new)
connect_root = dismod_at.create_connection(root_node_copy, new)
#
# node_table
new_node_table = get_table_csv( new_node_csv )
old_node_table = dismod_at.get_table_dict(connect_root, 'node')
not_found_list = list()
for old_row in old_node_table :
    old_node_name = old_row['node_name']
    old_node_name = old_node_name.replace(' ', '_')
    old_node_name = old_node_name.replace("'", '_')
    found = False
    for new_row in new_node_table :
        if new_row['node_name'] == old_node_name :
            found = True
    if not found :
        not_found_list.append( old_node_name )
print(not_found_list)
#
print('35057.py: OK')
sys.exit(0)
