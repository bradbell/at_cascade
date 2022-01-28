# -----------------------------------------------------------------------------
# at_cascade: Cascading Dismod_at Analysis From Parent To Child Regions
#           Copyright (C) 2021-22 University of Washington
#              (Bradley M. Bell bradbell@uw.edu)
#
# This program is distributed under the terms of the
#     GNU Affero General Public License version 3.0 or later
# see http://www.gnu.org/licenses/agpl.txt
# -----------------------------------------------------------------------------
'''
{xsrst_begin replace_avgint}

Replace The Avgint Table
########################

Syntax
******
{xsrst_file
    # BEGIN syntax
    # END syntax
}

connection
**********
is a dismod_at open connection to the database.

n_covariate
***********
is the number of covariates in the avgint table.

avgint_table
************
is a ``list`` of ``dict`` containing the new values for the
avgint table. Only the columns required by dismod_at are included.
This list can be empty.

message
*******
a log table entry is added with :ref:`add_log_entry.message`
equal to this ``str``.

{xsrst_end   replace_avgint}
'''
import time
import dismod_at
import at_cascade
# ----------------------------------------------------------------------------
# BEGIN syntax
def replace_avgint(connection, n_covariate, avgint_table, message) :
# END syntax
    #
    command     = 'DROP TABLE IF EXISTS avgint'
    dismod_at.sql_command(connection, command)
    #
    # col_name
    col_name = [
        'integrand_id',
        'node_id',
        'subgroup_id',
        'weight_id',
        'age_lower',
        'age_upper',
        'time_lower',
        'time_upper',
    ]
    for covariate_id in range(n_covariate) :
        col_name.append(f'x_{covariate_id}')
    #
    # col_type
    col_type = [
        'integer',
        'integer',
        'integer',
        'integer',
        'real',
        'real',
        'real',
        'real',
    ]
    for covariate_id in range(n_covariate) :
        col_type.append('real')
    #
    # row_list
    row_list = list()
    for row_in in avgint_table :
        row_out = list()
        for col in col_name :
            row_out.append( row_in[col] )
        row_list.append( row_out )
    #
    # create_table
    tbl_name = 'avgint'
    dismod_at.create_table(
        connection, tbl_name, col_name, col_type, row_list
    )
    #
    at_cascade.add_log_entry(connection, message)
