import solver
import generator
from src import rw
from src import settings


def f(m_list):
    """Return a list of filenames based on the given m list"""
    return ['trials/gen_n9_m{:02d}_1000.txt'.format(m) for m in m_list]


def g(m_list):
    """Output a set of files containing generated puzzles.
    The output file names will conform to the following spec:
    "trials/gen_n9_m{M_VALUE}_{HOW_MANY}.txt"
    eg, "trials/gen_n9_m20_1000.txt" will contain 1000 puzzles where m = 20
    """
    n, p, q = 9, 3, 3
    how_many = 1000
    for m in m_list:
        filename = 'trials/gen_n9_m{:02d}_{}.txt'.format(m, how_many)
        board_list = set(generator.g.generate_boards(n, p, q, m, how_many))
        board_str = '\n'.join(str(board) for board in board_list)

        rw.write_file(filename, board_str, rw.OVERWRITE)

        while len(board_list) < how_many:
            to_go = how_many - len(board_list)
            extras = set(generator.g.generate_boards(n, p, q, m, to_go))
            board_list.update(extras)
            board_str = '\n'.join(str(board) for board in board_list)
            # Update output file after each time this step is completed.
            # Since generations that need more time usually need A LOT MORE time,
            # it's better to update the file semi regularly in case we end up quitting early
            # (ie if we get tired of waiting)
            rw.write_file(filename, board_str, rw.OVERWRITE)


def trial_1(file_list):
    """For the first trial we will solve the following puzzles using backtracking ONLY"""
    settings.fc = False
    settings.mrv = False
    settings.dh = False
    settings.lcv = False
    settings.acp = False
    settings.ac = False

    for each in file_list:
        solver.s.run(each)


def trial_2(file_list):
    """For the second trial we will solve the following puzzles using backtrack + forward checking"""
    settings.fc = True
    settings.mrv = False
    settings.dh = False
    settings.lcv = False
    settings.acp = False
    settings.ac = False

    for each in file_list:
        solver.s.run(each)


if __name__ == '__main__':
    m_list = xrange(5, 30)
    f_list = f(m_list)
    trial_1(f_list)
    trial_2(f_list)