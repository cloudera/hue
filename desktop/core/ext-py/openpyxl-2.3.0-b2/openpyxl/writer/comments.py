from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl


from openpyxl.utils.indexed_list import IndexedList
from openpyxl.compat import iteritems
from openpyxl.xml.constants import SHEET_MAIN_NS
from openpyxl.xml.functions import Element, SubElement, tostring
from openpyxl.utils import (
    column_index_from_string,
    coordinate_from_string,
)

vmlns = "urn:schemas-microsoft-com:vml"
officens = "urn:schemas-microsoft-com:office:office"
excelns = "urn:schemas-microsoft-com:office:excel"


class CommentWriter(object):

    def extract_comments(self):
        """
         extract list of comments and authors
         """
        for _coord, cell in iteritems(self.sheet._cells):
            if cell.comment is not None:
                self.authors.add(cell.comment.author)
                self.comments.append(cell.comment)

    def __init__(self, sheet):
        self.sheet = sheet
        self.authors = IndexedList()
        self.comments = []

        self.extract_comments()


    def write_comments(self):
        # produce xml
        root = Element("{%s}comments" % SHEET_MAIN_NS)
        authorlist_tag = SubElement(root, "{%s}authors" % SHEET_MAIN_NS)
        for author in self.authors:
            leaf = SubElement(authorlist_tag, "{%s}author" % SHEET_MAIN_NS)
            leaf.text = author

        commentlist_tag = SubElement(root, "{%s}commentList" % SHEET_MAIN_NS)
        for comment in self.comments:
            attrs = {'ref': comment._parent.coordinate,
                     'authorId': '%d' % self.authors.index(comment.author),
                     'shapeId': '0'}
            comment_tag = SubElement(commentlist_tag,
                                     "{%s}comment" % SHEET_MAIN_NS, attrs)

            text_tag = SubElement(comment_tag, "{%s}text" % SHEET_MAIN_NS)
            run_tag = SubElement(text_tag, "{%s}r" % SHEET_MAIN_NS)
            SubElement(run_tag, "{%s}rPr" % SHEET_MAIN_NS)
            t_tag = SubElement(run_tag, "{%s}t" % SHEET_MAIN_NS)
            t_tag.text = comment.text

        return tostring(root)

    def write_comments_vml(self):
        root = Element("xml")
        shape_layout = SubElement(root, "{%s}shapelayout" % officens,
                                  {"{%s}ext" % vmlns: "edit"})
        SubElement(shape_layout,
                   "{%s}idmap" % officens,
                   {"{%s}ext" % vmlns: "edit", "data": "1"})
        shape_type = SubElement(root,
                                "{%s}shapetype" % vmlns,
                                {"id": "_x0000_t202",
                                 "coordsize": "21600,21600",
                                 "{%s}spt" % officens: "202",
                                 "path": "m,l,21600r21600,l21600,xe"})
        SubElement(shape_type, "{%s}stroke" % vmlns, {"joinstyle": "miter"})
        SubElement(shape_type,
                   "{%s}path" % vmlns,
                   {"gradientshapeok": "t",
                    "{%s}connecttype" % officens: "rect"})

        for i, comment in enumerate(self.comments, 1026):
            shape = self._write_comment_shape(comment, i)
            root.append(shape)

        return tostring(root)

    def _write_comment_shape(self, comment, idx):
        # get zero-indexed coordinates of the comment
        col, row = coordinate_from_string(comment._parent.coordinate)
        row -= 1
        column = column_index_from_string(col) - 1

        style = ("position:absolute; margin-left:59.25pt;"
                 "margin-top:1.5pt;width:%(width)s;height:%(height)s;"
                 "z-index:1;visibility:hidden") % {'height': comment._height,
                                                   'width': comment._width}
        attrs = {
            "id": "_x0000_s%04d" % idx ,
            "type": "#_x0000_t202",
            "style": style,
            "fillcolor": "#ffffe1",
            "{%s}insetmode" % officens: "auto"
        }
        shape = Element("{%s}shape" % vmlns, attrs)

        SubElement(shape, "{%s}fill" % vmlns,
                   {"color2": "#ffffe1"})
        SubElement(shape, "{%s}shadow" % vmlns,
                   {"color": "black", "obscured": "t"})
        SubElement(shape, "{%s}path" % vmlns,
                   {"{%s}connecttype" % officens: "none"})
        textbox = SubElement(shape, "{%s}textbox" % vmlns,
                             {"style": "mso-direction-alt:auto"})
        SubElement(textbox, "div", {"style": "text-align:left"})
        client_data = SubElement(shape, "{%s}ClientData" % excelns,
                                 {"ObjectType": "Note"})
        SubElement(client_data, "{%s}MoveWithCells" % excelns)
        SubElement(client_data, "{%s}SizeWithCells" % excelns)
        SubElement(client_data, "{%s}AutoFill" % excelns).text = "False"
        SubElement(client_data, "{%s}Row" % excelns).text = "%d" % row
        SubElement(client_data, "{%s}Column" % excelns).text = "%d" % column
        return shape
