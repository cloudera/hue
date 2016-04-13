from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl

from array import array
from warnings import warn

from openpyxl.compat import safe_string
from openpyxl.xml.functions import Element

from openpyxl.utils.indexed_list import IndexedList
from .numbers import BUILTIN_FORMATS, BUILTIN_FORMATS_REVERSE
from .proxy import StyleProxy
from . import Style


class StyleDescriptor(object):

    def __init__(self, collection, key):
        self.collection = collection
        self.key = key

    def __set__(self, instance, value):
        coll = getattr(instance.parent.parent, self.collection)
        if not getattr(instance, "_style"):
            instance._style = StyleArray()
        setattr(instance._style, self.key, coll.add(value))


    def __get__(self, instance, cls):
        coll = getattr(instance.parent.parent, self.collection)
        if not getattr(instance, "_style"):
            instance._style = StyleArray()
        idx =  getattr(instance._style, self.key)
        return StyleProxy(coll[idx])


class NumberFormatDescriptor(object):

    key = "numFmtId"
    collection = '_number_formats'

    def __set__(self, instance, value):
        coll = getattr(instance.parent.parent, self.collection)
        if value in BUILTIN_FORMATS_REVERSE:
            idx = BUILTIN_FORMATS_REVERSE[value]
        else:
            idx = coll.add(value) + 164
        if not getattr(instance, "_style"):
            instance._style = StyleArray()
        setattr(instance._style, self.key, idx)


    def __get__(self, instance, cls):
        if not getattr(instance, "_style"):
            instance._style = StyleArray()
        idx = getattr(instance._style, self.key)
        if idx < 164:
            return BUILTIN_FORMATS.get(idx, "General")
        coll = getattr(instance.parent.parent, self.collection)
        return coll[idx - 164]


class ArrayDescriptor(object):

    def __init__(self, key):
        self.key = key

    def __get__(self, instance, cls):
        return instance[self.key]

    def __set__(self, instance, value):
        instance[self.key] = value


class StyleArray(array):
    """
    Simplified named tuple with an array
    """

    __slots__ = ()
    tagname = 'xf'

    fontId = ArrayDescriptor(0)
    fillId = ArrayDescriptor(1)
    borderId = ArrayDescriptor(2)
    numFmtId = ArrayDescriptor(3)
    protectionId = ArrayDescriptor(4)
    alignmentId = ArrayDescriptor(5)
    pivotButton = ArrayDescriptor(6)
    quotePrefix = ArrayDescriptor(7)
    xfId = ArrayDescriptor(8)

    __attrs__ = ("fontId", "fillId", "borderId", "numFmtId", "protectionId",
                 "alignmentId", "pivotButton", "quotePrefix", "xfId")

    def __new__(cls, args=[0]*9):
        return array.__new__(cls, 'i', args)


    def __hash__(self):
        return hash(tuple(self))


    @classmethod
    def from_tree(cls, node):
        self = cls()
        for k, v in node.attrib.items():
            if k in cls.__attrs__:
                setattr(self, k, int(v))
        return self


    @property
    def applyAlignment(self):
        return self.alignmentId != 0


    @property
    def applyProtection(self):
        return self.protectionId != 0


    def to_tree(self):
        """
        Alignment and protection objects are implemented as child elements.
        This is a completely different API to other format objects. :-/
        """
        attrs = {}
        for key in self.__attrs__ + ('applyProtection', 'applyAlignment'):
            value = getattr(self, key)
            if key in ('alignmentId', 'protectionId'):
                continue
            elif key in ('quotePrefix', 'pivotButton', 'applyProtection', 'applyAlignment') and not value:
                continue
            attrs[key] = value
        attrs = dict((k, safe_string(v)) for k,v in attrs.items())
        return Element(self.tagname, attrs)


class StyleableObject(object):
    """
    Base class for styleble objects implementing proxy and lookup functions
    """

    font = StyleDescriptor('_fonts', "fontId")
    fill = StyleDescriptor('_fills', "fillId")
    border = StyleDescriptor('_borders', "borderId")
    number_format = NumberFormatDescriptor()
    protection = StyleDescriptor('_protections', "protectionId")
    alignment = StyleDescriptor('_alignments', "alignmentId")

    __slots__ = ('parent', '_style')

    def __init__(self, sheet, style_array=None):
        self.parent = sheet
        if style_array is not None:
            style_array = StyleArray(style_array)
        self._style = style_array


    @property
    def style_id(self):
        if self._style is None:
            self._style = StyleArray()
        return self.parent.parent._cell_styles.add(self._style)

    @property
    def has_style(self):
        if self._style is None:
            return False
        return any(self._style)

    #legacy
    @property
    def style(self):
        warn("Use formatting objects such as font directly")
        return Style(
            font=self.font.copy(),
            fill=self.fill.copy(),
            border=self.border.copy(),
            alignment=self.alignment.copy(),
            number_format=self.number_format,
            protection=self.protection.copy()
        )

    #legacy
    @style.setter
    def style(self, value):
        warn("Use formatting objects such as font directly")
        self.font = value.font.copy()
        self.fill = value.fill.copy()
        self.border = value.border.copy()
        self.protection = value.protection.copy()
        self.alignment = value.alignment.copy()
        self.number_format = value.number_format

    @property
    def pivotButton(self):
        if self._style is None:
            return False
        return bool(self._style[6])


    @property
    def quotePrefix(self):
        if self._style is None:
            return False
        return bool(self._style[7])
