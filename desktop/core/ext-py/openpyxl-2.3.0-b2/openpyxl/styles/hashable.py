from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl


import inspect
from openpyxl.compat import unicode, basestring, safe_string, zip
from openpyxl.descriptors import Descriptor
from openpyxl.descriptors.serialisable import Serialisable


BASE_TYPES = (str, unicode, float, int)


class HashableObject(Serialisable):
    """Define how to hash property classes."""
    __fields__ = ()
    __base__ = False
    _key = None

    @property
    def __defaults__(self):
        spec = inspect.getargspec(self.__class__.__init__)
        return dict(zip(spec.args[1:], spec.defaults))

    def copy(self, **kwargs):
        current = dict([(x, getattr(self, x)) for x in self.__fields__])
        current.update(kwargs)
        return self.__class__(**current)

    def __print__(self, defaults=False):
        if defaults:
            print_func = str
        else:
            print_func = repr
        pieces = []
        default_values = self.__defaults__
        for k in self.__fields__:
            value = getattr(self, k)
            if not defaults and value == default_values[k]:
                continue
            if isinstance(value, basestring):
                print_func = repr  # keep quotes around strings
            pieces.append('%s=%s' % (k, print_func(value)))
        if pieces or self.__base__:
            return '%s(%s)' % (self.__class__.__name__, ', '.join(pieces))
        else:
            return ''

    def __repr__(self):
        return self.__print__(defaults=False)

    def __str__(self):
        return self.__print__(defaults=True)

    @property
    def key(self):
        """Use a tuple of fields as the basis for a key"""
        if self._key is None:
            self._key = hash(tuple(getattr(self, x) for x in self.__fields__))
        return self._key

    def __hash__(self):
        return self.key

    def __eq__(self, other):
        if other.__class__ == self.__class__:
            return self.key == other.key
        return self.key == other

    def __ne__(self, other):
        return not self == other

    def __add__(self, other):
        vals = {}
        for attr in self.__fields__:
            vals[attr] = getattr(self, attr) or getattr(other, attr)
        return self.__class__(**vals)

    def __sub__(self, other):
        vals = {}
        if (self is other) or (self == other):
            return
        for attr in self.__fields__:
            if not getattr(other, attr) and getattr(self, attr):
                vals[attr] = getattr(self, attr)
        return self.__class__(**vals)
