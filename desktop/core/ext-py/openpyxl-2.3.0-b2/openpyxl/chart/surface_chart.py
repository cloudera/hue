from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl

from openpyxl.descriptors.serialisable import Serialisable
from openpyxl.descriptors import (
    Typed,
    Integer,
    Bool,
    Alias,
    Sequence,
)
from openpyxl.descriptors.excel import ExtensionList
from openpyxl.descriptors.nested import (
    NestedInteger,
    NestedBool,
)

from ._chart import ChartBase
from .axis import TextAxis, NumericAxis, SeriesAxis
from .shapes import ShapeProperties
from .series import Series


class BandFormat(Serialisable):

    tagname = "bandFmt"

    idx = NestedInteger()
    spPr = Typed(expected_type=ShapeProperties, allow_none=True)

    __elements__ = ('idx', 'spPr')

    def __init__(self,
                 idx=0,
                 spPr=None,
                ):
        self.idx = idx
        self.spPr = spPr


class BandFormats(Serialisable):

    tagname = "bandFmts"

    bandFmt = Sequence(expected_type=BandFormat, allow_none=True)

    __elements__ = ('bandFmt',)

    def __init__(self,
                 bandFmt=(),
                ):
        self.bandFmt = bandFmt


class _SurfaceChartBase(ChartBase):

    wireframe = NestedBool(allow_none=True)
    ser = Sequence(expected_type=Series, allow_none=True)
    bandFmts = Typed(expected_type=BandFormats, allow_none=True)

    _series_type = "surface"

    __elements__ = ('wireframe', 'ser', 'bandFmts')

    def __init__(self,
                 wireframe=None,
                 ser=(),
                 bandFmts=None,
                ):
        self.wireframe = wireframe
        self.ser = ser
        self.bandFmts = bandFmts
        super(_SurfaceChartBase, self).__init__()


class SurfaceChart(_SurfaceChartBase):

    tagname = "surfaceChart"

    wireframe = _SurfaceChartBase.wireframe
    ser = _SurfaceChartBase.ser
    bandFmts = _SurfaceChartBase.bandFmts

    extLst = Typed(expected_type=ExtensionList, allow_none=True)

    x_axis = Typed(expected_type=TextAxis)
    y_axis = Typed(expected_type=NumericAxis)
    z_axis = Typed(expected_type=SeriesAxis, allow_none=True)

    __elements__ = _SurfaceChartBase.__elements__ + ('axId',)

    def __init__(self, axId=None, extLst=None, **kw ):
        self.x_axis = TextAxis()
        self.y_axis = NumericAxis()
        self.z_axis = None
        super(SurfaceChart, self).__init__(**kw)


class SurfaceChart3D(_SurfaceChartBase):

    tagname = "surface3DChart"

    wireframe = _SurfaceChartBase.wireframe
    ser = _SurfaceChartBase.ser
    bandFmts = _SurfaceChartBase.bandFmts

    extLst = SurfaceChart.extLst

    x_axis = Typed(expected_type=TextAxis)
    y_axis = Typed(expected_type=NumericAxis)
    z_axis = Typed(expected_type=SeriesAxis)

    __elements__ = _SurfaceChartBase.__elements__ + ('axId',)

    def __init__(self, axId=None, **kw):
        self.x_axis = TextAxis()
        self.y_axis = NumericAxis()
        self.z_axis = SeriesAxis()
        super(SurfaceChart3D, self).__init__(**kw)
