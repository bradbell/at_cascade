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
import at_cascade.ihme
# -----------------------------------------------------------------------------
# age_group_id_dict = get_age_group_id_dict()
def get_age_group_id_dict() :
    all_age_group_id_set = at_cascade.ihme.all_age_group_id_set
    file_name            = at_cascade.ihme.age_group_inp_file
    file_ptr             = open(file_name)
    reader               = csv.DictReader(file_ptr)
    age_group_id_dict    = dict()
    for row_in in reader :
        row_out = dict()
        age_group_id      = int( row_in['age_group_id'] )
        age_lower         = float( row_in['age_group_years_start'] )
        age_upper         = float( row_in['age_group_years_end'] )
        #
        if age_group_id in all_age_group_id_set :
            assert age_lower <= 0.0
            assert 100.0     <= age_upper
        else :
            row_out = {
                'age_lower' : age_lower ,
                'age_upper' : age_upper ,
                'age_mid'   : (age_lower + age_upper) / 2.0,
            }
            age_group_id_dict[age_group_id] = row_out
        age_group_id_dict[age_group_id] = row_out
    return age_group_id_dict
