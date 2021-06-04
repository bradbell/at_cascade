AT Cascade Plan
***************

.. _dismod_at: https://bradbell.github.io/dismod_at/doc/dismod_at.htm
.. _dismod_at_input: https://bradbell.github.io/dismod_at/doc/input.htm

Purpose
#######
Run dismod_at_ starting at the root of the node tree and ending at a leaf.
The prior for a non-root node uses the prior for the root node
plus the fit for the parent of the non-root node.

Input Data
##########
Use the input tables from a dismod_at data for the world level to provided
as much information as possible; see dismod_at_input_\ .
In addition, a database with the following information will also be needed:

1. All cause mortality (mtall) for every node and
   on a rectangular grid in age and time.
   The same table could be used to hold this information for all diseases.
2. Cause specific mortality (mtspecific) for every node and
   on a rectangular grid in age and time.
   This is needed to compute the other cause mortality (omega) constraints:
   omega = mtall - mtspecific.
   Note that cause specific mortality is different for each disease so perhaps
   it should be in a differnent table that all cause mortality.
3. Covariate reference for every covariate (that appears in the world database)
   and every node (that we are predicting for). If it includes all covariates,
   the same table could be used for all diseases.

The mtall data in the world level dismod_at database will not be used.
(The mtspecifc data in that database will be used during fitting.)

Program Plan
############
1. Use cascade_ode and fit_ihme.py to get ideas for the design the algorithm.
2. Test using a data simulator with two levels of random effects.
3. Use python for the program and sphinx/rst for the documentation.
4. Run nodes at the same level in parallel
   (running a node will include running its children).
   There will be an abstract interface for lanuching parallel jobs so
   it can run on a cluster or a single computer.
5. There will be a drill option, where only one node is run at each level.
