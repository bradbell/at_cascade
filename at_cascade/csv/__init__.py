# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin csv_module}
{xrst_spell
   distributions
   boolean
}

The at_cascade.csv Python Module
################################

Notation
********

Demographer
===========
None of the data is in demographer notation.
For example,
:ref:`csv_simulate@Input Files@covariate.csv@time`
1990 means the beginning of 1990,
not the time interval from 1990 to 1991.

Rectangular Grid
================
Define a selection subset of a csv file as those rows with the same
value in column *select*.
For each value in *select* ,
a csv file is said to have a rectangular grid in age and time
if the following holds:

#. Define :math:`( a_1 , \ldots , a_M )`
   to be the vector of values in the age column for this selection subset.

#. Define :math:`( t_1 , \ldots , t_N )`
   to be the vector of values in the time column for this selection subset.

#. For :math:`m = 1 , \ldots , M`, :math:`n = 1,  \ldots , N` ,
   there is one and only one row in this selection subset with
   age equal to :math:`a_m`, and
   time equal to :math:`t_n`.

Data Type
=========
The actual data type for each entry in a csv file is a string; i.e.,
an arbitrary sequence of characters. Certain columns have further
restrictions as described below

Integer
-------
An integer value is a string represents of an integer.

Float
-----
A float value is a string that represents a floating point number.

Sex
---
A sex value is either ``female`` , ``both``, or ``male``.

Boolean
-------
A boolean value is either ``true`` or ``false`` .

Index Column
============
An index column for a csv file is an integer column
that has the row number corresponding to each row.
It starts with zero at the first row below the header row.
If a column name is an index column for two or more files,
rows with the same index value in the different files
correspond to each other.

Distributions
=============
Unless other wise specified, the mean and standard deviations that
simulate refers to are for a normal distribution.

Routines
********

.. BEGIN_SORT_THIS_LINE_PLUS_2
{xrst_toc_table
   at_cascade/csv/covariate_avg.py
   at_cascade/csv/covariate_spline.py
   at_cascade/csv/empty_str.py
   at_cascade/csv/fit.py
   at_cascade/csv/read_table.py
   at_cascade/csv/simulate.py
   at_cascade/csv/write_table.py
}
.. END_SORT_THIS_LINE_MINUS_2

{xrst_end csv_module}
'''
# BEGIN_SORT_THIS_LINE_PLUS_1
from .check_table      import check_table
from .covariate_avg    import covariate_avg
from .covariate_spline import covariate_spline
from .empty_str        import empty_str
from .fit              import fit
from .read_table       import read_table
from .simulate         import simulate
from .write_table      import write_table
# END_SORT_THIS_LINE_MINUS_1
