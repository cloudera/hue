#!/usr/bin/env python
# -*- coding: windows-1251 -*-
# Copyright (C) 2005 Kiseliov Roman

from xlwt import *

w = Workbook()
ws = w.add_sheet('Image')
ws.insert_bitmap('python.bmp', 2, 2)

# Also works if you already have the image bitmap data in memory...
with open ("python.bmp", "r") as bmpfile:
    bmpdata = bmpfile.read()
    ws.insert_bitmap_data(bmpdata, 10, 2)

w.save('image.xls')
