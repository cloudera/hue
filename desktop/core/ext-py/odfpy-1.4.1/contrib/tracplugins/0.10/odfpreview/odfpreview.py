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
from trac.mimeview.api import IHTMLPreviewRenderer
import os
from tempfile import mkstemp
from odf.odf2xhtml import ODF2XHTML


class ODF2XHTMLBody(ODF2XHTML):

    def __init__(self):
        ODF2XHTML.__init__(self, generate_css=False, embedable=True)

    def rewritelink(self, imghref):
        imghref = imghref.replace("Pictures/","index_html?pict=")
        return imghref

class OdfPreview(Component):
    """Display OpenDocument as HTML."""
    implements(IHTMLPreviewRenderer)

    def get_quality_ratio(self, mimetype):
        self.env.log.debug('Trac checking for %s' % mimetype)
        if mimetype in ('application/vnd.oasis.opendocument.text',
            'application/vnd.oasis.opendocument.text-template',
            'application/vnd.oasis.opendocument.spreadsheet',
            'application/vnd.oasis.opendocument.presentation'):
            return 7
        return 0

    def render(self, req, input_type, content, filename=None, url=None):
        self.env.log.debug('HTML output for ODF')
        odhandler = ODF2XHTMLBody()
        hfile, hfilename = mkstemp('tracodf')
        try:
            if hasattr(content,'read'):
                os.write(hfile, content.read())
            else:
                os.write(hfile, content)
            os.close(hfile)
            out = odhandler.odf2xhtml(hfilename).encode('us-ascii','xmlcharrefreplace')
        except:
            self.env.log.error("odf2xhtml failed")
        finally:
            os.unlink(hfilename)
        if out != '':
            return out
        return "<h1>HTML preview failed</h1>"

#   def render(self, req, input_type, content, filename=None, url=None):
#       self.env.log.debug('HTML output for ODF')
#       hfilename = None
#       odhandler = ODF2XHTML()
#       if filename is not None:
#           infile = filename
#       else:
#           hfile, hfilename = mkstemp('tracodf')
#           if hasattr(content,'read'):
#               os.write(hfile, content.read())
#           else:
#               os.write(hfile, content)
#           os.close(hfile)
#           infile = hfilename
#       out = odhandler.odf2xhtml(infile).encode('us-ascii','xmlcharrefreplace')
#       if hfilename is not None:
#           os.unlink(hfilename)
#       return out
