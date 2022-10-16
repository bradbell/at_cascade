# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
import copy
"""
{xrst_begin csv_empty_str}

Create A Table from a CSV File
##############################

Syntax
******
{xrst_literal
   BEGIN_SYNTAX
   END_SYNTAX
}
{xrst_literal
   BEGIN_RETURN
   END_RETURN
}


table_in
********
is a ``list`` of ``dict``.
We use *n* to denote the length of the list which is
the number of lines in the file minus one.
For *i*, an ``int`` ,  between zero and *n* -1,
and each column name *key* , a string,
*table* [ *i* ][ *key* ] is the ``str`` in line *i* +2 and column *key*.

direction
*********
is a ``str`` that is equal to ``to_none`` or ``from_none``.

to_none
-------
If *direction* is to_none, then every empty string is converted to None.
In this case there cannot be any None field values in the input.

from_none
---------
If *direction* is from_none, then every None value is converted to
the empty string.
In this case there cannot be any empty string values in the input.

table_out
*********
Is a copy of *table_in* after doing the conversion.


Example
*******
:ref:`csv_table`

{xrst_end csv_empty_str}
"""
# BEGIN_SYNTAX
# table_out =
def empty_str(table_in, direction) :
   assert type(table_in)  == list
   if len(table_in) > 0 :
      assert type(table_in[0]) == dict
   assert direction == 'to_none' or direction == 'from_none'
# END_SYNTAX
   #
   table_out = list()
   for row in table_in :
      row = copy.copy(row)
      for key in row :
         if direction == 'to_none' :
            if row[key] == '' :
               row[key] = None
         else :
            if row[key] == None :
               row[key] = ''
      table_out.append(row)
# BEGIN_RETURN
   assert type(table_out) == list
   if len(table_out) > 0 :
         assert type(table_out[0]) == dict
   return table_out
# END_RETURN
