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

    def display(self, highlights=None):
        """Displays the board in an easy to read format.

        :param highlights: Optional, a list of (x, y) tuples representing cells to highlight
        """
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
                if highlights is not None and (row, col) in highlights:
                    cell_value = '*'
                if cell_value == 0:
                    col_list.append('.'.center(width))
                else:
                    col_list.append(str(cell_value).center(width))

            row_list.append(''.join(col_list))

        print '\n'.join(row_list)

    def display_cell(self, x, y):
        """Displays information about the cell at (x, y)."""
        cell = self.grid[x][y]
        print 'Cell {}: token: {}, possible tokens: {}'.format((x, y), cell.token, self.possible_tokens(x, y))

    def reset(self, x=None, y=None):
        """Resets the board, clearing all token values and eliminated candidates.

        Optional: If parameters x and y are supplied then only the cell at (x, y) will be reset.
        """
        if x is not None and y is not None:
            cell = self.grid[x][y]
            cell.token = 0
            cell.eliminated_tokens = {key: 0 for key in xrange(1, self.N + 1)}
            return

        for row in xrange(self.N):
            for col in xrange(self.N):
                cell = self.grid[row][col]
                cell.token = 0
                cell.eliminated_tokens = {key: 0 for key in xrange(1, self.N + 1)}

    def assign(self, x, y, value):
        """Assigns value to the cell at (x, y)"""
        self.grid[x][y].token = value

    def undo_assign(self, x, y):
        self.grid[x][y].token = 0

    # eliminates possible_value from the cell at (x, y)
    # def eliminate(self, x, y, possible_value):
    # self.grid[x][y].possible_tokens.discard(possible_value)

    def cell_filled(self, x, y):
        return self.grid[x][y].token != 0

    def cell_value(self, x, y):
        return self.grid[x][y].token

    def possible_tokens(self, x, y):
        possible_tokens = []
        cell = self.grid[x][y]
        for value in xrange(1, self.N + 1):
            if cell.eliminated_tokens[value] == 0:
                possible_tokens.append(value)

        return possible_tokens

    def forward_check(self, x, y, value):
        """Removes value as a candidate in all peer cells of (x, y).

        Return True if the board still has possible values for all of its cells.
        Return False if any cell has all of its candidates eliminated.
        """
        viable = True
        for cell in self.peers(x, y):
            row, col = cell
            self.grid[row][col].eliminated_tokens[value] += 1
            if not self.possible_tokens(row, col):
                viable *= False
        return viable

    def undo_forward_check(self, x, y, value):
        for cell in self.peers(x, y):
            row, col = cell
            self.grid[row][col].eliminated_tokens[value] -= 1

    def peers(self, x, y):
        """Returns a list of all the peer cells of the given cell, in the form (x, y)"""

        # upperleft_x and upperleft_y designate the upper left corner of the peer box
        upperleft_x = x - x % self.p
        upperleft_y = y - y % self.q

        box_xs = [xs for xs in xrange(upperleft_x, upperleft_x + self.p)]
        box_ys = [ys for ys in xrange(upperleft_y, upperleft_y + self.q)]

        box = [(xs, ys) for xs in box_xs for ys in box_ys if (xs, ys) != (x, y)]
        row = [(xs, y) for xs in xrange(0, upperleft_x)] + [(xs, y) for xs in xrange(upperleft_x + self.p, self.N)]
        col = [(x, ys) for ys in xrange(0, upperleft_y)] + [(x, ys) for ys in xrange(upperleft_y + self.q, self.N)]

        return box + row + col

    def violates_constraints(self, x, y, value):
        """Checks if assigning value to the cell at (x, y) violates a row/column/box constraint."""
        if value == 0:  # zero designates an empty cell and thus never causes a violation
            return False

        for cell in self.peers(x, y):
            row, col = cell
            if self.grid[row][col].token == value:
                return True

        return False

    def verify(self):
        for row in xrange(self.N):
            for col in xrange(self.N):
                if self.violates_constraints(row, col, self.grid[row][col].token):
                    return False
        return True

    def solved(self):
        """Returns true if the board has a complete and consistent assignment, False otherwise."""
        for row in xrange(self.N):
            for col in xrange(self.N):
                cell_value = self.cell_value(row, col)
                if cell_value == 0 or self.violates_constraints(row, col, cell_value):
                    return False
        return True


class Cell(object):
    def __init__(self, N):
        self.token = 0
        # self.possible_tokens = set(range(1, N + 1))
        self.eliminated_tokens = {key: 0 for key in xrange(1, N + 1)}
