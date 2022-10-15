# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-22 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin clear_shared}
{xrst_spell
   errno
   inuse
}

Clear at_cascade Shared Memory
##############################

Syntax
******
clear_shared(all_node_database)

Purpose
*******
This routine clears the at_cascade shared memory that is in use
and has a particular prefix.
For example, you may get the following error message when trying
to run the cascade:

   FileExistsError: [Errno 17] File exists: *name*

where *name* ends with ``_number_cpu_inuse`` or ``_job_status``.
This may happen if the previous :ref:`run_parallel`
did not terminate cleanly; e.g., if the system crashed.

all_node_database
*****************
is a ``str`` containing a path to the :ref:`all_node_db`.
This is used to determine the
:ref:`all_option_table@shared_memory_prefix`.


{xrst_end clear_shared}
'''
import dismod_at
from multiprocessing import shared_memory
#
def clear_shared(all_node_database) :
   #
   # shared_memory_prefix
   new                  = False
   connection           = dismod_at.create_connection(all_node_database, new)
   all_option_table     = dismod_at.get_table_dict(connection, 'all_option')
   shared_memory_prefix = ""
   for row in all_option_table :
      if row['option_name'] == 'shared_memory_prefix' :
         shared_memory_prefix = row['option_value']
   #
   # shared_memory_name_list
   shared_memory_suffix_list = [ '_number_cpu_inuse', '_job_status', ]
   #
   # shared_memory_suffix
   for shared_memory_suffix in shared_memory_suffix_list :
      shared_memory_name = shared_memory_prefix + shared_memory_suffix
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
