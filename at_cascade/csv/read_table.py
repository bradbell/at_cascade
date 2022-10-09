# -----------------------------------------------------------------------------
# at_cascade: Cascading Dismod_at Analysis From Parent To Child Regions
#           Copyright (C) 2021-22 University of Washington
#              (Bradley M. Bell bradbell@uw.edu)
#
# This program is distributed under the terms of the
#     GNU Affero General Public License version 3.0 or later
# see http://www.gnu.org/licenses/agpl.txt
# -----------------------------------------------------------------------------
import csv
"""
{xrst_begin csv_read_table}

Create A Table from a CSV File
##############################

Syntax
******
{xrst_literal
   BEGIN_SYNTAX
   END_SYNTAX
}


file_name
*********
is a ``str`` with the name of the CSV file.
The first line of the file is the header line and the others contain
the data.
The header value in the j-th column of the first line is the
corresponding column name.

table
*****
the return value *table* is a ``list`` of ``dict``.
We use *n* to denote the length of the list which is
the number of lines in the file minus one.
For *i*, an ``int`` ,  between zero and *n*-1,
and each column name *key* , a string,
*table*[i][*key*] is the ``str`` in line i+2 and column *key*.

Example
*******
:ref:`csv_table`

{xrst_end csv_read_table}
"""
# BEGIN_SYNTAX
# table = at_cascade.csv.read_table(file_name)
# END_SYNTAX
def read_table(file_name) :
   assert type(file_name)  == str
   #
   file_ptr   = open(file_name)
   reader     = csv.DictReader(file_ptr)
   table      = list()
   for row in reader :
      table.append(row)
   file_ptr.close()
   return table
