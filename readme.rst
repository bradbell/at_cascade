AT Cascade Plan
***************

.. _dismod_at: https://bradbell.github.io/dismod_at/doc/dismod_at.htm
.. _dismod_at_input: https://bradbell.github.io/dismod_at/doc/input.htm

Purpose
#######
Run dismod_at_ starting at the root of the node tree and ending at a leaf.
The prior for a non-root node uses the prior for the root node
plus the fit for the parent of the non-root node.

=============   ==================================================
**Notation**    **Meaning**
start_node      The top level node for this cascade
fit_node        The option table parent node for a dismod_at fit
mtall           All cause mortality data
mtspecific      Cause specific mortality data
mtother         Other cause mortality data
omega           The model rate for other cause mortality
omega_grid      A single age-time grid used for omega constraints
sex_level       Level below start_node where fits split by sex
top_directory   Directory where the input data is located
=============   ==================================================

We also use the notation start_node_id and fit_node_id for the
node_id of the corresponding node.

Input Data
##########
We are using a dismod_at start_node data base so we can use its specifications
and so that the the current cascade can be used to download a lot of the data.
Eventually, the two databases below should probably be joined into one.

Start Node Database
===================
A dismod_at database were the start_node is the parent in the option table;
i.e., it is the fit_node.

1. There is no mtall or mtother data in this database.
2. There is no prior or grid for omega in this database.
3. The avgint table covariate values are null.
   The avgint node_id values correspond to the start_node.
4. Subgroups are not used; i.e., there is one group and one subgroup
   corresponding to all the data.
5. The option table parent_node in this database specifies the start_node.
6. The covariate table reference values must be the same as the other database
   reference values for the start_node.

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
3. Covariate reference for every covariate in the start_node database
   and every node that we are predicting for. If this includes all covariates,
   the same table could be used for all diseases.
4. An option table that applies to the cascade, but not individual fits.

   - Is this a drill and if so which node, below the start_node,
     are we drilling down to.
   - The sex_level. If the start_node corresponds to one sex,
     sex_level would be zero; i.e., there is no sex split.

Program Plan
############
1. Use cascade_ode and fit_ihme.py to get ideas for the design the algorithm.
2. Test using a data simulator with at least two levels of random effects.
3. Use python for the program and sphinx/rst for the documentation.
4. Run fit_nodes at the same level in parallel where
   running a node includes running its child nodes.
   There will be an abstract interface for launching parallel jobs so
   it can run on a cluster or a single computer.
5. The start_node database only specifies priors when fit_node is start_node.
   If *node* is not the start_node, the value priors when fit_node is *node*
   are computed using the posterior distributions for the fit where fit_node
   is the parent of *node*. The difference priors are the same as for the
   start_node.
6. The avgint node_id column will be set to the fit_node.
   This makes the predict table yield predictions for the fit_node.
7. If a fit terminates with an error, the corresponding predictions are not
   calculated, none of its child nodes are fit, and the fit can't be continued.
8. If a fit_node terminates with a warning (or no warning), the corresponding
   predictions are calculated. If it terminates with maximum iterations warning,
   none of its child nodes are run and the fit can be continued
   (including the child node fits).

Output Data
###########

Directories
===========
The results for start_node are stored in

    top_directory/start_node_id/dismod.db

where start_node_id is the node id for start_node and dismod.db is a
dismod_at database.
The results for other nodes are stored in

    parent_node_id/fit_node_id/dismod.db

dismod.db
=========
For each fit_node, the corresponding log table will tell if the fit
completed successfully and it not what warning or error occurred.
