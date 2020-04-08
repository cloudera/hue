#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2008-2009 Søren Roug, European Environment Agency
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
#
import string, sys, re, getopt
import urllib2, htmlentitydefs, urlparse
from urllib import quote_plus
from HTMLParser import HTMLParser
from cgi import escape,parse_header
from types import StringType

from odf.opendocument import OpenDocumentText, load
from odf import dc, text, table
import htmlstyles


def converturl(url, document=None):
    """ grab and convert url
    """
    url = string.strip(url)
#   if url.lower()[:5] != "http:":
#       raise IOError, "Only http is accepted"

    _proxies = {}
    proxy_support = urllib2.ProxyHandler(_proxies)
    opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler)

    urllib2.install_opener(opener)

    req = urllib2.Request(url)
    req.add_header("User-agent", "HTML2ODT: Convert HTML to OpenDocument")
    conn = urllib2.urlopen(req)

    if not conn:
        raise IOError, "Failure in open"
    data = conn.read()
    headers = conn.info()
    conn.close()

    encoding = 'iso8859-1'  #Standard HTML
    if headers.has_key('content-type'):
        (ct, parms) = parse_header(headers['content-type'])
        if parms.has_key('charset'):
            encoding = parms['charset']

    mhp = HTML2ODTParser(document, encoding, url)
    mhp.feed(data)
    return  mhp

entityref = re.compile('&([a-zA-Z][-.a-zA-Z0-9]*)[^a-zA-Z0-9]')
charref = re.compile('&#(?:[0-9]+|[xX][0-9a-fA-F]+)[^0-9a-fA-F]')
incomplete = re.compile('&[a-zA-Z#]')
ampersand = re.compile('&')

def listget(list, key, default=None):
    for l in list:
        if l[0] == key:
            default = l[1]
    return default

class TagObject:

    def __init__(self, tag, attrs, output_loc):
        self.tag = tag
        self.attrs = attrs
        self.output_loc = output_loc

