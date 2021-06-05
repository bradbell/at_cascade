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
omega           The model rate for other cause mortality
============    ==============================================

Input Data
##########

Dismod_at Data
==============
A dismod_at database were the world_node is the parent in the option table;
see dismod_at_input_\ .

1. The mtall data in this database is not used.
2. This database specifies the priors when the fit_node is the world_node.
   If *node* is not the world_node, the priors when the fit_node is *node*
   are computed using the posterior distributions for the fit where fit_node
   is the parent of *node*.


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

Program Plan
############
1. Use cascade_ode and fit_ihme.py to get ideas for the design the algorithm.
2. Test using a data simulator with at least two levels of random effects.
3. Use python for the program and sphinx/rst for the documentation.
4. Run fit_nodes at the same level in parallel where
   running a node includes running its child nodes.
   There will be an abstract interface for lanuching parallel jobs so
   it can run on a cluster or a single computer.
5. There will be a drill option where a drill_node is specified
   and only the ancestors of the drill_node, up to the world node, are run
   as the fit_node
