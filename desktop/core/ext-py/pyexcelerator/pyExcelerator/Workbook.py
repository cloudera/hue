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
Record Order in BIFF8
  Workbook Globals Substream
      BOF Type = workbook globals
      Interface Header
      MMS
      Interface End
      WRITEACCESS
      CODEPAGE
      DSF
      TABID
      FNGROUPCOUNT
      Workbook Protection Block
            WINDOWPROTECT
            PROTECT
            PASSWORD
            PROT4REV
            PROT4REVPASS
      BACKUP
      HIDEOBJ 
      WINDOW1 
      DATEMODE 
      PRECISION
      REFRESHALL
      BOOKBOOL 
      FONT +
      FORMAT *
      XF +
      STYLE +
    ? PALETTE
      USESELFS
    
      BOUNDSHEET +
    
      COUNTRY 
    ? Link Table 
      SST 
      ExtSST
      EOF
'''


__rev_id__ = """$Id: Workbook.py,v 1.5 2005/10/26 07:44:24 rvk Exp $"""


import BIFFRecords
import Style
from Deco import accepts, returns


class Workbook(object):

    macros = {
        'Consolidate_Area' : 0x00,
        'Auto_Open' : 0x01,
        'Auto_Close' : 0x02,
        'Extract' : 0x03,
        'Database' : 0x04,
        'Criteria' : 0x05,
        'Print_Area' : 0x06,
        'Print_Titles' : 0x07, # in the docs it says Pint_Titles, I think its a mistake
        'Recorder' : 0x08,
        'Data_Form' : 0x09,
        'Auto_Activate' : 0x0A,
        'Auto_Deactivate' : 0x0B,
        'Sheet_Title' : 0x0C,
        '_FilterDatabase' : 0x0D,
    }

    #################################################################
    ## Constructor
    #################################################################
    @accepts(object)
    def __init__(self):
        self.__owner = 'None'       
        self.__country_code = 0x07 
        self.__wnd_protect = 0
        self.__obj_protect = 0
        self.__protect = 0        
        self.__backup_on_save = 0
        # for WINDOW1 record
        self.__hpos_twips = 0x01E0
        self.__vpos_twips = 0x005A
        self.__width_twips = 0x3FCF
        self.__height_twips = 0x2A4E
        
        self.__active_sheet = 0
        self.__first_tab_index = 0
        self.__selected_tabs = 0x01
        self.__tab_width_twips = 0x0258
        
        self.__wnd_hidden = 0
        self.__wnd_mini = 0
        self.__hscroll_visible = 1
        self.__vscroll_visible = 1
        self.__tabs_visible = 1

        self.__styles = Style.StyleCollection()
         
        self.__dates_1904 = 0
        self.__use_cell_values = 1
        
        self.__sst = BIFFRecords.SharedStringTable()
        
        self.__worksheets = []
        self.__names = []
        self.__refs = []

    #################################################################
    ## Properties, "getters", "setters"
    #################################################################

    @accepts(object, str)
    def set_owner(self, value):
        self.__owner = value

    def get_owner(self):
        return self.__owner

    owner = property(get_owner, set_owner)

    #################################################################

    @accepts(object, int)
    def set_country_code(self, value):
        self.__country_code = value

    def get_country_code(self):
        return self.__country_code

    country_code = property(get_country_code, set_country_code)

    #################################################################

    @accepts(object, bool)
    def set_wnd_protect(self, value):
        self.__wnd_protect = int(value)

    def get_wnd_protect(self):
        return bool(self.__wnd_protect)

    wnd_protect = property(get_wnd_protect, set_wnd_protect)

    #################################################################

    @accepts(object, bool)
    def set_obj_protect(self, value):
        self.__obj_protect = int(value)

    def get_obj_protect(self):
        return bool(self.__obj_protect)

    obj_protect = property(get_obj_protect, set_obj_protect)

    #################################################################

    @accepts(object, bool)
    def set_protect(self, value):
        self.__protect = int(value)

    def get_protect(self):
        return bool(self.__protect)

    protect = property(get_protect, set_protect)
    
    #################################################################

    @accepts(object, bool)
    def set_backup_on_save(self, value):
        self.__backup_on_save = int(value)

    def get_backup_on_save(self):
        return bool(self.__backup_on_save)

    backup_on_save = property(get_backup_on_save, set_backup_on_save)

    #################################################################

    @accepts(object, int)
    def set_hpos(self, value):
        self.__hpos_twips = value & 0xFFFF

    def get_hpos(self):
        return self.__hpos_twips

    hpos = property(get_hpos, set_hpos)

    #################################################################

    @accepts(object, int)
    def set_vpos(self, value):
        self.__vpos_twips = value & 0xFFFF

    def get_vpos(self):
        return self.__vpos_twips

    vpos = property(get_vpos, set_vpos)

    #################################################################

    @accepts(object, int)
    def set_width(self, value):
        self.__width_twips = value & 0xFFFF

    def get_width(self):
        return self.__width_twips

    width = property(get_width, set_width)

    #################################################################

    @accepts(object, int)
    def set_height(self, value):
        self.__height_twips = value & 0xFFFF

    def get_height(self):
        return self.__height_twips

    height = property(get_height, set_height)

    #################################################################

    @accepts(object, int)
    def set_active_sheet(self, value):
        self.__active_sheet = value & 0xFFFF
        self.__first_tab_index = self.__active_sheet

    def get_active_sheet(self):
        return self.__active_sheet

    active_sheet = property(get_active_sheet, set_active_sheet)

    #################################################################

    @accepts(object, int)
    def set_tab_width(self, value):
        self.__tab_width_twips = value & 0xFFFF

    def get_tab_width(self):
        return self.__tab_width_twips

    tab_width = property(get_tab_width, set_tab_width)

    #################################################################

    @accepts(object, bool)
    def set_wnd_visible(self, value):
        self.__wnd_hidden = int(not value)

    def get_wnd_visible(self):
        return not bool(self.__wnd_hidden)

    wnd_visible = property(get_wnd_visible, set_wnd_visible)

    #################################################################

    @accepts(object, bool)
    def set_wnd_mini(self, value):
        self.__wnd_mini = int(value)

    def get_wnd_mini(self):
        return bool(self.__wnd_mini)

    wnd_mini = property(get_wnd_mini, set_wnd_mini)

    #################################################################

    @accepts(object, bool)
    def set_hscroll_visible(self, value):
        self.__hscroll_visible = int(value)

    def get_hscroll_visible(self):
        return bool(self.__hscroll_visible)

    hscroll_visible = property(get_hscroll_visible, set_hscroll_visible)

    #################################################################

    @accepts(object, bool)
    def set_vscroll_visible(self, value):
        self.__vscroll_visible = int(value)

    def get_vscroll_visible(self):
        return bool(self.__vscroll_visible)

    vscroll_visible = property(get_vscroll_visible, set_vscroll_visible)

    #################################################################

    @accepts(object, bool)
    def set_tabs_visible(self, value):
        self.__tabs_visible = int(value)

    def get_tabs_visible(self):
        return bool(self.__tabs_visible)

    tabs_visible = property(get_tabs_visible, set_tabs_visible)

    #################################################################

    @accepts(object, bool)
    def set_dates_1904(self, value):
        self.__dates_1904 = int(value)

    def get_dates_1904(self):
        return bool(self.__dates_1904)

    dates_1904 = property(get_dates_1904, set_dates_1904)

    #################################################################

    @accepts(object, bool)
    def set_use_cell_values(self, value):
        self.__use_cell_values = int(value)

    def get_use_cell_values(self):
        return bool(self.__use_cell_values)

    use_cell_values = property(get_use_cell_values, set_use_cell_values)

    #################################################################

    def get_default_style(self):
        return self.__styles.default_style

    default_style = property(get_default_style)

    ##################################################################
    ## Methods
    ##################################################################

    @accepts(object, (Style.XFStyle, type(None)))
    def add_style(self, style):
        return self.__styles.add(style)

    @accepts(object, (str, unicode))    
    def add_str(self, s):
        return self.__sst.add_str(s)
        
    @accepts(object, str)    
    def str_index(self, s):
        return self.__sst.str_index(s)
        
    @accepts(object, (str, unicode))    
    def add_sheet(self, sheetname):
        import Worksheet
        self.__worksheets.append(Worksheet.Worksheet(sheetname, self))
        return self.__worksheets[-1]

    @accepts(object, int)    
    def get_sheet(self, sheetnum):
        return self.__worksheets[sheetnum]
        
    @accepts(object, (int, unicode, str), int, int, int, int)    
    def print_area(self, sheetnum, rstart, rend, cstart, cend):
        import ExcelFormula
        from struct import pack
        if type(sheetnum) != int:
            for i, ws in enumerate(self.__worksheets):
                if ws.name == sheetnum: sheetnum = i+1
        
        options = 0x0020 # see Options Flags for Name record
        
        # FIXME: this is just a bad hack, need to use Formula to make the rpn
        #~ rpn = ExcelFormula.Formula('').rpn()[2:] # minus the size field
        rpn = pack('<BHHHHH', 0x3B, 0x0000, rstart, rend, cstart, cend)
        
        return self.__names.append(BIFFRecords.NameRecord(options, 0x00, self.macros['Print_Area'], sheetnum, rpn))

    ##################################################################
    ## BIFF records generation
    ##################################################################

    def __bof_rec(self):
        return BIFFRecords.Biff8BOFRecord(BIFFRecords.Biff8BOFRecord.BOOK_GLOBAL).get()

    def __eof_rec(self):
        return BIFFRecords.EOFRecord().get()
        
    def __intf_hdr_rec(self):
        return BIFFRecords.InteraceHdrRecord().get()

    def __intf_end_rec(self):
        return BIFFRecords.InteraceEndRecord().get()

    def __intf_mms_rec(self):
        return BIFFRecords.MMSRecord().get()

    def __write_access_rec(self):
        return BIFFRecords.WriteAccessRecord(self.__owner).get()

    def __wnd_protect_rec(self):
        return BIFFRecords.WindowProtectRecord(self.__wnd_protect).get()

    def __obj_protect_rec(self):
        return BIFFRecords.ObjectProtectRecord(self.__obj_protect).get()

    def __protect_rec(self):
        return BIFFRecords.ProtectRecord(self.__protect).get()

    def __password_rec(self):
        return BIFFRecords.PasswordRecord().get()

    def __prot4rev_rec(self):
        return BIFFRecords.Prot4RevRecord().get()

    def __prot4rev_pass_rec(self):
        return BIFFRecords.Prot4RevPassRecord().get()

    def __backup_rec(self):
        return BIFFRecords.BackupRecord(self.__backup_on_save).get()
        
    def __hide_obj_rec(self):
        return BIFFRecords.HideObjRecord().get()
        
    def __window1_rec(self):
        flags = 0
        flags |= (self.__wnd_hidden) << 0
        flags |= (self.__wnd_mini) << 1
        flags |= (self.__hscroll_visible) << 3
        flags |= (self.__vscroll_visible) << 4
        flags |= (self.__tabs_visible) << 5
        
        return BIFFRecords.Window1Record(self.__hpos_twips, self.__vpos_twips, 
                                self.__width_twips, self.__height_twips, 
                                flags,
                                self.__active_sheet, self.__first_tab_index, 
                                self.__selected_tabs, self.__tab_width_twips).get()
        
    def __codepage_rec(self):
        return BIFFRecords.CodepageBiff8Record().get()
        
    def __country_rec(self):
        return BIFFRecords.CountryRecord(self.__country_code, self.__country_code).get()
        
    def __dsf_rec(self):
        return BIFFRecords.DSFRecord().get()
        
    def __tabid_rec(self):
        return BIFFRecords.TabIDRecord(len(self.__worksheets)).get()
        
    def __fngroupcount_rec(self):
        return BIFFRecords.FnGroupCountRecord().get()
        
    def __datemode_rec(self):
        return BIFFRecords.DateModeRecord(self.__dates_1904).get()        

    def __precision_rec(self):
        return BIFFRecords.PrecisionRecord(self.__use_cell_values).get()         

    def __refresh_all_rec(self):
        return BIFFRecords.RefreshAllRecord().get()        

    def __bookbool_rec(self):
        return BIFFRecords.BookBoolRecord().get()         

    def __all_fonts_num_formats_xf_styles_rec(self):
        return self.__styles.get_biff_data()

    def __palette_rec(self):
        result = ''
        return result
        
    def __useselfs_rec(self):
        return BIFFRecords.UseSelfsRecord().get()
        
    def __names_rec(self):
        name_records = ''
        for n in self.__names:
            name_records += n.get()
        return name_records
        
    def __boundsheets_rec(self, data_len_before, data_len_after, sheet_biff_lens):
        #  .................................  
        # BOUNDSEHEET0
        # BOUNDSEHEET1
        # BOUNDSEHEET2
        # ..................................
        # WORKSHEET0
        # WORKSHEET1
        # WORKSHEET2
        boundsheets_len = 0
        for sheet in self.__worksheets:
            boundsheets_len += len(BIFFRecords.BoundSheetRecord(0x00L, sheet.hidden, sheet.name).get())
        
        start = data_len_before + boundsheets_len + data_len_after
        
        result = ''
        for sheet_biff_len,  sheet in zip(sheet_biff_lens, self.__worksheets):
            result += BIFFRecords.BoundSheetRecord(start, sheet.hidden, sheet.name).get()
            start += sheet_biff_len            
        return result

    def __all_links_rec(self):
        supbook_records = ''
        #~ supbook_records += BIFFRecords.AddInFunctionSupBookRecord(len(self.__worksheets)).get()
        supbook_records += BIFFRecords.InternalReferenceSupBookRecord(len(self.__worksheets)).get()
        #~ supbook_records += BIFFRecords.ExternalReferenceSupBookRecord(len(self.__worksheets)).get()
        externsheet_record = BIFFRecords.ExternSheetRecord(self.__refs).get()
        return supbook_records + externsheet_record
        
    def __sst_rec(self):
        return self.__sst.get_biff_record()
        
    def __ext_sst_rec(self, abs_stream_pos):
        return ''
        #return BIFFRecords.ExtSSTRecord(abs_stream_pos, self.sst_record.str_placement,
        #self.sst_record.portions_len).get()

    def get_biff_data(self):
        before = ''
        before += self.__bof_rec()
        before += self.__intf_hdr_rec()
        before += self.__intf_mms_rec()
        before += self.__intf_end_rec()
        before += self.__write_access_rec()
        before += self.__codepage_rec()
        before += self.__dsf_rec() 
        before += self.__tabid_rec() 
        before += self.__fngroupcount_rec()
        #~ before += self.__names_rec()
        before += self.__wnd_protect_rec()
        before += self.__protect_rec()
        before += self.__obj_protect_rec()
        before += self.__password_rec()
        before += self.__prot4rev_rec()
        before += self.__prot4rev_pass_rec()
        before += self.__backup_rec()        
        before += self.__hide_obj_rec()        
        before += self.__window1_rec()
        before += self.__datemode_rec()
        before += self.__precision_rec()
        before += self.__refresh_all_rec()
        before += self.__bookbool_rec()
        before += self.__all_fonts_num_formats_xf_styles_rec()
        before += self.__palette_rec()
        before += self.__useselfs_rec()
        
        country            = self.__country_rec()
        all_links          = self.__all_links_rec()
        names              = self.__names_rec()
        
        shared_str_table   = self.__sst_rec()        
        after = country + all_links + names + shared_str_table
        
        ext_sst = self.__ext_sst_rec(0) # need fake cause we need calc stream pos
        eof = self.__eof_rec()

        self.__worksheets[self.__active_sheet].selected = True
        sheets = ''
        sheet_biff_lens = []
        for sheet in self.__worksheets:
            data = sheet.get_biff_data()
            sheets += data
            sheet_biff_lens.append(len(data))
            
        bundlesheets = self.__boundsheets_rec(len(before), len(after)+len(ext_sst)+len(eof), sheet_biff_lens)       
       
        sst_stream_pos = len(before) + len(bundlesheets) + len(country)  + len(all_links) +  len(names)
        ext_sst = self.__ext_sst_rec(sst_stream_pos)           
        
        return before + bundlesheets + after + ext_sst + eof + sheets

    def save(self, filename):
        import CompoundDoc

        doc = CompoundDoc.XlsDoc()
        doc.save(filename, self.get_biff_data())

if __name__ == '__main__':
    wb = Workbook()
    f = file('workbook.bin', 'wb')
    f.write(wb.get_biff_data())
    f.close()
    