__author__ = 'jshoham'

import sys
from src import generator as gen


def main(*args):
    gen.main(*args)


if __name__ == "__main__":
    main(*sys.argv[1:])
