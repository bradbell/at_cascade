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
if [ "$0" != 'bin/run_sphinx.sh' ]
then
    echo 'bin/run_sphinx.sh must be run from its parent directory.'
    exit 1
fi
if [ "$1" == '' ]
then
    echo 'usage: bin/run_sphinx.sh line_increment'
    echo 'line_increment = 0 for no line number table at the end'
    exit 0
else
    if [ "$1" == '0' ]
    then
        line_increment=''
    else
        line_increment="$1"
    fi
fi
# -----------------------------------------------------------------------------
echo "xrst html doc.xrst sphinx $line_increment"
if ! xrst html doc.xrst sphinx $line_increment >& run_sphinx.$$
then
    cat run_sphinx.$$
    echo 'bin/run_sphinx: aboring due to xrst errors above'
    rm run_sphinx.$$
    exit 1
fi
if grep '^warning:' run_sphinx.$$ > /dev/null
then
    cat run_sphinx.$$
    echo 'bin/run_sphinx: aboring due to xrst warnings above'
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
