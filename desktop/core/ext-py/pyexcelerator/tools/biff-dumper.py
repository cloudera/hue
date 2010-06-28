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

__rev_id__ = """$Id: biff-dumper.py,v 1.5 2005/10/26 07:44:24 rvk Exp $"""


import Analyzer
from pyExcelerator import *
import sys
from struct import unpack


def print_bin_data(data):
    print
    i = 0
    while i < len(data):
        j = 0
        while (i < len(data)) and (j < 16):
            c = '0x%02X' % ord(data[i])
            sys.stdout.write(c)
            sys.stdout.write(' ')
            i += 1
            j += 1
        print
    if i == 0:
        print '<NO DATA>'


def print_ASCII_data(data):
    print
    i = 0
    while i < len(data):
        j = 0
        while (i < len(data)) and (j < 16):
            if data[i] < ' ':
                c = '.'
            else:
                c = data[i]
            sys.stdout.write(c)
            i += 1
            j += 1
        print
    if i == 0:
        print '<NO DATA>'


def main():
    if len(sys.argv) < 2:
        print 'no input files.'
        sys.exit(1)

    # Inside MS Office document looks like filesystem
    # We need extract stream named 'Workbook' or 'Book'
    ole_streams = CompoundDoc.Reader(sys.argv[1], True).STREAMS

    if 'Workbook' in ole_streams:
        workbook_stream = ole_streams['Workbook']
    elif 'Book' in ole_streams:
        workbook_stream = ole_streams['Book']
    else:
        raise Exception, 'No workbook stream in file.'

    wb_bin_data_len = len(workbook_stream)
    stream_pos = 0
    
    print 'workbook stream size 0x%X bytes '% len(workbook_stream)

    # Excel's method of data storing is based on 
    # ancient technology "TLV" (Type, Length, Value).
    # In addition, if record size grows to some limit
    # Excel writes CONTINUE records
    ws_num = 0
    EOFs = 0
    while stream_pos < len(workbook_stream) and EOFs <= ws_num:
        # header size == 4
        print 'stream position:', '0x%08X' % stream_pos
        header = workbook_stream[stream_pos:stream_pos+4]
        rec_id, data_size = unpack('<2H', header)
        print 'rec id:', '0x%04X' % rec_id
        print 'rec data size:', '0x%04X' % data_size
        stream_pos += 4
        rec_data = workbook_stream[stream_pos:stream_pos+data_size]
        stream_pos += data_size

        if rec_id == 0x000A:   # EOF 
            EOFs += 1
        elif rec_id == 0x0085: # BOUNDSHEET
            ws_num += 1
        
        if rec_id in Analyzer.all_records:
            rec_name, analyzer_func = Analyzer.all_records[rec_id]

            print 'rec name:', rec_name
            print 'rec data:',
            print_bin_data(rec_data)
            print 'ASCII data:',
            print_ASCII_data(rec_data)
            print 'analyzing...'
            analyzer_func(rec_data)
        else:
            print '<UNKNOWN RECORD>: rec_id == 0x%04X, size 0x%04X bytes' % (rec_id, data_size)
        print '---------------'


main()
