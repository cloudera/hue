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
from odf.style import PageLayout, MasterPage, Header, Footer
from odf.text import P

textdoc = OpenDocumentText()
pl = PageLayout(name="pagelayout")
textdoc.automaticstyles.addElement(pl)
mp = MasterPage(name="Standard", pagelayoutname=pl)
textdoc.masterstyles.addElement(mp)
h = Header()
hp = P(text="header try")
h.addElement(hp)
mp.addElement(h)
textdoc.save("headers.odt")
