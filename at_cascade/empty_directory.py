# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin empty_directory}

Create an Empty Directory
#########################

Syntax
******
{xrst_literal
   # BEGIN_DEF
   # END_DEF
}

directory
*********
If this directory exists, it is removed and then re-created.
Otherwise, it is just created.


{xrst_end empty_directory}
'''
# -----------------------------------------------------------------------------
import os
import shutil
#
# BEGIN_DEF
# at_cascade.empty_directory
def empty_directory(directory) :
   assert type(directory) == str
   assert directory.startswith('build/')
   # END_DEF
   #
   if os.path.exists( directory ) :
      shutil.rmtree( directory )
   os.makedirs(directory)
