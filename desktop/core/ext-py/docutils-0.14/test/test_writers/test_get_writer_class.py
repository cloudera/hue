#! /usr/bin/env python

# $Id: test_get_writer_class.py 7660 2013-05-07 09:01:00Z milde $
# Author: grubert
# Maintainer: docutils-develop@lists.sourceforge.net
# Copyright: This module has been placed in the public domain.

"""
test get_writer_class
"""

from __init__ import DocutilsTestSupport
from docutils.writers import get_writer_class

class GetWriterClassTestCase(DocutilsTestSupport.StandardTestCase):
    #tests = ( ('manpage', 1), ('nope', 0), ('dummy-writer', 1))

    def test_registered_writer(self):
        wr = get_writer_class('manpage')
        # raises ImportError on failure

    def test_bogus_writer(self):
        self.assertRaises(ImportError,
                          get_writer_class, 'nope')

    def test_local_writer(self):
        # requires local-writer.py in test directory (testroot)
        wr = get_writer_class('local-writer')

if __name__ == '__main__':
    import unittest
    unittest.main()

