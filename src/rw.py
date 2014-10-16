# A simple module for reading and writing to files
import os

def read_file(filename):
    """Opens the file and returns its contents as a string."""
    try:
        with open(filename) as f:
            return f.read()
    except:
        print "Failed to open file", filename
        exit(-1)


def write_file(filename, f_str):
    # if filename already exists, then rename this file as 'filename (x)'
    base, ext = filename.split('.')
    new_filename = filename
    i = 0
    while (os.path.isfile(new_filename)):
        i += 1
        new_base = base + ' ({})'.format(i)
        new_filename = new_base + '.' + ext
    try:
        with open(new_filename, 'w+') as f:
            f.write(f_str)
    except:
        print 'Failed to open output file', filename
        exit(-1)