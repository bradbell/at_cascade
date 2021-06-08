AT Cascade Plan
***************

.. _dismod_at: https://bradbell.github.io/dismod_at/doc/dismod_at.htm
.. _dismod_at_input: https://bradbell.github.io/dismod_at/doc/input.htm

Purpose
#######
Run a dismod_at_ fit starting at start_node and ending at
and all the nodes in end_node_set.
All of the nodes between start_node and and element of end_node_set are fit.

=============   ==================================================
**Notation**    **Meaning**
start_node      The top level node for this cascade
end_node_set    This is a set of nodes below start_node
fit_node        The option table parent node for a dismod_at fit
mtall           All cause mortality data
mtspecific      Cause specific mortality data
mtother         Other cause mortality data
omega           The model rate for other cause mortality
omega_grid      A single age-time grid used for omega constraints
sex_level       Level below start_node where fits split by sex
top_directory   Directory where the input data is located
cascade         end_node_set has more than one element
drill           end_note_set has only one element
=============   ==================================================


Input Data
##########
We are using a dismod_at start_node database so we can use the dismod_at
database specifications.
In addition, current cascade_at can be used to download a lot of the data.
Eventually, the two databases below should probably be joined into one.

Start Node Database
===================
A dismod_at database were the start_node is the parent in the option table;
i.e., it is the fit_node.

- There is no mtall or mtother data in this database.
- There is no prior or grid for omega in this database.
- The avgint table covariate values are null.
  The avgint node_id values correspond to the start_node.
- Subgroups are not used; i.e., there is one group and one subgroup
  corresponding to all the data.
- The option table parent_node in this database specifies the start_node.
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

  - The end_node_set.
  - The sex_level. If the start_node corresponds to one sex,
    sex_level would be zero; i.e., there is no sex split.

Program Plan
############
- Use cascade_ode, fit_ihme.py, cascade_at,
  to get ideas for the design the algorithm.
- Test using a data simulator with at least two levels of random effects.
- Use python for the program and sphinx/rst for the documentation.
- For a cascade, fit nodes at the same level in parallel where
  running a node includes running its child nodes.
  There will be an abstract interface for launching parallel jobs so
  it can run on a cluster or a single computer.
- For a drill, fit will run sequentially (not launch other processes).
  This will be easier to debug and should give the same result as a cascade
  (for all of the nodes in the drill).
- The start_node database only specifies priors when fit_node is start_node.
  If *node* is not the start_node, the value priors when fit_node is *node*
  are computed using the posterior distributions for the fit where fit_node
  is the parent of *node*. The difference priors are the same as for the
  start_node.
- The avgint node_id column will be set to the fit_node.
  This makes the predict table yield predictions for the fit_node.
- If a fit terminates with an error, the corresponding predictions are not
  calculated, none of its child nodes are fit, and the fit can't be continued.
- If a fit_node terminates with a warning (or no warning), the corresponding
  predictions are calculated. If it terminates with maximum iterations warning,
  none of its child nodes are run and the fit can be continued
  (including the child node fits).

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

dismod.db
=========
This database contains the information listed below
for the corresponding $icode fit_node_id$$:

===========    ============================================================
**Table**      **Information**
log            warnings and error messages
predict        results corresponding to fit_node and avgint table
fixed_trace    optimizer trace for optimizing the fixed effects
sample         Posterior samples of the fixed and random effects
predict        Avgint results correspsonding sample table and this fit_node
===========    ============================================================
