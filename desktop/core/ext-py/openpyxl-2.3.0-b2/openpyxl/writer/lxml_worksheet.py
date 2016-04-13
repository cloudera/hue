from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl

from operator import itemgetter

from openpyxl.compat import safe_string

from .etree_worksheet import get_rows_to_write
from openpyxl.xml.functions import xmlfile

### LXML optimisation using xf.element to reduce instance creation

def write_rows(xf, worksheet):
    """Write worksheet data to xml."""

    all_rows = get_rows_to_write(worksheet)

    dims = worksheet.row_dimensions
    max_column = worksheet.max_column

    with xf.element("sheetData"):
        for row_idx, row in sorted(all_rows):

            attrs = {'r': '%d' % row_idx, 'spans': '1:%d' % max_column}
            if row_idx in dims:
                row_dimension = dims[row_idx]
                attrs.update(dict(row_dimension))
            with xf.element("row", attrs):

                for col, cell in sorted(row, key=itemgetter(0)):
                    if cell.value is None and not cell.has_style:
                        continue
                    write_cell(xf, worksheet, cell, cell.has_style)


def write_cell(xf, worksheet, cell, styled=False):
    coordinate = cell.coordinate
    attributes = {'r': coordinate}
    if styled:
        attributes['s'] = '%d' % cell.style_id

    if cell.data_type != 'f':
        attributes['t'] = cell.data_type

    value = cell._value

    if value == '' or value is None:
        with xf.element("c", attributes):
            return

    with xf.element('c', attributes):
        if cell.data_type == 'f':
            shared_formula = worksheet.formula_attributes.get(coordinate, {})
            with xf.element('f', shared_formula):
                if value is not None:
                    xf.write(value[1:])
                    value = None

        if cell.data_type == 's':
            value = worksheet.parent.shared_strings.add(value)
        with xf.element("v"):
            if value is not None:
                xf.write(safe_string(value))
