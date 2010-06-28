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


__rev_id__ = """$Id: ExcelFormulaLexer.py,v 1.4 2005/08/14 06:40:23 rvk Exp $"""


import sys
from antlr import EOF, CommonToken as Tok, TokenStream, TokenStreamException
import struct
import ExcelFormulaParser
from re import compile as recompile, match, LOCALE, UNICODE, IGNORECASE


int_const_pattern = recompile(r"\d+")
flt_const_pattern = recompile(r"\d*\.\d+(?:[Ee][+-]?\d+)?")
str_const_pattern = recompile(r'["][^"]*["]')
#range2d_pattern   = recompile(r"\$?[A-I]?[A-Z]\$?\d+:\$?[A-I]?[A-Z]\$?\d+")
ref2d_pattern     = recompile(r"\$?[A-I]?[A-Z]\$?\d+")
true_pattern      = recompile(r"TRUE", IGNORECASE)
false_pattern     = recompile(r"FALSE", IGNORECASE)
name_pattern      = recompile(r"[\.\w]+", LOCALE)

pattern_type_tuples = (
    (flt_const_pattern, ExcelFormulaParser.NUM_CONST),
    (int_const_pattern, ExcelFormulaParser.INT_CONST),
    (str_const_pattern, ExcelFormulaParser.STR_CONST),
#    (range2d_pattern  , ExcelFormulaParser.RANGE2D),
    (ref2d_pattern    , ExcelFormulaParser.REF2D),
    (true_pattern     , ExcelFormulaParser.TRUE_CONST),
    (false_pattern    , ExcelFormulaParser.FALSE_CONST),
    (name_pattern     , ExcelFormulaParser.NAME)
)


type_text_tuples = (
    (ExcelFormulaParser.NE, '<>'),
    (ExcelFormulaParser.LE, '<='),
    (ExcelFormulaParser.GE, '>='),
    (ExcelFormulaParser.EQ, '='),
    (ExcelFormulaParser.LT, '<'),
    (ExcelFormulaParser.GT, '>'),
    (ExcelFormulaParser.ADD, '+'),
    (ExcelFormulaParser.SUB, '-'),
    (ExcelFormulaParser.MUL, '*'),
    (ExcelFormulaParser.DIV, '/'),
    (ExcelFormulaParser.COLON, ':'),
    (ExcelFormulaParser.SEMICOLON, ';'),
    (ExcelFormulaParser.COMMA, ','),
    (ExcelFormulaParser.LP, '('),
    (ExcelFormulaParser.RP, ')'),
    (ExcelFormulaParser.CONCAT, '&'),
    (ExcelFormulaParser.PERCENT, '%'),
    (ExcelFormulaParser.POWER, '^')
)


class Lexer(TokenStream):
    def __init__(self, text):
        self._text = text[:]
        self._pos = 0
        self._line = 0


    def isEOF(self):
        return len(self._text) <= self._pos


    def rest(self):
        return self._text[self._pos:]


    def curr_ch(self):
        return self._text[self._pos]


    def next_ch(self, n = 1):
        self._pos += n


    def is_whitespace(self):
        return self.curr_ch() in " \t\n\r\f\v"


    def match_pattern(self, pattern, toktype):
        m = pattern.match(self._text[self._pos:])
        if m:
            start_pos = self._pos + m.start(0)
            end_pos = self._pos + m.end(0)
            tt = self._text[start_pos:end_pos]
            self._pos = end_pos
            return Tok(type = toktype, text = tt, col = start_pos + 1)
        else:
            return None


    def nextToken(self):
        # skip whitespace
        while not self.isEOF() and self.is_whitespace():
            self.next_ch()
        if self.isEOF():
            return Tok(type = EOF)
        # first, try to match token with more chars
        for ptt in pattern_type_tuples:
            t = self.match_pattern(*ptt);
            if t:
                return t
        # second, we want find short tokens
        for ty, te in type_text_tuples:
            if self.rest().startswith(te):
                self.next_ch(len(te))
                return Tok(type = ty, text = te, col = self._pos)
        # at this point, smth strange is happened
        raise TokenStreamException("Unknown char %s at %u col." % (self.curr_ch(), self._pos))


if __name__ == '__main__' :
    import locale
    locale.setlocale(locale.LC_ALL, 'russian')
    try:
        for t in Lexer('1+2+3+67.8678 + " @##$$$ klhkh kljhklhkl " + .58e-678*A1:B4 - 1lkjljlkjl3535порпор'):
            print t
    except TokenStreamException, e:
        print "error:", e
