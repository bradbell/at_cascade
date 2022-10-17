# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin csv_module}
{xrst_spell
   distributions
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
A csv file is said to have a rectangular grid in columns
*name_a* , *name_b*, *name_c* if the following holds:

#. The csv file has columns with the names
   *name_a*, *name_b*, *name_c*.

#. :math:`( a_1 , \ldots , a_L )`
   is the vector of values in column *name_a* .

#. :math:`( b_1 , \ldots , b_M )`
   is the vector of values in column *name_b* .

#. :math:`( c_1 , \ldots , c_N )`
   is the vector of values in column *name_c* .

#. For :math:`\ell = 1 , \ldots , L`,
   :math:`m = 1 , \ldots , M`,
   :math:`n = 1,  \ldots , N` ,
   there is one and only one row with
   *name_a* equal to :math:`a_\ell`,
   *name_b* equal to :math:`b_m`, and
   *name_c* equal to :math:`c_n`.

Covariates
==========
For this csv interface, all the covariates are
:ref:`glossary@Relative Covariate` (called country covariates at IHME).
Other cause mortality ``omega`` is referred to as a
covariate (not as a rate) for this interface.
Sex is the
:ref:`all_option_table@split_covariate_name` and is not
referred to as a covariate.

Data Type
=========
The actual data type for each entry in a csv file is a string; i.e.,
an arbitrary sequence of characters. Certain columns have further
restrictions as described below

1. An integer value is a string represents of an integer.
2. A float value is a string that represents a floating point number.
3. A sex value is either ``female`` , ``male`` or ``both`` .

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
from .covariate_avg    import covariate_avg
from .covariate_spline import covariate_spline
from .empty_str        import empty_str
from .fit              import fit
from .read_table       import read_table
from .simulate         import simulate
from .write_table      import write_table
# END_SORT_THIS_LINE_MINUS_1
