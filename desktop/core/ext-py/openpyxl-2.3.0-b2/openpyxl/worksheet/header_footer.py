from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# @license: http://www.opensource.org/licenses/mit-license.php
# @author: see AUTHORS file


class HeaderFooterItem(object):
    """Individual left/center/right header/footer items

       Header & Footer ampersand codes:

       * &A   Inserts the worksheet name
       * &B   Toggles bold
       * &D or &[Date]   Inserts the current date
       * &E   Toggles double-underline
       * &F or &[File]   Inserts the workbook name
       * &I   Toggles italic
       * &N or &[Pages]   Inserts the total page count
       * &S   Toggles strikethrough
       * &T   Inserts the current time
       * &[Tab]   Inserts the worksheet name
       * &U   Toggles underline
       * &X   Toggles superscript
       * &Y   Toggles subscript
       * &P or &[Page]   Inserts the current page number
       * &P+n   Inserts the page number incremented by n
       * &P-n   Inserts the page number decremented by n
       * &[Path]   Inserts the workbook path
       * &&   Escapes the ampersand character
       * &"fontname"   Selects the named font
       * &nn   Selects the specified 2-digit font point size
    """
    CENTER = 'C'
    LEFT = 'L'
    RIGHT = 'R'

    REPLACE_LIST = (
        ('\n', '_x000D_'),
        ('&[Page]', '&P'),
        ('&[Pages]', '&N'),
        ('&[Date]', '&D'),
        ('&[Time]', '&T'),
        ('&[Path]', '&Z'),
        ('&[File]', '&F'),
        ('&[Tab]', '&A'),
        ('&[Picture]', '&G')
        )

    __slots__ = ('type',
                 'font_name',
                 'font_size',
                 'font_color',
                 'text')

    def __init__(self, type):
        self.type = type
        self.font_name = "Calibri,Regular"
        self.font_size = None
        self.font_color = "000000"
        self.text = None

    def has(self):
        return True if self.text else False

    def get(self):
        t = []
        if self.text:
            t.append('&%s' % self.type)
            t.append('&"%s"' % self.font_name)
            if self.font_size:
                t.append('&%d' % self.font_size)
            t.append('&K%s' % self.font_color)
            text = self.text
            for old, new in self.REPLACE_LIST:
                text = text.replace(old, new)
            t.append(text)
        return ''.join(t)

    def set(self, text):
        """
        Convert a compound string into attributes
        # incomplete because formatting commands can be nested
        """
        if text is None:
            return
        m = FONT_REGEX.search(text)
        if m:
            self.font_name = m.group('font')
            text = FONT_REGEX.sub('', text)

        m = SIZE_REGEX.search(text)
        if m:
            self.font_size = int(m.group('size'))
            text = SIZE_REGEX.sub('', text)

        m = COLOR_REGEX.search(text)
        if m:
            self.font_color = m.group('color')
            text = COLOR_REGEX.sub('', text)

        self.text = text


class HeaderFooter(object):
    """Information about the header/footer for this sheet.
    """
    __slots__ = ('left_header',
                 'center_header',
                 'right_header',
                 'left_footer',
                 'center_footer',
                 'right_footer')

    def __init__(self):
        self.left_header = HeaderFooterItem(HeaderFooterItem.LEFT)
        self.center_header = HeaderFooterItem(HeaderFooterItem.CENTER)
        self.right_header = HeaderFooterItem(HeaderFooterItem.RIGHT)
        self.left_footer = HeaderFooterItem(HeaderFooterItem.LEFT)
        self.center_footer = HeaderFooterItem(HeaderFooterItem.CENTER)
        self.right_footer = HeaderFooterItem(HeaderFooterItem.RIGHT)

    def hasHeader(self):
        return True if self.left_header.has() or self.center_header.has() or self.right_header.has() else False

    def hasFooter(self):
        return True if self.left_footer.has() or self.center_footer.has() or self.right_footer.has() else False

    def getHeader(self):
        t = []
        if self.left_header.has():
            t.append(self.left_header.get())
        if self.center_header.has():
            t.append(self.center_header.get())
        if self.right_header.has():
            t.append(self.right_header.get())
        return ''.join(t)

    def getFooter(self):
        t = []
        if self.left_footer.has():
            t.append(self.left_footer.get())
        if self.center_footer.has():
            t.append(self.center_footer.get())
        if self.right_footer.has():
            t.append(self.right_footer.get())
        return ''.join(t)


    def setHeader(self, item):
        matches = _split_string(item)
        l = matches['left']
        c = matches['center']
        r = matches['right']

        self.left_header.set(l)
        self.center_header.set(c)
        self.right_header.set(r)


    def setFooter(self, item):
        matches = _split_string(item)
        l = matches['left']
        c = matches['center']
        r = matches['right']

        self.left_footer.set(l)
        self.center_footer.set(c)
        self.right_footer.set(r)


# See http://stackoverflow.com/questions/27711175/regex-with-multiple-optional-groups for discussion
import re

ITEM_REGEX = re.compile("""
(&L(?P<left>.+?))?
(&C(?P<center>.+?))?
(&R(?P<right>.+?))?
$""", re.VERBOSE | re.DOTALL)

# add support for multiline strings (how do re.flags combine?)

from warnings import warn

def _split_string(text):
    """Split the combined (decoded) string into left, center and right parts"""
    m = ITEM_REGEX.match(text)
    try:
        parts = m.groupdict()
    except AttributeError:
        warn("""Cannot parse header or footer so it will be ignored""")
        parts = {'left':'', 'right':'', 'center':''}
    return parts

HEADER_REGEX = re.compile(r"(&[ABDEGHINOPSTUXYZ\+\-])") # split part into commands
FONT_REGEX = re.compile('&"(?P<font>.+)"')
COLOR_REGEX = re.compile("&K(?P<color>[A-F0-9]{6})")
SIZE_REGEX = re.compile(r"&(?P<size>\d+)")
