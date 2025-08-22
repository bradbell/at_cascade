#! /bin/bash -e
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2014-25 Bradley M. Bell
# ----------------------------------------------------------------------------
# test install of python module and executable
# ---------------------------------------------------------------------------
if [ "$0" != "bin/check_install.sh" ]
then
   echo "bin/check_install.sh: must be executed from its parent directory"
   exit 1
fi
# -----------------------------------------------------------------------------
# echo_eval
echo_eval() {
   echo $*
   eval $*
}
# -----------------------------------------------------------------------------
#
# check_install
if [ -e 'build/check_install' ]
then
   echo_eval rm -r build/check_install
fi
echo_eval mkdir build/check_install
echo_eval cd build/check_install
#
# uninstall
if pip3 list | grep '^at[_-]cascade ' > /dev/null
then
   pip3 uninstall --yes at_cascade
fi
if python3 -c 'import at_cascade' >& /dev/null
then
   python3 -c 'import at_cascade; print(at_cascade.__file__)'
   echo 'check_install.sh: cannot uninstall at_cascade'
   exit 1
fi
#
# install
cd ../..
pip3 install .
cd build/check_install
#
# sim_fit_pred.py
echo_eval python3 ../../example/csv/sim_fit_pred.py sim_fit_pred.py
#
# ---------------------------------------------------------------------------
echo 'check_install.sh: OK'
exit 0
