# generator

from grid import Grid
from random import *

inputFile = 'gen_input.txt'
outputFile = 'gen_output.txt'


def readfile(inputFile):
    f = open(inputFile, 'r')
    line = f.readline().split()
    if len(line) == 4:
        N, p, q, M = line
    else:
        print "input error"


def verifyInput(N, p, q, M):
    assert(N > 0)
    assert(p > 0)
    assert(q > 0)
    assert(M > 0)
    assert(p*q == N)
    assert(M <= N**N)



# bug: if a cell's possible values is reduced to 1 by constraint propagation then the cell
# is considered solved but it is not reflected in the 'filled' count. Thus when the board
# becomes full it gets stuck in an infinite loop looking for nonexistent vacant cells
def generate(N, p, q, M):
    filled = 0
    board = Grid(N, p, q, M)
    while filled < M:
        i = randint(0, N - 1)
        j = randint(0, N - 1)
        possible_values = board.grid[i][j]
        if len(possible_values) == 0:
            board.clear()
            filled = 0
            print 'restarting'
        elif len(possible_values) > 1:
            if board.choose(i, j, sample(possible_values, 1)[0]):
                filled += 1
                print 'new', filled
                board.display()

    return board


# Generate a random puzzle by repeatedly picking a random vacant cell and assigning a
# random token to it. If the token violates any of the constraints then undo that
# assignment, delete that token from the list of possible tokens at that cell, and
# repeat; if the list of possible tokens at that cell becomes empty, then fail globally
# (do not backtrack). Repeat until M cells have been filled. If you failed globally
# before the random puzzle was generated successfully, then execute a random restart and
# try again. Keep trying until success.
def generate2(N, p, q, M):
    filled = 0
    board = Grid(N, p, q, M)
    while filled < M:
        i = randint(0, N - 1)
        j = randint(0, N - 1)

        while not board.cellFilled(i, j):
            possible_values = board.grid[i][j]
            if len(possible_values) == 0:
                board.clear()
                filled = 0
                print 'restarting'
                break
            else:
                random_value = sample(possible_values, 1)[0]
                if board.violatesConstraints(i, j, random_value):
                    possible_values.discard(random_value)
                else:
                    board.assign(i, j, random_value)
                    filled += 1
                    print 'chose', filled, 'values', 'added', random_value, 'to', i, j
                    board.display()
    return board


#print str(generate(9, 3, 3, 25))

generate(2, 2, 1, 4).display()