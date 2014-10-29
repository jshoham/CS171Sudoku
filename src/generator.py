__author__ = 'jshoham'

import sys
from random import sample, randint
import time
from grid import Grid
import rw
import verifier
import settings


# Generate a random puzzle by repeatedly picking a random vacant cell and assigning a
# random token to it. If the token violates any of the constraints then undo that
# assignment, delete that token from the list of possible tokens at that cell, and
# repeat; if the list of possible tokens at that cell becomes empty, then fail globally
# (do not backtrack). Repeat until M cells have been filled. If you failed globally
# before the random puzzle was generated successfully, then execute a random restart and
# try again. Keep trying until success.
def generate(N, p, q, M, attempt=1, total=1):
    intro = 'Generating {}/{}'.format(attempt, total)
    sys.stdout.write(intro)
    time_start = time.clock()
    restart_count = 0
    filled = 0
    board = Grid(N, p, q)
    while filled < M:
        # Check timeout condition
        elapsed_time = time.clock() - time_start
        if elapsed_time >= settings.gen_time_limit and settings.gen_time_limit != 0:
            sys.stdout.write(' Timed out. Consider using a lower M value.\n')
            return None

        # Choose a random cell to try
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
                sys.stdout.write('\r{}: restarting.. (x{})'.format(intro, restart_count))
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


def main(*args):
    if len(args) != 2:
        print('Incorrect usage: generator requires exactly 2 arguments ({} given).'.format(len(args)))
        return

    input_filepath, output_filepath = args[0:2]

    print('Reading input file "{}"...'.format(input_filepath))
    f_str = rw.read_file(input_filepath)
    if not f_str:
        return
    if not verifier.gen_input(f_str):
        print 'Input file does not meet the required format: "N p q M"'
        return

    print('Done. Generating board(s)...')
    N, p, q, M = [int(x) for x in f_str.split()]
    board_list = generate_boards(N, p, q, M, settings.gen_how_many)

    if not board_list:
        print 'Finished. No output generated.'
        return

    print 'Writing output to file "{}"...'.format(output_filepath)
    rw.write_file(output_filepath, '\n'.join(str(board) for board in board_list))
    print 'Finished.'
    if settings.gen_how_many == 1 and board_list[0]:
        print board_list[0].display()


if __name__ == "__main__":
    main(*sys.argv[1:])