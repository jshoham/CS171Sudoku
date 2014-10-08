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


time_overall_start = None
time_search_start = None
assignment_count = None
solution = None
timeout = None


def puzzle_list(f_str):
    """Returns a list strings with each element containing an individual puzzle."""
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
                if not board.cell_filled(row, col):
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
    for cell in cell_list[1:]:
        cell_v = len(board.possible_values(*cell))
        if cell_v < mrv_v:
            mrv_cell = cell
            mrv_v = cell_v
        elif settings.dh and cell_v == mrv_v:
            mrv_cell = choose_cell_dh(board, [mrv_cell, cell])
    return mrv_cell


def choose_cell_mrv2(board, cell_list):
    if not cell_list:
        return None
    return min(cell_list, key=(lambda cell: len(board.possible_values(*cell)))) if cell_list else None


def choose_cell_dh(board, cell_list):
    """Chooses the next empty cell which has the highest degree to other unassigned cells.

    The chosen cell will have the greatest number of peers which are unassigned and have at least
    2 possible values. Cells which have only 1 possible value are considered solved by the degree
    heuristic, even if they haven't been explicitly assigned by backtrack.
    """
    if not cell_list:
        return None
    dh_cell = cell_list[0]
    dh_degree = board.degree_heuristic(*dh_cell)
    for cell in cell_list[1:]:
        cell_degree = board.degree_heuristic(*cell)
        if cell_degree > dh_degree:
            dh_cell = cell
            dh_degree = cell_degree

    return dh_cell


# todo implement
def order_values_lcv(board, x, y):
    return []


def order_possible_values(board, x, y):
    """Returns a list of possible tokens at (x, y) sorted in increasing order."""
    if settings.lcv:
        return order_values_lcv(board, x, y)
    else:
        return sorted(board.possible_values(x, y))


def arc_consistency(board):
    cells = [(row, col) for row in xrange(board.N) for col in xrange(board.N)]
    arcs = [(cell_i, cell_j) for cell_i in cells for cell_j in board.peers(*cell_i)]

    changed_list = []
    while arcs:
        cell_i, cell_j = arcs.pop()
        revised, r_changed_list = revise(board, cell_i, cell_j)
        if revised:
            changed_list.append(r_changed_list)
            if len(board.possible_values(*cell_i)) == 0:
                return False, changed_list
            for peer in board.peers(*cell_i):
                if peer != cell_j:
                    arcs.append((peer, cell_i))
    return True, changed_list


def revise(board, cell_i, cell_j):
    revised = False
    del_list = []
    for value in board.possible_values(*cell_i):
        domain_j = board.possible_values(*cell_j)
        if (board.cell_filled(*cell_j) and board.cell_value(*cell_j) == value) or \
                                len(domain_j) == 1 and value in domain_j:
            del_list.append(value)
            revised = True
    for value in del_list:
        board.eliminate(cell_i[0], cell_i[1], value)

    changed_list = [cell_i, del_list]
    return revised, changed_list

def undo_ac_changes(board, changed_list):
    for change in changed_list:
        cell = change[0]
        deleted_values = change[1]
        for value in deleted_values:
            board.undo_eliminate(cell[0], cell[1], value)


def forward_check(board, x, y, value):
    """Removes value as a possible value from all the peers of cell (x, y).

    forward_check() only modifies peers where value is a possible value.

    forward_check() returns two items, changed_list and viable. changed_list is a list which
    contains the (x, y) of each cell that has been modified, while viable dictates whether
    all modified cells still have remaining possible values.
    """
    viable = True
    changed_list = []
    for (row, col) in board.peers(x, y):
        if value in board.possible_values(row, col):
            changed_list.append((row, col))
            board.eliminate(row, col, value)
            if not board.possible_values(row, col):
                viable = False
    return changed_list, viable


def undo_forward_check(board, value, changed_list):
    for (row, col) in changed_list:
        board.undo_eliminate(row, col, value)


