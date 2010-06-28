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


__rev_id__ = """$Id: ExcelMagic.py,v 1.2 2005/10/26 07:44:24 rvk Exp $"""


"""
lots of Excel Magic Numbers
"""

# Boundaries BIFF8+

MAX_ROW = 65536
MAX_COL = 256


biff_records = {
    0x0000: "DIMENSIONS",
    0x0001: "BLANK",
    0x0002: "INTEGER",
    0x0003: "NUMBER",
    0x0004: "LABEL",
    0x0005: "BOOLERR",
    0x0006: "FORMULA",
    0x0007: "STRING",
    0x0008: "ROW",
    0x0009: "BOF",
    0x000A: "EOF",
    0x000B: "INDEX",
    0x000C: "CALCCOUNT",
    0x000D: "CALCMODE",
    0x000E: "PRECISION",
    0x000F: "REFMODE",
    0x0010: "DELTA",
    0x0011: "ITERATION",
    0x0012: "PROTECT",
    0x0013: "PASSWORD",
    0x0014: "HEADER",
    0x0015: "FOOTER",
    0x0016: "EXTERNCOUNT",
    0x0017: "EXTERNSHEET",
    0x0018: "NAME",
    0x0019: "WINDOWPROTECT",
    0x001A: "VERTICALPAGEBREAKS",
    0x001B: "HORIZONTALPAGEBREAKS",
    0x001C: "NOTE",
    0x001D: "SELECTION",
    0x001E: "FORMAT",
    0x001F: "FORMATCOUNT",
    0x0020: "COLUMNDEFAULT",
    0x0021: "ARRAY",
    0x0022: "1904",
    0x0023: "EXTERNNAME",
    0x0024: "COLWIDTH",
    0x0025: "DEFAULTROWHEIGHT",
    0x0026: "LEFTMARGIN",
    0x0027: "RIGHTMARGIN",
    0x0028: "TOPMARGIN",
    0x0029: "BOTTOMMARGIN",
    0x002A: "PRINTHEADERS",
    0x002B: "PRINTGRIDLINES",
    0x002F: "FILEPASS",
    0x0031: "FONT",
    0x0036: "TABLE",
    0x003C: "CONTINUE",
    0x003D: "WINDOW1",
    0x003E: "WINDOW2",
    0x0040: "BACKUP",
    0x0041: "PANE",
    0x0042: "CODEPAGE",
    0x0043: "XF",
    0x0044: "IXFE",
    0x0045: "EFONT",
    0x004D: "PLS",
    0x0050: "DCON",
    0x0051: "DCONREF",
    0x0053: "DCONNAME",
    0x0055: "DEFCOLWIDTH",
    0x0056: "BUILTINFMTCNT",
    0x0059: "XCT",
    0x005A: "CRN",
    0x005B: "FILESHARING",
    0x005C: "WRITEACCESS",
    0x005D: "OBJ",
    0x005E: "UNCALCED",
    0x005F: "SAFERECALC",
    0x0060: "TEMPLATE",
    0x0063: "OBJPROTECT",
    0x007D: "COLINFO",
    0x007E: "RK",
    0x007F: "IMDATA",
    0x0080: "GUTS",
    0x0081: "WSBOOL",
    0x0082: "GRIDSET",
    0x0083: "HCENTER",
    0x0084: "VCENTER",
    0x0085: "BOUNDSHEET",
    0x0086: "WRITEPROT",
    0x0087: "ADDIN",
    0x0088: "EDG",
    0x0089: "PUB",
    0x008C: "COUNTRY",
    0x008D: "HIDEOBJ",
    0x008E: "BUNDLESOFFSET",
    0x008F: "BUNDLEHEADER",
    0x0090: "SORT",
    0x0091: "SUB",
    0x0092: "PALETTE",
    0x0093: "STYLE",
    0x0094: "LHRECORD",
    0x0095: "LHNGRAPH",
    0x0096: "SOUND",
    0x0098: "LPR",
    0x0099: "STANDARDWIDTH",
    0x009A: "FNGROUPNAME",
    0x009B: "FILTERMODE",
    0x009C: "FNGROUPCOUNT",
    0x009D: "AUTOFILTERINFO",
    0x009E: "AUTOFILTER",
    0x00A0: "SCL",
    0x00A1: "SETUP",
    0x00A9: "COORDLIST",
    0x00AB: "GCW",
    0x00AE: "SCENMAN",
    0x00AF: "SCENARIO",
    0x00B0: "SXVIEW",
    0x00B1: "SXVD",
    0x00B2: "SXVI",
    0x00B4: "SXIVD",
    0x00B5: "SXLI",
    0x00B6: "SXPI",
    0x00B8: "DOCROUTE",
    0x00B9: "RECIPNAME",
    0x00BC: "SHRFMLA",
    0x00BD: "MULRK",
    0x00BE: "MULBLANK",
    0x00C1: "MMS",
    0x00C2: "ADDMENU",
    0x00C3: "DELMENU",
    0x00C5: "SXDI",
    0x00C6: "SXDB",
    0x00C7: "SXFIELD",
    0x00C8: "SXINDEXLIST",
    0x00C9: "SXDOUBLE",
    0x00CD: "SXSTRING",
    0x00CE: "SXDATETIME",
    0x00D0: "SXTBL",
    0x00D1: "SXTBRGITEM",
    0x00D2: "SXTBPG",
    0x00D3: "OBPROJ",
    0x00D5: "SXIDSTM",
    0x00D6: "RSTRING",
    0x00D7: "DBCELL",
    0x00DA: "BOOKBOOL",
    0x00DC: "SXEXT|PARAMQRY",
    0x00DD: "SCENPROTECT",
    0x00DE: "OLESIZE",
    0x00DF: "UDDESC",
    0x00E0: "XF",
    0x00E1: "INTERFACEHDR",
    0x00E2: "INTERFACEEND",
    0x00E3: "SXVS",
    0x00E5: "MERGEDCELLS",
    0x00E9: "BITMAP",
    0x00EB: "MSODRAWINGGROUP",
    0x00EC: "MSODRAWING",
    0x00ED: "MSODRAWINGSELECTION",
    0x00F0: "SXRULE",
    0x00F1: "SXEX",
    0x00F2: "SXFILT",
    0x00F6: "SXNAME",
    0x00F7: "SXSELECT",
    0x00F8: "SXPAIR",
    0x00F9: "SXFMLA",
    0x00FB: "SXFORMAT",
    0x00FC: "SST",
    0x00FD: "LABELSST",
    0x00FF: "EXTSST",
    0x0100: "SXVDEX",
    0x0103: "SXFORMULA",
    0x0122: "SXDBEX",
    0x0137: "CHTRINSERT",
    0x0138: "CHTRINFO",
    0x013B: "CHTRCELLCONTENT",
    0x013D: "TABID",
    0x0140: "CHTRMOVERANGE",
    0x014D: "CHTRINSERTTAB",
    0x015F: "LABELRANGES",
    0x0160: "USESELFS",
    0x0161: "DSF",
    0x0162: "XL5MODIFY",
    0x0196: "CHTRHEADER",
    0x01A9: "USERBVIEW",
    0x01AA: "USERSVIEWBEGIN",
    0x01AB: "USERSVIEWEND",
    0x01AD: "QSI",
    0x01AE: "SUPBOOK",
    0x01AF: "PROT4REV",
    0x01B0: "CONDFMT",
    0x01B1: "CF",
    0x01B2: "DVAL",
    0x01B5: "DCONBIN",
    0x01B6: "TXO",
    0x01B7: "REFRESHALL",
    0x01B8: "HLINK",
    0x01BA: "CODENAME",
    0x01BB: "SXFDBTYPE",
    0x01BC: "PROT4REVPASS",
    0x01BE: "DV",
    0x01C0: "XL9FILE",
    0x01C1: "RECALCID",
    0x0200: "DIMENSIONS",
    0x0201: "BLANK",
    0x0203: "NUMBER",
    0x0204: "LABEL",
    0x0205: "BOOLERR",
    0x0206: "FORMULA",
    0x0207: "STRING",
    0x0208: "ROW",
    0x0209: "BOF",
    0x020B: "INDEX",
    0x0218: "NAME",
    0x0221: "ARRAY",
    0x0223: "EXTERNNAME",
    0x0225: "DEFAULTROWHEIGHT",
    0x0231: "FONT",
    0x0236: "TABLE",
    0x023E: "WINDOW2",
    0x0243: "XF",
    0x027E: "RK",
    0x0293: "STYLE",
    0x0406: "FORMULA",
    0x0409: "BOF",
    0x041E: "FORMAT",
    0x0443: "XF",
    0x04BC: "SHRFMLA",
    0x0800: "SCREENTIP",
    0x0803: "WEBQRYSETTINGS",
    0x0804: "WEBQRYTABLES",
    0x0809: "BOF",
    0x0862: "SHEETLAYOUT",
    0x0867: "SHEETPROTECTION",
    0x1001: "UNITS",
    0x1002: "ChartChart",
    0x1003: "ChartSeries",
    0x1006: "ChartDataformat",
    0x1007: "ChartLineformat",
    0x1009: "ChartMarkerformat",
    0x100A: "ChartAreaformat",
    0x100B: "ChartPieformat",
    0x100C: "ChartAttachedlabel",
    0x100D: "ChartSeriestext",
    0x1014: "ChartChartformat",
    0x1015: "ChartLegend",
    0x1016: "ChartSerieslist",
    0x1017: "ChartBar",
    0x1018: "ChartLine",
    0x1019: "ChartPie",
    0x101A: "ChartArea",
    0x101B: "ChartScatter",
    0x101C: "ChartChartline",
    0x101D: "ChartAxis",
    0x101E: "ChartTick",
    0x101F: "ChartValuerange",
    0x1020: "ChartCatserrange",
    0x1021: "ChartAxislineformat",
    0x1022: "ChartFormatlink",
    0x1024: "ChartDefaulttext",
    0x1025: "ChartText",
    0x1026: "ChartFontx",
    0x1027: "ChartObjectLink",
    0x1032: "ChartFrame",
    0x1033: "BEGIN",
    0x1034: "END",
    0x1035: "ChartPlotarea",
    0x103A: "Chart3D",
    0x103C: "ChartPicf",
    0x103D: "ChartDropbar",
    0x103E: "ChartRadar",
    0x103F: "ChartSurface",
    0x1040: "ChartRadararea",
    0x1041: "ChartAxisparent",
    0x1043: "ChartLegendxn",
    0x1044: "ChartShtprops",
    0x1045: "ChartSertocrt",
    0x1046: "ChartAxesused",
    0x1048: "ChartSbaseref",
    0x104A: "ChartSerparent",
    0x104B: "ChartSerauxtrend",
    0x104E: "ChartIfmt",
    0x104F: "ChartPos",
    0x1050: "ChartAlruns",
    0x1051: "ChartAI",
    0x105B: "ChartSerauxerrbar",
    0x105D: "ChartSerfmt",
    0x105F: "Chart3DDataFormat",
    0x1060: "ChartFbi",
    0x1061: "ChartBoppop",
    0x1062: "ChartAxcext",
    0x1063: "ChartDat",
    0x1064: "ChartPlotgrowth",
    0x1065: "ChartSiindex",
    0x1066: "ChartGelframe",
    0x1067: "ChartBoppcustom",
    0xFFFF: ""
}


