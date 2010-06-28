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


__rev_id__ = """$Id: ImportXLS.py,v 1.6 2005/10/26 07:44:24 rvk Exp $"""


import UnicodeUtils
import CompoundDoc
import ExcelMagic
from struct import pack, unpack


def parse_xls(filename, encoding = None):
    
    ##########################################################################

    def process_BOUNDSHEET(biff8, rec_data):
        sheet_stream_pos, visibility, sheet_type = unpack('<I2B', rec_data[:6])
        sheet_name = rec_data[6:]

        if biff8:
            chars_num, options = unpack('2B', sheet_name[:2])
            
            chars_start = 2
            runs_num = 0
            asian_phonetic_size = 0

            result = ''

            compressed = (options & 0x01) == 0
            has_asian_phonetic = (options & 0x04) != 0
            has_format_runs = (options & 0x08) != 0

            if has_format_runs:
                runs_num , = unpack('<H', sheet_name[chars_start:chars_start+2])
                chars_start += 2
            if has_asian_phonetic:
                asian_phonetic_size , = unpack('<I', sheet_name[chars_start:chars_start+4])
                chars_start += 4

            if compressed:
                chars_end = chars_start + chars_num
                result = sheet_name[chars_start:chars_end].decode('latin_1', 'replace')
            else:
                chars_end = chars_start + 2*chars_num
                result = sheet_name[chars_start:chars_end].decode('utf_16_le', 'replace')
            
            tail_size = 4*runs_num + asian_phonetic_size
        else:
            result = sheet_name[1:].decode(encoding, 'replace')
        
        return result


    def unpack2str(biff8, label_name): # 2 bytes length str
        if biff8:
            chars_num, options = unpack('<HB', label_name[:3])
            
            chars_start = 3
            runs_num = 0
            asian_phonetic_size = 0

            result = ''

            compressed = (options & 0x01) == 0
            has_asian_phonetic = (options & 0x04) != 0
            has_format_runs = (options & 0x08) != 0

            if has_format_runs:
                runs_num , = unpack('<H', label_name[chars_start:chars_start+2])
                chars_start += 2
            if has_asian_phonetic:
                asian_phonetic_size , = unpack('<I', label_name[chars_start:chars_start+4])
                chars_start += 4

            if compressed:
                chars_end = chars_start + chars_num
                result = label_name[chars_start:chars_end].decode('latin_1', 'replace')
            else:
                chars_end = chars_start + 2*chars_num
                result = label_name[chars_start:chars_end].decode('utf_16_le', 'replace')
            
            tail_size = 4*runs_num + asian_phonetic_size
        else:
            result = label_name[2:].decode(encoding, 'replace')

        return result


    def process_LABEL(biff8, rec_data):
        row_idx, col_idx, xf_idx = unpack('<3H', rec_data[:6])
        label_name = rec_data[6:]
        result = unpack2str(biff8, label_name)
        return (row_idx, col_idx, result)


    def process_LABELSST(rec_data):
        row_idx, col_idx, xf_idx, sst_idx = unpack('<3HI', rec_data)
        return (row_idx, col_idx, sst_idx)


    def process_RSTRING(biff8, rec_data):
        if biff8:
            return process_LABEL(biff8, rec_data)
        else:
            row_idx, col_idx, xf_idx, length = unpack('<4H', rec_data[:8])
            result = rec_data[8:8+length].decode(encoding, 'replace')

        return (row_idx, col_idx, result)
        

    def decode_rk(encoded):
        b0, b1, b2, b3 = unpack('4B', encoded)
        is_multed_100 = (b0 & 0x01) != 0
        is_integer = (b0 & 0x02) != 0

        if is_integer:
            result , = unpack('<i', encoded)
            result >>= 2
        else:
            ieee754 = struct.pack('8B', 0, 0, 0, 0, b0 & 0xFC, b1, b2, b3)
            result , = unpack('<d', ieee754)
        if is_multed_100:
            result /= 100.0
        
        return result


    def process_RK(rec_data):
        row_idx, col_idx, xf_idx, encoded = unpack('<3H4s', rec_data)
        result = decode_rk(encoded)
        return (row_idx, col_idx, result)


    def process_MULRK(rec_data):
        row_idx, first_col_idx = unpack('<2H', rec_data[:4])
        last_col_idx , = unpack('<H', rec_data[-2:])
        xf_rk_num = last_col_idx - first_col_idx + 1

        results = []
        for i in range(xf_rk_num):
            xf_idx, encoded = unpack('<H4s', rec_data[4+6*i : 4+6*(i+1)])
            results.append(decode_rk(encoded))

        return zip([row_idx]*xf_rk_num, range(first_col_idx, last_col_idx+1), results)


    def process_NUMBER(rec_data):
        row_idx, col_idx, xf_idx, result = unpack('<3Hd', rec_data)
        return (row_idx, col_idx, result)

    
    def process_SST(rec_data, sst_continues):
        # 0x00FC
        total_refs, total_str = unpack('<2I', rec_data[:8])
        #print total_refs, str_num

        pos = 8
        curr_block = rec_data
        curr_block_num = -1
        curr_str_num = 0
        SST = {}

        while curr_str_num < total_str:
            if pos >= len(curr_block):
                curr_block_num += 1
                curr_block = sst_continues[curr_block_num]
                pos = 0

            chars_num, options = unpack('<HB', curr_block[pos:pos+3])
            #print chars_num, options
            pos += 3

            asian_phonetic_size = 0
            runs_num = 0
            has_asian_phonetic = (options & 0x04) != 0
            has_format_runs = (options & 0x08) != 0
            if has_format_runs:
                runs_num , = unpack('<H', curr_block[pos:pos+2])
                pos += 2
            if has_asian_phonetic:
                asian_phonetic_size , = unpack('<I', curr_block[pos:pos+4])
                pos += 4

            curr_char = 0
            result = ''
            while curr_char < chars_num:
                if pos >= len(curr_block):
                    curr_block_num += 1
                    curr_block = sst_continues[curr_block_num]
                    options = ord(curr_block[0])
                    pos = 1
                #print curr_block_num

                compressed = (options & 0x01) == 0
                if compressed:
                    chars_end = pos + chars_num - curr_char
                else:
                    chars_end = pos + 2*(chars_num - curr_char)
                #print compressed, has_asian_phonetic, has_format_runs

                splitted = chars_end > len(curr_block)
                if splitted:
                    chars_end = len(curr_block)
                #print splitted, curr_char, pos, chars_end, repr(curr_block[pos:chars_end])

                if compressed:
                    result += curr_block[pos:chars_end].decode('latin_1', 'replace')
                else:
                    result += curr_block[pos:chars_end].decode('utf_16_le', 'replace')

                pos = chars_end
                curr_char = len(result)
            # end while

            # TODO: handle spanning format runs over CONTINUE blocks ???
            tail_size = 4*runs_num + asian_phonetic_size
            if len(curr_block) < pos + tail_size:
                pos = pos + tail_size - len(curr_block)
                curr_block_num += 1
                curr_block = sst_continues[curr_block_num]
            else:
                pos += tail_size

            #print result.encode('cp866')

            SST[curr_str_num] = result
            curr_str_num += 1

        return SST


    #####################################################################################
    
    import struct

    encodings = {
        0x016F: 'ascii',     #ASCII
        0x01B5: 'cp437',     #IBM PC CP-437 (US)
        0x02D0: 'cp720',     #IBM PC CP-720 (OEM Arabic)
        0x02E1: 'cp737',     #IBM PC CP-737 (Greek)
        0x0307: 'cp775',     #IBM PC CP-775 (Baltic)
        0x0352: 'cp850',     #IBM PC CP-850 (Latin I)
        0x0354: 'cp852',     #IBM PC CP-852 (Latin II (Central European))
        0x0357: 'cp855',     #IBM PC CP-855 (Cyrillic)
        0x0359: 'cp857',     #IBM PC CP-857 (Turkish)
        0x035A: 'cp858',     #IBM PC CP-858 (Multilingual Latin I with Euro)
        0x035C: 'cp860',     #IBM PC CP-860 (Portuguese)
        0x035D: 'cp861',     #IBM PC CP-861 (Icelandic)
        0x035E: 'cp862',     #IBM PC CP-862 (Hebrew)
        0x035F: 'cp863',     #IBM PC CP-863 (Canadian (French))
        0x0360: 'cp864',     #IBM PC CP-864 (Arabic)
        0x0361: 'cp865',     #IBM PC CP-865 (Nordic)
        0x0362: 'cp866',     #IBM PC CP-866 (Cyrillic (Russian))
        0x0365: 'cp869',     #IBM PC CP-869 (Greek (Modern))
        0x036A: 'cp874',     #Windows CP-874 (Thai)
        0x03A4: 'cp932',     #Windows CP-932 (Japanese Shift-JIS)
        0x03A8: 'cp936',     #Windows CP-936 (Chinese Simplified GBK)
        0x03B5: 'cp949',     #Windows CP-949 (Korean (Wansung))
        0x03B6: 'cp950',     #Windows CP-950 (Chinese Traditional BIG5)
        0x04B0: 'utf_16_le', #UTF-16 (BIFF8)
        0x04E2: 'cp1250',    #Windows CP-1250 (Latin II) (Central European)
        0x04E3: 'cp1251',    #Windows CP-1251 (Cyrillic)
        0x04E4: 'cp1252',    #Windows CP-1252 (Latin I) (BIFF4-BIFF7)
        0x04E5: 'cp1253',    #Windows CP-1253 (Greek)
        0x04E6: 'cp1254',    #Windows CP-1254 (Turkish)
        0x04E7: 'cp1255',    #Windows CP-1255 (Hebrew)
        0x04E8: 'cp1256',    #Windows CP-1256 (Arabic)
        0x04E9: 'cp1257',    #Windows CP-1257 (Baltic)
        0x04EA: 'cp1258',    #Windows CP-1258 (Vietnamese)
        0x0551: 'cp1361',    #Windows CP-1361 (Korean (Johab))
        0x2710: 'mac_roman', #Apple Roman
        0x8000: 'mac_roman', #Apple Roman
        0x8001: 'cp1252'     #Windows CP-1252 (Latin I) (BIFF2-BIFF3)
    }

    biff8 = True
    SST = {}
    sheets = []
    sheet_names = []
    values = {}
    ws_num = 0
    BOFs = 0
    EOFs = 0

    # Inside MS Office document looks like filesystem
    # We need extract stream named 'Workbook' or 'Book'
    ole_streams = CompoundDoc.Reader(filename).STREAMS

    if 'Workbook' in ole_streams:
        workbook_stream = ole_streams['Workbook']
    elif 'Book' in ole_streams:
        workbook_stream = ole_streams['Book']
    else:
        raise Exception, 'No workbook stream in file.'

    workbook_stream_len = len(workbook_stream)
    stream_pos = 0
    
    # Excel's method of data storing is based on 
    # ancient technology "TLV" (Type, Length, Value).
    # In addition, if record size grows to some limit
    # Excel writes CONTINUE records
    while stream_pos < workbook_stream_len and EOFs <= ws_num:
        rec_id, data_size = unpack('<2H', workbook_stream[stream_pos:stream_pos+4])
        stream_pos += 4
        
        rec_data = workbook_stream[stream_pos:stream_pos+data_size]
        stream_pos += data_size

        if rec_id == 0x0809: # BOF
            #print 'BOF', 
            BOFs += 1
            ver, substream_type = unpack('<2H', rec_data[:4])
            if substream_type == 0x0005:
                # workbook global substream
                biff8 = ver >= 0x0600
            elif substream_type == 0x0010:
                # worksheet substream
                pass
            else: # skip chart stream or unknown stream
            # stream offsets may be used from BOUNDSHEET record
                rec_id, data_size = unpack('<2H', workbook_stream[stream_pos:stream_pos+4])
                while rec_id != 0x000A: # EOF
                    #print 'SST CONTINUE'
                    stream_pos += 4
                    stream_pos += data_size
                    rec_id, data_size = unpack('<2H', workbook_stream[stream_pos:stream_pos+4])
            #print 'BIFF8 == ', biff8
        elif rec_id == 0x000A: # EOF
            #print 'EOF'
            if BOFs > 1:
                sheets.extend([values])
                values = {}
            EOFs += 1
        elif rec_id == 0x0042: # CODEPAGE
            cp ,  = unpack('<H', rec_data)
            #print 'CODEPAGE', hex(cp)
            if not encoding:
                encoding = encodings[cp]
            #print encoding
        elif rec_id == 0x0085: # BOUNDSHEET
            #print 'BOUNDSHEET',
            ws_num += 1
            b = process_BOUNDSHEET(biff8, rec_data)
            sheet_names.extend([b])
            #print b.encode('cp866')
        elif rec_id == 0x00FC: # SST
            #print 'SST'
            sst_data = rec_data
            sst_continues = []
            rec_id, data_size = unpack('<2H', workbook_stream[stream_pos:stream_pos+4])
            while rec_id == 0x003C: # CONTINUE
                #print 'SST CONTINUE'
                stream_pos += 4
                rec_data = workbook_stream[stream_pos:stream_pos+data_size]
                sst_continues.extend([rec_data])
                stream_pos += data_size
                rec_id, data_size = unpack('<2H', workbook_stream[stream_pos:stream_pos+4])
            SST = process_SST(sst_data, sst_continues)
        elif rec_id == 0x00FD: # LABELSST
            #print 'LABELSST',
            r, c, i = process_LABELSST(rec_data)
            values[(r, c)] = SST[i]
            #print r, c, SST[i].encode('cp866')
        elif rec_id == 0x0204: # LABEL
            #print 'LABEL',
            r, c, b = process_LABEL(biff8, rec_data)
            values[(r, c)] = b
            #print r, c, b.encode('cp866')
        elif rec_id == 0x00D6: # RSTRING
            #print 'RSTRING',
            r, c, b = process_RSTRING(biff8, rec_data)
            values[(r, c)] = b
            #print r, c, b.encode('cp866')
        elif rec_id == 0x027E: # RK
            #print 'RK',
            r, c, b = process_RK(rec_data)
            values[(r, c)] = b
            #print r, c, b
        elif rec_id == 0x00BD: # MULRK
            #print 'MULRK',
            for r, c, b in process_MULRK(rec_data):
                values[(r, c)] = b
            #print r, c, b
        elif rec_id == 0x0203: # NUMBER
            #print 'NUMBER',
            r, c, b = process_NUMBER(rec_data)
            values[(r, c)] = b
            #print r, c, b
        elif rec_id == 0x0006: # FORMULA
            #print 'FORMULA',
            r, c, x = unpack('<3H', rec_data[0:6])
            if rec_data[12] == '\xFF' and rec_data[13] == '\xFF':
                if rec_data[6] == '\x00':
                    got_str = False
                    if ord(rec_data[14]) & 8:
                        # part of shared formula
                        rec_id, data_size = unpack('<2H', workbook_stream[stream_pos:stream_pos+4])
                        stream_pos += 4                      
                        rec_data = workbook_stream[stream_pos:stream_pos+data_size]
                        stream_pos += data_size
                        if rec_id == 0x0207: # STRING
                            got_str = True
                        elif rec_id not in (0x0221, 0x04BC, 0x0236, 0x0037, 0x0036):
                            raise Exception("Expected ARRAY, SHRFMLA, TABLEOP* or STRING record")
                    if not got_str:
                        rec_id, data_size = unpack('<2H', workbook_stream[stream_pos:stream_pos+4])
                        stream_pos += 4                      
                        rec_data = workbook_stream[stream_pos:stream_pos+data_size]
                        stream_pos += data_size
                        if rec_id != 0x0207: # STRING
                            raise Exception("Expected STRING record")
                    values[(r, c)] = unpack2str(biff8, rec_data)
                elif rec_data[6] == '\x01':
                    # boolean 
                    v = ord(rec_data[8])
                    values[(r, c)] = bool(v)
                elif rec_data[6] == '\x02':
                    # error
                    v = ord(rec_data[8])
                    if v in ExcelMagic.error_msg_by_code:
                        values[(r, c)] = ExcelMagic.error_msg_by_code[v]
                    else:
                        values[(r, c)] = u'#UNKNOWN ERROR!'
                elif rec_data[6] == '\x03':
                    # empty
                    values[(r, c)] = u''
                else:
                    raise Exception("Unknown value for formula result")
            else:
                # 64-bit float
                d, = unpack("<d", rec_data[6:14])
                values[(r, c)] = d

    encoding = None
    return zip(sheet_names, sheets)
