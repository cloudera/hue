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


__rev_id__ = """$Id: Column.py,v 1.4 2005/07/20 07:24:11 rvk Exp $"""


import Style
from BIFFRecords import ColInfoRecord
from Deco import *
from Worksheet import Worksheet


class Column(object):
    @accepts(object, int, Worksheet)
    def __init__(self, indx, parent_sheet):
        self.__index = indx
        self.__parent = parent_sheet
        self.__parent_wb = parent_sheet.get_parent()
        self.__xf_index = 0x0F
        
        self.width = 0x0B92
        self.hidden = 0
        self.level = 0
        self.collapse = 0


    def get_biff_record(self):
        options =  (self.hidden & 0x01) << 0
        options |= (self.level & 0x07) << 8
        options |= (self.collapse & 0x01) << 12
        
        return ColInfoRecord(self.__index, self.__index, self.width, self.__xf_index, options).get()
        
        
    @accepts(object, Style.XFStyle)
    def set_style(self, style):
        # self.__adjust_height(style)
        self.__xf_index = self.__parent_wb.add_style(style)        
        

    def get_index(self):
        return self.__index
        
