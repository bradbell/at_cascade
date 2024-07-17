# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin map_shared}
{xrst_spell
   darwin
}

Map at_cascade Shared Memory Names
##################################

Prototype
*********
{xrst_literal ,
   # BEGIN DEF , # END DEF
   # BEGIN RETURN , # END RETURN
}

Purpose
*******
The mac Darwin system has a limit on the length (in characters) of
shared memory names. This routine returns a hash mapping of the shared memory
name that is short enough to work on all systems.

{xrst_end map_shared}
'''
# BEGIN DEF
# at_cascade.map_shared
import platform
import os
def map_shared(shared_name) :
   assert type(shared_name) == str
   # END DEF
   mac_os  = platform.system() == 'Darwin'
   sandbox  = os.getcwd().endswith('at_cascade.git')
   if mac_os or sandbox :
      hash_code   = 0
      factor      = 0
      for ch in shared_name :
         factor    += 1
         hash_code += factor * ord(ch)
      mapped_name = str( hash_code )
   else :
      mapped = shared_name
   # BEGIN RETURN
   assert type(mapped_name) == str
   return mapped_name
   # END RETURN
