__author__ = 'jshoham'

import shutil
import glob


def main(*args):
    src = args[0]
    dst = args[1]

    for file in glob.glob(src):
        shutil.move(file, dst)


if __name__ == '__main__':
    n = 12
    directory = 'trials n{} 100'.format(n)

    t0 = 'bt fc acp'
    t1 = 'bt fc mrv dh lcv acp ac'
    t2 = 'bt fc mrv dh acp'

    all_args = [('{}/*_summary.txt'.format(directory), '{}/n{} results {}/'.format(directory, n, t0)),
                ('{}/*_data.txt'.format(directory), '{}/n{} results {}/'.format(directory, n, t0)),
                ('{}/*_solution.txt'.format(directory), '{}/n{} results {}/'.format(directory, n, t0)),
                ('{}/*(1).txt'.format(directory), '{}/n{} results {}/'.format(directory, n, t1)),
                # ('{}/*(2).txt'.format(directory), '{}/n{} results {}/'.format(directory, n, t2)),
                # ('{}/*(3).txt'.format(directory), '{}/n{} results {}/'.format(directory, n, t3)),
                # ('{}/*(4).txt'.format(directory), '{}/n{} results {}/'.format(directory, n, t4))
                ]

    for src, dst in all_args:
        main(src, dst)