std_func_by_name = {
             "ABS": (0x018,  1,  1,   "V",             "V", False), # 1
            "ACOS": (0x063,  1,  1,   "V",             "V", False), # 2
           "ACOSH": (0x0e9,  1,  1,   "V",             "V", False), # 3
         "ADDRESS": (0x0db,  2,  5,   "V",     "V V V V V", False), # 4
             "AND": (0x024,  1, 30,   "V",         "R ...", False), # 5
          "ARCTAN": (0x012,  1,  1,   "V",             "V", False), # 6
           "AREAS": (0x04b,  1,  1,   "V",             "R", False), # 7
             "ASC": (0x0d6,  1,  1,   "V",             "V", False), # 8
            "ASIN": (0x062,  1,  1,   "V",             "V", False), # 9
           "ASINH": (0x0e8,  1,  1,   "V",             "V", False), # 10
           "ATAN2": (0x061,  2,  2,   "V",           "V V", False), # 11
           "ATANH": (0x0ea,  1,  1,   "V",             "V", False), # 12
          "AVEDEV": (0x10d,  1, 30,   "V",         "R ...", False), # 13
         "AVERAGE": (0x005,  1, 30,   "V",         "R ...", False), # 14
        "AVERAGEA": (0x169,  1, 30,   "V",         "R ...", False), # 15
        "BETADIST": (0x10e,  3,  5,   "V",     "V V V V V", False), # 16
         "BETAINV": (0x110,  3,  5,   "V",     "V V V V V", False), # 17
       "BINOMDIST": (0x111,  4,  4,   "V",       "V V V V", False), # 18
         "CEILING": (0x120,  2,  2,   "V",           "V V", False), # 19
            "CELL": (0x07d,  1,  2,   "V",           "V R",  True), # 20
            "CHAR": (0x06f,  1,  1,   "V",             "V", False), # 21
         "CHIDIST": (0x112,  2,  2,   "V",           "V V", False), # 22
          "CHIINV": (0x113,  2,  2,   "V",           "V V", False), # 23
         "CHITEST": (0x132,  2,  2,   "V",           "A A", False), # 24
          "CHOOSE": (0x064,  2, 30,   "R",       "V R ...", False), # 25
           "CLEAN": (0x0a2,  1,  1,   "V",             "V", False), # 26
            "CODE": (0x079,  1,  1,   "V",             "V", False), # 27
          "COLUMN": (0x009,  0,  1,   "V",             "R", False), # 28
         "COLUMNS": (0x04d,  1,  1,   "V",             "R", False), # 29
          "COMBIN": (0x114,  2,  2,   "V",           "V V", False), # 30
     "CONCATENATE": (0x150,  0, 30,   "V",         "V ...", False), # 31
      "CONFIDENCE": (0x115,  3,  3,   "V",         "V V V", False), # 32
          "CORREL": (0x133,  2,  2,   "V",           "A A", False), # 33
             "COS": (0x010,  1,  1,   "V",             "V", False), # 34
            "COSH": (0x0e6,  1,  1,   "V",             "V", False), # 35
           "COUNT": (0x000,  0, 30,   "V",         "R ...", False), # 36
          "COUNTA": (0x0a9,  0, 30,   "V",         "R ...", False), # 37
      "COUNTBLANK": (0x15b,  1,  1,   "V",             "R", False), # 38
         "COUNTIF": (0x15a,  2,  2,   "V",           "R V", False), # 39
           "COVAR": (0x134,  2,  2,   "V",           "A A", False), # 40
       "CRITBINOM": (0x116,  3,  3,   "V",         "V V V", False), # 41
            "DATE": (0x041,  3,  3,   "V",         "V V V", False), # 42
         "DATEDIF": (0x15f,  3,  3,   "V",         "V V V", False), # 43
      "DATESTRING": (0x160,  1,  1,   "V",             "V", False), # 44
       "DATEVALUE": (0x08c,  1,  1,   "V",             "V", False), # 45
        "DAVERAGE": (0x02a,  3,  3,   "V",         "R R R", False), # 46
             "DAY": (0x043,  1,  1,   "V",             "V", False), # 47
         "DAYS360": (0x0dc,  2,  3,   "V",         "V V V", False), # 48
              "DB": (0x0f7,  4,  5,   "V",     "V V V V V", False), # 49
            "DBSC": (0x0d7,  1,  1,   "V",             "V", False), # 50
          "DCOUNT": (0x028,  3,  3,   "V",         "R R R", False), # 51
         "DCOUNTA": (0x0c7,  3,  3,   "V",         "R R R", False), # 52
             "DDB": (0x090,  4,  5,   "V",     "V V V V V", False), # 53
         "DEGREES": (0x157,  1,  1,   "V",             "V", False), # 54
           "DEVSQ": (0x13e,  1, 30,   "V",         "R ...", False), # 55
            "DGET": (0x0eb,  3,  3,   "V",         "R R R", False), # 56
            "DMAX": (0x02c,  3,  3,   "V",         "R R R", False), # 57
            "DMIN": (0x02b,  3,  3,   "V",         "R R R", False), # 58
          "DOLLAR": (0x00d,  1,  2,   "V",           "V V", False), # 59
        "DPRODUCT": (0x0bf,  3,  3,   "V",         "R R R", False), # 60
          "DSTDEV": (0x02d,  3,  3,   "V",         "R R R", False), # 61
         "DSTDEVP": (0x0c3,  3,  3,   "V",         "R R R", False), # 62
            "DSUM": (0x029,  3,  3,   "V",         "R R R", False), # 63
            "DVAR": (0x02f,  3,  3,   "V",         "R R R", False), # 64
           "DVARP": (0x0c4,  3,  3,   "V",         "R R R", False), # 65
      "ERROR.TYPE": (0x105,  1,  1,   "V",             "V", False), # 66
            "EVEN": (0x117,  1,  1,   "V",             "V", False), # 67
           "EXACT": (0x075,  2,  2,   "V",           "V V", False), # 68
             "EXP": (0x015,  1,  1,   "V",             "V", False), # 69
       "EXPONDIST": (0x118,  3,  3,   "V",         "V V V", False), # 70
            "FACT": (0x0b8,  1,  1,   "V",             "V", False), # 71
           "FALSE": (0x023,  0,  0,   "V",             "-", False), # 72
           "FDIST": (0x119,  3,  3,   "V",         "V V V", False), # 73
            "FIND": (0x07c,  2,  3,   "V",         "V V V", False), # 74
           "FINDB": (0x0cd,  2,  3,   "V",         "V V V", False), # 75
            "FINV": (0x11a,  3,  3,   "V",         "V V V", False), # 76
          "FISHER": (0x11b,  1,  1,   "V",             "V", False), # 77
       "FISHERINV": (0x11c,  1,  1,   "V",             "V", False), # 78
           "FIXED": (0x00e,  2,  3,   "V",         "V V V", False), # 79
           "FLOOR": (0x11d,  2,  2,   "V",           "V V", False), # 80
        "FORECAST": (0x135,  3,  3,   "V",         "V A A", False), # 81
       "FREQUENCY": (0x0fc,  2,  2,   "A",           "R R", False), # 82
           "FTEST": (0x136,  2,  2,   "V",           "A A", False), # 83
              "FV": (0x039,  3,  5,   "V",     "V V V V V", False), # 84
       "GAMMADIST": (0x11e,  4,  4,   "V",       "V V V V", False), # 85
        "GAMMAINV": (0x11f,  3,  3,   "V",         "V V V", False), # 86
         "GAMMALN": (0x10f,  1,  1,   "V",             "V", False), # 87
         "GEOMEAN": (0x13f,  1, 30,   "V",         "R ...", False), # 88
    "GETPIVOTDATA": (0x166,  2, 30,   "A",             "-", False), # 89
          "GROWTH": (0x034,  1,  4,   "A",       "R R R V", False), # 90
         "HARMEAN": (0x140,  1, 30,   "V",         "R ...", False), # 91
         "HLOOKUP": (0x065,  3,  4,   "V",       "V R R V", False), # 92
            "HOUR": (0x047,  1,  1,   "V",             "V", False), # 93
       "HYPERLINK": (0x167,  1,  2,   "V",           "V V", False), # 94
     "HYPGEOMVERT": (0x121,  4,  4,   "V",       "V V V V", False), # 95
              "IF": (0x001,  2,  3,   "R",         "V R R", False), # 96
           "INDEX": (0x01d,  2,  4,   "R",       "R V V V", False), # 97
        "INDIRECT": (0x094,  1,  2,   "R",           "V V",  True), # 98
            "INFO": (0x0f4,  1,  1,   "V",             "V", False), # 99
             "INT": (0x019,  1,  1,   "V",             "V", False), # 100
       "INTERCEPT": (0x137,  2,  2,   "V",           "A A", False), # 101
            "IPMT": (0x0a7,  4,  6,   "V",   "V V V V V V", False), # 102
             "IRR": (0x03e,  1,  2,   "V",           "R V", False), # 103
         "ISBLANK": (0x081,  1,  1,   "V",             "V", False), # 104
           "ISERR": (0x07e,  1,  1,   "V",             "V", False), # 105
         "ISERROR": (0x003,  1,  1,   "V",             "V", False), # 106
       "ISLOGICAL": (0x0c6,  1,  1,   "V",             "V", False), # 107
            "ISNA": (0x002,  1,  1,   "V",             "V", False), # 108
       "ISNONTEXT": (0x0c0,  1,  1,   "V",             "V", False), # 109
        "ISNUMBER": (0x080,  1,  1,   "V",             "V", False), # 110
           "ISPMT": (0x15e,  4,  4,   "V",       "V V V V", False), # 111
           "ISREF": (0x069,  1,  1,   "V",             "R", False), # 112
          "ISTEXT": (0x07f,  1,  1,   "V",             "V", False), # 113
            "KURT": (0x142,  1, 30,   "V",         "R ...", False), # 114
           "LARGE": (0x145,  2,  2,   "V",           "R V", False), # 115
            "LEFT": (0x073,  1,  2,   "V",           "V V", False), # 116
           "LEFTB": (0x0d0,  1,  2,   "V",           "V V", False), # 117
             "LEN": (0x020,  1,  1,   "V",             "V", False), # 118
            "LENB": (0x0d3,  1,  1,   "V",             "V", False), # 119
          "LINEST": (0x031,  1,  4,   "A",       "R R V V", False), # 120
              "LN": (0x016,  1,  1,   "V",             "V", False), # 121
             "LOG": (0x06d,  1,  2,   "V",           "V V", False), # 122
           "LOG10": (0x017,  1,  1,   "V",             "V", False), # 123
          "LOGEST": (0x033,  1,  4,   "A",       "R R V V", False), # 124
          "LOGINV": (0x123,  3,  3,   "V",         "V V V", False), # 125
     "LOGNORMDIST": (0x122,  3,  3,   "V",         "V V V", False), # 126
          "LOOKUP": (0x01c,  2,  3,   "V",         "V R R", False), # 127
           "LOWER": (0x070,  1,  1,   "V",             "V", False), # 128
           "MATCH": (0x040,  2,  3,   "V",         "V R R", False), # 129
             "MAX": (0x007,  1, 30,   "V",         "R ...", False), # 130
            "MAXA": (0x16a,  1, 30,   "V",         "R ...", False), # 131
         "MDETERM": (0x0a3,  1,  1,   "V",             "A", False), # 132
          "MEDIAN": (0x0e3,  1, 30,   "V",         "R ...", False), # 133
             "MID": (0x01f,  3,  3,   "V",         "V V V", False), # 134
            "MIDB": (0x0d2,  3,  3,   "V",         "V V V", False), # 135
             "MIN": (0x006,  1, 30,   "V",         "R ...", False), # 136
            "MINA": (0x16b,  1, 30,   "V",         "R ...", False), # 137
          "MINUTE": (0x048,  1,  1,   "V",             "V", False), # 138
        "MINVERSE": (0x0a4,  1,  1,   "A",             "A", False), # 139
            "MIRR": (0x03d,  3,  3,   "V",         "R V V", False), # 140
           "MMULT": (0x0a5,  2,  2,   "A",           "A A", False), # 141
       "MNORMSINV": (0x128,  1,  1,   "V",             "V", False), # 142
             "MOD": (0x027,  2,  2,   "V",           "V V", False), # 143
            "MODE": (0x14a,  1, 30,   "V",         "A ...", False), # 144
           "MONTH": (0x044,  1,  1,   "V",             "V", False), # 145
               "N": (0x083,  1,  1,   "V",             "R", False), # 146
              "NA": (0x00a,  0,  0,   "V",             "-", False), # 147
    "NEGBINOMDIST": (0x124,  3,  3,   "V",         "V V V", False), # 148
        "NORMDIST": (0x125,  4,  4,   "V",       "V V V V", False), # 149
         "NORMINV": (0x127,  3,  3,   "V",         "V V V", False), # 150
       "NORMSDIST": (0x126,  1,  1,   "V",             "V", False), # 151
             "NOT": (0x026,  1,  1,   "V",             "V", False), # 152
             "NOW": (0x04a,  0,  0,   "V",             "-",  True), # 153
            "NPER": (0x03a,  3,  5,   "V",     "V V V V V", False), # 154
             "NPV": (0x00b,  2, 30,   "V",       "V R ...", False), # 155
    "NUMBERSTRING": (0x161,  2,  2,   "V",           "V V", False), # 156
             "ODD": (0x12a,  1,  1,   "V",             "V", False), # 157
          "OFFSET": (0x04e,  3,  5,   "R",     "R V V V V",  True), # 158
              "OR": (0x025,  1, 30,   "V",         "R ...", False), # 159
         "PEARSON": (0x138,  2,  2,   "V",           "A A", False), # 160
      "PERCENTILE": (0x148,  2,  2,   "V",           "R V", False), # 161
     "PERCENTRANK": (0x149,  2,  3,   "V",         "R V V", False), # 162
          "PERMUT": (0x12b,  2,  2,   "V",           "V V", False), # 163
        "PHONETIC": (0x168,  1,  1,   "V",             "R", False), # 164
              "PI": (0x013,  0,  0,   "V",             "-", False), # 165
             "PMT": (0x03b,  3,  5,   "V",     "V V V V V", False), # 166
         "POISSON": (0x12c,  3,  3,   "V",         "V V V", False), # 167
           "POWER": (0x151,  2,  2,   "V",           "V V", False), # 168
            "PPMT": (0x0a8,  4,  6,   "V",   "V V V V V V", False), # 169
            "PROB": (0x13d,  3,  4,   "V",       "A A V V", False), # 170
         "PRODUCT": (0x0b7,  0, 30,   "V",         "R ...", False), # 171
          "PROPER": (0x072,  1,  1,   "V",             "V", False), # 172
              "PV": (0x038,  3,  5,   "V",     "V V V V V", False), # 173
        "QUARTILE": (0x147,  2,  2,   "V",           "R V", False), # 174
         "RADIANS": (0x156,  1,  1,   "V",             "V", False), # 175
            "RAND": (0x03f,  0,  0,   "V",             "-",  True), # 176
            "RANK": (0x0d8,  2,  3,   "V",         "V R V", False), # 177
            "RATE": (0x03c,  3,  6,   "V",   "V V V V V V", False), # 178
         "REPLACE": (0x077,  4,  4,   "V",       "V V V V", False), # 179
        "REPLACEB": (0x0cf,  4,  4,   "V",       "V V V V", False), # 180
            "REPT": (0x01e,  2,  2,   "V",           "V V", False), # 181
           "RIGHT": (0x074,  1,  2,   "V",           "V V", False), # 182
          "RIGHTB": (0x0d1,  1,  2,   "V",           "V V", False), # 183
           "ROMAN": (0x162,  1,  2,   "V",           "V V", False), # 184
           "ROUND": (0x01b,  2,  2,   "V",           "V V", False), # 185
       "ROUNDDOWN": (0x0d5,  2,  2,   "V",           "V V", False), # 186
         "ROUNDUP": (0x0d4,  2,  2,   "V",           "V V", False), # 187
             "ROW": (0x008,  0,  1,   "V",             "R", False), # 188
            "ROWS": (0x04c,  1,  1,   "V",             "R", False), # 189
             "RSQ": (0x139,  2,  2,   "V",           "A A", False), # 190
          "SEARCH": (0x052,  2,  3,   "V",         "V V V", False), # 191
         "SEARCHB": (0x0ce,  2,  3,   "V",         "V V V", False), # 192
          "SECOND": (0x049,  1,  1,   "V",             "V", False), # 193
            "SIGN": (0x01a,  1,  1,   "V",             "V", False), # 194
             "SIN": (0x00f,  1,  1,   "V",             "V", False), # 195
            "SINH": (0x0e5,  1,  1,   "V",             "V", False), # 196
            "SKEW": (0x143,  1, 30,   "V",         "R ...", False), # 197
             "SLN": (0x08e,  3,  3,   "V",         "V V V", False), # 198
           "SLOPE": (0x13b,  2,  2,   "V",           "A A", False), # 199
           "SMALL": (0x146,  2,  2,   "V",           "R V", False), # 200
            "SQRT": (0x014,  1,  1,   "V",             "V", False), # 201
     "STANDARDIZE": (0x129,  3,  3,   "V",         "V V V", False), # 202
           "STDEV": (0x00c,  1, 30,   "V",         "R ...", False), # 203
          "STDEVA": (0x16e,  1, 30,   "V",         "R ...", False), # 204
          "STDEVP": (0x0c1,  1, 30,   "V",         "R ...", False), # 205
         "STDEVPA": (0x16c,  1, 30,   "V",         "R ...", False), # 206
           "STEYX": (0x13a,  2,  2,   "V",           "A A", False), # 207
      "SUBSTITUTE": (0x078,  3,  4,   "V",       "V V V V", False), # 208
        "SUBTOTAL": (0x158,  2, 30,   "V",       "V R ...", False), # 209
             "SUM": (0x004,  0, 30,   "V",         "R ...", False), # 210
           "SUMIF": (0x159,  2,  3,   "V",         "R V R", False), # 211
      "SUMPRODUCT": (0x0e4,  1, 30,   "V",         "A ...", False), # 212
           "SUMSQ": (0x141,  0, 30,   "V",         "R ...", False), # 213
        "SUMX2MY2": (0x130,  2,  2,   "V",           "A A", False), # 214
        "SUMX2PY2": (0x131,  2,  2,   "V",           "A A", False), # 215
         "SUMXMY2": (0x12f,  2,  2,   "V",           "A A", False), # 216
             "SYD": (0x08f,  4,  4,   "V",       "V V V V", False), # 217
               "T": (0x082,  1,  1,   "V",             "R", False), # 218
             "TAN": (0x011,  1,  1,   "V",             "V", False), # 219
            "TANH": (0x0e7,  1,  1,   "V",             "V", False), # 220
           "TDIST": (0x12d,  3,  3,   "V",         "V V V", False), # 221
            "TEXT": (0x030,  2,  2,   "V",           "V V", False), # 222
            "TIME": (0x042,  3,  3,   "V",         "V V V", False), # 223
       "TIMEVALUE": (0x08d,  1,  1,   "V",             "V", False), # 224
            "TINV": (0x14c,  2,  2,   "V",           "V V", False), # 225
           "TODAY": (0x0dd,  0,  0,   "V",             "-",  True), # 226
       "TRANSPOSE": (0x053,  1,  1,   "A",             "A", False), # 227
           "TREND": (0x032,  1,  4,   "A",       "R R R V", False), # 228
            "TRIM": (0x076,  1,  1,   "V",             "V", False), # 229
        "TRIMMEAN": (0x14b,  2,  2,   "V",           "R V", False), # 230
            "TRUE": (0x022,  0,  0,   "V",             "-", False), # 231
           "TRUNC": (0x0c5,  1,  2,   "V",           "V V", False), # 232
           "TTEST": (0x13c,  4,  4,   "V",       "A A V V", False), # 233
            "TYPE": (0x056,  1,  1,   "V",             "V", False), # 234
           "UPPER": (0x071,  1,  1,   "V",             "V", False), # 235
        "USDOLLAR": (0x0cc,  1,  2,   "V",           "V V", False), # 236
           "VALUE": (0x021,  1,  1,   "V",             "V", False), # 237
             "VAR": (0x02e,  1, 30,   "V",         "R ...", False), # 238
            "VARA": (0x16f,  1, 30,   "V",         "R ...", False), # 239
            "VARP": (0x0c2,  1, 30,   "V",         "R ...", False), # 240
           "VARPA": (0x16d,  1, 30,   "V",         "R ...", False), # 241
             "VDB": (0x0de,  5,  7,   "V", "V V V V V V V", False), # 242
         "VLOOKUP": (0x066,  3,  4,   "V",       "V R R V", False), # 243
         "WEEKDAY": (0x046,  1,  2,   "V",           "V V", False), # 244
         "WEIBULL": (0x12e,  4,  4,   "V",       "V V V V", False), # 245
            "YEAR": (0x045,  1,  1,   "V",             "V", False), # 246
           "ZTEST": (0x144,  2,  3,   "V",         "R V V", False)  # 247
}


