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
s|absolute_covariates_py|absolute_covariates.py|
s|continue_cascade_py|continue_cascade.py|
s|max_fit_option_py|max_fit_option.py|
s|mulcov_freeze_py|mulcov_freeze.py|
s|no_ode_xam_py|no_ode_xam.py|
s|one_at_function_py|one_at_function.py|
s|prevalence2iota_py|prevalence2iota.py|
s|remission_py|remission.py|
s|split_covariate_py|split_covariate.py|
s|split_covariate_py|split_covariate.py|
