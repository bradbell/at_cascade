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
# -----------------------------------------------------------------------------
echo_eval xsrst.py html doc.xsrst sphinx spelling keyword
echo_eval sphinx-build -b html sphinx doc
# -----------------------------------------------------------------------------
echo 'run_sphinx.sh: OK'
exit 0
