# -----------------------------------------------------------------------------
# at_cascade: Cascading Dismod_at Analysis From Parent To Child Regions
#           Copyright (C) 2021-21 University of Washington
#              (Bradley M. Bell bradbell@uw.edu)
#
# This program is distributed under the terms of the
#     GNU Affero General Public License version 3.0 or later
# see http://www.gnu.org/licenses/agpl.txt
# -----------------------------------------------------------------------------
'''
{xsrst_begin data4cov_reference}}

Use Data Table Average Covariates for Reference
###############################################

Syntax
******
{xsrst_file
    # BEGIN syntax
    # END syntax
}

connection
**********
This is a dismod_at connection to a dismod_at database.

data_subset Table
=================
This database must have a data_subset table.

covariate_table
================
The ``reference`` column in the covariate table is replaced
by the average of the corresponding covariate in the data table.
Only the data_id that appear in the data_subset table are included
in this average.
In addition, null covariate values in the data table
are not included in the average.

{xsrst_end data4cov_reference}}
'''
import dismod_at
#
# BEGIN syntax
# data4cov_reference(database)
# END syntax
def data4cov_reference(connection) :
    #
    # tables
    tables = dict()
    for tbl_name in [
        'data',
        'data_subset',
        'node',
        'covariate',
    ] :
        tables[tbl_name] = dismod_at.get_table_dict(connection, tbl_name)
    #
    # covariate_value
    n_covariate    = len( tables['covariate'] )
    covariate_value = list()
    covariate_label = list()
    for covariate_id in range( n_covariate ) :
        covariate_value.append( list() )
        covariate_label.append( f'x_{covariate_id}' )
    for subset_row in tables['data_subset'] :
        data_id  = subset_row['data_id']
        data_row = tables['data'][data_id]
        for covariate_id in range( n_covariate ) :
            value = data_row[ covariate_label[covariate_id] ]
            if not value is None :
                covariate_value[covariate_id].append(value)
    #
    # covariate_avg
    covariate_avg = list()
    for covariate_id in range( n_covariate ) :
        cov_list = covariate_value[covariate_id]
        if len( cov_list ) == 0 :
            covariate_avg.append(None)
        else :
            covariate_avg.append( sum(cov_list) / len(cov_list) )
    #
    # tables['covariate']
    for (covariate_id, row) in enumerate(tables['covariate']) :
        avg = covariate_avg[covariate_id]
        if not avg is None :
            row['reference'] = avg
    dismod_at.replace_table(connection, 'covariate', tables['covariate'])
    #
    return
