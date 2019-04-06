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

from odf.opendocument import OpenDocumentText
from odf.style import Style, TextProperties, ParagraphProperties, TableColumnProperties
from odf.text import P
from odf.table import Table, TableColumn, TableRow, TableCell

PWENC = "utf-8"

textdoc = OpenDocumentText()
# Create a style for the table content. One we can modify
# later in the word processor.
tablecontents = Style(name="Table Contents", family="paragraph")
tablecontents.addElement(ParagraphProperties(numberlines="false", linenumber="0"))
textdoc.styles.addElement(tablecontents)

# Create automatic styles for the column widths.
# We want two different widths, one in inches, the other one in metric.
# ODF Standard section 15.9.1
widthshort = Style(name="Wshort", family="table-column")
widthshort.addElement(TableColumnProperties(columnwidth="1.7cm"))
textdoc.automaticstyles.addElement(widthshort)

widthwide = Style(name="Wwide", family="table-column")
widthwide.addElement(TableColumnProperties(columnwidth="1.5in"))
textdoc.automaticstyles.addElement(widthwide)

# Start the table, and describe the columns
table = Table()
table.addElement(TableColumn(numbercolumnsrepeated=4,stylename=widthshort))
table.addElement(TableColumn(numbercolumnsrepeated=3,stylename=widthwide))

f = open('/etc/passwd')
for line in f:
    rec = line.strip().split(":")
    tr = TableRow()
    table.addElement(tr)
    for val in rec:
        tc = TableCell()
        tr.addElement(tc)
        p = P(stylename=tablecontents,text=unicode(val,PWENC))
        tc.addElement(p)

textdoc.text.addElement(table)
textdoc.save("passwd.odt")
