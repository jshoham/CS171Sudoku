__author__ = 'Jake'
import grid


def peers(x, y):
        """Returns a list of all the peer cells of the given cell, in the form (x, y)"""
        N, p, q = 16, 4, 4

        upperleft_x = x - x % p
        upperleft_y = y - y % q

        box_xs = [xs for xs  in xrange(upperleft_x, upperleft_x + p)]
        box_ys = [ys for ys in xrange(upperleft_y, upperleft_y + q)]

        box = [(xs, ys) for xs in box_xs for ys in box_ys]


        row = [(xs, y) for xs in xrange(0, upperleft_x)] + [(xs, y) for xs in xrange(upperleft_x + p, N)]

        col = [(x, ys) for ys in xrange(0, upperleft_y)] + [(x, ys) for ys in xrange(upperleft_y + q, N)]

        return box + row + col

board = grid.Grid(16, 4, 4)

board.display(board.peers(3,4))
