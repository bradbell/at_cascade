#! /usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-25 Bradley M. Bell
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
#
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
#
# grep, sed
source bin/grep_and_sed.sh
# -----------------------------------------------------------------------------
#
if [ $# == 1 ]
then
   if [ "$1" == --help ]
   then
cat << EOF
bin/check_all.sh flags
possible flags
--help                     print this help message
--skip_external_links      do not check documentation external links
--suppress_spell_warnings  do not check for documentaiton spelling errors
EOF
      exit 0
   fi
fi
#
# skip_external_links, suppress_spell_warnings
skip_external_links='no'
suppress_spell_warnings='no'
while [ $# != 0 ]
do
   case "$1" in

      --skip_external_links)
      skip_external_links='yes'
      ;;

      --suppress_spell_warnings)
      suppress_spell_warnings='yes'
      ;;

      *)
      echo "bin/check_all.sh: command line argument "$1" is not valid"
      exit 1
      ;;

   esac
   shift
done
# -----------------------------------------------------------------------------
list='
   at_cascade/fit_one_process.py
   at_cascade/csv/pre_one_process.py
'
for file in $list
do
   if ! $grep 'catch_exceptions_and_continue *= *True' $file > /dev/null
   then
      echo "$file: catch_exceptions_and_continue is not True"
      exit 1
   fi
done
# -----------------------------------------------------------------------------
list=$(ls bin/check_*.sh | $sed -e '/check_all.sh/d' )
for check in $list
do
   echo_eval $check
done
if which xrst >& /dev/null
then
   xrst_flags=''
   if [ "$skip_external_links" == 'no' ]
   then
      xrst_flags+=' --external_links'
   fi
   if [ "$suppress_spell_warnings" == 'yes' ]
   then
      xrst_flags+=' --suppress_spell_warnings'
   fi
   bin/run_xrst.sh $xrst_flags
fi
# -----------------------------------------------------------------------------
list=$(\
   ls example/*.py example/csv/*.py test/*.py test/csv/*.py | \
   $sed -e '/.*[/]temp.py/d' -e '/.*[/]temp.[0-9]*.py/d'  \
)
for script in $list
do
   echo_eval bin/run_test.sh $script
done
# -----------------------------------------------------------------------------
echo 'check_all.sh: OK'
exit 0
