import os
import sys
import unittest
from nose.config import Config
from nose.plugins import doctests
from mock import Bucket

class TestDoctestErrorHandling(unittest.TestCase):

    def setUp(self):
        self._path = sys.path[:]
        here = os.path.dirname(__file__)
        testdir = os.path.join(here, 'support', 'doctest')
        sys.path.insert(0, testdir)
        p = doctests.Doctest()
        p.can_configure = True
        p.configure(Bucket(), Config())
        self.p = p

    def tearDown(self):
        sys.path = self._path[:]

    def test_no_name(self):
        p = self.p
        mod = __import__('noname_wrapper')
        loaded = [ t for t in p.loadTestsFromModule(mod) ]
        assert len(loaded) == 1, 'Need 1 test suite from noname_wrapper'
        found_tests = list(loaded[0])
        assert len(found_tests) == 1, 'Need 1 test from noname_wrapper suite'
        assert found_tests[0].id() == 'noname_wrapper.func'


if __name__ == '__main__':
    unittest.main()
