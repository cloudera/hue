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

from trac.core import *
from trac.mimeview.api import IContentConverter
import os
import re
from odf.odf2xhtml import ODF2XHTML

class OdfToHtmlConverter(Component):
    """Convert OpenDocument to HTML."""
    implements(IContentConverter)

    # IContentConverter methods
    def get_supported_conversions(self):
        yield ('odt', 'OpenDocument Text', 'odt', 'application/vnd.oasis.opendocument.text', 'text/html', 7)
        yield ('ott', 'OpenDocument Text', 'ott', 'application/vnd.oasis.opendocument.text-template', 'text/html', 7)
        yield ('ods', 'OpenDocument Spreadsheet', 'ods', 'application/vnd.oasis.opendocument.spreadsheet', 'text/html', 7)
        yield ('odp', 'OpenDocument Presentation', 'odp', 'application/vnd.oasis.opendocument.presentation', 'text/html', 7)

    def convert_content(self, req, input_type, source, output_type):
        odhandler = ODF2XHTML()
        out = odhandler.odf2xhtml(source).encode('us-ascii','xmlcharrefreplace')
        self.env.log.debug('HTML output for ODF')
        return (out, 'text/html')
