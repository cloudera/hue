# -*- coding: utf-8 -*-
# (c) 2007 Ian Bicking and Philip Jenvey; written for Paste (http://pythonpaste.org)
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
import cgi
from StringIO import StringIO
from paste.fixture import TestApp
from paste.wsgiwrappers import WSGIRequest
from paste.util.multidict import MultiDict, UnicodeMultiDict
from py.test import raises

def test_dict():
    d = MultiDict({'a': 1})
    assert d.items() == [('a', 1)]

    d['b'] = 2
    d['c'] = 3
    assert d.items() == [('a', 1), ('b', 2), ('c', 3)]

    d['b'] = 4
    assert d.items() == [('a', 1), ('c', 3), ('b', 4)]

    d.add('b', 5)
    raises(KeyError, 'd.getone("b")')
    assert d.getall('b') == [4, 5]
    assert d.items() == [('a', 1), ('c', 3), ('b', 4), ('b', 5)]

    del d['b']
    assert d.items() == [('a', 1), ('c', 3)]
    assert d.pop('xxx', 5) == 5
    assert d.getone('a') == 1
    assert d.popitem() == ('c', 3)
    assert d.items() == [('a', 1)]

    item = []
    assert d.setdefault('z', item) is item
    assert d.items() == [('a', 1), ('z', item)]

    assert d.setdefault('y', 6) == 6

    assert d.mixed() == {'a': 1, 'y': 6, 'z': item}
    assert d.dict_of_lists() == {'a': [1], 'y': [6], 'z': [item]}

    assert 'a' in d
    dcopy = d.copy()
    assert dcopy is not d
    assert dcopy == d
    d['x'] = 'x test'
    assert dcopy != d

    d[(1, None)] = (None, 1)
    assert d.items() == [('a', 1), ('z', []), ('y', 6), ('x', 'x test'),
                         ((1, None), (None, 1))]

def test_unicode_dict():
    _test_unicode_dict()
    _test_unicode_dict(decode_param_names=True)

def _test_unicode_dict(decode_param_names=False):
    d = UnicodeMultiDict(MultiDict({'a': 'a test'}))
    d.encoding = 'utf-8'
    d.errors = 'ignore'

    if decode_param_names:
        key_str = unicode
        d.decode_keys = True
    else:
        key_str = str

    def assert_unicode(obj):
        assert isinstance(obj, unicode)

    def assert_key_str(obj):
        assert isinstance(obj, key_str)

    def assert_unicode_item(obj):
        key, value = obj
        assert isinstance(key, key_str)
        assert isinstance(value, unicode)

    assert d.items() == [('a', u'a test')]
    map(assert_key_str, d.keys())
    map(assert_unicode, d.values())

    d['b'] = '2 test'
    d['c'] = '3 test'
    assert d.items() == [('a', u'a test'), ('b', u'2 test'), ('c', u'3 test')]
    map(assert_unicode_item, d.items())

    d['b'] = '4 test'
    assert d.items() == [('a', u'a test'), ('c', u'3 test'), ('b', u'4 test')]
    map(assert_unicode_item, d.items())

    d.add('b', '5 test')
    raises(KeyError, 'd.getone("b")')
    assert d.getall('b') == [u'4 test', u'5 test']
    map(assert_unicode, d.getall('b'))
    assert d.items() == [('a', u'a test'), ('c', u'3 test'), ('b', u'4 test'),
                         ('b', u'5 test')]
    map(assert_unicode_item, d.items())

    del d['b']
    assert d.items() == [('a', u'a test'), ('c', u'3 test')]
    map(assert_unicode_item, d.items())
    assert d.pop('xxx', u'5 test') == u'5 test'
    assert isinstance(d.pop('xxx', u'5 test'), unicode)
    assert d.getone('a') == u'a test'
    assert isinstance(d.getone('a'), unicode)
    assert d.popitem() == ('c', u'3 test')
    d['c'] = '3 test'
    assert_unicode_item(d.popitem())
    assert d.items() == [('a', u'a test')]
    map(assert_unicode_item, d.items())

    item = []
    assert d.setdefault('z', item) is item
    items = d.items()
    assert items == [('a', u'a test'), ('z', item)]
    assert isinstance(items[1][0], key_str)
    assert isinstance(items[1][1], list)

    assert isinstance(d.setdefault('y', 'y test'), unicode)
    assert isinstance(d['y'], unicode)

    assert d.mixed() == {u'a': u'a test', u'y': u'y test', u'z': item}
    assert d.dict_of_lists() == {u'a': [u'a test'], u'y': [u'y test'],
                                 u'z': [item]}
    del d['z']
    map(assert_unicode_item, d.mixed().iteritems())
    map(assert_unicode_item, [(k, v[0]) for \
                                   k, v in d.dict_of_lists().iteritems()])

    assert u'a' in d
    dcopy = d.copy()
    assert dcopy is not d
    assert dcopy == d
    d['x'] = 'x test'
    assert dcopy != d

    d[(1, None)] = (None, 1)
    assert d.items() == [('a', u'a test'), ('y', u'y test'), ('x', u'x test'),
                         ((1, None), (None, 1))]
    item = d.items()[-1]
    assert isinstance(item[0], tuple)
    assert isinstance(item[1], tuple)

    fs = cgi.FieldStorage()
    fs.name = 'thefile'
    fs.filename = 'hello.txt'
    fs.file = StringIO('hello')
    d['f'] = fs
    ufs = d['f']
    assert isinstance(ufs, cgi.FieldStorage)
    assert ufs is not fs
    assert ufs.name == fs.name
    assert isinstance(ufs.name, key_str)
    assert ufs.filename == fs.filename
    assert isinstance(ufs.filename, unicode)
    assert isinstance(ufs.value, str)
    assert ufs.value == 'hello'
