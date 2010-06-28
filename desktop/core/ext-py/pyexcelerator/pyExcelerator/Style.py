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


__rev_id__ = """$Id: Style.py,v 1.4 2005/07/20 07:24:11 rvk Exp $"""


import Formatting
from BIFFRecords import *


_default_num_format = 'general'
_default_font = Formatting.Font()
_default_alignment = Formatting.Alignment()
_default_borders = Formatting.Borders()
_default_pattern = Formatting.Pattern()
_default_protection = Formatting.Protection()

class XFStyle(object):
    
    def __init__(self):
        self.num_format_str  = _default_num_format
        self.font            = _default_font.copy()
        self.alignment       = _default_alignment.copy()
        self.borders         = _default_borders.copy()
        self.pattern         = _default_pattern.copy()
        self.protection      = _default_protection.copy()

class StyleCollection(object):
    _std_num_fmt_list = [
            'general',
            '0',
            '0.00',
            '#,##0',
            '#,##0.00',
            '"$"#,##0_);("$"#,##',
            '"$"#,##0_);[Red]("$"#,##',
            '"$"#,##0.00_);("$"#,##',
            '"$"#,##0.00_);[Red]("$"#,##',
            '0%',
            '0.00%',
            '0.00E+00',
            '# ?/?',
            '# ??/??',
            'M/D/YY',
            'D-MMM-YY',
            'D-MMM',
            'MMM-YY',
            'h:mm AM/PM',
            'h:mm:ss AM/PM',
            'h:mm',
            'h:mm:ss',
            'M/D/YY h:mm',
            '_(#,##0_);(#,##0)',
            '_(#,##0_);[Red](#,##0)',
            '_(#,##0.00_);(#,##0.00)',
            '_(#,##0.00_);[Red](#,##0.00)',
            '_("$"* #,##0_);_("$"* (#,##0);_("$"* "-"_);_(@_)',
            '_(* #,##0_);_(* (#,##0);_(* "-"_);_(@_)',
            '_("$"* #,##0.00_);_("$"* (#,##0.00);_("$"* "-"??_);_(@_)',
            '_(* #,##0.00_);_(* (#,##0.00);_(* "-"??_);_(@_)',
            'mm:ss',
            '[h]:mm:ss',
            'mm:ss.0',
            '##0.0E+0',
            '@'   
    ]

    def __init__(self):
        self._fonts = {}
        self._fonts[Formatting.Font()] = 0
        self._fonts[Formatting.Font()] = 1
        self._fonts[Formatting.Font()] = 2
        self._fonts[Formatting.Font()] = 3
        # The font with index 4 is omitted in all BIFF versions
        self._fonts[Formatting.Font()] = 5
        
        self._num_formats = {}
        for fmtidx, fmtstr in zip(range(0, 23), StyleCollection._std_num_fmt_list[0:23]):
            self._num_formats[fmtstr] = fmtidx 
        for fmtidx, fmtstr in zip(range(37, 50), StyleCollection._std_num_fmt_list[23:]):
            self._num_formats[fmtstr] = fmtidx 

        self._xf = {}
        self.default_style = XFStyle()
        self._default_xf = self._add_style(self.default_style)[0]
        
    def add(self, style): 
        if style == None:
            return 0x10
        return self._add_style(style)[1]
    
    def _add_style(self, style):
        num_format_str = style.num_format_str
        if num_format_str in self._num_formats:
            num_format_idx = self._num_formats[num_format_str]
        else:
            num_format_idx = 163 + len(self._num_formats) - len(StyleCollection._std_num_fmt_list)
            self._num_formats[num_format_str] = num_format_idx
            
        font = style.font
        if font in self._fonts:
            font_idx = self._fonts[font]
        else:
            font_idx = len(self._fonts) + 1
            self._fonts[font] = font_idx
            
        xf = (font_idx, num_format_idx, style.alignment, style.borders, style.pattern, style.protection)
        
        if xf in self._xf:
            xf_index = self._xf[xf]
        else:
            xf_index = 0x10 + len(self._xf)
            self._xf[xf] = xf_index
            
        return xf, xf_index
        
    def get_biff_data(self):
        result = ''
        result += self._all_fonts()
        result += self._all_num_formats()
        result += self._all_cell_styles()
        result += self._all_styles()
        return result 
            
    def _all_fonts(self):
        result = ''
        i = sorted([(v, k) for k, v in self._fonts.items()])
        for font_idx, font in i:
            result += font.get_biff_record().get()
        return result
    
    def _all_num_formats(self):
        result = ''
        i = sorted([(v, k) for k, v in self._num_formats.items() if v>=163])
        for fmtidx, fmtstr in i:
            result += NumberFormatRecord(fmtidx, fmtstr).get()
        return result
    
    def _all_cell_styles(self):        
        result = ''
        for i in range(0, 16):
            result += XFRecord(self._default_xf, 'style').get()
            
        i = sorted([(v, k) for k, v in self._xf.items()])                            
        for xf_idx, xf in i:
            result += XFRecord(xf).get()
        return result
        
    def _all_styles(self):
        return StyleRecord().get()
        
if __name__ == '__main__':
    sc = StyleCollection()
    f = file('styles.bin', 'wb')
    f.write(sc.get_biff_data())
    f.close()

            