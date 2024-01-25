#! /bin/bash -e
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-23 Bradley M. Bell
# ----------------------------------------------------------------------------
# bash function that echos and executes a command
echo_eval() {
   echo $*
   eval $*
}
# -----------------------------------------------------------------------------
if [ "$0" != 'bin/check_all.sh' ]
then
   echo 'bin/check_all.sh must be run from its parent directory.'
   exit 1
fi
# -----------------------------------------------------------------------------
file='at_cascade/fit_parallel.py'
if ! grep 'catch_exceptions_and_continue *= *True' $file > /dev/null
then
   echo "$file: catch_exceptions_and_continue is not True"
   exit 1
fi
echo_eval bin/check_tab.sh
echo_eval bin/run_xrst.sh
# -----------------------------------------------------------------------------
list=$(ls example/*.py example/csv/*.py test/*.py)
for script in $list
do
   echo_eval bin/run_test.sh $script
done
# -----------------------------------------------------------------------------
echo 'check_all.sh: OK'
exit 0
