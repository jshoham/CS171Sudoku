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

import sys
import time
import re
import grid
import generator
import settings


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


# creates a puzzle based on the given string representation
def create_board(board_str):


    row_list = board_str.splitlines()
    N, p, q = [int(x) for x in row_list[0].split()]
    board = grid.Grid(N, p, q)

    for row in range(N):
        col_list = [int(x) for x in row_list[row + 1].split()]
        for col in range(N):
            board.assign(row, col, col_list[col])

    return board

def create_board2(board_str):
    N, p, q = 9, 3, 3
    board = grid.Grid(N, p, q)
    for row in range(N):
        for col in range(N):
            cell_value = board_str[row*9+col]
            cell_value = 0 if cell_value == '.' else int(cell_value)
            board.assign(row, col, cell_value)
    return board


# returns the row and col coordinates of the next empty cell
# returns None if there are no more empty cells
def choose_empty_cell(board):
    for row in range(board.N):
        for col in range(board.N):
            if board.grid[row][col].token == 0:
                return (row, col)
    return None


# returns a list of possible tokens at (x, y) sorted in increasing order
def order_possible_tokens(board, x, y):
    return sorted(board.grid[x][y].possible_tokens)


def infer(board, x, y, value):
    if settings.fc:
        board.propagate_constraints(x, y, value)


def undo_infer(board, x, y, value):
    if settings.fc:
        board.undo_constraints(x, y, value)


def backtrack(board):
    next_cell = choose_empty_cell(board)
    if next_cell == None:
        return board
    next_x, next_y = next_cell

    for value in order_possible_tokens(board, next_x, next_y):
        #print 'considering {} at ({},{})'.format(value, next_x, next_y)
        if not board.violates_constraints(next_x, next_y, value):
            #print 'assigning {} to ({},{})'.format(value, next_x, next_y)
            board.assign(next_x, next_y, value)
            #board.display()
            infer(board, next_x, next_y, value)
            result = backtrack(board)
            if result != None:
                return result
            else:
                #print 'removing {} from ({},{})'.format(value, next_x, next_y)
                undo_infer(board, next_x, next_y, value)
                board.undo_assign(next_x, next_y)
                #board.display()

    #print 'ran out of values to consider for ({},{})'.format(next_x, next_y)
    return None


# returns a list strings with each entry containing an individual puzzle
def puzzle_list(f_str):
    matches = re.findall(r'^([\d\.]+)$', f_str, re.MULTILINE)
    return (False, matches) if matches else (True, [f_str])


def solve_puzzles(filename):
    f_str = read_file(filename)
    normal, p_list = puzzle_list(f_str)

    for each in p_list:
        if normal:
            board = create_board(each)
            backtrack(board)
        else:
            print '========'
            board = create_board2(each)
            board.display()
            backtrack(board).display()

    return

def time_solve(function, board, num):
    for x in range(100):  # warming up for memory etc(???)
        function(board)

    average_time = 0

    for x in range(num):
        start_time = time.clock()
        function(board)
        end_time = time.clock()
        average_time += end_time - start_time

    return average_time/num



if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "solver.py accepts exactly 1 argument ({} given).".format(len(sys.argv) - 1)
        exit(-1)

    input_filename = sys.argv[1]

    board = create_board(read_file(input_filename))
    # board = generator.generate(9, 3, 3, 10)


    backtrack(board)