class HTML2ODTParser(HTMLParser):

    def __init__(self, document, encoding, baseurl):
        HTMLParser.__init__(self)
        self.doc = document
        self.curr = self.doc.text
        if self.doc.getStyleByName("Standard") is None:
            style = Style(name="Standard", family="paragraph", attributes={'class':"text"})
            self.doc.styles.addElement(style)

        if self.doc.getStyleByName("Text_20_body") is None:
            style = Style(name="Text_20_body", displayname="Text body", family="paragraph",
               parentstylename="Standard", attributes={'class':"text"})
            p = ParagraphProperties(margintop="0cm", marginbottom="0.212cm")
            style.addElement(p)
            self.doc.styles.addElement(style)

        if self.doc.getStyleByName("Heading") is None:
            style = Style(name="Heading", family="paragraph", parentstylename="Standard",
                nextstylename="Text_20_body", attributes={'class':"text"})
            p = ParagraphProperties(margintop="0.423cm", marginbottom="0.212cm", keepwithnext="always")
            style.addElement(p)
            p = TextProperties(fontname="Nimbus Sans L", fontsize="14pt",
                 fontnameasian="DejaVu LGC Sans", fontsizeasian="14pt",
                 fontnamecomplex="DejaVu LGC Sans", fontsizecomplex="14pt")
            style.addElement(p)
            self.doc.styles.addElement(style)

        self.encoding = encoding
        (scheme, host, path, params, fragment) = urlparse.urlsplit(baseurl)
        lastslash = path.rfind('/')
        if lastslash > -1:
            path = path[:lastslash]
        self.baseurl = urlparse.urlunsplit((scheme, host, path,'',''))
        self.basehost = urlparse.urlunsplit((scheme, host, '','',''))
        self.sectnum = 0
        self.tagstack = []
        self.pstack = []
        self.processelem = True
        self.processcont = True
        self.__data = []
        self.elements = {
     'a':    (self.s_html_a, self.close_tag),
     'base': ( self.output_base, None),
     'b':    ( self.s_html_fontstyle, self.close_tag),
     'big':  ( self.s_html_fontstyle, self.close_tag),
     'br':   ( self.output_br, None),
     'col':  ( self.s_html_col, None),
     'dd':   ( self.s_html_dd, self.close_tag),
     'dt':   ( self.s_html_dt, None),
     'div':  ( self.s_html_section, self.e_html_section),
     'em':   ( self.s_html_emphasis, self.close_tag),
     'h1':   ( self.s_html_headline, self.close_tag),
     'h2':   ( self.s_html_headline, self.close_tag),
     'h3':   ( self.s_html_headline, self.close_tag),
     'h4':   ( self.s_html_headline, self.close_tag),
     'h5':   ( self.s_html_headline, self.close_tag),
     'h6':   ( self.s_html_headline, self.close_tag),
     'head': ( self.s_ignorexml, None),
     'i':    ( self.s_html_fontstyle, self.close_tag),
     'img':  ( self.output_img, None),
     'li':   ( self.s_html_li, self.e_html_li),
     'meta': ( self.meta_encoding, None),
     'ol':   ( self.output_ol, self.e_html_list),
     'p':    ( self.s_html_block, self.e_html_block),
     's':    ( self.s_html_fontstyle, self.close_tag),
     'small':( self.s_html_fontstyle, self.close_tag),
     'span': ( self.s_html_span, self.close_tag),
     'strike':( self.s_html_fontstyle, self.close_tag),
     'strong':( self.s_html_emphasis, self.close_tag),
     'table':( self.s_html_table, self.e_html_table),
     'td':   ( self.s_html_td, self.close_tag),
     'th':   ( self.s_html_td, self.close_tag),
     'title':( self.s_html_title, self.e_html_title),
     'tr':   ( self.s_html_tr, self.close_tag),
     'tt':   ( self.s_html_fontstyle, self.close_tag),
     'u':    ( self.s_html_fontstyle, self.close_tag),
     'ul':   ( self.output_ul, self.e_html_list),
     'var':  ( self.s_html_emphasis, self.close_tag),
    }

    def result(self):
        """ Return a string
            String must be in UNICODE
        """
        str = string.join(self.__data,'')
        self.__data = []
        return str

    def meta_name(self, attrs):
        """ Look in meta tag for textual info"""
        foundit = 0
        # Is there a name attribute?
        for attr in attrs:
            if attr[0] == 'name' and string.lower(attr[1]) in ('description',
            'keywords','title',
            'dc.description','dc.keywords','dc.title'
            ):
                foundit = 1
        if foundit == 0:
            return 0

        # Is there a content attribute?
        content = self.find_attr(attrs,'content')
        if content:
            self.handle_data(u' ')
            self.handle_attr(content)
            self.handle_data(u' ')
        return 1

    def meta_encoding(self, tag, attrs):
        """ Look in meta tag for page encoding (Content-Type)"""
        foundit = 0
        # Is there a content-type attribute?
        for attr in attrs:
            if attr[0] == 'http-equiv' and string.lower(attr[1]) == 'content-type':
                foundit = 1
        if foundit == 0:
            return 0

        # Is there a content attribute?
        for attr in attrs:
            if attr[0] == 'content':
                (ct, parms) = parse_header(attr[1])
                if parms.has_key('charset'):
                    self.encoding = parms['charset']
        return 1

    def s_ignorexml(self, tag, attrs):
        self.processelem = False

    def output_base(self, tag, attrs):
        """ Change the document base if there is a base tag """
        baseurl = listget(attrs, 'href', self.baseurl)
        (scheme, host, path, params, fragment) = urlparse.urlsplit(baseurl)
        lastslash = path.rfind('/')
        if lastslash > -1:
            path = path[:lastslash]
        self.baseurl = urlparse.urlunsplit((scheme, host, path,'',''))
        self.basehost = urlparse.urlunsplit((scheme, host, '','',''))

    def output_br(self, tag, attrs):
        self.curr.addElement(text.LineBreak())

    def s_html_font(self, tag, attrs):
        """ 15.2.1 Font style elements: the TT, I, B, BIG, SMALL,
            STRIKE, S, and U elements
        """
        tagdict = {
        }

    def s_html_emphasis(self, tag, attrs):
        """ 9.2.1 Phrase elements: EM, STRONG, DFN, CODE, SAMP, KBD,
            VAR, CITE, ABBR, and ACRONYM
        """
        tagdict = {
           'cite':      ['Citation', {'fontstyle':"italic", 'fontstyleasian':"italic", 'fontstylecomplex':"italic" }],
           'code':      ['Source_20_Text', {'fontname':"Courier", 'fontnameasian':"Courier",'fontnamecomplex':"Courier" }],
           'dfn':      ['Definition',{ }],
           'em':      ['Emphasis', {'fontstyle':"italic", 'fontstyleasian':"italic", 'fontstylecomplex':"italic" }],
           'strong':   ['Strong_20_Emphasis': {'fontweight':"bold",'fontweightasian':"bold",'fontweightcomplex':"bold"}],
           'var':      ['Variable', {'fontstyle':"italic", 'fontstyleasian':"italic", 'fontstylecomplex':"italic" }],
           }
        stylename = tagdict.get(tag,'Emphasis')
        # Add the styles we need to the stylesheet
        if stylename == "Source_20_Text" and self.doc.getStyleByName(stylename) is None:
            style = Style(name="Source_20_Text", displayname="Source Text", family="text")
            p = TextProperties(fontname="Courier", fontnameasian="Courier", fontnamecomplex="Courier")
            style.addElement(p)
            self.doc.styles.addElement(style)

        e = text.Span(stylename=stylename)
        self.curr.addElement(e)
        self.curr = e

    def s_html_fontstyle(self, tag, attrs):
        """ 15.2.1 Font style elements: the TT, I, B, BIG, SMALL,
            STRIKE, S, and U elements
            ('tt' is not considered an automatic style by OOo)
        """
        tagdict = {
           'b':      ['BoldX',{'fontweight':"bold",
                      'fontweightasian':"bold",'fontweightcomplex':"bold" }],
           'big':    ['BigX', {'fontsize':"120%"}],
           'i':      ['ItalicX', {'fontstyle':"italic", 'fontstyleasian':"italic", 'fontstylecomplex':"italic" }],
           'tt':     ['TeletypeX', {'fontname':"Courier", 'fontnameasian':"Courier", 'fontnamecomplex':"Courier" }],
           's':      ['StrikeX', {'textlinethroughstyle':"solid"}],
           'small':  ['SmallX', {'fontsize':"80%"}],
           'strike': ['StrikeX', {'textlinethroughstyle':"solid"}],
           'u':      ['UnderlineX', {'textunderlinestyle':"solid", 'textunderlinewidth':"auto",
                      'textunderlinecolor':"fontcolor"}],
        }
        stylename,styledecl = tagdict.get(tag,[None,None])
        if stylename and self.doc.getStyleByName(stylename) is None:
            style = Style(name=stylename, family="text")
            style.addElement(TextProperties(attributes=styledecl))
            self.doc.automaticstyles.addElement(style)
        if stylename:
            e = text.Span(stylename=stylename)
        else:
            e = text.Span()
        self.curr.addElement(e)
        self.curr = e


    def s_html_span(self, tag, attrs):
        e = text.Span()
        self.curr.addElement(e)
        self.curr = e

    def s_html_title(self, tag, attrs):
        e = dc.Title()
        self.doc.meta.addElement(e)
        self.curr = e

    def e_html_title(self, tag):
        self.curr = self.curr.parentNode

    def output_img(self, tag, attrs):
        src = listget(attrs, 'src', "Illegal IMG tag!")
        alt = listget(attrs, 'alt', src)
        # Must remember name of image and download it.
        self.write_odt(u'<draw:image xlink:href="Pictures/%s" xlink:type="simple" xlink:show="embed" xlink:actuate="onLoad"/>' % '00000.png')

    def s_html_a(self, tag, attrs):
        href = None
        href = listget(attrs, 'href', None)
        if href:
            if href in ("", "#"):
                href == self.baseurl
            elif href.find("://") >= 0:
                pass
            elif href[0] == '/':
                href = self.basehost + href
            e = text.A(type="simple", href=href)
        else:
            e = text.A()
