# -----------------------------------------------------------------------------
# at_cascade: Cascading Dismod_at Analysis From Parent To Child Regions
#           Copyright (C) 2021-22 University of Washington
#              (Bradley M. Bell bradbell@uw.edu)
#
# This program is distributed under the terms of the
#     GNU Affero General Public License version 3.0 or later
# see http://www.gnu.org/licenses/agpl.txt
# -----------------------------------------------------------------------------
'''
{xsrst_begin clear_shared}
{xsrst_spell
    inuse
    Errno
}

Clear at_cascade Shared Memory
##############################

Syntax
******
clear_shared()

Purpose
*******
This routine clears the at_cascade memory pointers that are in use.
For example, you may get the following error message when trying
to run the cascade:

    FileExistsError: [Errno 17] File exists: '/at_cascade_number_cpu_inuse'

This may happen if the previous :ref:`run_parallel`
did not terminate cleanly; e.g., if the system crashed.


{xsrst_end clear_shared}
'''
from multiprocessing import shared_memory
#
def clear_shared() :
    #
    # shared_memory_name_list
    shared_memory_name_list = [
        'at_cascade_number_cpu_inuse',
        'at_cascade_job_status',
    ]
    #
    # shared_memory_name
    for shared_memory_name in shared_memory_name_list :
        try :
            shm = shared_memory.SharedMemory(
                create = True, name = shared_memory_name, size = 1
            )
        except FileExistsError :
            try :
                shm = shared_memory.SharedMemory(
                    create = False, name = shared_memory_name
                )
            except Exception as e :
                msg = str(e)
                assert False, msg
        #
        print(f'removing shared memory: {shared_memory_name}')
        shm.close()
        shm.unlink()
