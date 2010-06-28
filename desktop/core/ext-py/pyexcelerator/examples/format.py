#!/usr/bin/env python
# -*- coding: windows-1251 -*-
# Copyright (C) 2005 Kiseliov Roman

__rev_id__ = """$Id: format.py,v 1.3 2005/03/27 12:47:06 rvk Exp $"""


from pyExcelerator import *

style0 = XFStyle()
style0.font.name = 'Times New Roman'
style0.font.struck_out = True
style0.font.bold = True


wb = Workbook()
ws0 = wb.add_sheet('0')

ws0.write(1, 1, 'Test', style0)

for i in range(0, 0x53):
    style = XFStyle()
    style.font.name = 'Arial'
    style.font.colour_index = i
    style.font.outline = True
    style.borders.left = i

    ws0.write(i, 2, 'colour', style)
    ws0.write(i, 3, hex(i), style0)


wb.save('format.xls')