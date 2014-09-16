"""Driver specific portion of the DB API test suite provided by Stuart Bishop
   available at http://stuartbishop.net/Software/DBAPI20TestSuite/"""

import cx_Oracle
import dbapi20
import unittest

import TestEnv

class TestSuite(dbapi20.DatabaseAPI20Test):

    connect_args = (TestEnv.USERNAME, TestEnv.PASSWORD, TestEnv.TNSENTRY)
    driver = cx_Oracle

    # not implemented; use a string instead
    def test_Binary(self):
        pass

    # not implemented; see cx_Oracle specific test suite instead
    def test_callproc(self):
        pass

    # not implemented; Oracle does not support the concept
    def test_nextset(self):
        pass

    # not implemented; see cx_Oracle specific test suite instead
    def test_setinputsizes(self):
        pass

    # not implemented; see cx_Oracle specific test suite instead
    def test_setoutputsize(self):
        pass


if __name__ == "__main__":
    print "Testing cx_Oracle version", cx_Oracle.version
    unittest.main()

