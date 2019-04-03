from __future__ import absolute_import

from future.builtins.iterators import *
from future.tests.base import unittest


class TestIterators(unittest.TestCase):
    def test_range(self):
        self.assertNotEqual(type(range(10)), list)
        self.assertEqual(sum(range(10)), 45)
        self.assertTrue(9 in range(10))
        self.assertEqual(list(range(5)), [0, 1, 2, 3, 4])
        self.assertEqual(repr(range(10)), 'range(0, 10)')
        self.assertEqual(repr(range(1, 10)), 'range(1, 10)')
        self.assertEqual(repr(range(1, 1)), 'range(1, 1)')
        self.assertEqual(repr(range(-10, 10, 2)), 'range(-10, 10, 2)')

    def test_map(self):
        def square(x):
            return x**2
        self.assertNotEqual(type(map(square, range(10))), list)
        self.assertEqual(sum(map(square, range(10))), 285)
        self.assertEqual(list(map(square, range(3))), [0, 1, 4])

    def test_zip(self):
        a = range(10)
        b = ['a', 'b', 'c']
        self.assertNotEqual(type(zip(a, b)), list)
        self.assertEqual(list(zip(a, b)), [(0, 'a'), (1, 'b'), (2, 'c')])

    def test_filter(self):
        a = range(10)
        def is_odd(x):
            return x % 2 == 1
        self.assertNotEqual(type(filter(is_odd, a)), list)
        self.assertEqual(list(filter(is_odd, a)), [1, 3, 5, 7, 9])

if __name__ == '__main__':
    unittest.main()
