# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ----------------------------------------------------------------------------
import numpy
import scipy.interpolate
"""
{xrst_begin bilinear}

Bilinear Spline Interpolation
#############################

Syntax
******
{xrst_literal ,
   BEGIN_SYNTAX, END_SYNTAX
   BEGIN_RETURN, END_RETURN
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
Is a ``dict`` of spline functions with keys equal to
each *z_name* in  *z_list* .
The function call
{xrst_code py}
   z = spline_dict[z_name](x, y)
{xrst_code}
sets z to the value of the spline for *z_name* .

#. The values x and y are ``float`` or ``int`` .
#. The value z is a  ``float`` .
#. The function is extended as constant with respect to x (y)
   for values of x (y) outside the limits of x_grid (y_grid).

Example
*******
:ref:`example_bilinear-name`

{xrst_end bilinear}
"""
class spline_wrapper :
   def __init__(self, spline, x_min, x_max, y_min, y_max) :
      self.spline = spline
      self.x_min  = x_min
      self.x_max  = x_max
      self.y_min  = y_min
      self.y_max  = y_max
   def __call__(self, x, y) :
      if type(x) == int :
         x = float(x)
      if type(y) == int :
         y = float(y)
      assert type(x) == float
      assert type(y) == float
      #
      # The documentation for RectBivariateSpline says
      # 'Evaluated points outside the data range will be extrapolated.' .
      # but testing indicates the following is not necessary
      x = max(x, self.x_min)
      x = min(x, self.x_max)
      y = max(y, self.y_min)
      y = min(y, self.y_max)
      #
      result = self.spline(x, y)
      assert type(result) == numpy.ndarray
      assert result.size == 1
      return float(result)

# BEGIN_SYNTAX
# at_cascade.bilinear
def bilinear(
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
      x_min = x_grid[0]
      x_max = x_grid[-1]
      y_min = y_grid[0]
      y_max = y_grid[-1]
      spline_dict[z_name] = spline_wrapper(spline , x_min, x_max, y_min, y_max)
   #
   # BEGIN_RETURN
   # ...
   assert type(x_grid_in) == list
   assert type(y_grid_in) == list
   assert type(spline_dict) == dict
   return (x_grid_in, y_grid_in, spline_dict)
   # END_RETURN
