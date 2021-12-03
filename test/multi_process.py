# -----------------------------------------------------------------------------
# at_cascade: Cascading Dismod_at Analysis From Parent To Child Regions
#           Copyright (C) 2021-21 University of Washington
#              (Bradley M. Bell bradbell@uw.edu)
#
# This program is distributed under the terms of the
#     GNU Affero General Public License version 3.0 or later
# see http://www.gnu.org/licenses/agpl.txt
# ----------------------------------------------------------------------------
# imports
# ----------------------------------------------------------------------------
import multiprocessing
#
# ----------------------------------------------------------------------------
# global variables
# ----------------------------------------------------------------------------
max_pro    = 5
number_pro = 0
node_table = [
    { 'node' : 0, 'parent' : None , 'start' : False, 'done' : False  },
    { 'node' : 1, 'parent' : 0    , 'start' : False, 'done' : False },
    { 'node' : 2, 'parent' : 0    , 'start' : False, 'done' : False },
    { 'node' : 3, 'parent' : 1    , 'start' : False, 'done' : False },
    { 'node' : 4, 'parent' : 1    , 'start' : False, 'done' : False },
    { 'node' : 5, 'parent' : 2    , 'start' : False, 'done' : False },
    { 'node' : 6, 'parent' : 2    , 'start' : False, 'done' : False },
]
# -----------------------------------------------------------------------------
# functions
# -----------------------------------------------------------------------------
def worker(node, lock):
    """worker function"""
    global number_pro
    #
    row = node_table[node]
    assert row['start']
    #
    lock.acquire()
    row['done'] = True
    print( f'node {node} done' )
    #
    ready = list()
    for row in node_table :
        node   = row['node']
        start  = row['start']
        parent = row['parent']
        if not start  and node_table[parent]['done'] :
            ready.append( node )
    n_do   = min( max_pro - number_pro + 1, len(ready) )
    do_set = ready[: n_do]
    for node in do_set :
        assert not node_table[node]['start']
        node_table[node]['start'] = True
    number_pro = number_pro + n_do - 1
    lock.release()
    #
    if n_do > 0 :
        for i in range(1, n_do) :
            node = do_set[i]
            p = multiprocessing.Process(
                target = worker ,
                args   = (node, lock)
            )
            p.deamon = True
            p.start()
        #
        node = do_set[0]
        worker(node, lock)
    #
    return

if __name__ == '__main__':
    lock = multiprocessing.Lock()
    node = 0
    node_table[node]['start'] = True
    worker(node, lock)
