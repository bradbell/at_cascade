# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ---------------------------------------------------------------------------
import sys
def main() :
   dict_obj = { 'a' : 1, 'z' : 2 , 'd' : 3 }
   dict_obj.update( {'z' : 4,  'c' : 5} )
   assert list( dict_obj.keys() ) == [ 'a', 'z', 'd', 'c' ]
   assert list( dict_obj.values() ) == [ 1, 4, 3, 5 ]
#
if __name__ == '__main__' :
   main()
   print('dict_order: OK')
   sys.exit(0)
