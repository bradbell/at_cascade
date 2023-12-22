#! /bin/bash -e
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-23 Bradley M. Bell
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
test_file="$1"
for try in {1..2}
do
   if python3 $test_file >& run_test.tmp
   then
      if [ "$test_file" == 'test/recover_fit.py' ]
      then
         sed -i run_test.tmp \
            -e '/fixed effects information matrix is not positive/d' \
            -e '/sample table was not created/d'
      fi
      if [ "$test_file" == 'test/csv_sample_fail.py' ]
      then
         sed -i run_test.tmp \
            -e '/dismod_at warning: sample asymptotic/d' \
            -e '/sample table was not created/d'
      fi
      if ! grep 'warning:' run_test.tmp > /dev/null
      then
         cat run_test.tmp
         rm run_test.tmp
         echo 'run_test.sh: OK'
         exit 0
      fi
   fi
   if [ "$try" != '2' ]
   then
      echo "$run_test: Error or warning, re-running with a different seed:"
      echo 'sleep 1'
      sleep 1
   fi
done
cat run_test.tmp
rm run_test.tmp
echo "run_test.sh: $test_file: Error or warning 2 times in a row."
exit 1
