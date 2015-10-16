from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl

"""Read shared style definitions"""

# package imports
from openpyxl.compat import OrderedDict, zip
from openpyxl.utils.indexed_list import IndexedList
from openpyxl.styles import (
    numbers,
    Font,
    Fill,
    PatternFill,
    GradientFill,
    Border,
    Side,
    Protection,
    Alignment,
    borders,
)
from openpyxl.styles.differential import DifferentialStyle
from openpyxl.styles.colors import COLOR_INDEX, Color
from openpyxl.styles.styleable import StyleArray
from openpyxl.styles.named_styles import NamedStyle
from openpyxl.xml.functions import fromstring, safe_iterator, localname
from openpyxl.xml.constants import SHEET_MAIN_NS, ARC_STYLE
from copy import deepcopy


class SharedStylesParser(object):

    def __init__(self, xml_source):
        self.root = fromstring(xml_source)
        self.cell_styles = IndexedList()
        self.differential_styles = []
        self.color_index = COLOR_INDEX
        self.font_list = IndexedList()
        self.fill_list = IndexedList()
        self.border_list = IndexedList()
        self.alignments = IndexedList([Alignment()])
        self.protections = IndexedList([Protection()])
        self.custom_number_formats = {}
        self.number_formats = IndexedList()

    def parse(self):
        self.parse_custom_num_formats()
        self.parse_color_index()
        self.font_list = IndexedList(self.parse_fonts())
        self.fill_list = IndexedList(self.parse_fills())
        self.border_list = IndexedList(self.parse_borders())
        self.parse_dxfs()
        self.parse_cell_styles()
        self.parse_named_styles()


    def parse_custom_num_formats(self):
        """Read in custom numeric formatting rules from the shared style table"""
        custom_formats = {}
        num_fmts = self.root.findall('{%s}numFmts/{%s}numFmt' % (SHEET_MAIN_NS, SHEET_MAIN_NS))
        for node in num_fmts:
            idx = int(node.get('numFmtId'))
            self.custom_number_formats[idx] = node.get('formatCode')
            self.number_formats.append(node.get('formatCode'))


    def parse_color_index(self):
        """Read in the list of indexed colors"""
        colors =\
            self.root.findall('{%s}colors/{%s}indexedColors/{%s}rgbColor' %
                              (SHEET_MAIN_NS, SHEET_MAIN_NS, SHEET_MAIN_NS))
        if not colors:
            return
        self.color_index = IndexedList([node.get('rgb') for node in colors])


    def parse_dxfs(self):
        """Read in the dxfs effects - used by conditional formatting."""
        for node in self.root.findall("{%s}dxfs/{%s}dxf" % (SHEET_MAIN_NS, SHEET_MAIN_NS) ):
            self.differential_styles.append(DifferentialStyle.from_tree(node))


    def parse_fonts(self):
        """Read in the fonts"""
        fonts = self.root.findall('{%s}fonts/{%s}font' % (SHEET_MAIN_NS, SHEET_MAIN_NS))
        for node in fonts:
            yield Font.from_tree(node)


    def parse_fills(self):
        """Read in the list of fills"""
        fills = self.root.findall('{%s}fills/{%s}fill' % (SHEET_MAIN_NS, SHEET_MAIN_NS))
        for fill in fills:
            yield Fill.from_tree(fill)

    def parse_borders(self):
        """Read in the boarders"""
        borders = self.root.findall('{%s}borders/{%s}border' % (SHEET_MAIN_NS, SHEET_MAIN_NS))
        for border_node in borders:
            yield Border.from_tree(border_node)


    def parse_named_styles(self):
        """
        Extract named styles
        """
        node = self.root.find("{%s}cellStyleXfs" % SHEET_MAIN_NS)
        styles = self._parse_xfs(node)

        names = self._parse_style_names()
        for style in names.values():
            _id = styles[style.xfId]
            style.border = self.border_list[_id.borderId]
            style.fill = self.fill_list[_id.fillId]
            style.font = self.font_list[_id.fontId]
            if _id.alignmentId:
                style.alignment = self.alignments[_id.alignmentId]
            if _id.protectionId:
                style.protection = self.protections[_id.protectionId]
        self.named_styles = names


    def _parse_style_names(self):
        """
        Extract style names. There can be duplicates in which case last wins
        """
        node = self.root.find("{%s}cellStyles" % SHEET_MAIN_NS)
        names = {}
        for _name in node:
            name = _name.get("name")
            style = NamedStyle(name=name,
                               builtinId=_name.get("builtinId"),
                               hidden=_name.get("hidden")
                               )
            style.xfId = int(_name.get("xfId"))
            names[name] = style
        return names


    def parse_cell_styles(self):
        """
        Extract individual cell styles
        """
        node = self.root.find('{%s}cellXfs' % SHEET_MAIN_NS)
        if node is not None:
            self.cell_styles = self._parse_xfs(node)


    def _parse_xfs(self, node):
        """Read styles from the shared style table"""
        _style_ids = []

        xfs = safe_iterator(node, '{%s}xf' % SHEET_MAIN_NS)
        for xf in xfs:
            style = StyleArray.from_tree(xf)

            al = xf.find('{%s}alignment' % SHEET_MAIN_NS)
            if al is not None:
                alignment = Alignment(**al.attrib)
                style.alignmentId = self.alignments.add(alignment)

            prot = xf.find('{%s}protection' % SHEET_MAIN_NS)
            if prot is not None:
                protection = Protection(**prot.attrib)
                style.protectionId = self.protections.add(protection)

            numFmtId = int(xf.get("numFmtId", 0))
            # check for custom formats and normalise indices

            if numFmtId in self.custom_number_formats:
                format_code = self.custom_number_formats[numFmtId]
                style.numFmtId = self.number_formats.add(format_code) + 164

            _style_ids.append(style)
        return IndexedList(_style_ids)


def read_style_table(archive):
    if ARC_STYLE in archive.namelist():
        xml_source = archive.read(ARC_STYLE)
        p = SharedStylesParser(xml_source)
        p.parse()
        return p


def bool_attrib(element, attr):
    """
    Cast an XML attribute that should be a boolean to a Python equivalent
    None, 'f', '0' and 'false' all cast to False, everything else to true
    """
    value = element.get(attr)
    if not value or value in ("false", "f", "0"):
        return False
    return True
