#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2007-2009 Søren Roug, European Environment Agency
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
import os,sys,getopt,struct
from cStringIO import StringIO
from odf.opendocument import OpenDocumentPresentation
from odf.style import Style, MasterPage, PageLayout, PageLayoutProperties, \
TextProperties, GraphicProperties, ParagraphProperties, DrawingPageProperties
from odf.text import P
from odf.draw  import Page, Frame, TextBox, Image


def getImageInfo(data):
    size = len(data)
    height = -1
    width = -1
    w = -1
    h = -1
    content_type = ''

    # handle GIFs
    if (size >= 10) and data[:6] in ('GIF87a', 'GIF89a'):
        # Check to see if content_type is correct
        content_type = 'image/gif'
        w, h = struct.unpack("<HH", data[6:10])
        width = int(w)
        height = int(h)

    # See PNG v1.2 spec (http://www.cdrom.com/pub/png/spec/)
    # Bytes 0-7 are below, 4-byte chunk length, then 'IHDR'
    # and finally the 4-byte width, height
    elif ((size >= 24) and (data[:8] == '\211PNG\r\n\032\n')
          and (data[12:16] == 'IHDR')):
        content_type = 'image/png'
        w, h = struct.unpack(">LL", data[16:24])
        width = int(w)
        height = int(h)

    # Maybe this is for an older PNG version.
    elif (size >= 16) and (data[:8] == '\211PNG\r\n\032\n'):
        # Check to see if we have the right content type
        content_type = 'image/png'
        w, h = struct.unpack(">LL", data[8:16])
        width = int(w)
        height = int(h)

    # handle JPEGs
    elif (size >= 2) and (data[:2] == '\377\330'):
        content_type = 'image/jpeg'
        jpeg = StringIO(data)
        jpeg.read(2)
        b = jpeg.read(1)
        try:
            while (b and ord(b) != 0xDA):
                while (ord(b) != 0xFF): b = jpeg.read(1)
                while (ord(b) == 0xFF): b = jpeg.read(1)
                if (ord(b) >= 0xC0 and ord(b) <= 0xC3):
                    jpeg.read(3)
                    h, w = struct.unpack(">HH", jpeg.read(4))
                    break
                else:
                    jpeg.read(int(struct.unpack(">H", jpeg.read(2))[0])-2)
                b = jpeg.read(1)
            width = int(w)
            height = int(h)
        except: pass

    return content_type, width, height

def usage():
   sys.stderr.write("Usage: %s [-o outputfile] [input-directory]\n" % sys.argv[0])

if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "o:", ["output="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    outputfile = "photoalbum.odp"

    for o, a in opts:
        if o in ("-o", "--output"):
            outputfile = a
            if outputfile[-4:] != ".odp": outputfile += ".odp"

    doc = OpenDocumentPresentation()

    # We must describe the dimensions of the page
    pagelayout = PageLayout(name="MyLayout")
    doc.automaticstyles.addElement(pagelayout)
    pagelayout.addElement(PageLayoutProperties(margin="0pt", pagewidth="800pt",
        pageheight="600pt", printorientation="landscape"))

    # Style for the title frame of the page
    # We set a centered 34pt font with yellowish background
    titlestyle = Style(name="MyMaster-title", family="presentation")
    titlestyle.addElement(ParagraphProperties(textalign="center"))
    titlestyle.addElement(TextProperties(fontsize="34pt"))
    titlestyle.addElement(GraphicProperties(fillcolor="#ffff99"))
    doc.styles.addElement(titlestyle)

    # Style for the photo frame
    photostyle = Style(name="MyMaster-photo", family="presentation")
    doc.styles.addElement(photostyle)

    # Create automatic transition
    dpstyle = Style(name="dp1", family="drawing-page")
    dpstyle.addElement(DrawingPageProperties(transitiontype="automatic",
       transitionstyle="move-from-top", duration="PT5S"))
    doc.automaticstyles.addElement(dpstyle)

    # Every drawing page must have a master page assigned to it.
    masterpage = MasterPage(name="MyMaster", pagelayoutname=pagelayout)
    doc.masterstyles.addElement(masterpage)

    if len(args) == 0:
        pict_dir = "."
    else:
        pict_dir = args[0]
    # Slides
    for picture in os.listdir(pict_dir):
        try:
            pictdata = open(pict_dir + "/" + picture).read()
        except:
            continue
        ct,w,h = getImageInfo(pictdata) # Get dimensions in pixels
        if ct != 'image/jpeg':
            continue
        if w > 720:
           h = float(h) * 720.0 / float(w)
           w = 720.0
        if h > 540.0:
           w = float(w) * 540.0 / float(h)
           h = 540.0

        page = Page(stylename=dpstyle, masterpagename=masterpage)
        doc.presentation.addElement(page)
        titleframe = Frame(stylename=titlestyle, width="720pt", height="56pt", x="40pt", y="10pt")
        page.addElement(titleframe)
        textbox = TextBox()
        titleframe.addElement(textbox)
        textbox.addElement(P(text=picture))

        offsetx = 400.0 - w/2.0
        photoframe = Frame(stylename=photostyle, width="%fpt" % w, height="%fpt" % h, x="%fpt" % offsetx, y="56pt")
        page.addElement(photoframe)
        href = doc.addPicture(pict_dir + "/" + picture)
        photoframe.addElement(Image(href=href))

    doc.save(outputfile)
