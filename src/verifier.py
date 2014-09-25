# This module verifies that input files are in the correct formats


import re


# Generator input: Exactly one line containing four integers, N, p, q, and M, separated by spaces.
# N = p*q and M <= N*N must be true. For example:
# 9 3 3 40
# or
# 16 4 4 50
def gen_input(s):
    verified = re.match(r'^(\d+)(\s+\d+){3}\s*$', s)
    if verified:
        N, p, q, M = [int(x) for x in s.split()]
        verified = (N > 0) and\
                   (p > 0) and\
                   (q > 0) and\
                   (M >= 0) and\
                   (N == p*q) and\
                   (M <= N**N)
    return verified


# Board default representation:
# The first line contains 3 integers N, p, and q separated by spaces. N = p*q must be true.
# There must be N following lines, each line containing N integers separated by spaces. Every
# integer must be within 0-N. A file may contain 1 or more puzzles separated by newlines.
# For example:
# 6 2 3
# 5 0 0 3 0 0
# 0 0 2 0 0 4
# 4 3 0 0 5 0
# 0 0 1 2 0 0
# 1 0 0 0 4 0
# 0 2 0 0 1 5
def board_default(s):
    verified = re.match(r"""^(\d+(\s+\d+){2})       # puzzle parameters
                            (\n\d+(\s+\d+)*)\s*$    # 1 or more lines of numbers
                            """, s, re.VERBOSE)
    if verified:
        s_lines = s.splitlines()
        p_index = 0   # index of the starting line/parameter list of the next puzzle in the file

        while p_index < len(s_lines):
            puzzle_params = [int(x) for x in s_lines[p_index].split()]
            if len(puzzle_params) != 3:
                return False
            N, p, q = puzzle_params
            if N != p*q:
                return False

            for row in range(N):
                col_list = [int(x) for x in s_lines[p_index + row + 1].split()]
                if len(col_list) != N:
                    return False
                for col in col_list:
                    if col not in range(0, N + 1):
                        return False
            p_index += N + 1
    return True if verified else False


# Board inline representation (9x9 puzzles only):
# A puzzle is represented on a single line 81 characters long. Each character is either the digits
# 1-9 or a '.' to represent blank cells. A file can contain an arbitrary number of puzzles.
# For example a file containing three puzzles might look like:
# 52...6.........7.13...........4..8..6......5...........418.........3..2...87.....
# 4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......
# 48.3............71.2.......7.5....6....2..8.............1.76...3.....4......5....
def board_inline(s):
    matches = re.match(r'^([\d\.]{81})(\n[\d\.]{81})*\s*$', s)
    return True if matches else False


# a file string contains valid puzzles if they are in either the inline representation or the
# default representation
def valid_puzzles(s):
    return board_inline(s) or board_default(s)
