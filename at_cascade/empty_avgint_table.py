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
{xsrst_begin empty_avgint_table}

Create An Empty avgint Table
############################

Syntax
******
{xsrst_file
    # BEGIN syntax
    # END syntax
}

connection
**********
is a dismod_at open connection to the database.

covariate Table
***************
There must be a covariate table in the database so
this procedure can determine the number of covariates.

avgint Table
************
Any previous avgint table is lost.

log Table
*********
The message ``empty_avgint_table`` is added at the end of the log table
with message type ``at_cascade``.

{xsrst_end   empty_avgint_table}
'''
import time
import dismod_at
import at_cascade
# ----------------------------------------------------------------------------
# BEGIN syntax
def empty_avgint_table(connection) :
# END syntax
# ----------------------------------------------------------------------------
    #
    # n_covariate
    covariate_table = dismod_at.get_table_dict(connection, 'covariate')
    n_covariate     = len(covariate_table)
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
    # create_table
    row_list = list()
    tbl_name = 'avgint'
    dismod_at.create_table(
        connection, tbl_name, col_name, col_type, row_list
    )
    #
    # add_log_entry
    message = 'empty_avgint_table'
    at_cascade.add_log_entry(connection, message)
