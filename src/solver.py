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
    """Returns a list of possible tokens at (x, y) sorted in increasing order."""
    if settings.lcv:
        return order_values_lcv(board, x, y)
    else:
        return sorted(board.possible_values(x, y))


# todo implement
def order_values_lcv(board, x, y):
    return []


def infer(board, x, y, value):
    if settings.fc:
        return board.forward_check(x, y, value)
    else:
        return True, True


def undo_infer(board, x, y, value, changed_list):
    if settings.fc:
        board.undo_changes(changed_list)


def backtrack(board, history=None, start_time=None):
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

    if settings.solver_display_verbose and not settings.solver_display_realtime:
        print "Possible values at ({},{}): {}".format(next_x, next_y, order_possible_values(board, next_x, next_y))
    for value in order_possible_values(board, next_x, next_y):
        if settings.solver_display_verbose and not settings.solver_display_realtime:
            print 'considering {} at ({},{})'.format(value, next_x, next_y)
        if not board.violates_constraints(next_x, next_y, value):
            board.assign(next_x, next_y, value)
            assignment_count += 1

            if settings.solver_display_verbose and not settings.solver_display_realtime:
                print 'assigning {} to ({},{})'.format(value, next_x, next_y)
                print board.display()
            elif settings.solver_display_realtime:
                os.system('CLS')
                sys.stdout.write(board.display() + '\n')
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

            if settings.solver_display_verbose and not settings.solver_display_realtime:
                print 'removing {} from ({},{})'.format(value, next_x, next_y)
                print board.display()

    if settings.solver_display_verbose and not settings.solver_display_realtime:
        print 'ran out of values to consider for ({},{})'.format(next_x, next_y)
    return None


def solve(board, start_time=None):
    return backtrack(board, [], start_time)


def solve_puzzles(board_list):
    global assignment_count
    global timeout
    global raw_data_log
    global solution_log

    pnum = 1
    ptotal = len(board_list)
    for each in board_list:
        time_overall_start = time.clock()
        assignment_count = 0
        timeout = False
        viable = True

        board = create_board(each)

        puzzle_header = '==Puzzle {}/{}=='.format(pnum, ptotal).center(2 * board.N, '=')
        solution_header = '==Solution {}/{}=='.format(pnum, ptotal).center(2 * board.N, '=')
        print puzzle_header
        print board.display()

        if settings.acp:
            viable, changed_list = board.arc_consistency()

        time_search_start = time.clock()
        if viable:  # Skip attempting to solve if ACP finds the board not viable
            board = solve(board, time_search_start)
        time_end = time.clock()
        solved = board.solved() if board else False

        print solution_header
        if solved:
            print board.display()

        print 'Time:', 1000 * (time_end - time_search_start)
        print 'Assignments:', assignment_count
        print 'Solution:', 'Yes' if solved else 'No'
        print 'Timeout:', 'Yes' if timeout else 'No'

        if settings.solver_export_solution:
            original = str(create_board(each))
            solution = str(board) if solved else 'No Solution Found.'
            solution_log.append((puzzle_header, original, solution))

        if settings.solver_export_raw_data or settings.solver_export_data_summary:
            data_entry = (1000 * time_overall_start, 1000 * time_search_start, 1000 * time_end,
                          assignment_count, solved, timeout)
            raw_data_log.append(data_entry)
        pnum += 1
    return


def run(filename):
    global raw_data_log
    global solution_log

    raw_data_log = [('time_overall_start', 'time_search_start', 'time_end', 'assignments', 'solution', 'timeout')]
    solution_log = []

    f_str = rw.read_file(filename)
    if not verifier.valid_puzzles(f_str):
        print 'Input file does not contain puzzle(s) in a valid format.'
        exit(-1)
    puzzles = puzzle_list(f_str)

    solve_puzzles(puzzles)

    if settings.solver_export_solution:
        solution_filename = filename[:-4] + '_solution.txt'
        solution_str = '\n'.join('\n'.join(entry) for entry in solution_log)
        rw.write_file(solution_filename, solution_str)

    if settings.solver_export_raw_data:
        data_filename = filename[:-4] + '_raw_data.txt'
        data_str = '\n'.join('\t'.join(str(item) for item in entry) for entry in raw_data_log)
        rw.write_file(data_filename, data_str)

    if settings.solver_export_data_summary:
        data_summary_filename = filename[:-4] + '_data_summary.txt'
        summary_header = 'Average Data for {} Puzzles'.format(len(raw_data_log) - 1)
        summary_divider = '-' * len(summary_header)

        averages = [sum(category) / float(len(category)) for category in zip(*raw_data_log[1:])]

        init_time = 'Initialization Time: ' + str(averages[1] - averages[0])
        search_time = 'Search Time: ' + str(averages[2] - averages[1])
        total_time = 'Total Time: ' + str(averages[2] - averages[0])
        assignments = 'Assignments: ' + str(averages[3])
        solutions = 'Solution Frequency: ' + str(averages[4])
        timeouts = 'Timeout Frequency: ' + str(averages[5])

        data_summary_str = '\n'.join((summary_header, summary_divider,
                                      total_time, init_time, search_time,
                                      assignments, solutions, timeouts))
        rw.write_file(data_summary_filename, data_summary_str)


def db_run():
    """Debugging use"""
    run("easypuzzle.txt")


def db_board(filename='easypuzzle.txt'):
    """Debugging use"""
    return create_board(puzzle_list(rw.read_file(filename))[0])


def db_inspect(board):
    """Debugging use"""
    for row in xrange(board.N):
        for col in xrange(board.N):
            board.display_cell(row, col)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "solver.py requires exactly 1 argument ({} given).".format(len(sys.argv) - 1)
        exit(-1)

    input_filename = sys.argv[1]

    run(input_filename)