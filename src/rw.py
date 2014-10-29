__author__ = 'jshoham'

# A simple module for reading and writing to files
import os
import traceback

OVERWRITE = 1

def read_file(file_path):
    """Opens the file and returns its contents as a string."""
    try:
        with open(file_path) as f:
            return f.read()
    except:
        print "Error: Failed to open file", file_path
        traceback.print_exc()
        exit(-1)


def write_file(file_path, f_str, overwrite_flag=0):
    """Writes f_str out to filename. If filename already exists then write to a new file
    with (x) appended to it. So if 'example.txt' exists then write to 'example (1).txt' instead"""
    root, ext = os.path.splitext(file_path)
    new_file_path = file_path
    if not overwrite_flag:
        # if 'example.txt' already exists, then rename file as 'example (1).txt', 'example (2).txt', and so on.
        i = 0
        while (os.path.isfile(new_file_path)):
            i += 1
            new_root = '{} ({})'.format(root, i)
            new_file_path = new_root + ext
    try:
        with open(new_file_path, 'w+') as f:
            f.write(f_str)
    except:
        print 'Error: Failed to open output file', file_path
        traceback.print_exc()
        exit(-1)


def adjust_col_widths(table):
    """Takes a 2 dimensional list of strings and adjusts the width of each column.
    The ith column is defined as including the ith element of each list in the table.
    Adjusting the width is accomplished by left justifying each element by the width of
    the longest element in that column.
    This way all columns will line up nicely when written to a text file.
    """
    zipped_table = zip(*table)
    col_widths = [max([len(item) for item in col]) for col in zipped_table]
    width_adjusted_columns = [[item.ljust(width) for item in column] for (width, column) in
                           zip(col_widths, zipped_table)]
    return zip(*width_adjusted_columns)