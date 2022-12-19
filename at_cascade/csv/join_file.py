# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
import csv
"""
{xrst_begin csv_join_file}
{xrst_spell
}

Join The Tables In Two Csv Files
################################

Syntax
******
{xrst_literal
   BEGIN_SYNTAX
   END_SYNTAX
}

left_file
*********
Is the name of the first csv files.
Its columns will come first in the output file
(and in the same order as in *left_file* ).

right_file
**********
Is the name of the second csv file.
Its columns will come second in the output file
(and in the same order as in *right_file* ).
This file must have the exact same number or rows as *left_file* .

result_file
***********
Is the name of the resulting file.
It will have all the columns in *left_file* and *right_file*.
The values in the *i* -th row of *result_file* will be the
corresponding values in the *i* -th row of *left_file* and *right_file*.
If a column appears in both files,
the position of the column is its position in *left_file*,
and its value is the value in  *right_file* .

Example
*******
:ref:`csv_join_file_xam-name`


{xrst_end csv_join_file}
"""
import at_cascade
#
def join_file(
# BEGIN_SYNTAX
# at_cascade.csv.join_file(
   left_file    ,
   right_file   ,
   result_file  ,
# )
) :
   assert type(left_file)  == str
   assert type(right_file)  == str
   assert type(result_file)  == str
   # END_SYNTAX
   #
   # left_table, right_table
   left_table   = at_cascade.csv.read_table(left_file)
   right_table  = at_cascade.csv.read_table(right_file)
   if len(left_table) != len(right_table) :
      left_lines  = len(left_table) + 1
      right_lines = len(right_table) + 1
      msg  = 'join_file: left and right files have different number of lines\n'
      msg += f'left file  {left_file} has {left_lines}'
      msg += f'right file {right_file} has {right_lines}'
      assert False, msg
   #
   # result_table
   result_table = list()
   for index in range( len(left_table) ) :
      row  = left_table[index]
      row.update( right_table[index] )
      result_table.append( row )
   #
   # result_file
   at_cascade.csv.write_table(
      file_name = result_file  ,
      table     = result_table ,
   )