std_func_by_num = {
    0x000: (       "COUNT",  0, 30,   "V",         "R ...", False), # 1
    0x001: (          "IF",  2,  3,   "R",         "V R R", False), # 2
    0x002: (        "ISNA",  1,  1,   "V",             "V", False), # 3
    0x003: (     "ISERROR",  1,  1,   "V",             "V", False), # 4
    0x004: (         "SUM",  0, 30,   "V",         "R ...", False), # 5
    0x005: (     "AVERAGE",  1, 30,   "V",         "R ...", False), # 6
    0x006: (         "MIN",  1, 30,   "V",         "R ...", False), # 7
    0x007: (         "MAX",  1, 30,   "V",         "R ...", False), # 8
    0x008: (         "ROW",  0,  1,   "V",             "R", False), # 9
    0x009: (      "COLUMN",  0,  1,   "V",             "R", False), # 10
    0x00a: (          "NA",  0,  0,   "V",             "-", False), # 11
    0x00b: (         "NPV",  2, 30,   "V",       "V R ...", False), # 12
    0x00c: (       "STDEV",  1, 30,   "V",         "R ...", False), # 13
    0x00d: (      "DOLLAR",  1,  2,   "V",           "V V", False), # 14
    0x00e: (       "FIXED",  2,  3,   "V",         "V V V", False), # 15
    0x00f: (         "SIN",  1,  1,   "V",             "V", False), # 16
    0x010: (         "COS",  1,  1,   "V",             "V", False), # 17
    0x011: (         "TAN",  1,  1,   "V",             "V", False), # 18
    0x012: (      "ARCTAN",  1,  1,   "V",             "V", False), # 19
    0x013: (          "PI",  0,  0,   "V",             "-", False), # 20
    0x014: (        "SQRT",  1,  1,   "V",             "V", False), # 21
    0x015: (         "EXP",  1,  1,   "V",             "V", False), # 22
    0x016: (          "LN",  1,  1,   "V",             "V", False), # 23
    0x017: (       "LOG10",  1,  1,   "V",             "V", False), # 24
    0x018: (         "ABS",  1,  1,   "V",             "V", False), # 25
    0x019: (         "INT",  1,  1,   "V",             "V", False), # 26
    0x01a: (        "SIGN",  1,  1,   "V",             "V", False), # 27
    0x01b: (       "ROUND",  2,  2,   "V",           "V V", False), # 28
    0x01c: (      "LOOKUP",  2,  3,   "V",         "V R R", False), # 29
    0x01d: (       "INDEX",  2,  4,   "R",       "R V V V", False), # 30
    0x01e: (        "REPT",  2,  2,   "V",           "V V", False), # 31
    0x01f: (         "MID",  3,  3,   "V",         "V V V", False), # 32
    0x020: (         "LEN",  1,  1,   "V",             "V", False), # 33
    0x021: (       "VALUE",  1,  1,   "V",             "V", False), # 34
    0x022: (        "TRUE",  0,  0,   "V",             "-", False), # 35
    0x023: (       "FALSE",  0,  0,   "V",             "-", False), # 36
    0x024: (         "AND",  1, 30,   "V",         "R ...", False), # 37
    0x025: (          "OR",  1, 30,   "V",         "R ...", False), # 38
    0x026: (         "NOT",  1,  1,   "V",             "V", False), # 39
    0x027: (         "MOD",  2,  2,   "V",           "V V", False), # 40
    0x028: (      "DCOUNT",  3,  3,   "V",         "R R R", False), # 41
    0x029: (        "DSUM",  3,  3,   "V",         "R R R", False), # 42
    0x02a: (    "DAVERAGE",  3,  3,   "V",         "R R R", False), # 43
    0x02b: (        "DMIN",  3,  3,   "V",         "R R R", False), # 44
    0x02c: (        "DMAX",  3,  3,   "V",         "R R R", False), # 45
    0x02d: (      "DSTDEV",  3,  3,   "V",         "R R R", False), # 46
    0x02e: (         "VAR",  1, 30,   "V",         "R ...", False), # 47
    0x02f: (        "DVAR",  3,  3,   "V",         "R R R", False), # 48
    0x030: (        "TEXT",  2,  2,   "V",           "V V", False), # 49
    0x031: (      "LINEST",  1,  4,   "A",       "R R V V", False), # 50
    0x032: (       "TREND",  1,  4,   "A",       "R R R V", False), # 51
    0x033: (      "LOGEST",  1,  4,   "A",       "R R V V", False), # 52
    0x034: (      "GROWTH",  1,  4,   "A",       "R R R V", False), # 53
    0x038: (          "PV",  3,  5,   "V",     "V V V V V", False), # 54
    0x039: (          "FV",  3,  5,   "V",     "V V V V V", False), # 55
    0x03a: (        "NPER",  3,  5,   "V",     "V V V V V", False), # 56
    0x03b: (         "PMT",  3,  5,   "V",     "V V V V V", False), # 57
    0x03c: (        "RATE",  3,  6,   "V",   "V V V V V V", False), # 58
    0x03d: (        "MIRR",  3,  3,   "V",         "R V V", False), # 59
    0x03e: (         "IRR",  1,  2,   "V",           "R V", False), # 60
    0x03f: (        "RAND",  0,  0,   "V",             "-",  True), # 61
    0x040: (       "MATCH",  2,  3,   "V",         "V R R", False), # 62
    0x041: (        "DATE",  3,  3,   "V",         "V V V", False), # 63
    0x042: (        "TIME",  3,  3,   "V",         "V V V", False), # 64
    0x043: (         "DAY",  1,  1,   "V",             "V", False), # 65
    0x044: (       "MONTH",  1,  1,   "V",             "V", False), # 66
    0x045: (        "YEAR",  1,  1,   "V",             "V", False), # 67
    0x046: (     "WEEKDAY",  1,  2,   "V",           "V V", False), # 68
    0x047: (        "HOUR",  1,  1,   "V",             "V", False), # 69
    0x048: (      "MINUTE",  1,  1,   "V",             "V", False), # 70
    0x049: (      "SECOND",  1,  1,   "V",             "V", False), # 71
    0x04a: (         "NOW",  0,  0,   "V",             "-",  True), # 72
    0x04b: (       "AREAS",  1,  1,   "V",             "R", False), # 73
    0x04c: (        "ROWS",  1,  1,   "V",             "R", False), # 74
    0x04d: (     "COLUMNS",  1,  1,   "V",             "R", False), # 75
    0x04e: (      "OFFSET",  3,  5,   "R",     "R V V V V",  True), # 76
    0x052: (      "SEARCH",  2,  3,   "V",         "V V V", False), # 77
    0x053: (   "TRANSPOSE",  1,  1,   "A",             "A", False), # 78
    0x056: (        "TYPE",  1,  1,   "V",             "V", False), # 79
    0x061: (       "ATAN2",  2,  2,   "V",           "V V", False), # 80
    0x062: (        "ASIN",  1,  1,   "V",             "V", False), # 81
    0x063: (        "ACOS",  1,  1,   "V",             "V", False), # 82
    0x064: (      "CHOOSE",  2, 30,   "R",       "V R ...", False), # 83
    0x065: (     "HLOOKUP",  3,  4,   "V",       "V R R V", False), # 84
    0x066: (     "VLOOKUP",  3,  4,   "V",       "V R R V", False), # 85
    0x069: (       "ISREF",  1,  1,   "V",             "R", False), # 86
    0x06d: (         "LOG",  1,  2,   "V",           "V V", False), # 87
    0x06f: (        "CHAR",  1,  1,   "V",             "V", False), # 88
    0x070: (       "LOWER",  1,  1,   "V",             "V", False), # 89
    0x071: (       "UPPER",  1,  1,   "V",             "V", False), # 90
    0x072: (      "PROPER",  1,  1,   "V",             "V", False), # 91
    0x073: (        "LEFT",  1,  2,   "V",           "V V", False), # 92
    0x074: (       "RIGHT",  1,  2,   "V",           "V V", False), # 93
    0x075: (       "EXACT",  2,  2,   "V",           "V V", False), # 94
    0x076: (        "TRIM",  1,  1,   "V",             "V", False), # 95
    0x077: (     "REPLACE",  4,  4,   "V",       "V V V V", False), # 96
    0x078: (  "SUBSTITUTE",  3,  4,   "V",       "V V V V", False), # 97
    0x079: (        "CODE",  1,  1,   "V",             "V", False), # 98
    0x07c: (        "FIND",  2,  3,   "V",         "V V V", False), # 99
    0x07d: (        "CELL",  1,  2,   "V",           "V R",  True), # 100
    0x07e: (       "ISERR",  1,  1,   "V",             "V", False), # 101
    0x07f: (      "ISTEXT",  1,  1,   "V",             "V", False), # 102
    0x080: (    "ISNUMBER",  1,  1,   "V",             "V", False), # 103
    0x081: (     "ISBLANK",  1,  1,   "V",             "V", False), # 104
    0x082: (           "T",  1,  1,   "V",             "R", False), # 105
    0x083: (           "N",  1,  1,   "V",             "R", False), # 106
    0x08c: (   "DATEVALUE",  1,  1,   "V",             "V", False), # 107
    0x08d: (   "TIMEVALUE",  1,  1,   "V",             "V", False), # 108
    0x08e: (         "SLN",  3,  3,   "V",         "V V V", False), # 109
    0x08f: (         "SYD",  4,  4,   "V",       "V V V V", False), # 110
    0x090: (         "DDB",  4,  5,   "V",     "V V V V V", False), # 111
    0x094: (    "INDIRECT",  1,  2,   "R",           "V V",  True), # 112
    0x0a2: (       "CLEAN",  1,  1,   "V",             "V", False), # 113
    0x0a3: (     "MDETERM",  1,  1,   "V",             "A", False), # 114
    0x0a4: (    "MINVERSE",  1,  1,   "A",             "A", False), # 115
    0x0a5: (       "MMULT",  2,  2,   "A",           "A A", False), # 116
    0x0a7: (        "IPMT",  4,  6,   "V",   "V V V V V V", False), # 117
    0x0a8: (        "PPMT",  4,  6,   "V",   "V V V V V V", False), # 118
    0x0a9: (      "COUNTA",  0, 30,   "V",         "R ...", False), # 119
    0x0b7: (     "PRODUCT",  0, 30,   "V",         "R ...", False), # 120
    0x0b8: (        "FACT",  1,  1,   "V",             "V", False), # 121
    0x0bf: (    "DPRODUCT",  3,  3,   "V",         "R R R", False), # 122
    0x0c0: (   "ISNONTEXT",  1,  1,   "V",             "V", False), # 123
    0x0c1: (      "STDEVP",  1, 30,   "V",         "R ...", False), # 124
    0x0c2: (        "VARP",  1, 30,   "V",         "R ...", False), # 125
    0x0c3: (     "DSTDEVP",  3,  3,   "V",         "R R R", False), # 126
    0x0c4: (       "DVARP",  3,  3,   "V",         "R R R", False), # 127
    0x0c5: (       "TRUNC",  1,  2,   "V",           "V V", False), # 128
    0x0c6: (   "ISLOGICAL",  1,  1,   "V",             "V", False), # 129
    0x0c7: (     "DCOUNTA",  3,  3,   "V",         "R R R", False), # 130
    0x0cc: (    "USDOLLAR",  1,  2,   "V",           "V V", False), # 131
    0x0cd: (       "FINDB",  2,  3,   "V",         "V V V", False), # 132
    0x0ce: (     "SEARCHB",  2,  3,   "V",         "V V V", False), # 133
    0x0cf: (    "REPLACEB",  4,  4,   "V",       "V V V V", False), # 134
    0x0d0: (       "LEFTB",  1,  2,   "V",           "V V", False), # 135
    0x0d1: (      "RIGHTB",  1,  2,   "V",           "V V", False), # 136
    0x0d2: (        "MIDB",  3,  3,   "V",         "V V V", False), # 137
    0x0d3: (        "LENB",  1,  1,   "V",             "V", False), # 138
    0x0d4: (     "ROUNDUP",  2,  2,   "V",           "V V", False), # 139
    0x0d5: (   "ROUNDDOWN",  2,  2,   "V",           "V V", False), # 140
    0x0d6: (         "ASC",  1,  1,   "V",             "V", False), # 141
    0x0d7: (        "DBSC",  1,  1,   "V",             "V", False), # 142
    0x0d8: (        "RANK",  2,  3,   "V",         "V R V", False), # 143
    0x0db: (     "ADDRESS",  2,  5,   "V",     "V V V V V", False), # 144
    0x0dc: (     "DAYS360",  2,  3,   "V",         "V V V", False), # 145
    0x0dd: (       "TODAY",  0,  0,   "V",             "-",  True), # 146
    0x0de: (         "VDB",  5,  7,   "V", "V V V V V V V", False), # 147
    0x0e3: (      "MEDIAN",  1, 30,   "V",         "R ...", False), # 148
    0x0e4: (  "SUMPRODUCT",  1, 30,   "V",         "A ...", False), # 149
    0x0e5: (        "SINH",  1,  1,   "V",             "V", False), # 150
    0x0e6: (        "COSH",  1,  1,   "V",             "V", False), # 151
    0x0e7: (        "TANH",  1,  1,   "V",             "V", False), # 152
    0x0e8: (       "ASINH",  1,  1,   "V",             "V", False), # 153
    0x0e9: (       "ACOSH",  1,  1,   "V",             "V", False), # 154
    0x0ea: (       "ATANH",  1,  1,   "V",             "V", False), # 155
    0x0eb: (        "DGET",  3,  3,   "V",         "R R R", False), # 156
    0x0f4: (        "INFO",  1,  1,   "V",             "V", False), # 157
    0x0f7: (          "DB",  4,  5,   "V",     "V V V V V", False), # 158
    0x0fc: (   "FREQUENCY",  2,  2,   "A",           "R R", False), # 159
    0x105: (  "ERROR.TYPE",  1,  1,   "V",             "V", False), # 160
    0x10d: (      "AVEDEV",  1, 30,   "V",         "R ...", False), # 161
    0x10e: (    "BETADIST",  3,  5,   "V",     "V V V V V", False), # 162
    0x10f: (     "GAMMALN",  1,  1,   "V",             "V", False), # 163
    0x110: (     "BETAINV",  3,  5,   "V",     "V V V V V", False), # 164
    0x111: (   "BINOMDIST",  4,  4,   "V",       "V V V V", False), # 165
    0x112: (     "CHIDIST",  2,  2,   "V",           "V V", False), # 166
    0x113: (      "CHIINV",  2,  2,   "V",           "V V", False), # 167
    0x114: (      "COMBIN",  2,  2,   "V",           "V V", False), # 168
    0x115: (  "CONFIDENCE",  3,  3,   "V",         "V V V", False), # 169
    0x116: (   "CRITBINOM",  3,  3,   "V",         "V V V", False), # 170
    0x117: (        "EVEN",  1,  1,   "V",             "V", False), # 171
    0x118: (   "EXPONDIST",  3,  3,   "V",         "V V V", False), # 172
    0x119: (       "FDIST",  3,  3,   "V",         "V V V", False), # 173
    0x11a: (        "FINV",  3,  3,   "V",         "V V V", False), # 174
    0x11b: (      "FISHER",  1,  1,   "V",             "V", False), # 175
    0x11c: (   "FISHERINV",  1,  1,   "V",             "V", False), # 176
    0x11d: (       "FLOOR",  2,  2,   "V",           "V V", False), # 177
    0x11e: (   "GAMMADIST",  4,  4,   "V",       "V V V V", False), # 178
    0x11f: (    "GAMMAINV",  3,  3,   "V",         "V V V", False), # 179
    0x120: (     "CEILING",  2,  2,   "V",           "V V", False), # 180
    0x121: ( "HYPGEOMVERT",  4,  4,   "V",       "V V V V", False), # 181
    0x122: ( "LOGNORMDIST",  3,  3,   "V",         "V V V", False), # 182
    0x123: (      "LOGINV",  3,  3,   "V",         "V V V", False), # 183
    0x124: ("NEGBINOMDIST",  3,  3,   "V",         "V V V", False), # 184
    0x125: (    "NORMDIST",  4,  4,   "V",       "V V V V", False), # 185
    0x126: (   "NORMSDIST",  1,  1,   "V",             "V", False), # 186
    0x127: (     "NORMINV",  3,  3,   "V",         "V V V", False), # 187
    0x128: (   "MNORMSINV",  1,  1,   "V",             "V", False), # 188
    0x129: ( "STANDARDIZE",  3,  3,   "V",         "V V V", False), # 189
    0x12a: (         "ODD",  1,  1,   "V",             "V", False), # 190
    0x12b: (      "PERMUT",  2,  2,   "V",           "V V", False), # 191
    0x12c: (     "POISSON",  3,  3,   "V",         "V V V", False), # 192
    0x12d: (       "TDIST",  3,  3,   "V",         "V V V", False), # 193
    0x12e: (     "WEIBULL",  4,  4,   "V",       "V V V V", False), # 194
    0x12f: (     "SUMXMY2",  2,  2,   "V",           "A A", False), # 195
    0x130: (    "SUMX2MY2",  2,  2,   "V",           "A A", False), # 196
    0x131: (    "SUMX2PY2",  2,  2,   "V",           "A A", False), # 197
    0x132: (     "CHITEST",  2,  2,   "V",           "A A", False), # 198
    0x133: (      "CORREL",  2,  2,   "V",           "A A", False), # 199
    0x134: (       "COVAR",  2,  2,   "V",           "A A", False), # 200
    0x135: (    "FORECAST",  3,  3,   "V",         "V A A", False), # 201
    0x136: (       "FTEST",  2,  2,   "V",           "A A", False), # 202
    0x137: (   "INTERCEPT",  2,  2,   "V",           "A A", False), # 203
    0x138: (     "PEARSON",  2,  2,   "V",           "A A", False), # 204
    0x139: (         "RSQ",  2,  2,   "V",           "A A", False), # 205
    0x13a: (       "STEYX",  2,  2,   "V",           "A A", False), # 206
    0x13b: (       "SLOPE",  2,  2,   "V",           "A A", False), # 207
    0x13c: (       "TTEST",  4,  4,   "V",       "A A V V", False), # 208
    0x13d: (        "PROB",  3,  4,   "V",       "A A V V", False), # 209
    0x13e: (       "DEVSQ",  1, 30,   "V",         "R ...", False), # 210
    0x13f: (     "GEOMEAN",  1, 30,   "V",         "R ...", False), # 211
    0x140: (     "HARMEAN",  1, 30,   "V",         "R ...", False), # 212
    0x141: (       "SUMSQ",  0, 30,   "V",         "R ...", False), # 213
    0x142: (        "KURT",  1, 30,   "V",         "R ...", False), # 214
    0x143: (        "SKEW",  1, 30,   "V",         "R ...", False), # 215
    0x144: (       "ZTEST",  2,  3,   "V",         "R V V", False), # 216
    0x145: (       "LARGE",  2,  2,   "V",           "R V", False), # 217
    0x146: (       "SMALL",  2,  2,   "V",           "R V", False), # 218
    0x147: (    "QUARTILE",  2,  2,   "V",           "R V", False), # 219
    0x148: (  "PERCENTILE",  2,  2,   "V",           "R V", False), # 220
    0x149: ( "PERCENTRANK",  2,  3,   "V",         "R V V", False), # 221
    0x14a: (        "MODE",  1, 30,   "V",         "A ...", False), # 222
    0x14b: (    "TRIMMEAN",  2,  2,   "V",           "R V", False), # 223
    0x14c: (        "TINV",  2,  2,   "V",           "V V", False), # 224
    0x150: ( "CONCATENATE",  0, 30,   "V",         "V ...", False), # 225
    0x151: (       "POWER",  2,  2,   "V",           "V V", False), # 226
    0x156: (     "RADIANS",  1,  1,   "V",             "V", False), # 227
    0x157: (     "DEGREES",  1,  1,   "V",             "V", False), # 228
    0x158: (    "SUBTOTAL",  2, 30,   "V",       "V R ...", False), # 229
    0x159: (       "SUMIF",  2,  3,   "V",         "R V R", False), # 230
    0x15a: (     "COUNTIF",  2,  2,   "V",           "R V", False), # 231
    0x15b: (  "COUNTBLANK",  1,  1,   "V",             "R", False), # 232
    0x15e: (       "ISPMT",  4,  4,   "V",       "V V V V", False), # 233
    0x15f: (     "DATEDIF",  3,  3,   "V",         "V V V", False), # 234
    0x160: (  "DATESTRING",  1,  1,   "V",             "V", False), # 235
    0x161: ("NUMBERSTRING",  2,  2,   "V",           "V V", False), # 236
    0x162: (       "ROMAN",  1,  2,   "V",           "V V", False), # 237
    0x166: ("GETPIVOTDATA",  2, 30,   "A",             "-", False), # 238
    0x167: (   "HYPERLINK",  1,  2,   "V",           "V V", False), # 239
    0x168: (    "PHONETIC",  1,  1,   "V",             "R", False), # 240
    0x169: (    "AVERAGEA",  1, 30,   "V",         "R ...", False), # 241
    0x16a: (        "MAXA",  1, 30,   "V",         "R ...", False), # 242
    0x16b: (        "MINA",  1, 30,   "V",         "R ...", False), # 243
    0x16c: (     "STDEVPA",  1, 30,   "V",         "R ...", False), # 244
    0x16d: (       "VARPA",  1, 30,   "V",         "R ...", False), # 245
    0x16e: (      "STDEVA",  1, 30,   "V",         "R ...", False), # 246
    0x16f: (        "VARA",  1, 30,   "V",         "R ...", False)  # 247
}


