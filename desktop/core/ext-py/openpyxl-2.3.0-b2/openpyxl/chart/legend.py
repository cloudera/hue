from openpyxl.descriptors.serialisable import Serialisable
from openpyxl.descriptors import (
    Typed,
    Integer,
    Alias,
)
from openpyxl.descriptors.excel import ExtensionList
from openpyxl.descriptors.nested import (
    NestedBool,
    NestedSet,
    NestedInteger
)

from .layout import Layout
from .shapes import ShapeProperties
from .text import RichText


class LegendEntry(Serialisable):

    tagname = "legendEntry"

    idx = NestedInteger()
    delete = NestedBool()
    txPr = Typed(expected_type=RichText, allow_none=True)
    extLst = Typed(expected_type=ExtensionList, allow_none=True)

    __elements__ = ('idx',)

    def __init__(self,
                 idx=0,
                 delete=False,
                 txPr=None,
                 extLst=None,
                ):
        self.idx = idx
        self.delete = delete
        self.txPr = txPr


class Legend(Serialisable):

    tagname = "legend"

    legendPos = NestedSet(values=(['b', 'tr', 'l', 'r', 't']))
    legendEntry = Typed(expected_type=LegendEntry, allow_none=True)
    layout = Typed(expected_type=Layout, allow_none=True)
    overlay = NestedBool(allow_none=True)
    spPr = Typed(expected_type=ShapeProperties, allow_none=True)
    shapeProperties = Alias('spPr')
    txPr = Typed(expected_type=RichText, allow_none=True)
    textProperies = Alias('txPr')
    extLst = Typed(expected_type=ExtensionList, allow_none=True)

    __elements__ = ('legendPos', 'legendEntry', 'layout', 'overlay', 'spPr', 'txPr',)

    def __init__(self,
                 legendPos="r",
                 legendEntry=None,
                 layout=None,
                 overlay=None,
                 spPr=None,
                 txPr=None,
                 extLst=None,
                ):
        self.legendPos = legendPos
        self.legendEntry = legendEntry
        self.layout = layout
        self.overlay = overlay
        self.spPr = spPr
        self.txPr = txPr
