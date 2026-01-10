# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-26 Bradley M. Bell
# ----------------------------------------------------------------------------
import numpy
import scipy.interpolate
"""
{xrst_begin bilinear}

Bilinear Spline Interpolation
#############################

Prototype
*********
{xrst_literal ,
   BEGIN_DEF, END_DEF
   BEGIN_RETURN, END_RETURN
}

x_name
******
is the name in *table* for the x
variable in the interpolation.

y_name
******
is the name in *table* for the y
variable in the interpolation.

z_list
******
Each element of  *z_list* is a ``str`` specifying
the name in *table* for a z
variable in the interpolation.

table
*****
Each element of *table* is a ``dict``.
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
   def __init__(self, spline, box, const_x, const_y) :
      self.spline  = spline
      self.box     = box
      self.const_x = const_x
      self.const_y = const_y
   def __call__(self, x, y) :
      #
      # x, y
      if type(x) == int :
         x = float(x)
      if type(y) == int :
         y = float(y)
      assert type(x) == float
      assert type(y) == float
      #
      # x, y
      # The documentation for RectBivariateSpline says
      # 'Evaluated points outside the data range will be extrapolated.' .
      # but testing indicates the following is not necessary
      x = max(x, self.box['x_min'])
      x = min(x, self.box['x_max'])
      y = max(y, self.box['y_min'])
      y = min(y, self.box['y_max'])
      #
      # result
      if self.const_x and self.const_y :
         result = self.spline
      elif self.const_x :
         result = self.spline(y)
      elif self.const_y :
         result = self.spline(x)
      else :
         result = self.spline(x, y)
      assert type(result) == numpy.ndarray
      assert result.size == 1
      #
      result = result.flatten()
      result = result[0]
      return result

# BEGIN_DEF
# at_cascade.bilinear
def bilinear(
   table,
   x_name,
   y_name,
   z_list
) :
   assert type(table) == list
   assert type(x_name) == str
   assert type(y_name) == str
   assert type(z_list) == list
   # END_DEF
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
   # triple_list
   triple_list = list()
   for row in table :
      x      = float( row[x_name] )
      y      = float( row[y_name] )
      triple = (x, y, row)
      triple_list.append( triple )
      #
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
      return (x_grid, y_grid, None)
   #
   # triple_list
   triple_list = sorted(triple_list)
   #
   # spline_dict
   spline_dict = dict()
   #
   # z_name
   for z_name in z_list :
      #
      # z_grid
      z_grid    = numpy.empty( (n_x, n_y) )
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
            return(x_grid, y_grid, None)
         if y != y_grid[y_index] :
            return(x_grid, y_grid, None)
         #
         # z_grid
         row                      = triple[2]
         value                    = float( row[z_name] )
         z_grid[x_index, y_index] =  value
      #
      # const_x
      const_x = True
      for y_index in range(n_y) :
         const_col = numpy.all( z_grid[0, y_index] == z_grid[:, y_index] )
         const_x   = const_x and const_col
      #
      # const_y
      const_y = True
      for x_index in range(n_x) :
         const_row = numpy.all( z_grid[x_index, 0] == z_grid[x_index, :] )
         const_y   = const_y and const_row
      #
      # spline
      if const_x and const_y :
         spline = numpy.array( z_grid[0, 0] )
      elif const_x :
         spline = scipy.interpolate.UnivariateSpline(
            y_grid, z_grid[0,:], k=1, s=0
         )
      elif const_y :
         spline = scipy.interpolate.UnivariateSpline(
            x_grid, z_grid[:,0], k=1, s=0
         )
      else :
         spline = scipy.interpolate.RectBivariateSpline(
            x_grid, y_grid, z_grid, kx=1, ky=1, s=0
         )
      box = {
         'x_min' : x_grid[0],
         'x_max' : x_grid[-1],
         'y_min' : y_grid[0],
         'y_max' : y_grid[-1],
      }
      spline_dict[z_name] = spline_wrapper(spline , box, const_x, const_y)
   #
   # BEGIN_RETURN
   # ...
   assert type(x_grid) == list
   assert type(y_grid) == list
   assert type(spline_dict) == dict
   return (x_grid, y_grid, spline_dict)
   # END_RETURN
