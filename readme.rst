AT Cascade Plan
***************

.. _dismod_at: https://bradbell.github.io/dismod_at/doc/dismod_at.htm
.. _dismod_at_input: https://bradbell.github.io/dismod_at/doc/input.htm

Purpose
#######
Run a dismod_at_ fit starting at start_node and including
all the nodes in end_node_set.
All of the nodes between start_node and each element of end_node_set
are also fit.

=============   ==================================================
**Notation**    **Meaning**
start_node      The top level node for this cascade
end_node_set    This is a set of nodes below start_node
fit_node        Is the dismod_at option table parent node
mtall           All cause mortality data
mtspecific      Cause specific mortality data
mtother         Other cause mortality data
omega           The model rate for other cause mortality
omega_grid      A single age-time grid used for omega constraints
sex_level       Level below start_node where fits split by sex
top_directory   Directory where the input data is located
=============   ==================================================

Input Data
##########
We are using a dismod_at start_node database so we can use the dismod_at
database specifications.
In addition, current cascade_at can be used to download a lot of the data.
Eventually, the two databases below should probably be joined into one.

Start Node Database
===================
A dismod_at database corresponding to fitting the start_node;
i.e., the start_node is the fit_node

- The option table parent_node in this database must be the start_node.
- There is no mtall or mtspecific data in this database
  (because the other database has this information for every node).
- There is no prior or grid for omega in this database
  (because it is computed using mtall - mtspecific).
- The avgint table covariate values are null.
  The avgint node_id values correspond to the start_node.
- Subgroups are not used; i.e., there is one group and one subgroup
  corresponding to all the data.
- The covariate table reference values must be the same as the other database
  reference values for the start_node.

Other Database
==============

In addition to the dismod_at database,
a database with the following information will also be needed:

- The mtall data for every node on the omega_grid.
  The same table could be used to hold this information for all diseases.
- The mtspecific data for every node on the omega_grid.
  Note that mtspecific is different for each disease.
  For each node and grid point, the omega constraints are computed using
  omega = mtall - mtspecific.
- Covariate reference for every covariate in the start_node database
  and every node that we are predicting for. If this includes all covariates,
  the same table could be used for all diseases.
- An option table that applies to the cascade, but not individual fits.

  - The *start_node*.
  - The *end_node_set*.
  - The *sex_level*. If the start_node corresponds to one sex,
    sex_level would be zero; i.e., there is no sex split.
  - Run in *parallel*. If this is true,
    nodes at the same level are fit in parallel.
    Here fitting a node includes fitting its child nodes that are required
    by the end_node_set.
    If *parallel* is false, the fitting will be done sequentially.
    This should be easier to debug and should give the same results.
  - The *min_interval*. Compress to a single point all age and time intervals
    in data table that are less than or equal this value.

Program Plan
############
- Use cascade_ode, fit_ihme.py, cascade_at,
  to get ideas for the design the algorithm.
- Nodes that do not have mtall, or the covariate references
  will not be included in the analysis (nor will children of such nodes).
- Nodes that do not have mtspecific data will approximate the omega
  constraint using just mtall.
  We should indicate which nodes are missing mtspecific data.
- Test using a data simulator with at least two levels of random effects.
- Use python for the program and sphinx/rst for the documentation.
- The start_node database only specifies priors when fit_node is start_node.
  If *node* is not the start_node, the value priors when fit_node is *node*
  are computed using the posterior distributions for the fit where fit_node
  is the parent of *node*. The difference priors are the same as for the
  start_node.
- The avgint node_id column will be set to the fit_node.
  This makes the predict table yield predictions for the fit_node.
- If a fit terminates with an error, the corresponding predictions are not
  calculated, none of its child nodes are fit, and the fit can't be continued.
- If there is no data for a fit_node, no fit is necessary and the predictions
  can be done using the prior means.

Output Data
###########

Directories
===========
We also use the notation start_node_id and fit_node_id for the
node_id of the corresponding to start_node and fit_node.
The results for start_node are stored in

   top_directory/start_node_id/dismod.db

The results for other fit_nodes are stored in

   parent_node_id/fit_node_id/dismod.db

where parent_node is the parent corresponding to fit_node.
Do not confuse this with the the parent_node in the dismod_at option table
which is the fit_node in this context.

dismod.db
=========
This database contains the information listed below
for the corresponding fit_node_id:

===========    ============================================================
**Table**      **Information**
log            warnings and error messages
predict        results corresponding to fit_node and avgint table
trace_fixed    optimizer trace for optimizing the fixed effects
sample         Posterior samples of the fixed and random effects
predict        Avgint results corresponding sample table and this fit_node
===========    ============================================================

Dismod_at Wish List
###################
The following changes to dismod_at would make at_cascade easier to implement,
would make its output easier to understand, or would make it more robust.

- Automatically remove variables at bounds from asymptotic statistics.
- Implement a Jacobian, instead of Hessian, version of asymptotic statistics.

These changes will be made in a backward compatible way so that
current code that uses dismod_at still works.
