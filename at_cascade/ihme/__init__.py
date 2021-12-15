# -----------------------------------------------------------------------------
# at_cascade: Cascading Dismod_at Analysis From Parent To Child Regions
#           Copyright (C) 2021-21 University of Washington
#              (Bradley M. Bell bradbell@uw.edu)
#
# This program is distributed under the terms of the
#     GNU Affero General Public License version 3.0 or later
# see http://www.gnu.org/licenses/agpl.txt
# -----------------------------------------------------------------------------
location_csv_file = 'ihme_db/DisMod_AT/metadata/gbd2019_location_map.csv'
node_csv_file     = 'ihme_db/node_table.csv'
# ----------------------------------------------------------------------------
from .write_csv         import write_csv
from .write_node_csv    import write_node_csv
