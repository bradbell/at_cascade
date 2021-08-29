#! /bin/bash -e
# -----------------------------------------------------------------------------
# at_cascade: Cascading Dismod_at Analysis From Parent To Child Regions
#           Copyright (C) 2021-21 University of Washington
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
if [ "$0" != 'bin/run_sphinx.sh' ]
then
    echo 'bin/run_sphinx.sh must be run from its parent directory.'
    exit 1
fi
if [ "$1" != '' ]
then
    line_increment=10
else
    line_increment=''
fi
# -----------------------------------------------------------------------------
echo "xsrst.py html doc.xsrst sphinx spelling keyword $line_increment"
if ! xsrst.py html doc.xsrst sphinx spelling keyword $line_increment >& run_sphinx.$$
then
    cat run_sphinx.$$
    echo 'bin/run_sphinx: aboring due to xsrst errors above'
    rm run_sphinx.$$
    exit 1
fi
if grep '^warning:' run_sphinx.$$ > /dev/null
then
    cat run_sphinx.$$
    echo 'bin/run_sphinx: aboring due to xsrst warnings above'
    rm run_sphinx.$$
    exit 1
fi
# -----------------------------------------------------------------------------
echo 'sphinx-build -b html sphinx doc'
if ! sphinx-build -b html sphinx doc >& run_sphinx.$$
then
    cat run_sphinx.$$
    echo 'bin/run_sphinx: aboring due to sphinx warnings above'
    rm run_sphinx.$$
    exit 1
fi
if grep '^build succeeded,.*warning' run_sphinx.$$ > /dev/null
then
    cat run_sphinx.$$
    echo 'bin/run_sphinx: aboring due to sphinx warnings above'
    rm run_sphinx.$$
    exit 1
fi
# -----------------------------------------------------------------------------
rm run_sphinx.$$
echo 'run_sphinx.sh: OK'
exit 0
