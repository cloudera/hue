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

__rev_id__ = """$Id: Analyzer.py,v 1.4 2005/05/12 06:51:17 rvk Exp $"""


# total 258 records in database
import struct

def analyze_1904_record(data):
    # 0x0022
    pass


def analyze_ADDIN_record(data):
    # 0x0087
    pass


def analyze_ADDMENU_record(data):
    # 0x00C2
    pass


def analyze_ARRAY_record(data):
    # 0x0021, 0x0221
    pass


def analyze_AUTOFILTER_record(data):
    # 0x009E
    pass


def analyze_AUTOFILTERINFO_record(data):
    # 0x009D
    pass


def analyze_BACKUP_record(data):
    # 0x0040
    pass


def analyze_BEGIN_record(data):
    # 0x1033
    pass


def analyze_BITMAP_record(data):
    # 0x00E9
    pass


def analyze_BLANK_record(data):
    # 0x0001, 0x0201
    pass


def analyze_BOF_record(data):
    # 0x0009, 0x0209, 0x0409, 0x0809
    pass


def analyze_BOOKBOOL_record(data):
    # 0x00DA
    pass


def analyze_BOOLERR_record(data):
    # 0x0005, 0x0205
    pass


def analyze_BOTTOMMARGIN_record(data):
    # 0x0029
    print struct.unpack('<d', data)[0]
    pass


def analyze_BOUNDSHEET_record(data):
    # 0x0085
    pass


def analyze_BUILTINFMTCNT_record(data):
    # 0x0056
    pass


def analyze_BUNDLEHEADER_record(data):
    # 0x008F
    pass


def analyze_BUNDLESOFFSET_record(data):
    # 0x008E
    pass


def analyze_CALCCOUNT_record(data):
    # 0x000C
    pass


def analyze_CALCMODE_record(data):
    # 0x000D
    pass


def analyze_MERGEDCELLS_record(data):
    # 0x00E5
    pass


def analyze_CF_record(data):
    # 0x01B1
    pass


def analyze_CHTRCELLCONTENT_record(data):
    # 0x013B
    pass


def analyze_CHTRHEADER_record(data):
    # 0x0196
    pass


def analyze_CHTRINFO_record(data):
    # 0x0138
    pass


def analyze_CHTRINSERT_record(data):
    # 0x0137
    pass


def analyze_CHTRINSERTTAB_record(data):
    # 0x014D
    pass


def analyze_CHTRMOVERANGE_record(data):
    # 0x0140
    pass


def analyze_CODENAME_record(data):
    # 0x01BA
    pass


def analyze_CODEPAGE_record(data):
    # 0x0042
    pass


def analyze_COLINFO_record(data):
    # 0x007D
    pass


def analyze_COLUMNDEFAULT_record(data):
    # 0x0020
    pass


def analyze_COLWIDTH_record(data):
    # 0x0024
    pass


def analyze_CONDFMT_record(data):
    # 0x01B0
    pass


def analyze_CONTINUE_record(data):
    # 0x003C
    pass


def analyze_COORDLIST_record(data):
    # 0x00A9
    pass


def analyze_COUNTRY_record(data):
    # 0x008C
    pass


def analyze_CRN_record(data):
    # 0x005A
    pass


def analyze_Chart3D_record(data):
    # 0x103A
    pass


def analyze_Chart3DDataFormat_record(data):
    # 0x105F
    pass


def analyze_ChartAI_record(data):
    # 0x1051
    pass


def analyze_ChartAlruns_record(data):
    # 0x1050
    pass


def analyze_ChartArea_record(data):
    # 0x101A
    pass


def analyze_ChartAreaformat_record(data):
    # 0x100A
    pass


def analyze_ChartAttachedlabel_record(data):
    # 0x100C
    pass


def analyze_ChartAxcext_record(data):
    # 0x1062
    pass


def analyze_ChartAxesused_record(data):
    # 0x1046
    pass


def analyze_ChartAxis_record(data):
    # 0x101D
    pass


def analyze_ChartAxislineformat_record(data):
    # 0x1021
    pass


def analyze_ChartAxisparent_record(data):
    # 0x1041
    pass


def analyze_ChartBar_record(data):
    # 0x1017
    pass


def analyze_ChartBoppcustom_record(data):
    # 0x1067
    pass


def analyze_ChartBoppop_record(data):
    # 0x1061
    pass


def analyze_ChartCatserrange_record(data):
    # 0x1020
    pass


def analyze_ChartChart_record(data):
    # 0x1002
    pass


def analyze_ChartChartformat_record(data):
    # 0x1014
    pass


def analyze_ChartChartline_record(data):
    # 0x101C
    pass


def analyze_ChartDat_record(data):
    # 0x1063
    pass


def analyze_ChartDataformat_record(data):
    # 0x1006
    pass


def analyze_ChartDefaulttext_record(data):
    # 0x1024
    pass


def analyze_ChartDropbar_record(data):
    # 0x103D
    pass


def analyze_ChartFbi_record(data):
    # 0x1060
    pass


def analyze_ChartFontx_record(data):
    # 0x1026
    pass


def analyze_ChartFormatlink_record(data):
    # 0x1022
    pass


def analyze_ChartFrame_record(data):
    # 0x1032
    pass


def analyze_ChartGelframe_record(data):
    # 0x1066
    pass


def analyze_ChartIfmt_record(data):
    # 0x104E
    pass


def analyze_ChartLegend_record(data):
    # 0x1015
    pass


def analyze_ChartLegendxn_record(data):
    # 0x1043
    pass


