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
ok='yes'
if [ "$1" != 'html' ] && [ "$1" != 'pdf' ]
then
    ok='no'
else
    target="$1"
fi
if [ "$2" == '' ]
then
    ok='no'
elif [ "$2" == '0' ]
then
    line_increment=''
else
    line_increment="$2"
fi
if [ "$ok" == 'no' ]
then
    echo 'usage: bin/run_sphinx.sh target line_increment'
    echo 'target is html or pdf'
    echo 'line_increment = 0 for no line number table'
    exit 1
fi
# -----------------------------------------------------------------------------
echo "xrst $target doc.xrst sphinx $line_increment"
if ! xrst $target doc.xrst sphinx $line_increment >& run_sphinx.$$
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
if [ "$target" == 'html' ]
then
    sphinx_target='html'
    destination='doc'
else
    sphinx_target='latex'
    destination='doc/latex'
fi
echo "sphinx-build -b $sphinx_target sphinx $destination"
if ! sphinx-build -b $sphinx_target sphinx $destination >& run_sphinx.$$
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
if [ "$sphinx_target" == 'latex' ]
then
    echo_eval cd doc/latex
    make at_cascade.pdf
fi
# -----------------------------------------------------------------------------
rm run_sphinx.$$
echo 'run_sphinx.sh: OK'
exit 0
