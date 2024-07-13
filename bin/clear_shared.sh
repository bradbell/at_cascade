#! /bin/bash -e
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ----------------------------------------------------------------------------
if [ "$0" != 'bin/clear_shared.sh' ] || [ "$#" != 2 ]
then
   echo 'bin/clear_shared.sh all_node_dir job_name'
   echo 'all_node_dir: directory where all_node.db is located'
   echo 'job_name:     is the node_name.sex_name'
   exit 1
fi
all_node_dir="$1"
job_name="$2"
#
cat << EOF > python.$$
import at_cascade
all_node_database = '$all_node_dir/all_node.db'
job_name          = '$job_name'
at_cascade.clear_shared(all_node_database, job_name)
EOF
python3 python.$$
rm python.$$
echo 'clear_shared.sh: OK'
exit 0
