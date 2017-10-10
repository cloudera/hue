"""Unit tests for code in urllib.response."""

from __future__ import absolute_import, division, unicode_literals

from future.backports import urllib
import future.backports.urllib.response as urllib_response
from future.backports.test import support as test_support
from future.tests.base import unittest


class TestFile(object):

    def __init__(self):
        self.closed = False

    def read(self, bytes):
        pass

    def readline(self):
        pass

    def close(self):
        self.closed = True


class Testaddbase(unittest.TestCase):

    # TODO(jhylton): Write tests for other functionality of addbase()

    def setUp(self):
        self.fp = TestFile()
        self.addbase = urllib_response.addbase(self.fp)

    def test_with(self):
        def f():
            with self.addbase as spam:
                pass
        self.assertFalse(self.fp.closed)
        f()
        self.assertTrue(self.fp.closed)
        self.assertRaises(ValueError, f)


if __name__ == '__main__':
    unittest.main()
