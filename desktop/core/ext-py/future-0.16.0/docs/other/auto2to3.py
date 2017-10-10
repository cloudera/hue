#!/usr/bin/env python3
"""Wrapper to run 2to3 automatically at import time.

Usage:
  auto2to3 -m mypackage.main_module
  auto2to3 mypackage/script.py

By default, all modules imported from a subdirectory of the current
directory will be run through `2to3`.  To change this behavior, use the
`--package` or `--dir` flags to `auto2to3` to specify which packages or
directories contain Python 2 code that should be converted.

2to3 output is cached on disk between runs for speed.

Based on auto2to3.py by Georg Brandl:
http://dev.pocoo.org/hg/sandbox/file/tip/auto2to3.py
"""

import argparse
import os
import sys
import imp
import runpy
from io import StringIO
from pkgutil import ImpImporter, ImpLoader
import runpy
import sys
import tempfile

import lib2to3
from lib2to3.refactor import RefactoringTool, get_fixers_from_package

fixes = get_fixers_from_package('lib2to3.fixes')
rt = RefactoringTool(fixes)

PACKAGES = []
DIRS = []

def maybe_2to3(filename, modname=None):
    """Returns a python3 version of filename."""
    need_2to3 = False
    filename = os.path.abspath(filename)
    if any(filename.startswith(d) for d in DIRS):
        need_2to3 = True
    elif modname is not None and any(modname.startswith(p) for p in PACKAGES):
        need_2to3 = True
    if not need_2to3:
        return filename
    outfilename = '/_auto2to3_'.join(os.path.split(filename))
    if (not os.path.exists(outfilename) or
        os.stat(filename).st_mtime > os.stat(outfilename).st_mtime):
        try:
            with open(filename) as file:
                contents = file.read()
            contents = rt.refactor_docstring(contents, filename)
            tree = rt.refactor_string(contents, filename)
        except Exception as err:
            raise ImportError("2to3 couldn't convert %r" % filename)
        outfile = open(outfilename, 'wb')
        outfile.write(str(tree).encode('utf8'))
        outfile.close()
    return outfilename



class ToThreeImporter(ImpImporter):
    def find_module(self, fullname, path=None):
        # this duplicates most of ImpImporter.find_module
        subname = fullname.split(".")[-1]
        if subname != fullname and self.path is None:
            return None
        if self.path is None:
            path = None
        else:
            path = [os.path.realpath(self.path)]
        try:
            file, filename, etc = imp.find_module(subname, path)
        except ImportError:
            return None
        if file and etc[2] == imp.PY_SOURCE:
            outfilename = maybe_2to3(filename, modname=fullname)
            if outfilename != filename:
                file.close()
                filename = outfilename
                file = open(filename, 'rb')
        return ImpLoader(fullname, file, filename, etc)


# setup the hook
sys.path_hooks.append(ToThreeImporter)
for key in sys.path_importer_cache:
    if sys.path_importer_cache[key] is None:
        sys.path_importer_cache[key] = ToThreeImporter(key)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--package', action='append')
    parser.add_argument('--dir', action='append')
    parser.add_argument('-m', action='store', metavar='MODULE')
    args, rest = parser.parse_known_args()
    if args.package:
        PACKAGES.extend(args.package)
    if args.dir:
        DIRS.extend(os.path.abspath(d) for d in args.dir)
    if not PACKAGES and not DIRS:
        DIRS.append(os.getcwd())
    if args.m:
        sys.argv[1:] = rest
        runpy.run_module(args.m, run_name='__main__', alter_sys=True)
    elif rest:
        sys.argv = rest
        converted = maybe_2to3(rest[0])
        with open(converted) as f:
            new_globals = dict(__name__='__main__',
                               __file__=rest[0])
            exec(f.read(), new_globals)
    else:
        import code
        code.interact()

if __name__ == '__main__':
    main()
