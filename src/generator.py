import sys
from random import sample, randint
from grid import Grid
import verifier


def read_file(filename):
    f_str = ''
    try:
        with open(filename) as f:
            f_str = f.read()
    except:
        print "Failed to open file", filename
        exit(-1)
    return f_str


def write_file(board_list, filename):
    f_str = '\n'.join(str(board) for board in board_list)
    try:
        with open(filename, 'w+') as f:
            f.write(f_str)
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
        print "Incorrect usage: generator accepts exactly 2 arguments ({} given).".format(len(sys.argv) - 1)
        exit(-1)

    input_filename, output_filename = sys.argv[1:3]
    how_many = 1

    print 'Reading input file "{}"...'.format(input_filename)
    f_str = read_file(input_filename)
    if not verifier.gen_input(f_str):
        print 'Input file does not meet the required format: "N p q M"'
        exit(-1)

    print 'Done. Generating board...'
    board_list = []
    N, p, q, M = [int(x) for x in f_str.split()]
    for x in range(how_many):
        board_list.append(generate(N, p, q, M))

    print 'Done. Writing to output file "{}"...'.format(output_filename)
    write_file(board_list, output_filename)
    print 'Finished.'
    if how_many == 1:
        board_list[0].display()
