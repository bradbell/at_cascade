#! /bin/bash -e
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
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
