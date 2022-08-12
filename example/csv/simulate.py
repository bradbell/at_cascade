# -----------------------------------------------------------------------------
# at_cascade: Cascading Dismod_at Analysis From Parent To Child Regions
#           Copyright (C) 2021-22 University of Washington
#              (Bradley M. Bell bradbell@uw.edu)
#
# This program is distributed under the terms of the
#     GNU Affero General Public License version 3.0 or later
# see http://www.gnu.org/licenses/agpl.txt
# -----------------------------------------------------------------------------
import os
import sys
# import at_cascade with a preference current directory version
current_directory = os.getcwd()
if os.path.isfile( current_directory + '/at_cascade/__init__.py' ) :
    sys.path.insert(0, current_directory)
import at_cascade
"""
{xrst_begin example_csv_simulate}
{xrst_spell
    csv
    dir
}

Example Using csv_simulate
##########################

..  list-table::
    :header-rows: 1

    *   -   Symbol
        -   Documentation
    *   -   csv_dir
        -   :ref:`csv_interface@arguments@csv_dir`
    *   -   command
        -   :ref:`csv_interface@arguments@command`
    *   -   ``option_csv``
        -   :ref:`csv_simulate@option.csv`


{xrst_file
    BEGIN_PYTHON
    END_PYTHON
}


{xrst_end example_csv_simulate}
"""
# BEGIN_PYTHON
#
option_csv = \
'''name,value
std_random_effects,.1
integrand_step_size,5
'''
def main() :
    #
    # csv_dir
    csv_dir = 'build/csv'
    if not os.path.exists(csv_dir) :
        os.mkdir(csv_dir)
    #
    #
    # option.csv
    file_name = f'{csv_dir}/option.csv'
    file_ptr  = open(file_name, 'w')
    file_ptr.write(option_csv)
    file_ptr.close()
    #
    # simulate command
    command = 'simulate'
    at_cascade.csv_interface(csv_dir, command)
#
main()
# END_PYTHON
