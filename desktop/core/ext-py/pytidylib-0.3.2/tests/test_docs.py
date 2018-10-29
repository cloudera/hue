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
from tidylib import Tidy, PersistentTidy, tidy_document

DOC = u'''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN">
<html>
  <head>
    <title></title>
  </head>
  <body>
    %s
  </body>
</html>
'''


class TestDocs1(unittest.TestCase):

    """ Test some sample documents """

    def test_p_element_closed(self):
        h = "<p>hello"
        expected = DOC % '''<p>\n      hello\n    </p>'''
        doc, err = tidy_document(h)
        self.assertEqual(doc, expected)

    def test_alt_added_to_img(self):
        h = "<img src='foo'>"
        expected = DOC % '''<img src='foo' alt="bar">'''
        doc, err = tidy_document(h, {'alt-text': 'bar'})
        self.assertEqual(doc, expected)

    def test_entity_preserved_using_bytes(self):
        h = b"&eacute;"
        expected = (DOC % "&eacute;").encode('utf-8')
        doc, err = tidy_document(h, {'preserve-entities': 1})
        self.assertEqual(doc, expected)

    def test_numeric_entities_using_bytes(self):
        h = b"&eacute;"
        expected = (DOC % "&#233;").encode('utf-8')
        doc, err = tidy_document(h, {'numeric-entities': 1, 'output-encoding': 'ascii'})
        self.assertEqual(doc, expected)

    def test_non_ascii_preserved(self):
        h = u"unicode string ß"
        expected = DOC % h
        doc, err = tidy_document(h)
        self.assertEqual(doc, expected)

    def test_large_document(self):
        h = u"A" * 10000
        expected = DOC % h
        doc, err = tidy_document(h)
        self.assertEqual(doc, expected)

    def test_can_use_two_tidy_instances(self):
        t1 = Tidy()
        t2 = Tidy()
        self.assertEqual(t1.tidy_document(DOC % 'a')[0], DOC % 'a')
        self.assertEqual(t2.tidy_document(DOC % 'b')[0], DOC % 'b')

    def test_tidy_doesnt_persist_options(self):
        tidy = Tidy()
        # This option makes it a fragment
        doc, err = tidy.tidy_document(DOC % 'a', {'show-body-only': 1})
        self.assertEqual(doc, 'a\n')
        doc, err = tidy.tidy_document(DOC % 'a')
        self.assertEqual(doc, DOC % 'a')

    def test_persistent_tidy_does_persist_options(self):
        tidy = PersistentTidy()
        # This option makes it a fragment
        doc, err = tidy.tidy_document(DOC % 'a', {'show-body-only': 1})
        self.assertEqual(doc, 'a\n')
        doc, err = tidy.tidy_document(DOC % 'a')
        self.assertEqual(doc, 'a\n')

    def test_xmlns_large_document_xml_corner_case(self):
        # Test for a super weird edge case in Tidy that can cause it to return
        # the wrong required buffer size.
        body = '<span><span>A</span></span>' + 'A' * 7937
        html = '<html xmlns="http://www.w3.org/1999/xhtml">' + body
        doc, err = tidy_document(html, {'output-xml': 1})
        self.assertEqual(doc.strip()[-7:], "</html>")


if __name__ == '__main__':
    unittest.main()
