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
import time
import re
import grid
import settings
import verifier


time_overall_start = None
time_search_start = None
assignments = None
solution = None
timeout = None


def read_file(filename):
    """Opens the file and returns its contents as a string."""
    f_str = ''
    try:
        with open(filename) as f:
            f_str = f.read()
    except:
        print "Failed to open file", filename
        exit(-1)
    return f_str


def puzzle_list(f_str):
    """Returns a list strings with each element containing an individual puzzle."""
    matches = re.findall(r'^([\d\.]+)$', f_str, re.MULTILINE)
    if matches:     # inline representation
        return matches
    else:       # default representation
        puzzle_list = []
        f_str_lines = f_str.splitlines()
        p_index = 0

        while p_index < len(f_str_lines):
            N, p, q = [int(x) for x in f_str_lines[p_index].split()]
            puzzle_lines = [f_str_lines[p_index]]

            for row in xrange(N):
                puzzle_lines.append(f_str_lines[p_index + row + 1])

            puzzle_list.append('\n'.join(puzzle_lines))
            p_index += N + 1

        return puzzle_list


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
    for row in xrange(board.N):
        for col in xrange(board.N):
            if board.grid[row][col].token == 0:
                return (row, col)
    return None


def order_possible_tokens(board, x, y):
    """Returns a list of possible tokens at (x, y) sorted in increasing order."""
    return sorted(board.possible_tokens(x, y))


def infer(board, x, y, value):
    if settings.fc:
        return board.forward_check(x, y, value)
    return True


def undo_infer(board, x, y, value):
    if settings.fc:
        board.undo_forward_check(x, y, value)


def backtrack(board):
    global time_search_start
    global assignments
    global timeout

    elapsed_time = time.clock() - time_search_start
    if elapsed_time >= settings.time_limit:
        timeout = True
        return board

    next_cell = choose_empty_cell(board)
    if next_cell is None:
        return board
    next_x, next_y = next_cell
    #print "Possible values at ({},{}): {}".format(next_x, next_y, order_possible_tokens(board, next_x, next_y))

    for value in order_possible_tokens(board, next_x, next_y):
        #print 'considering {} at ({},{})'.format(value, next_x, next_y)
        if not board.violates_constraints(next_x, next_y, value):
            viable = infer(board, next_x, next_y, value)
            if viable:
                #print 'assigning {} to ({},{})'.format(value, next_x, next_y)
                board.assign(next_x, next_y, value)
                assignments += 1
                #board.display()
                result = backtrack(board)
                if result is not None:
                    return result
                #print 'removing {} from ({},{})'.format(value, next_x, next_y)
                board.undo_assign(next_x, next_y)
                #board.display()
            undo_infer(board, next_x, next_y, value)

    #print 'ran out of values to consider for ({},{})'.format(next_x, next_y)
    return None


def solve(board):
    return backtrack(board)


def solve_puzzles(filename):
    global time_overall_start
    global time_search_start
    global time_end
    global assignments
    global solution
    global timeout


    f_str = read_file(filename)
    if not verifier.valid_puzzles(f_str):
        print 'Input file does not contain puzzle(s) in a valid format.'
        exit(-1)
    p_list = puzzle_list(f_str)

    for each in p_list:
        time_overall_start = time.clock()
        assignments = 0
        timeout = False
        board = create_board(each)
        print '=====Puzzle====='
        board.display()

        time_search_start = time.clock()
        board = solve(board)
        time_end = time.clock()
        solved = board.solved() if board else False

        print '=====Solution====='
        print 'Search Time: ', 1000*(time_end - time_search_start), ' milliseconds'
        print 'Assignments: ', assignments
        print 'Solution: ', 'Yes' if solved else 'No'
        print 'Timeout: ', 'Yes' if timeout else 'No'
        if solved:
            board.display()
    return


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "solver.py accepts exactly 1 argument ({} given).".format(len(sys.argv) - 1)
        exit(-1)

    input_filename = sys.argv[1]



    solve_puzzles(input_filename)


