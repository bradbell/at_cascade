AT Cascade
**********

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

1. All cause mortality for every node. This can be done once for all diseases.
2. Covariate reference for every covariate (in the world database)
   and every node (that we are prediciting for). If we include all covariates,
   this can be done once for all diseases.
3. Cause specific mortality for every node, so that we can compute other cause
   mortailty (all cause mortality minus cause specific mortality).
4. A list of which integrand are not really input data and should only
   be used to help initialization of the fit.
