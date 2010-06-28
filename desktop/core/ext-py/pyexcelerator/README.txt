
                        pyExcelerator
                    --------------------


                                                         Dedicated to Olya. 
                                                With you it can be reality.



0x0000. What's this?
--------------------
This   is   a    library   for   generating   Excel   97/2000/XP/2003   and
OpenOffice    Calc   compatible     spreadsheets.     pyExcelerator     has
full-blown   support   for  UNICODE  in Excel and Calc spreadsheets, allows
using variety of formatting features,   provides   interface   to  printing
options   of   Excel   and OpenOffice  Calc.  pyExcelerator  contains  also
Excel BIFF8 dumper and MS compound  documents  dumper.  Main  advantage  is
possibility of generating Excel  spreadsheets  without  MS  Windows  and/or
COM  servers.  The  only requirement -- Python 2.4a3 or higher.


0x0001. Why?
--------------------
I  had need to generate .xls with UNICODE under FreeBSD.


0x0002. Requirements.
--------------------
Python    2.4   up   and   running.   I've   tested   pyExcelerator   under
Win32  (Python     compiled     with    MS    C    compiler    and    Intel
C  compiler),    Win64-x86  (MS       C      compiler),   FreeBSD/i386 (GCC
3.4.2),   FreeBSD/amd64   (GCC    3.4.2).    Fastest    was   Python  under
FreeBSD/amd64.


0x0003. Installation.
--------------------
As usually: python ./setup.py install


0x0004. Documentation.
--------------------
In progress. At the present time you can use examples and sources (I hope
I commented sources well and gave variables good names).


0x0005. Extra features.
--------------------
See  ./tools/*.py.  You'll  find  there  BIFF8  dumper  and MS Compound doc
dumper.  In  ./hrc  you  can take my python.hrc for Colorer plug-in for FAR
manager.


0x0006. Reporting bugs.
--------------------
Please! 


0x0008. Future.
--------------------
Support for Esher layer and (maybe) charts.


0x0009. Useful links.
--------------------
http://www.python.org    --
                           Python's home.
http://sf.net/pyXLWriter -- 
                           port of the first version Spreadsheet-WriteExcel.
                           This library can write only BIFF5/7 spreadsheets
                           and therefore can't use UNICODE in spreadsheets.
                           pyXLWriter however can write formulas with help
                           of PLY. IMHO, PLY and ambiguous grammar used by
                           author for formulas support are too power tools.
                           But in this case power was equals to simplicity.
                           I want overcome these restrictions and (strictly
                           IMHO) misfeatures. 
http://www.openoffice.org --
                           OpenOffice home. 
                           About 650 Mb sources -- the best teachers.

0x000A. Legality.
--------------------
With  help  from  lawyers  pyExcelerator is protect by Russian Federation's
laws  and  international  treaties and can be used iff you agreed following
BSD-like agreement.

 Copyright (C) 2005 Roman V. Kiseliov
 All rights reserved.
 
 Redistribution and use in source and binary forms, with or without
 modification, are permitted provided that the following conditions
 are met:
 
 1. Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.
 
 2. Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in
    the documentation and/or other materials provided with the
    distribution.
 
 3. All advertising materials mentioning features or use of this
    software must display the following acknowledgment:
    "This product includes software developed by
     Roman V. Kiseliov <roman@kiseliov.ru>."
 
 4. Redistributions of any form whatsoever must retain the following
    acknowledgment:
    "This product includes software developed by
     Roman V. Kiseliov <roman@kiseliov.ru>."
 
 THIS SOFTWARE IS PROVIDED BY Roman V. Kiseliov ``AS IS'' AND ANY
 EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL Roman V. Kiseliov OR
 ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
 NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
 STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
 OF THE POSSIBILITY OF SUCH DAMAGE.



0xFFFF. Contacting author.
--------------------
Feel free to send me feedback and bug reports.

Roman V. Kiseliov
Russia
Kursk
Libknecht St., 4

+7(0712)56-09-83

<roman@kiseliov.ru>
subject *must* be 
"pyExcelerator-bug" (without quotes)
or 
"pyExcelerator-feedback" (without quotes)

