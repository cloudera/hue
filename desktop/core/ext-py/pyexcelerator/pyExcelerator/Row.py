#!/usr/bin/env python
# -*- coding: windows-1251 -*-

#  Copyright (C) 2005 Roman V. Kiseliov
#  All rights reserved.
# 
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions
#  are met:
# 
#  1. Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
# 
#  2. Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in
#     the documentation and/or other materials provided with the
#     distribution.
# 
#  3. All advertising materials mentioning features or use of this
#     software must display the following acknowledgment:
#     "This product includes software developed by
#      Roman V. Kiseliov <roman@kiseliov.ru>."
# 
#  4. Redistributions of any form whatsoever must retain the following
#     acknowledgment:
#     "This product includes software developed by
#      Roman V. Kiseliov <roman@kiseliov.ru>."
# 
#  THIS SOFTWARE IS PROVIDED BY Roman V. Kiseliov ``AS IS'' AND ANY
#  EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#  PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL Roman V. Kiseliov OR
#  ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
#  NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
#  HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
#  STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
#  ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
#  OF THE POSSIBILITY OF SUCH DAMAGE.


__rev_id__ = """$Id: Row.py,v 1.6 2005/08/11 08:53:48 rvk Exp $"""


import BIFFRecords
from Deco import *
from Worksheet import Worksheet
import Style
import Cell
import ExcelFormula
import datetime as dt


