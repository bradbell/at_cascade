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
if [ "$0" != 'bin/run_xrst.sh' ]
then
   echo 'bin/run_xrst.sh must be run from its parent directory.'
   exit 1
fi
ok='yes'
# -----------------------------------------------------------------------------
# index_page_name
index_page_name=$(\
   sed -n -e '/^ *--index_page_name*/p' .readthedocs.yaml | \
   sed -e 's|^ *--index_page_name *||' \
)
# -----------------------------------------------------------------------------
# cmd
cmd="xrst \
--local_toc \
--target html \
--html_theme sphinx_rtd_theme \
--index_page_name $index_page_name \
"
echo "$cmd"
if ! $cmd >& >( tee run_xrst.$$ )
then
   echo 'run_xrst.sh: aboring due to xrst errors above'
   rm run_xrst.$$
   exit 1
fi
if grep '^warning:' run_xrst.$$ > /dev/null
then
   echo 'run_xrst.sh: aboring due to xrst warnings above'
   rm run_xrst.$$
   exit 1
fi
# -----------------------------------------------------------------------------
rm run_xrst.$$
echo 'run_xrst.sh: OK'
exit 0
