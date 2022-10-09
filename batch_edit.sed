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
#  at_cascade/read_csv_table.py
# '
# list of sed commands that map old file and directory names to new names.
# The characters @s, @d, @n get converted to a space, dollar sign, new line.
# move_seds='
#  s|read_csv_table|csv/read_table|
# '
# list of files that get edited by the extra_seds command
# extra_files='
#  example/csv/simulate_xam.py
#  test/csv_simulate.py
# '
# list of sed commands that are applied to the extra files,
# after the other sed commands in this file.
# The characters @s, @d, @n get converted to a space, dollar sign, new line.
# extra_seds='
#  /import@sat_cascade.csv/d
# '
# ----------------------------------------------------------------------------
# Put other sed commands below here and without # at start of line
s|at_cascade.read_csv_table|at_cascade.csv.read_table|g
s|read_csv_table|csv_read_table|g