# Formulas Parse things

ptgExp          = 0x01
ptgTbl          = 0x02
ptgAdd          = 0x03
ptgSub          = 0x04
ptgMul          = 0x05
ptgDiv          = 0x06
ptgPower        = 0x07
ptgConcat       = 0x08
ptgLT           = 0x09
ptgLE           = 0x0a
ptgEQ           = 0x0b
ptgGE           = 0x0c
ptgGT           = 0x0d
ptgNE           = 0x0e
ptgIsect        = 0x0f
ptgUnion        = 0x10
ptgRange        = 0x11
ptgUplus        = 0x12
ptgUminus       = 0x13
ptgPercent      = 0x14
ptgParen        = 0x15
ptgMissArg      = 0x16
ptgStr          = 0x17
ptgExtend       = 0x18
ptgAttr         = 0x19
ptgSheet        = 0x1a
ptgEndSheet     = 0x1b
ptgErr          = 0x1c
ptgBool         = 0x1d
ptgInt          = 0x1e
ptgNum          = 0x1f

ptgArrayR       = 0x20
ptgFuncR        = 0x21
ptgFuncVarR     = 0x22
ptgNameR        = 0x23
ptgRefR         = 0x24
ptgAreaR        = 0x25
ptgMemAreaR     = 0x26
ptgMemErrR      = 0x27
ptgMemNoMemR    = 0x28
ptgMemFuncR     = 0x29
ptgRefErrR      = 0x2a
ptgAreaErrR     = 0x2b
ptgRefNR        = 0x2c
ptgAreaNR       = 0x2d
ptgMemAreaNR    = 0x2e
ptgMemNoMemNR   = 0x2f
ptgNameXR       = 0x39
ptgRef3dR       = 0x3a
ptgArea3dR      = 0x3b
ptgRefErr3dR    = 0x3c
ptgAreaErr3dR   = 0x3d

