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

from odf.opendocument import OpenDocumentSpreadsheet
from odf.style import (ParagraphProperties, Style, TableColumnProperties,
                       TextProperties)
from odf.table import Table, TableCell, TableColumn, TableRow
from odf.text import P

textdoc = OpenDocumentSpreadsheet()
# Create a style for the table content. One we can modify
# later in the word processor.
tablecontents = Style(parent=textdoc.styles,
                      name='Table Contents', family='paragraph')
ParagraphProperties(parent=tablecontents, numberlines='false', linenumber='0')
TextProperties(parent=tablecontents, fontweight='bold')

# Create automatic styles for the column widths.
# We want two different widths, one in inches, the other one in metric.
# ODF Standard section 15.9.1
widthshort = Style(parent=textdoc.automaticstyles,
                   name='Wshort', family='table-column')
TableColumnProperties(parent=widthshort, columnwidth='1.7cm')

widthwide = Style(parent=textdoc.automaticstyles,
                  name='Wwide', family='table-column')
TableColumnProperties(parent=widthwide, columnwidth='1.5in')

# Start the table, and describe the columns
table = Table(parent=textdoc.spreadsheet, name='Password')
TableColumn(parent=table, numbercolumnsrepeated=4, stylename=widthshort)
TableColumn(parent=table, numbercolumnsrepeated=3, stylename=widthwide)

with open('/etc/passwd') as f:
    for line in f:
        rec = line.strip().split(':')
        tr = TableRow(parent=table)
        for val in rec:
            tc = TableCell(parent=tr)
            p = P(parent=tc, stylename=tablecontents, text=val)

textdoc.save('passwd.ods')
