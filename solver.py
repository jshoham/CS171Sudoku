__author__ = 'jshoham'

import sys
from src import solver as s


def main(*args):
    s.main(*args)


if __name__ == '__main__':
    main(*sys.argv[1:])