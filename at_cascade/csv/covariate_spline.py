# -----------------------------------------------------------------------------
# at_cascade: Cascading Dismod_at Analysis From Parent To Child Regions
#           Copyright (C) 2021-22 University of Washington
#              (Bradley M. Bell bradbell@uw.edu)
#
# This program is distributed under the terms of the
#     GNU Affero General Public License version 3.0 or later
# see http://www.gnu.org/licenses/agpl.txt
# -----------------------------------------------------------------------------
import at_cascade
'''
{xrst_begin covariate_spline}
{xrst_spell
   spline
   cov
}

Create Spline Functions For Covariates
######################################

Syntax
******
{xrst_literal
   BEGIN_SYNTAX
   END_SYNTAX
}

covariate_table
***************
This is a list of dict with the same keys for each dict
containing the information in :ref:`csv_simulate@Input Files@covariate.csv` .
All of the keys are covariate names except for
``node_name`` , ``sex``, ``age`` and ``time`` .

node_set
********
This is the set of nodes in :ref:`csv_simulate@Input Files@node.csv`

spline_cov
**********
This is a dict of dict of dict.
For each *node_name* in *covariate_table*,
each *sex* in *covariate_table*,
and each *covariate_name* in *covariate_table*
{xrst_code py}
   spline = spline_cov[node_name][sex][covariate_name]
{xrst_code}
is a spline function returning the value of the specified covariate,
for the specified sex and node.
To be more specific
{xrst_code py}
   z = spline(age, time)
{xrst_code}
is the value of the covariate at the specified age and time where
*age*, *time*, and *z* are floats.

{xrst_end covariate_spline}
'''
# BEGIN_SYNTAX
# spline_cov =
def covariate_spline(covariate_table , node_set) :
   assert type( covariate_table ) == list
   assert type( covariate_table[0] ) == dict
   assert type( node_set ) == set
   # END_SYNTAX
   #
   # cov_name_list
   cov_name_list = list()
   for key in covariate_table[0].keys() :
      if key not in [ 'node_name', 'sex', 'age', 'time' ] :
         cov_name_list.append( key )
   #
   # covariate_row_list
   covariate_row_list  = dict()
   line_number         = 0
   for row in covariate_table :
      line_number += 1
      node_name    = row['node_name']
      sex          = row['sex']
      age          = float( row['age'] )
      time         = float( row['time'] )
      if node_name not in node_set :
         msg  = f'csv_interface: Error: '
         msg += f'line {line_number} in covariate.csv\n'
         msg += f'node_name {node_name} is not in node.csv'
         assert False, msg
      if sex not in ['male', 'female'] :
         msg  = f'csv_interface: Error: '
         msg += f'line {line_number} in covariate.csv\n'
         msg += f'sex {sex} is not male or female'
         assert False, msg
      #
      # covariate_row_list
      if node_name not in covariate_row_list :
         covariate_row_list[node_name] = dict()
      if sex not in covariate_row_list[node_name] :
         covariate_row_list[node_name][sex] = list()
      covariate_row_list[node_name][sex].append( row )
   #
   # spline_cov
   spline_cov = dict()
   #
   # node_name
   for node_name in covariate_row_list :
      #
      # spline_cov[node_name]
      spline_cov[node_name] = dict()
      #
      # sex
      for sex in covariate_row_list[node_name] :
         #
         # age_grid, time_grid, spline_dict
         age_grid, time_grid, spline_dict = at_cascade.bilinear(
            table  = covariate_row_list[node_name][sex] ,
            x_name = 'age',
            y_name = 'time',
            z_list = cov_name_list
         )
         #
         if spline_dict == None :
            msg  = 'csv_interface: Error in covariate.csv\n'
            msg += 'node_name = {node_name}, sex = {sex} \n'
            msg += 'Expected following rectangular grid:\n'
            msg += f'age_grid  = {age_grid}\n'
            msg += f'time_grid = {time_grid}'
            assert False, msg
         #
         # spline_cov[node_name][sex]
         spline_cov[node_name][sex] = spline_dict
   #
   return spline_cov
