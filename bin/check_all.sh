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
if [ "$0" != 'bin/check_all.sh' ]
then
    echo 'bin/check_all.sh must be run from its parent directory.'
    exit 1
fi
# -----------------------------------------------------------------------------
echo_eval bin/run_sphinx.sh 0
# BEGIN_SORT_THIS_LINE_PLUS_2
list='
    example/absolute_covariates.py
    example/max_fit_option.py
    example/no_ode_xam.py
    example/one_at_function.py
    example/prevalence2iota.py
    example/split_list.py
    test/avgint_parent_grid.py
    test/data4cov_reference.py
    test/get_fit_children.py
    test/get_fit_integrand.py
    test/omega_constraint.py
'
# END_SORT_THIS_LINE_MINUS_2
for script in $list
do
    echo_eval python3 $script
done
# -----------------------------------------------------------------------------
echo 'check_all.sh: OK'
exit 0
