from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl

"""Track named groups of cells in a worksheet"""

# Python stdlib imports
import re
import warnings

# package imports
from openpyxl.utils import absolute_coordinate
from openpyxl.compat import unicode
from openpyxl.utils.exceptions import NamedRangeException
from openpyxl.xml.functions import fromstring, safe_iterator
from openpyxl.xml.constants import SHEET_MAIN_NS

# constants
NAMED_RANGE_RE = re.compile("""
^(('(?P<quoted>([^']|'')*)')|(?P<notquoted>[^']*))
!(?P<range>
([$][A-Za-z]+)?([$][0-9]+)?
(:([$][A-Za-z]+[$][0-9]+)?)
?)""", re.VERBOSE)
SPLIT_NAMED_RANGE_RE = re.compile(r"((?:[^,']|'(?:[^']|'')*')+)")
EXTERNAL_RE = re.compile(r"(?P<external>\[\d+\])?(?P<range_string>.*)")
FORMULA_REGEX = re.compile(r"^[a-zA-Z]+[(]+.*[)]$")
DISCARDED_RANGES = re.compile("^_xlnm\.")


class NamedValue(object):
    """A named value"""
    __slots__ = ('name', 'value', 'scope')

    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.scope = None

    @property
    def localSheetId(self):
        return self.scope

    def __repr__(self):
        return u'<{0} "{1}">'.format(self.__class__.__name__, self.value)

    def __iter__(self):
        for attr in ('name', 'localSheetId'):
            value = getattr(self, attr, None)
            if value is not None:
                yield attr, value


#backwards compatibility
NamedRangeContainingValue = NamedValue


class NamedRange(NamedValue):
    """A named group of cells

    Scope is a worksheet object or None for workbook scope names (the default)
    """
    __slots__ = ('name', 'destinations', 'scope')

    str_format = unicode('%s!%s')
    repr_format = unicode('<%s "%s">')

    def __init__(self, name, destinations, scope=None):
        self.name = name
        self.destinations = destinations
        self.scope = scope

    @property
    def value(self):
        dest_cells = []
        for ws, xlrange in self.destinations:
            dest_cells.append("'%s'!%s" % (ws.title.replace("'", "''"),
                                       absolute_coordinate(xlrange)))
        return ",".join(dest_cells)

    def __str__(self):
        return  ','.join([self.str_format % (sheet, name) for sheet, name in self.destinations])

    def __repr__(self):
        return  self.repr_format % (self.__class__.__name__, str(self))


def split_named_range(range_string):
    """Separate a named range into its component parts"""

    for range_string in SPLIT_NAMED_RANGE_RE.split(range_string)[1::2]: # Skip first and from there every second item

        match = NAMED_RANGE_RE.match(range_string)
        if match is None:
            raise NamedRangeException('Invalid named range string: "%s"' % range_string)
        else:
            match = match.groupdict()
            sheet_name = match['quoted'] or match['notquoted']
            xlrange = match['range']
            sheet_name = sheet_name.replace("''", "'") # Unescape '
            yield sheet_name, xlrange


def refers_to_range(range_string):
    if FORMULA_REGEX.match(range_string):
        return
    if range_string:
        return NAMED_RANGE_RE.match(range_string) is not None


def external_range(range_string):
    m = EXTERNAL_RE.match(range_string)
    if m is not None:
        return m.group('external') is not None


def read_named_ranges(xml_source, workbook):
    """Read named ranges, excluding poorly defined ranges."""
    sheetnames = set(sheet.title for sheet in workbook.worksheets)
    root = fromstring(xml_source)
    for name_node in safe_iterator(root, '{%s}definedName' %SHEET_MAIN_NS):

        range_name = name_node.get('name')
        if DISCARDED_RANGES.match(range_name):
            warnings.warn("Discarded range with reserved name")
            continue

        node_text = name_node.text

        if external_range(node_text):
            # treat names referring to external workbooks as values
            named_range = NamedValue(range_name, node_text)

        elif refers_to_range(node_text):
            destinations = split_named_range(node_text)
            # it can happen that a valid named range references
            # a missing worksheet, when Excel didn't properly maintain
            # the named range list
            destinations = [(workbook[sheet], cells) for sheet, cells in destinations
                            if sheet in sheetnames]
            if not destinations:
                continue
            named_range = NamedRange(range_name, destinations)
        else:
            named_range = NamedValue(range_name, node_text)

        named_range.scope = name_node.get("localSheetId")

        yield named_range
