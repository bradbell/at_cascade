# -----------------------------------------------------------------------------
# at_cascade: Cascading Dismod_at Analysis From Parent To Child Regions
#           Copyright (C) 2021-21 University of Washington
#              (Bradley M. Bell bradbell@uw.edu)
#
# This program is distributed under the terms of the
#     GNU Affero General Public License version 3.0 or later
# see http://www.gnu.org/licenses/agpl.txt
# -----------------------------------------------------------------------------
'''
{xsrst_begin get_job_table}

Table of Jobs That Can Run in Parallel
######################################

Under Construction
******************

Syntax
******
{xsrst_file
    # BEGIN syntax
    # END syntax
}

Purpose
*******
This routine returns a list of shift (node_id, split_reference_id) pairs
with a corresponding fit (node_id, split_reference_id) pair.
Each shift pairs requires the corresponding fit pair to have completed before
it can be run.

all_node_database
*****************
is a python string specifying the location of the
:ref:`all_node_db<all_node_db>`
relative to the current working directory.
This argument can't be ``None``.

root_node_database
******************
is a python string specifying the location of the
:ref:`glossary.root_node_database`
relative to the current working directory.
This argument can't be ``None``.

start_node_id
*************
This, together with *start_split_reference_id*
corresponds to a completed fit that we are starting from.

start_split_reference_id
************************
This, together with *start_node_id*
corresponds to a completed fit that we are starting from.
Only jobs that depend on the start jobs completion will be included in
the job table.

fit_goal_set
************
This is the :ref:`glossary.fit_goal_set`.

job_table
*********
The return value *job_table* is a ``list``.
Each row of the list is a ``dict`` with the following keys:
shift_node_id, shift_reference_id, fit_node_id, fit_reference_id.
The shift pair is a job that can be run in parallel.
The fit pair is a job that must be completed before the shift job can be run.



{xsrst_end get_job_table}
'''
# -----------------------------------------------------------------------------
def get_shift_job_table(
    fit_node_id                ,
    fit_split_reference_id     ,
    root_split_reference_id    ,
    split_reference_table      ,
    node_split_set             ,
) :
    #
    # already_split
    already_split = root_split_reference_id != fit_split_reference_id
    #
    # shift_reference_set
    if already_split or fit_node_id not in node_split_set :
        shift_reference_set = { fit_split_reference_id }
    else :
        shift_reference_set = set( range( len(split_reference_table) ) )
        shift_reference_set.remove( root_split_reference_id )
    #
    # shift_node_set
    if fit_node_id in node_split_set and not already_split :
        shift_node_set = { fit_node_id }
    else :
        shift_node_set = fit_children[ fit_node_id ]
    #
    # shift_job_table
    shift_job_table = list()
    for shift_split_reference_id in shift_reference_set :
        for shift_node_id in shift_node_set :
            row = {
                'shift_node_id'            : shift_node_id,
                'shift_split_reference_id' : shift_split_reference_id,
                'fit_node_id'              : fit_node_id,
                'fit_split_reference_id'   : fit_split_reference_id,
            }
            shift_job_table.append( row )
    #
    return shift_job_table
# -----------------------------------------------------------------------------
def get_job_table(
# BEGIN syntax
# job_table = at_cascade.get_job_table(
    all_node_database          = None,
    root_node_database         = None,
    start_node_id              = None,
    start_split_reference_id   = None,
    fit_goal_set               = None,
# )
# END syntax
) :
    #
    # node_table, covariate_table
    root_table      = dict()
    new             = False
    connection      = dismod_at.create_connection(root_node_database, new)
    node_table      = dismod_at.get_table_dict(connection, 'node')
    covariate_table = dismod_at.get_table_dict(connection, 'covariate')
    connection.close()
    #
    # all_table
    all_table = dict()
    new        = False
    connection = dismod_at.create_connection(all_node_database, new)
    tbl_list   =  [ 'all_option', 'split_reference', 'node_split' ]
    for name in tbl_list :
        all_table[name] = dismod_at.get_table_dict(connection, name)
    connection.close()
    #
    # node_split_set
    node_split_set = set()
    for row in all_table['node_split'] :
        node_split_set.add( row['node_id'] )
    #
    # root_node_name
    root_node_name = None
    for row in all_option_table :
        if row['option_name'] == 'root_node_name' :
            root_node_naem = row['option_value']
    #
    # root_node_id
    root_node_id = at_cascade.table_name2id(node_table, 'node', root_node_name)
    #
    # fit_children
    fit_children = at_cascade.get_fit_children(
        root_node_id, fit_goal_set, node_table
    )
    #
    # root_split_reference_id
    cov_info = at_cascade.get_cov_info(
        all_table['all_option'], covariate_table, all_table['split_reference']
    )
    root_split_reference_id = cov_info['split_reference_id']
    #
    # job_table
    job_table = get_shift_job_table(
        start_node_id,
        start_split_reference_id,
        root_split_reference_id,
        all_table['split_reference'],
        node_split_set,
    )
    #
    # job_index
    job_index = 0
    #
    while job_index < len(job_table) :
        #
        # node_id, split_reference
        row                = job_table[job_index]
        node_id            = row['shift_node_id']
        split_reference_id = row['shift_split_reference_id']
        #
        # job_index
        job_index += 1
        #
        # child_job_table
        child_job_table    = get_shift_job_table(
            node_id,
            split_reference_id,
            root_split_reference_id,
            all_table['split_reference'],
            node_split_set,
        )
        #
        # job_table
        job_table += child_job_table
    #
    return job_table
