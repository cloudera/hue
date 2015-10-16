from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl

try:
    from itertools import izip as zip
except ImportError:
    zip = zip

try:
    range = xrange
except NameError:
    range = range

def iteritems(iterable):
    if hasattr(iterable, 'iteritems'):
        for item in iterable.iteritems():
            yield item
    else:
        for item in iterable.items():
            yield item

def iterkeys(iterable):
    if hasattr(iterable, 'iterkeys'):
        for item in iterable.iterkeys():
            yield item
    else:
        for item in iterable.keys():
            yield item


def itervalues(iterable):
    if hasattr(iterable, 'itervalues'):
        for item in iterable.itervalues():
            yield item
    else:
        for item in iterable.values():
            yield item
