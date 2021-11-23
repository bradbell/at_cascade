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
#   at_cascade/create_subset_db.py
# '
# list of sed commands that map old file and directory names to new names.
# The characters @s, @d, @n get converted to a space, dollar sign, new line.
# move_seds='
#   s|create_subset_db|create_shift_db|
# '
# list of files that get edited by the extra_seds command
# extra_files='
#   at_cascade/create_shift_db.py
# '
# list of sed commands that are applied to the extra files,
# after the other sed commands in this file.
# The characters @s, @d, @n get converted to a space, dollar sign, new line.
# extra_seds='
#   s|subset|shift|g
# '
# ----------------------------------------------------------------------------
# Put other sed commands below here and without # at start of line
s|create_subset_db|create_shift_db|g
s|c_subset_predict_fit_var|c_shift_predict_fit_var|g
s|c_subset_predict_sample|c_shift_predict_sample|g
s|c_subset_avgint|c_shift_avgint|g
