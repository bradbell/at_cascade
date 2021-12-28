# --------------------------------------------------------------------------
# at_cascade: Cascading Dismod_at Analysis From Parent To Child Regions
#           Copyright (C) 2021-21 University of Washington
#              (Bradley M. Bell bradbell@uw.edu)
#
# This program is distributed under the terms of the
#     GNU Affero General Public License version 3.0 or later
# see http://www.gnu.org/licenses/agpl.txt
# ---------------------------------------------------------------------------
#
# input files for all diseases
location_inp_file  = 'ihme_db/DisMod_AT/metadata/gbd2019_location_map.csv'
age_group_inp_file = 'ihme_db/DisMod_AT/metadata/gbd2019_age_metadata.csv'
mtall_inp_file     = 'ihme_db/DisMod_AT/mtall/gbd2019_all_cause_mortality.csv'
#
# Intermediate result files that are used for all diseases.
# This names are relative to the result_dir in the all_option table.
# BEGIN_SORT_THIS_LINE_PLUS_2
csv_file = {
    'all_mtall'     : 'all_mtall_table.csv',
    'all_option'    : 'all_option_table.csv',
    'data'          : 'data_table.csv',
    'mtall_index'   : 'mtall_index_table.csv',
    'mulcov_freeze' : 'mulcov_freeze_table.csv',
    'node'          : 'node_table.csv',
    'node_split'    : 'node_split_table.csv',
    'omega_age'     : 'omega_age_table.csv',
    'omega_time'    : 'omega_time_table.csv',
}
# END_SORT_THIS_LINE_MINUS_2
#
# all_node_database
all_node_database = 'ihme_db/DisMod_AT/results/all_node.db'
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
# age_grid_n_digits
# Number of digits of precison in age grid values (used so conversion to
# ascii and back yields same result).
age_grid_n_digits = 8
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
# ----------------------------------------------------------------------------
# BEGIN_SORT_THIS_LINE_PLUS_1
from .get_age_group_id_table      import get_age_group_id_table
from .get_interpolate_covariate   import get_interpolate_covariate
from .get_table_csv               import get_table_csv
from .ihme_csv                    import ihme_csv
from .main                        import main
from .write_all_node_database     import write_all_node_database
from .write_all_option_table      import write_all_option_table
from .write_csv                   import write_csv
from .write_data_table            import write_data_table
from .write_mtall_tables          import write_mtall_tables
from .write_mulcov_freeze_table   import write_mulcov_freeze_table
from .write_node_split_table      import write_node_split_table
from .write_node_table            import write_node_table
# END_SORT_THIS_LINE_MINUS_1
