# -*- coding: utf-8 -*-

import thriftpy2

from thriftpy2.utils import serialize, deserialize

thriftpy2.install_import_hook()

import container_thrift as container  # noqa


def test_list_item():
    l_item = container.ListItem()
    l_item.list_string = ['foo', 'bar']
    l_item.list_list_string = [['foo', 'bar']]

    b = serialize(l_item)
    l_item2 = deserialize(container.ListItem(), b)
    assert l_item == l_item2

    l_item3 = container.ListItem()
    assert l_item != l_item3


def test_map_item():
    m_item = container.MapItem()
    m_item.map_string = {'foo': 'bar'}
    m_item.map_map_string = {'foo': {'hello': 'world'}}

    b = serialize(m_item)
    m_item2 = deserialize(container.MapItem(), b)
    assert m_item == m_item2


def test_mix_item():
    x_item = container.MixItem()
    x_item.list_map = [{'foo': 'bar'}]
    x_item.map_list = {'foo': ['hello', 'world']}

    b = serialize(x_item)
    x_item2 = deserialize(container.MixItem(), b)
    assert x_item == x_item2


def test_list_struct():
    l_item = container.ListItem()
    l_item.list_string = ['foo', 'bar'] * 100
    l_item.list_list_string = [['foo', 'bar']] * 100

    l_struct = container.ListStruct()
    l_struct.list_items = [l_item] * 100

    b = serialize(l_struct)
    l_struct2 = deserialize(container.ListStruct(), b)
    assert l_struct == l_struct2