ptgArrayV       = 0x40
ptgFuncV        = 0x41
ptgFuncVarV     = 0x42
ptgNameV        = 0x43
ptgRefV         = 0x44
ptgAreaV        = 0x45
ptgMemAreaV     = 0x46
ptgMemErrV      = 0x47
ptgMemNoMemV    = 0x48
ptgMemFuncV     = 0x49
ptgRefErrV      = 0x4a
ptgAreaErrV     = 0x4b
ptgRefNV        = 0x4c
ptgAreaNV       = 0x4d
ptgMemAreaNV    = 0x4e
ptgMemNoMemNV   = 0x4f
ptgFuncCEV      = 0x58
ptgNameXV       = 0x59
ptgRef3dV       = 0x5a
ptgArea3dV      = 0x5b
ptgRefErr3dV    = 0x5c
ptgAreaErr3dV   = 0x5d

ptgArrayA       = 0x60
ptgFuncA        = 0x61
ptgFuncVarA     = 0x62
ptgNameA        = 0x63
ptgRefA         = 0x64
ptgAreaA        = 0x65
ptgMemAreaA     = 0x66
ptgMemErrA      = 0x67
ptgMemNoMemA    = 0x68
ptgMemFuncA     = 0x69
ptgRefErrA      = 0x6a
ptgAreaErrA     = 0x6b
ptgRefNA        = 0x6c
ptgAreaNA       = 0x6d
ptgMemAreaNA    = 0x6e
ptgMemNoMemNA   = 0x6f
ptgFuncCEA      = 0x78
ptgNameXA       = 0x79
ptgRef3dA       = 0x7a
ptgArea3dA      = 0x7b
ptgRefErr3dA    = 0x7c
ptgAreaErr3dA   = 0x7d


