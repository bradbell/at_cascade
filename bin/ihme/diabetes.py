#! /usr/bin/python3
# -----------------------------------------------------------------------------
# at_cascade: Cascading Dismod_at Analysis From Parent To Child Regions
#           Copyright (C) 2021-21 University of Washington
#              (Bradley M. Bell bradbell@uw.edu)
#
# This program is distributed under the terms of the
#     GNU Affero General Public License version 3.0 or later
# see http://www.gnu.org/licenses/agpl.txt
# ----------------------------------------------------------------------------
# covariate_csv_file_list
covariate_name_list = [ 'ldi', 'obesity_prevalence' ]
covariate_csv_file_list = list()
for covariate_name in covariate_name_list :
    file_name = 'ihme_db/DisMod_AT/covariates/gbd2019_'
    file_name += covariate_name
    file_name += '_covariate.csv'
    covariate_csv_file_list.append(file_name)
#
# input files
data_dir        = 'ihme_db/DisMod_AT/testing/diabetes/data'
data_inp_file   = f'{data_dir}/gbd2019_diabetes_crosswalk_12437.csv'
csmr_inp_file   = f'{data_dir}/gbd2019_diabetes_csmr.csv'
#
# intermediate files
results_dir     = 'ihme_db/DisMod_AT/results'
data_table_file = f'{results_dir}/data_table.csv'
# ----------------------------------------------------------------------------
import os
import sys
#
current_directory = os.getcwd()
if os.path.isfile( current_directory + '/at_cascade/__init__.py' ) :
    sys.path.insert(0, current_directory)
#
import at_cascade.ihme
# ----------------------------------------------------------------------------
def main() :
    #
    # write_node_table
    at_cascade.ihme.write_node_table()
    #
    # write_data_table
    at_cascade.ihme.write_data_table(
        data_inp_file           = data_inp_file,
        csmr_inp_file           = csmr_inp_file,
        covariate_csv_file_list = covariate_csv_file_list,
        data_table_file         = data_table_file,
    )
    #
    # write_mtall_tables
    at_cascade.ihme.write_mtall_tables()
# ----------------------------------------------------------------------------
main()
print('diabetes.py: OK')
sys.exit(0)