def infer(board, x, y, value):
    if settings.fc:
        return forward_check(board, x, y, value)
    else:
        return True, True


def undo_infer(board, x, y, value, inference):
    if settings.fc:
        undo_forward_check(board, value, inference)


def backtrack(board, assignment):
    global assignment_count
    global timeout

    elapsed_time = time.clock() - time_search_start
    if elapsed_time >= settings.time_limit and settings.time_limit != 0:
        timeout = True
        return board

    next_cell = choose_empty_cell(board)
    if next_cell is None:
        return board
    next_x, next_y = next_cell

    if settings.solver_verbose:
        print "Possible values at ({},{}): {}".format(next_x, next_y, order_possible_values(board, next_x, next_y))
    for value in order_possible_values(board, next_x, next_y):
        if settings.solver_verbose:
            print 'considering {} at ({},{})'.format(value, next_x, next_y)
        if not board.violates_constraints(next_x, next_y, value):
            inferences, viable = infer(board, next_x, next_y, value)
            if viable:
                assignment.append(inferences)
                board.assign(next_x, next_y, value)
                assignment_count += 1
                if settings.solver_verbose:
                    print 'assigning {} to ({},{})'.format(value, next_x, next_y)
                    print board.display()
                elif settings.solver_display:
                    os.system('CLS')
                    sys.stdout.write(board.display() + '\n')
                    sys.stdout.flush()

                result = backtrack(board, assignment)
                if result:
                    return result
                board.undo_assign(next_x, next_y)
                if settings.solver_verbose:
                    print 'removing {} from ({},{})'.format(value, next_x, next_y)
                    print board.display()
                inferences = assignment.pop()
            undo_infer(board, next_x, next_y, value, inferences)

    if settings.solver_verbose:
        print 'ran out of values to consider for ({},{})'.format(next_x, next_y)
    return None


def solve(board):
    return backtrack(board, [])


def solve_puzzles(board_list):
    global time_overall_start
    global time_search_start
    global time_end
    global assignment_count
    global solution
    global timeout

    for each in board_list:
        time_overall_start = time.clock()
        assignment_count = 0
        timeout = False
        board = create_board(each)
        print '=====Puzzle====='
        print board.display()

        if settings.acp:
            solvable = arc_consistency(board)
            if not solvable:
                print 'ac found board to be unsolvable'
                exit(-1)

        time_search_start = time.clock()
        board = solve(board)
        time_end = time.clock()
        solved = board.solved() if board else False

        print '=====Solution====='
        print 'Search Time: ', 1000 * (time_end - time_search_start), ' milliseconds'
        print 'Assignments: ', assignment_count
        print 'Solution: ', 'Yes' if solved else 'No'
        print 'Timeout: ', 'Yes' if timeout else 'No'
        if solved:
            print board.display()
    return


def run(filename):
    f_str = rw.read_file(filename)
    if not verifier.valid_puzzles(f_str):
        print 'Input file does not contain puzzle(s) in a valid format.'
        exit(-1)
    puzzles = puzzle_list(f_str)

    solve_puzzles(puzzles)


def ezrun():
    run("easypuzzle.txt")

def ezboard(filename='easypuzzle.txt'):
    return create_board(puzzle_list(rw.read_file(filename))[0])

def ezinspect(board):
    for row in xrange(board.N):
        for col in xrange(board.N):
            board.display_cell(row, col)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "solver.py accepts exactly 1 argument ({} given).".format(len(sys.argv) - 1)
        exit(-1)

    input_filename = sys.argv[1]

    file_list = ['1011rand', 'subig20', 'top91', 'top95', 'top100', 'top870', 'top1465', 'top2365',
                 'topn87', 'topn234']
    file_list = ['puzzles_' + f + '.txt' for f in file_list]

    for f in file_list:
        run(f)
#    run(input_filename)
