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
echo "xrst at_cascade.xrst --target $target --output doc $rst_line"
if ! xrst at_cascade.xrst --target $target --output doc $rst_line >& \
    >( tee run_sphinx.$$ )
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
