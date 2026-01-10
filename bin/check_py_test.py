#! /usr/bin/env python
# -----------------------------------------------------------------------------
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-25 Bradley M. Bell
# -----------------------------------------------------------------------------
#
# The python program ``bin/check_test.py`` runs of the *.py files in the
# example and test directories.
#
# If one of these tests fails,
# it will be tried again up to three times. This handles the case where
# a test uses the clock for a random seed and will try a different
# random seed the each time.
#
#. If a test fails three times in a row, check_test.py will exit with an error.
#
#
#
import os
import sys
import subprocess
import time
#
#
# main
def main() :
   #
   # subdir
   if sys.argv[0] != 'bin/check_py_test.py' :
      sys.exit( 'bin/check_py_test.py must be run from its parent directory' )
   if len(sys.argv) != 1 :
      sys.exit( 'bin/check_py_test.py does not expect any arguments' )
   #
   # max_try
   # maximum number of times to try to pass each test
   max_try = 3
   #
   # start_check
   start_check = time.time()
   #
   # python_executable
   python_executable = sys.executable
   #
   # file_list
   # *.py files below the example and test directories (excluding temp.*)
   file_list = []
   for subdir in [ 'example', 'test' ] :
      for root, dirs, files in os.walk(subdir) :
         for file in files :
            if file.endswith('.py') and not file.startswith('temp.') :
               file_list.append( os.path.join(root, file) )
   #
   # max_len
   max_len = 0
   for file in file_list :
      max_len  = max( max_len, len(file) )
   #
   # test_file, start
   end = time.time()
   for test_file in file_list :
      start = end
      #
      # print test_file
      n_fill = max_len - len(test_file)
      print(test_file + n_fill * ' ', end = '' )
      sys.stdout.flush()
      #
      # n_try, test_passed
      n_try        = 0
      test_passed  = False
      while not test_passed and n_try < max_try :
         n_try += 1
         #
         # result
         command = [ python_executable, test_file ]
         result  = subprocess.run(
            command,
            text      = True,
            stdout    = subprocess.PIPE,
            stderr    = subprocess.STDOUT,
         )
         #
         if result.returncode != 0 and n_try == max_try :
            print(': Error')
            assert result.stderr == None
            assert type( result.stdout ) == str
            sys.exit( result.stdout )
         #
         # test_passed
         if result.returncode == 0 :
            test_passed = True
            #
            # end
            end     = time.time()
            #
            # print test_file OK message
            seconds = end - start
            seconds = '{:6.2f}'.format(seconds)
            if n_try == 1 :
               print(f':          : seconds = {seconds}: OK')
            else :
               print(f': n_try = {n_try}: seconds = {seconds}: OK')
   #
   # print test_all OK message
   end_check = time.time()
   minutes = ( end_check - start_check) / 60.0
   minutes = round(minutes, 2)
   print(f'bin/check_py_test.py: minutes = {minutes}: OK')
#
main()
