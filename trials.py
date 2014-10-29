__author__ = 'jshoham'

# This script is for convenience when running a large number of data gathering solver runs.

import solver
import generator
from src import rw
from src import settings

DIRECTORY = 'trials2'

def f(n, m, how_many):
    return '{}/gen_n{}_m{:02d}_{}.txt'.format(DIRECTORY, n, m, how_many)


def gen_puzzles(n, p, q, m_list, how_many):
    """Output a set of files containing generated puzzles.
    The output file names will conform to the following spec:
    "trials2/gen_n{N_VALUE}_m{M_VALUE}_{HOW_MANY}.txt"
    eg, "trials2/gen_n9_m20_1000.txt" will contain 1000 9x9 puzzles where m = 20
    """
    for m in m_list:
        filename = f(n, m, how_many)
        board_list = set(generator.gen.generate_boards(n, p, q, m, how_many))
        board_str = '\n'.join(str(board) for board in board_list)

        rw.write_file(filename, board_str, rw.OVERWRITE)

        while len(board_list) < how_many:
            to_go = how_many - len(board_list)
            extras = set(generator.gen.generate_boards(n, p, q, m, to_go))
            board_list.update(extras)
            board_str = '\n'.join(str(board) for board in board_list)
            # Update output file after each time this step is completed.
            # Since generations that need more time usually need A LOT MORE time,
            # it's better to update the file semi regularly in case we end up quitting early
            # (ie if we get tired of waiting)
            rw.write_file(filename, board_str, rw.OVERWRITE)


def trial_1(file_list):
    """BT only"""
    settings.fc = False
    settings.mrv = False
    settings.dh = False
    settings.lcv = False
    settings.acp = False
    settings.ac = False
    settings.solver_display_realtime = False
    settings.solver_display_verbose = False

    for each in file_list:
        solver.s.main(each)


def trial_2(file_list):
    """BT+FC"""
    settings.fc = True
    settings.mrv = False
    settings.dh = False
    settings.lcv = False
    settings.acp = False
    settings.ac = False
    settings.solver_display_realtime = False
    settings.solver_display_verbose = False

    for each in file_list:
        solver.s.main(each)


def trial_3(file_list):
    """BT+FC+MRV"""
    settings.fc = True
    settings.mrv = True
    settings.dh = False
    settings.lcv = False
    settings.acp = False
    settings.ac = False
    settings.solver_display_realtime = False
    settings.solver_display_verbose = False

    for each in file_list:
        solver.s.main(each)


def trial_4(file_list):
    """BT+FC+MRV+DH"""
    settings.fc = True
    settings.mrv = True
    settings.dh = True
    settings.lcv = False
    settings.acp = False
    settings.ac = False
    settings.solver_display_realtime = False
    settings.solver_display_verbose = False

    for each in file_list:
        solver.s.main(each)


def trial_5(file_list):
    """BT+FC+MRV+DH+LCV"""
    settings.fc = True
    settings.mrv = True
    settings.dh = True
    settings.lcv = True
    settings.acp = False
    settings.ac = False
    settings.solver_display_realtime = False
    settings.solver_display_verbose = False

    for each in file_list:
        solver.s.main(each)


def trial_6(file_list):
    """BT+FC+MRV+DH+LCV+ACP"""
    settings.fc = True
    settings.mrv = True
    settings.dh = True
    settings.lcv = True
    settings.acp = True
    settings.ac = False
    settings.solver_display_realtime = False
    settings.solver_display_verbose = False

    for each in file_list:
        solver.s.main(each)


if __name__ == '__main__':
    m_list_ = range(5, 35) + range(35, 61, 5)
    file_list_ = [f(9, m_, 100) for m_ in m_list_]
    # gen_puzzles(9, 3, 3, m_list_, 100)


    trial_5(file_list_)