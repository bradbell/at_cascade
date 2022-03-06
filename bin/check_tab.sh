#! /bin/bash -e
# -----------------------------------------------------------------------------
# at_cascade: Cascading Dismod_at Analysis From Parent To Child Regions
#           Copyright (C) 2021-22 University of Washington
#              (Bradley M. Bell bradbell@uw.edu)
#
# This program is distributed under the terms of the
#     GNU Affero General Public License version 3.0 or later
# see http://www.gnu.org/licenses/agpl.txt
# -----------------------------------------------------------------------------
if [ "$0" != 'bin/check_tab.sh' ]
then
    echo 'bin/check_tab.sh must be run from its parent directory.'
    exit 1
fi
# -----------------------------------------------------------------------------
list=$(git ls-files)
ok='yes'
for file in $list
do
   if grep $'\t' $file > /dev/null
    then
        if [ "$ok" == 'yes' ]
        then
            echo '-----------------------------------------------------------'
        fi
        echo $file
        ok='no'
    fi
done
if [ "$ok" == 'no' ]
then
    echo 'bin/check_tab.sh: The files listed above contain tabs'
    exit 1
fi
# -----------------------------------------------------------------------------
echo 'check_tab.sh: OK'
exit 0
