# A simple module for reading and writing to files

def read_file(filename):
    """Opens the file and returns its contents as a string."""
    try:
        with open(filename) as f:
            return f.read()
    except:
        print "Failed to open file", filename
        exit(-1)


def write_file(filename, f_str):
    try:
        with open(filename, 'w+') as f:
            f.write(f_str)
    except:
        print 'Failed to open output file', filename
        exit(-1)