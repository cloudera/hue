from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl


def normalize_reference(cell_range):
    # Normalize range to a str or None
    if not cell_range:
        cell_range = None
    elif isinstance(cell_range, str):
        cell_range = cell_range.upper()
    else:  # Assume a row generator
        cell_range = tuple(cell_range)
        first_cell = cell_range[0][0]
        last_cell = cell_range[-1][-1]
        cell_range = "%s:%s" % (first_cell.coordinate, last_cell.coordinate)
    return cell_range


class FilterColumn(object):
    __slots__ = ("_vals", "_col_id", "_blank")

    def __init__(self, col_id, vals, blank):
        self._vals = list(vals)
        self.col_id = col_id
        self.blank = blank

    @property
    def col_id(self):
        return self._col_id

    @col_id.setter
    def col_id(self, value):
        self._col_id = int(value)

    @property
    def vals(self):
        return self._vals

    @property
    def blank(self):
        return self._blank

    @blank.setter
    def blank(self, value):
        self._blank = bool(int(value)) if value else False


class SortCondition(object):
    __slots__ = ("_ref", "_descending")

    def __init__(self, ref, descending):
        self.ref = ref
        self.descending = descending

    @property
    def ref(self):
        """Return the ref for this sheet."""
        return self._ref

    @ref.setter
    def ref(self, value):
        self._ref = normalize_reference(value)

    @property
    def descending(self):
        return self._descending

    @descending.setter
    def descending(self, value):
        self._descending = bool(int(value)) if value else False


class AutoFilter(object):
    """Represents a auto filter.

    Don't create auto filters by yourself. It is created by :class:`~openpyxl.worksheet.Worksheet`.
    You can use via :attr:`~~openpyxl.worksheet.Worksheet.auto_filter` attribute.
    """
    __slots__ = ("_ref", "_filter_columns", "_sort_conditions")

    def __init__(self):
        self._ref = None
        self._filter_columns = {}
        self._sort_conditions = []

    @property
    def ref(self):
        """Return the reference of this auto filter."""
        return self._ref

    @ref.setter
    def ref(self, value):
        self._ref = normalize_reference(value)

    @property
    def filter_columns(self):
        """Return filters for columns."""
        return self._filter_columns

    def add_filter_column(self, col_id, vals, blank=False):
        """
        Add row filter for specified column.

        :param col_id: Zero-origin column id. 0 means first column.
        :type  col_id: int
        :param vals: Value list to show.
        :type  vals: str[]
        :param blank: Show rows that have blank cell if True (default=``False``)
        :type  blank: bool
        """
        filter_column = FilterColumn(col_id, vals, blank)
        self._filter_columns[filter_column.col_id] = filter_column
        return filter_column

    @property
    def sort_conditions(self):
        """Return sort conditions"""
        return self._sort_conditions

    def add_sort_condition(self, ref, descending=False):
        """
        Add sort condition for cpecified range of cells.

        :param ref: range of the cells (e.g. 'A2:A150')
        :type  ref: string
        :param descending: Descending sort order (default=``False``)
        :type  descending: bool
        """
        sort_condition = SortCondition(ref, descending)
        self._sort_conditions.append(sort_condition)
        return sort_condition


