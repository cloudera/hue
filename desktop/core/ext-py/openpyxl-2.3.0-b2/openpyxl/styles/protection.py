from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl

from openpyxl.descriptors import Bool

from .hashable import HashableObject


class Protection(HashableObject):
    """Protection options for use in styles."""

    tagname = "protection"

    __fields__ = ('locked',
                  'hidden')
    locked = Bool()
    hidden = Bool()

    def __init__(self, locked=True, hidden=False):
        self.locked = locked
        self.hidden = hidden
