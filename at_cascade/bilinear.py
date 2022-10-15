# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
import numpy
import scipy.interpolate
"""
{xrst_begin bilinear}
{xrst_spell
   bilinear
   spline
}

Bilinear Spline Interpolation
#############################

Syntax
******
{xrst_literal
   BEGIN_SYNTAX
   END_SYNTAX
}

x_name
******
Is a ``str`` containing the name in *table* for the x
variable in the interpolation.

y_name
******
Is a ``str`` containing the name in *table* for the y
variable in the interpolation.

z_list
******
Is a ``list`` of ``str`` .
Each element of *z_list*  contains the name in *table* for a z
variable in the interpolation.

table
*****
This is a ``list`` of ``dict``.
The values *x_name* , *y_name* and each element of *z_list*
must be a key in each of the dictionaries.
Furthermore, the corresponding dictionary values must be ``str`` or ``float`` .
This table must be non-empty.

Rectangular Grid
================
For each x in *x_grid* and y in *y_grid* there must be one,
and only one, row in *table* with that x and y value.
If this is not the case, ``bilinear`` will return with *spline_dict*
equal to ``None`` .

x_grid
******
Is the a sorted ``list`` of values that appear
in the *x_name* column of *table* .
Duplicates are not included in this list.

y_grid
******
Is the a sorted ``list`` of values that appear
in the *y_name* column of *table* .
Duplicates are not included in this list.

spline_dict
***********
Is a ``dict`` of spline functions.
This for each *z_name* in  *z_list* .
The function call
{xrst_code py}
   z = spline_dict[z_name](x, y)
{xrst_code}
sets z to the value of the spline for *z_name*
where the values x, y, and z are ``float`` ,

Example
*******
:ref:`example_bilinear`

{xrst_end bilinear}
"""
class spline_wrapper :
   def __init__(self, spline) :
      self.spline = spline
   def __call__(self, x, y) :
      assert type(x) == float
      assert type(y) == float
      result = self.spline(x, y)
      assert type(result) == numpy.ndarray
      assert result.size == 1
      return float(result)

def bilinear(
# BEGIN_SYNTAX
# x_grid, y_grid, spline_dict = bilinear(
   table,
   x_name,
   y_name,
   z_list
# )
# END_SYNTAX
) :
   #
   if len(table) == 0 :
      return (list(), list(), None)
   #
   # x_set, y_set
   x_set       = set()
   y_set       = set()
   for row in table :
      x      = float( row[x_name] )
      y      = float( row[y_name] )
      x_set.add(x)
      y_set.add(y)
   #
   # n_x, n_y
   n_x = len(x_set)
   n_y = len(y_set)
   #
   # x_grid_in, y_grid_in
   x_grid_in = sorted(x_set)
   y_grid_in = sorted(y_set)
   #
   # triple_list, x_set, y_set
   triple_list = list()
   for row in table :
      x      = float( row[x_name] )
      y      = float( row[y_name] )
      triple = (x, y, row)
      triple_list.append( triple )
      #
      if n_x == 1 :
         if x == 0.0 :
            x_other = 1.0
         else :
            x_other = 2.0 * x
         triple = (x_other, y, row)
         triple_list.append( triple )
         x_set.add(x_other)
      #
      if n_y == 1 :
         if y == 0.0 :
            y_other = 1.0
         else :
            y_other = 2.0 * y
         triple = (x, y_other, row)
         triple_list.append( triple )
         y_set.add(y_other)
      #
      if n_x == 1 and n_y == 1 :
         triple = (x_other, y_other, row)
         triple_list.append( triple )
   #
   # n_x, n_y
   n_x = len(x_set)
   n_y = len(y_set)
   #
   # x_grid, y_grid
   x_grid = sorted(x_set)
   y_grid = sorted(y_set)
   #
   if len(triple_list) != n_x * n_y :
      return (x_grid_in, y_grid_in, None)
   #
   # triple_list
   triple_list = sorted(triple_list)
   #
   # spline_dict
   spline_dict = dict()
   #
   # z_grid
   z_grid = numpy.empty( (n_x, n_y) )
   #
   # z_name
   for z_name in z_list :
      #
      # z_grid
      z_grid[:] = numpy.nan
      #
      # index, triple
      for (index, triple) in enumerate( triple_list ) :
         #
         # x_index, y_index
         x        = triple[0]
         y        = triple[1]
         x_index  = int( index / n_y )
         y_index  = index % n_y
         if x != x_grid[x_index] :
            return(x_grid_in, y_grid_in, None)
         if y != y_grid[y_index] :
            return(x_grid_in, y_grid_in, None)
         #
         # z_grid
         row   = triple[2]
         value = float( row[z_name] )
         z_grid[x_index][y_index] =  value
      #
      # spline_dict
      spline = scipy.interpolate.RectBivariateSpline(
         x_grid, y_grid, z_grid, kx=1, ky=1, s=0
      )
      spline_dict[z_name] = spline_wrapper( spline )
   #
   return (x_grid_in, y_grid_in, spline_dict)
