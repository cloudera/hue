# -*- coding: utf-8 -*-
# Copyright 2009 Jason Stitt
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

import unittest
from tidylib import tidy_document

DOC = '''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
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
    
    def test_doc_with_unclosed_tag(self):
        h = "<p>hello"
        expected = DOC % '''<p>
      hello
    </p>'''
        doc, err = tidy_document(h)
        self.assertEqual(doc, expected)
        
    def test_doc_with_incomplete_img_tag(self):
        h = "<img src='foo'>"
        expected = DOC % '''<img src='foo' alt="" />'''
        doc, err = tidy_document(h)
        self.assertEqual(doc, expected)
        
    def test_doc_with_entity(self):
        h = "&eacute;"
        expected = DOC % "&eacute;"
        doc, err = tidy_document(h)
        self.assertEqual(doc, expected)
        
        expected = DOC % "&#233;"
        doc, err = tidy_document(h, {'numeric-entities':1})
        self.assertEqual(doc, expected)
    
    def test_doc_with_unicode(self):
        h = u"unicode string ß"
        expected = unicode(DOC, 'utf-8') % h
        doc, err = tidy_document(h)
        self.assertEqual(doc, expected)
        
    def test_doc_with_unicode_subclass(self):
        class MyUnicode(unicode):
            pass
        
        h = MyUnicode(u"unicode string ß")
        expected = unicode(DOC, 'utf-8') % h
        doc, err = tidy_document(h)
        self.assertEqual(doc, expected)
        
    
if __name__ == '__main__':
    unittest.main()