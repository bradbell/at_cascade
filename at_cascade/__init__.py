# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2021-24 Bradley M. Bell
# ----------------------------------------------------------------------------
'''
{xrst_begin module}
{xrst_spell
   cov
}

The at_cascade Python Module
############################

at_cascade.version
******************
The version number for this copy of at_cascade.
{xrst_code py}'''
version = '2024.8.19'
'''{xrst_code}

at_cascade.constant_table_list
******************************
Some of the dismod_at input tables are the same for every fit of a cascade.
The :ref:`fit_or_root_class-name` uses the
:ref:`glossary@root_node_database` to get the value for these tables:
{xrst_code py} '''
constant_table_list = [
   'age',
   'data',
   'density',
   'integrand',
   'node',
   'rate_eff_cov',
   'subgroup',
   'time',
   'weight',
   'weight_grid',
]
'''{xrst_code}

.. BEGIN_SORT_THIS_LINE_PLUS_2
{xrst_toc_table
   at_cascade/map_shared.py
   at_cascade/add_log_entry.py
   at_cascade/avgint_parent_grid.py
   at_cascade/bilinear.py
   at_cascade/cascade_root_node.py
   at_cascade/check_cascade_node.py
   at_cascade/check_log.py
   at_cascade/clear_shared.py
   at_cascade/continue_cascade.py
   at_cascade/copy_other_tbl.py
   at_cascade/copy_root_db.py
   at_cascade/create_all_node_db.py
   at_cascade/create_job_table.py
   at_cascade/create_shift_db.py
   at_cascade/empty_avgint_table.py
   at_cascade/empty_directory.py
   at_cascade/extract_avgint.py
   at_cascade/fit_one_job.py
   at_cascade/fit_one_process.py
   at_cascade/fit_or_root_class.py
   at_cascade/fit_parallel.py
   at_cascade/get_cov_info.py
   at_cascade/get_cov_reference.py
   at_cascade/get_database_dir.py
   at_cascade/get_fit_children.py
   at_cascade/get_fit_integrand.py
   at_cascade/get_parent_node.py
   at_cascade/get_var_id.py
   at_cascade/job_descendent.py
   at_cascade/move_table.py
   at_cascade/no_ode_fit.py
   at_cascade/omega_constraint.py
   at_cascade/table_exists.py
   at_cascade/table_name2id.py
}
.. END_SORT_THIS_LINE_MINUS_2

{xrst_end module}
'''

# The file at_cascade/csv/__init__.py should be a sibling (not child)
# of this file in the xrst table of contents.

# BEGIN_SORT_THIS_LINE_PLUS_1
from .                      import csv
from .map_shared            import map_shared
from .add_log_entry         import add_log_entry
from .avgint_parent_grid    import avgint_parent_grid
from .bilinear              import bilinear
from .cascade_root_node     import cascade_root_node
from .check_cascade_node    import check_cascade_node
from .check_log             import check_log
from .clear_shared          import clear_shared
from .continue_cascade      import continue_cascade
from .copy_other_tbl        import copy_other_tbl
from .copy_root_db          import copy_root_db
from .create_all_node_db    import create_all_node_db
from .create_job_table      import create_job_table
from .create_shift_db       import create_shift_db
from .empty_avgint_table    import empty_avgint_table
from .empty_directory       import empty_directory
from .extract_avgint        import extract_avgint
from .fit_one_job           import fit_one_job
from .fit_one_process       import fit_one_process
from .fit_or_root_class     import fit_or_root_class
from .fit_parallel          import fit_parallel
from .get_cov_info          import get_cov_info
from .get_cov_reference     import get_cov_reference
from .get_database_dir      import get_database_dir
from .get_fit_children      import get_fit_children
from .get_fit_integrand     import get_fit_integrand
from .get_parent_node       import get_parent_node
from .get_var_id            import get_var_id
from .job_descendent        import job_descendent
from .move_table            import move_table
from .no_ode_fit            import no_ode_fit
from .omega_constraint      import omega_constraint
from .table_exists          import table_exists
from .table_name2id         import table_name2id
# END_SORT_THIS_LINE_MINUS_1
