from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl

from operator import itemgetter

from openpyxl.compat import safe_string
from openpyxl.xml.functions import xmlfile, Element, SubElement


def get_rows_to_write(worksheet):
    """Return all rows, and any cells that they contain"""
    # order cells by row
    rows = {}
    for (row, col), cell in worksheet._cells.items():
        rows.setdefault(row, []).append((col, cell))

    # add empty rows if styling has been applied
    for row_idx in worksheet.row_dimensions:
        if row_idx not in rows:
            rows[row_idx] = []

    return sorted(rows.items())


def write_rows(xf, worksheet):
    """Write worksheet data to xml."""

    all_rows = get_rows_to_write(worksheet)

    dims = worksheet.row_dimensions
    max_column = worksheet.max_column

    with xf.element("sheetData"):
        for row_idx, row in all_rows:

            attrs = {'r': '%d' % row_idx, 'spans': '1:%d' % max_column}
            if row_idx in dims:
                row_dimension = dims[row_idx]
                attrs.update(dict(row_dimension))

            with xf.element("row", attrs):
                for col, cell in sorted(row, key=itemgetter(0)):
                    if cell.value is None and not cell.has_style:
                        continue
                    el = write_cell(worksheet, cell, cell.has_style)
                    xf.write(el)


def write_cell(worksheet, cell, styled=None):
    coordinate = cell.coordinate
    attributes = {'r': coordinate}
    if styled:
        attributes['s'] = '%d' % cell.style_id

    if cell.data_type != 'f':
        attributes['t'] = cell.data_type

    value = cell._value

    el = Element("c", attributes)
    if value is None or value == "":
        return el

    if cell.data_type == 'f':
        shared_formula = worksheet.formula_attributes.get(coordinate, {})
        formula = SubElement(el, 'f', shared_formula)
        if value is not None:
            formula.text = value[1:]
            value = None

    if cell.data_type == 's':
        value = worksheet.parent.shared_strings.add(value)
    cell_content = SubElement(el, 'v')
    if value is not None:
        cell_content.text = safe_string(value)
    return el
