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
{xsrst_begin xam_level2_leaf4}
{xsrst_spell
    delim
}

A Simple Example with Two Levels and Four Leaf Nodes
====================================================

Node Table
**********
The following is a diagram of the node tree for this example::

                n1
          /-----/\-----\
        n11            n12
      /     \        /     \
    n111   n112    n121   n122

For this example, n1 is the :ref:`glossary.root_node` and
n111, n112, n121, n122 re in the :ref:`glossary.leaf_node_set`.

Statistical Model
*****************

.. list-table:: Notation
    :widths: 10, 5, 50
    :header-rows: 1

    *   - Name
        - Symbol
        - Description
    *   - *iota_r*
        - :math:`\iota_r(a,t)`
        - :ref:`glossary.iota` for *root_node* as a function of age and time.


{xsrst_end xam_level2_leaf4}
'''
