# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ----------------------------------------------------------------------------
import csv
r"""
{xrst_begin csv.write_table}
{xrst_spell
   len
}

Create A CSV File from a Table
##############################

Prototype
*********
{xrst_literal
   BEGIN_DEF
   END_DEF
}

table
*****
This must be  a ``list`` of ``dict``.

columns
*******
This is a ``list`` of ``str`` specifying the keys in the table dictionary
that are written to the file.
If this argument is ``None`` ,
*table* [0].keys() is used as its default value.

file_name
*********
is a ``str`` with the name of the CSV file.
Upon return, this file has ``len(`` *table* ``)`` + 1 lines,
``len(`` *columns* ``)`` columns, with the following values

.. list-table::

   * - columns[0]
     - columns[1]
     - columns[2]
     - ...
   * - table[0][ columns[0] ]
     - table[0][ columns[1] ]
     - table[0][ columns[2] ]
     - ...
   * - table[1][ columns[0] ]
     - table[1][ columns[1] ]
     - table[1][ columns[2] ]
     - ...
   * - \:
     - \:
     - \:
     - ...

Example
*******
:ref:`csv.table-name`


{xrst_end csv.write_table}
"""
# BEGIN_DEF
# at_cascade.csv.write_table(
def write_table(
   file_name  = None,
   table      = None,
   columns    = None,
) :
   assert type(file_name)  == str
   assert type(table)      == list
   assert type(columns) == list or columns == None
   if columns == None :
      columns = table[0].keys()
   # END_DEF
   #
   file_ptr    = open(file_name, 'w')
   writer      = csv.DictWriter(file_ptr, fieldnames = columns)
   writer.writeheader()
   writer.writerows( table )
   file_ptr.close()