class Row(object):
    __slots__ = ["__init__", 
                 "__adjust_height",
                 "__adjust_bound_col_idx",
                 "__excel_date_dt",
                 "get_height_in_pixels",
                 "set_style",
                 "get_xf_index",
                 "get_cells_count",
                 "get_min_col",
                 "get_max_col",
                 "get_str_count",
                 "get_row_biff_data",
                 "get_cells_biff_data",
                 "get_index",
                 "write",
                 "write_blanks",
                 # private variables
                 "__idx",
                 "__parent",
                 "__parent_wb",
                 "__cells",
                 "__min_col_idx",
                 "__max_col_idx",
                 "__total_str",
                 "__xf_index",
                 "__has_default_format",
                 "__has_default_height",
                 "__height",
                 "__height_in_pixels",
                 "__frmla_opts",
                 # public variables
                 "level",
                 "collapse",
                 "hidden",
                 "space_above",
                 "space_below",
                 "height",
                 "frmla_opts",]

    #################################################################
    ## Constructor
    #################################################################
    def __init__(self, index, parent_sheet):
        self.__idx = index
        self.__parent = parent_sheet
        self.__parent_wb = parent_sheet.get_parent()
        self.__cells = []
        self.__min_col_idx = 0
        self.__max_col_idx = 0
        self.__total_str = 0
        self.__xf_index = 0x0F
        self.__has_default_format = 0
        self.__has_default_height = 0x01
        self.__height = 0x00FF
        self.__height_in_pixels = 0x11
        self.__frmla_opts = self.__parent.frmla_opts
        
        self.level = 0
        self.collapse = 0
        self.hidden = 0
        self.space_above = 0
        self.space_below = 0


    def __adjust_height(self, style):
        twips = style.font.height
        points = float(twips)/20.0
        # Cell height in pixels can be calcuted by following approx. formula:
        # cell height in pixels = font height in points * 83/50 + 2/5
        # It works when screen resolution is 96 dpi 
        pix = int(round(points*83.0/50.0 + 2.0/5.0))
        if pix > self.__height_in_pixels:
            self.__height_in_pixels = pix


    def __adjust_bound_col_idx(self, *args):
        for arg in args:
            if arg < self.__min_col_idx:
                self.__min_col_idx = arg
            elif arg > self.__max_col_idx:
                self.__max_col_idx = arg

    def __excel_date_dt(self, date):
        if isinstance(date, dt.date) and (not isinstance(date, dt.datetime)):
            epoch = dt.date(1899, 12, 31)
        elif isinstance(date, dt.time):
            date = dt.datetime.combine(dt.datetime(1900, 1, 1), date)
            epoch = dt.datetime(1900, 1, 1, 0, 0, 0)
        else:
            epoch = dt.datetime(1899, 12, 31, 0, 0, 0)
        delta = date - epoch
        xldate = delta.days + float(delta.seconds) / (24*60*60)
        # Add a day for Excel's missing leap day in 1900
        if xldate > 59:
            xldate += 1
        return xldate

    def get_height_in_pixels(self):
        return self.__height_in_pixels


    @accepts(object, Style.XFStyle)
    def set_style(self, style):
        self.__adjust_height(style)
        self.__xf_index = self.__parent_wb.add_style(style)

            
    def get_xf_index(self):
        return self.__xf_index

    
    def get_cells_count(self):
        return len(self.__cells)

    
    def get_min_col(self):
        return self.__min_col_idx

        
    def get_max_col(self):
        return self.__max_col_idx

        
    def get_str_count(self):
        return self.__total_str


    def get_row_biff_data(self):
        height_options = (self.__height & 0x07FFF) 
        height_options |= (self.__has_default_height & 0x01) << 15

        options =  (self.level & 0x07) << 0
        options |= (self.collapse & 0x01) << 4
        options |= (self.hidden & 0x01) << 5
        options |= (0x00 & 0x01) << 6
        options |= (0x01 & 0x01) << 8
        if self.__xf_index != 0x0F:
            options |= (0x01 & 0x01) << 7
        else:
            options |= (0x00 & 0x01) << 7
        options |= (self.__xf_index & 0x0FFF) << 16 
        options |= (0x00 & self.space_above) << 28
        options |= (0x00 & self.space_below) << 29
        
        return BIFFRecords.RowRecord(self.__idx, self.__min_col_idx, self.__max_col_idx, height_options, options).get()                                              
                        

    def get_cells_biff_data(self):
        return ''.join([ cell.get_biff_data() for cell in self.__cells ])


    def get_index(self):
        return self.__idx


    def get_height(self):
        return self.__height

    def set_height(self, h):
        if h == None:
            self.__has_default_height = 0x01
        else: self.__height = h
    
    height = property(get_height, set_height)

    @accepts(object, int)
    def set_frmla_opts(self, value):
        assert (int(value) & ~(0x0b)) == 0, "Invalid bits set for frmla_opts (%s)"%hex(int(value))
        self.__frmla_opts = int(value)

    def get_frmla_opts(self):
        return self.__frmla_opts

    frmla_opts = property(get_frmla_opts, set_frmla_opts)

    @accepts(object, int, (str, unicode, int, long, float, dt.datetime, dt.time, dt.date, ExcelFormula.Formula), (Style.XFStyle, type(None)))
    def write(self, col, label, style):
        self.__adjust_height(style)
        self.__adjust_bound_col_idx(col)
        if isinstance(label, (str, unicode)):
            if len(label) > 0:
                self.__cells.extend([ Cell.StrCell(self, col, self.__parent_wb.add_style(style), self.__parent_wb.add_str(label)) ])
                self.__total_str += 1
            else:
                self.__cells.extend([ Cell.BlankCell(self, col, self.__parent_wb.add_style(style)) ])
        elif isinstance(label, (int, long, float)):
            self.__cells.extend([ Cell.NumberCell(self, col, self.__parent_wb.add_style(style), label) ])            
        elif isinstance(label, (dt.datetime, dt.time)):
            self.__cells.extend([ Cell.NumberCell(self, col, self.__parent_wb.add_style(style), self.__excel_date_dt(label)) ])
        else:
            self.__cells.extend([ Cell.FormulaCell(self, col, self.__parent_wb.add_style(style), label) ])

    @accepts(object, int, int, Style.XFStyle)                        
    def write_blanks(self, c1, c2, style):
        self.__adjust_height(style)
        self.__adjust_bound_col_idx(c1, c2)
        self.__cells.extend([ Cell.MulBlankCell(self, c1, c2, self.__parent_wb.add_style(style)) ])

        
        