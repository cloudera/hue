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


'''
From BIFF8 on, strings are always stored using UTF-16LE  text encoding. The
character  array  is  a  sequence  of  16-bit  values4.  Additionally it is
possible  to  use  a  compressed  format, which omits the high bytes of all
characters, if they are all zero.

The following tables describe the standard format of the entire string, but
in many records the strings differ from this format. This will be mentioned
separately. It is possible (but not required) to store Rich-Text formatting
information  and  Asian  phonetic information inside a Unicode string. This
results  in  four  different  ways  to  store a string. The character array
is not zero-terminated.

The  string  consists  of  the  character count (as usual an 8-bit value or
a  16-bit value), option flags, the character array and optional formatting
information.  If the string is empty, sometimes the option flags field will
not occur. This is mentioned at the respective place.

Offset  Size    Contents
0       1 or 2  Length of the string (character count, ln)
1 or 2  1       Option flags:
                  Bit   Mask Contents
                  0     01H  Character compression (ccompr):
                               0 = Compressed (8-bit characters)
                               1 = Uncompressed (16-bit characters)
                  2     04H  Asian phonetic settings (phonetic):
                               0 = Does not contain Asian phonetic settings
                               1 = Contains Asian phonetic settings
                  3     08H  Rich-Text settings (richtext):
                               0 = Does not contain Rich-Text settings
                               1 = Contains Rich-Text settings
[2 or 3] 2      (optional, only if richtext=1) Number of Rich-Text formatting runs (rt)
[var.]   4      (optional, only if phonetic=1) Size of Asian phonetic settings block (in bytes, sz)
var.     ln or 
         2·ln   Character array (8-bit characters or 16-bit characters, dependent on ccompr)
[var.]   4·rt   (optional, only if richtext=1) List of rt formatting runs 
[var.]   sz     (optional, only if phonetic=1) Asian Phonetic Settings Block 
'''


__rev_id__ = """$Id: UnicodeUtils.py,v 1.4 2005/07/20 07:24:11 rvk Exp $"""


import struct


DEFAULT_ENCODING = 'cp1251'

def u2ints(ustr):
    ints = [ord(uchr) for uchr in ustr]
    return ints

def u2bytes(ustr):
    ints = u2ints(ustr)
    return struct.pack('<' + 'H'*len(ints), *ints)

def upack2(_str):
    try:
        ustr = u2bytes(unicode(_str, 'ascii'))
        return struct.pack('<HB', len(_str), 0) + _str    
    except:
        if isinstance(_str, unicode):
            ustr = u2bytes(_str)
        else:
            ustr = u2bytes(unicode(_str, DEFAULT_ENCODING))
        return struct.pack('<HB', len(_str), 1) + ustr

def upack1(_str):
    try:
        ustr = u2bytes(unicode(_str, 'ascii'))
        return struct.pack('BB', len(_str), 0) + _str    
    except:
        if isinstance(_str, unicode):
            ustr = u2bytes(_str)
        else:
            ustr = u2bytes(unicode(_str, DEFAULT_ENCODING))
        return struct.pack('BB', len(_str), 1) + ustr

if __name__ == '__main__':   
    f = file('out0.bin', 'wb')
    f.write(u2bytes('юникод: unicode'))
    f.close()

    f = file('out1.bin', 'wb')
    f.write(upack1('юникод: unicode'))
    f.close()

    f = file('out2.bin', 'wb')
    f.write(upack2('юникод: unicode'))
    f.close()



