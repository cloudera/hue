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
from odf.style import Style, TextProperties, ParagraphProperties, ListLevelProperties
from odf.text import P, List, ListItem, ListStyle, ListLevelStyleBullet

textdoc = OpenDocumentText()

symbolstyle = Style(name="Numbering Symbols", family="text")
textdoc.styles.addElement(symbolstyle)

liststyle = Style(name="List Content", family="paragraph")
liststyle.addElement(ParagraphProperties(numberlines="false", linenumber="0"))
textdoc.automaticstyles.addElement(liststyle)

listhier = ListStyle(name="MyList")
level = 1
for bullet in [u"–", u"•", u"–",u"•", u"✗", u"✗", u"✗", u"✗", u"✗", u"✗"]:
    b = ListLevelStyleBullet(level=str(level), stylename=symbolstyle, bulletchar=bullet)
    listhier.addElement(b)
    b.addElement(ListLevelProperties(minlabelwidth="%dcm" % level))
    b.addElement(TextProperties(fontname="StarSymbol"))
    level = level + 1

textdoc.styles.addElement(listhier)

l = List(stylename=listhier)
textdoc.text.addElement(l)
for x in [1,2,3,4]:
    elem = ListItem()
    elem.addElement(P(text="Listitem %d" % x))
    l.addElement(elem)


textdoc.save("list-example.odt")
