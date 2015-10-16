from __future__ import absolute_import
#copyright openpyxl 2010-2015

"""
Excel specific descriptors
"""

from openpyxl.compat import basestring
from openpyxl.xml.constants import REL_NS
from . import MatchPattern, MinMax, Integer, String, Typed, Sequence
from .serialisable import Serialisable


class HexBinary(MatchPattern):

    pattern = "[0-9a-fA-F]+$"


class UniversalMeasure(MatchPattern):

    pattern = "[0-9]+(\.[0-9]+)?(mm|cm|in|pt|pc|pi)"


class TextPoint(MinMax):
    """
    Size in hundredths of points.
    In theory other units of measurement can be used but these are unbounded
    """
    expected_type = int

    min = -400000
    max = 400000


Coordinate = Integer


class Percentage(MatchPattern):

    pattern = "((100)|([0-9][0-9]?))(\.[0-9][0-9]?)?%"


class Extension(Serialisable):

    uri = String()

    def __init__(self,
                 uri=None,
                ):
        self.uri = uri


class ExtensionList(Serialisable):

    ext = Sequence(expected_type=Extension)

    def __init__(self,
                 ext=None,
                ):
        self.ext = ext


class Relation(String):

    namespace = REL_NS
    allow_none = True
