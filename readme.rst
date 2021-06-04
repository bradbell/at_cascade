AT Cascade Plan
***************

.. _dismod_at: https://bradbell.github.io/dismod_at/doc/dismod_at.htm

Purpose
#######
Run dismod_at_ starting at the root of the node tree and ending at a leaf.
The prior for a non-root node uses the prior for the root node
plus the fit for the parent of the non-root node.

Input Data
##########
Use a dismod_at data for the world level to provided for as much information
as possible. The following information is missing:

1. All cause mortality (mtall) for every node.
   This can be done once for all diseases.
2. Cause specific mortality (mtspecific) for every node.
   This is needed to compute other cause mortality omega = mtall - mtspecific.
   Note that cause specific mortality is different for each disease.
3. Covariate reference for every covariate (in the world database)
   and every node (that we are predicting for). If we include all covariates,
   this can be done once for all diseases.

The mtall data in the world level dismod_at data base is not used.
(The mtspecifc data in that data base is used.)

Program Plan
############
1. Use cascade_ode and fit_ihme.py to get ideas for the design the algorithm.
2. Test using a data simulator with two levels of random effects.
3. Use python for the program and sphinx/rst for the documentation.
4. Design to run nodes at the same level in parallel where running a node
   includes running its children.
