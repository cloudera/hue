# -*- coding: utf-8 -*-
# Copyright 2009-2014 Jason Stitt
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import unicode_literals

import unittest
from tidylib import tidy_fragment


class TestFrags1(unittest.TestCase):
    """ Test some sample fragment documents """

    def test_p_element_closed(self):
        h = "<p>hello"
        expected = '''<p>\n  hello\n</p>'''
        doc, err = tidy_fragment(h)
        self.assertEqual(doc, expected)

    def test_alt_added_to_img(self):
        h = "<img src='foo'>"
        expected = '''<img src='foo' alt="bar">'''
        doc, err = tidy_fragment(h, {'alt-text': 'bar'})
        self.assertEqual(doc, expected)

    def test_entity_preserved_using_bytes(self):
        h = b"&eacute;"
        expected = b"&eacute;"
        doc, err = tidy_fragment(h, {'preserve-entities': 1})
        self.assertEqual(doc, expected)

    def test_numeric_entities_using_bytes(self):
        h = b"&eacute;"
        expected = b"&#233;"
        doc, err = tidy_fragment(h, {'numeric-entities': 1, 'output-encoding': 'ascii'})
        self.assertEqual(doc, expected)

    def test_non_ascii_preserved(self):
        h = u"unicode string ß"
        expected = h
        doc, err = tidy_fragment(h)
        self.assertEqual(doc, expected)

if __name__ == '__main__':
    unittest.main()
