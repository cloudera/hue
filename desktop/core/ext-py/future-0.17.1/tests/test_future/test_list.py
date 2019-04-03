# -*- coding: utf-8 -*-
"""
Tests for the backported class:`list` class.
"""

from __future__ import absolute_import, unicode_literals, print_function
from future.builtins import *
from future import utils
from future.tests.base import unittest, expectedFailurePY2


class TestList(unittest.TestCase):
    def test_isinstance_list(self):
        self.assertTrue(isinstance([], list))
        self.assertEqual([1, 2, 3], list([1, 2, 3]))

    def test_isinstance_list_subclass(self):
        """
        Issue #89
        """
        value = list([1, 2, 3])
        class Magic(list):
            pass
        self.assertTrue(isinstance(value, list))
        self.assertFalse(isinstance(value, Magic))

    def test_list_empty(self):
        """
        list() -> []
        """
        self.assertEqual(list(), [])

    def test_list_clear(self):
        l = list()
        l.append(1)
        l.clear()
        self.assertEqual(len(l), 0)
        l.extend([2, 3])
        l.clear()
        self.assertEqual(len(l), 0)

    def test_list_list(self):
        self.assertEqual(list(list()), [])
        self.assertTrue(isinstance(list(list()), list))

    def test_list_list2(self):
        """
        Issue #50
        """
        l = list([1, 2, 3])
        l2 = list(l)
        self.assertEqual(len(l2), 3)
        self.assertEqual(l2, [1, 2, 3])

    def test_list_equal(self):
        l = [1, 3, 5]
        self.assertEqual(list(l), l)

    def test_list_getitem(self):
        l = list('ABCD')
        self.assertEqual(l, ['A', 'B', 'C', 'D'])
        self.assertEqual(l[0], 'A')
        self.assertEqual(l[-1], 'D')
        self.assertEqual(l[0:1], ['A'])
        self.assertEqual(l[0:2], ['A', 'B'])
        self.assertEqual(''.join(l[:]), 'ABCD')

    def test_list_setitem(self):
        l = list('ABCD')
        l[1] = b'B'
        self.assertEqual(l, ['A', b'B', 'C', 'D'])

    def test_list_iteration(self):
        l = list('ABCD')
        for item in l:
            self.assertTrue(isinstance(item, str))

    def test_list_plus_list(self):
        l1 = list('ABCD')
        l2 = ['E', 'F', 'G', 'H']
        self.assertEqual(l1 + l2, ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'])
        self.assertEqual(type(l1 + l2), list)
        self.assertEqual(l2 + l1, ['E', 'F', 'G', 'H', 'A', 'B', 'C', 'D'])
        self.assertEqual(l2 + l1, list('EFGHABCD'))
        self.assertEqual(type(l2 + l1), list)
        self.assertTrue(isinstance(l2 + l1, list))

    def test_list_contains_something(self):
        l = list('ABCD')
        self.assertTrue('A' in l)
        self.assertFalse(['A', 'B'] in l)

    def test_list_index(self):
        l = list('ABCD')
        self.assertEqual(l.index('B'), 1)
        with self.assertRaises(ValueError):
            l.index('')

    def test_copy(self):
        l = list('ABCD')
        l2 = l.copy()
        self.assertEqual(l, l2)
        l2.pop()
        self.assertNotEqual(l, l2)

    # @unittest.skip('Fails on Python <= 2.7.6 due to list subclass slicing bug')
    def test_slice(self):
        """
        Do slices return newlist objects?
        """
        l = list(u'abcd')
        self.assertEqual(l[:2], [u'a', u'b'])
        # Fails due to bug on Py2:
        # self.assertEqual(type(l[:2]), list)
        self.assertEqual(l[-2:], [u'c', u'd'])
        # Fails due to bug on Py2:
        # self.assertEqual(type(l[-2:]), list)

    # @unittest.skip('Fails on Python <= 2.7.6 due to list subclass slicing bug')
    def test_subclassing(self):
        """
        Can newlist be subclassed and do list methods then return instances of
        the same class? (This is the Py3 behaviour).
        """
        class SubClass(list):
            pass
        l = SubClass(u'abcd')
        l2 = SubClass(str(u'abcd'))
        self.assertEqual(type(l), SubClass)
        self.assertTrue(isinstance(l, list))
        # Fails on Py2.7 but passes on Py3.3:
        # self.assertEqual(type(l + l), list)
        self.assertTrue(isinstance(l[0], str))
        self.assertEqual(type(l2[0]), str)
        # This is not true on Py3.3:
        # self.assertEqual(type(l[:2]), SubClass)
        self.assertTrue(isinstance(l[:2], list))

    def test_subclassing_2(self):
        """
        Tests __new__ method in subclasses. Fails in versions <= 0.11.4
        """
        class SubClass(list):
            def __new__(cls, *args, **kwargs):
                self = list.__new__(cls, *args, **kwargs)
                assert type(self) == SubClass
                return self
        l = SubClass(u'abcd')
        self.assertEqual(type(l), SubClass)
        self.assertEqual(l, [u'a', u'b', u'c', u'd'])

    def test_bool(self):
        l = list([])
        l2 = list([1, 3, 5])
        self.assertFalse(bool(l))
        self.assertTrue(bool(l2))
        l2.clear()
        self.assertFalse(bool(l2))

    @expectedFailurePY2
    def test_multiple_inheritance(self):
        """
        Issue #96 (for newdict instead of newobject)
        """
        import collections

        class Base(list):
            pass

        class Foo(Base, collections.Container):
            def __contains__(self, item):
                return False

    @expectedFailurePY2
    def test_with_metaclass_and_list(self):
        """
        Issue #91 (for newdict instead of newobject)
        """
        from future.utils import with_metaclass

        class MetaClass(type):
            pass

        class TestClass(with_metaclass(MetaClass, list)):
            pass


if __name__ == '__main__':
    unittest.main()
