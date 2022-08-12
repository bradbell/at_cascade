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

Node Tree
*********
                n0
          /-----/\-----\
        n1              n2

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
# csv_file
csv_file = dict()
#
# option.csv
csv_file['option.csv'] = \
'''name,value
std_random_effects,.1
integrand_step_size,5
'''
#
# node.csv
csv_file['node.csv'] = \
'''node_name,parent_name
n0,
n1,n0
n2,n0
'''
#
# covariate.csv
csv_file['covariate.csv'] = \
'''node_name,sex,age,time,omega,haqi
n0,female,50,2000,0.01,1.0
n0,male,50,2000,0.01,1.0
n1,female,50,2000,0.01,0.5
n1,male,50,2000,0.01,0.5
n2,female,50,2000,0.01,1.5
n2,male,50,2000,0.01,1.5
'''
#
def main() :
    #
    # csv_dir
    csv_dir = 'build/csv'
    if not os.path.exists(csv_dir) :
        os.mkdir(csv_dir)
    #
    # write csv files
    for name in csv_file :
        file_name = f'{csv_dir}/{name}'
        file_ptr  = open(file_name, 'w')
        file_ptr.write( csv_file[name] )
        file_ptr.close()
    #
    # simulate command
    command = 'simulate'
    at_cascade.csv_interface(csv_dir, command)
    #
    print('simulte.py: OK')
    sys.exit(0)
#
main()
# END_PYTHON
