#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2007 Søren Roug, European Environment Agency
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
# Contributor(s):
#

from odf.opendocument import OpenDocumentText
from odf import style, text, dc, meta
import sys, getopt, time

def usage():
   sys.stderr.write("""Usage: %s [-l language] [-e encoding] [-T] [-a author]
\t[-c creation_date] [-d description] [-n etext] [-p publisher] [-t title] inputfile\n""" % sys.argv[0])

try:
    opts, args = getopt.getopt(sys.argv[1:], "a:n:c:d:e:l:p:t:T", ["author=",
        "date=", "created=", "description=", "number=", "title=",
        "language=", "publisher=", "encoding="])

except getopt.GetoptError:
    usage()
    sys.exit(2)

language = None
description = None
encoding = 'cp1252' # Codepage 1252 is a superset of ASCII and ISO-8859-1
argencoding = 'utf-8'
creator = ""
creationdate = None
title = ""
ebooknum = None
publisher = "Project Gutenberg"
copyrights = "http://www.gutenberg.org/license"
fn_is_title = False

for o, a in opts:
    if o in ("-l", "--language"):
        if len(a) > 3 and  a[2] != '-' and a[3] != '-' or len(a) > 6:
            sys.stderr.write("""Language must be a two or three letter language code optionally
\tfollowed by a hyphen and a two-letter country code""")
            sys.exit(2)
        language = a
    elif o in ("-e", "--encoding"):
        encoding = a
    elif o in ("-a", "--author"):
        creator = unicode(a, argencoding)
    elif o in ("-d", "--description"):
        description = a
    elif o in ("-c", "--date", "--created"):
        if len(a) > 10 and a[10] != "T":
            sys.stderr.write("""Date must be in ISO8601 format (YYYY-MM-DDTHH:MM:SS)\n""")
            sys.exit(2)
        if len(a) < 10 or (len(a) == 10 and a[4] != "-" and a[7] != "-"):
            sys.stderr.write("""Date must be in ISO8601 format (YYYY-MM-DD)\n""")
            sys.exit(2)
        creationdate = a
    elif o in ("-p", "--publisher"):
        publisher = a
    elif o in ("-n", "--number"):
        ebooknum = unicode(a, argencoding)
    elif o in ("-t", "--title"):
        title = unicode(a, argencoding)
    elif o == "-T":
        fn_is_title = True

if len(args) != 1:
    usage()
    sys.exit(2)

doc=OpenDocumentText()
textdoc = doc.text

if creator != "":
    doc.meta.addElement(meta.InitialCreator(text=creator))
    doc.meta.addElement(dc.Creator(text=creator))
if creationdate is not None:
    doc.meta.addElement(meta.CreationDate(text=creationdate))
    doc.meta.addElement(dc.Date(text=creationdate))
if description is not None:
    doc.meta.addElement(dc.Description(text=description))
if title != "":
    doc.meta.addElement(dc.Title(text=title))
if language is not None:
    doc.meta.addElement(dc.Language(text=language))
if publisher is not None:
#   doc.meta.addElement(dc.Publisher(text=publisher))
    doc.meta.addElement(meta.UserDefined(name="Publisher", text=publisher))
if copyrights is not None:
#   doc.meta.addElement(dc.Rights(text=copyrights))
    doc.meta.addElement(meta.UserDefined(name="Rights", text=copyrights))
if ebooknum is not None:
    doc.meta.addElement(meta.UserDefined(name="EText", text=ebooknum))

arial =  style.FontFace(name="Arial", fontfamily="Arial", fontfamilygeneric="swiss", fontpitch="variable")
doc.fontfacedecls.addElement(arial)

# Paragraph styles
standardstyle = style.Style(name="Standard", family="paragraph")
standardstyle.addElement(style.ParagraphProperties(marginbottom="0cm", margintop="0cm" ))
doc.styles.addElement(standardstyle)

h1style = style.Style(name="Heading 1", family="paragraph", defaultoutlinelevel="1")
h1style.addElement(style.TextProperties(attributes={'fontsize':"20pt", 'fontweight':"bold"}))
doc.styles.addElement(h1style)

textbodystyle = style.Style(name="Text body", family="paragraph", parentstylename=standardstyle)
textbodystyle.addElement(style.ParagraphProperties(attributes={'marginbottom':"0.212cm", 'margintop':"0cm",
  'textalign':"justify", 'justifysingleword':"false"}))
doc.styles.addElement(textbodystyle)

subtitlestyle = style.Style(name="Subtitle", family="paragraph", nextstylename=textbodystyle)
subtitlestyle.addElement(style.ParagraphProperties(textalign="center") )
subtitlestyle.addElement(style.TextProperties(fontsize="14pt", fontstyle="italic", fontname="Arial"))
doc.styles.addElement(subtitlestyle)

