# -*- coding: utf-8 -*-
"""
Tests for the backported class:`dict` class.
"""

from __future__ import absolute_import, unicode_literals, print_function
from future.builtins import *
from future import utils
from future.tests.base import unittest, expectedFailurePY2

import os
import sys

class TestDict(unittest.TestCase):
    def setUp(self):
        self.d1 = {'C': 1, 'B': 2, 'A': 3}
        self.d2 = dict(key1='value1', key2='value2')

    def test_dict_empty(self):
        """
        dict() -> {}
        """
        self.assertEqual(dict(), {})

    def test_dict_dict(self):
        """
        Exrapolated from issue #50 -- newlist(newlist([...]))
        """
        d = dict({1: 2, 2: 4, 3: 9})
        d2 = dict(d)
        self.assertEqual(len(d2), 3)
        self.assertEqual(d2, d)
        self.assertTrue(isinstance(d2, dict))
        self.assertTrue(type(d2) == dict)

    def test_dict_eq(self):
        d = self.d1
        self.assertEqual(dict(d), d)

    def test_dict_keys(self):
        """
        The keys, values and items methods should now return iterators on
        Python 2.x (with set-like behaviour on Python 2.7).
        """
        d = self.d1
        self.assertEqual(set(dict(d)), set(d))
        self.assertEqual(set(dict(d).keys()), set(d.keys()))
        with self.assertRaises(TypeError):
            dict(d).keys()[0]

    def test_dict_values(self):
        d = self.d1
        self.assertEqual(set(dict(d).values()), set(d.values()))
        with self.assertRaises(TypeError):
            dict(d).values()[0]

    def test_dict_items(self):
        d = self.d1
        self.assertEqual(set(dict(d).items()), set(d.items()))
        with self.assertRaises(TypeError):
            dict(d).items()[0]

    def test_isinstance_dict(self):
        d = self.d1
        self.assertTrue(isinstance(d, dict))

    def test_isinstance_dict_subclass(self):
        """
        Issue #89
        """
        value = dict()
        class Magic(dict):
            pass
        self.assertTrue(isinstance(value, dict))
        self.assertFalse(isinstance(value, Magic))

    def test_dict_getitem(self):
        d = dict({'C': 1, 'B': 2, 'A': 3})
        self.assertEqual(d['C'], 1)
        self.assertEqual(d['B'], 2)
        self.assertEqual(d['A'], 3)
        with self.assertRaises(KeyError):
            self.assertEqual(d['D'])

    def test_methods_do_not_produce_lists(self):
        for d in (dict(self.d1), self.d2):
            assert not isinstance(d.keys(), list)
            assert not isinstance(d.values(), list)
            assert not isinstance(d.items(), list)

    @unittest.skipIf(sys.version_info[:2] == (2, 6),
             'set-like behaviour of dict methods is only available in Py2.7+')
    def test_set_like_behaviour(self):
        d1, d2 = self.d1, self.d2
        assert d1.keys() & d2.keys() == set()
        assert isinstance(d1.keys() & d2.keys(), set)
        assert isinstance(d1.values() | d2.keys(), set)
        assert isinstance(d1.items() | d2.items(), set)

    @expectedFailurePY2
    def test_braces_create_newdict_object(self):
        """
        It would nice if the {} dict syntax could be coaxed
        into producing our new dict objects somehow ...
        """
        d = self.d1
        self.assertTrue(type(d) == dict)

    @expectedFailurePY2
    def test_multiple_inheritance(self):
        """
        Issue #96 (for newdict instead of newobject)
        """
        import collections

        class Base(dict):
            pass

        class Foo(Base, collections.Container):
            def __contains__(self, item):
                return False

    @expectedFailurePY2
    def test_with_metaclass_and_dict(self):
        """
        Issue #91 (for newdict instead of newobject)
        """
        from future.utils import with_metaclass

        class MetaClass(type):
            pass

        class TestClass(with_metaclass(MetaClass, dict)):
            pass



if __name__ == '__main__':
    unittest.main()
