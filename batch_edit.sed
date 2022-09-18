# ----------------------------------------------------------------------------
# None of the lists below can have white space or a dollar sign in an entry.
#
# list of directories that are added to the repository by batch_edit.sh
# new_directories='
# '
# list of files that are deleted by batch_edit.sh
# delete_files='
# '
# List of files that are not edited by the sed commands in this file
# (with the possible exception of the extra_seds commands).
# The files in bin/devel.sh ignore_files are automatically in this list
# (see devel.sh for pattern matching convention).
# ignore_files='
# '
# list of files and or directories that are moved to new names
# move_paths='
# '
# list of sed commands that map old file and directory names to new names.
# The characters @s, @d, @n get converted to a space, dollar sign, new line.
# move_seds='
# '
# list of files that get edited by the extra_seds command
# extra_files='
# '
# list of sed commands that are applied to the extra files,
# after the other sed commands in this file.
# The characters @s, @d, @n get converted to a space, dollar sign, new line.
# extra_seds='
# '
# ----------------------------------------------------------------------------
# Put other sed commands below here and without # at start of line
s/at_cascade@children/at_cascade@Children/g
s/at_cascade@git_repository/at_cascade@Git Repository/g
s/at_cascade@version_2022.9.18/at_cascade@Version 2022.9.18/g
s/glossary@sincidence/glossary@Sincidence/g
s/glossary@relative_covariate/glossary@Relative Covariate/g
s/glossary@input_node_database@rate_table/glossary@input_node_database@Rate Table/g
s/glossary@input_node_database@avgint_table/glossary@input_node_database@avgint Table/g
s/glossary@input_node_database@nslist_table/glossary@input_node_database@nslist Table/g
s/glossary@input_node_database@input_tables/glossary@input_node_database@Input Tables/g
s/glossary@fit_node_database@integrand_table/glossary@fit_node_database@Integrand Table/g
s/glossary@fit_node_database@rate_table/glossary@fit_node_database@Rate Table/g
s/glossary@fit_node_database@random_effects_smoothing/glossary@fit_node_database@Random Effects Smoothing/g
s/glossary@fit_node_database@fixed_effects_smoothings/glossary@fit_node_database@Fixed Effects Smoothings/g
s/glossary@fit_node_database@covariate_table/glossary@fit_node_database@Covariate Table/g
s/glossary@fit_node_database@option_table/glossary@fit_node_database@Option Table/g
s/glossary@fit_node_database@constant_tables/glossary@fit_node_database@Constant Tables/g
s/all_node_db@primary_key/all_node_db@Primary Key/g
s/omega_grid@omega_time_grid_table@time_id/omega_grid@omega_time_grid Table@time_id/g
s/omega_grid@omega_time_grid_table@omega_time_grid_id/omega_grid@omega_time_grid Table@omega_time_grid_id/g
s/omega_grid@omega_time_grid_table@n_omega_time/omega_grid@omega_time_grid Table@n_omega_time/g
s/omega_grid@omega_time_grid_table/omega_grid@omega_time_grid Table/g
s/omega_grid@omega_age_grid_table@age_id/omega_grid@omega_age_grid Table@age_id/g
s/omega_grid@omega_age_grid_table@omega_age_grid_id/omega_grid@omega_age_grid Table@omega_age_grid_id/g
s/omega_grid@omega_age_grid_table@n_omega_age/omega_grid@omega_age_grid Table@n_omega_age/g
s/omega_grid@omega_age_grid_table/omega_grid@omega_age_grid Table/g
s/all_mtall@mtall_index_table@all_mtall_id/all_mtall@mtall_index Table@all_mtall_id/g
s/all_mtall@mtall_index_table@split_reference_id/all_mtall@mtall_index Table@split_reference_id/g
s/all_mtall@mtall_index_table@node_id/all_mtall@mtall_index Table@node_id/g
s/all_mtall@mtall_index_table@mtall_index_id/all_mtall@mtall_index Table@mtall_index_id/g
s/all_mtall@mtall_index_table/all_mtall@mtall_index Table/g
s/all_mtall@all_mtall_table@all_mtall_value/all_mtall@all_mtall Table@all_mtall_value/g
s/all_mtall@all_mtall_table@all_mtall_id/all_mtall@all_mtall Table@all_mtall_id/g
s/all_mtall@all_mtall_table/all_mtall@all_mtall Table/g
s/all_mtspecific@mtspecific_index_table@all_mtspecific_id/all_mtspecific@mtspecific_index Table@all_mtspecific_id/g
s/all_mtspecific@mtspecific_index_table@split_reference_id/all_mtspecific@mtspecific_index Table@split_reference_id/g
s/all_mtspecific@mtspecific_index_table@node_id/all_mtspecific@mtspecific_index Table@node_id/g
s/all_mtspecific@mtspecific_index_table@mtspecific_index_id/all_mtspecific@mtspecific_index Table@mtspecific_index_id/g
s/all_mtspecific@mtspecific_index_table/all_mtspecific@mtspecific_index Table/g
s/all_mtspecific@all_mtspecific_table@all_mtspecific_value/all_mtspecific@all_mtspecific Table@all_mtspecific_value/g
s/all_mtspecific@all_mtspecific_table@all_mtspecific_id/all_mtspecific@all_mtspecific Table@all_mtspecific_id/g
s/all_mtspecific@all_mtspecific_table/all_mtspecific@all_mtspecific Table/g
s/all_option_table@table_format@option_value/all_option_table@Table Format@option_value/g
s/all_option_table@table_format@option_name/all_option_table@Table Format@option_name/g
s/all_option_table@table_format@all_option_id/all_option_table@Table Format@all_option_id/g
s/all_option_table@table_format/all_option_table@Table Format/g
s/wish_list@packaging/wish_list@Packaging/g
s/wish_list@disk_space/wish_list@Disk Space/g
s/absolute_covariates@checking_the_fit/absolute_covariates@Checking The Fit/g
s/absolute_covariates@alpha_smoothing@value_prior/absolute_covariates@Alpha Smoothing@Value Prior/g
s/absolute_covariates@alpha_smoothing/absolute_covariates@Alpha Smoothing/g
s/absolute_covariates@parent_rate_smoothing@value_prior/absolute_covariates@Parent Rate Smoothing@Value Prior/g
s/absolute_covariates@parent_rate_smoothing/absolute_covariates@Parent Rate Smoothing/g
s/absolute_covariates@simulated_data@n_i/absolute_covariates@Simulated Data@n_i/g
s/absolute_covariates@simulated_data@y_i/absolute_covariates@Simulated Data@y_i/g
s/absolute_covariates@simulated_data@rate_true(rate,_a,_t,_n,_c)/absolute_covariates@Simulated Data@rate_true(rate, a, t, n, c)/g
s/absolute_covariates@simulated_data@mtall/absolute_covariates@Simulated Data@mtall/g
s/absolute_covariates@simulated_data/absolute_covariates@Simulated Data/g
s/absolute_covariates@random_effects/absolute_covariates@Random Effects/g
s/absolute_covariates@covariate@alpha/absolute_covariates@Covariate@alpha/g
s/absolute_covariates@covariate@absolute_covariates/absolute_covariates@Covariate@absolute_covariates/g
s/absolute_covariates@covariate/absolute_covariates@Covariate/g
s/absolute_covariates@rates@splitting_covariate/absolute_covariates@Rates@Splitting Covariate/g
s/absolute_covariates@rates/absolute_covariates@Rates/g
s/absolute_covariates@nodes@fit_goal_set/absolute_covariates@Nodes@fit_goal_set/g
s/absolute_covariates@nodes/absolute_covariates@Nodes/g
s/example_bilinear@example_source_code/example_bilinear@Example Source Code/g
s/continue_cascade_xam@checking_the_fit/continue_cascade_xam@Checking The Fit/g
s/continue_cascade_xam@child_rate_smoothing@value_prior/continue_cascade_xam@Child Rate Smoothing@Value Prior/g
s/continue_cascade_xam@child_rate_smoothing/continue_cascade_xam@Child Rate Smoothing/g
s/continue_cascade_xam@parent_rate_smoothing@value_prior/continue_cascade_xam@Parent Rate Smoothing@Value Prior/g
s/continue_cascade_xam@parent_rate_smoothing/continue_cascade_xam@Parent Rate Smoothing/g
s/continue_cascade_xam@simulated_data@n_i/continue_cascade_xam@Simulated Data@n_i/g
s/continue_cascade_xam@simulated_data@y_i/continue_cascade_xam@Simulated Data@y_i/g
s/continue_cascade_xam@simulated_data@rate_true(rate,_a,_t,_n,_c)/continue_cascade_xam@Simulated Data@rate_true(rate, a, t, n, c)/g
s/continue_cascade_xam@simulated_data/continue_cascade_xam@Simulated Data/g
s/continue_cascade_xam@covariate/continue_cascade_xam@Covariate/g
s/continue_cascade_xam@rates/continue_cascade_xam@Rates/g
s/continue_cascade_xam@parallel_processing/continue_cascade_xam@Parallel Processing/g
s/continue_cascade_xam@nodes@fit_goal_set/continue_cascade_xam@Nodes@fit_goal_set/g
s/continue_cascade_xam@nodes/continue_cascade_xam@Nodes/g
s/csv_table@example_source_code/csv_table@Example Source Code/g
s/csv_simulate_xam@node_tree/csv_simulate_xam@Node Tree/g
s/max_fit_option@checking_the_fit/max_fit_option@Checking The Fit/g
s/max_fit_option@child_rate_smoothing@value_prior/max_fit_option@Child Rate Smoothing@Value Prior/g
s/max_fit_option@child_rate_smoothing/max_fit_option@Child Rate Smoothing/g
s/max_fit_option@parent_rate_smoothing@value_prior/max_fit_option@Parent Rate Smoothing@Value Prior/g
s/max_fit_option@parent_rate_smoothing/max_fit_option@Parent Rate Smoothing/g
s/max_fit_option@simulated_data@n_i/max_fit_option@Simulated Data@n_i/g
s/max_fit_option@simulated_data@y_i/max_fit_option@Simulated Data@y_i/g
s/max_fit_option@simulated_data@rate_true(rate,_a,_t,_n,_c)/max_fit_option@Simulated Data@rate_true(rate, a, t, n, c)/g
s/max_fit_option@simulated_data@random_seed/max_fit_option@Simulated Data@Random Seed/g
s/max_fit_option@simulated_data/max_fit_option@Simulated Data/g
s/max_fit_option@covariate/max_fit_option@Covariate/g
s/max_fit_option@rates/max_fit_option@Rates/g
s/max_fit_option@nodes@fit_goal_set/max_fit_option@Nodes@fit_goal_set/g
s/max_fit_option@nodes/max_fit_option@Nodes/g
s/mulcov_freeze@checking_the_fit/mulcov_freeze@Checking The Fit/g
s/mulcov_freeze@alpha_smoothing@value_prior/mulcov_freeze@Alpha Smoothing@Value Prior/g
s/mulcov_freeze@alpha_smoothing/mulcov_freeze@Alpha Smoothing/g
s/mulcov_freeze@child_rate_smoothing@value_prior/mulcov_freeze@Child Rate Smoothing@Value Prior/g
s/mulcov_freeze@child_rate_smoothing/mulcov_freeze@Child Rate Smoothing/g
s/mulcov_freeze@parent_rate_smoothing@dage_prior/mulcov_freeze@Parent Rate Smoothing@dage Prior/g
s/mulcov_freeze@parent_rate_smoothing@value_prior/mulcov_freeze@Parent Rate Smoothing@Value Prior/g
s/mulcov_freeze@parent_rate_smoothing/mulcov_freeze@Parent Rate Smoothing/g
s/mulcov_freeze@simulated_data@i_i/mulcov_freeze@Simulated Data@I_i/g
s/mulcov_freeze@simulated_data@a_i/mulcov_freeze@Simulated Data@a_i/g
s/mulcov_freeze@simulated_data@n_i/mulcov_freeze@Simulated Data@n_i/g
s/mulcov_freeze@simulated_data@y_i/mulcov_freeze@Simulated Data@y_i/g
s/mulcov_freeze@simulated_data@rate_true(rate,_a,_t,_n,_c)/mulcov_freeze@Simulated Data@rate_true(rate, a, t, n, c)/g
s/mulcov_freeze@simulated_data@random_seed/mulcov_freeze@Simulated Data@Random Seed/g
s/mulcov_freeze@simulated_data/mulcov_freeze@Simulated Data/g
s/mulcov_freeze@random_effects@s_n/mulcov_freeze@Random Effects@s_n/g
s/mulcov_freeze@random_effects/mulcov_freeze@Random Effects/g
s/mulcov_freeze@covariate@freeze/mulcov_freeze@Covariate@Freeze/g
s/mulcov_freeze@covariate@alpha/mulcov_freeze@Covariate@alpha/g
s/mulcov_freeze@covariate@r_n/mulcov_freeze@Covariate@r_n/g
s/mulcov_freeze@covariate/mulcov_freeze@Covariate/g
s/mulcov_freeze@rates/mulcov_freeze@Rates/g
s/mulcov_freeze@nodes@fit_goal_set/mulcov_freeze@Nodes@fit_goal_set/g
s/mulcov_freeze@nodes/mulcov_freeze@Nodes/g
s/no_ode_xam@checking_the_fit/no_ode_xam@Checking The Fit/g
s/no_ode_xam@alpha_smoothing@value_prior/no_ode_xam@Alpha Smoothing@Value Prior/g
s/no_ode_xam@alpha_smoothing/no_ode_xam@Alpha Smoothing/g
s/no_ode_xam@child_rate_smoothing@value_prior/no_ode_xam@Child Rate Smoothing@Value Prior/g
s/no_ode_xam@child_rate_smoothing/no_ode_xam@Child Rate Smoothing/g
s/no_ode_xam@parent_rate_smoothing@dage_prior/no_ode_xam@Parent Rate Smoothing@dage Prior/g
s/no_ode_xam@parent_rate_smoothing@value_prior/no_ode_xam@Parent Rate Smoothing@Value Prior/g
s/no_ode_xam@parent_rate_smoothing@iota_and_chi/no_ode_xam@Parent Rate Smoothing@iota and chi/g
s/no_ode_xam@parent_rate_smoothing/no_ode_xam@Parent Rate Smoothing/g
s/no_ode_xam@omega_constraints/no_ode_xam@Omega Constraints/g
s/no_ode_xam@simulated_data@i_i/no_ode_xam@Simulated Data@I_i/g
s/no_ode_xam@simulated_data@a_i/no_ode_xam@Simulated Data@a_i/g
s/no_ode_xam@simulated_data@n_i/no_ode_xam@Simulated Data@n_i/g
s/no_ode_xam@simulated_data@y_i/no_ode_xam@Simulated Data@y_i/g
s/no_ode_xam@simulated_data@rate_true(rate,_a,_t,_n,_c)/no_ode_xam@Simulated Data@rate_true(rate, a, t, n, c)/g
s/no_ode_xam@simulated_data@random_seed/no_ode_xam@Simulated Data@Random Seed/g
s/no_ode_xam@simulated_data/no_ode_xam@Simulated Data/g
s/no_ode_xam@random_effects@r_n/no_ode_xam@Random Effects@R_n/g
s/no_ode_xam@random_effects/no_ode_xam@Random Effects/g
s/no_ode_xam@covariate@alpha/no_ode_xam@Covariate@alpha/g
s/no_ode_xam@covariate@i_n/no_ode_xam@Covariate@I_n/g
s/no_ode_xam@covariate/no_ode_xam@Covariate/g
s/no_ode_xam@rates/no_ode_xam@Rates/g
s/no_ode_xam@nodes@fit_goal_set/no_ode_xam@Nodes@fit_goal_set/g
s/no_ode_xam@nodes/no_ode_xam@Nodes/g
s/one_at_function@checking_the_fit/one_at_function@Checking The Fit/g
s/one_at_function@alpha_smoothing@value_prior/one_at_function@Alpha Smoothing@Value Prior/g
s/one_at_function@alpha_smoothing/one_at_function@Alpha Smoothing/g
s/one_at_function@child_rate_smoothing@value_prior/one_at_function@Child Rate Smoothing@Value Prior/g
s/one_at_function@child_rate_smoothing/one_at_function@Child Rate Smoothing/g
s/one_at_function@parent_rate_smoothing@dage_prior/one_at_function@Parent Rate Smoothing@dage Prior/g
s/one_at_function@parent_rate_smoothing@value_prior/one_at_function@Parent Rate Smoothing@Value Prior/g
s/one_at_function@parent_rate_smoothing/one_at_function@Parent Rate Smoothing/g
s/one_at_function@simulated_data@i_i/one_at_function@Simulated Data@I_i/g
s/one_at_function@simulated_data@a_i/one_at_function@Simulated Data@a_i/g
s/one_at_function@simulated_data@n_i/one_at_function@Simulated Data@n_i/g
s/one_at_function@simulated_data@y_i/one_at_function@Simulated Data@y_i/g
s/one_at_function@simulated_data@rate_true(rate,_a,_t,_n,_c)/one_at_function@Simulated Data@rate_true(rate, a, t, n, c)/g
s/one_at_function@simulated_data@random_seed/one_at_function@Simulated Data@Random Seed/g
s/one_at_function@simulated_data/one_at_function@Simulated Data/g
s/one_at_function@random_effects@s_n/one_at_function@Random Effects@s_n/g
s/one_at_function@random_effects/one_at_function@Random Effects/g
s/one_at_function@covariate@alpha/one_at_function@Covariate@alpha/g
s/one_at_function@covariate@r_n/one_at_function@Covariate@r_n/g
s/one_at_function@covariate/one_at_function@Covariate/g
s/one_at_function@rates/one_at_function@Rates/g
s/one_at_function@nodes@fit_goal_set/one_at_function@Nodes@fit_goal_set/g
s/one_at_function@nodes/one_at_function@Nodes/g
s/prevalence2iota@checking_the_fit/prevalence2iota@Checking The Fit/g
s/prevalence2iota@gamma_smoothing/prevalence2iota@Gamma Smoothing/g
s/prevalence2iota@alpha_smoothing@value_prior/prevalence2iota@Alpha Smoothing@Value Prior/g
s/prevalence2iota@alpha_smoothing/prevalence2iota@Alpha Smoothing/g
s/prevalence2iota@child_rate_smoothing@value_prior/prevalence2iota@Child Rate Smoothing@Value Prior/g
s/prevalence2iota@child_rate_smoothing/prevalence2iota@Child Rate Smoothing/g
s/prevalence2iota@parent_rate_smoothing@dage_prior/prevalence2iota@Parent Rate Smoothing@dage Prior/g
s/prevalence2iota@parent_rate_smoothing@value_prior/prevalence2iota@Parent Rate Smoothing@Value Prior/g
s/prevalence2iota@parent_rate_smoothing@iota/prevalence2iota@Parent Rate Smoothing@iota/g
s/prevalence2iota@parent_rate_smoothing/prevalence2iota@Parent Rate Smoothing/g
s/prevalence2iota@omega_constraints/prevalence2iota@Omega Constraints/g
s/prevalence2iota@simulated_data@i_i/prevalence2iota@Simulated Data@I_i/g
s/prevalence2iota@simulated_data@a_i/prevalence2iota@Simulated Data@a_i/g
s/prevalence2iota@simulated_data@n_i/prevalence2iota@Simulated Data@n_i/g
s/prevalence2iota@simulated_data@y_i/prevalence2iota@Simulated Data@y_i/g
s/prevalence2iota@simulated_data@rate_true(rate,_a,_t,_n,_c)/prevalence2iota@Simulated Data@rate_true(rate, a, t, n, c)/g
s/prevalence2iota@simulated_data@random_seed/prevalence2iota@Simulated Data@Random Seed/g
s/prevalence2iota@simulated_data/prevalence2iota@Simulated Data/g
s/prevalence2iota@random_effects@s_n/prevalence2iota@Random Effects@s_n/g
s/prevalence2iota@random_effects/prevalence2iota@Random Effects/g
s/prevalence2iota@covariate@gamma/prevalence2iota@Covariate@gamma/g
s/prevalence2iota@covariate@alpha/prevalence2iota@Covariate@alpha/g
s/prevalence2iota@covariate@r_n/prevalence2iota@Covariate@r_n/g
s/prevalence2iota@covariate/prevalence2iota@Covariate/g
s/prevalence2iota@rates/prevalence2iota@Rates/g
s/prevalence2iota@nodes@fit_goal_set/prevalence2iota@Nodes@fit_goal_set/g
s/prevalence2iota@nodes/prevalence2iota@Nodes/g
s/remission@checking_the_fit/remission@Checking The Fit/g
s/remission@child_rate_smoothing@value_prior/remission@Child Rate Smoothing@Value Prior/g
s/remission@child_rate_smoothing/remission@Child Rate Smoothing/g
s/remission@parent_rate_smoothing@parent_rate_priors/remission@Parent Rate Smoothing@Parent Rate Priors/g
s/remission@parent_rate_smoothing@iota/remission@Parent Rate Smoothing@iota/g
s/remission@parent_rate_smoothing/remission@Parent Rate Smoothing/g
s/remission@omega_constraints/remission@Omega Constraints/g
s/remission@simulated_data@a_i/remission@Simulated Data@a_i/g
s/remission@simulated_data@n_i/remission@Simulated Data@n_i/g
s/remission@simulated_data@y_i/remission@Simulated Data@y_i/g
s/remission@simulated_data@rate_true(rate,_a,_t,_n,_c)/remission@Simulated Data@rate_true(rate, a, t, n, c)/g
s/remission@simulated_data@random_seed/remission@Simulated Data@Random Seed/g
s/remission@simulated_data/remission@Simulated Data/g
s/remission@random_effects@s_n/remission@Random Effects@s_n/g
s/remission@random_effects/remission@Random Effects/g
s/remission@covariate/remission@Covariate/g
s/remission@rates/remission@Rates/g
s/remission@nodes@fit_goal_set/remission@Nodes@fit_goal_set/g
s/remission@nodes/remission@Nodes/g
s/split_covariate@checking_the_fit/split_covariate@Checking The Fit/g
s/split_covariate@alpha_smoothing@value_prior/split_covariate@Alpha Smoothing@Value Prior/g
s/split_covariate@alpha_smoothing/split_covariate@Alpha Smoothing/g
s/split_covariate@parent_rate_smoothing@value_prior/split_covariate@Parent Rate Smoothing@Value Prior/g
s/split_covariate@parent_rate_smoothing/split_covariate@Parent Rate Smoothing/g
s/split_covariate@simulated_data@cases_simulated/split_covariate@Simulated Data@Cases Simulated/g
s/split_covariate@simulated_data@y_i/split_covariate@Simulated Data@y_i/g
s/split_covariate@simulated_data@rate_true(rate,_a,_t,_n,_c)/split_covariate@Simulated Data@rate_true(rate, a, t, n, c)/g
s/split_covariate@simulated_data@mtall/split_covariate@Simulated Data@mtall/g
s/split_covariate@simulated_data/split_covariate@Simulated Data/g
s/split_covariate@random_effects/split_covariate@Random Effects/g
s/split_covariate@covariate@alpha/split_covariate@Covariate@alpha/g
s/split_covariate@covariate/split_covariate@Covariate/g
s/split_covariate@splitting_covariate/split_covariate@Splitting Covariate/g
s/split_covariate@rates/split_covariate@Rates/g
s/split_covariate@nodes@fit_goal_set/split_covariate@Nodes@fit_goal_set/g
s/split_covariate@nodes/split_covariate@Nodes/g
s/add_log_entry@log_table/add_log_entry@Log Table/g
s/add_log_entry@purpose/add_log_entry@Purpose/g
s/add_log_entry@syntax/add_log_entry@Syntax/g
s/avgint_parent_grid@avgint_table@rectangular_grid/avgint_parent_grid@avgint Table@Rectangular Grid/g
s/avgint_parent_grid@avgint_table@c_split_reference_id/avgint_parent_grid@avgint Table@c_split_reference_id/g
s/avgint_parent_grid@avgint_table@c_time_id/avgint_parent_grid@avgint Table@c_time_id/g
s/avgint_parent_grid@avgint_table@c_age_id/avgint_parent_grid@avgint Table@c_age_id/g
s/avgint_parent_grid@avgint_table/avgint_parent_grid@avgint Table/g
s/avgint_parent_grid@purpose/avgint_parent_grid@Purpose/g
s/avgint_parent_grid@syntax/avgint_parent_grid@Syntax/g
s/bilinear@spline_dict@rectangular_grid/bilinear@spline_dict@Rectangular Grid/g
s/bilinear@syntax/bilinear@Syntax/g
s/cascade_root_node@output_dismod.db@log/cascade_root_node@Output dismod.db@log/g
s/cascade_root_node@output_dismod.db@sample/cascade_root_node@Output dismod.db@sample/g
s/cascade_root_node@output_dismod.db@fit_var/cascade_root_node@Output dismod.db@fit_var/g
s/cascade_root_node@output_dismod.db/cascade_root_node@Output dismod.db/g
s/cascade_root_node@syntax/cascade_root_node@Syntax/g
s/check_cascade_node@fit_node_database@avgint_table/check_cascade_node@fit_node_database@avgint Table/g
s/check_cascade_node@syntax/check_cascade_node@Syntax/g
s/check_log@purpose/check_log@Purpose/g
s/check_log@syntax/check_log@Syntax/g
s/clear_shared@purpose/clear_shared@Purpose/g
s/clear_shared@syntax/clear_shared@Syntax/g
s/continue_cascade@purpose/continue_cascade@Purpose/g
s/continue_cascade@syntax/continue_cascade@Syntax/g
s/create_all_node_db@mulcov_freeze_table@fit_node_id,_fit_node_name/create_all_node_db@mulcov_freeze_table@fit_node_id, fit_node_name/g
s/create_all_node_db@root_node_database@list/create_all_node_db@root_node_database@List/g
s/create_all_node_db@syntax/create_all_node_db@Syntax/g
s/create_job_table@purpose/create_job_table@Purpose/g
s/create_job_table@syntax/create_job_table@Syntax/g
s/create_shift_db@shift_databases@dage_and_dtime_priors/create_shift_db@shift_databases@dage and dtime Priors/g
s/create_shift_db@shift_databases@value_priors/create_shift_db@shift_databases@Value Priors/g
s/create_shift_db@shift_databases@fit_node/create_shift_db@shift_databases@Fit Node/g
s/create_shift_db@shift_databases@child_node/create_shift_db@shift_databases@Child Node/g
s/create_shift_db@fit_node_database@c_shift_predict_fit_var_table/create_shift_db@fit_node_database@c_shift_predict_fit_var Table/g
s/create_shift_db@fit_node_database@c_shift_predict_sample_table/create_shift_db@fit_node_database@c_shift_predict_sample Table/g
s/create_shift_db@fit_node_database@c_shift_avgint_table/create_shift_db@fit_node_database@c_shift_avgint Table/g
s/create_shift_db@fit_node_database@sample_table/create_shift_db@fit_node_database@sample Table/g
s/create_shift_db@syntax/create_shift_db@Syntax/g
s/csv_interface@notation@distributions/csv_interface@Notation@Distributions/g
s/csv_interface@notation@index_column/csv_interface@Notation@Index Column/g
s/csv_interface@notation@data_type/csv_interface@Notation@Data Type/g
s/csv_interface@notation@covariates/csv_interface@Notation@Covariates/g
s/csv_interface@notation@rectangular_grid/csv_interface@Notation@Rectangular Grid/g
s/csv_interface@notation@demographer/csv_interface@Notation@Demographer/g
s/csv_interface@notation/csv_interface@Notation/g
s/csv_interface@arguments@command/csv_interface@Arguments@command/g
s/csv_interface@arguments@csv_dir/csv_interface@Arguments@csv_dir/g
s/csv_interface@arguments/csv_interface@Arguments/g
s/csv_interface@syntax/csv_interface@Syntax/g
s/csv_interface@under_construction/csv_interface@Under Construction/g
s/csv_fit@output_files@multiplier_fit.csv@std_error/csv_fit@Output Files@multiplier_fit.csv@std_error/g
s/csv_fit@output_files@multiplier_fit.csv@estimate/csv_fit@Output Files@multiplier_fit.csv@estimate/g
s/csv_fit@output_files@multiplier_fit.csv@multiplier_id/csv_fit@Output Files@multiplier_fit.csv@multiplier_id/g
s/csv_fit@output_files@multiplier_fit.csv/csv_fit@Output Files@multiplier_fit.csv/g
s/csv_fit@output_files@rate_fit.csv@std_error/csv_fit@Output Files@rate_fit.csv@std_error/g
s/csv_fit@output_files@rate_fit.csv@estimate/csv_fit@Output Files@rate_fit.csv@estimate/g
s/csv_fit@output_files@rate_fit.csv@rate_sim_id/csv_fit@Output Files@rate_fit.csv@rate_sim_id/g
s/csv_fit@output_files@rate_fit.csv/csv_fit@Output Files@rate_fit.csv/g
s/csv_fit@output_files@data_fit.csv@residual/csv_fit@Output Files@data_fit.csv@residual/g
s/csv_fit@output_files@data_fit.csv@estimate/csv_fit@Output Files@data_fit.csv@estimate/g
s/csv_fit@output_files@data_fit.csv@simulate_id/csv_fit@Output Files@data_fit.csv@simulate_id/g
s/csv_fit@output_files@data_fit.csv/csv_fit@Output Files@data_fit.csv/g
s/csv_fit@output_files/csv_fit@Output Files/g
s/csv_fit@input_files@rate_prior.csv@upper/csv_fit@Input Files@rate_prior.csv@upper/g
s/csv_fit@input_files@rate_prior.csv@lower/csv_fit@Input Files@rate_prior.csv@lower/g
s/csv_fit@input_files@rate_prior.csv@prior_std/csv_fit@Input Files@rate_prior.csv@prior_std/g
s/csv_fit@input_files@rate_prior.csv@prior_mean/csv_fit@Input Files@rate_prior.csv@prior_mean/g
s/csv_fit@input_files@rate_prior.csv@rate_sim_id/csv_fit@Input Files@rate_prior.csv@rate_sim_id/g
s/csv_fit@input_files@rate_prior.csv/csv_fit@Input Files@rate_prior.csv/g
s/csv_fit@input_files@multiplier_prior.csv@upper/csv_fit@Input Files@multiplier_prior.csv@upper/g
s/csv_fit@input_files@multiplier_prior.csv@lower/csv_fit@Input Files@multiplier_prior.csv@lower/g
s/csv_fit@input_files@multiplier_prior.csv@prior_std/csv_fit@Input Files@multiplier_prior.csv@prior_std/g
s/csv_fit@input_files@multiplier_prior.csv@prior_mean/csv_fit@Input Files@multiplier_prior.csv@prior_mean/g
s/csv_fit@input_files@multiplier_prior.csv@multiplier_id/csv_fit@Input Files@multiplier_prior.csv@multiplier_id/g
s/csv_fit@input_files@multiplier_prior.csv/csv_fit@Input Files@multiplier_prior.csv/g
s/csv_fit@input_files@data_subset.csv@simulate_id/csv_fit@Input Files@data_subset.csv@simulate_id/g
s/csv_fit@input_files@data_subset.csv/csv_fit@Input Files@data_subset.csv/g
s/csv_fit@input_files/csv_fit@Input Files/g
s/csv_predict@output_files@predict.csv@integrand_truth/csv_predict@Output Files@predict.csv@integrand_truth/g
s/csv_predict@output_files@predict.csv@integrand_predict/csv_predict@Output Files@predict.csv@integrand_predict/g
s/csv_predict@output_files@predict.csv@case_id/csv_predict@Output Files@predict.csv@case_id/g
s/csv_predict@output_files@predict.csv/csv_predict@Output Files@predict.csv/g
s/csv_predict@output_files/csv_predict@Output Files/g
s/csv_predict@input_files@case.csv@time_upper/csv_predict@Input Files@case.csv@time_upper/g
s/csv_predict@input_files@case.csv@time_lower/csv_predict@Input Files@case.csv@time_lower/g
s/csv_predict@input_files@case.csv@age_upper/csv_predict@Input Files@case.csv@age_upper/g
s/csv_predict@input_files@case.csv@age_lower/csv_predict@Input Files@case.csv@age_lower/g
s/csv_predict@input_files@case.csv@sex/csv_predict@Input Files@case.csv@sex/g
s/csv_predict@input_files@case.csv@node_name/csv_predict@Input Files@case.csv@node_name/g
s/csv_predict@input_files@case.csv@integrand_name/csv_predict@Input Files@case.csv@integrand_name/g
s/csv_predict@input_files@case.csv@case_id/csv_predict@Input Files@case.csv@case_id/g
s/csv_predict@input_files@case.csv/csv_predict@Input Files@case.csv/g
s/csv_predict@input_files/csv_predict@Input Files/g
s/empty_avgint_table@log_table/empty_avgint_table@log Table/g
s/empty_avgint_table@avgint_table/empty_avgint_table@avgint Table/g
s/empty_avgint_table@covariate_table/empty_avgint_table@covariate Table/g
s/empty_avgint_table@syntax/empty_avgint_table@Syntax/g
s/get_cov_info@syntax/get_cov_info@Syntax/g
s/get_cov_reference@all_node_database@all_option_table/get_cov_reference@all_node_database@all_option Table/g
s/get_cov_reference@fit_node_database@data_table/get_cov_reference@fit_node_database@data Table/g
s/get_cov_reference@fit_node_database@option_table/get_cov_reference@fit_node_database@option Table/g
s/get_cov_reference@syntax/get_cov_reference@Syntax/g
s/get_database_dir@syntax/get_database_dir@Syntax/g
s/get_fit_children@syntax/get_fit_children@Syntax/g
s/get_fit_integrand@syntax/get_fit_integrand@Syntax/g
s/get_parent_node@syntax/get_parent_node@Syntax/g
s/get_var_id@other_arguments/get_var_id@Other Arguments/g
s/get_var_id@syntax/get_var_id@Syntax/g
s/move_table@log_table/move_table@Log Table/g
s/move_table@purpose/move_table@Purpose/g
s/move_table@syntax/move_table@Syntax/g
s/no_ode_fit@syntax/no_ode_fit@Syntax/g
s/omega_constraint@fit_node_database@other_tables/omega_constraint@fit_node_database@Other Tables/g
s/omega_constraint@fit_node_database@nslist_pair_table/omega_constraint@fit_node_database@nslist_pair Table/g
s/omega_constraint@fit_node_database@nslist_table/omega_constraint@fit_node_database@nslist Table/g
s/omega_constraint@fit_node_database@smooth_grid_table/omega_constraint@fit_node_database@smooth_grid Table/g
s/omega_constraint@fit_node_database@smooth_table/omega_constraint@fit_node_database@smooth Table/g
s/omega_constraint@all_node_database@use/omega_constraint@all_node_database@Use/g
s/omega_constraint@syntax/omega_constraint@Syntax/g
s/read_csv_table@example/read_csv_table@Example/g
s/read_csv_table@syntax/read_csv_table@Syntax/g
s/run_one_job@fit_node_database@upon_input/run_one_job@fit_node_database@Upon Input/g
s/run_one_job@default_value/run_one_job@Default Value/g
s/run_one_job@syntax/run_one_job@Syntax/g
s/run_parallel@default_value/run_parallel@Default Value/g
s/run_parallel@syntax/run_parallel@Syntax/g
s/table_name2id@syntax/table_name2id@Syntax/g
s/write_csv_table@example/write_csv_table@Example/g
s/write_csv_table@syntax/write_csv_table@Syntax/g
s/csv_simulate@output_files@data_sim.csv@covariate_name/csv_simulate@Output Files@data_sim.csv@covariate_name/g
s/csv_simulate@output_files@data_sim.csv@meas_std/csv_simulate@Output Files@data_sim.csv@meas_std/g
s/csv_simulate@output_files@data_sim.csv@meas_value/csv_simulate@Output Files@data_sim.csv@meas_value/g
s/csv_simulate@output_files@data_sim.csv@meas_mean/csv_simulate@Output Files@data_sim.csv@meas_mean/g
s/csv_simulate@output_files@data_sim.csv@simulate_id/csv_simulate@Output Files@data_sim.csv@simulate_id/g
s/csv_simulate@output_files@data_sim.csv/csv_simulate@Output Files@data_sim.csv/g
s/csv_simulate@output_files@random_effect.csv@discussion/csv_simulate@Output Files@random_effect.csv@Discussion/g
s/csv_simulate@output_files@random_effect.csv@random_effect/csv_simulate@Output Files@random_effect.csv@random_effect/g
s/csv_simulate@output_files@random_effect.csv@rate_name/csv_simulate@Output Files@random_effect.csv@rate_name/g
s/csv_simulate@output_files@random_effect.csv@sex/csv_simulate@Output Files@random_effect.csv@sex/g
s/csv_simulate@output_files@random_effect.csv@node_name/csv_simulate@Output Files@random_effect.csv@node_name/g
s/csv_simulate@output_files@random_effect.csv/csv_simulate@Output Files@random_effect.csv/g
s/csv_simulate@output_files/csv_simulate@Output Files/g
s/csv_simulate@input_files@simulate.csv@percent_cv/csv_simulate@Input Files@simulate.csv@percent_cv/g
s/csv_simulate@input_files@simulate.csv@time_upper/csv_simulate@Input Files@simulate.csv@time_upper/g
s/csv_simulate@input_files@simulate.csv@time_lower/csv_simulate@Input Files@simulate.csv@time_lower/g
s/csv_simulate@input_files@simulate.csv@age_upper/csv_simulate@Input Files@simulate.csv@age_upper/g
s/csv_simulate@input_files@simulate.csv@age_lower/csv_simulate@Input Files@simulate.csv@age_lower/g
s/csv_simulate@input_files@simulate.csv@sex/csv_simulate@Input Files@simulate.csv@sex/g
s/csv_simulate@input_files@simulate.csv@node_name/csv_simulate@Input Files@simulate.csv@node_name/g
s/csv_simulate@input_files@simulate.csv@integrand_name/csv_simulate@Input Files@simulate.csv@integrand_name/g
s/csv_simulate@input_files@simulate.csv@simulate_id/csv_simulate@Input Files@simulate.csv@simulate_id/g
s/csv_simulate@input_files@simulate.csv/csv_simulate@Input Files@simulate.csv/g
s/csv_simulate@input_files@multiplier_sim.csv@multiplier_truth/csv_simulate@Input Files@multiplier_sim.csv@multiplier_truth/g
s/csv_simulate@input_files@multiplier_sim.csv@covariate_or_sex/csv_simulate@Input Files@multiplier_sim.csv@covariate_or_sex/g
s/csv_simulate@input_files@multiplier_sim.csv@rate_name/csv_simulate@Input Files@multiplier_sim.csv@rate_name/g
s/csv_simulate@input_files@multiplier_sim.csv@multiplier_id/csv_simulate@Input Files@multiplier_sim.csv@multiplier_id/g
s/csv_simulate@input_files@multiplier_sim.csv/csv_simulate@Input Files@multiplier_sim.csv/g
s/csv_simulate@input_files@no_effect_rate.csv@rate_truth/csv_simulate@Input Files@no_effect_rate.csv@rate_truth/g
s/csv_simulate@input_files@no_effect_rate.csv@time/csv_simulate@Input Files@no_effect_rate.csv@time/g
s/csv_simulate@input_files@no_effect_rate.csv@age/csv_simulate@Input Files@no_effect_rate.csv@age/g
s/csv_simulate@input_files@no_effect_rate.csv@rate_name/csv_simulate@Input Files@no_effect_rate.csv@rate_name/g
s/csv_simulate@input_files@no_effect_rate.csv/csv_simulate@Input Files@no_effect_rate.csv/g
s/csv_simulate@input_files@covariate.csv@covariate_name/csv_simulate@Input Files@covariate.csv@covariate_name/g
s/csv_simulate@input_files@covariate.csv@omega/csv_simulate@Input Files@covariate.csv@omega/g
s/csv_simulate@input_files@covariate.csv@time/csv_simulate@Input Files@covariate.csv@time/g
s/csv_simulate@input_files@covariate.csv@age/csv_simulate@Input Files@covariate.csv@age/g
s/csv_simulate@input_files@covariate.csv@sex/csv_simulate@Input Files@covariate.csv@sex/g
s/csv_simulate@input_files@covariate.csv@node_name/csv_simulate@Input Files@covariate.csv@node_name/g
s/csv_simulate@input_files@covariate.csv/csv_simulate@Input Files@covariate.csv/g
s/csv_simulate@input_files@node.csv@parent_name/csv_simulate@Input Files@node.csv@parent_name/g
s/csv_simulate@input_files@node.csv@node_name/csv_simulate@Input Files@node.csv@node_name/g
s/csv_simulate@input_files@node.csv/csv_simulate@Input Files@node.csv/g
s/csv_simulate@input_files@option.csv@std_random_effects/csv_simulate@Input Files@option.csv@std_random_effects/g
s/csv_simulate@input_files@option.csv@random_seed/csv_simulate@Input Files@option.csv@random_seed/g
s/csv_simulate@input_files@option.csv@integrand_step_size/csv_simulate@Input Files@option.csv@integrand_step_size/g
s/csv_simulate@input_files@option.csv@float_precision/csv_simulate@Input Files@option.csv@float_precision/g
s/csv_simulate@input_files@option.csv@absolute_tolerance/csv_simulate@Input Files@option.csv@absolute_tolerance/g
s/csv_simulate@input_files@option.csv/csv_simulate@Input Files@option.csv/g
s/csv_simulate@input_files/csv_simulate@Input Files/g
s/csv_simulate@example/csv_simulate@Example/g
