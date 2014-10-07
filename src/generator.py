import sys
from random import sample, randint
import time
from grid import Grid
import verifier
import settings


def read_file(filename):
    try:
        with open(filename) as f:
            return f.read()
    except:
        print "Failed to open input file", filename
        exit(-1)


def write_file(filename, f_str):
    try:
        with open(filename, 'w+') as f:
            f.write(f_str)
    except:
        print 'Failed to open output file', filename
        exit(-1)


# Generate a random puzzle by repeatedly picking a random vacant cell and assigning a
# random token to it. If the token violates any of the constraints then undo that
# assignment, delete that token from the list of possible tokens at that cell, and
# repeat; if the list of possible tokens at that cell becomes empty, then fail globally
# (do not backtrack). Repeat until M cells have been filled. If you failed globally
# before the random puzzle was generated successfully, then execute a random restart and
# try again. Keep trying until success.
def generate(N, p, q, M, attempt=1, total=1):
    intro = 'Generating {}/{}'.format(attempt, total) if attempt and total else ''
    sys.stdout.write(intro)
    time_start = time.clock()
    restart_count = 0
    filled = 0
    board = Grid(N, p, q)
    while filled < M:
        elapsed_time = time.clock() - time_start
        if elapsed_time >= settings.gen_time_limit and settings.gen_time_limit:
            sys.stdout.write('Timed out. Consider using a lower M value.\n')
            return None

        row = randint(0, N - 1)
        col = randint(0, N - 1)

        while board.cell_empty(row, col):
            candidates = board.possible_values(row, col)
            if candidates:
                random_token = sample(candidates, 1)[0]
                if board.violates_constraints(row, col, random_token):
                    board.eliminate(row, col, random_token)
                else:
                    board.assign(row, col, random_token)
                    filled += 1
            else:
                restart_count += 1
                sys.stdout.write('\r{}: restarting.. (x{}) '.format(intro, restart_count))
                board.reset()
                filled = 0
                break
    sys.stdout.write('\n')
    return board


def generate_boards(N, p, q, M, quantity):
    board_list = [generate(N, p, q, M, x, quantity) for x in xrange(1, quantity + 1)]
    board_list = [board for board in board_list if board is not None]
    successful = len(board_list)
    print 'Generated {}/{} board(s) successfully.'.format(successful, quantity)
    return board_list


if __name__ == "__main__":
    if (not isinstance(settings.gen_how_many, (int, long))) or (settings.gen_how_many < 1):
        print('Invalid value for <settings.gen_how_many> (must be an integer greater than 0). Defaulting to 1.')
        settings.gen_how_many = 1
    if (not isinstance(settings.gen_time_limit, (int, long, float))) or (settings.gen_time_limit < 0):
        print('Invalid value for <settings.gen_time_limit> (must be a number greater or equal to 0). Defaulting to 5.')
        settings.gen_time_limit = 5
    if len(sys.argv) != 3:
        print('Incorrect usage: generator accepts exactly 2 arguments ({} given).'.format(len(sys.argv) - 1))
        exit(-1)

    input_filename, output_filename = sys.argv[1:3]

    print('Reading input file "{}"...'.format(input_filename))
    f_str = read_file(input_filename)
    if not verifier.gen_input(f_str):
        print 'Input file does not meet the required format: "N p q M"'
        exit(-1)

    print('Done. Generating board(s)...')
    N, p, q, M = [int(x) for x in f_str.split()]
    board_list = generate_boards(N, p, q, M, settings.gen_how_many)

    if not board_list:
        print 'Finished. No output generated.'
        exit(0)

    print 'Writing output to file "{}"...'.format(output_filename)
    write_file(output_filename, '\n'.join(str(board) for board in board_list))
    print 'Finished.'
    if settings.gen_how_many == 1:
        board_list[0].display()
