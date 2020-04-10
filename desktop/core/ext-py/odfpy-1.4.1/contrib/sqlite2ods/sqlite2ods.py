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
import os, sys
import sqlite
from odf.opendocument import OpenDocumentSpreadsheet
from odf.style import Style, TextProperties, ParagraphProperties, TableColumnProperties
from odf.text import P
from odf.table import Table, TableColumn, TableRow, TableCell

if len(sys.argv) != 3:
    print "Usage: sqlite-db table"
    sys.exit(2)

sqldb = sys.argv[1]
sqltable = sys.argv[2]
textdoc = OpenDocumentSpreadsheet()
# Create a style for the table content. One we can modify
# later in the word processor.
tablecontents = Style(name="Table Contents", family="paragraph")
tablecontents.addElement(ParagraphProperties(numberlines="false", linenumber="0"))
#tablecontents.addElement(TextProperties(fontweight="bold"))
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
table = Table(name=sqltable)
#table.addElement(TableColumn(numbercolumnsrepeated=4,stylename=widthshort))
#table.addElement(TableColumn(numbercolumnsrepeated=3,stylename=widthwide))

cx = sqlite.connect(sqldb)
cu = cx.cursor()
cu.execute("select * from %s" % sqltable)
for row in cu.fetchall():
    tr = TableRow()
    table.addElement(tr)
    for val in row:
        tc = TableCell()
        tr.addElement(tc)
        if type(val) == type(''):
	    textval = unicode(val,'utf-8')
        else:
            textval = str(val)
        p = P(stylename=tablecontents,text=textval)
        tc.addElement(p)

cx.close()

textdoc.spreadsheet.addElement(table)
textdoc.save(sqltable, True)

