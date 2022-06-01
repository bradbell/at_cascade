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
if [ "$0" != 'bin/ihme/get_csv_input.sh' ]
then
    echo 'usage: bin/get_csv_input.sh diseash'
    echo "where disease is one of: $disease_list"
    exit 1
fi
#
# ok
ok=no
disease_list='asthma copd diabetes neural_tube'
for disease in $disease_list
do
    if [ "$1" == "$disease" ]
    then
        ok=yes
    fi
done
if [ "$ok" != 'yes' ]
then
    echo 'get_csv_input.sh: disease is not one of the following:'
    echo "$disease_list"
    exit 1
fi
#
# disease
disease="$1"
# -----------------------------------------------------------------------------
set -e
#
# local_at, remove_at, remote_machine
local_at='ihme_db/DisMod_AT'
remote_at='/snfs1/Project/nfrqe/DisMod_AT'
remote_machine='gen-slurm-slogin-p01.cluster.ihme.washington.edu'
remote_connect="$USER@$remote_machine"
# -----------------------------------------------------------------------------
if ! ping  -c 1 $remote_machine > /dev/null
then
    echo "get_csv_input.sh: ping -c 1 $remote_machine failed"
    exit 1
fi
# -----------------------------------------------------------------------------
# local_at
if [ ! -e $local_at ]
then
    echo_eval mkdir -p $local_at
fi
# -----------------------------------------------------------------------------
# copy_file(remote_dir, remote_connect, local_dir, file)
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
        remote_size=$(ssh -q $remote_connect "$remote_command")
        if [ "$remote_size" != "$local_size" ]
        then
            echo "$local_size = size of $local_dir/$file"
            echo "$remote_size = size of $remote_connect:$remotd_dir/$file"
            exit 1
        fi
    else
        echo_eval scp -q $remote_connect:$remote_dir/$file $local_dir/$file
    fi
}
# -----------------------------------------------------------------------------
# files used by all diseases
#
# local_dir, remote_dir
local_dir="$local_at/metadata"
remote_dir="$remote_at/metadata"
#
# meta_data_csv_file_list
metadata_csv_file_list='
    gbd2019_location_map.csv
    gbd2019_age_metadata.csv
'
#
# file
for file in $metadata_csv_file_list
do
    copy_file
done
#
# local_dir, remote_dir, file
local_dir="$local_at/mtall"
remote_dir="$remote_at/mtall"
file='gbd2019_all_cause_mortality.csv'
#
copy_file
# -----------------------------------------------------------------------------
# disease specific covariate files
#
# locat_dir, remote_dir
local_dir="$local_at/covariates"
remote_dir="$remote_at/covariates"
#
# covariate_csv_file_list
case $disease in

    asthma)
    covariate_csv_file_list='
    gbd2019_SEV_scalar_asthma_log_transform_covariate.csv
    gbd2019_haqi_covariate.csv
    '
    ;;

    copd)
    covariate_csv_file_list='
    gbd2019_SEV_scalar_COPD_age_std_log_transform_covariate.csv
    gbd2019_elevation_over_1500m_covariate.csv
    gbd2019_haqi_covariate.csv
    '
    ;;

    diabetes)
    covariate_csv_file_list='
    gbd2019_ldi_log_transformed_covariate.csv
    gbd2019_obesity_prevalence_covariate.csv
    '
    ;;

    *)
    echo 'get_csv_input.sh: program error'
    exit 1

esac
#
# file
for file in $covariate_csv_file_list
do
    copy_file
done
# -----------------------------------------------------------------------------
# disease specific data files
#
local_dir="$local_at/testing/$disease/data"
remote_dir="$remote_at/testing/$disease/data"
#
# data_csv_file_list
case $disease in

    asthma)
    data_csv_file_list='
    gbd2019_asthma_crosswalk_12080.csv
    gbd2019_asthma_csmr.csv
    '
    ;;

    copd)
    data_csv_file_list='
    gbd2019_copd_crosswalk_5528.csv
    gbd2019_copd_csmr.csv
    '
    ;;

    diabetes)
    data_csv_file_list='
    gbd2019_diabetes_crosswalk_12437.csv
    '
    ;;

    *)
    echo 'get_csv_input.sh: program error'
    exit 1
esac
#
# file
for file in $data_csv_file_list
do
    copy_file
done
# -----------------------------------------------------------------------------
echo 'get_csv_input.sh: OK'
exit 0
