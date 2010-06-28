#!/usr/bin/env python
# -*- coding: windows-1251 -*-
# Copyright (C) 2005 Kiseliov Roman
__rev_id__ = """$Id: mini.py,v 1.3 2005/03/27 12:47:06 rvk Exp $"""


from pyExcelerator import *

w = Workbook()
ws = w.add_sheet('Hey, Dude')
w.save('mini.xls')
