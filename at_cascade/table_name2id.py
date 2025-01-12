# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ----------------------------------------------------------------------------
r'''
{xrst_begin table_name2id}
{xrst_spell
  tbl
}

Map a Table Row Name to The Row Index
#####################################

Prototype
*********
{xrst_literal ,
   # BEGIN_DEF, END_DEF
   # BEGIN_RETURN, END_RETURN
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

{xrst_end table_name2id}
'''
# -----------------------------------------------------------------------------
# BEGIN_DEF
# at_cascade.table_name2id
def table_name2id(
   table, tbl_name, row_name
) :
   assert type(table) == list
   assert type(tbl_name) == str
   # END_DEF
   col_name = tbl_name + '_name'
   row_id   = None
   for (index, row) in enumerate(table) :
      if row[col_name] == row_name :
         row_id = index
   if row_id == None :
      msg  = f'table_name2id: "{row_name}" '
      msg += f'is not presnet in column "{col_name}" of "{tbl_name}" table.'
      assert False, msg
   #
   # BEGIN_RETURN
   # ...
   assert type(row_id) == int
   return row_id
   # END_RETURN
