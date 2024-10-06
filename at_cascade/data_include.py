# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2024 Bradley M. Bell
r'''
{xrst_begin data_include}

Rows of Data Table That are Include for a Fit
#############################################

Prototype
*********
{xrst_literal ,
   # BEGIN DEF, # END DEF
   # BEGIN RETURN, # END RETURN
}

fit_database
************
This is the database for the job that we will be fitting.
All of the dismod_at hold out commands that will be used for the fit
must be executed; i.e., the hold_out column in the data_subset table
is the same as will be used for the fit.

root_database
*************
This is the root node database. It contains the dismod_at tables
that are the same for all the fits in the cascade.

data_include_table
******************
This is the rows of the data table that are included in the fit; i.e.,
the rows that satisfy the following conditions:

#. The node is the node being fit or a descendant of the node being fit.
#. All the covariates are within their maximum difference limits.
#. The hold_out value in the data table is zero
#. The corresponding hold_out value in the data_subset table is zero.
#. The corresponding integrand is not in the option table hold_out list.

{xrst_end data_include}
'''
import at_cascade
#
# BEGIN DEF
# at_cascade.data_include
def data_include(
   fit_database,
   root_database
) :
   assert type( fit_database ) == str
   assert type( root_database ) == str
   # END DEF
   #
   # fit_or_root
   fit_or_root = at_cascade.fit_or_root_class(
      fit_database, root_database
   )
   #
   # data_subset_table
   data_subset_table = fit_or_root.get_table('data_subset')
   #
   # data_table
   data_table = fit_or_root.get_table('data')
   #
   # integrand_table
   integrand_table = fit_or_root.get_table('integrand')
   #
   # option_table
   option_table = fit_or_root.get_table('option')
   #
   # fit_or_root
   fit_or_root.close()
   #
   # hold_out_name_list
   hold_out_integrand = None
   for row in option_table :
      if row['option_name'] == 'hold_out_integrand' :
         hold_out_integrand = row[ 'option_value' ]
   if hold_out_integrand == None :
      hold_out_name_list = list()
   else :
      hold_out_name_list = hold_out_integrand.split()
   #
   # hold_out_id_list
   hold_out_id_set   = set()
   for integrand_name in hold_out_name_list :
      integrand_id = at_cascade.table_name2id(
         integrand_table, 'integrand', integrand_name
      )
      hold_out_id_set.add(integrand_id)
   #
   # data_include_table
   data_include_table = list()
   for subset_row in data_subset_table :
      #
      # data_id
      data_id = subset_row['data_id']
      #
      # data_row
      data_row = data_table[data_id]
      #
      # integrand_id
      integrand_id = data_row['integrand_id']
      #
      # hold_out
      hold_out = integrand_id in hold_out_id_set
      hold_out = hold_out or bool( data_row['hold_out'] )
      hold_out = hold_out or bool( subset_row['hold_out'] )
      #
      # data_include_table
      if not hold_out :
         data_include_table.append(data_row)
   #
   # BEGIN RETURN
   assert type( data_include_table ) == list
   if len( data_include_table ) > 0 :
      assert type( data_include_table[0] ) == dict
      assert data_include_table[0]['hold_out'] == 0
   return data_include_table
   # END RETURN
