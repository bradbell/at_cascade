# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ----------------------------------------------------------------------------
import os
import sys
import time
import math
import shutil
import csv
import multiprocessing
import dismod_at
# import at_cascade with a preference current directory version
current_directory = os.getcwd()
if os.path.isfile( current_directory + '/at_cascade/__init__.py' ) :
   sys.path.insert(0, current_directory)
import at_cascade
"""
{xrst_begin prior_pred.py}
{xrst_spell
   const
   dage
   delim
   dtime
   eps
   haqi
   meas
   sincidence
   std
   uniform uniform
}

{xrst_end prior_pred.py}
"""

"""
Make temp.py section into a module, which is called by the test. Get that
passing the test, then build on the function and integrate it into predict.py
after.

Later: Try refactoring predict.py so it can predict off either priors or
posteriors, and lets us use the existing parallelizations etc. without
reinventing the wheel. Flag if we use ancestor.db or the no-data prior.db and
the flag switches which is being used. Have the outputs from predict.py go to
subdirectories depending on whether they're from prior or from posterior. We may
need to support predicting from both at the same time.
"""
current_directory = os.getcwd()
# sys.path.insert(0, current_directory)
import at_cascade
#
# example/csv/break_fit_pred.py
command = [ 'python3', 'example/csv/break_fit_pred.py' ] 
if True :
   dismod_at.system_command_prc(command)
#
print('\n\n =============== BEGIN prior_pred.py =============== \n\n')
#
# Run our new prior prediction module
command = [ 'python3', 'at_cascade/csv/predict_prior.py' ] 
if True :
   dismod_at.system_command_prc(command)
print('prior_pred.py: OK')
