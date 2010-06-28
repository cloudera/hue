#!/usr/bin/env python
# -*- coding: windows-1251 -*-
# Copyright (C) 2005 Kiseliov Roman

__rev_id__ = """$Id: image.py,v 1.3 2005/03/27 12:47:06 rvk Exp $"""


from pyExcelerator import *

w = Workbook()
ws = w.add_sheet('Image')
ws.insert_bitmap('python.bmp', 2, 2)
ws.insert_bitmap('python.bmp', 10, 2)

w.save('image.xls')
