# -----------------------------------------------------------------------------
# at_cascade: Cascading Dismod_at Analysis From Parent To Child Regions
#           Copyright (C) 2021-21 University of Washington
#              (Bradley M. Bell bradbell@uw.edu)
#
# This program is distributed under the terms of the
#     GNU Affero General Public License version 3.0 or later
# see http://www.gnu.org/licenses/agpl.txt
# -----------------------------------------------------------------------------
import csv
# table = get_table_csv(file_name)
def get_table_csv(file_name) :
    file_ptr   = open(file_name)
    reader     = csv.DictReader(file_ptr)
    table      = list()
    for row in reader :
        table.append(row)
    file_ptr.close()
    return table
