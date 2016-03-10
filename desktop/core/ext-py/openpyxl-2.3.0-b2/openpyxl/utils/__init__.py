from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl

"""
Collection of utilities used within the package and also available for client code
"""

import datetime
import re

from .formulas import FORMULAE
from openpyxl.compat import basestring
from openpyxl.utils.exceptions import CellCoordinatesException

# constants
COORD_RE = re.compile('^[$]?([A-Z]+)[$]?(\d+)$')
RANGE_EXPR = """
[$]?(?P<min_col>[A-Z]+)
[$]?(?P<min_row>\d+)
(:[$]?(?P<max_col>[A-Z]+)
[$]?(?P<max_row>\d+))?
"""
ABSOLUTE_RE = re.compile('^' + RANGE_EXPR +'$', re.VERBOSE)
SHEETRANGE_RE = re.compile("""
^(('(?P<quoted>([^']|'')*)')|(?P<notquoted>[^']*))!
(?P<cells>{0})$""".format(RANGE_EXPR), re.VERBOSE)


def get_column_interval(start, end):
    if isinstance(start, basestring):
        start = column_index_from_string(start)
    if isinstance(end, basestring):
        end = column_index_from_string(end)
    return [get_column_letter(x) for x in range(start, end + 1)]


def coordinate_from_string(coord_string):
    """Convert a coordinate string like 'B12' to a tuple ('B', 12)"""
    match = COORD_RE.match(coord_string.upper())
    if not match:
        msg = 'Invalid cell coordinates (%s)' % coord_string
        raise CellCoordinatesException(msg)
    column, row = match.groups()
    row = int(row)
    if not row:
        msg = "There is no row 0 (%s)" % coord_string
        raise CellCoordinatesException(msg)
    return (column, row)


def absolute_coordinate(coord_string):
    """Convert a coordinate to an absolute coordinate string (B12 -> $B$12)"""
    m = ABSOLUTE_RE.match(coord_string.upper())
    if m:
        parts = m.groups()
        if all(parts[-2:]):
            return '$%s$%s:$%s$%s' % (parts[0], parts[1], parts[3], parts[4])
        else:
            return '$%s$%s' % (parts[0], parts[1])
    else:
        return coord_string

def _get_column_letter(col_idx):
    """Convert a column number into a column letter (3 -> 'C')

    Right shift the column col_idx by 26 to find column letters in reverse
    order.  These numbers are 1-based, and can be converted to ASCII
    ordinals by adding 64.

    """
    # these indicies corrospond to A -> ZZZ and include all allowed
    # columns
    if not 1 <= col_idx <= 18278:
        raise ValueError("Invalid column index {0}".format(col_idx))
    letters = []
    while col_idx > 0:
        col_idx, remainder = divmod(col_idx, 26)
        # check for exact division and borrow if needed
        if remainder == 0:
            remainder = 26
            col_idx -= 1
        letters.append(chr(remainder+64))
    return ''.join(reversed(letters))


_COL_STRING_CACHE = {}
_STRING_COL_CACHE = {}
for i in range(1, 18279):
    col = _get_column_letter(i)
    _STRING_COL_CACHE[i] = col
    _COL_STRING_CACHE[col] = i


def get_column_letter(idx,):
    """Convert a column index into a column letter
    (3 -> 'C')
    """
    try:
        return _STRING_COL_CACHE[idx]
    except KeyError:
        raise ValueError("Invalid column index {0}".format(idx))


def column_index_from_string(str_col):
    """Convert a column name into a numerical index
    ('A' -> 1)
    """
    # we use a function argument to get indexed name lookup
    try:
        return _COL_STRING_CACHE[str_col.upper()]
    except KeyError:
        raise ValueError("{0} is not a valid column name".format(str_col))


def range_boundaries(range_string):
    """
    Convert a range string into a tuple of boundaries:
    (min_col, min_row, max_col, max_row)
    Cell coordinates will be converted into a range with the cell at both end
    """
    m = ABSOLUTE_RE.match(range_string)
    min_col, min_row, sep, max_col, max_row = m.groups()
    min_col = column_index_from_string(min_col)
    min_row = int(min_row)

    if max_col is None or max_row is None:
        max_col = min_col
        max_row = min_row
    else:
        max_col = column_index_from_string(max_col)
        max_row = int(max_row)

    return min_col, min_row, max_col, max_row


def rows_from_range(range_string):
    """
    Get individual addresses for every cell in a range.
    Yields one row at a time.
    """
    min_col, min_row, max_col, max_row = range_boundaries(range_string)
    for row in range(min_row, max_row+1):
        yield tuple('%s%d' % (get_column_letter(col), row)
                    for col in range(min_col, max_col+1))


def cols_from_range(range_string):
    """
    Get individual addresses for every cell in a range.
    Yields one row at a time.
    """
    min_col, min_row, max_col, max_row = range_boundaries(range_string)
    for col in range(min_col, max_col+1):
        yield tuple('%s%d' % (get_column_letter(col), row)
                    for row in range(min_row, max_row+1))


def coordinate_to_tuple(coordinate):
    """
    Convert an Excel style coordinate to (row, colum) tuple
    """
    col, row = coordinate_from_string(coordinate)
    return row, _COL_STRING_CACHE[col]


def range_to_tuple(range_string):
    """
    Convert a worksheet range to the sheetname and maximum and minimum
    coordinate indices
    """
    m = SHEETRANGE_RE.match(range_string)
    if m is None:
        raise ValueError("Value must be of the form sheetname!A1:E4")
    sheetname = m.group("quoted") or m.group("notquoted")
    cells = m.group("cells")
    boundaries = range_boundaries(cells)
    return sheetname, boundaries


def quote_sheetname(sheetname):
    if " " in sheetname:
        sheetname = "'{0}'".format(sheetname)
    return sheetname