def analyze_ChartLine_record(data):
    # 0x1018
    pass


def analyze_ChartLineformat_record(data):
    # 0x1007
    pass


def analyze_ChartMarkerformat_record(data):
    # 0x1009
    pass


def analyze_ChartObjectLink_record(data):
    # 0x1027
    pass


def analyze_ChartPicf_record(data):
    # 0x103C
    pass


def analyze_ChartPie_record(data):
    # 0x1019
    pass


def analyze_ChartPieformat_record(data):
    # 0x100B
    pass


def analyze_ChartPlotarea_record(data):
    # 0x1035
    pass


def analyze_ChartPlotgrowth_record(data):
    # 0x1064
    pass


def analyze_ChartPos_record(data):
    # 0x104F
    pass


def analyze_ChartRadar_record(data):
    # 0x103E
    pass


def analyze_ChartRadararea_record(data):
    # 0x1040
    pass


def analyze_ChartSbaseref_record(data):
    # 0x1048
    pass


def analyze_ChartScatter_record(data):
    # 0x101B
    pass


def analyze_ChartSerauxerrbar_record(data):
    # 0x105B
    pass


def analyze_ChartSerauxtrend_record(data):
    # 0x104B
    pass


def analyze_ChartSerfmt_record(data):
    # 0x105D
    pass


def analyze_ChartSeries_record(data):
    # 0x1003
    pass


def analyze_ChartSerieslist_record(data):
    # 0x1016
    pass


def analyze_ChartSeriestext_record(data):
    # 0x100D
    pass


def analyze_ChartSerparent_record(data):
    # 0x104A
    pass


def analyze_ChartSertocrt_record(data):
    # 0x1045
    pass


def analyze_ChartShtprops_record(data):
    # 0x1044
    pass


def analyze_ChartSiindex_record(data):
    # 0x1065
    pass


def analyze_ChartSurface_record(data):
    # 0x103F
    pass


def analyze_ChartText_record(data):
    # 0x1025
    pass


def analyze_ChartTick_record(data):
    # 0x101E
    pass


def analyze_ChartValuerange_record(data):
    # 0x101F
    pass


def analyze_DBCELL_record(data):
    # 0x00D7
    pass


def analyze_DCON_record(data):
    # 0x0050
    pass


def analyze_DCONBIN_record(data):
    # 0x01B5
    pass


def analyze_DCONNAME_record(data):
    # 0x0053
    pass


def analyze_DCONREF_record(data):
    # 0x0051
    pass


def analyze_DEFAULTROWHEIGHT_record(data):
    # 0x0025, 0x0225
    pass


def analyze_DEFCOLWIDTH_record(data):
    # 0x0055
    pass


def analyze_DELMENU_record(data):
    # 0x00C3
    pass


def analyze_DELTA_record(data):
    # 0x0010
    pass


def analyze_DIMENSIONS_record(data):
    # 0x0000, 0x0200
    pass


def analyze_DOCROUTE_record(data):
    # 0x00B8
    pass


def analyze_DSF_record(data):
    # 0x0161
    pass


def analyze_DV_record(data):
    # 0x01BE
    pass


def analyze_DVAL_record(data):
    # 0x01B2
    pass


def analyze_EDG_record(data):
    # 0x0088
    pass


def analyze_EFONT_record(data):
    # 0x0045
    pass


def analyze_END_record(data):
    # 0x1034
    pass


def analyze_EOF_record(data):
    # 0x000A
    pass


def analyze_EXTERNCOUNT_record(data):
    # 0x0016
    pass


def analyze_EXTERNNAME_record(data):
    # 0x0023, 0x0223
    pass


def analyze_EXTERNSHEET_record(data):
    # 0x0017
    pass


def analyze_EXTSST_record(data):
    # 0x00FF
    pass


def analyze_FILEPASS_record(data):
    # 0x002F
    pass


def analyze_FILESHARING_record(data):
    # 0x005B
    pass


def analyze_FILTERMODE_record(data):
    # 0x009B
    pass


def analyze_FNGROUPCOUNT_record(data):
    # 0x009C
    pass


def analyze_FNGROUPNAME_record(data):
    # 0x009A
    pass


def analyze_FONT_record(data):
    # 0x0031, 0x0231
    pass


def analyze_FOOTER_record(data):
    # 0x0015
    pass


def analyze_FORMAT_record(data):
    # 0x001E, 0x041E
    fmt_idx = struct.unpack('<H', data[0:2])
    name_len = struct.unpack('<H', data[2:4])
    compressed = data[4] == '\x00'
    print 'format index      : 0x%04X' % fmt_idx
    print 'format name len   : 0x%04X' % name_len
    print 'compressed UNICODE:', compressed

    name = data[5:]
    if not compressed:
        name = [c for c in name if c != '\x00']    
        name = ''.join(name)
    print 'format str        :', name            
    pass


def analyze_FORMATCOUNT_record(data):
    # 0x001F
    pass


def analyze_FORMULA_record(data):
    # 0x0006, 0x0206, 0x0406
    pass


def analyze_GCW_record(data):
    # 0x00AB
    pass


def analyze_GRIDSET_record(data):
    # 0x0082
    pass


def analyze_GUTS_record(data):
    # 0x0080
    pass


def analyze_HCENTER_record(data):
    # 0x0083
    pass


def analyze_HEADER_record(data):
    # 0x0014
    pass


def analyze_HIDEOBJ_record(data):
    # 0x008D
    pass


def analyze_HLINK_record(data):
    # 0x01B8
    pass


def analyze_HORIZONTALPAGEBREAKS_record(data):
    # 0x001B
    pass


