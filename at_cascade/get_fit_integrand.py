# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin get_fit_integrand}

Determine the Set of Integrands in Data Table
#############################################

Syntax
******
{xrst_literal
   # BEGIN syntax
   # END syntax
}


fit_node_database
*****************
is a python string specifying the location of a
:ref:`glossary@fit_node_database`
relative to the current working directory.
Note that only the data table in this database is used and
it is the same data table as the data table in the root_node_database.
This argument can't be None.

fit_integrand
*************
The return value *fit_integrand* is a python set of integrand_id
that appear in the data table in the *fit_node_database*.
Furthermore there is a row in the data table
where each such integrand_id is not held out.

{xrst_end get_fit_integrand}
'''
# ----------------------------------------------------------------------------
import sys
import dismod_at
# ----------------------------------------------------------------------------
def get_fit_integrand(
# BEGIN syntax
# fit_integrand = at_cascade.get_fit_integrand(
   fit_node_database = None ,
# )
# END syntax
) :
   #
   # data_table
   new  = False
   connection = dismod_at.create_connection(fit_node_database, new)
   data_table = dismod_at.get_table_dict(connection, 'data')
   connection.close()
   #
   # fit_integrand
   fit_integrand = set()
   for row in data_table :
      if row['hold_out'] == 0 :
         fit_integrand.add( row['integrand_id'] )
   #
   return fit_integrand
