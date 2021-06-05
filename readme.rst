AT Cascade Plan
***************

.. _dismod_at: https://bradbell.github.io/dismod_at/doc/dismod_at.htm
.. _dismod_at_input: https://bradbell.github.io/dismod_at/doc/input.htm

Purpose
#######
Run dismod_at_ starting at the root of the node tree and ending at a leaf.
The prior for a non-root node uses the prior for the root node
plus the fit for the parent of the non-root node.

============    ==================================================
**Notation**    **Meaning**
world_node      The top level node at which the cascade starts
fit_node        The option table parent node for a dismod_at fit
mtall           All cause mortality data
mtspecific      Cause specific mortality data
mtother         Other cause mortality data
omega           The model rate for other cause mortality
omega_grid      A single age-time grid used for omega constraints
============    ==================================================

Input Data
##########

World Database
==============
A dismod_at database were the world_node is the parent in the option table;
i.e., it is the fit_node.

1. There is no mtall or mtother data in this database.
2. There is no prior or grid for omega in this database.
3. The avgint table covariate values are null.
   In addition, the avgint node_id values are changed to the fit_node.
   This makes the predict table yield predictions for the fit_node.
4. Subgroups are not used; i.e., there is one group and one subgroup
   corresponding to all the data.
5. The option table parent_node in this database specifies the world_node.
6. The covariate table reference values must be the same as the other database
   reference values for the world_node. The max difference is set to infinity
   for all covariates (see next item).
7. The node table is used to control splits by any covariate at any level.
   For example, the world_node could correspond to both sexes. The next
   level below could be the female / male split of that node. All levels below
   a female (male) node would be female (male) nodes.

Other Database
==============
In addition to the dismod_at database,
a database with the following information will also be needed:

1. The mtall data for every node on the omega_grid.
   The same table could be used to hold this information for all diseases.
2. The mtspecific data for every node on the omega_grid.
   Note that mtspecific is different for each disease.
   For each node and grid point, the omega constraints are computed using
   omega = mtall - mtspecific.
3. Covariate reference for every covariate in the world_node database
   and every node that we are predicting for. If this includes all covariates,
   the same table could be used for all diseases.

Program Plan
############
1. Use cascade_ode and fit_ihme.py to get ideas for the design the algorithm.
2. Test using a data simulator with at least two levels of random effects.
3. Use python for the program and sphinx/rst for the documentation.
4. Run fit_nodes at the same level in parallel where
   running a node includes running its child nodes.
   There will be an abstract interface for launching parallel jobs so
   it can run on a cluster or a single computer.
5. There will be a drill option where a drill_node is specified
   and only the ancestors of the drill_node, up to the world node, are run
   as the fit_node
6. The world database only specifies priors when fit_node is world_node.
   If *node* is not the world_node, the value priors when fit_node is *node*
   are computed using the posterior distributions for the fit where fit_node
   is the parent of *node*. The difference priors are the same as for the
   world_node.

Output Data
###########
For each fit_node, the corresponding log table will tell if the fit
completed successfully and it not what the error was.
If it did complete successfully,
or it it reached the maximum number of iterations,
samples corresponding to the avgint table will be in the predict table.
One will be able to continue the fits that terminated due to the
maximum number of iterations being reached.
