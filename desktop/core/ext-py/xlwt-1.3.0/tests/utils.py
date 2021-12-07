import os
from os.path import join, dirname, abspath, isdir

def in_tst_dir(filename):
    return join(dirname(abspath(__file__)), filename)

def in_tst_output_dir(filename):
    output_dir = join(dirname(abspath(__file__)), 'output')
    if not isdir(output_dir):
        os.mkdir(output_dir, 0o755)
    return join(output_dir, filename)