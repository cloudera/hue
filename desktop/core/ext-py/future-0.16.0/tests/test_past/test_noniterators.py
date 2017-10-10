# -*- coding: utf-8 -*-
"""
Tests for the Py2-like list-producing functions
"""

from __future__ import absolute_import, unicode_literals, print_function
import os

from past import utils
from future.tests.base import unittest
from past.builtins import filter, map, range, zip


class TestNonIterators(unittest.TestCase):

    def test_noniterators_produce_lists(self):
        l = range(10)
        self.assertTrue(isinstance(l, list))

        l2 = zip(l, list('ABCDE')*2)
        self.assertTrue(isinstance(l2, list))

        double = lambda x: x*2
        l3 = map(double, l)
        self.assertTrue(isinstance(l3, list))

        is_odd = lambda x: x % 2 == 1
        l4 = filter(is_odd, range(10))
        self.assertEqual(l4, [1, 3, 5, 7, 9])
        self.assertTrue(isinstance(l4, list))


if __name__ == '__main__':
    unittest.main()
