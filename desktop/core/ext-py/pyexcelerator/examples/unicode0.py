#!/usr/bin/env python
# -*- coding: windows-1251 -*-
# Copyright (C) 2005 Kiseliov Roman
__rev_id__ = """$Id: unicode0.py,v 1.1 2005/03/27 12:47:06 rvk Exp $"""


from pyExcelerator import *

w = Workbook()
ws1 = w.add_sheet('cp1251')

UnicodeUtils.DEFAULT_ENCODING = 'cp1251'
ws1.write(0, 0, 'Оля')

w.save('unicode0.xls')

