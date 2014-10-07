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

        return '\n'.join(row_list)

    def display_cell(self, x, y):
        """Displays information about the cell at (x, y)."""
        cell = self.grid[x][y]
        print 'Cell {}: token: {}, possible values: {}'.format((x, y), cell.token, self.possible_values(x, y))

    def reset(self, x=None, y=None):
        """Resets the board, clearing all token values and eliminated candidates.

        Optional: If parameters x and y are supplied then only the cell at (x, y) will be reset.
        """
        if x is not None and y is not None:
            cell = self.grid[x][y]
            cell.token = 0
            cell.possible_values.update(xrange(1, self.N + 1))
            return

        for row in xrange(self.N):
            for col in xrange(self.N):
                cell = self.grid[row][col]
                cell.token = 0
                cell.possible_values.update(xrange(1, self.N + 1))

    def assign(self, x, y, value):
        """Assigns value to the cell at (x, y)"""
        self.grid[x][y].token = value

    def undo_assign(self, x, y):
        self.grid[x][y].token = 0

    def eliminate(self, x, y, possible_value):
        """Eliminates possible_value from the cell at (x, y)"""
        self.grid[x][y].possible_values.discard(possible_value)

    def undo_eliminate(self, x, y, possible_value):
        self.grid[x][y].possible_values.add(possible_value)

    def cell_filled(self, x, y):
        return self.grid[x][y].token != 0

    def cell_empty(self, x, y):
        return self.grid[x][y].token == 0

    def cell_value(self, x, y):
        return self.grid[x][y].token

    def possible_values(self, x, y):
        return self.grid[x][y].possible_values

    def degree_heuristic(self, x, y):
        """Returns the degree of the given cell to other unassigned cells.

        To calculate the degree of a cell we need to count how many of its peers are both empty
        and have at least 2 possible values. Cells which are empty but have only 1 possible value
        are considered solved and are ignored by the degree heuristic, even if they haven't been
        explicitly assigned by backtrack."""
        # upperleft_x and upperleft_y designate the upper left corner of the peer box
        upperleft_x = x - x % self.p
        upperleft_y = y - y % self.q

        box_xs = [bxs for bxs in xrange(upperleft_x, upperleft_x + self.p)]
        box_ys = [bys for bys in xrange(upperleft_y, upperleft_y + self.q)]

        box = [(bxs, bys) for bxs in box_xs for bys in box_ys if (bxs, bys) != (x, y) and
               self.cell_empty(bxs, bys) and
               len(self.possible_values(bxs, bys)) > 1]
        row = [(x, ys) for ys in xrange(0, upperleft_y) if self.cell_empty(x, ys) and
               len(self.possible_values(x, ys)) > 1] + \
              [(x, ys) for ys in xrange(upperleft_y + self.q, self.N) if self.cell_empty(x, ys) and
               len(self.possible_values(x, ys)) > 1]
        col = [(xs, y) for xs in xrange(0, upperleft_x) if self.cell_empty(xs, y) and
               len(self.possible_values(xs, y)) > 1] + \
              [(xs, y) for xs in xrange(upperleft_x + self.p, self.N) if self.cell_empty(xs, y) and
               len(self.possible_values(xs, y)) > 1]

        return len(box + row + col)

    def degree_heuristic2(self, x, y):
        upperleft_x = x - x % self.p
        upperleft_y = y - y % self.q

        degree = 0

        # todo count the peers in box
        box_xs = [bxs for bxs in xrange(upperleft_x, upperleft_x + self.p)]
        box_ys = [bys for bys in xrange(upperleft_y, upperleft_y + self.q)]
        for bxs, bys in [(bxs, bys) for bxs in box_xs for bys in box_ys]:
            if self.cell_empty(bxs, bys) and len(self.possible_values(bxs, bys)) > 1 and (bxs, bys) != (x, y):
                degree += 1

        for ys in [range(0, upperleft_y) + range(upperleft_y + self.q, self.N)]:
            if self.cell_empty(x, ys) and len(self.possible_values(x, ys)) > 1:
                degree += 1

        for xs in [range(0, upperleft_x) + range(upperleft_x + self.p, self.N)]:
            if self.cell_empty(xs, y) and len(self.possible_values(xs, y)) > 1:
                degree += 1

        return degree

    def empty_cells(self):
        """Returns a list of all empty cells, in the form (x, y)."""
        empties = []
        for row in xrange(self.N):
            for col in xrange(self.N):
                if self.cell_empty(row, col):
                    empties.append((row, col))
        return empties

    def empty_cells2(self):
        # todo compare this implementation with the one above
        """Alternate implementation"""
        return [(row, col) for row in xrange(self.N) for col in xrange(self.N) if self.cell_empty(row, col)]

    def peers(self, x, y):
        """Returns a list of all the peer cells of the given cell, in the form (x, y)."""

        # upperleft_x and upperleft_y designate the upper left corner of the peer box
        upperleft_x = x - x % self.p
        upperleft_y = y - y % self.q

        box_xs = [xs for xs in xrange(upperleft_x, upperleft_x + self.p)]
        box_ys = [ys for ys in xrange(upperleft_y, upperleft_y + self.q)]

        box = [(xs, ys) for xs in box_xs for ys in box_ys if (xs, ys) != (x, y)]
        row = [(x, ys) for ys in xrange(0, upperleft_y)] + [(x, ys) for ys in xrange(upperleft_y + self.q, self.N)]
        col = [(xs, y) for xs in xrange(0, upperleft_x)] + [(xs, y) for xs in xrange(upperleft_x + self.p, self.N)]

        return box + row + col

    def violates_constraints(self, x, y, value):
        """Checks if assigning value to the cell at (x, y) violates a row/column/box constraint."""
        if value == 0:  # zero designates an empty cell and thus never causes a violation
            return False

        for (row, col) in self.peers(x, y):
            if self.grid[row][col].token == value:
                return True

        return False

    def verify(self):
        """Returns True if the board has no constraint violations, False otherwise."""
        for row in xrange(self.N):
            for col in xrange(self.N):
                if self.violates_constraints(row, col, self.grid[row][col].token):
                    return False
        return True

    def solved(self):
        """Returns True if the board has a complete and consistent assignment, False otherwise."""
        for row in xrange(self.N):
            for col in xrange(self.N):
                cell_value = self.cell_value(row, col)
                if cell_value == 0 or self.violates_constraints(row, col, cell_value):
                    return False
        return True


class Cell(object):
    def __init__(self, N):
        self.token = 0
        self.possible_values = set(xrange(1, N + 1))