PtgNames = {
    ptgExp         : "ptgExp",
    ptgTbl         : "ptgTbl",
    ptgAdd         : "ptgAdd",
    ptgSub         : "ptgSub",
    ptgMul         : "ptgMul",
    ptgDiv         : "ptgDiv",
    ptgPower       : "ptgPower",
    ptgConcat      : "ptgConcat",
    ptgLT          : "ptgLT",
    ptgLE          : "ptgLE",
    ptgEQ          : "ptgEQ",
    ptgGE          : "ptgGE",
    ptgGT          : "ptgGT",
    ptgNE          : "ptgNE",
    ptgIsect       : "ptgIsect",
    ptgUnion       : "ptgUnion",
    ptgRange       : "ptgRange",
    ptgUplus       : "ptgUplus",
    ptgUminus      : "ptgUminus",
    ptgPercent     : "ptgPercent",
    ptgParen       : "ptgParen",
    ptgMissArg     : "ptgMissArg",
    ptgStr         : "ptgStr",
    ptgExtend      : "ptgExtend",
    ptgAttr        : "ptgAttr",
    ptgSheet       : "ptgSheet",
    ptgEndSheet    : "ptgEndSheet",
    ptgErr         : "ptgErr",
    ptgBool        : "ptgBool",
    ptgInt         : "ptgInt",
    ptgNum         : "ptgNum",
    ptgArrayR      : "ptgArrayR",
    ptgFuncR       : "ptgFuncR",
    ptgFuncVarR    : "ptgFuncVarR",
    ptgNameR       : "ptgNameR",
    ptgRefR        : "ptgRefR",
    ptgAreaR       : "ptgAreaR",
    ptgMemAreaR    : "ptgMemAreaR",
    ptgMemErrR     : "ptgMemErrR",
    ptgMemNoMemR   : "ptgMemNoMemR",
    ptgMemFuncR    : "ptgMemFuncR",
    ptgRefErrR     : "ptgRefErrR",
    ptgAreaErrR    : "ptgAreaErrR",
    ptgRefNR       : "ptgRefNR",
    ptgAreaNR      : "ptgAreaNR",
    ptgMemAreaNR   : "ptgMemAreaNR",
    ptgMemNoMemNR  : "ptgMemNoMemNR",
    ptgNameXR      : "ptgNameXR",
    ptgRef3dR      : "ptgRef3dR",
    ptgArea3dR     : "ptgArea3dR",
    ptgRefErr3dR   : "ptgRefErr3dR",
    ptgAreaErr3dR  : "ptgAreaErr3dR",
    ptgArrayV      : "ptgArrayV",
    ptgFuncV       : "ptgFuncV",
    ptgFuncVarV    : "ptgFuncVarV",
    ptgNameV       : "ptgNameV",
    ptgRefV        : "ptgRefV",
    ptgAreaV       : "ptgAreaV",
    ptgMemAreaV    : "ptgMemAreaV",
    ptgMemErrV     : "ptgMemErrV",
    ptgMemNoMemV   : "ptgMemNoMemV",
    ptgMemFuncV    : "ptgMemFuncV",
    ptgRefErrV     : "ptgRefErrV",
    ptgAreaErrV    : "ptgAreaErrV",
    ptgRefNV       : "ptgRefNV",
    ptgAreaNV      : "ptgAreaNV",
    ptgMemAreaNV   : "ptgMemAreaNV",
    ptgMemNoMemNV  : "ptgMemNoMemNV",
    ptgFuncCEV     : "ptgFuncCEV",
    ptgNameXV      : "ptgNameXV",
    ptgRef3dV      : "ptgRef3dV",
    ptgArea3dV     : "ptgArea3dV",
    ptgRefErr3dV   : "ptgRefErr3dV",
    ptgAreaErr3dV  : "ptgAreaErr3dV",
    ptgArrayA      : "ptgArrayA",
    ptgFuncA       : "ptgFuncA",
    ptgFuncVarA    : "ptgFuncVarA",
    ptgNameA       : "ptgNameA",
    ptgRefA        : "ptgRefA",
    ptgAreaA       : "ptgAreaA",
    ptgMemAreaA    : "ptgMemAreaA",
    ptgMemErrA     : "ptgMemErrA",
    ptgMemNoMemA   : "ptgMemNoMemA",
    ptgMemFuncA    : "ptgMemFuncA",
    ptgRefErrA     : "ptgRefErrA",
    ptgAreaErrA    : "ptgAreaErrA",
    ptgRefNA       : "ptgRefNA",
    ptgAreaNA      : "ptgAreaNA",
    ptgMemAreaNA   : "ptgMemAreaNA",
    ptgMemNoMemNA  : "ptgMemNoMemNA",
    ptgFuncCEA     : "ptgFuncCEA",
    ptgNameXA      : "ptgNameXA",
    ptgRef3dA      : "ptgRef3dA",
    ptgArea3dA     : "ptgArea3dA",
    ptgRefErr3dA   : "ptgRefErr3dA",
    ptgAreaErr3dA  : "ptgAreaErr3dA"
}


error_msg_by_code = {
    0x00: u"#NULL!",  # intersection of two cell ranges is empty
    0x07: u"#DIV/0!", # division by zero
    0x0F: u"#VALUE!", # wrong type of operand
    0x17: u"#REF!",   # illegal or deleted cell reference
    0x1D: u"#NAME?",  # wrong function or range name
    0x24: u"#NUM!",   # value range overflow
    0x2A: u"#N/A!"    # argument or function not available
}
