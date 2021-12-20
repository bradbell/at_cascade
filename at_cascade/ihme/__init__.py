# -----------------------------------------------------------------------------
# at_cascade: Cascading Dismod_at Analysis From Parent To Child Regions
#           Copyright (C) 2021-21 University of Washington
#              (Bradley M. Bell bradbell@uw.edu)
#
# This program is distributed under the terms of the
#     GNU Affero General Public License version 3.0 or later
# see http://www.gnu.org/licenses/agpl.txt
# -----------------------------------------------------------------------------
#
# input files for all diseases
location_inp_file  = 'ihme_db/DisMod_AT/metadata/gbd2019_location_map.csv'
age_group_inp_file = 'ihme_db/DisMod_AT/metadata/gbd2019_age_metadata.csv'
mtall_inp_file     = 'ihme_db/DisMod_AT/mtall/gbd2019_all_cause_mortality.csv'
#
# intermediate result files for all diseases
node_table_file         = 'ihme_db/DisMod_AT/results/node_table.csv'
all_mtall_table_file    = 'ihme_db/DisMod_AT/results/all_mtall_table.csv'
mtall_index_table_file  = 'ihme_db/DisMod_AT/results/mtall_index_table.csv'
omega_age_table_file    = 'ihme_db/DisMod_AT/results/omega_age_table.csv'
omega_time_table_file   = 'ihme_db/DisMod_AT/results/omega_time_table.csv'
#
# root_node_database_file
root_node_database = 'ihme_db/DisMod_AT/results/root_node.db'
#
# age group id's that are aggregates of other age groups
aggregate_age_group_id_set = {22, 27}
#
# sex_info_dict
sex_info_dict = {
'Female' : { 'sex_id' : 2, 'covariate_value' :-0.5, 'split_reference_id' : 0},
'Both'   : { 'sex_id' : 3, 'covariate_value' : 0.0, 'split_reference_id' : 1},
'Male'   : { 'sex_id' : 1, 'covariate_value' : 0.5, 'split_reference_id' : 2},
}
#
# gbd_version
gbd_version = 'gbd2019_'
#
# integrand_name2measure_id
# Mappping from the dismod_at integrand name to IHME measure_id;
integrand_name2measure_id = {
    'Sincidence' : 41,
    'remission'  : 7,
    'mtexcess'   : 9,
    'mtother'    : 16,
    'mtwith'     : 13,
    'prevalence' : 5,
    'Tincidence' : 42,
    'mtspecific' : 10,
    'mtall'      : 14,
    'mtstandard' : 12,
    'relrisk'    : 11,
}
#
# covaraite_short_name
covariate_short_name = {
'composite_fortification_standard_and_folic_acid_inclusion' :
    'fortification',
'elevation_over_1500m' :
    'at_elevation',
'folic_acid' :
    'folic_acid',
'haqi' :
    'haqi',
'ldi' :
    'ldi',
'mean_war_mortality' :
    'war' ,
'negative_experience_index_log_tranform' :
    'experience' ,
'obesity_prevalence' :
    'obesity',
'SEV_scalar_COPD_age_std_log_transform' :
   'sev_scalar',
}
#
# ----------------------------------------------------------------------------
# BEGIN_SORT_THIS_LINE_PLUS_1
from .get_age_group_id_table      import get_age_group_id_table
from .get_interpolate_covariate   import get_interpolate_covariate
from .get_table_csv               import get_table_csv
from .write_csv                   import write_csv
from .write_data_table            import write_data_table
from .write_mtall_tables          import write_mtall_tables
from .write_node_table            import write_node_table
# END_SORT_THIS_LINE_MINUS_1
