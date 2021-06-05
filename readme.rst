AT Cascade Plan
***************

.. _dismod_at: https://bradbell.github.io/dismod_at/doc/dismod_at.htm
.. _dismod_at_input: https://bradbell.github.io/dismod_at/doc/input.htm

Purpose
#######
Run dismod_at_ starting at the root of the node tree and ending at a leaf.
The prior for a non-root node uses the prior for the root node
plus the fit for the parent of the non-root node.

============    ==============================================
**Notation**    **Meaning**
world_node      The top level node at which the cascade starts
fit_node        Is the parent node in a dismod_at fit
mtall           All cause mortality data
mtspecific      Cause specific mortality data
mtother         Other cause mortality data
omega           The model rate for other cause mortality
============    ==============================================

Input Data
##########

Dismod_at Data
==============
A dismod_at database were the world_node is the parent in the option table;
i.e., it is the fit_node.

1. The mtall data in this database is not used.
2. This database specifies the priors when the fit_node is the world_node.
   If *node* is not the world_node, the priors when the fit_node is *node*
   are computed using the posterior distributions for the fit where fit_node
   is the parent of *node*.
3. The priors on omega and mtother data are ignored.
4. For each fit, the values in the node_id column of the avgint table are
   changed to correspond to the fit_node. In addition, the covariate
   values are changed to the reference value for the fit_node.
   This makes the predict table yield predictions for the fit_node.
5. Subgroups are not used; i.e., there is one group and one subgroup
   corresponding to all the data.


Other Data
==========
In addition to the dismod_at database,
a database with the following information will also be needed:

1. The mtall data on a rectangular grid in age and time.
   The same table could be used to hold this information for all diseases.
2. The mtspecific data for every node on a rectangular grid in age and time.
   This is needed to compute the the omega constraints using
   omega = mtall - mtspecific.
   Note that cause specific mortality is different for each disease.
3. Covariate reference for every covariate in the world_node database
   and every node that we are predicting for. If this includes all covariates,
   the same table could be used for all diseases.
4. Option settings that are just for the cascade. For example:

   - a random seed
   - a maximum number of data points per integrand

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

Output Data
###########
For each fit_node, the corresponding log table will tell if the fit
completed successfully and it not what the error was.
If it did complete successfully,
or it it reached the maximum number of iterations,
samples corresponding to the avgint table will be in the predict table.
One will be able to continue the fits that terminated due to the
maximum number of iterations being reached.
