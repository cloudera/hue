# -*- coding: utf-8 -*-

from thriftpy2.parser import load


def test_recursive_definition():
    thrift = load('./recursive_definition.thrift')
    assert thrift.Bar.thrift_spec == {1: (12, 'test', thrift.Foo, False)}
    assert thrift.Foo.thrift_spec == {
        1: (12, 'test', thrift.Bar, False), 2: (15, 'some_int', 8, False)}


def test_const():
    thrift = load('./recursive_definition.thrift')
    assert thrift.SOME_INT == [1, 2, 3]
