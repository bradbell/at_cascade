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
{xsrst_begin table_name2id}
{xsrst_spell
    tbl
}

Map a Table Row Name to The Row Index
#####################################

Syntax
******
{xsrst_file
    # BEGIN syntax
    # END syntax
}

table
*****
This is a ``list`` of ``dict`` containing the table.
The primary key is not included because it is the row index.

tbl_name
********
This is a ``str`` containing the name of the table.
This table must have a column named *table_name*\ ``_name``.

row_name
********
This is the value we are searching for in the
*table_name*\ ``_name`` column.

row_id
******
This is the index of the row in the table where
*row_name* occurs. An assert will occur if there is no such row.

{xsrst_end table_name2id}
'''
# -----------------------------------------------------------------------------
def table_name2id(
# BEGIN syntax
# row_id = at_cascade.table_name2id(
    table, tbl_name, row_name
# )
# END syntax
) :
    col_name = tbl_name + '_name'
    for (row_id, row) in enumerate(table) :
        if row[col_name] == row_name :
            return row_id
    msg  = f'table_name2id: "{row_name}" '
    msg += f'is not presnet in column "{col_name}" of "{tbl_name}" table.'
    assert False, msg