#       if self.curr.parentNode.qname != text.P().qname:
#           p = text.P()
#           self.curr.addElement(p)
#           self.curr = p
        self.curr.addElement(e)
        self.curr = e

    def close_tag(self, tag):
        self.curr = self.curr.parentNode

    def s_html_dd(self, tag, attrs):
        if self.doc.getStyleByName("List_20_Contents") is None:
            style = Style(name="List_20_Contents", displayname="List Contents", family="paragraph",
                 parentstylename="Standard", attributes={'class':"html"})
            p = ParagraphProperties(marginleft="1cm", marginright="0cm", textindent="0cm", autotextindent="false")
            style.addElement(p)
            self.doc.styles.addElement(style)
        e = text.P(stylename="List_20_Contents")
        self.curr.addElement(e)
        self.curr = e

    def s_html_dt(self, tag, attrs):
        if self.doc.getStyleByName("List_20_Heading") is None:
            style = Style(name="List_20_Heading", displayname="List Heading", family="paragraph", parentstylename="Standard",
                 nextstylename="List_20_Contents", attributes={'class':"html"})
            p = ParagraphProperties(marginleft="0cm", marginright="0cm", textindent="0cm", autotextindent="false")
            style.addElement(p)
            self.doc.styles.addElement(style)
        e = text.P(stylename="List_20_Heading")
        self.curr.addElement(e)
        self.curr = e

    def output_ul(self, tag, attrs):
        self.write_odt(u'<text:list text:style-name="List_20_1">')

    def output_ol(self, tag, attrs):
        self.write_odt(u'<text:list text:style-name="Numbering_20_1">')

    def e_html_list(self, tag):
        self.write_odt(u'</text:list>')

    def s_html_li(self, tag, attrs):
        self.write_odt(u'<text:list-item><text:p text:style-name="P1">')

    def e_html_li(self, tag):
        self.write_odt(u'</text:p></text:list-item>')

    def s_html_headline(self, tag, attrs):
        stylename = "Heading_20_%s" % tag[1]
        if stylename == "Heading_20_1" and self.doc.getStyleByName("Heading_20_1") is None:
            style = Style(name="Heading_20_1", displayname="Heading 1",
                 family="paragraph", parentstylename="Heading", nextstylename="Text_20_body",
                 attributes={'class':"text"}, defaultoutlinelevel=1)
            p = TextProperties(fontsize="115%", fontweight="bold", fontsizeasian="115%",
                 fontweightasian="bold", fontsizecomplex="115%", fontweightcomplex="bold")
            style.addElement(p)
            self.doc.styles.addElement(style)

        if stylename == "Heading_20_2" and self.doc.getStyleByName("Heading_20_2") is None:
            style = Style(name="Heading_20_2", displayname="Heading 2",
                 family="paragraph", parentstylename="Heading", nextstylename="Text_20_body",
                 attributes={'class':"text"}, defaultoutlinelevel=2)
            p = TextProperties(fontsize="14pt", fontstyle="italic", fontweight="bold",
                 fontsizeasian="14pt", fontstyleasian="italic", fontweightasian="bold",
                 fontsizecomplex="14pt", fontstylecomplex="italic", fontweightcomplex="bold")
            style.addElement(p)
            self.doc.styles.addElement(style)

        if stylename == "Heading_20_3" and self.doc.getStyleByName("Heading_20_3") is None:
            style = Style(name="Heading_20_3", displayname="Heading 3",
                 family="paragraph", parentstylename="Heading", nextstylename="Text_20_body",
                 attributes={'class':"text"}, defaultoutlinelevel=3)
            p = TextProperties(fontsize="14pt", fontweight="bold", fontsizeasian="14pt",
                 fontweightasian="bold", fontsizecomplex="14pt", fontweightcomplex="bold")
            style.addElement(p)
            self.doc.styles.addElement(style)

        e = text.H(stylename="Heading_20_%s" % tag[1], outlinelevel=tag[1])
        self.curr.addElement(e)
        self.curr = e

    def s_html_table(self, tag, attrs):
        e = table.Table()
        self.curr.addElement(e)
        self.curr = e

    def e_html_table(self, tag):
        self.curr = self.curr.parentNode

    def s_html_td(self, tag, attrs):
        e = table.TableCell()
        self.curr.addElement(e)
        self.curr = e

    def s_html_tr(self, tag, attrs):
        e = table.TableRow()
        self.curr.addElement(e)
        self.curr = e

    def s_html_col(self, tag, attrs):
        e = table.TableColumn()
        self.curr.addElement(e)

    def s_html_section(self, tag, attrs):
        """ Outputs block tag such as <p> and <div> """
        name = self.find_attr(attrs,'id')
        if name is None:
            self.sectnum = self.sectnum + 1
            name = "Sect%d" % self.sectnum
        e = text.Section(name=name)
        self.curr.addElement(e)
        self.curr = e

    def e_html_section(self, tag):
        """ Outputs block tag such as <p> and <div> """
        self.curr = self.curr.parentNode

    def s_html_block(self, tag, attrs):
        """ Outputs block tag such as <p> and <div> """
        e = text.P(stylename="Text_20_body")
        self.curr.addElement(e)
        self.curr = e

    def e_html_block(self, tag):
        """ Outputs block tag such as <p> and <div> """
        self.curr = self.curr.parentNode
