from grid import Grid
from random import sample, randint
import sys


def read_file(filename):
    f_str = ''
    try:
        with open(filename) as f:
            f_str = f.readline()
    except:
        print 'Failed to open input file.'
        exit(-1)

    line = f_str.split()
    param_list = []
    try:
        if len(line) == 4:
            param_list = [int(x) for x in line]
        else:
            exit(-1)
    except:
        print 'Input file is not in the correct format. Ensure that the input file only contains' \
              'four integers on one line, separated by spaces.'
        exit(-1)

    return param_list

def verify_input(N, p, q, M):
    verify = (N > 0) and \
             (p > 0) and \
             (q > 0) and \
             (M >= 0) and \
             (p*q == N) and \
             (M <= N**N)

    if not verify:
        print 'Invalid parameters: Ensure that all parameters are positive integers and' \
              ' N = p*q and M < N^2'
        exit(-1)


def write_file(board, filename):
    try:
        with open(filename, 'w+') as f:
            f.write(str(board))
    except:
        print 'Failed to open output file.'
        exit(-1)


# Generate a random puzzle by repeatedly picking a random vacant cell and assigning a
# random token to it. If the token violates any of the constraints then undo that
# assignment, delete that token from the list of possible tokens at that cell, and
# repeat; if the list of possible tokens at that cell becomes empty, then fail globally
# (do not backtrack). Repeat until M cells have been filled. If you failed globally
# before the random puzzle was generated successfully, then execute a random restart and
# try again. Keep trying until success.
def generate(N, p, q, M):
    filled = 0
    board = Grid(N, p, q)
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
                random_token = sample(cell.possible_tokens, 1)[0]
                if board.violates_constraints(i, j, random_token):
                    cell.possible_tokens.discard(random_token)
                else:
                    board.assign(i, j, random_token)
                    filled += 1
    return board


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "generator accepts exactly 2 arguments ({} given).".format(len(sys.argv)-1)
        exit(-1)

    input_filename, output_filename = sys.argv[1:3]

    print 'Reading input file "{}"...'.format(input_filename)
    N, p, q, M = read_file(input_filename)
    verify_input(N, p, q, M)

    print 'Done. Generating board...'
    board = generate(N, p, q, M)
    print 'Done. Writing to output file "{}"...'.format(output_filename)
    write_file(board, output_filename)
    print 'Finished.'
    board.display()
