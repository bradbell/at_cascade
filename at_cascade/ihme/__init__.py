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
location_csv_file  = 'ihme_db/DisMod_AT/metadata/gbd2019_location_map.csv'
age_group_csv_file = 'ihme_db/DisMod_AT/metadata/gbd2019_age_metadata.csv'
#
# intermediate result files for all diseases
node_table_file = 'ihme_db/DisMod_AT/node_table.csv'
#
# age_groud_id for age groups that span all ages
all_age_group_id_set = [22, 27]
#
# sex_name2sex_id
# Mapping from sex name to IHME sex_id.
sex_name2sex_id = {'Male' : 1,  'Female' : 2, 'Both' : 3}
#
# gbd_version
gbd_version = 'gbd2019_'
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
from .get_age_group_id_dict       import get_age_group_id_dict
from .get_interpolate_covariate   import get_interpolate_covariate
from .write_csv                   import write_csv
from .write_data_table            import write_data_table
from .write_node_table            import write_node_table
# END_SORT_THIS_LINE_MINUS_1
