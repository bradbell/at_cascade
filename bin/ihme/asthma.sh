#! /usr/bin/env bash
# -----------------------------------------------------------------------------
# at_cascade: Cascading Dismod_at Analysis From Parent To Child Regions
#           Copyright (C) 2021-22 University of Washington
#              (Bradley M. Bell bradbell@uw.edu)
#
# This program is distributed under the terms of the
#     GNU Affero General Public License version 3.0 or later
# see http://www.gnu.org/licenses/agpl.txt
# ----------------------------------------------------------------------------
# bash function that echos and executes a command
echo_eval() {
	echo $*
	eval $*
}
# -----------------------------------------------------------------------------
if [ "$0" != 'bin/ihme/asthma.sh' ]
then
    echo 'usage: bin/asthma.sh'
    exit 1
fi
# -----------------------------------------------------------------------------
set -e
local_at='ihme_db/DisMod_AT'
remote_at='/snfs1/Project/nfrqe/DisMod_AT'
remote_machine='bradbell@gen-slurm-slogin-p01.cluster.ihme.washington.edu'
# -----------------------------------------------------------------------------
if [ ! -e $local_at ]
then
    echo_eval mkdir -p $local_at
fi
# -----------------------------------------------------------------------------
function copy_file {
    if [ ! -e $local_dir ]
    then
        echo_eval mkdir -p $local_dir
    fi
    if [ -e $local_dir/$file ]
    then
        echo "Checking size of $local_dir/$file"
        local_size=$(stat --print='%s' $local_dir/$file)
        remote_command="stat --print='%s' $remote_dir/$file"
        remote_size=$(ssh -q $remote_machine "$remote_command")
        if [ "$remote_size" != "$local_size" ]
        then
            echo "$local_size = size of $local_dir/$file"
            echo "$remote_size = size of $remote_machine:$remotd_dir/$file"
            exit 1
        fi
    else
        echo_eval scp -q $remote_machine:$remote_dir/$file $local_dir/$file
    fi
}
# -----------------------------------------------------------------------------
# asthma specific covariate files
#
local_dir="$local_at/covariates"
remote_dir="$remote_at/covariates"
#
covariate_csv_file_list='
    gbd2019_SEV_scalar_asthma_log_transform_covariate.csv
    gbd2019_haqi_covariate.csv
'
for file in $covariate_csv_file_list
do
    copy_file
done
# -----------------------------------------------------------------------------
# asthma specific data files
#
local_dir="$local_at/testing/asthma/data"
remote_dir="$remote_at/testing/asthma/data"
#
data_csv_file_list='
    gbd2019_asthma_crosswalk_12080.csv
    gbd2019_asthma_csmr.csv
'
for file in $data_csv_file_list
do
    copy_file
done
# -----------------------------------------------------------------------------
# files used by all diseases
#
local_dir="$local_at/metadata"
remote_dir="$remote_at/metadata"
#
metadata_csv_file_list='
    gbd2019_location_map.csv
    gbd2019_age_metadata.csv
'
for file in $metadata_csv_file_list
do
    copy_file
done
#
local_dir="$local_at/mtall"
remote_dir="$remote_at/mtall"
file='gbd2019_all_cause_mortality.csv'
copy_file
# -----------------------------------------------------------------------------
echo 'asthma.sh: OK'
exit 0
