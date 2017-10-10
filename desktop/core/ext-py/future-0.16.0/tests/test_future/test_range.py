# -*- coding: utf-8 -*-
"""
Tests for the backported class:`range` class.
"""

from future.builtins import range
from future.tests.base import unittest

from collections import Iterator, Sequence
from operator import attrgetter


class RangeTests(unittest.TestCase):
    def test_range(self):
        self.assertTrue(isinstance(range(0), Sequence))
        self.assertTrue(isinstance(reversed(range(0)), Iterator))

    def test_bool_range(self):
        self.assertFalse(range(0))
        self.assertTrue(range(1))
        self.assertFalse(range(1, 1))
        self.assertFalse(range(5, 2))

    def test_equality_range(self):
        self.assertEqual(range(7), range(7))
        self.assertEqual(range(0), range(1, 1))
        self.assertEqual(range(0, 10, 3), range(0, 11, 3))

    # Use strict equality of attributes when slicing to catch subtle differences
    def assertRangesEqual(self, r1, r2):
        by_attrs = attrgetter('start', 'stop', 'step')
        self.assertEqual(by_attrs(r1), by_attrs(r2))

    def test_slice_empty_range(self):
        self.assertRangesEqual(range(0)[:], range(0))
        self.assertRangesEqual(range(0)[::-1], range(-1, -1, -1))

    def test_slice_overflow_range(self):
        r = range(8)
        self.assertRangesEqual(r[2:200], range(2, 8))
        self.assertRangesEqual(r[-200:-2], range(0, 6))

    def test_slice_range(self):
        r = range(-8, 8)
        self.assertRangesEqual(r[:], range(-8, 8))
        self.assertRangesEqual(r[:2], range(-8, -6))
        self.assertRangesEqual(r[:-2], range(-8, 6))
        self.assertRangesEqual(r[2:], range(-6, 8))
        self.assertRangesEqual(r[-2:], range(6, 8))
        self.assertRangesEqual(r[2:-2], range(-6, 6))

    def test_rev_slice_range(self):
        r = range(-8, 8)
        self.assertRangesEqual(r[::-1], range(7, -9, -1))
        self.assertRangesEqual(r[:2:-1], range(7, -6, -1))
        self.assertRangesEqual(r[:-2:-1], range(7, 6, -1))
        self.assertRangesEqual(r[2::-1], range(-6, -9, -1))
        self.assertRangesEqual(r[-2::-1], range(6, -9, -1))
        self.assertRangesEqual(r[-2:2:-1], range(6, -6, -1))

    def test_slice_rev_range(self):
        r = range(8, -8, -1)
        self.assertRangesEqual(r[:], range(8, -8, -1))
        self.assertRangesEqual(r[:2], range(8, 6, -1))
        self.assertRangesEqual(r[:-2], range(8, -6, -1))
        self.assertRangesEqual(r[2:], range(6, -8, -1))
        self.assertRangesEqual(r[-2:], range(-6, -8, -1))
        self.assertRangesEqual(r[2:-2], range(6, -6, -1))

    def test_rev_slice_rev_range(self):
        r = range(8, -8, -1)
        self.assertRangesEqual(r[::-1], range(-7, 9))
        self.assertRangesEqual(r[:2:-1], range(-7, 6))
        self.assertRangesEqual(r[:-2:-1], range(-7, -6))
        self.assertRangesEqual(r[2::-1], range(6, 9))
        self.assertRangesEqual(r[-2::-1], range(-6, 9))
        self.assertRangesEqual(r[-2:2:-1], range(-6, 6))

    def test_stepped_slice_range(self):
        r = range(-8, 8)
        self.assertRangesEqual(r[::2], range(-8, 8, 2))
        self.assertRangesEqual(r[:2:2], range(-8, -6, 2))
        self.assertRangesEqual(r[:-2:2], range(-8, 6, 2))
        self.assertRangesEqual(r[2::2], range(-6, 8, 2))
        self.assertRangesEqual(r[-2::2], range(6, 8, 2))
        self.assertRangesEqual(r[2:-2:2], range(-6, 6, 2))

    def test_rev_stepped_slice_range(self):
        r = range(-8, 8)
        self.assertRangesEqual(r[::-2], range(7, -9, -2))
        self.assertRangesEqual(r[:2:-2], range(7, -6, -2))
        self.assertRangesEqual(r[:-2:-2], range(7, 6, -2))
        self.assertRangesEqual(r[2::-2], range(-6, -9, -2))
        self.assertRangesEqual(r[-2::-2], range(6, -9, -2))
        self.assertRangesEqual(r[-2:2:-2], range(6, -6, -2))

    def test_stepped_slice_rev_range(self):
        r = range(8, -8, -1)
        self.assertRangesEqual(r[::2], range(8, -8, -2))
        self.assertRangesEqual(r[:2:2], range(8, 6, -2))
        self.assertRangesEqual(r[:-2:2], range(8, -6, -2))
        self.assertRangesEqual(r[2::2], range(6, -8, -2))
        self.assertRangesEqual(r[-2::2], range(-6, -8, -2))
        self.assertRangesEqual(r[2:-2:2], range(6, -6, -2))

    def test_rev_stepped_slice_rev_range(self):
        r = range(8, -8, -1)
        self.assertRangesEqual(r[::-2], range(-7, 9, 2))
        self.assertRangesEqual(r[:2:-2], range(-7, 6, 2))
        self.assertRangesEqual(r[:-2:-2], range(-7, -6, 2))
        self.assertRangesEqual(r[2::-2], range(6, 9, 2))
        self.assertRangesEqual(r[-2::-2], range(-6, 9, 2))
        self.assertRangesEqual(r[-2:2:-2], range(-6, 6, 2))

    def test_slice_stepped_range(self):
        r = range(-8, 8, 2)
        self.assertRangesEqual(r[:], range(-8, 8, 2))
        self.assertRangesEqual(r[:2], range(-8, -4, 2))
        self.assertRangesEqual(r[:-2], range(-8, 4, 2))
        self.assertRangesEqual(r[2:], range(-4, 8, 2))
        self.assertRangesEqual(r[-2:], range(4, 8, 2))
        self.assertRangesEqual(r[2:-2], range(-4, 4, 2))

    def test_rev_slice_stepped_range(self):
        r = range(-8, 8, 2)
        self.assertRangesEqual(r[::-1], range(6, -10, -2))
        self.assertRangesEqual(r[:2:-1], range(6, -4, -2))
        self.assertRangesEqual(r[:-2:-1], range(6, 4, -2))
        self.assertRangesEqual(r[2::-1], range(-4, -10, -2))
        self.assertRangesEqual(r[-2::-1], range(4, -10, -2))
        self.assertRangesEqual(r[-2:2:-1], range(4, -4, -2))

    def test_slice_rev_stepped_range(self):
        r = range(8, -8, -2)
        self.assertRangesEqual(r[:], range(8, -8, -2))
        self.assertRangesEqual(r[:2], range(8, 4, -2))
        self.assertRangesEqual(r[:-2], range(8, -4, -2))
        self.assertRangesEqual(r[2:], range(4, -8, -2))
        self.assertRangesEqual(r[-2:], range(-4, -8, -2))
        self.assertRangesEqual(r[2:-2], range(4, -4, -2))

    def test_rev_slice_rev_stepped_range(self):
        r = range(8, -8, -2)
        self.assertRangesEqual(r[::-1], range(-6, 10, 2))
        self.assertRangesEqual(r[:2:-1], range(-6, 4, 2))
        self.assertRangesEqual(r[:-2:-1], range(-6, -4, 2))
        self.assertRangesEqual(r[2::-1], range(4, 10, 2))
        self.assertRangesEqual(r[-2::-1], range(-4, 10, 2))
        self.assertRangesEqual(r[-2:2:-1], range(-4, 4, 2))

    def test_stepped_slice_stepped_range(self):
        r = range(-8, 8, 2)
        self.assertRangesEqual(r[::2], range(-8, 8, 4))
        self.assertRangesEqual(r[:2:2], range(-8, -4, 4))
        self.assertRangesEqual(r[:-2:2], range(-8, 4, 4))
        self.assertRangesEqual(r[2::2], range(-4, 8, 4))
        self.assertRangesEqual(r[-2::2], range(4, 8, 4))
        self.assertRangesEqual(r[2:-2:2], range(-4, 4, 4))

    def test_rev_stepped_slice_stepped_range(self):
        r = range(-8, 8, 2)
        self.assertRangesEqual(r[::-2], range(6, -10, -4))
        self.assertRangesEqual(r[:2:-2], range(6, -4, -4))
        self.assertRangesEqual(r[:-2:-2], range(6, 4, -4))
        self.assertRangesEqual(r[2::-2], range(-4, -10, -4))
        self.assertRangesEqual(r[-2::-2], range(4, -10, -4))
        self.assertRangesEqual(r[-2:2:-2], range(4, -4, -4))

    def test_stepped_slice_rev_stepped_range(self):
        r = range(8, -8, -2)
        self.assertRangesEqual(r[::2], range(8, -8, -4))
        self.assertRangesEqual(r[:2:2], range(8, 4, -4))
        self.assertRangesEqual(r[:-2:2], range(8, -4, -4))
        self.assertRangesEqual(r[2::2], range(4, -8, -4))
        self.assertRangesEqual(r[-2::2], range(-4, -8, -4))
        self.assertRangesEqual(r[2:-2:2], range(4, -4, -4))

    def test_rev_stepped_slice_rev_stepped_range(self):
        r = range(8, -8, -2)
        self.assertRangesEqual(r[::-2], range(-6, 10, 4))
        self.assertRangesEqual(r[:2:-2], range(-6, 4, 4))
        self.assertRangesEqual(r[:-2:-2], range(-6, -4, 4))
        self.assertRangesEqual(r[2::-2], range(4, 10, 4))
        self.assertRangesEqual(r[-2::-2], range(-4, 10, 4))
        self.assertRangesEqual(r[-2:2:-2], range(-4, 4, 4))

    def test_slice_zero_step(self):
        msg = '^slice step cannot be zero$'
        with self.assertRaisesRegexp(ValueError, msg):
            range(8)[::0]

    def test_properties(self):
        # Exception string differs between PY2/3
        r = range(0)
        with self.assertRaises(AttributeError):
            r.start = 0
        with self.assertRaises(AttributeError):
            r.stop = 0
        with self.assertRaises(AttributeError):
            r.step = 0


if __name__ == '__main__':
    unittest.main()
