from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl

from openpyxl.descriptors import Typed
from openpyxl.compat import deprecated

from .alignment import Alignment
from .borders import Border, Side
from .colors import Color
from .fills import PatternFill, GradientFill, Fill
from .fonts import Font
from .hashable import HashableObject
from .numbers import NumberFormatDescriptor, is_date_format, is_builtin
from .protection import Protection
from .proxy import StyleProxy


class Style(HashableObject):
    """Style object containing all formatting details."""
    __fields__ = ('font',
                  'fill',
                  'border',
                  'alignment',
                  'number_format',
                  'protection')
    __base__ = True

    font = Typed(expected_type=Font)
    fill = Typed(expected_type=Fill, allow_none=True)
    border = Typed(expected_type=Border)
    alignment = Typed(expected_type=Alignment)
    number_format = NumberFormatDescriptor()
    protection = Typed(expected_type=Protection)

    def __init__(self,
                 font=Font(),
                 fill=PatternFill(),
                 border=Border(),
                 alignment=Alignment(),
                 number_format=None,
                 protection=Protection()
                 ):
        self.font = font
        self.fill = fill
        self.border = border
        self.alignment = alignment
        self.number_format = number_format
        self.protection = protection


    @deprecated("Copy formatting objects like font directly")
    def copy(self):
        cls = self.__class__
        return cls(font=self.font.copy(),
                   fill=self.fill.copy(),
                   border=self.border.copy(),
                   alignment=self.alignment.copy(),
                   number_format=self.number_format,
                   protection=self.protection.copy()
                   )


DEFAULTS = Style()
