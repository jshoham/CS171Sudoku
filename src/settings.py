# User Changeable Settings

##### Backtracking Settings #####
# fc - Forward Checking
# mrv - Minimum Remaining Values
# dh - Degree Heuristic
# lcv - Least Constraining Value (Note: setting is currently not implemented and has no effect)
# acp - Arc Consistency Pre-processing
# ac - Arc Consistency (Note: setting is currently not implemented and has no effect)
# time_limit - Timeout limit in seconds for backtracking search (Zero designates unlimited time)
fc = True
mrv = True
dh = True
lcv = False
acp = True
ac = False
time_limit = 60

##### Console Display Settings #####
# solver_display_realtime - displays a real-time visualization of backtracking search
# solver_display_verbose - prints out LOTS of information while backtracking, use for debugging
#       Note: This setting overrides solver_display_realtime
solver_display_realtime = False
solver_display_verbose = False

##### Solver Log Output Settings #####
# solver_export_solution - exports solutions in a text file named <filename>'_solution.txt'
# solver_export_raw_data - exports various gathered data in a text file named <filename>'_raw_data.txt'
# solver_export_data_summary - exports a summary of gathered data in a text file named <filename>'_data_summary.txt'
solver_export_solution = True
solver_export_raw_data = True
solver_export_data_summary = True

##### Generator Settings #####
# gen_how_many - Number of puzzles for the generator to attempt to produce
# gen_time_limit - Generator timeout limit in seconds (Zero designates unlimited time)
gen_how_many = 10
gen_time_limit = 5