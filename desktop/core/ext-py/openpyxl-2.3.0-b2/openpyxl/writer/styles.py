from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl

"""Write the shared style table."""

# package imports

from openpyxl.compat import safe_string
from openpyxl.utils.indexed_list import IndexedList
from openpyxl.xml.functions import (
    Element,
    SubElement,
    ConditionalElement,
    tostring,
    )
from openpyxl.xml.constants import SHEET_MAIN_NS

from openpyxl.styles.colors import COLOR_INDEX
from openpyxl.styles import DEFAULTS
from openpyxl.styles.numbers import BUILTIN_FORMATS_REVERSE
from openpyxl.styles.fills import GradientFill, PatternFill


class StyleWriter(object):

    def __init__(self, workbook):
        self.wb = workbook
        self._root = Element('styleSheet', {'xmlns': SHEET_MAIN_NS})

    def write_table(self):
        self._write_number_formats()
        self._write_fonts()
        self._write_fills()
        self._write_borders()

        self._write_named_styles()
        self._write_cell_styles()
        self._write_style_names()
        self._write_differential_styles()
        self._write_table_styles()
        self._write_colors()

        return tostring(self._root)


    def _write_number_formats(self):
        node = SubElement(self._root, 'numFmts', count= "%d" % len(self.wb._number_formats))
        for idx, nf in enumerate(self.wb._number_formats, 164):
            SubElement(node, 'numFmt', {'numFmtId':'%d' % idx,
                                        'formatCode':'%s' % nf}
                       )

    def _write_fonts(self):
        fonts_node = SubElement(self._root, 'fonts', count="%d" % len(self.wb._fonts))
        for font in self.wb._fonts:
            fonts_node.append(font.to_tree())


    def _write_fills(self):
        fills_node = SubElement(self._root, 'fills', count="%d" % len(self.wb._fills))
        for fill in self.wb._fills:
            fills_node.append(fill.to_tree())

    def _write_borders(self):
        """Write the child elements for an individual border section"""
        borders_node = SubElement(self._root, 'borders', count="%d" % len(self.wb._borders))
        for border in self.wb._borders:
            borders_node.append(border.to_tree())

    def _write_named_styles(self):
        styles = self.wb._named_styles
        cell_style_xfs = SubElement(self._root, 'cellStyleXfs', count="%d" % len(styles))

        for style in self.wb._named_styles.values():
            attrs = {}

            attrs['fontId'] =  str(self.wb._fonts.add(style.font))
            attrs['borderId'] = str(self.wb._borders.add(style.border))
            attrs['fillId'] =  str(self.wb._fills.add(style.fill))
            fmt = style.number_format
            if fmt in BUILTIN_FORMATS_REVERSE:
                fmt = BUILTIN_FORMATS_REVERSE[fmt]
            else:
                fmt = self.wb._number_formats.add(style.number_format) + 164
            attrs['numFmtId'] = str(fmt)

            SubElement(cell_style_xfs, 'xf', attrs)

    def _write_cell_styles(self):
        """ write styles combinations based on ids found in tables """
        # writing the cellXfs
        cell_xfs = SubElement(self._root, 'cellXfs',
                              count='%d' % len(self.wb._cell_styles))

        for style in self.wb._cell_styles:

            node = style.to_tree()
            cell_xfs.append(node)

            if style.applyAlignment:
                al = self.wb._alignments[style.alignmentId]
                el = al.to_tree()
                node.append(el)

            if style.applyProtection:
                prot = self.wb._protections[style.protectionId]
                el = prot.to_tree()
                node.append(el)


    def _write_style_names(self):
        styles = self.wb._named_styles

        cell_styles = SubElement(self._root, 'cellStyles', count=str(len(styles)))

        for idx, style in enumerate(styles.values()):
            attrs = dict(style)
            attrs['xfId'] = str(idx)
            SubElement(cell_styles, 'cellStyle', attrs)


    def _write_differential_styles(self):
        dxfs = SubElement(self._root, "dxfs", count=str(len(self.wb._differential_styles)))
        for fmt in self.wb._differential_styles:
            dxfs.append(fmt.to_tree())
        return dxfs


    def _write_table_styles(self):

        SubElement(self._root, 'tableStyles',
            {'count':'0', 'defaultTableStyle':'TableStyleMedium9',
            'defaultPivotStyle':'PivotStyleLight16'})

    def _write_colors(self):
        """
        Workbook contains a different colour index.
        """

        if self.wb._colors == COLOR_INDEX:
            return

        cols = SubElement(self._root, "colors")
        rgb = SubElement(cols, "indexedColors")
        for color in self.wb._colors:
            SubElement(rgb, "rgbColor", rgb=color)
