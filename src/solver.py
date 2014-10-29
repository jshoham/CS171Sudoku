__author__ = 'jshoham'

# Solver
# The solver will expect one filename argument.
# The first line of that file will be the parameters N, p, and q, separated by spaces.
# The N file lines that follow will give the N puzzle lines, one puzzle line on each 
# file line. Tokens will be represented as above. Blank cells will be represented as a
# zero. Tokens and zeroes will be separated by spaces. For example, the input file for 
# a 6x6 puzzle with boxes that are 2 rows by 3 columns might look like:
# 6 2 3
# 5 0 0 3 0 0
# 0 0 2 0 0 4
# 4 3 0 0 5 0
# 0 0 1 2 0 0
# 1 0 0 0 4 0
# 0 2 0 0 1 5
#
# Added support for a common representation of 9x9 puzzles, where each puzzle is represented
# on a single line as a string of 81 characters. Each cell is represented by the digits 1-9
# and blank cells are represented by '.'. For example, an input file containing three puzzles
# might look like:
# 52...6.........7.13...........4..8..6......5...........418.........3..2...87.....
# 4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......
# 48.3............71.2.......7.5....6....2..8.............1.76...3.....4......5....
#


import sys
import os
import time
import re
from random import sample
import grid
import rw
import verifier
import settings


def puzzle_list(f_str):
    """Returns a list of strings with each element containing an individual puzzle."""
    matches = re.findall(r'^([\d\.]+)$', f_str, re.MULTILINE)
    if matches:  # inline representation
        return matches
    else:  # default representation
        p_list = []
        f_str_lines = f_str.splitlines()
        p_index = 0

        while p_index < len(f_str_lines):
            N, p, q = [int(x) for x in f_str_lines[p_index].split()]
            puzzle_lines = [f_str_lines[p_index]]

            for row in xrange(N):
                puzzle_lines.append(f_str_lines[p_index + row + 1])

            p_list.append('\n'.join(puzzle_lines))
            p_index += N + 1

        return p_list


def create_board(board_str):
    """Creates a single puzzle based on the given string representation."""
    matches = re.match(r'^([\d\.]+)$', board_str, re.MULTILINE)
    if matches:  # inline representation (81 chars on a line (9x9 puzzles only)
        N, p, q = 9, 3, 3
        board = grid.Grid(N, p, q)
        for row in xrange(N):
            for col in xrange(N):
                cell_value = board_str[row * 9 + col]
                cell_value = 0 if cell_value == '.' else int(cell_value)
                board.assign(row, col, cell_value)
        return board

    else:  # default representation (first line 'N p q' followed by N lines)
        row_list = board_str.splitlines()
        N, p, q = [int(x) for x in row_list[0].split()]
        board = grid.Grid(N, p, q)
        for row in xrange(N):
            col_list = [int(x) for x in row_list[row + 1].split()]
            for col in xrange(N):
                board.assign(row, col, col_list[col])
        return board


def choose_empty_cell(board):
    """Returns the next empty cell as a tuple (row, col), or None if there are no more empty cells."""
    if settings.mrv:
        empty_cells = board.empty_cells()
        return choose_cell_mrv(board, empty_cells)
    elif settings.dh:
        empty_cells = board.empty_cells()
        return choose_cell_dh(board, empty_cells)
    else:
        for row in xrange(board.N):
            for col in xrange(board.N):
                if board.cell_empty(row, col):
                    return row, col
        return None


def choose_cell_random(cell_list):
    """Chooses a random cell from the given list. Useful for testing and debugging."""
    if not cell_list:
        return None
    return sample(cell_list, 1)[0]


def choose_cell_mrv(board, cell_list):
    """Chooses the next empty cell which has the fewest possible remaining values.

    Ties are broken arbitrarily, or by DH if it is turned on.
    """
    if not cell_list:
        return None
    mrv_cell = cell_list[0]
    mrv_v = len(board.possible_values(*mrv_cell))
    for cell in cell_list[1:]:  # Start with the 2nd cell
        cell_v = len(board.possible_values(*cell))
        if cell_v < mrv_v:
            mrv_cell = cell
            mrv_v = cell_v
        elif cell_v == mrv_v and settings.dh:
            mrv_cell = choose_cell_dh(board, [mrv_cell, cell])
    return mrv_cell


def choose_cell_dh(board, cell_list):
    """Chooses the cell from cell_list which has the highest degree to other unassigned cells.

    The chosen cell will have the greatest number of peers which are unassigned and have at least
    2 possible values. Cells which have only 1 possible value are considered solved by the degree
    heuristic, even if they haven't been explicitly assigned by backtrack.
    """
    if not cell_list:
        return None
    dh_cell = cell_list[0]
    dh_degree = board.degree_heuristic(*dh_cell)
    for cell in cell_list[1:]:  # Start with the 2nd cell
        cell_degree = board.degree_heuristic(*cell)
        if cell_degree > dh_degree:
            dh_cell = cell
            dh_degree = cell_degree

    return dh_cell


