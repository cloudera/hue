#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2009 Brad Ralph, Sydney, Australia
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
# Søren Roug
# This example shows how to do a conditional currency style. We want negative
# numbers to show as red and as Australian dollars.

from odf.opendocument import OpenDocumentSpreadsheet
from odf.style import Style, TextProperties, TableColumnProperties, Map
from odf.number import NumberStyle, CurrencyStyle, CurrencySymbol,  Number,  Text
from odf.text import P
from odf.table import Table, TableColumn, TableRow, TableCell

textdoc = OpenDocumentSpreadsheet()
# Create a style for the table content. One we can modify
# later in the spreadsheet.
tablecontents = Style(name="Large number", family="table-cell")
tablecontents.addElement(TextProperties(fontfamily="Arial", fontsize="15pt"))
textdoc.styles.addElement(tablecontents)

# Create automatic styles for the column widths.
widewidth = Style(name="co1", family="table-column")
widewidth.addElement(TableColumnProperties(columnwidth="2.8cm", breakbefore="auto"))
textdoc.automaticstyles.addElement(widewidth)

# Create the styles for $AUD format currency values
ns1 = CurrencyStyle(name="positive-AUD", volatile="true")
ns1.addElement(CurrencySymbol(language="en", country="AU", text=u"$"))
ns1.addElement(Number(decimalplaces="2", minintegerdigits="1", grouping="true"))
textdoc.styles.addElement(ns1)

# Create the main style.
ns2 = CurrencyStyle(name="main-AUD")
ns2.addElement(TextProperties(color="#ff0000"))
ns2.addElement(Text(text=u"-"))
ns2.addElement(CurrencySymbol(language="en", country="AU", text=u"$"))
ns2.addElement(Number(decimalplaces="2", minintegerdigits="1", grouping="true"))
ns2.addElement(Map(condition="value()>=0", applystylename="positive-AUD"))
textdoc.styles.addElement(ns2)

# Create automatic style for the price cells.
moneycontents = Style(name="ce1", family="table-cell", parentstylename=tablecontents, datastylename="main-AUD")
textdoc.automaticstyles.addElement(moneycontents)

# Start the table, and describe the columns
table = Table(name="Currency colours")
# Create a column (same as <col> in HTML) Make all cells in column default to currency
table.addElement(TableColumn(stylename=widewidth, defaultcellstylename="ce1"))
# Create a row (same as <tr> in HTML)
tr = TableRow()
table.addElement(tr)
# Create a cell with a negative value. It should show as red.
cell = TableCell(valuetype="currency", currency="AUD", value="-125")
cell.addElement(P(text=u"$-125.00")) # The current displayed value
tr.addElement(cell)

# Create a row (same as <tr> in HTML)
tr = TableRow()
table.addElement(tr)
# Create another cell but with a positive value. It should show in black
cell = TableCell(valuetype="currency", currency="AUD", value="123")
cell.addElement(P(text=u"$123.00")) # The current displayed value
tr.addElement(cell)

textdoc.spreadsheet.addElement(table)
textdoc.save("currency.ods")
