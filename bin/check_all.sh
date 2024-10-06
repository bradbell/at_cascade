#! /usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
set -e -u
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
if ! which dismod_at >& /dev/null
then
   echo 'Cannot find dismod_at executable is not in your PATH directories:'
   echo $PATH
   exit 1
fi
if ! python -c 'import dismod_at' >& /dev/null
then
   echo 'Cannot find dismod_at python module in your PYTHONPATH directories:'
   echo $PYTHONPATH
   exit 1
fi
if ! which gsed >& /dev/null
then
   if [ $(uname -s) == 'Darwin' ]
   then
      echo 'This is a macOS system and the gsed program is not installed'
      exit 1
   fi
fi
# -----------------------------------------------------------------------------
list='
   at_cascade/fit_one_process.py
   at_cascade/csv/pre_one_process.py
'
for file in $list
do
   if ! grep 'catch_exceptions_and_continue *= *True' $file > /dev/null
   then
      echo "$file: catch_exceptions_and_continue is not True"
      exit 1
   fi
done
# -----------------------------------------------------------------------------
list=$(ls bin/check_*.sh | sed -e '/check_all.sh/d' )
for check in $list
do
   echo_eval $check
done
if which xrst >& /dev/null
then
   echo_eval bin/run_xrst.sh
fi
# -----------------------------------------------------------------------------
list=$(\
   ls example/*.py example/csv/*.py test/*.py test/csv/*.py | \
   sed -e '/.*[/]temp.py/d' -e '/.*[/]temp.[0-9]*.py/d'  \
)
for script in $list
do
   echo_eval bin/run_test.sh $script
done
# -----------------------------------------------------------------------------
echo 'check_all.sh: OK'
exit 0
