# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin clear_shared}
{xrst_spell
   errno
   inuse
}

Clear at_cascade Shared Memory
##############################

Prototype
*********
{xrst_literal
   # BEGIN DEF
   # END DEF
}

Purpose
*******
This routine clears the at_cascade shared memory that is in use
and has a particular prefix.
For example, you may get the following error message when trying
to run the cascade:

   FileExistsError: [Errno 17] File exists: *name*

where *name* ends with ``_number_cpu_inuse`` or ``_job_status``.
This may happen if the previous :ref:`fit_parallel-name`
did not terminate cleanly; e.g., if the system crashed.

all_node_database
*****************
is a path to the :ref:`all_node_db-name`.
This is used to determine the
:ref:`option_all_table@shared_memory_prefix`.

job_name
********
This is the :ref:`create_job_table@job_table@job_name`
for the shared memory that we are clearing; see
:ref:`fit_parallel@shared_unique` .

{xrst_end clear_shared}
'''
import dismod_at
from multiprocessing import shared_memory
# BEGIN DEF
# at_cascade.clear_shared
def clear_shared(all_node_database, job_name) :
   assert type(all_node_database) == str
   assert type(job_name) == str
   # END DEF
   #
   # shared_memory_prefix
   connection           = dismod_at.create_connection(
      all_node_database, new = False, readonly = True
   )
   option_all_table     = dismod_at.get_table_dict(connection, 'option_all')
   connection.close()
   shared_memory_prefix = ""
   for row in option_all_table :
      if row['option_name'] == 'shared_memory_prefix' :
         shared_memory_prefix = row['option_value']
   #
   #
   # shared_memory_prefix_plus
   shared_memory_prefix_plus = f'{shared_memory_prefix}_{job_name}'
   #
   # name
   for name in  [ '_number_cpu_inuse', '_job_status' ] :
      #
      # shared_memory_name
      shared_memory_name = shared_memory_prefix_plus + name
      mapped_memory_name = at_cascde.map_shared( shared_memory_name )
      try :
         shm = shared_memory.SharedMemory(
            create = True, name = mapped_memory_name, size = 1
         )
         exists = False
      except FileExistsError :
         try :
            shm = shared_memory.SharedMemory(
               create = False, name = mapped_memory_name
            )
            exist = True
         except Exception as e :
            print( str(e) )
            exist = None
      #
      if exists == None :
         print( f'Unknonw state: {shared_memory_name}' )
         print( 'Try re-runing clear_shared')
      else :
         if exists :
            print( f'Did Find:       {shared_memory_name}' )
         else :
            print( f'Did Not Find:   {shared_memory_name}' )
         #
         shm.close()
         shm.unlink()
   print('clear_shared: OK')
