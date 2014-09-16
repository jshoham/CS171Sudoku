# grid
from random import randint


class Grid(object):
    def __init__(self, N=9, p=3, q=3, M=0):
        self.N = N  # The number of tokens
        self.p = p  # The number of rows per block
        self.q = q  # The number of columns per block
        self.M = M  # The number of tokens initially given
        self.grid = [[Cell(N) for i in xrange(N)] for j in xrange(N)]

    def __str__(self):
        grid_str = str(self.N) + " " + str(self.p) + " " + str(self.q) + " " \
                   + str(self.M) + "\n"

        for row in range(self.N):
            for col in range(self.N):
                grid_str += str(self.cellValue(row, col)) + " "
            grid_str += '\n'
        return grid_str

    def display(self, x=None, y=None):
        width = len(str(self.N)) + 1
        row_separator = '+'.join(['-' * (width * self.q)] * self.p)

        for row in range(self.N):
            if row%self.p == 0 and row != 0: print row_separator
            line = ''
            for col in range(self.N):
                if col%self.q == 0 and col != 0: line += '|' # column separator
                cell_value = self.cellValue(row, col)
                if row == x and col == y:
                    cell_value = '*'
                if cell_value == 0:
                    line += '.'.center(width)
                else:
                    line += str(cell_value).center(width)
            print line

    def displayCell(self, x, y):
        cell = self.grid[x][y]
        print 'Contents of cell at (', x, ',', y, '): token:', cell.token, 'possible tokens:', cell.possible_tokens

    def randomFill(self):
        for i in range(self.N):
            for j in range(self.N):
                cell = self.grid[i][j]
                cell.token = randint(0, self.N)

    def clear(self):
        for i in range(self.N):
            for j in range(self.N):
                cell = self.grid[i][j]
                cell.token = 0
                cell.possible_tokens.clear()
                cell.possible_tokens.update(range(1,self.N+1))

    # sets the cell at (x, y) to value, then runs a constraint propagation
    def choose(self, x, y, value):
        cell = self.grid[x][y]
        if value in cell.possible_tokens:
            self.propagateConstraints(x, y, value)
            cell.token = value
            return True
        else:
            return False

    # sets the cell at (x, y) to value, without running a constraint propagation
    def assign(self, x, y, value):
        self.grid[x][y].token = value

    def propagateConstraints(self, x, y, value):
        # remove value as a candidate from all peers in the same box
        upperleft_x = x - x%self.p
        upperleft_y = y - y%self.q
        for row in range(upperleft_x, upperleft_x+self.p):
            for col in range(upperleft_y, upperleft_y+self.q):
                self.grid[row][col].possible_tokens.discard(value)

        # remove value as a candidate from all peers in the same row and column
        for cell in range(self.N):
            self.grid[x][cell].possible_tokens.discard(value)
            self.grid[cell][y].possible_tokens.discard(value)

        # the cell at (x, y) will be cleared during the propagation process so re-add it
        self.grid[x][y].possible_tokens.add(value)


    # checks if placing value in the cell at (x, y) will violate a row/column/box constraint
    def violatesConstraints(self, x, y, value):
        if value == 0: # zero designates an empty cell and thus never causes a violation
            return False

        # first check if value is contained in a peer cell in the same box
        upperleft_x = x - x%self.p
        upperleft_y = y - y%self.q
        for row in range(upperleft_x, upperleft_x+self.p):
            for col in range(upperleft_y, upperleft_y+self.q):
                if self.cellValue(row, col) == value:
                   return True

        # next check if value is contained in a peer cell in the same row or column
        for cell in range(self.N):
            if self.cellValue(cell, y) == value:
                return True
            if self.cellValue(x, cell) == value:
                return True

        return False


    def cellFilled(self, x, y):
        return self.grid[x][y].token != 0

    def cellValue(self, x, y):
        return self.grid[x][y].token

class Cell(object):

    def __init__(self, N):
        self.token = 0
        self.possible_tokens = set(range(1, N+1))