titlestyle = style.Style(name="Title", family="paragraph", nextstylename=subtitlestyle)
titlestyle.addElement(style.ParagraphProperties(textalign="center") )
titlestyle.addElement(style.TextProperties(fontsize="18pt", fontweight="bold", fontname="Arial"))
doc.styles.addElement(titlestyle)

# Text styles
emphasisstyle = style.Style(name="Emphasis",family="text")
emphasisstyle.addElement(style.TextProperties(fontstyle="italic"))
doc.styles.addElement(emphasisstyle)

# Make the Gutenberg sections grey
sectstyle  = style.Style(name="Sect1", family="section")
sectstyle.addElement(style.SectionProperties(backgroundcolor="#e6e6e6"))
doc.automaticstyles.addElement(sectstyle)

FULLLINE=55

paragraph=[]

def addparagraph(section):
    """ Join the paragraph list and add it to the section
    """
    global paragraph

    p = ' '.join(paragraph)
    textsegs = p.split('_')
    para = text.P(stylename=textbodystyle)
    section.addElement(para)
    if len(textsegs) > 1 and (len(textsegs) % 2) == 1:
        # We have found some kursive text segments
        for i in range(len(textsegs)):
            if len(textsegs[i]) > 0:
                if (i % 2) == 1:
                    y = text.Span(stylename=emphasisstyle, text=textsegs[i])
                    para.addElement(y)
                else:
                    para.addText(textsegs[i])
    else:
        para.addText(p)

def cleantext(s):
    if s[0] == '"' or s[-1] == '"':
        ls=list(s)
        if ls[0] == '"': ls[0] = u'“'
        if ls[-1] == '"': ls[-1] = u'”'
        s = ''.join(ls)
    s = s.replace('" ',u'” ')
    s = s.replace(' "',u' “')
    s = s.replace("'m",u"’m") # I'm
    s = s.replace("'s",u"’s") # genitive case
    s = s.replace("'t",u"’t") # don't, doesn't, haven't
    s = s.replace("'S",u"’S") # genitive case
    s = s.replace("'T",u"’T") # DON'T, etc
    s = s.replace("l'",u"l’")  # French
    s = s.replace("d'",u"d’")  # French
    if s.find('---') < 0:  # Don't replace double dash for lines
        s = s.replace('--',u'—')
    return s

def pretext(section, line, linelen):
    section.addElement(text.P(stylename=standardstyle, text=line))

def posttext(section, line, linelen):
    section.addElement(text.P(stylename=standardstyle, text=line))

def mainpart(section, line, linelen):
    global paragraph

    if linelen > 0 and len(paragraph) == 0 and \
       line.upper() == line and line.upper() != line.lower():
        # Headlines are always upper case
        style = h1style
        l = cleantext(line)
        section.addElement(text.H(outlinelevel=1, stylename=h1style, text=l))
    elif linelen >= FULLLINE:
        # In the middle of a paragraph
        paragraph.append(cleantext(line))
    elif linelen == 0:
        # End of paragraph
        if len(paragraph) > 0:
            addparagraph(section)
            paragraph=[]
    elif linelen < FULLLINE and len(paragraph) > 0:
        # Short tail of paragraph
        paragraph.append(cleantext(line))
    else:
        if line == title or line == title + " by " + creator:
            section.addElement(text.P( stylename=titlestyle, text=cleantext(line)))
            return
        if line == "by" or line == creator:
            section.addElement(text.P( stylename=subtitlestyle, text=cleantext(line)))
            return
        if len(paragraph) > 0:
            addparagraph(section)
            paragraph=[]
        section.addElement(text.P(stylename=textbodystyle, text=cleantext(line)))


PRETEXT = 1
MAINPART = 2
POSTTEXT = 3
textpart = PRETEXT

# Start in the preamble
section = text.Section(stylename=sectstyle, name="preamble") #, display="none")
textdoc.addElement(section)

filename = args[0]
if fn_is_title and title is not None and title != "":
    outfn = title
else:
    suffixi = filename.rfind(".")
    if suffixi > 1:
       outfn = filename[:suffixi]
    else:
       outfn = "interimname"

f = open(filename)
for rawline in f:
    line = unicode(rawline.strip(), encoding)
    linelen = len(line)
    if line.find("*** END OF TH") == 0:
        textpart = POSTTEXT
        section = text.Section(stylename=sectstyle, name="license") #, display="none")
        textdoc.addElement(section)
    if textpart == PRETEXT:
        pretext(section, line, linelen)
        if line.find("*** START OF TH") == 0 or \
           line.find("*END THE SMALL PRINT!") == 0 or \
           line.find("*END*THE SMALL PRINT!") == 0:
            textpart = MAINPART
    elif textpart == MAINPART:
        section = textdoc
        mainpart(section, line, linelen)
    else:
        posttext(section, line, linelen)

#   print d.contentxml()
doc.save(outfn, True)
