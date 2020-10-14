# -*- coding: utf-8 -*-

from thriftpy2 import load
from thriftpy2.thrift import TType


def test_set():
    s = load("type.thrift")

    assert s.Set.thrift_spec == {1: (TType.SET, "a_set", TType.STRING, True)}
