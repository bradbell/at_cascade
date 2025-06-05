#! /bin/bash -e
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-25 Bradley M. Bell
# ----------------------------------------------------------------------------
if [ "$0" != 'bin/run_test.sh' ]
then
   echo 'bin/run_test.sh: must be executed from its parent directory'
   exit 1
fi
if [ ! -e "$1" ]
then
   echo 'usage: bin/run_test.sh test_file'
   echo "The test_file '$1' does not exist."
   exit 1
fi
#
# sed_path
if which gsed >& /dev/null
then
   sed_path=$(which gsed)
else
   sed_path=$(which sed)
fi
#
# test_file
test_file="$1"
if [ "$test_file" == 'example/csv/coverage.py' ]
then
   set +e
   random_03=$(expr $RANDOM % 4)
   set -e
   if [ "$random_03" == 0 ]
   then
      echo "   Running $test_file this time (it takes about 2 minutes)."
   else
      echo "   Skipping $test_file this time (it takes about 2 minutes)."
      exit 0
   fi
fi
#
# try_number
for try_number in {1..3}
do
   if python3 $test_file >& run_test.tmp
   then
      if [ "$test_file" == 'test/csv/rcond_lower.py' ]
      then
         $sed_path -i run_test.tmp \
            -e '/sample_fixed: *rcond *=/d'
      fi
      if [ "$test_file" == 'test/recover_fit.py' ]
      then
         $sed_path -i run_test.tmp \
            -e '/fixed effects information matrix is not positive/d' \
            -e '/sample table was not created/d'
      fi
      if [ "$test_file" == 'test/csv/sample_fail.py' ]
      then
         $sed_path -i run_test.tmp \
            -e '/dismod_at warning: sample asymptotic/d' \
            -e '/sample table was not created/d'
      fi
      # virtual box is getting these warnings:
      $sed_path -i run_test.tmp \
         -e '/^libEGL warning: egl: failed to create dri2 screen/d'
      if ! grep 'warning:' run_test.tmp > /dev/null
      then
         cat run_test.tmp
         rm run_test.tmp
         echo 'run_test.sh: OK'
         exit 0
      fi
   fi
   echo "run_test.sh $test_file: Error or warning during try number $try_number"
done
cat run_test.tmp
rm run_test.tmp
echo "run_test.sh: $test_file: giving up after try number $try_number"
exit 1
