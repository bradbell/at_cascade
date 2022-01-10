# -----------------------------------------------------------------------------
# at_cascade: Cascading Dismod_at Analysis From Parent To Child Regions
#           Copyright (C) 2021-22 University of Washington
#              (Bradley M. Bell bradbell@uw.edu)
#
# This program is distributed under the terms of the
#     GNU Affero General Public License version 3.0 or later
# see http://www.gnu.org/licenses/agpl.txt
# -----------------------------------------------------------------------------
import os
import csv
import dismod_at
import at_cascade.ihme
# -----------------------------------------------------------------------------
#
def write_mulcov_freeze_table(
    result_dir, mulcov_freeze_list, root_node_database
) :
    #
    # mulcov_freeze_table_file
    mulcov_freeze_table_file = at_cascade.ihme.csv_file['mulcov_freeze']
    mulcov_freeze_table_file = f'{result_dir}/{mulcov_freeze_table_file}'
    if os.path.exists(mulcov_freeze_table_file) :
        print( f'Using existing {mulcov_freeze_table_file}' )
        return
    else :
        print( f'Creating {mulcov_freeze_table_file}' )
    #
    # root_table
    new        = False
    connection = dismod_at.create_connection(root_node_database, new)
    root_table = dict()
    for tbl_name in [ 'covariate', 'mulcov', 'node', 'rate' ] :
        root_table[tbl_name] = dismod_at.get_table_dict(connection, tbl_name)
    connection.close()
    #
    # mulcov_freeze_table
    mulcov_freeze_table = list()
    for row_in in mulcov_freeze_list :
        #
        # rate_name, covariate_name, node_name, sex
        rate_name      = row_in['rate']
        covariate_name = row_in['covariate']
        node_name      = row_in['node']
        sex_name       = row_in['sex']
        #
        # rate_id
        rate_id        = at_cascade.table_name2id(
            root_table['rate'], 'rate', rate_name
        )
        # covariate_id
        covariate_id   = at_cascade.table_name2id(
            root_table['covariate'], 'covariate', covariate_name
        )
        # fit_node_id
        fit_node_id    = at_cascade.table_name2id(
            root_table['node'], 'node', node_name
        )
        #
        # mulcov_id
        mulcov_id = None
        for (row_id, row) in enumerate(root_table['mulcov']) :
            if row['mulcov_type'] == 'rate_value' :
                if row['rate_id'] == rate_id :
                    if row['covariate_id'] == covariate_id :
                        mulcov_id = row_id
        assert mulcov_id is not None
        #
        # split_reference_id
        sex_info_dict      = at_cascade.ihme.sex_info_dict
        split_reference_id = sex_info_dict[sex_name]['split_reference_id']
        #
        # row_out
        row_out = {
            'fit_node_id'        : fit_node_id ,
            'split_reference_id' : split_reference_id,
            'mulcov_id'          : mulcov_id,
        }
        mulcov_freeze_table.append( row_out )
    #
    #
    # mulcov_freeze_table_file
    fieldnames = [ 'fit_node_id', 'split_reference_id', 'mulcov_id' ]
    at_cascade.ihme.write_csv(
       file_name   = mulcov_freeze_table_file,
        table      = mulcov_freeze_table,
        fieldnames = fieldnames,
    )
