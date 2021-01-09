#------------------------------------------------------------------------------
# Copyright 2016, 2017, Oracle and/or its affiliates. All rights reserved.
#
# Portions Copyright 2007-2015, Anthony Tuininga. All rights reserved.
#
# Portions Copyright 2001-2007, Computronix (Canada) Ltd., Edmonton, Alberta,
# Canada. All rights reserved.
#------------------------------------------------------------------------------

"""Module for testing interval variables."""

import datetime

class TestIntervalVar(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)
        self.rawData = []
        self.dataByKey = {}
        for i in range(1, 11):
            delta = datetime.timedelta(days = i, hours = i, minutes = i * 2,
                    seconds = i * 3)
            if i % 2 == 0:
                nullableDelta = None
            else:
                nullableDelta = datetime.timedelta(days = i + 5, hours = i + 2,
                        minutes = i * 2 + 5, seconds = i * 3 + 5)
            tuple = (i, delta, nullableDelta)
            self.rawData.append(tuple)
            self.dataByKey[i] = tuple

    def testBindInterval(self):
        "test binding in an interval"
        self.cursor.setinputsizes(value = cx_Oracle.INTERVAL)
        self.cursor.execute("""
                select * from TestIntervals
                where IntervalCol = :value""",
                value = datetime.timedelta(days = 5, hours = 5, minutes = 10,
                        seconds = 15))
        self.assertEqual(self.cursor.fetchall(), [self.dataByKey[5]])

    def testBindNull(self):
        "test binding in a null"
        self.cursor.setinputsizes(value = cx_Oracle.INTERVAL)
        self.cursor.execute("""
                select * from TestIntervals
                where IntervalCol = :value""",
                value = None)
        self.assertEqual(self.cursor.fetchall(), [])

    def testBindOutSetInputSizes(self):
        "test binding out with set input sizes defined"
        vars = self.cursor.setinputsizes(value = cx_Oracle.INTERVAL)
        self.cursor.execute("""
                begin
                  :value := to_dsinterval('8 09:24:18.123789');
                end;""")
        self.assertEqual(vars["value"].getvalue(),
                datetime.timedelta(days = 8, hours = 9, minutes = 24,
                        seconds = 18, microseconds = 123789))

    def testBindInOutSetInputSizes(self):
        "test binding in/out with set input sizes defined"
        vars = self.cursor.setinputsizes(value = cx_Oracle.INTERVAL)
        self.cursor.execute("""
                begin
                  :value := :value + to_dsinterval('5 08:30:00');
                end;""",
                value = datetime.timedelta(days = 5, hours = 2, minutes = 15))
        self.assertEqual(vars["value"].getvalue(),
                datetime.timedelta(days = 10, hours = 10, minutes = 45))

    def testBindInOutFractionalSecond(self):
        "test binding in/out with set input sizes defined"
        vars = self.cursor.setinputsizes(value = cx_Oracle.INTERVAL)
        self.cursor.execute("""
                begin
                  :value := :value + to_dsinterval('5 08:30:00');
                end;""",
                value = datetime.timedelta(days = 5, seconds=12.123789))
        self.assertEqual(vars["value"].getvalue(),
                datetime.timedelta(days = 10, hours = 8, minutes = 30,
                                   seconds=12, microseconds=123789))

    def testBindOutVar(self):
        "test binding out with cursor.var() method"
        var = self.cursor.var(cx_Oracle.INTERVAL)
        self.cursor.execute("""
                begin
                  :value := to_dsinterval('15 18:35:45.586');
                end;""",
                value = var)
        self.assertEqual(var.getvalue(),
                datetime.timedelta(days = 15, hours = 18, minutes = 35,
                        seconds = 45, milliseconds = 586))

    def testBindInOutVarDirectSet(self):
        "test binding in/out with cursor.var() method"
        var = self.cursor.var(cx_Oracle.INTERVAL)
        var.setvalue(0, datetime.timedelta(days = 1, minutes = 50))
        self.cursor.execute("""
                begin
                  :value := :value + to_dsinterval('8 05:15:00');
                end;""",
                value = var)
        self.assertEqual(var.getvalue(),
                datetime.timedelta(days = 9, hours = 6, minutes = 5))

    def testCursorDescription(self):
        "test cursor description is accurate"
        self.cursor.execute("select * from TestIntervals")
        self.assertEqual(self.cursor.description,
                [ ('INTCOL', cx_Oracle.NUMBER, 10, None, 9, 0, 0),
                  ('INTERVALCOL', cx_Oracle.INTERVAL, None, None, 2, 6, 0),
                  ('NULLABLECOL', cx_Oracle.INTERVAL, None, None, 2, 6, 1) ])

    def testFetchAll(self):
        "test that fetching all of the data returns the correct results"
        self.cursor.execute("select * From TestIntervals order by IntCol")
        self.assertEqual(self.cursor.fetchall(), self.rawData)
        self.assertEqual(self.cursor.fetchall(), [])

    def testFetchMany(self):
        "test that fetching data in chunks returns the correct results"
        self.cursor.execute("select * From TestIntervals order by IntCol")
        self.assertEqual(self.cursor.fetchmany(3), self.rawData[0:3])
        self.assertEqual(self.cursor.fetchmany(2), self.rawData[3:5])
        self.assertEqual(self.cursor.fetchmany(4), self.rawData[5:9])
        self.assertEqual(self.cursor.fetchmany(3), self.rawData[9:])
        self.assertEqual(self.cursor.fetchmany(3), [])

    def testFetchOne(self):
        "test that fetching a single row returns the correct results"
        self.cursor.execute("""
                select *
                from TestIntervals
                where IntCol in (3, 4)
                order by IntCol""")
        self.assertEqual(self.cursor.fetchone(), self.dataByKey[3])
        self.assertEqual(self.cursor.fetchone(), self.dataByKey[4])
        self.assertEqual(self.cursor.fetchone(), None)

