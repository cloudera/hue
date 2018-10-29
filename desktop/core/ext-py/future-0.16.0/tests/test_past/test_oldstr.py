# -*- coding: utf-8 -*-
"""
Tests for the resurrected Py2-like 8-bit string type.
"""

from __future__ import absolute_import, unicode_literals, print_function

from numbers import Integral
from future.tests.base import unittest
from past.builtins import str as oldstr
from past.types.oldstr import unescape


class TestOldStr(unittest.TestCase):
    def test_repr(self):
        s1 = oldstr(b'abc')
        self.assertEqual(repr(s1), "'abc'")
        s2 = oldstr(b'abc\ndef')
        self.assertEqual(repr(s2), "'abc\\ndef'")

    def test_str(self):
        s1 = oldstr(b'abc')
        self.assertEqual(str(s1), 'abc')
        s2 = oldstr(b'abc\ndef')
        self.assertEqual(str(s2), 'abc\ndef')

    def test_unescape(self):
        self.assertEqual(unescape('abc\\ndef'), 'abc\ndef')
        s = unescape(r'a\\b\c\\d')   # i.e. 'a\\\\b\\c\\\\d'
        self.assertEqual(str(s), r'a\b\c\d')
        s2 = unescape(r'abc\\ndef')   # i.e. 'abc\\\\ndef'
        self.assertEqual(str(s2), r'abc\ndef')

    def test_getitem(self):
        s = oldstr(b'abc')

        self.assertNotEqual(s[0], 97)
        self.assertEqual(s[0], b'a')
        self.assertEqual(s[0], oldstr(b'a'))

        self.assertEqual(s[1:], b'bc')
        self.assertEqual(s[1:], oldstr(b'bc'))


if __name__ == '__main__':
    unittest.main()
