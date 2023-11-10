# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: University of Washington <https://www.washington.edu>
# SPDX-FileContributor: 2023-11-09 Darius Jake Roy, Garland Culbreth
# ----------------------------------------------------------------------------
{xrst_begin csv_simulate_xam_r}
{xrst_spell
   dir
   sim
}

Example making csv.simulate input files with R
##############################################

Node Tree
*********
::

                n0
          /-----/\-----\
        n1              n2

.. list-table::
   :header-rows: 1

   *  -  Symbol
      -  Documentation
   *  -  sim_dir
      -  :ref:`csv_simulate@sim_dir`
   *  -  csv_file['option_sim.csv']
      -  :ref:`csv_simulate@Input Files@option_sim.csv`
   *  -  csv_file['node.csv']
      -  :ref:`csv_simulate@Input Files@node.csv`
   *  -  csv_file['covariate.csv']
      -  :ref:`csv_simulate@Input Files@covariate.csv`
   *  -  csv_file['no_effect_rate.csv']
      -  :ref:`csv_simulate@Input Files@no_effect_rate.csv`
   *  -  csv_file['multiplier_sim.csv']
      -  :ref:`csv_simulate@Input Files@multiplier_sim.csv`
   *  -  csv_file['simulate.csv']
      -  :ref:`csv_simulate@Input Files@simulate.csv`
   *  -  csv_file['random_effect.csv']
      -  :ref:`csv_simulate@random_effect.csv`
   *  -  csv_file['data_sim.csv']
      -  :ref:`csv_simulate@Output Files@data_sim.csv`

{xrst_literal
   BEGIN_R
   END_R
}

{xrst_end csv_simulate_xam_r}
# BEGIN_R
setwd("WHERE TO SAVE SIM")
#
# Setting seed
library(data.table)
rand_seed = 123456789
set.seed(rand_seed)
#
# option_sim.csv
option_sim <- data.table(
  name = c(
    "absolute_tolerance",
    "float_precision",
    "integrand_step_size",
    "random_depend_sex",
    "std_random_effects_iota",
    "random_seed"
  ),
  value = list(
    1e-5,
    4,
    5,
    "true",
    0.1,
    rand_seed
  )
)
option_sim <- apply(option_sim,2,as.character)
#
# node.csv
node <- data.table(
  node_name = c("n0", "n1", "n2"),
  parent_name = c("","n0","n0")
)
node <- as.data.frame(node)
#
# covariate.csv
covariate <- data.table(
  node_name = c("n0", "n0", "n1", "n1", "n2", "n2"),
  sex = rep(c("female", "male"), 3),
  age = rep(50, 6),
  time = rep(2000, 6),
  omega = rep(0.0, 6),
  haqi = c(1.0, 1.0, 0.5, 0.5, 1.5, 1.5)
)
covariate <- as.data.frame(covariate)
#
# no_effect_rate.csv
no_effect_rate <- data.table(
  rate_name = c("iota"),
  age = c(0.0),
  time = c(1980.0),
  rate_truth = c(0.01)
)
no_effect_rate <- as.data.frame(no_effect_rate)
#
# multiplier_sim.csv
multiplier_sim <- data.table(
  multiplier_id = c(0),
  rate_name = c("iota"),
  covariate_or_sex = c("haqi"),
  multiplier_truth = c(0.5)
)
multiplier_sim <- as.data.frame(multiplier_sim)
#
# simulate.csv
simulate <- data.table(
  simulate_id = c(0, 1, 2),
  integrand_name = rep("Sincidence", 3),
  node_name = c("n0", "n1", "n2"),
  sex = c("female", "male", "female"),
  age_lower = c(0, 10, 20),
  age_upper = c(10, 20, 30),
  time_lower = c(1990, 2000, 2010),
  time_upper = c(2000, 2010, 2020),
  meas_std_cv = rep(0.2, 3),
  meas_std_min = rep(0.01, 3)
)
simulate <- as.data.frame(simulate)
#
# Save files
write.csv(option_sim, "option_sim.csv", row.names=FALSE)
write.csv(node, "node.csv", row.names=FALSE)
write.csv(covariate, "covariate.csv", row.names=FALSE)
write.csv(no_effect_rate, "no_effect_rate.csv", row.names=FALSE)
write.csv(multiplier_sim, "multiplier_sim.csv", row.names=FALSE)
write.csv(simulate, "simulate.csv", row.names=FALSE)
# END_R
