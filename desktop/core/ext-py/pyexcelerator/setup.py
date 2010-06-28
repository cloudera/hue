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

__rev_id__ = """$Id: setup.py,v 1.10 2005/10/26 07:44:23 rvk Exp $"""

import sys
from distutils.core import setup

DESCRIPTION = \
'generating Excel 97+ files; importing Excel 95+ files; Excel files dumper; OLE2 files dumper; xls2txt, xls2csv, xls2html'

LONG_DESCRIPTION = \
'''pyExcelerator  is a   library  for  generating  Excel  97/2000/XP/2003  and
OpenOffice    Calc   compatible     spreadsheets.     pyExcelerator     has
full-blown   support   for  UNICODE  in Excel and Calc spreadsheets, allows
using variety of formatting features,   provides   interface   to  printing
options   of   Excel   and OpenOffice  Calc.  pyExcelerator  contains  also
Excel BIFF8 dumper and MS compound  documents  dumper.  Main  advantage  is
possibility  of generating Excel  spreadsheets  without  COM  servers.  The
only requirement -- Python 2.4b2 or higher.
From version 0.5 pyExcelerator can import data from Excel spreadsheets.'''

CLASSIFIERS = \
[
 'Operating System :: OS Independent',
 'Programming Language :: Python',
 'License :: OSI Approved :: BSD License',
 'Development Status :: 3 - Alpha',
 'Intended Audience :: Developers',
 'Topic :: Software Development :: Libraries :: Python Modules',
 'Topic :: Office/Business :: Financial :: Spreadsheet',
 'Topic :: Database',
 'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries',
]

KEYWORDS = \
'xls openoffice excel spreadsheet workbook database table unicode'

setup(name = 'pyExcelerator',
      version = '0.6.4.1',
      author = 'Roman V. Kiseliov',
      author_email = 'roman@kiseliov.ru',
      url = 'http://sourceforge.net/projects/pyexcelerator/',
      download_url='http://sourceforge.net/projects/pyexcelerator/',    
      description = DESCRIPTION,
      long_description = LONG_DESCRIPTION,
      license = 'BSD',
      platforms = 'Platform Independent',
      packages = ['pyExcelerator'],
      keywords = KEYWORDS,
      classifiers = CLASSIFIERS
      )
