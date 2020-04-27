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

from odf.style import Style, ParagraphProperties, TextProperties

def addStandardStyles(doc):
    style = Style(name="Standard", family="paragraph", attributes={'class':"text"})
    doc.styles.addElement(style)

    style = Style(name="Text_20_body", displayname="Text body", family="paragraph", parentstylename="Standard", attributes={'class':"text"})
    p = ParagraphProperties(margintop="0cm", marginbottom="0.212cm")
    style.addElement(p)
    doc.styles.addElement(style)

    style = Style(name="List_20_Contents", displayname="List Contents", family="paragraph", parentstylename="Standard", attributes={'class':"html"})
    p = ParagraphProperties(marginleft="1cm", marginright="0cm", textindent="0cm", autotextindent="false")
    style.addElement(p)
    doc.styles.addElement(style)

    
    style = Style(name="List_20_Heading", displayname="List Heading", family="paragraph", parentstylename="Standard",
         nextstylename="List_20_Contents", attributes={'class':"html"})
    p = ParagraphProperties(marginleft="0cm", marginright="0cm", textindent="0cm", autotextindent="false")
    style.addElement(p)
    doc.styles.addElement(style)

    style = Style(name="Text_20_body_20_indent", displayname="Text body indent", family="paragraph", parentstylename="Text_20_body", attributes={'class':"text"})
    p = ParagraphProperties(marginleft="0.499cm", marginright="0cm", textindent="0cm", autotextindent="false")
    style.addElement(p)
    doc.styles.addElement(style)

    style = Style(name="Heading", family="paragraph", parentstylename="Standard", nextstylename="Text_20_body", attributes={'class':"text"})
    p = ParagraphProperties(margintop="0.423cm", marginbottom="0.212cm", keepwithnext="always")
    style.addElement(p)
    p = TextProperties(fontname="Nimbus Sans L", fontsize="14pt", fontnameasian="DejaVu LGC Sans", fontsizeasian="14pt", fontnamecomplex="DejaVu LGC Sans", fontsizecomplex="14pt")
    style.addElement(p)
    doc.styles.addElement(style)

    style = Style(name="Heading_20_1", displayname="Heading 1", family="paragraph", parentstylename="Heading", nextstylename="Text_20_body", attributes={'class':"text"}, defaultoutlinelevel=1)
    p = TextProperties(fontsize="115%", fontweight="bold", fontsizeasian="115%", fontweightasian="bold", fontsizecomplex="115%", fontweightcomplex="bold")
    style.addElement(p)
    doc.styles.addElement(style)

    style = Style(name="Heading_20_2", displayname="Heading 2", family="paragraph", parentstylename="Heading", nextstylename="Text_20_body", attributes={'class':"text"}, defaultoutlinelevel=2)
    p = TextProperties(fontsize="14pt", fontstyle="italic", fontweight="bold", fontsizeasian="14pt", fontstyleasian="italic", fontweightasian="bold", fontsizecomplex="14pt", fontstylecomplex="italic", fontweightcomplex="bold")
    style.addElement(p)
    doc.styles.addElement(style)

    style = Style(name="Heading_20_3", displayname="Heading 3", family="paragraph", parentstylename="Heading", nextstylename="Text_20_body", attributes={'class':"text"}, defaultoutlinelevel=3)
    p = TextProperties(fontsize="14pt", fontweight="bold", fontsizeasian="14pt", fontweightasian="bold", fontsizecomplex="14pt", fontweightcomplex="bold")
    style.addElement(p)
    doc.styles.addElement(style)

    style = Style(name="List", family="paragraph", parentstylename="Text_20_body", attributes={'class':"list"})
    doc.styles.addElement(style)

    style = Style(name="Caption", family="paragraph", parentstylename="Standard", attributes={'class':"extra"})
    p = ParagraphProperties(margintop="0.212cm", marginbottom="0.212cm", numberlines="false", linenumber="0")
    style.addElement(p)
    p = TextProperties(fontsize="12pt", fontstyle="italic", fontsizeasian="12pt", fontstyleasian="italic", fontsizecomplex="12pt", fontstylecomplex="italic")
    style.addElement(p)
    doc.styles.addElement(style)

    style = Style(name="Index", family="paragraph", parentstylename="Standard", attributes={'class':"index"})
    p = ParagraphProperties(numberlines="false", linenumber=0)
    doc.styles.addElement(style)

    style = Style(name="Source_20_Text", displayname="Source Text", family="text")
    p = TextProperties(fontname="Courier", fontnameasian="Courier", fontnamecomplex="Courier")
    style.addElement(p)
    doc.styles.addElement(style)

    style = Style(name="Variable", family="text")
    p = TextProperties(fontstyle="italic", fontstyleasian="italic", fontstylecomplex="italic")
    style.addElement(p)
    doc.styles.addElement(style)

    style = Style(name="Emphasis", family="text")
    p = TextProperties(fontstyle="italic", fontstyleasian="italic", fontstylecomplex="italic")
    style.addElement(p)
    doc.styles.addElement(style)

    style = Style(name="Strong_20_Emphasis", displayname="Strong Emphasis", family="text")
    p = TextProperties(fontweight="bold", fontweightasian="bold", fontweightcomplex="bold")
    style.addElement(p)
    doc.styles.addElement(style)

# Automatic styles
    style = Style(name="Bold", displayname="Bold", family="text")
    p = TextProperties(fontweight="bold", fontweightasian="bold", fontweightcomplex="bold")
    style.addElement(p)
    doc.automaticstyles.addElement(style)

    style = Style(name="Italic", family="text")
    p = TextProperties(fontstyle="italic", fontstyleasian="italic", fontstylecomplex="italic")
    style.addElement(p)
    doc.automaticstyles.addElement(style)

