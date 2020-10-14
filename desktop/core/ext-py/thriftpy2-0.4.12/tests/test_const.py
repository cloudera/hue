# -*- coding: utf-8 -*-

import thriftpy2
thriftpy2.install_import_hook()

import const_thrift as const    # noqa


def test_num_const():
    assert -10 == const.NEGATIVE_I16
    assert -123.456 == const.NEGATIVE_DOUBLE

    assert 10 == const.I16_CONST
    assert 100000 == const.I32_CONST
    assert 123.456 == const.DOUBLE_CONST


def test_string_const():
    assert "hello" == const.DOUBLE_QUOTED_CONST
    assert "hello" == const.SINGLE_QUOTED_CONST


def test_const_with_sep():
    assert "hello" == const.CONST_WITH_SEP1
    assert "hello" == const.CONST_WITH_SEP2


def test_list_const():
    assert [1, 2, 3] == const.I32_LIST_CONST
    assert [1.1, 2.2, 3.3] == const.DOUBLE_LIST_CONST
    assert ["hello", "world"] == const.STRING_LIST_CONST

    assert [[1, 2, 3], [4, 5, 6]] == const.I32_LIST_LIST_CONST
    assert [[1.1, 2.2, 3.3], [4.4, 5.5, 6.6]] == const.DOUBLE_LIST_LIST_CONST
    assert [["hello", "world"], ["foo", "bar"]] == const.STRING_LIST_LIST_CONST