def order_possible_values(board, x, y):
    """Returns the ordered domain of a given cell at (x, y)."""
    if settings.lcv:
        return order_values_lcv(board, x, y)
    else:
        return sorted(board.possible_values(x, y))


# todo implement and test
def order_values_lcv(board, x, y):
    """Order domain values based on the least constraining value.
    The least constraining value deletes the fewest values from peer domains."""

    # lcv takes a value argument and computes its 'lcv' value, ie, how many values it would delete from peers
    lcv = lambda value: len([peer for peer in board.peers(x, y)
                             if board.cell_empty(*peer) and
                             value in board.possible_values(*peer)])
    return sorted(board.possible_values(x, y), key=lcv)


# Alternate implementation. This one doesn't use a list comprehension for lcv so it might be faster (less mem alloc?)
def order_values_lcv2(board, x, y):
    def lcv(value):
        lcv_value = 0
        for peer in board.peers(x, y):
            if board.cell_empty(*peer) and value in board.possible_values(*peer):
                lcv_value += 1
        return lcv_value
    return sorted(board.possible_values(x, y,), key=lcv)


def infer(board, x, y, value):
    viable = True
    changed_list = []
    if settings.fc:
        fc_viable, fc_changed_list = board.forward_check(x, y, value)
        changed_list += fc_changed_list
        if not fc_viable:
            return fc_viable, changed_list
    if settings.ac:
        ac_viable, ac_changed_list = board.arc_consistency()
        changed_list += ac_changed_list
        if not ac_viable:
            return ac_viable, changed_list

    return viable, changed_list


def undo_infer(board, x, y, value, changed_list):
    if settings.fc or settings.ac:
        board.undo_changes(changed_list)


def backtrack(board, history=None, start_time=None):
    """This backtracking algorithm closely follows the model from Chapter 6 of Norvig's
    'Artifical Intelligence: A Modern Approach 3rd Edition' A brief outline of the algorithm
    is as follows:
        1. Choose an empty cell (if there are no empty cells then return the board as it is completed)
        2. Order the values in that cell's domain, then pick the first value to try
        3. If the chosen value doesn't violate a constraint, assign it to that cell
            (otherwise move to the next value in the ordering)
        4. Perform any inferences based on that assignment
        5. Perform backtrack() on the resulting board (recursion "magic" happens here!)
        6. If backtrack returns a solution then return that solution, otherwise
        7. Undo the assignment and inferences
        8. Proceed to the next value in the ordering from step 2, then proceed to step 3
        9. If there are no more values left in the ordering from step 2, then return None
            (This step will go "one level up" in the recursion and land at step 6)
    """
    if not history:
        history = []
    if not start_time:
        start_time = time.clock()
    global assignment_count
    global timeout

    elapsed_time = time.clock() - start_time
    if elapsed_time >= settings.time_limit and settings.time_limit != 0:
        timeout = True
        return board

    next_cell = choose_empty_cell(board)
    if next_cell is None:
        return board
    next_x, next_y = next_cell

    if settings.solver_display_verbose:
        print "Possible values at ({},{}): {}".format(next_x, next_y, order_possible_values(board, next_x, next_y))
    for value in order_possible_values(board, next_x, next_y):
        if settings.solver_display_verbose:
            print 'considering {} at ({},{})'.format(value, next_x, next_y)
        if not board.violates_constraints(next_x, next_y, value):
            board.assign(next_x, next_y, value)
            assignment_count += 1

            if settings.solver_display_verbose:
                print 'assigning {} to ({},{})'.format(value, next_x, next_y)
                print board.display()
            elif settings.solver_display_realtime:
                os.system('CLS')
                frame = '\n'.join([unsolved_puzzle_str, solution_header, board.display()])
                sys.stdout.write(frame + '\n')
                sys.stdout.flush()

            viable, inferences = infer(board, next_x, next_y, value)
            if viable:
                history.append(inferences)
                result = backtrack(board, history, start_time)
                if result:
                    return result
                inferences = history.pop()
            undo_infer(board, next_x, next_y, value, inferences)
            board.undo_assign(next_x, next_y)

            if settings.solver_display_verbose:
                print 'removing {} from ({},{})'.format(value, next_x, next_y)
                print board.display()

    if settings.solver_display_verbose:
        print 'ran out of values to consider for ({},{})'.format(next_x, next_y)
    return None


def solve(board, start_time=None):
    return backtrack(board, [], start_time)


