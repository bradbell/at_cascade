#! /usr/bin/env bash
set -e -u
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: Bradley M. Bell <bradbell@seanet.com>
# SPDX-FileContributor: 2020-24 Bradley M. Bell
# -----------------------------------------------------------------------------
# bash function that echos and executes a command
echo_eval() {
   echo $*
   eval $*
}
# -----------------------------------------------------------------------------
if [ $# != 0 ]
then
   echo 'bin/check_version.sh: does not expect any arguments'
   exit 1
fi
if [ "$0" != 'bin/check_version.sh' ]
then
   echo 'bin/check_version.sh: must be executed from its parent directory'
   exit 1
fi
if [ ! -e './.git' ]
then
   echo 'bin/check_version.sh: cannot find ./.git'
   exit 1
fi
# -----------------------------------------------------------------------------
#
# check_version
check_version() {
   sed -f temp.sed "$1" > temp.out
   if ! diff "$1" temp.out > /dev/null
   then
      version_ok='no'
      #
      if [ -x "$1" ]
      then
         mv temp.out "$1"
         chmod +x "$1"
      else
         mv temp.out "$1"
      fi
      echo_eval git diff "$1"
   fi
}
#
# version
version=$(
   sed -n -e '/^ *version *=/p' pyproject.toml | \
      sed -e 's|.*= *||' -e "s|'||g"
)
# branch
branch=$(git branch | sed -n -e '/^[*]/p' | sed -e 's|^[*] *||')
#
# version
if [ "$branch" == 'master' ]
then
   version=$(date +%Y.%m.%d | sed -e 's|\.0*|.|g')
fi
if echo $branch | grep '^stable/' > /dev/null
then
   if ! echo $version | grep '[0-9]\{4\}[.]0[.]' > /dev/null
   then
      echo 'check_version.sh: stable version does not begin with yyyy.0.'
      exit 1
   fi
fi
#
# year
year=$( echo $version | sed -e 's|\..*||' )
#
# version_ok
version_ok='yes'
#
# version_files
version_files='
   pyproject.toml
   at_cascade/__init__.py
   at_cascade.xrst
'
#
# temp.sed
cat << EOF > temp.sed
#
# at_cascade.xrst
s|at_cascade-[0-9]\\{4\\}[.][0-9]*[.][0-9]*|at_cascade-$version|g
#
# pyproject.toml and at_cascade/__init__.py
s|version\\( *\\)= *'[0-9]\\{4\\}[.][0-9]*[.][0-9]*'|version\\1= '$version'|
EOF
#
# check_version
for file in $version_files
do
   check_version $file
done
#
# ----------------------------------------------------------------------------
if [ "$version_ok" == 'no' ]
then
   echo 'bin/check_version.sh: version numbers were fixed (see above).'
   echo "Re-execute bin/check_version.sh $version ?"
   exit 1
fi
echo 'check_version.sh OK'
exit 0
