#! /usr/bin/env python

# $Id: test_get_reader_class.py 7504 2012-08-27 07:55:20Z grubert $
# Author: grubert abadger1999
# Maintainer: docutils-develop@lists.sourceforge.net
# Copyright: This module has been placed in the public domain.

"""
test get_reader_class
"""

from __init__ import DocutilsTestSupport
from docutils.readers import get_reader_class

class GetReaderClassTestCase(DocutilsTestSupport.StandardTestCase):

    def test_registered_reader(self):
        rdr = get_reader_class('pep')
        # raises ImportError on failure

    def test_bogus_reader(self):
        self.assertRaises(ImportError,
                          get_reader_class, 'nope')

    def test_local_reader(self):
        # requires local-reader.py in test directory (testroot)
        wr = get_reader_class('local-reader')

if __name__ == '__main__':
    import unittest
    unittest.main()