#
# HANDLE STARTTAG
#
    def handle_starttag(self, tag, attrs):
        self.pstack.append( (self.processelem, self.processcont) )
        tagobj = TagObject(tag, attrs, self.last_data_pos())
        self.tagstack.append(tagobj)

        method = self.elements.get(tag, (None, None))[0]
        if self.processelem and method:
            method(tag, attrs)
#
# HANDLE END
#
    def handle_endtag(self, tag):
        """ 
        """
        tagobj = self.tagstack.pop()
        method = self.elements.get(tag, (None, None))[1]
        if self.processelem and method:
            method(tag)
        self.processelem, self.processcont = self.pstack.pop()


#
# Data operations
#
    def handle_data(self, data):
        if data.strip() == '': return
        if self.processelem and self.processcont:
            self.curr.addText(data)

    def write_odt(self, data):
        """ Collect the data to show on the webpage """
        if type(data) == StringType:
            data = unicode(data, self.encoding)
        self.__data.append(data)

    def last_data_pos(self):
        return len(self.__data)

    def find_attr(self, attrs, key):
        """ Run through the attibutes to find a specific one
            return None if not found
        """
        for attr in attrs:
            if attr[0] == key:
                return attr[1]
        return None

#
# Tagstack operations
#
    def find_tag(self, tag):
        """ Run down the stack to find the last entry with the same tag name
            Not Tested
        """
        for tagitem in range(len(self.tagstack), 0, -1):
            if tagitem.tag == tag:
                return tagitem
        return None

    def handle_charref(self, name):
        """ Handle character reference for UNICODE
        """
        if name[0] in ('x', 'X'):
            try:
                n = int(name[1:],16)
            except ValueError:
                return
        else:
            try:
                n = int(name)
            except ValueError:
                return
        if not 0 <= n <= 65535:
            return
        self.handle_data(unichr(n))

    def handle_entityref(self, name):
        """Handle entity references.
        """
        table = htmlentitydefs.name2codepoint
        if name in table:
            self.handle_data(unichr(table[name]))
        else:
            return

    def handle_attr(self, attrval):
        """ Scan attribute values for entities and resolve them
            Simply calls handle_data
        """
        i = 0
        n = len(attrval)
        while i < n:
            match = ampersand.search(attrval, i) #
            if match:
                j = match.start()
            else:
                j = n
            if i < j: self.handle_data(attrval[i:j])
            i = j
            if i == n: break
            startswith = attrval.startswith
            if startswith('&#', i):
                match = charref.match(attrval, i)
                if match:
                    name = match.group()[2:-1]
                    self.handle_charref(name)
                    k = match.end()
                    if not startswith(';', k-1):
                        k = k - 1
                    i = k
                    continue
                else:
                    break
            elif startswith('&', i):
                match = entityref.match(attrval, i)
                if match:
                    name = match.group(1)
                    self.handle_entityref(name)
                    k = match.end()
                    if not startswith(';', k-1):
                        k = k - 1
                    i = k
                    continue
                match = incomplete.match(attrval, i)
                if match:
                    # match.group() will contain at least 2 chars
                    if match.group() == attrval[i:]:
                        self.error("EOF in middle of entity or char ref")
                    # incomplete
                    break
                elif (i + 1) < n:
                    # not the end of the buffer, and can't be confused
                    # with some other construct
                    self.handle_data("&")
                    i = i + 1
                else:
                    break
            else:
                assert 0, "interesting.search() lied"
        # end while
        if i < n:
            self.handle_data(attrval[i:n])
            i = n

def usage():
   sys.stderr.write("Usage: %s [-a] inputurl outputfile\n" % sys.argv[0])

if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "a", ["append"])

    except getopt.GetoptError:
        usage()
        sys.exit(2)

    appendto = False
    for o, a in opts:
        if o in ("-a", "--append"):
            appendto = True

    if appendto:
        doc = load(args[1])
    else:
        doc = OpenDocumentText()

    result = converturl(args[0], doc)
    print result.doc.xml()
    result.doc.save(args[1])


