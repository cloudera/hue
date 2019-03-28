#------------------------------------------------------------------------------
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# Portions Copyright 2007-2015, Anthony Tuininga. All rights reserved.
#
# Portions Copyright 2001-2007, Computronix (Canada) Ltd., Edmonton, Alberta,
# Canada. All rights reserved.
#------------------------------------------------------------------------------

"""Driver specific portion of the DB API test suite provided by Stuart Bishop
   available at http://stuartbishop.net/Software/DBAPI20TestSuite/"""

from __future__ import print_function

import cx_Oracle
import dbapi20
import unittest

import TestEnv

class TestSuite(dbapi20.DatabaseAPI20Test):

    connect_args = (TestEnv.GetMainUser(), TestEnv.GetMainPassword(),
            TestEnv.GetConnectString())
    driver = cx_Oracle

    # not implemented; see cx_Oracle specific test suite instead
    def test_callproc(self):
        pass

    # not implemented; see cx_Oracle specific test suite instead
    def test_fetchmany(self):
        pass

    # not implemented; Oracle does not support the concept
    def test_nextset(self):
        pass

    # not implemented; see cx_Oracle specific test suite instead
    def test_rowcount(self):
        pass

    # not implemented; see cx_Oracle specific test suite instead
    def test_setinputsizes(self):
        pass

    # not implemented; not used by cx_Oracle
    def test_setoutputsize(self):
        pass

    # not implemented; Oracle does not support the concept
    def test_Time(self):
        pass

if __name__ == "__main__":
    print("Testing cx_Oracle version", cx_Oracle.__version__)
    TestEnv.RunTestCases()

