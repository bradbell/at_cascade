#! /bin/bash -e
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
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
if [ "$1" != 'html' ] && [ "$1" != 'pdf' ]
then
   echo 'usage: bin/run_xrst.sh target [ rst_line ]'
   echo 'target is html or pdf'
   exit 1
fi
target="$1"
rst_line="$2"
if [ "$rst_line" != '' ]
then
   rst_line="-rst $rst_line"
fi
# -----------------------------------------------------------------------------
cmd="xrst at_cascade.xrst --target $target --output doc"
if [ "$rst_line" != '' ]
then
   cmd="$cmd --rst $rst_line"
fi
if [ "$target" == 'html' ]
then
   cmd="$cmd --html sphinx_rtd_theme"
fi
echo "$cmd"
if ! $cmd >& >( tee run_sphinx.$$ )
then
   echo 'bin/run_sphinx: aboring due to xrst errors above'
   rm run_sphinx.$$
   exit 1
fi
if grep '^warning:' run_sphinx.$$ > /dev/null
then
   echo 'bin/run_sphinx: aboring due to xrst warnings above'
   rm run_sphinx.$$
   exit 1
fi
# -----------------------------------------------------------------------------
rm run_sphinx.$$
echo 'run_xrst.sh: OK'
exit 0
