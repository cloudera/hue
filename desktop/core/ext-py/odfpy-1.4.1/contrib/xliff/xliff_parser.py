# -*- coding: utf-8 -*-
# Copyright (C) 2000-2004  Juan David Ibáñez Palomar <jdavid@itaapy.com>
#               2003  Roberto Quero, Eduardo Corrales
#               2004  Søren Roug
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

# NOTE:
# This parser doesn't understand the ALT-TRANS element.

from odf.xml import make_parser
from xml.sax.handler import ContentHandler
from xml.sax import handler, InputSource

from cStringIO import StringIO
from types import StringType, UnicodeType

#constants
_FILE_ATTRS = ['original', 'source-language', 'datatype', 'date',
          'target-language', 'product-name', 'product-version', 'build-num']
_PHASE_ATTRS = ['phase-name', 'process-name', 'tool', 'date', 'contact-name',
          'contact-email', 'company-name']


class XLIFFHandler(ContentHandler):
    """ This is used to parse the xliff file
    """

    def __init__(self):
        """constructor """
        self.__currentTag = ''
        self.__filetag = []
        self.__phase_group = []
        self.__source = 0
        self.__body = {}
        self.__data = []
        self.__inside_alttrans = 0
        self.__tuid = ''

    #functions related with <file> tag
    def getFileTag(self):
        return self.__filetag

    def setFileTag(self, dict):
        self.__filetag.extend(dict)

    #functions related with <phase-group> tag
    def getPhaseGroup(self):
        return self.__phase_group

    def setPhaseGroup(self, dict):
        self.__phase_group.append(dict)

    def getBody(self):
        return self.__body

    def setBody(self, key, value):
        self.__body[key] = value

    def startElement(self, name, attrs):
        self.__currentTag = name

        if name == 'alt-trans':
            self.__inside_alttrans = 1
        # Make the attributes available
        # Implicit assumption: There is only one <file> element.
        if name == 'file':
            tmp = attrs.items()
            for i in [elem for elem in attrs.keys() if elem not in _FILE_ATTRS]:
                tmp.remove((i, attrs[i]))
            self.setFileTag(tmp)

        if name == 'phase':
            tmp = attrs.items()
            for i in [elem for elem in attrs.keys() if elem not in _PHASE_ATTRS]:
                tmp.remove((i, attrs[i]))
            self.setPhaseGroup(tmp)

        if name == 'trans-unit':
            self.__tuid = attrs['id']
            self.__source = u''
            self.__target = u''
            self.__note = u''

    def endElement(self, name):
        if name == 'alt-trans':
            self.__inside_alttrans = 0

        if name == 'source' and self.__inside_alttrans == 0:
            content = u''.join(self.__data).strip()
            self.__data = []
            self.__source = content

        if name == 'target' and self.__inside_alttrans == 0:
            content = u''.join(self.__data).strip()
            self.__data = []
            self.__target = content

        if name == 'note' and self.__inside_alttrans == 0:
            content = u''.join(self.__data).strip()
            self.__data = []
            self.__note = content

        if name == 'trans-unit':
            self.setBody(self.__tuid, {'source':self.__source,
                'target':self.__target, 'note':self.__note})

        self.__currentTag = ''

    def characters(self, content):
        currentTag = self.__currentTag
        if currentTag in ( 'source', 'target', 'note'):
            self.__data.append(content)

class HandleXliffParsing:
    """ class for parse xliff files """

    def __init__(self):
        """ """
        pass

    def parseXLIFFSTring(self, xml_string):
        """ """
        chandler = XLIFFHandler()
        parser = make_parser()
        # Tell the parser to use our handler
        parser.setContentHandler(chandler)
        # Don't load the DTD from the Internet
        parser.setFeature(handler.feature_external_ges, 0)
        inpsrc = InputSource()
        inpsrc.setByteStream(StringIO(xml_string))
        try:
            parser.parse(inpsrc)
            return chandler
        except:
            return None

    def parseXLIFFFile(self, file):
        # Create a parser
        parser = make_parser()
        chandler = XLIFFHandler()
        # Tell the parser to use our handler
        parser.setContentHandler(chandler)
        # Don't load the DTD from the Internet
        parser.setFeature(handler.feature_external_ges, 0)
        inputsrc = InputSource()

        try:
            if type(file) is StringType:
                inputsrc.setByteStream(StringIO(file))
            else:
                filecontent = file.read()
                inputsrc.setByteStream(StringIO(filecontent))
            parser.parse(inputsrc)
            return chandler
        except:
            return None


