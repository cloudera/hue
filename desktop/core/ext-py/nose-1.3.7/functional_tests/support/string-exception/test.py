import unittest
import warnings

warnings.filterwarnings('ignore', category=DeprecationWarning,
                        module='test')


def test_string_exc():
    raise "string exception"


class TestStringExceptionInSetup(unittest.TestCase):
    def setUp(self):
        raise "string exception in setup"

    def testNothing(self):
        pass


class TestStringExceptionInTeardown(unittest.TestCase):
    def tearDown(self):
        raise "string exception in teardown"

    def testNothing(self):
        pass


class TestStringExceptionInClass(unittest.TestCase):
    def testStringExc(self):
        raise "string exception in test"
