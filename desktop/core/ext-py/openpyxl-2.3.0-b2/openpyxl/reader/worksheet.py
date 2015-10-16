from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl

"""Reader for a single worksheet."""
from io import BytesIO
from warnings import warn

# compatibility imports
from openpyxl.xml.functions import iterparse

# package imports
from openpyxl.cell import Cell
from openpyxl.cell.read_only import _cast_number
from openpyxl.worksheet import Worksheet, ColumnDimension, RowDimension
from openpyxl.worksheet.page import PageMargins, PrintOptions, PrintPageSetup
from openpyxl.worksheet.protection import SheetProtection
from openpyxl.worksheet.views import SheetView
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.xml.constants import (
    SHEET_MAIN_NS,
    REL_NS,
    EXT_TYPES
)
from openpyxl.xml.functions import safe_iterator
from openpyxl.styles import Color
from openpyxl.formatting import ConditionalFormatting, Rule
from openpyxl.formula.translate import Translator
from openpyxl.worksheet.properties import WorksheetProperties
from openpyxl.utils import (
    coordinate_from_string,
    get_column_letter,
    column_index_from_string,
    coordinate_to_tuple,
    )
from openpyxl.descriptors.excel import ExtensionList, Extension


def _get_xml_iter(xml_source):
    """
    Possible inputs: strings, bytes, members of zipfile, temporary file
    Always return a file like object
    """
    if not hasattr(xml_source, 'read'):
        try:
            xml_source = xml_source.encode("utf-8")
        except (AttributeError, UnicodeDecodeError):
            pass
        return BytesIO(xml_source)
    else:
        try:
            xml_source.seek(0)
        except:
            pass
        return xml_source


