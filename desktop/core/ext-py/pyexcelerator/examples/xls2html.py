#!/usr/bin/env python
# -*- coding: windows-1251 -*-
# Copyright (C) 2005 Kiseliov Roman

__rev_id__ = """$Id: xls2html.py,v 1.1 2005/05/19 09:27:42 rvk Exp $"""


from pyExcelerator import *
import sys

me, args = sys.argv[0], sys.argv[1:]


if args:
    for arg in args:
        print >>sys.stderr, 'extracting data from', arg
        print '<html>'
        for sheet_name, values in parse_xls(arg, 'cp1251'): # parse_xls(arg) -- default encoding
            matrix = [[]]
            print 'Sheet = "%s"' % sheet_name.encode('cp1251', 'backslashreplace')
            print '<table border="2" cellpadding="1" cellspacing="1" >'

            for row_idx, col_idx in sorted(values.keys()):
                v = values[(row_idx, col_idx)]
                if isinstance(v, unicode):
                    v = v.encode('cp1251', 'backslashreplace')
                else:
                    v = str(v)
                last_row, last_col = len(matrix), len(matrix[-1])
                while last_row < row_idx:
                    matrix.extend([[]])
                    last_row = len(matrix)

                while last_col < col_idx:
                    matrix[-1].extend([''])
                    last_col = len(matrix[-1])

                matrix[-1].extend([v])
                    
            for row in matrix:
                print '<tr>'
                for col in row:
                    print '<td> %s </td>' % col
                print '</tr>'

            print '</table>'
        print '</html>'

else:
    print 'usage: %s (inputfile)+' % me

