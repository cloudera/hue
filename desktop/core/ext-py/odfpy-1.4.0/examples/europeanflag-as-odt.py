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

# This is an example of an OpenDocument Text.
# We are going to draw the European flag. I chose this motive because
# it has just the right complexity for an example. It contains 12 five-edge
# stars in a circle on a blue background.  The production specifications can
# be found at http://europa.eu/abc/symbols/emblem/index_en.htm
#
# The stars are drawn with a vector-oriented "turtle" the way Seymour Papert's
# LOGO language does.
import math
from odf.opendocument import OpenDocumentText
from odf.style import Style, GraphicProperties, DrawingPageProperties
from odf.text import P
from odf.draw import G, Polygon, Rect

class VectorSet:
    """ A class to simulate LOGO's turtle. The turtle starts a 0,0 pointing
        right along the x-axis, since we use the mathematical coordinate system.
    """
    orientation = 0 # Degrees
    x = 0.0
    y = 0.0
    polygon = []

    def forward(self, length):
        orirad = math.radians(self.orientation)
        self.x = self.x + length * math.cos(orirad)
        self.y = self.y + length * math.sin(orirad)

    def right(self, turn):
        self.orientation = (self.orientation + turn) % 360

    def left(self, turn):
        self.orientation = (self.orientation - turn) % 360

    def mark(self):
        self.polygon.append((self.x,self.y))

    def firstmark(self):
        self.polygon.append(self.polygon[0])

    def getpoints(self):
        """ Return the polygon points """
        strpairs = ["%.0f,%.0f" % item for item in self.polygon]
        return ' '.join(strpairs)

    def getviewbox(self):
        ''' The value of the viewBox attribute is a list of four numbers
            <min-x>, <min-y>, <width> and <height>'''
        xvals = [ item[0] for item in self.polygon]
        maxx = int(reduce(max,xvals)) + 1
        minx = int(reduce(min,xvals))
        yvals = [ item[1] for item in self.polygon]
        maxy = int(reduce(max,yvals)) + 1
        miny = int(reduce(min,yvals))
        return minx, miny, maxx-minx, maxy-miny


# Create the document
doc = OpenDocumentText()

# The blue background style of the flag
backgroundstyle = Style(family="graphic", name="blueback")
backgroundstyle.addElement(GraphicProperties(fill="solid", fillcolor="#003399", stroke="none"))
doc.automaticstyles.addElement(backgroundstyle)

# The style for the stars
starstyle = Style(family="graphic", name="starstyle")
starstyle.addElement(GraphicProperties(fill="solid", fillcolor="#ffcc00", stroke="none"))
doc.automaticstyles.addElement(starstyle)

# Create a paragraph to contain the drawing
drawpage = P()
doc.text.addElement(drawpage)

group=G()
drawpage.addElement(group)

turtle = VectorSet()
# Draw the edges
turtle.mark()
for edge in [ 0,1,2,3,5 ]:
    turtle.forward(100)
    turtle.mark()
    turtle.right(144)
    turtle.forward(100)
    turtle.mark()
    turtle.left(72)
turtle.firstmark()

# Draw a rectangle containing the blue background
group.addElement(Rect(height="120mm", width="180mm", x="0mm", y="0mm", stylename=backgroundstyle))

viewbox = ' '.join(map(str,turtle.getviewbox()))
points = turtle.getpoints()

# Go around in a circle in twelve steps
for deg in range(0,360,30):
    x = 83.3 + math.cos(math.radians(deg)) * 40
    y = 53.3 + math.sin(math.radians(deg)) * 40
    group.addElement(Polygon(points=points,
       stylename=starstyle, viewbox=viewbox, width="13.3mm", height="13.3mm", x="%0.2fmm" % x, y="%0.2fmm" % y))

# Save the work
doc.save("europeanflag", True)
