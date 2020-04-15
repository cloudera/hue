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

# This is an example of an OpenDocument Text with an embedded Chart.
#
from odf.opendocument import OpenDocumentChart, OpenDocumentText
from odf import chart, style, table, text, draw

# import a support class from the examples directory
from datatable import DataTable

class BarChart(object):

    def __init__(self):
        self.charttype = 'chart:bar'
        self.subtype = 'normal'  # 'percentage', 'stacked' or 'normal'
        self.threedimensional = "false"
        self.x_axis = "X"
        self.y_axis = "Y"
        self.values = (1,2,3)
        self.title = None
        self.subtitle = None

    def __call__(self, doc):
        chartstyle  = style.Style(name="chartstyle", family="chart")
        chartstyle.addElement( style.GraphicProperties(stroke="none", fillcolor="#ffffff"))
        doc.automaticstyles.addElement(chartstyle)

        mychart = chart.Chart(width="476pt", height="404pt",stylename=chartstyle, attributes={'class':self.charttype})
        doc.chart.addElement(mychart)

        # Title
        if self.title:
            titlestyle = style.Style(name="titlestyle", family="chart")
            titlestyle.addElement( style.GraphicProperties(stroke="none", fill="none"))
            titlestyle.addElement( style.TextProperties(fontfamily="'Nimbus Sans L'",
                    fontfamilygeneric="swiss", fontpitch="variable", fontsize="13pt"))
            doc.automaticstyles.addElement(titlestyle)

            mytitle = chart.Title(x="185pt", y="27pt", stylename=titlestyle)
            mytitle.addElement( text.P(text=self.title))
            mychart.addElement(mytitle)

        # Subtitle
        if self.subtitle:
            subtitlestyle = style.Style(name="subtitlestyle", family="chart")
            subtitlestyle.addElement( style.GraphicProperties(stroke="none", fill="none"))
            subtitlestyle.addElement( style.TextProperties(fontfamily="'Nimbus Sans L'",
                    fontfamilygeneric="swiss", fontpitch="variable", fontsize="10pt"))
            doc.automaticstyles.addElement(subtitlestyle)

            subtitle = chart.Subtitle(x="50pt", y="50pt", stylename=subtitlestyle)
            subtitle.addElement( text.P(text= self.subtitle))
            mychart.addElement(subtitle)

        # Legend
        legendstyle = style.Style(name="legendstyle", family="chart")
        legendstyle.addElement( style.GraphicProperties(fill="none"))
        legendstyle.addElement( style.TextProperties(fontfamily="'Nimbus Sans L'",
                fontfamilygeneric="swiss", fontpitch="variable", fontsize="8pt"))
        doc.automaticstyles.addElement(legendstyle)

        mylegend = chart.Legend(legendposition="end", legendalign="center", stylename=legendstyle)
        mychart.addElement(mylegend)

        # Plot area
        plotstyle = style.Style(name="plotstyle", family="chart")
        if self.subtype == "stacked": percentage="false"; stacked="true"
        elif self.subtype == "percentage": percentage="true"; stacked="false"
        else: percentage="false"; stacked="false"
        plotstyle.addElement( style.ChartProperties(seriessource="columns",
                percentage=percentage, stacked=stacked,
                threedimensional=self.threedimensional))
        doc.automaticstyles.addElement(plotstyle)

        plotarea = chart.PlotArea(datasourcehaslabels=self.datasourcehaslabels, stylename=plotstyle)
        mychart.addElement(plotarea)

        # Style for the X,Y axes
        axisstyle = style.Style(name="axisstyle", family="chart")
        axisstyle.addElement( style.ChartProperties(displaylabel="true"))
        axisstyle.addElement( style.TextProperties(fontfamily="'Nimbus Sans L'",
                fontfamilygeneric="swiss", fontpitch="variable", fontsize="8pt"))
        doc.automaticstyles.addElement(axisstyle)

        # Title for the X axis
        xaxis = chart.Axis(dimension="x", name="primary-x", stylename=axisstyle)
        plotarea.addElement(xaxis)
        xt = chart.Title()
        xaxis.addElement(xt)
        xt.addElement(text.P(text=self.x_axis))

        # Title for the Y axis
        yaxis = chart.Axis(dimension="y", name="primary-y", stylename=axisstyle)
        plotarea.addElement(yaxis)
        yt = chart.Title()
        yaxis.addElement(yt)
        yt.addElement(text.P(text=self.y_axis))

        # Set up the data series. OOo doesn't show correctly without them.
        s = chart.Series(valuescellrangeaddress="local-table.B2:.B6", labelcelladdress="local-table.B1")
        s.addElement(chart.DataPoint(repeated=5))
        plotarea.addElement(s)

        s = chart.Series(valuescellrangeaddress="local-table.C2:.C6", labelcelladdress="local-table.C1")
        s.addElement(chart.DataPoint(repeated=5))
        plotarea.addElement(s)

        # The data are placed in a table inside the chart object - but could also be a
        # table in the main document
        datatable = DataTable(self.values)
        datatable.datasourcehaslabels = self.datasourcehaslabels
        mychart.addElement(datatable())

if __name__ == "__main__":
    # Create the subdocument
    chartdoc = OpenDocumentChart()
    mychart = BarChart()
    mychart.title = "SPECTRE"
    mychart.subtitle = "SPecial Executive for Counter-intelligence, Terrorism, Revenge and Extortion"
    mychart.x_axis = "Divisions"
    mychart.y_axis = u"€ (thousand)"
    # These represent the data. Six rows in three columns
    mychart.values = (
        ('','Expense','Revenue'),
        ('Counterfeit',1000,1500),
        ('Murder',1100,1150),
        ('Prostitution',3200,2350),
        ('Blackmail',1100,1150),
        ('Larceny',1000,1750)
    )
    mychart.datasourcehaslabels = "both"
    mychart(chartdoc)

    # Create the containg document
    textdoc = OpenDocumentText()
    # Create a paragraph to contain the frame. You can put the frame directly
    # as a child og textdoc.text, but both Kword and OOo has problems wiht
    # this approach.
    p = text.P()
    textdoc.text.addElement(p)
    # Create the frame.
    df = draw.Frame(width="476pt", height="404pt", anchortype="paragraph")
    p.addElement(df)

    # Here we add the subdocument to the main document. We get back a reference
    # to use in the href.
    objectloc = textdoc.addObject(chartdoc)
    do = draw.Object(href=objectloc)
    # Put the object inside the frame
    df.addElement(do)
    textdoc.save("spectre-balance", True)
