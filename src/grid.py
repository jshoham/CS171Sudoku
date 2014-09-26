from random import randint


class Grid(object):
    def __init__(self, N=9, p=3, q=3):
        self.N = N  # The number of tokens
        self.p = p  # The number of rows per block
        self.q = q  # The number of columns per block
        self.grid = [[Cell(N) for i in xrange(N)] for j in xrange(N)]

    def __str__(self):
        param_list = [str(self.N), str(self.p), str(self.q)]
        row_list = [' '.join(param_list)]

        for row in xrange(self.N):
            cell_list = []
            for col in xrange(self.N):
                cell_list.append(str(self.cell_value(row, col)))
            row_list.append(' '.join(cell_list))
        grid_str = '\n'.join(row_list)
        return grid_str

    def __repr__(self):
        return str(self)

    def display(self, x=None, y=None):
        width = len(str(self.N)) + 1
        row_separator = '+'.join(['-' * (width * self.q)] * self.p)

        row_list = []
        for row in xrange(self.N):
            if row % self.p == 0 and row != 0:
                row_list.append(row_separator)

            col_list = []
            for col in xrange(self.N):
                if col % self.q == 0 and col != 0:
                    col_list.append('|')  # column separator

                cell_value = self.grid[row][col].token
                if row == x and col == y:
                    cell_value = '*'
                if cell_value == 0:
                    col_list.append('.'.center(width))
                else:
                    col_list.append(str(cell_value).center(width))

            row_list.append(''.join(col_list))

        display_str = '\n'.join(row_list)
        print display_str

    def display_cell(self, x, y):
        cell = self.grid[x][y]
        print 'Cell {}: token: {}, possible tokens: {}'.format((x, y), cell.token, cell.possible_tokens)

    def reset(self, x=None, y=None):
        if x is not None and y is not None:
            cell = self.grid[x][y]
            cell.token = 0
            cell.possible_tokens.update(range(1, self.N + 1))
            return

        for row in xrange(self.N):
            for col in xrange(self.N):
                cell = self.grid[row][col]
                cell.token = 0
                cell.possible_tokens.update(range(1, self.N + 1))

    # sets the cell at (x, y) to value, without running a constraint propagation
    def assign(self, x, y, value):
        self.grid[x][y].token = value

    def undo_assign(self, x, y,):
        self.grid[x][y].token = 0

    # eliminates possible_value from the cell at (x, y)
    def eliminate(self, x, y, possible_value):
        self.grid[x][y].possible_tokens.discard(possible_value)

    def cell_filled(self, x, y):
        return self.grid[x][y].token != 0

    def cell_value(self, x, y):
        return self.grid[x][y].token

    # propagate constraints only on empty cells
    def propagate_constraints(self, x, y, value):
        # remove value as a candidate from all peers in the same box
        upperleft_x = x - x % self.p
        upperleft_y = y - y % self.q
        for row in xrange(upperleft_x, upperleft_x + self.p):
            for col in xrange(upperleft_y, upperleft_y + self.q):
                if self.grid[row][col].token == 0:
                    self.grid[row][col].possible_tokens.discard(value)

        # remove value as a candidate from all peers in the same row and column
        for cell in xrange(self.N):
            if self.grid[x][cell].token == 0:
                self.grid[x][cell].possible_tokens.discard(value)
            if self.grid[cell][y].token == 0:
                self.grid[cell][y].possible_tokens.discard(value)

        # the cell at (x, y) will be cleared during the propagation process so re-add it
        self.grid[x][y].possible_tokens.add(value)

    def forward_check(self, x, y, value):
        # remove value as a candidate from all peers in the same box
        upperleft_x = x - x % self.p
        upperleft_y = y - y % self.q
        for row in xrange(upperleft_x, upperleft_x + self.p):
            for col in xrange(upperleft_y, upperleft_y + self.q):
                if self.grid[row][col].token == 0:
                    self.grid[row][col].eliminated_tokens[value] += 1

        # remove value as a candidate from all peers in the same row and column
        for cell in xrange(self.N):
            if self.grid[x][cell].token == 0:
                self.grid[x][cell].eliminated_tokens[value] += 1
            if self.grid[cell][y].token == 0:
                self.grid[cell][y].eliminated_tokens[value] += 1

        # the cell at (x, y) will be cleared during the propagation process so re-add it
        self.grid[x][y].eliminated_tokens[value] -= 1

    #todo
    def peers(self, x, y):
        """Returns a list of all the peer cells of the given cell, in the form (x, y)"""
        peer_list = []
        upperleft_x = x - x % self.p
        upperleft_y = y - y % self.q
        for row in xrange(self.N):
            for col in xrange(self.N):
                in_peers = (row == x) or\
                           (col == y) or\
                           (upperleft_x <= row and
                            row <= upperleft_x + x and
                            upperleft_y <= col and
                            col <= upperleft_y + y)
                if in_peers:
                    peer_list.append((row, col))

        return peer_list

    # re-adds value as a possible token to all peers of cell (x, y) if they are empty
    def undo_constraints(self, x, y, value):
        # re-add value as a candidate from all peers in the same box
        upperleft_x = x - x % self.p
        upperleft_y = y - y % self.q
        for row in xrange(upperleft_x, upperleft_x + self.p):
            for col in xrange(upperleft_y, upperleft_y + self.q):
                if self.grid[row][col].token == 0:
                    self.grid[row][col].possible_tokens.add(value)

        # re-add value as a candidate from all peers in the same row and column
        for cell in xrange(self.N):
            if self.grid[x][cell].token == 0:
                self.grid[x][cell].possible_tokens.add(value)
            if self.grid[cell][y].token == 0:
                self.grid[cell][y].possible_tokens.add(value)

    # checks if placing value in the cell at (x, y) will violate a row/column/box constraint
    def violates_constraints(self, x, y, value):
        if value == 0:  # zero designates an empty cell and thus never causes a violation
            return False

        # first check if value is contained in a peer cell in the same box
        upperleft_x = x - x % self.p
        upperleft_y = y - y % self.q
        for row in xrange(upperleft_x, upperleft_x + self.p):
            for col in xrange(upperleft_y, upperleft_y + self.q):
                if self.grid[row][col].token == value and (row, col) != (x, y):
                    return True

        # next check if value is contained in a peer cell in the same row or column
        for cell in xrange(self.N):
            if self.grid[cell][y].token == value and (cell, y) != (x, y):
                return True
            if self.grid[x][cell].token == value and (x, cell) != (x, y):
                return True

        return False


    def verify(self):
        for row in xrange(self.N):
            for col in xrange(self.N):
                if self.violates_constraints(row, col, self.grid[row][col].token):
                    return False
        return True


class Cell(object):
    def __init__(self, N):
        self.token = 0
        self.possible_tokens = set(range(1, N + 1))
        self.eliminated_tokens = [0 for x in xrange(1, N +1)]
