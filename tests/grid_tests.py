from nose.tools import *
from src.grid import *


def test_reset():
    N, p, q = 9, 3, 3
    board = Grid(N, p, q)

    for row in xrange(N):
        for col in xrange(N):
            board.grid[row][col].possible_values.discard(1)
            board.reset(row, col)
            assert_equals(board.grid[row][col].possible_values, set(xrange(1, N + 1)))

    for row in xrange(N):
        for col in xrange(N):
            board.grid[row][col].possible_values.discard(1)

    board.reset()

    for row in xrange(N):
        for col in xrange(N):
            assert_equals(board.grid[row][col].possible_values, set(xrange(1, N + 1)))
