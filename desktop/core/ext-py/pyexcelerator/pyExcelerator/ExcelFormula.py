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


__rev_id__ = """$Id: ExcelFormula.py,v 1.3 2005/08/11 08:53:48 rvk Exp $"""


import ExcelFormulaParser, ExcelFormulaLexer, ExcelMagic
import struct
from Deco import *
from antlr import ANTLRException

NoCalcs=0x00
RecalcAlways=0x01
CalcOnOpen=0x02
PartOfShareFormula=0x08

class ErrorCode(object):
    error_msg = dict([(i[1], i[0]) for i in ExcelMagic.error_msg_by_code.items()])
    
    def __init__(self, s):
        self.val = self.error_msg[s]
    
    def int(self): return self.val

class Formula(object):
    __slots__ = ["__init__", "text", "rpn", "default", "opts", "__s", "__parser", "__default", "__opts"]


    def __init__(self, s, default=None, opts=None):
        self.__default = default
        self.__opts = opts
        try:
            self.__s = s
            lexer = ExcelFormulaLexer.Lexer(s)
            self.__parser = ExcelFormulaParser.Parser(lexer)
            self.__parser.formula()
        except ANTLRException:
            raise Exception, "can't parse formula " + s

    def set_default(self, val):
        self.__default = val

    def get_default(self):
        return self.__default

    default = property(get_default, set_default)

    @accepts(object, int)
    def set_opts(self, value):
        assert (int(value) & ~(0x0b)) == 0, "Invalid bits set for opts (%s)"%hex(int(value))
        self.__opts = int(value)

    def get_opts(self):
        return self.__opts

    opts = property(get_opts, set_opts)

    def text(self):
        return self.__s

    def rpn(self):
        '''
        Offset    Size    Contents
        0         2       Size of the following formula data (sz)
        2         sz      Formula data (RPN token array)
        [2+sz]    var.    (optional) Additional data for specific tokens

        '''
        return struct.pack("<H", len(self.__parser.rpn)) + self.__parser.rpn

