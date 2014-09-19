# generator

from grid import Grid
from random import *
import sys


def read_file(input_filename):
    f = None
    try:
        f = open(input_filename, 'r')
    except:
        print 'Failed to open input file.'
        exit(-1)

    line = f.readline().split()
    param_list = []
    try:
        if len(line) == 4:
            param_list = [int(x) for x in line]
        else:
            exit(-1)
    except:
        print 'Input file is not in the correct format.'
        exit(-1)

    f.close()
    return param_list

def verify_input(N, p, q, M):
    verify = (N > 0) and \
             (p > 0) and \
             (q > 0) and \
             (M >= 0) and \
             (p*q == N) and \
             (M <= N**N)

    if not verify:
        print 'Invalid parameters: N = p*q and M < N^2 must be true'
        exit(-1)


def write_file(board, outfile):
    f = None
    try:
        f = open(outfile, 'w+')
    except:
        print 'Failed to open output file.'
        exit(-1)

    f.write(str(board))
    f.close()


# Generate a random puzzle by repeatedly picking a random vacant cell and assigning a
# random token to it. If the token violates any of the constraints then undo that
# assignment, delete that token from the list of possible tokens at that cell, and
# repeat; if the list of possible tokens at that cell becomes empty, then fail globally
# (do not backtrack). Repeat until M cells have been filled. If you failed globally
# before the random puzzle was generated successfully, then execute a random restart and
# try again. Keep trying until success.
def generate(N, p, q, M):
    filled = 0
    board = Grid(N, p, q, M)
    while filled < M:
        i = randint(0, N - 1)
        j = randint(0, N - 1)

        while not board.cell_filled(i, j):
            cell = board.grid[i][j]
            if len(cell.possible_tokens) == 0:
                board.reset()
                filled = 0
                print 'restarting..'
                break
            else:
                random_value = sample(cell.possible_tokens, 1)[0]
                if board.violates_constraints(i, j, random_value):
                    cell.possible_tokens.discard(random_value)
                else:
                    board.assign(i, j, random_value)
                    filled += 1
    return board


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "generator accepts exactly 2 arguments (", len(sys.argv)-1, " given)."
        exit(-1)

    input_filename, output_filename = sys.argv[1:3]

    print 'Reading input file...'
    N, p, q, M = read_file(input_filename)
    verify_input(N, p, q, M)

    print 'Done. Generating board...'
    board = generate(N, p, q, M)
    print 'Done. Writing to output file...'
    write_file(board, output_filename)
    print 'Finished.'
    board.display()