class WorkSheetParser(object):

    COL_TAG = '{%s}col' % SHEET_MAIN_NS
    ROW_TAG = '{%s}row' % SHEET_MAIN_NS
    CELL_TAG = '{%s}c' % SHEET_MAIN_NS
    VALUE_TAG = '{%s}v' % SHEET_MAIN_NS
    FORMULA_TAG = '{%s}f' % SHEET_MAIN_NS
    MERGE_TAG = '{%s}mergeCell' % SHEET_MAIN_NS
    INLINE_STRING = "{%s}is/{%s}t" % (SHEET_MAIN_NS, SHEET_MAIN_NS)
    INLINE_RICHTEXT = "{%s}is/{%s}r/{%s}t" % (SHEET_MAIN_NS, SHEET_MAIN_NS, SHEET_MAIN_NS)

    def __init__(self, wb, title, xml_source, shared_strings):
        self.ws = wb.create_sheet(title=title)
        self.source = xml_source
        self.shared_strings = shared_strings
        self.guess_types = wb._guess_types
        self.data_only = wb.data_only
        self.styles = self.ws.parent._cell_styles
        self.differential_styles = wb._differential_styles
        self.keep_vba = wb.vba_archive is not None
        self.shared_formula_masters = {}  # {si_str: Translator()}

    def parse(self):
        dispatcher = {
            '{%s}mergeCells' % SHEET_MAIN_NS: self.parse_merge,
            '{%s}col' % SHEET_MAIN_NS: self.parse_column_dimensions,
            '{%s}row' % SHEET_MAIN_NS: self.parse_row_dimensions,
            '{%s}printOptions' % SHEET_MAIN_NS: self.parse_print_options,
            '{%s}pageMargins' % SHEET_MAIN_NS: self.parse_margins,
            '{%s}pageSetup' % SHEET_MAIN_NS: self.parse_page_setup,
            '{%s}headerFooter' % SHEET_MAIN_NS: self.parse_header_footer,
            '{%s}conditionalFormatting' % SHEET_MAIN_NS: self.parser_conditional_formatting,
            '{%s}autoFilter' % SHEET_MAIN_NS: self.parse_auto_filter,
            '{%s}sheetProtection' % SHEET_MAIN_NS: self.parse_sheet_protection,
            '{%s}dataValidations' % SHEET_MAIN_NS: self.parse_data_validation,
            '{%s}sheetPr' % SHEET_MAIN_NS: self.parse_properties,
            '{%s}legacyDrawing' % SHEET_MAIN_NS: self.parse_legacy_drawing,
            '{%s}sheetViews' % SHEET_MAIN_NS: self.parse_sheet_views,
            '{%s}extLst' % SHEET_MAIN_NS: self.parse_extensions,
                      }
        tags = dispatcher.keys()
        stream = _get_xml_iter(self.source)
        it = iterparse(stream, tag=tags)

        for _, element in it:
            tag_name = element.tag
            if tag_name in dispatcher:
                dispatcher[tag_name](element)
                element.clear()

        self.ws._current_row = self.ws.max_row

    def parse_cell(self, element):
        value = element.find(self.VALUE_TAG)
        if value is not None:
            value = value.text
        formula = element.find(self.FORMULA_TAG)
        data_type = element.get('t', 'n')
        coordinate = element.get('r')
        style_id = element.get('s')

        # assign formula to cell value unless only the data is desired
        if formula is not None and not self.data_only:
            data_type = 'f'
            if formula.text:
                value = "=" + formula.text
            else:
                value = "="
            formula_type = formula.get('t')
            if formula_type:
                if formula_type != "shared":
                    self.ws.formula_attributes[coordinate] = dict(formula.attrib)

                else:
                    si = formula.get('si')  # Shared group index for shared formulas

                    # The spec (18.3.1.40) defines shared formulae in
                    # terms of the following:
                    #
                    # `master`: "The first formula in a group of shared
                    #            formulas"
                    # `ref`: "Range of cells which the formula applies
                    #        to." It's a required attribute on the master
                    #        cell, forbidden otherwise.
                    # `shared cell`: "A cell is shared only when si is
                    #                 used and t is `shared`."
                    #
                    # Whether to use the cell's given formula or the
                    # master's depends on whether the cell is shared,
                    # whether it's in the ref, and whether it defines its
                    # own formula, as follows:
                    #
                    #  Shared?   Has formula? | In ref    Not in ref
                    # ========= ==============|======== ===============
                    #   Yes          Yes      | master   impl. defined
                    #    No          Yes      |  own         own
                    #   Yes           No      | master   impl. defined
                    #    No           No      |  ??          N/A
                    #
                    # The ?? is because the spec is silent on this issue,
                    # though my inference is that the cell does not
                    # receive a formula at all.
                    #
                    # For this implementation, we are using the master
                    # formula in the two "impl. defined" cases and no
                    # formula in the "??" case. This choice of
                    # implementation allows us to disregard the `ref`
                    # parameter altogether, and does not require
                    # computing expressions like `C5 in A1:D6`.
                    # Presumably, Excel does not generate spreadsheets
                    # with such contradictions.
                    if si in self.shared_formula_masters:
                        trans = self.shared_formula_masters[si]
                        value = trans.translate_formula(coordinate)
                    else:
                        self.shared_formula_masters[si] = Translator(value, coordinate)


        style_array = None
        if style_id is not None:
            style_id = int(style_id)
            style_array = self.styles[style_id]

        row, column = coordinate_to_tuple(coordinate)
        cell = Cell(self.ws, row=row, col_idx=column, style_array=style_array)
        self.ws._cells[(row, column)] = cell

        if value is not None:
            if data_type == 'n':
                value = _cast_number(value)
            elif data_type == 'b':
                value = bool(int(value))
            elif data_type == 's':
                value = self.shared_strings[int(value)]
            elif data_type == 'str':
                data_type = 's'

        else:
            if data_type == 'inlineStr':
                data_type = 's'
                child = element.find(self.INLINE_STRING)
                if child is None:
                    child = element.find(self.INLINE_RICHTEXT)
                if child is not None:
                    value = child.text

        if self.guess_types or value is None:
            cell.value = value
        else:
            cell._value=value
            cell.data_type=data_type


    def parse_merge(self, element):
        for mergeCell in safe_iterator(element, ('{%s}mergeCell' % SHEET_MAIN_NS)):
            self.ws.merge_cells(mergeCell.get('ref'))

    def parse_column_dimensions(self, col):
        attrs = dict(col.attrib)
        column = get_column_letter(int(attrs['min']))
        attrs['index'] = column
        if 'style' in attrs:
            attrs['style'] = self.styles[int(attrs['style'])]
        dim = ColumnDimension(self.ws, **attrs)
        self.ws.column_dimensions[column] = dim


    def parse_row_dimensions(self, row):
        attrs = dict(row.attrib)
        keys = set(attrs)
        for key in keys:
            if key == "s":
                attrs['s'] = self.styles[int(attrs['s'])]
            elif key.startswith('{'):
                del attrs[key]


        keys = set(attrs)
        if keys != set(['r', 'spans']) and keys != set(['r']):
            # don't create dimension objects unless they have relevant information
            dim = RowDimension(self.ws, **attrs)
            self.ws.row_dimensions[dim.index] = dim

        for cell in safe_iterator(row, self.CELL_TAG):
            self.parse_cell(cell)


    def parse_print_options(self, element):
        self.ws.print_options = PrintOptions.from_tree(element)

    def parse_margins(self, element):
        self.page_margins = PageMargins.from_tree(element)

    def parse_page_setup(self, element):
        self.ws.page_setup = PrintPageSetup.from_tree(element)

    def parse_header_footer(self, element):
        oddHeader = element.find('{%s}oddHeader' % SHEET_MAIN_NS)
        if oddHeader is not None and oddHeader.text is not None:
            self.ws.header_footer.setHeader(oddHeader.text)
        oddFooter = element.find('{%s}oddFooter' % SHEET_MAIN_NS)
        if oddFooter is not None and oddFooter.text is not None:
            self.ws.header_footer.setFooter(oddFooter.text)


    def parser_conditional_formatting(self, element):
        range_string = element.get('sqref')
        cfRules = element.findall('{%s}cfRule' % SHEET_MAIN_NS)
        self.ws.conditional_formatting.cf_rules[range_string] = []
        for node in cfRules:
            rule = Rule.from_tree(node)
            if rule.dxfId is not None:
                rule.dxf = self.differential_styles[rule.dxfId]
            self.ws.conditional_formatting.cf_rules[range_string].append(rule)


    def parse_auto_filter(self, element):
        self.ws.auto_filter.ref = element.get("ref")
        for fc in safe_iterator(element, '{%s}filterColumn' % SHEET_MAIN_NS):
            filters = fc.find('{%s}filters' % SHEET_MAIN_NS)
            if filters is None:
                continue
            vals = [f.get("val") for f in safe_iterator(filters, '{%s}filter' % SHEET_MAIN_NS)]
            blank = filters.get("blank")
            self.ws.auto_filter.add_filter_column(fc.get("colId"), vals, blank=blank)
        for sc in safe_iterator(element, '{%s}sortCondition' % SHEET_MAIN_NS):
            self.ws.auto_filter.add_sort_condition(sc.get("ref"), sc.get("descending"))

    def parse_sheet_protection(self, element):
        self.ws.protection = SheetProtection.from_tree(element)
        password = element.get("password")
        if password is not None:
            self.ws.protection.set_password(password, True)

    def parse_data_validation(self, element):
        for node in safe_iterator(element, "{%s}dataValidation" % SHEET_MAIN_NS):
            dv = DataValidation.from_tree(node)
            self.ws._data_validations.append(dv)


    def parse_properties(self, element):
        self.ws.sheet_properties = WorksheetProperties.from_tree(element)


    def parse_legacy_drawing(self, element):
        if self.keep_vba:
            # Create an id that will not clash with any other ids that will
            # be generated.
            self.ws.vba_controls = 'vbaControlId'


    def parse_sheet_views(self, element):
        for el in element.findall("{%s}sheetView" % SHEET_MAIN_NS):
            # according to the specification the last view wins
            pass
        self.ws.sheet_view = SheetView.from_tree(el)


    def parse_extensions(self, element):
        extLst = ExtensionList.from_tree(element)
        for e in extLst.ext:
            ext_type = EXT_TYPES.get(e.uri.upper(), "Unknown")
            msg = "{0} extension is not supported and will be removed".format(ext_type)
            warn(msg)


def fast_parse(xml_source, parent, sheet_title, shared_strings):
    parser = WorkSheetParser(parent, sheet_title, xml_source, shared_strings)
    parser.parse()
    return parser.ws
