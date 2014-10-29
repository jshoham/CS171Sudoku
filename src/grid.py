class Grid(object):
    def __init__(self, N=9, p=3, q=3):
        self.N = N  # The number of tokens
        self.p = p  # The number of rows per block
        self.q = q  # The number of columns per block
        self.grid = [[Cell(N) for col in xrange(N)] for row in xrange(N)]

    def __str__(self):
        param_list = [' '.join((str(self.N), str(self.p), str(self.q)))]
        row_list = [' '.join(str(self.cell_value(row, col)) for col in xrange(self.N)) for row in xrange(self.N)]
        return '\n'.join(param_list + row_list)

    def __repr__(self):
        return str(self)

    def display(self, highlights=None):
        """Returns a string of the board in an easy to read format.

        :param highlights: Optional, a list of (x, y) tuples representing cells to highlight. Highlighted cells show
        stars in place of their actual values.
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
                cell_value = str(cell_value) if cell_value != 0 else '.'
                col_list.append(cell_value.center(width))

            row_list.append(''.join(col_list))

        return '\n'.join(row_list)

    def display_cell(self, x, y):
        """Displays detailed information about the cell at (x, y). For testing and debugging use."""
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

        box_xs = xrange(upperleft_x, upperleft_x + self.p)
        box_ys = xrange(upperleft_y, upperleft_y + self.q)

        box = [(bxs, bys) for bxs in box_xs for bys in box_ys if self.cell_empty(bxs, bys) and
               len(self.possible_values(bxs, bys)) > 1 and (bxs, bys) != (x, y)]
        row = [(x, rys) for rys in xrange(0, upperleft_y) if self.cell_empty(x, rys) and
               len(self.possible_values(x, rys)) > 1] + \
              [(x, rys) for rys in xrange(upperleft_y + self.q, self.N) if self.cell_empty(x, rys) and
               len(self.possible_values(x, rys)) > 1]
        col = [(cxs, y) for cxs in xrange(0, upperleft_x) if self.cell_empty(cxs, y) and
               len(self.possible_values(cxs, y)) > 1] + \
              [(cxs, y) for cxs in xrange(upperleft_x + self.p, self.N) if self.cell_empty(cxs, y) and
               len(self.possible_values(cxs, y)) > 1]

        return len(box + row + col)

    # Alternate implementation. This one doesn't use list comprehensions so it might be faster (less memory allocation?)
    def degree_heuristic2(self, x, y):
        upper_left_x = x - x % self.p
        upper_left_y = y - y % self.q

        degree = 0

        # Count in the box
        for bxs in xrange(upper_left_x, upper_left_x + self.p):
            for bys in xrange(upper_left_y, upper_left_y + self.q):
                if self.cell_empty(bxs, bys) and len(self.possible_values(bxs, bys)) > 1 and (bxs, bys) != (x, y):
                    degree += 1

        # Count in the row
        for rys in xrange(0, upper_left_y):
            if self.cell_empty(x, rys) and len(self.possible_values(x, rys)) > 1:
                degree += 1
        for rys in xrange(upper_left_y + self.q, self.N):
            if self.cell_empty(x, rys) and len(self.possible_values(x, rys)) > 1:
                degree += 1

        # Count in the column
        for cxs in xrange(0, upper_left_x):
            if self.cell_empty(cxs, y) and len(self.possible_values(cxs, y)) > 1:
                degree += 1
        for cxs in xrange(upper_left_x + self.p, self.N):
            if self.cell_empty(cxs, y) and len(self.possible_values(cxs, y)) > 1:
                degree += 1

        return degree


    def forward_check(self, x, y, value):
        """Removes value as a possible value from all the peers of cell (x, y).

        Only modifies peers which contain value as a possible value.
        Returns True/False if the board is still viable, and a list of all changes made.
        """
        changed_list = []
        for (row, col) in self.peers(x, y):
            if value in self.possible_values(row, col):
                changed_list.append(((row, col), [value]))
                self.eliminate(row, col, value)
                if not self.possible_values(row, col):
                    return False, changed_list
        return True, changed_list

    def arc_consistency(self):
        """Establishes arc consistency on board.

        A cell i is arc consistent with another cell j if, for each possible value in i's domain,
        j has a legal assignment. Naturally this is only significant when i and j are peers of
        each other, as non-peer cells can never violate a constraint by their very nature. A board
        is arc consistent if all of its cells are arc consistent with each of their peers.

        Returns True if the board is solvable, False otherwise. Also returns a list of all changes
        which have been made to board, so that they can be undone if needed.
        """
        def revise(board, cell_i, cell_j):
            """Make cell_i arc consistent with cell_j. If a possible value in cell_i's
            domain leaves cell_j with no legal assignment, then discard that value from
            cell_i's domain. Returns True if cell_i's domain has been modified, False
            otherwise. Also returns a record of all changes made to the cell.
            """
            revised = False
            del_list = []
            for i_value in board.possible_values(*cell_i):
                domain_j = board.possible_values(*cell_j)
                if board.cell_value(*cell_j) == i_value or (len(domain_j) == 1 and i_value in domain_j):
                    del_list.append(i_value)
                    revised = True
            # We have to do all the eliminations here since we cannot edit the possible_values set
            # while iterating over it. This is a property of the set built-in type in Python.
            for i_value in del_list:
                board.eliminate(cell_i[0], cell_i[1], i_value)

            changed_record = (cell_i, del_list)
            return revised, changed_record

        # Begin Arc Consistency here by creating a stack of all arcs in the board
        cells = [(row, col) for row in xrange(self.N) for col in xrange(self.N)]
        arcs = [(cell_i, cell_j) for cell_i in cells for cell_j in self.peers(*cell_i)]

        changed_list = []  # track all changes made to board so they can be undone if needed
        while arcs:
            cell_i, cell_j = arcs.pop()
            revised, r_changed_record = revise(self, cell_i, cell_j)
            if revised:
                changed_list.append(r_changed_record)
                if len(self.possible_values(*cell_i)) == 0:
                    return False, changed_list
                for peer in self.peers(*cell_i):
                    if peer != cell_j:
                        arcs.append((peer, cell_i))
        return True, changed_list

    def undo_changes(self, changed_list):
        """Undo changes made by forward check or arc consistency."""
        for change in changed_list:
            (row, col), values = change
            for value in values:
                self.undo_eliminate(row, col, value)

    def empty_cells(self):
        """Returns a list of all the empty cells in the board, in the form (x, y)."""
        return [(row, col) for row in xrange(self.N) for col in xrange(self.N) if self.cell_empty(row, col)]

    def peers(self, x, y):
        """Returns a list of all the peer cells of the given cell, in the form (x, y)."""

        # upperleft_x and upperleft_y designate the upper left corner of the peer box
        upperleft_x = x - x % self.p
        upperleft_y = y - y % self.q

        box_xs = xrange(upperleft_x, upperleft_x + self.p)
        box_ys = xrange(upperleft_y, upperleft_y + self.q)

        box = [(bxs, bys) for bxs in box_xs for bys in box_ys if (bxs, bys) != (x, y)]
        row = [(x, rys) for rys in xrange(0, upperleft_y)] + [(x, rys) for rys in xrange(upperleft_y + self.q, self.N)]
        col = [(cxs, y) for cxs in xrange(0, upperleft_x)] + [(cxs, y) for cxs in xrange(upperleft_x + self.p, self.N)]

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
