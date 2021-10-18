# -----------------------------------------------------------------------------
# at_cascade: Cascading Dismod_at Analysis From Parent To Child Regions
#           Copyright (C) 2021-21 University of Washington
#              (Bradley M. Bell bradbell@uw.edu)
#
# This program is distributed under the terms of the
#     GNU Affero General Public License version 3.0 or later
# see http://www.gnu.org/licenses/agpl.txt
# ----------------------------------------------------------------------------
# imports
# ----------------------------------------------------------------------------
import sys
import os
import distutils.dir_util
import dismod_at
#
# import at_cascade with a preference current directory version
current_directory = os.getcwd()
if os.path.isfile( current_directory + '/at_cascade/__init__.py' ) :
    sys.path.insert(0, current_directory)
import at_cascade
#
# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------
def main() :
    # -------------------------------------------------------------------------
    # change into the build/test directory
    distutils.dir_util.mkpath('build/test')
    os.chdir('build/test')
    #
    # database
    database  = 'root_node.db'
    #
    # connection
    new        = True
    connection = dismod_at.create_connection(database, new)
    #
    # option_table
    tbl_name = 'option'
    col_name = [ 'option_name', 'option_value' ]
    col_type = [ 'text',        'text'         ]
    row_list = [
        [ 'parent_node_name', 'n1' ]
    ]
    dismod_at.create_table(
        connection, tbl_name, col_name, col_type, row_list
    )
    #
    # node_table
    tbl_name = 'node'
    col_name = [ 'node_name', 'parent'  ]
    col_type = [ 'text',      'integer' ]
    row_list = [
        [ 'n0', None ] ,
        [ 'n1', 0    ] ,
        [ 'n2', 1    ] ,
        [ 'n3', 2    ] ,
    ]
    dismod_at.create_table(
        connection, tbl_name, col_name, col_type, row_list
    )
    #
    # covariate_table
    tbl_name = 'covariate'
    col_name = [ 'covariate_name', 'reference', 'max_difference' ]
    col_type = [ 'text',           'real',      'real'           ]
    row_list = [
        [ 'sex',   0.0,   0.6 ],
        [ 'bmi',   10.0,  None ],
    ]
    dismod_at.create_table(
        connection, tbl_name, col_name, col_type, row_list
    )
    #
    # data_table
    tbl_name = 'data'
    col_name = [ 'node_id', 'x_0',  'x_1'  ]
    col_type = [ 'integer', 'real', 'real' ]
    row_list = [
        [ 0, 0.0, 1e4 ], # node not descendant of parent node
        [ 1, 1.0, 1e4 ], # sex does not satisfy max_difference
        [ 1, 0.5, 1.0 ], # included in average
        [ 2, 0.5, 2.0 ], # included in average
        [ 3, 0.5, 3.0 ], # included in average
    ]
    dismod_at.create_table(
        connection, tbl_name, col_name, col_type, row_list
    )
    #
    # data4cov_reference
    at_cascade.data4cov_reference(connection)
    #
    # covariate_table
    covariate_table = dismod_at.get_table_dict(connection, 'covariate')
    #
    # check
    check = [
        {'covariate_name': 'sex', 'reference': 0.0, 'max_difference': 0.6},
        {'covariate_name': 'bmi', 'reference': 2.0, 'max_difference': None},
    ]
    assert covariate_table == check
main()
print('data4cov_reference: OK')
sys.exit(0)
