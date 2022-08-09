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
    ok='no'
else
    target="$1"
fi
if [ "$2" == '' ]
then
    ok='no'
elif [ "$2" == '0' ]
then
    error_line=''
else
    error_line="-e $2"
fi
if [ "$ok" == 'no' ]
then
    echo 'usage: bin/run_xrst.sh target error_line'
    echo 'target is html or pdf'
    echo 'error_line = 0 for no line number table'
    exit 1
fi
# -----------------------------------------------------------------------------
echo "xrst at_cascade.xrst -t $target -o doc $error_line"
if ! xrst at_cascade.xrst -t $target $error_line -o doc >& >( tee run_sphinx.$$ )
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
