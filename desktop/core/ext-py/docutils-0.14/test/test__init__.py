#! /usr/bin/env python
# .. coding: utf-8
# $Id: test__init__.py 8126 2017-06-23 09:34:28Z milde $
# Author: Günter Milde <milde@users.sourceforge.net>
# Copyright: This module has been placed in the public domain.

"""
Test module for the docutils' __init__.py.
"""

import unittest
import sys
import DocutilsTestSupport              # must be imported before docutils
import docutils

class ApplicationErrorTests(unittest.TestCase):

    def test_message(self):
        err = docutils.ApplicationError('the message')
        self.assertEqual(unicode(err), u'the message')

    def test_non_ASCII_message(self):
        err = docutils.ApplicationError(u'\u0169')
        self.assertEqual(unicode(err), u'\u0169')

class VersionInfoTests(unittest.TestCase):

    def test_version_info(self):
        self.assertEqual(len(docutils.__version_info__), 6)
        # self.assertEqual(type(docutils.__version_info__.major), int)
        # self.assertEqual(type(docutils.__version_info__.minor), int)
        # self.assertEqual(type(docutils.__version_info__.micro), int)
        # self.assertEqual(type(docutils.__version_info__.releaselevel), str)
        # self.assertEqual(type(docutils.__version_info__.serial), int)
        # self.assertEqual(type(docutils.__version_info__.release), bool)

if __name__ == '__main__':
    unittest.main()
