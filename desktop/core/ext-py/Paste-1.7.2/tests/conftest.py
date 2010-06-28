import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pkg_resources
pkg_resources.require('Paste')

import py
"""
Option = py.test.Config.Option
option = py.test.Config.addoptions(
    "Paste options",
    Option('-W',
           action="store_true", dest="raise_warnings",
           default=False,
           help="Turn warnings into errors"))

class SetupDirectory(py.test.collect.Directory):

    def __init__(self, *args, **kw):
        super(SetupDirectory, self).__init__(*args, **kw)
        if option.raise_warnings:
            import warnings
            warnings.filterwarnings('error')
        
Directory = SetupDirectory
"""