def analyze_IMDATA_record(data):
    # 0x007F
    pass


def analyze_INDEX_record(data):
    # 0x000B, 0x020B
    pass


def analyze_INTEGER_record(data):
    # 0x0002
    pass


def analyze_INTERFACEEND_record(data):
    # 0x00E2
    pass


def analyze_INTERFACEHDR_record(data):
    # 0x00E1
    pass


def analyze_ITERATION_record(data):
    # 0x0011
    pass


def analyze_IXFE_record(data):
    # 0x0044
    pass


def analyze_LABEL_record(data):
    # 0x0004, 0x0204
    pass


def analyze_LABELRANGES_record(data):
    # 0x015F
    pass


def analyze_LABELSST_record(data):
    # 0x00FD
    row, col, xf_idx, sst_idx = struct.unpack('<3HL', data)
    print 'row     : 0x%000X'  % row
    print 'col     : 0x%000X'  % col
    print 'xf  idx : 0x%000X'  % xf_idx
    print 'sst idx : 0x%000X'  % sst_idx

    pass


def analyze_LEFTMARGIN_record(data):
    # 0x0026
    print struct.unpack('<d', data)[0]
    pass


def analyze_LHNGRAPH_record(data):
    # 0x0095
    pass


def analyze_LHRECORD_record(data):
    # 0x0094
    pass


def analyze_LPR_record(data):
    # 0x0098
    pass


def analyze_MMS_record(data):
    # 0x00C1
    pass


def analyze_MSODRAWING_record(data):
    # 0x00EC
    pass


def analyze_MSODRAWINGGROUP_record(data):
    # 0x00EB
    pass


def analyze_MSODRAWINGSELECTION_record(data):
    # 0x00ED
    pass


def analyze_MULBLANK_record(data):
    # 0x00BE
    pass


def analyze_MULRK_record(data):
    # 0x00BD
    pass


def analyze_NAME_record(data):
    # 0x0018, 0x0218
    pass


def analyze_NOTE_record(data):
    # 0x001C
    pass


def analyze_NUMBER_record(data):
    # 0x0003, 0x0203
    pass


def analyze_OBJ_record(data):
    # 0x005D
    pass


def analyze_OBJPROTECT_record(data):
    # 0x0063
    pass


def analyze_OBPROJ_record(data):
    # 0x00D3
    pass


def analyze_OLESIZE_record(data):
    # 0x00DE
    pass


def analyze_PALETTE_record(data):
    # 0x0092
    pass


def analyze_PANE_record(data):
    # 0x0041
    pass


def analyze_PASSWORD_record(data):
    # 0x0013
    pass


def analyze_PLS_record(data):
    # 0x004D
    pass


def analyze_PRECISION_record(data):
    # 0x000E
    pass


def analyze_PRINTGRIDLINES_record(data):
    # 0x002B
    pass


def analyze_PRINTHEADERS_record(data):
    # 0x002A
    pass


def analyze_PROT4REV_record(data):
    # 0x01AF
    pass


def analyze_PROT4REVPASS_record(data):
    # 0x01BC
    pass


def analyze_PROTECT_record(data):
    # 0x0012
    pass


def analyze_PUB_record(data):
    # 0x0089
    pass


def analyze_QSI_record(data):
    # 0x01AD
    pass

def analyze_RECALCID_record(data):
    # 0x01C1: 
    pass


def analyze_RECIPNAME_record(data):
    # 0x00B9
    pass


def analyze_REFMODE_record(data):
    # 0x000F
    pass


def analyze_REFRESHALL_record(data):
    # 0x01B7
    pass


def analyze_RIGHTMARGIN_record(data):
    # 0x0027
    print struct.unpack('<d', data)[0]
    pass


def analyze_RK_record(data):
    # 0x007E, 0x027E
    pass


def analyze_ROW_record(data):
    # 0x0008, 0x0208
    idx, col1, col2, height_options, not_used, not_used, options = \
        struct.unpack('<6HL', data)
    print 'row index        : 0x%000X'  % idx
    print 'start col        : 0x%000X'  % col1
    print 'last col + 1     : 0x%000X'  % col2
    print 'height           : 0x%000X'  % (height_options & 0x7FFF)
    print 'height is custom : 0x%000X'  % ((height_options & 0x8000) >> 15)
    print 'outline level    : 0x%000X'  % ((options & 0x00000007L) >> 0)
    print 'level collapsed  : 0x%000X'  % ((options & 0x00000010L) >> 4)
    print 'row is hidden    : 0x%000X'  % ((options & 0x00000020L) >> 5)
    print 'font height match: 0x%000X'  % ((options & 0x00000040L) >> 6)
    print 'default format   : 0x%000X'  % ((options & 0x00000080L) >> 7)
    print 'default xf index : 0x%000X'  % ((options & 0x0FFF0000L) >> 16)
    print 'add space above  : 0x%000X'  % ((options & 0x10000000L) >> 28)
    print 'add space below  : 0x%000X'  % ((options & 0x20000000L) >> 29)


def analyze_RSTRING_record(data):
    # 0x00D6
    pass


def analyze_SAFERECALC_record(data):
    # 0x005F
    pass


def analyze_SCENARIO_record(data):
    # 0x00AF
    pass


def analyze_SCENMAN_record(data):
    # 0x00AE
    pass


def analyze_SCENPROTECT_record(data):
    # 0x00DD
    pass


def analyze_SCL_record(data):
    # 0x00A0
    pass


def analyze_SCREENTIP_record(data):
    # 0x0800
    pass


