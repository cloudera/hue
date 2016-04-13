from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl


from openpyxl.descriptors import Alias

from openpyxl.descriptors.nested import (
    NestedValue,
    NestedBool,
    NestedNoneSet,
    NestedMinMax,
    NestedString,
    NestedInteger,
    NestedFloat,
)
from .hashable import HashableObject
from .colors import ColorDescriptor, BLACK

from openpyxl.compat import safe_string
from openpyxl.xml.functions import Element, SubElement


def _no_value(tagname, value, namespace=None):
    if value:
        return Element(tagname, val=safe_string(value))


class Font(HashableObject):
    """Font options used in styles."""

    UNDERLINE_DOUBLE = 'double'
    UNDERLINE_DOUBLE_ACCOUNTING = 'doubleAccounting'
    UNDERLINE_SINGLE = 'single'
    UNDERLINE_SINGLE_ACCOUNTING = 'singleAccounting'

    name = NestedString()
    charset = NestedInteger(allow_none=True)
    family = NestedMinMax(min=0, max=14)
    sz = NestedFloat()
    size = Alias("sz")
    b = NestedBool(to_tree=_no_value)
    bold = Alias("b")
    i = NestedBool(to_tree=_no_value)
    italic = Alias("i")
    strike = NestedBool(to_tree=_no_value)
    strikethrough = Alias("strike")
    outline = NestedBool(to_tree=_no_value)
    shadow = NestedBool(to_tree=_no_value)
    condense = NestedBool(to_tree=_no_value)
    extend = NestedBool(to_tree=_no_value)
    u = NestedNoneSet(values=('single', 'double', 'singleAccounting',
                             'doubleAccounting'))
    underline = Alias("u")
    vertAlign = NestedNoneSet(values=('superscript', 'subscript', 'baseline'))
    color = ColorDescriptor()
    scheme = NestedNoneSet(values=("major", "minor"))

    tagname = "font"

    __elements__ = ('name', 'charset', 'family', 'b', 'i', 'strike', 'outline',
                  'shadow', 'condense', 'color', 'extend', 'sz', 'u', 'vertAlign',
                  'scheme')

    __fields__ = __elements__


    def __init__(self, name='Calibri', sz=11, b=False, i=False, charset=None,
                 u=None, strike=False, color=BLACK, scheme=None, family=2, size=None,
                 bold=None, italic=None, strikethrough=None, underline=None,
                 vertAlign=None, outline=False, shadow=False, condense=False,
                 extend=False):
        self.name = name
        self.family = family
        if size is not None:
            sz = size
        self.sz = sz
        if bold is not None:
            b = bold
        self.b = b
        if italic is not None:
            i = italic
        self.i = i
        if underline is not None:
            u = underline
        self.u = u
        if strikethrough is not None:
            strike = strikethrough
        self.strike = strike
        self.color = color
        self.vertAlign = vertAlign
        self.charset = charset
        self.outline = outline
        self.shadow = shadow
        self.condense = condense
        self.extend = extend
        self.scheme = scheme


from . colors import Color

DEFAULT_FONT = Font(color=Color(theme=1), scheme="minor")
