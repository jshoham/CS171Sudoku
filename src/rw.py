# A simple module for reading and writing to files
import os
import traceback

OVERWRITE = 1

def read_file(filename):
    """Opens the file and returns its contents as a string."""
    try:
        with open(filename) as f:
            return f.read()
    except:
        print "Failed to open file", filename
        traceback.print_exc()
        exit(-1)


def write_file(filename, f_str, overwrite_flag=0):
    """Writes f_str out to filename. If filename already exists then create a duplicate
    with (x) appended to it."""
    base, ext = filename.split('.')
    new_filename = filename
    if not overwrite_flag:
        # if filename already exists, then rename this file as 'filename (x)'
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
        traceback.print_exc()
        exit(-1)