def analyze_SELECTION_record(data):
    # 0x001D
    pass


def analyze_SETUP_record(data):
    # 0x00A1
    pass


def analyze_SHEETLAYOUT_record(data):
    # 0x0862
    pass


def analyze_SHEETPROTECTION_record(data):
    # 0x0867
    pass


def analyze_SHRFMLA_record(data):
    # 0x00BC, 0x04BC
    pass


def analyze_SORT_record(data):
    # 0x0090
    pass


def analyze_SOUND_record(data):
    # 0x0096
    pass


def analyze_SST_record(data):
    # 0x00FC
    pass


def analyze_STANDARDWIDTH_record(data):
    # 0x0099
    pass


def analyze_STRING_record(data):
    # 0x0007, 0x0207
    pass


def analyze_STYLE_record(data):
    # 0x0093, 0x0293
    pass


def analyze_SUB_record(data):
    # 0x0091
    pass


def analyze_SUPBOOK_record(data):
    # 0x01AE
    pass


def analyze_SXDATETIME_record(data):
    # 0x00CE
    pass


def analyze_SXDB_record(data):
    # 0x00C6
    pass


def analyze_SXDBEX_record(data):
    # 0x0122
    pass


def analyze_SXDI_record(data):
    # 0x00C5
    pass


def analyze_SXDOUBLE_record(data):
    # 0x00C9
    pass


def analyze_SXEX_record(data):
    # 0x00F1
    pass


def analyze_SXEXT_PARAMQRY_record(data):
    # 0x00DC
    pass


def analyze_SXFDBTYPE_record(data):
    # 0x01BB
    pass


def analyze_SXFIELD_record(data):
    # 0x00C7
    pass


def analyze_SXFILT_record(data):
    # 0x00F2
    pass


def analyze_SXFMLA_record(data):
    # 0x00F9
    pass


def analyze_SXFORMAT_record(data):
    # 0x00FB
    pass


def analyze_SXFORMULA_record(data):
    # 0x0103
    pass


def analyze_SXIDSTM_record(data):
    # 0x00D5
    pass


def analyze_SXINDEXLIST_record(data):
    # 0x00C8
    pass


def analyze_SXIVD_record(data):
    # 0x00B4
    pass


def analyze_SXLI_record(data):
    # 0x00B5
    pass


def analyze_SXNAME_record(data):
    # 0x00F6
    pass


def analyze_SXPAIR_record(data):
    # 0x00F8
    pass


def analyze_SXPI_record(data):
    # 0x00B6
    pass


def analyze_SXRULE_record(data):
    # 0x00F0
    pass


def analyze_SXSELECT_record(data):
    # 0x00F7
    pass


def analyze_SXSTRING_record(data):
    # 0x00CD
    pass


def analyze_SXTBL_record(data):
    # 0x00D0
    pass


def analyze_SXTBPG_record(data):
    # 0x00D2
    pass


def analyze_SXTBRGITEM_record(data):
    # 0x00D1
    pass


def analyze_SXVD_record(data):
    # 0x00B1
    pass


def analyze_SXVDEX_record(data):
    # 0x0100
    pass


def analyze_SXVI_record(data):
    # 0x00B2
    pass


def analyze_SXVIEW_record(data):
    # 0x00B0
    pass


def analyze_SXVS_record(data):
    # 0x00E3
    pass


def analyze_TABID_record(data):
    # 0x013D
    pass


def analyze_TABLE_record(data):
    # 0x0036, 0x0236
    pass


def analyze_TEMPLATE_record(data):
    # 0x0060
    pass


def analyze_TOPMARGIN_record(data):
    # 0x0028
    print struct.unpack('<d', data)[0]
    pass


def analyze_TXO_record(data):
    # 0x01B6
    pass


def analyze_UDDESC_record(data):
    # 0x00DF
    pass


def analyze_UNCALCED_record(data):
    # 0x005E
    pass


def analyze_UNITS_record(data):
    # 0x1001
    pass


def analyze_USERBVIEW_record(data):
    # 0x01A9
    pass


def analyze_USERSVIEWBEGIN_record(data):
    # 0x01AA
    pass


def analyze_USERSVIEWEND_record(data):
    # 0x01AB
    pass


def analyze_USESELFS_record(data):
    # 0x0160
    pass


def analyze_VCENTER_record(data):
    # 0x0084
    pass


def analyze_VERTICALPAGEBREAKS_record(data):
    # 0x001A
    pass


def analyze_WEBQRYSETTINGS_record(data):
    # 0x0803
    pass


def analyze_WEBQRYTABLES_record(data):
    # 0x0804
    pass


def analyze_WINDOW1_record(data):
    # 0x003D
    pass


def analyze_WINDOW2_record(data):
    # 0x003E, 0x023E
    pass


def analyze_WINDOWPROTECT_record(data):
    # 0x0019
    pass


def analyze_WRITEACCESS_record(data):
    # 0x005C
    pass


def analyze_WRITEPROT_record(data):
    # 0x0086
    pass


def analyze_WSBOOL_record(data):
    # 0x0081
    pass


def analyze_XCT_record(data):
    # 0x0059
    pass


