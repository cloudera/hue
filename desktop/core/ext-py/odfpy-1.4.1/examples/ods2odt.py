#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2008 Søren Roug, European Environment Agency
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

# This script converts a spreadsheet to a text file. I.e. it copies
# the sheets and turns them into tables in the textfile
# Note: Copy of images does not work?
#
import sys, getopt
from odf.opendocument import OpenDocumentText, load
from odf.table import Table
from odf.text import P

def usage():
   sys.stderr.write("Usage: %s [-o outputfile] inputfile\n" % sys.argv[0])

if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "o:", ["output="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    outputfile = None

    for o, a in opts:
        if o in ("-o", "--output"):
            outputfile = a

    if len(args) != 1:
        usage()
        sys.exit(2)

    inputfile = args[0]
    if outputfile is None:
        outputfile = inputfile[:inputfile.rfind('.')] + ".odt"

    spreadsheetdoc = load(inputfile)

    textdoc = OpenDocumentText()

    # Need to make a copy of the list because addElement unlinks from the original
    for meta in spreadsheetdoc.meta.childNodes[:]:
        textdoc.meta.addElement(meta)

    for font in spreadsheetdoc.fontfacedecls.childNodes[:]:
        textdoc.fontfacedecls.addElement(font)

    for style in spreadsheetdoc.styles.childNodes[:]:
        textdoc.styles.addElement(style)

    for autostyle in spreadsheetdoc.automaticstyles.childNodes[:]:
        textdoc.automaticstyles.addElement(autostyle)

    for sheet in spreadsheetdoc.getElementsByType(Table):
        textdoc.text.addElement(sheet)
        textdoc.text.addElement(P())

    textdoc.Pictures = spreadsheetdoc.Pictures
    textdoc.save(outputfile)
