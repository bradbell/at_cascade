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
# -----------------------------------------------------------------------------
#
# write_csv(file_name, table)
# write_csv(file_name, table, fieldnames)
def write_csv(
    file_name  = None,
    table      = None,
    fieldnames = None,
) :
    assert file_name is not None
    assert table is not None
    if fieldnames is None :
        fieldnames  = table[0].keys()
    file_ptr    = open(file_name, 'w')
    writer      = csv.DictWriter(file_ptr, fieldnames = fieldnames)
    writer.writeheader()
    writer.writerows( table )
    file_ptr.close()
