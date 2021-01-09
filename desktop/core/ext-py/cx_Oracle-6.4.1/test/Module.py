#------------------------------------------------------------------------------
# Copyright 2018, Oracle and/or its affiliates. All rights reserved.
#------------------------------------------------------------------------------

"""Module for testing module methods."""

import datetime
import time

class TestModule(BaseTestCase):

    def testDateFromTicks(self):
        "test DateFromTicks()"
        today = datetime.datetime.today()
        timestamp = time.mktime(today.timetuple())
        date = cx_Oracle.DateFromTicks(timestamp)
        self.assertEqual(date, today.date())

    def testFutureObj(self):
        "test management of __future__ object"
        self.assertEqual(cx_Oracle.__future__.ctx_mgr_close, False)
        cx_Oracle.__future__.ctx_mgr_close = True
        self.assertEqual(cx_Oracle.__future__.ctx_mgr_close, True)
        self.assertEqual(cx_Oracle.__future__.dummy, None)
        cx_Oracle.__future__.dummy = "Unimportant"
        self.assertEqual(cx_Oracle.__future__.dummy, None)

    def testTimestampFromTicks(self):
        "test TimestampFromTicks()"
        timestamp = time.mktime(datetime.datetime.today().timetuple())
        today = datetime.datetime.fromtimestamp(timestamp)
        date = cx_Oracle.TimestampFromTicks(timestamp)
        self.assertEqual(date, today)

    def testUnsupportedFunctions(self):
        "test unsupported time functions"
        self.assertRaises(cx_Oracle.NotSupportedError, cx_Oracle.Time,
                12, 0, 0)
        self.assertRaises(cx_Oracle.NotSupportedError, cx_Oracle.TimeFromTicks,
                100)

