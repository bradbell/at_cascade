# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-25 Bradley M. Bell
# ----------------------------------------------------------------------------
import csv
"""
{xrst_begin csv.get_header}

Get the Header from a CSV File
##############################

Prototype
*********
{xrst_literal ,
   BEGIN_DEF, END_DEF
   BEGIN_RETURN, END_RETURN
}


file_name
*********
is a ``str`` with the name of the CSV file.
The first line of the file is the header line and the others contain
the data.
The header value in the j-th column of the first line is the
corresponding column name.

header
******
the return value *header* is a ``list`` of ``str``.
We use *n* to denote the length of the list which is
the number of commas in the first line plus one.
For *j*, an ``int`` ,  between zero and *n* -1,
the name of the *j*\ -th column is *header* [ *j* ].

Example
*******
:ref:`csv.table-name`

{xrst_end csv.get_header}
"""
# BEGIN_DEF
# at_cascade.csv.get_header
def get_header(file_name) :
   assert type(file_name)  == str
   # END_DEF
   #
   file_ptr   = open(file_name)
   reader     = csv.reader(file_ptr)
   header     = next( reader )
   #
   # BEGIN_RETURN
   # ...
   assert type(header) == list
   return header
   # END_RETURN
