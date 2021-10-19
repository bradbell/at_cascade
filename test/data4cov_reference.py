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
    # ------------------------------------------------------------------------
    # all_node_database
    all_node_database = 'all_node.db'
    #
    # connection
    new        = True
    connection = dismod_at.create_connection(all_node_database, new)
    #
    # split_reference_list
    split_reference_list = [ -0.5, 0.0, 0.5 ]
    #
    # all_option table
    tbl_name = 'all_option'
    col_name = [ 'option_name', 'option_value' ]
    col_type = [ 'text',        'text'         ]
    split_level          = '-1 '
    split_covariate_name = 'sex '
    split_list = split_level + split_covariate_name
    for reference in split_reference_list :
        split_list += ' ' + str(reference)
    row_list = [
        [ 'split_list', split_list ]
    ]
    dismod_at.create_table(
        connection, tbl_name, col_name, col_type, row_list
    )
    #
    # all_cov_reference table
    tbl_name = 'all_cov_reference'
    col_name = ['node_id', 'covariate_id', 'split_reference_id', 'reference']
    col_type = ['integer', 'integer',      'integer',            'real'     ]
    row_list = list()
    for node_id in range(4) :
        for (k, sex_reference)  in enumerate(split_reference_list) :
            split_reference_id = str(k)
            #
            covariate_id = '0' # sex
            row = [ node_id, covariate_id, split_reference_id, sex_reference ]
            row_list.append(row)
            #
            covariate_id  = '1' # bmi
            row = [ str(node_id), covariate_id, split_reference_id, '100.0' ]
            row_list.append(row)
    dismod_at.create_table(
        connection, tbl_name, col_name, col_type, row_list
    )
    connection.close()
    #
    # ------------------------------------------------------------------------
    # root_node_database
    root_node_database  = 'root_node.db'
    #
    # connection
    connection.close()
    new        = True
    connection = dismod_at.create_connection(root_node_database, new)
    #
    # option table
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
    # node table
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
    #
    # covariate table
    split_reference_id = 1
    tbl_name = 'covariate'
    col_name = [ 'covariate_name', 'reference', 'max_difference' ]
    col_type = [ 'text',           'real',      'real'           ]
    row_list = [
        [ 'sex',   split_reference_list[split_reference_id],   0.6 ],
        [ 'bmi',   10.0,                                       None ],
    ]
    dismod_at.create_table(
        connection, tbl_name, col_name, col_type, row_list
    )
    #
    # data table
    tbl_name = 'data'
    col_name = [ 'node_id', 'x_0',  'x_1'  ]
    col_type = [ 'integer', 'real', 'real' ]
    row_list = [
        [ 1, 1.0, 1e4 ], # sex does not satisfy max_difference
        [ 0, 0.0, 0.0 ], # include in average for node_id >= 0
        [ 1, 0.5, 1.0 ], # included in average for node_id >= 1
        [ 2, 0.5, 2.0 ], # included in average for node_id >= 2
        [ 3, 0.5, 3.0 ], # included in average for node_id >= 3
    ]
    dismod_at.create_table(
        connection, tbl_name, col_name, col_type, row_list
    )
    # ------------------------------------------------------------------------
    #
    # data4cov_reference
    at_cascade.data4cov_reference(
        all_node_database  = all_node_database,
        root_node_database = root_node_database
    )
    #
    # all_cov_reference_table
    new             = False
    connection      = dismod_at.create_connection(all_node_database, new)
    all_cov_reference_table = dismod_at.get_table_dict(
        connection, 'all_cov_reference'
    )
    #
    # check
    for row in all_cov_reference_table :
        node_id            = row['node_id']
        covariate_id       = row['covariate_id']
        split_reference_id = row['split_reference_id']
        reference          = row['reference']
        same               = node_id == 0 or split_reference_id != 1
        if covariate_id == 0 :
            assert reference == split_reference_list[split_reference_id]
        else :
            if split_reference_id != 1 :
                assert reference == 100.0
            else :
                avg = sum( range(node_id, 4) ) / (4 - node_id)
                assert reference == avg
main()
print('data4cov_reference: OK')
sys.exit(0)
