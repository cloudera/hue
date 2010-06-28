#!/usr/bin/env python
# -*- coding: windows-1251 -*-
# Copyright (C) 2005 Kiseliov Roman
__rev_id__ = """$Id: row_styles_empty.py,v 1.3 2005/03/27 12:47:06 rvk Exp $"""


from pyExcelerator import *

w = Workbook()
ws = w.add_sheet('Hey, Dude')

for i in range(6, 80):
    fnt = Font()
    fnt.height = i*20
    style = XFStyle()
    style.font = fnt
    ws.row(i).set_style(style)
w.save('row_styles_empty.xls')
