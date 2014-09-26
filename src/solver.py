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
import generator
import settings
import verifier


# opens the file and returns its contents as a string
def read_file(filename):
    f_str = ''
    try:
        with open(filename) as f:
            f_str = f.read()
    except:
        print "Failed to open file", filename
        exit(-1)
    return f_str


# creates a single puzzle based on the given string representation
def create_board(board_str):
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


# returns the row and col coordinates of the next empty cell
# returns None if there are no more empty cells
def choose_empty_cell(board):
    for row in xrange(board.N):
        for col in xrange(board.N):
            if board.grid[row][col].token == 0:
                return (row, col)
    return None


# returns a list of possible tokens at (x, y) sorted in increasing order
def order_possible_tokens(board, x, y):
    return sorted(board.possible_tokens(x, y))


def infer(board, x, y, value):
    if settings.fc:
        board.forward_check(x, y, value)


def undo_infer(board, x, y, value):
    if settings.fc:
        board.undo_forward_check(x, y, value)


def backtrack(board):
    elapsed_time = time.clock() - settings.start_time
    if elapsed_time > settings.time_limit:
        return board

    next_cell = choose_empty_cell(board)
    if next_cell is None:
        return board
    next_x, next_y = next_cell

    for value in order_possible_tokens(board, next_x, next_y):
        # print 'considering {} at ({},{})'.format(value, next_x, next_y)
        if not board.violates_constraints(next_x, next_y, value):
            # print 'assigning {} to ({},{})'.format(value, next_x, next_y)
            board.assign(next_x, next_y, value)
            #board.display()
            infer(board, next_x, next_y, value)
            result = backtrack(board)
            if result is not None:
                return result
            else:
                #print 'removing {} from ({},{})'.format(value, next_x, next_y)
                undo_infer(board, next_x, next_y, value)
                board.undo_assign(next_x, next_y)
                #board.display()

    # print 'ran out of values to consider for ({},{})'.format(next_x, next_y)
    return None


# returns a list strings with each entry containing an individual puzzle
def puzzle_list(f_str):
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


def solve_puzzles(filename):
    f_str = read_file(filename)
    if not verifier.valid_puzzles(f_str):
        print 'Input file does not contain puzzle(s) in a valid format.'
        exit(-1)
    p_list = puzzle_list(f_str)

    for each in p_list:
        settings.start_time = time.clock()
        board = create_board(each)
        print '=====Puzzle====='
        board.display()
        print '=====Solution====='
        solve(board).display()

    return


def solve(board):
    return backtrack(board)


def time_solve(function, board, num):
    for x in xrange(100):  # warming up for memory etc(???)
        function(board)

    average_time = 0

    for x in xrange(num):
        start_time = time.clock()
        function(board)
        end_time = time.clock()
        average_time += end_time - start_time

    return average_time / num


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "solver.py accepts exactly 1 argument ({} given).".format(len(sys.argv) - 1)
        exit(-1)

    input_filename = sys.argv[1]



    solve_puzzles(input_filename)


