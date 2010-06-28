#!/usr/bin/env python
# -*- coding: windows-1251 -*-
# Copyright (C) 2005 Kiseliov Roman

__rev_id__ = """$Id: xls2txt.py,v 1.1 2005/10/26 07:44:24 rvk Exp $"""


from pyExcelerator import *
import sys

me, args = sys.argv[0], sys.argv[1:]

if args:
    for arg in args:
        print >>sys.stderr, 'extracting data from', arg
        for sheet_name, values in parse_xls(arg, 'cp1251'): # parse_xls(arg) -- default encoding
            print 'Sheet = "%s"' % sheet_name.encode('cp866', 'backslashreplace')
            print '----------------'
            for row_idx, col_idx in sorted(values.keys()):
                v = values[(row_idx, col_idx)]
                if isinstance(v, unicode):
                    v = v.encode('cp866', 'backslashreplace')
                else:
                    v = `v`
                print '(%d, %d) =' % (row_idx, col_idx), v
            print '----------------'
else:
    print 'usage: %s (inputfile)+' % me

