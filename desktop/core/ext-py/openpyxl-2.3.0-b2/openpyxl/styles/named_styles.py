from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl


from openpyxl.compat import safe_string

from openpyxl.descriptors import (
    Strict,
    Typed,
    Integer,
    Bool,
)
from .fills import PatternFill, Fill
from . fonts import Font, DEFAULT_FONT
from . borders import Border
from . alignment import Alignment
from . numbers import NumberFormatDescriptor
from . protection import Protection


class NamedStyle(Strict):

    """
    Named and editable styles
    """

    font = Typed(expected_type=Font)
    fill = Typed(expected_type=Fill)
    border = Typed(expected_type=Border)
    alignment = Typed(expected_type=Alignment)
    number_format = NumberFormatDescriptor()
    protection = Typed(expected_type=Protection)
    builtinId = Integer(allow_none=True)
    hidden = Bool(allow_none=True)

    __fields__ = ("name", "font", "fill", "border", "number_format", "alignment", "protection")

    def __init__(self,
                 name="Normal",
                 font=Font(),
                 fill=PatternFill(),
                 border=Border(),
                 alignment=Alignment(),
                 number_format=None,
                 protection=Protection(),
                 builtinId=0,
                 hidden=False,
                 ):
        self.name = name
        self.font = font
        self.fill = fill
        self.border = border
        self.alignment = alignment
        self.number_format = number_format
        self.protection = protection
        self.builtinId = builtinId
        self.hidden = hidden


    def _make_key(self):
        """Use a tuple of fields as the basis for a key"""
        self._key = hash(tuple(getattr(self, x) for x in self.__fields__))

    def __hash__(self):
        if not hasattr(self, '_key'):
            self._make_key()
        return self._key


    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if not hasattr(self, '_key'):
                self._make_key()
            if not hasattr(other, '_key'):
                other._make_key()
            return self._key == other._key


    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        pieces = []
        for k in self.__fields__:
            value = getattr(self, k)
            pieces.append('%s=%s' % (k, repr(value)))
        return '%s(%s)' % (self.__class__.__name__, ', '.join(pieces))


    def __iter__(self):
        for key in ('name', 'builtinId', 'hidden', 'xfId'):
            value = getattr(self, key, None)
            if value is not None:
                yield key, safe_string(value)