def analyze_XF_record(data):
    # 0x0043, 0x00E0, 0x0243, 0x0443
    #fnt_idx, num_ftm_idx, \
    #    cell_prot,         \
    #    align, rotation, txt_format, \
    #    used_attrib, \
    #    border0, border1, border2 = struct.unpack('<3H4B2LH', data)
    #print 'fnt idx                 : 0x%000X'  % fnt_idx
    #print 'num fmt idx             : 0x%000X'  % num_ftm_idx
    #print 'cell is locked          : 0x%0X  '  % ((cell_prot) & 0x01)
    #print 'format is hidden        : 0x%0X  '  % ((cell_prot & 0x02) >> 1)
    #print 'style XF(1), cell XF(0) : 0x%0X  '  % ((cell_prot & 0x03) >> 3)
    #print 'Index to parent style XF: 0x%0000X' % ((cell_prot & 0xFFF0) >> 4)

    pass


def analyze_XL5MODIFY_record(data):
    # 0x0162
    pass

def analyze_XL9FILE_record(data):
    # 0x01C0: 
    pass

all_records = {
    0x0000: ('DIMENSIONS', analyze_DIMENSIONS_record),
    0x0001: ('BLANK', analyze_BLANK_record),
    0x0002: ('INTEGER', analyze_INTEGER_record),
    0x0003: ('NUMBER', analyze_NUMBER_record),
    0x0004: ('LABEL', analyze_LABEL_record),
    0x0005: ('BOOLERR', analyze_BOOLERR_record),
    0x0006: ('FORMULA', analyze_FORMULA_record),
    0x0007: ('STRING', analyze_STRING_record),
    0x0008: ('ROW', analyze_ROW_record),
    0x0009: ('BOF', analyze_BOF_record),
    0x000A: ('EOF', analyze_EOF_record),
    0x000B: ('INDEX', analyze_INDEX_record),
    0x000C: ('CALCCOUNT', analyze_CALCCOUNT_record),
    0x000D: ('CALCMODE', analyze_CALCMODE_record),
    0x000E: ('PRECISION', analyze_PRECISION_record),
    0x000F: ('REFMODE', analyze_REFMODE_record),
    0x0010: ('DELTA', analyze_DELTA_record),
    0x0011: ('ITERATION', analyze_ITERATION_record),
    0x0012: ('PROTECT', analyze_PROTECT_record),
    0x0013: ('PASSWORD', analyze_PASSWORD_record),
    0x0014: ('HEADER', analyze_HEADER_record),
    0x0015: ('FOOTER', analyze_FOOTER_record),
    0x0016: ('EXTERNCOUNT', analyze_EXTERNCOUNT_record),
    0x0017: ('EXTERNSHEET', analyze_EXTERNSHEET_record),
    0x0018: ('NAME', analyze_NAME_record),
    0x0019: ('WINDOWPROTECT', analyze_WINDOWPROTECT_record),
    0x001A: ('VERTICALPAGEBREAKS', analyze_VERTICALPAGEBREAKS_record),
    0x001B: ('HORIZONTALPAGEBREAKS', analyze_HORIZONTALPAGEBREAKS_record),
    0x001C: ('NOTE', analyze_NOTE_record),
    0x001D: ('SELECTION', analyze_SELECTION_record),
    0x001E: ('FORMAT', analyze_FORMAT_record),
    0x001F: ('FORMATCOUNT', analyze_FORMATCOUNT_record),
    0x0020: ('COLUMNDEFAULT', analyze_COLUMNDEFAULT_record),
    0x0021: ('ARRAY', analyze_ARRAY_record),
    0x0022: ('1904', analyze_1904_record),
    0x0023: ('EXTERNNAME', analyze_EXTERNNAME_record),
    0x0024: ('COLWIDTH', analyze_COLWIDTH_record),
    0x0025: ('DEFAULTROWHEIGHT', analyze_DEFAULTROWHEIGHT_record),
    0x0026: ('LEFTMARGIN', analyze_LEFTMARGIN_record),
    0x0027: ('RIGHTMARGIN', analyze_RIGHTMARGIN_record),
    0x0028: ('TOPMARGIN', analyze_TOPMARGIN_record),
    0x0029: ('BOTTOMMARGIN', analyze_BOTTOMMARGIN_record),
    0x002A: ('PRINTHEADERS', analyze_PRINTHEADERS_record),
    0x002B: ('PRINTGRIDLINES', analyze_PRINTGRIDLINES_record),
    0x002F: ('FILEPASS', analyze_FILEPASS_record),
    0x0031: ('FONT', analyze_FONT_record),
    0x0036: ('TABLE', analyze_TABLE_record),
    0x003C: ('CONTINUE', analyze_CONTINUE_record),
    0x003D: ('WINDOW1', analyze_WINDOW1_record),
    0x003E: ('WINDOW2', analyze_WINDOW2_record),
    0x0040: ('BACKUP', analyze_BACKUP_record),
    0x0041: ('PANE', analyze_PANE_record),
    0x0042: ('CODEPAGE', analyze_CODEPAGE_record),
    0x0043: ('XF', analyze_XF_record),
    0x0044: ('IXFE', analyze_IXFE_record),
    0x0045: ('EFONT', analyze_EFONT_record),
    0x004D: ('PLS', analyze_PLS_record),
    0x0050: ('DCON', analyze_DCON_record),
    0x0051: ('DCONREF', analyze_DCONREF_record),
    0x0053: ('DCONNAME', analyze_DCONNAME_record),
    0x0055: ('DEFCOLWIDTH', analyze_DEFCOLWIDTH_record),
    0x0056: ('BUILTINFMTCNT', analyze_BUILTINFMTCNT_record),
    0x0059: ('XCT', analyze_XCT_record),
    0x005A: ('CRN', analyze_CRN_record),
    0x005B: ('FILESHARING', analyze_FILESHARING_record),
    0x005C: ('WRITEACCESS', analyze_WRITEACCESS_record),
    0x005D: ('OBJ', analyze_OBJ_record),
    0x005E: ('UNCALCED', analyze_UNCALCED_record),
    0x005F: ('SAFERECALC', analyze_SAFERECALC_record),
    0x0060: ('TEMPLATE', analyze_TEMPLATE_record),
    0x0063: ('OBJPROTECT', analyze_OBJPROTECT_record),
    0x007D: ('COLINFO', analyze_COLINFO_record),
    0x007E: ('RK', analyze_RK_record),
    0x007F: ('IMDATA', analyze_IMDATA_record),
    0x0080: ('GUTS', analyze_GUTS_record),
    0x0081: ('WSBOOL', analyze_WSBOOL_record),
    0x0082: ('GRIDSET', analyze_GRIDSET_record),
    0x0083: ('HCENTER', analyze_HCENTER_record),
    0x0084: ('VCENTER', analyze_VCENTER_record),
    0x0085: ('BOUNDSHEET', analyze_BOUNDSHEET_record),
    0x0086: ('WRITEPROT', analyze_WRITEPROT_record),
    0x0087: ('ADDIN', analyze_ADDIN_record),
    0x0088: ('EDG', analyze_EDG_record),
    0x0089: ('PUB', analyze_PUB_record),
    0x008C: ('COUNTRY', analyze_COUNTRY_record),
    0x008D: ('HIDEOBJ', analyze_HIDEOBJ_record),
    0x008E: ('BUNDLESOFFSET', analyze_BUNDLESOFFSET_record),
    0x008F: ('BUNDLEHEADER', analyze_BUNDLEHEADER_record),
    0x0090: ('SORT', analyze_SORT_record),
    0x0091: ('SUB', analyze_SUB_record),
    0x0092: ('PALETTE', analyze_PALETTE_record),
    0x0093: ('STYLE', analyze_STYLE_record),
    0x0094: ('LHRECORD', analyze_LHRECORD_record),
    0x0095: ('LHNGRAPH', analyze_LHNGRAPH_record),
    0x0096: ('SOUND', analyze_SOUND_record),
    0x0098: ('LPR', analyze_LPR_record),
    0x0099: ('STANDARDWIDTH', analyze_STANDARDWIDTH_record),
    0x009A: ('FNGROUPNAME', analyze_FNGROUPNAME_record),
    0x009B: ('FILTERMODE', analyze_FILTERMODE_record),
    0x009C: ('FNGROUPCOUNT', analyze_FNGROUPCOUNT_record),
    0x009D: ('AUTOFILTERINFO', analyze_AUTOFILTERINFO_record),
    0x009E: ('AUTOFILTER', analyze_AUTOFILTER_record),
    0x00A0: ('SCL', analyze_SCL_record),
    0x00A1: ('SETUP', analyze_SETUP_record),
    0x00A9: ('COORDLIST', analyze_COORDLIST_record),
    0x00AB: ('GCW', analyze_GCW_record),
    0x00AE: ('SCENMAN', analyze_SCENMAN_record),
    0x00AF: ('SCENARIO', analyze_SCENARIO_record),
    0x00B0: ('SXVIEW', analyze_SXVIEW_record),
    0x00B1: ('SXVD', analyze_SXVD_record),
    0x00B2: ('SXVI', analyze_SXVI_record),
    0x00B4: ('SXIVD', analyze_SXIVD_record),
    0x00B5: ('SXLI', analyze_SXLI_record),
    0x00B6: ('SXPI', analyze_SXPI_record),
    0x00B8: ('DOCROUTE', analyze_DOCROUTE_record),
    0x00B9: ('RECIPNAME', analyze_RECIPNAME_record),
    0x00BC: ('SHRFMLA', analyze_SHRFMLA_record),
    0x00BD: ('MULRK', analyze_MULRK_record),
    0x00BE: ('MULBLANK', analyze_MULBLANK_record),
    0x00C1: ('MMS', analyze_MMS_record),
    0x00C2: ('ADDMENU', analyze_ADDMENU_record),
    0x00C3: ('DELMENU', analyze_DELMENU_record),
    0x00C5: ('SXDI', analyze_SXDI_record),
    0x00C6: ('SXDB', analyze_SXDB_record),
    0x00C7: ('SXFIELD', analyze_SXFIELD_record),
    0x00C8: ('SXINDEXLIST', analyze_SXINDEXLIST_record),
    0x00C9: ('SXDOUBLE', analyze_SXDOUBLE_record),
    0x00CD: ('SXSTRING', analyze_SXSTRING_record),
    0x00CE: ('SXDATETIME', analyze_SXDATETIME_record),
    0x00D0: ('SXTBL', analyze_SXTBL_record),
    0x00D1: ('SXTBRGITEM', analyze_SXTBRGITEM_record),
    0x00D2: ('SXTBPG', analyze_SXTBPG_record),
    0x00D3: ('OBPROJ', analyze_OBPROJ_record),
    0x00D5: ('SXIDSTM', analyze_SXIDSTM_record),
    0x00D6: ('RSTRING', analyze_RSTRING_record),
    0x00D7: ('DBCELL', analyze_DBCELL_record),
    0x00DA: ('BOOKBOOL', analyze_BOOKBOOL_record),
    0x00DC: ('SXEXT|PARAMQRY', analyze_SXEXT_PARAMQRY_record),
    0x00DD: ('SCENPROTECT', analyze_SCENPROTECT_record),
    0x00DE: ('OLESIZE', analyze_OLESIZE_record),
    0x00DF: ('UDDESC', analyze_UDDESC_record),
    0x00E0: ('XF', analyze_XF_record),
    0x00E1: ('INTERFACEHDR', analyze_INTERFACEHDR_record),
    0x00E2: ('INTERFACEEND', analyze_INTERFACEEND_record),
    0x00E3: ('SXVS', analyze_SXVS_record),
    0x00E5: ('MERGEDCELLS', analyze_MERGEDCELLS_record),
    0x00E9: ('BITMAP', analyze_BITMAP_record),
    0x00EB: ('MSODRAWINGGROUP', analyze_MSODRAWINGGROUP_record),
    0x00EC: ('MSODRAWING', analyze_MSODRAWING_record),
    0x00ED: ('MSODRAWINGSELECTION', analyze_MSODRAWINGSELECTION_record),
    0x00F0: ('SXRULE', analyze_SXRULE_record),
    0x00F1: ('SXEX', analyze_SXEX_record),
    0x00F2: ('SXFILT', analyze_SXFILT_record),
    0x00F6: ('SXNAME', analyze_SXNAME_record),
    0x00F7: ('SXSELECT', analyze_SXSELECT_record),
    0x00F8: ('SXPAIR', analyze_SXPAIR_record),
    0x00F9: ('SXFMLA', analyze_SXFMLA_record),
    0x00FB: ('SXFORMAT', analyze_SXFORMAT_record),
    0x00FC: ('SST', analyze_SST_record),
    0x00FD: ('LABELSST', analyze_LABELSST_record),
    0x00FF: ('EXTSST', analyze_EXTSST_record),
    0x0100: ('SXVDEX', analyze_SXVDEX_record),
    0x0103: ('SXFORMULA', analyze_SXFORMULA_record),
    0x0122: ('SXDBEX', analyze_SXDBEX_record),
    0x0137: ('CHTRINSERT', analyze_CHTRINSERT_record),
    0x0138: ('CHTRINFO', analyze_CHTRINFO_record),
    0x013B: ('CHTRCELLCONTENT', analyze_CHTRCELLCONTENT_record),
    0x013D: ('TABID', analyze_TABID_record),
    0x0140: ('CHTRMOVERANGE', analyze_CHTRMOVERANGE_record),
    0x014D: ('CHTRINSERTTAB', analyze_CHTRINSERTTAB_record),
    0x015F: ('LABELRANGES', analyze_LABELRANGES_record),
    0x0160: ('USESELFS', analyze_USESELFS_record),
    0x0161: ('DSF', analyze_DSF_record),
    0x0162: ('XL5MODIFY', analyze_XL5MODIFY_record),
    0x0196: ('CHTRHEADER', analyze_CHTRHEADER_record),
    0x01A9: ('USERBVIEW', analyze_USERBVIEW_record),
    0x01AA: ('USERSVIEWBEGIN', analyze_USERSVIEWBEGIN_record),
    0x01AB: ('USERSVIEWEND', analyze_USERSVIEWEND_record),
    0x01AD: ('QSI', analyze_QSI_record),
    0x01AE: ('SUPBOOK', analyze_SUPBOOK_record),
    0x01AF: ('PROT4REV', analyze_PROT4REV_record),
    0x01B0: ('CONDFMT', analyze_CONDFMT_record),
    0x01B1: ('CF', analyze_CF_record),
    0x01B2: ('DVAL', analyze_DVAL_record),
    0x01B5: ('DCONBIN', analyze_DCONBIN_record),
    0x01B6: ('TXO', analyze_TXO_record),
    0x01B7: ('REFRESHALL', analyze_REFRESHALL_record),
    0x01B8: ('HLINK', analyze_HLINK_record),
    0x01BA: ('CODENAME', analyze_CODENAME_record),
    0x01BB: ('SXFDBTYPE', analyze_SXFDBTYPE_record),
    0x01BC: ('PROT4REVPASS', analyze_PROT4REVPASS_record),
    0x01BE: ('DV', analyze_DV_record),
    0x01C0: ('XL9FILE', analyze_XL9FILE_record),
    0x01C1: ('RECALCID',analyze_RECALCID_record),
    0x0200: ('DIMENSIONS', analyze_DIMENSIONS_record),
    0x0201: ('BLANK', analyze_BLANK_record),
    0x0203: ('NUMBER', analyze_NUMBER_record),
    0x0204: ('LABEL', analyze_LABEL_record),
    0x0205: ('BOOLERR', analyze_BOOLERR_record),
    0x0206: ('FORMULA', analyze_FORMULA_record),
    0x0207: ('STRING', analyze_STRING_record),
    0x0208: ('ROW', analyze_ROW_record),
    0x0209: ('BOF', analyze_BOF_record),
    0x020B: ('INDEX', analyze_INDEX_record),
    0x0218: ('NAME', analyze_NAME_record),
    0x0221: ('ARRAY', analyze_ARRAY_record),
    0x0223: ('EXTERNNAME', analyze_EXTERNNAME_record),
    0x0225: ('DEFAULTROWHEIGHT', analyze_DEFAULTROWHEIGHT_record),
    0x0231: ('FONT', analyze_FONT_record),
    0x0236: ('TABLE', analyze_TABLE_record),
    0x023E: ('WINDOW2', analyze_WINDOW2_record),
    0x0243: ('XF', analyze_XF_record),
    0x027E: ('RK', analyze_RK_record),
    0x0293: ('STYLE', analyze_STYLE_record),
    0x0406: ('FORMULA', analyze_FORMULA_record),
    0x0409: ('BOF', analyze_BOF_record),
    0x041E: ('FORMAT', analyze_FORMAT_record),
    0x0443: ('XF', analyze_XF_record),
    0x04BC: ('SHRFMLA', analyze_SHRFMLA_record),
    0x0800: ('SCREENTIP', analyze_SCREENTIP_record),
    0x0803: ('WEBQRYSETTINGS', analyze_WEBQRYSETTINGS_record),
    0x0804: ('WEBQRYTABLES', analyze_WEBQRYTABLES_record),
    0x0809: ('BOF', analyze_BOF_record),
    0x0862: ('SHEETLAYOUT', analyze_SHEETLAYOUT_record),
    0x0867: ('SHEETPROTECTION', analyze_SHEETPROTECTION_record),
    0x1001: ('UNITS', analyze_UNITS_record),
    0x1002: ('ChartChart', analyze_ChartChart_record),
    0x1003: ('ChartSeries', analyze_ChartSeries_record),
    0x1006: ('ChartDataformat', analyze_ChartDataformat_record),
    0x1007: ('ChartLineformat', analyze_ChartLineformat_record),
    0x1009: ('ChartMarkerformat', analyze_ChartMarkerformat_record),
    0x100A: ('ChartAreaformat', analyze_ChartAreaformat_record),
    0x100B: ('ChartPieformat', analyze_ChartPieformat_record),
    0x100C: ('ChartAttachedlabel', analyze_ChartAttachedlabel_record),
    0x100D: ('ChartSeriestext', analyze_ChartSeriestext_record),
    0x1014: ('ChartChartformat', analyze_ChartChartformat_record),
    0x1015: ('ChartLegend', analyze_ChartLegend_record),
    0x1016: ('ChartSerieslist', analyze_ChartSerieslist_record),
    0x1017: ('ChartBar', analyze_ChartBar_record),
    0x1018: ('ChartLine', analyze_ChartLine_record),
    0x1019: ('ChartPie', analyze_ChartPie_record),
    0x101A: ('ChartArea', analyze_ChartArea_record),
    0x101B: ('ChartScatter', analyze_ChartScatter_record),
    0x101C: ('ChartChartline', analyze_ChartChartline_record),
    0x101D: ('ChartAxis', analyze_ChartAxis_record),
    0x101E: ('ChartTick', analyze_ChartTick_record),
    0x101F: ('ChartValuerange', analyze_ChartValuerange_record),
    0x1020: ('ChartCatserrange', analyze_ChartCatserrange_record),
    0x1021: ('ChartAxislineformat', analyze_ChartAxislineformat_record),
    0x1022: ('ChartFormatlink', analyze_ChartFormatlink_record),
    0x1024: ('ChartDefaulttext', analyze_ChartDefaulttext_record),
    0x1025: ('ChartText', analyze_ChartText_record),
    0x1026: ('ChartFontx', analyze_ChartFontx_record),
    0x1027: ('ChartObjectLink', analyze_ChartObjectLink_record),
    0x1032: ('ChartFrame', analyze_ChartFrame_record),
    0x1033: ('BEGIN', analyze_BEGIN_record),
    0x1034: ('END', analyze_END_record),
    0x1035: ('ChartPlotarea', analyze_ChartPlotarea_record),
    0x103A: ('Chart3D', analyze_Chart3D_record),
    0x103C: ('ChartPicf', analyze_ChartPicf_record),
    0x103D: ('ChartDropbar', analyze_ChartDropbar_record),
    0x103E: ('ChartRadar', analyze_ChartRadar_record),
    0x103F: ('ChartSurface', analyze_ChartSurface_record),
    0x1040: ('ChartRadararea', analyze_ChartRadararea_record),
    0x1041: ('ChartAxisparent', analyze_ChartAxisparent_record),
    0x1043: ('ChartLegendxn', analyze_ChartLegendxn_record),
    0x1044: ('ChartShtprops', analyze_ChartShtprops_record),
    0x1045: ('ChartSertocrt', analyze_ChartSertocrt_record),
    0x1046: ('ChartAxesused', analyze_ChartAxesused_record),
    0x1048: ('ChartSbaseref', analyze_ChartSbaseref_record),
    0x104A: ('ChartSerparent', analyze_ChartSerparent_record),
    0x104B: ('ChartSerauxtrend', analyze_ChartSerauxtrend_record),
    0x104E: ('ChartIfmt', analyze_ChartIfmt_record),
    0x104F: ('ChartPos', analyze_ChartPos_record),
    0x1050: ('ChartAlruns', analyze_ChartAlruns_record),
    0x1051: ('ChartAI', analyze_ChartAI_record),
    0x105B: ('ChartSerauxerrbar', analyze_ChartSerauxerrbar_record),
    0x105D: ('ChartSerfmt', analyze_ChartSerfmt_record),
    0x105F: ('Chart3DDataFormat', analyze_Chart3DDataFormat_record),
    0x1060: ('ChartFbi', analyze_ChartFbi_record),
    0x1061: ('ChartBoppop', analyze_ChartBoppop_record),
    0x1062: ('ChartAxcext', analyze_ChartAxcext_record),
    0x1063: ('ChartDat', analyze_ChartDat_record),
    0x1064: ('ChartPlotgrowth', analyze_ChartPlotgrowth_record),
    0x1065: ('ChartSiindex', analyze_ChartSiindex_record),
    0x1066: ('ChartGelframe', analyze_ChartGelframe_record),
    0x1067: ('ChartBoppcustom', analyze_ChartBoppcustom_record),
    0xFFFF: ('', None)
}
if __name__ == '__main__':
    for r in all_records:
        if all_records[r][1]:
            all_records[r][1]('analyze it!')
            