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

import sys
from odf.odf2moinmoin import ODF2MoinMoin

class ODF2ZWikiMoin(ODF2MoinMoin):

    def __init__(self, filepath):
        super(ODF2ZWikiMoin, self).__init__(filepath)
        self.baseURL = "BaseURL"

    def draw_image(self, node):
        """
        """
        link = node.getAttribute("xlink:href")
        if link and link[:2] == './': # Indicates a sub-object, which isn't supported
            return "%s\n" % link
        if link and link[:9] == 'Pictures/':
            link = self.baseURL + "/" + link[9:]
        return "%s\n" % link

    def text_line_break(self, node):
        return "\n"

if __name__ == "__main__":
    odt = ODF2ZWikiMoin(sys.argv[1])
    out_utf8 = odt.toString().encode("utf-8")
    sys.stdout.write(out_utf8)
