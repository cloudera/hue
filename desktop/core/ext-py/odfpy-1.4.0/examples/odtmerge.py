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
# Contributor(s): Ramiro Batista da Luz
#

# Inspired by ods2odt.py
#
import sys, getopt
import zipfile, xml.dom.minidom
from odf.opendocument import OpenDocumentText, load
from odf.element import Text
from odf.text import P


def usage():
   sys.stderr.write("Usage: %s -o outputfile inputfile [inputfile2 inputfile3 ...]\n" % sys.argv[0])


def merge(inputfile, textdoc):
    inputtextdoc = load(inputfile)

    # Need to make a copy of the list because addElement unlinks from the original
    for meta in inputtextdoc.meta.childNodes[:]:
        textdoc.meta.addElement(meta)

    for font in inputtextdoc.fontfacedecls.childNodes[:]:
        textdoc.fontfacedecls.addElement(font)

    for style in inputtextdoc.styles.childNodes[:]:
        textdoc.styles.addElement(style)

    for autostyle in inputtextdoc.automaticstyles.childNodes[:]:
        textdoc.automaticstyles.addElement(autostyle)


    for scripts in inputtextdoc.scripts.childNodes[:]:
        textdoc.scripts.addElement(scripts)

    for settings in inputtextdoc.settings.childNodes[:]:
        textdoc.settings.addElement(settings)

    for masterstyles in inputtextdoc.masterstyles.childNodes[:]:
        textdoc.masterstyles.addElement(masterstyles)

    for body in inputtextdoc.body.childNodes[:]:
        textdoc.body.addElement(body)

    textdoc.Pictures = inputtextdoc.Pictures
    return textdoc


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

    if outputfile is None:
        usage()
        sys.exit(2)

    if len(args) < 2:
        usage()
        sys.exit(2)

    inputfiles = args[1:]

    textdoc = OpenDocumentText()

    for inputfile in inputfiles:
        textdoc = merge(inputfile, textdoc)

    textdoc.save(outputfile)