def solve_puzzles(board_list):
    global assignment_count
    global timeout
    global unsolved_puzzle_str
    global solution_header
    global solution_str
    global raw_data_log
    global solution_log

    pnum = 1
    ptotal = len(board_list)
    solution_str = ''
    for each in board_list:
        if settings.solver_display_realtime and not settings.solver_display_verbose:
            os.system('CLS')  # Clear out old console output if realtime is on

        time_overall_start = time.clock()
        assignment_count = 0
        timeout = False
        viable = True

        board = create_board(each)

        puzzle_header = '==Puzzle {}/{}=='.format(pnum, ptotal).center(2 * board.N, '=')
        solution_header = '==Solution {}/{}=='.format(pnum, ptotal).center(2 * board.N, '=')
        unsolved_puzzle_str = '\n'.join([puzzle_header, board.display()])
        print unsolved_puzzle_str

        # ACP and FCP toss their 2nd return values (changed_list) because as pre-processes, there is no reason
        # to undo anything and therefore no reason to keep the changed_lists
        if settings.acp:
            viable *= board.arc_consistency()[0]
        if settings.fcp:
            for row in xrange(board.N):
                for col in xrange(board.N):
                    if board.cell_filled(row, col):
                        viable *= board.forward_check(row, col, board.cell_value(row, col))[0]

        time_search_start = time.clock()
        if viable:  # Skip attempting to solve if ACP or FCP finds the board not viable
            board = solve(board, time_search_start)
        time_end = time.clock()
        solved = board.solved() if board else False

        if settings.solver_display_realtime and not settings.solver_display_verbose:
            os.system('CLS')  # Clear out old console output if realtime is on
            print unsolved_puzzle_str

        solution_str = '\n'.join([solution_header,
                                  board.display() if solved else 'No Solution Found.',
                                  'Time: ' + str(1000 * (time_end - time_search_start)),
                                  'Assignments: ' + str(assignment_count),
                                  'Solution: ' + ('Yes' if solved else 'No'),
                                  'Timeout: ' + ('Yes' if timeout else 'No')])
        print solution_str

        if settings.solver_export_solution:
            solution_log.append((unsolved_puzzle_str, solution_str))

        if settings.solver_export_raw_data or settings.solver_export_data_summary:
            data_entry = (1000 * time_overall_start, 1000 * time_search_start, 1000 * time_end,
                          assignment_count, solved, timeout)
            raw_data_log.append(data_entry)
        pnum += 1
    return



def main(*args):
    if len(args) != 1:
        print "solver.py requires exactly 1 argument ({} given).".format(len(args))
        exit(-1)

    input_filepath = args[0]
    global raw_data_log
    global solution_log

    raw_data_log = [('time_overall_start', 'time_search_start', 'time_end', 'assignments', 'solution', 'timeout')]
    solution_log = []

    f_str = rw.read_file(input_filepath)
    if not verifier.valid_puzzles(f_str):
        print 'Input file does not contain puzzle(s) in a valid format.'
        exit(-1)
    puzzles = puzzle_list(f_str)

    solve_puzzles(puzzles)

    root, ext = os.path.splitext(input_filepath)

    if settings.solver_export_solution:
        solution_file_path = root + '_solution' + ext
        solution_str = '\n'.join('\n'.join(entry) for entry in solution_log)
        rw.write_file(solution_file_path, solution_str)

    if settings.solver_export_raw_data:
        data_file_path = root + '_raw_data' + ext
        str_data_log = [[str(item) for item in entry] for entry in raw_data_log]
        str_data_log = rw.adjust_col_widths(str_data_log)
        data_str = '\n'.join('\t'.join(entry) for entry in str_data_log)
        rw.write_file(data_file_path, data_str)

    if settings.solver_export_data_summary:
        data_summary_file_path = root + '_data_summary' + ext
        summary_header = 'Average Data for {} Puzzles'.format(len(raw_data_log) - 1)
        summary_divider = '-' * len(summary_header)

        averages = [sum(category) / float(len(category)) for category in zip(*raw_data_log[1:])]

        total_time = 'Total Time:'.ljust(21) + format(averages[2] - averages[0], '.2f')
        init_time = 'Initialization Time:'.ljust(21) + format(averages[1] - averages[0], '.2f')
        search_time = 'Search Time:'.ljust(21) + format(averages[2] - averages[1], '.2f')
        assignments = 'Assignments:'.ljust(21) + format(averages[3], '.2f')
        solutions = 'Solution Frequency:'.ljust(21) + format(averages[4], '.3f')
        timeouts = 'Timeout Frequency:'.ljust(21) + format(averages[5], '.3f')

        settings_str = 'Settings:' \
                       '\nForward Checking: ' + str(settings.fc) + \
                       '\nMinimum Remaining Values: ' + str(settings.mrv) + \
                       '\nDegree Heuristic: ' + str(settings.dh) + \
                       '\nLeast Constraining Value: ' + str(settings.lcv) + \
                       '\nArc Consistency Pre-Processing: ' + str(settings.acp) + \
                       '\nArc Consistency: ' + str(settings.ac) + \
                       '\n' + summary_divider + \
                       '\nDisplay Settings:' + \
                       '\nRealtime: ' + str(settings.solver_display_realtime) + \
                       '\nVerbose: ' + str(settings.solver_display_verbose)

        data_summary_str = '\n'.join((summary_header, summary_divider,
                                      total_time, init_time, search_time,
                                      assignments, solutions, timeouts,
                                      summary_divider, settings_str))
        rw.write_file(data_summary_file_path, data_summary_str)


if __name__ == '__main__':
    main(*sys.argv[1:])