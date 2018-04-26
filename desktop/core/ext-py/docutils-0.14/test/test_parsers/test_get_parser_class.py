#! /usr/bin/env python

# $Id: test_get_parser_class.py 7504 2012-08-27 07:55:20Z grubert $
# Author: grubert abadger1999
# Maintainer: docutils-develop@lists.sourceforge.net
# Copyright: This module has been placed in the public domain.

"""
test get_parser_class
"""

from __init__ import DocutilsTestSupport
from docutils.parsers import get_parser_class

class GetParserClassTestCase(DocutilsTestSupport.StandardTestCase):

    def test_registered_parser(self):
        rdr = get_parser_class('rst')
        # raises ImportError on failure

    def test_bogus_parser(self):
        self.assertRaises(ImportError,
                          get_parser_class, 'nope')

    def test_local_parser(self):
        # requires local-parser.py in test directory (testroot)
        wr = get_parser_class('local-parser')

if __name__ == '__main__':
    import unittest
    unittest.main()

