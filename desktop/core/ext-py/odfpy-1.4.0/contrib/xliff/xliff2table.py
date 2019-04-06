#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2007 Søren Roug, European Environment Agency
#
# This is free software.  You may redistribute it under the terms
# of the Apache license and the GNU General Public License Version
# 2 or at your option any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public
# License along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
# Contributor(s):
#
from xliff_parser import HandleXliffParsing
import sys

from odf.opendocument import OpenDocumentText
from odf import style, table
from odf.text import P, UserFieldDecls, UserFieldDecl, UserFieldInput
from odf.namespaces import TABLENS

textdoc = OpenDocumentText()
# Create a style for the table content. One we can modify
# later in the word processor.
tablecontents = style.Style(name="Table Contents", family="paragraph")
tablecontents.addElement(style.ParagraphProperties(numberlines="false", linenumber="0"))
textdoc.styles.addElement(tablecontents)

#tablestyle = style.Style(name="Table style", family="table")
#tablestyle.addElement(style.TableProperties(protected="true"))
#textdoc.automaticstyles.addElement(tablestyle)

# Create automatic styles for the column widths.
widthwide = style.Style(name="Wwide", family="table-column")
widthwide.addElement(style.TableColumnProperties(columnwidth="8cm"))
textdoc.automaticstyles.addElement(widthwide)

tcstyle = style.Style(name="Table Cell", family="table-cell")
tcstyle.addElement(style.TableCellProperties(cellprotect="protected"))
textdoc.automaticstyles.addElement(tcstyle)

parser = HandleXliffParsing()
xliff = file('global.xlf').read()
chandler = parser.parseXLIFFSTring(xliff)
if chandler is None:
    print "Unable to parse XLIFF file"
    sys.exit(0)

header_info = chandler.getFileTag()
body_info = chandler.getBody() #return a dictionary

uf = UserFieldDecls()
textdoc.text.addElement(uf)

# Add user fields
for id,transunit in body_info.items():
    uf.addElement(UserFieldDecl(name=id,valuetype="string", stringvalue=transunit['target']))
   

# Start the table, and describe the columns
mytable = table.Table(protected="true")
mytable.addElement(table.TableColumn(numbercolumnsrepeated=2,stylename=widthwide))

for id,transunit in body_info.items():
    tr = table.TableRow()
    mytable.addElement(tr)

    tc = table.TableCell(stylename=tcstyle, qattributes={(TABLENS,'protected'):'true'})
    tr.addElement(tc)
    p = P(stylename=tablecontents,text=transunit['source'])
    tc.addElement(p)

    tc = table.TableCell(qattributes={(TABLENS,'protected'):'true'})
    tr.addElement(tc)
    p = P(stylename=tablecontents)
    tc.addElement(p)
    f = UserFieldInput(name=id,description="Enter translation")
    p.addElement(f)

textdoc.text.addElement(mytable)
textdoc.save("translations.odt")
