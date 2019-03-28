#------------------------------------------------------------------------------
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# Portions Copyright 2007-2015, Anthony Tuininga. All rights reserved.
#
# Portions Copyright 2001-2007, Computronix (Canada) Ltd., Edmonton, Alberta,
# Canada. All rights reserved.
#------------------------------------------------------------------------------

"""Module for testing date/time variables."""

import TestEnv

import cx_Oracle
import datetime
import time

class TestCase(TestEnv.BaseTestCase):

    def setUp(self):
        TestEnv.BaseTestCase.setUp(self)
        self.rawData = []
        self.dataByKey = {}
        for i in range(1, 11):
            timeTuple = (2002, 12, 9, 0, 0, 0, 0, 0, -1)
            timeInTicks = time.mktime(timeTuple) + i * 86400 + i * 8640
            dateCol = cx_Oracle.TimestampFromTicks(int(timeInTicks))
            if i % 2:
                timeInTicks = time.mktime(timeTuple) + i * 86400 * 2 + \
                        i * 12960
                nullableCol = cx_Oracle.TimestampFromTicks(int(timeInTicks))
            else:
                nullableCol = None
            tuple = (i, dateCol, nullableCol)
            self.rawData.append(tuple)
            self.dataByKey[i] = tuple

    def testBindDate(self):
        "test binding in a date"
        self.cursor.execute("""
                select * from TestDates
                where DateCol = :value""",
                value = cx_Oracle.Timestamp(2002, 12, 13, 9, 36, 0))
        self.assertEqual(self.cursor.fetchall(), [self.dataByKey[4]])

    def testBindDateTime(self):
        "test binding in a Python 2.3 and higher date time"
        self.cursor.execute("""
                select * from TestDates
                where DateCol = :value""",
                value = datetime.datetime(2002, 12, 13, 9, 36, 0))
        self.assertEqual(self.cursor.fetchall(), [self.dataByKey[4]])

    def testBindDateInDateTimeVar(self):
        "test binding date in a datetime variable"
        var = self.cursor.var(cx_Oracle.DATETIME)
        dateVal = datetime.date.today()
        var.setvalue(0, dateVal)
        self.assertEqual(var.getvalue().date(), dateVal)

    def testBindDateAfterString(self):
        "test binding in a date after setting input sizes to a string"
        self.cursor.setinputsizes(value = 15)
        self.cursor.execute("""
                select * from TestDates
                where DateCol = :value""",
                value = cx_Oracle.Timestamp(2002, 12, 14, 12, 0, 0))
        self.assertEqual(self.cursor.fetchall(), [self.dataByKey[5]])

    def testBindNull(self):
        "test binding in a null"
        self.cursor.setinputsizes(value = cx_Oracle.DATETIME)
        self.cursor.execute("""
                select * from TestDates
                where DateCol = :value""",
                value = None)
        self.assertEqual(self.cursor.fetchall(), [])

    def testBindDateArrayDirect(self):
        "test binding in a date array"
        returnValue = self.cursor.var(cx_Oracle.NUMBER)
        array = [r[1] for r in self.rawData]
        statement = """
                begin
                  :returnValue := pkg_TestDateArrays.TestInArrays(
                      :startValue, :baseDate, :array);
                end;"""
        self.cursor.execute(statement,
                returnValue = returnValue,
                startValue = 5,
                baseDate = cx_Oracle.Date(2002, 12, 12),
                array = array)
        self.assertEqual(returnValue.getvalue(), 35.5)
        array = array + array[:5]
        self.cursor.execute(statement,
                startValue = 7,
                baseDate = cx_Oracle.Date(2002, 12, 13),
                array = array)
        self.assertEqual(returnValue.getvalue(), 24.0)

    def testBindDateArrayBySizes(self):
        "test binding in a date array (with setinputsizes)"
        returnValue = self.cursor.var(cx_Oracle.NUMBER)
        self.cursor.setinputsizes(array = [cx_Oracle.DATETIME, 10])
        array = [r[1] for r in self.rawData]
        self.cursor.execute("""
                begin
                  :returnValue := pkg_TestDateArrays.TestInArrays(
                      :startValue, :baseDate, :array);
                end;""",
                returnValue = returnValue,
                startValue = 6,
                baseDate = cx_Oracle.Date(2002, 12, 13),
                array = array)
        self.assertEqual(returnValue.getvalue(), 26.5)

    def testBindDateArrayByVar(self):
        "test binding in a date array (with arrayvar)"
        returnValue = self.cursor.var(cx_Oracle.NUMBER)
        array = self.cursor.arrayvar(cx_Oracle.DATETIME, 10, 20)
        array.setvalue(0, [r[1] for r in self.rawData])
        self.cursor.execute("""
                begin
                  :returnValue := pkg_TestDateArrays.TestInArrays(
                      :startValue, :baseDate, :array);
                end;""",
                returnValue = returnValue,
                startValue = 7,
                baseDate = cx_Oracle.Date(2002, 12, 14),
                array = array)
        self.assertEqual(returnValue.getvalue(), 17.5)

    def testBindInOutDateArrayByVar(self):
        "test binding in/out a date array (with arrayvar)"
        array = self.cursor.arrayvar(cx_Oracle.DATETIME, 10, 100)
        originalData = [r[1] for r in self.rawData]
        array.setvalue(0, originalData)
        self.cursor.execute("""
                begin
                  pkg_TestDateArrays.TestInOutArrays(:numElems, :array);
                end;""",
                numElems = 5,
                array = array)
        self.assertEqual(array.getvalue(),
                [ cx_Oracle.Timestamp(2002, 12, 17, 2, 24, 0),
                  cx_Oracle.Timestamp(2002, 12, 18, 4, 48, 0),
                  cx_Oracle.Timestamp(2002, 12, 19, 7, 12, 0),
                  cx_Oracle.Timestamp(2002, 12, 20, 9, 36, 0),
                  cx_Oracle.Timestamp(2002, 12, 21, 12, 0, 0) ] + \
                originalData[5:])

    def testBindOutDateArrayByVar(self):
        "test binding out a date array (with arrayvar)"
        array = self.cursor.arrayvar(cx_Oracle.DATETIME, 6, 100)
        self.cursor.execute("""
                begin
                  pkg_TestDateArrays.TestOutArrays(:numElems, :array);
                end;""",
                numElems = 6,
                array = array)
        self.assertEqual(array.getvalue(),
                [ cx_Oracle.Timestamp(2002, 12, 13, 4, 48, 0),
                  cx_Oracle.Timestamp(2002, 12, 14, 9, 36, 0),
                  cx_Oracle.Timestamp(2002, 12, 15, 14, 24, 0),
                  cx_Oracle.Timestamp(2002, 12, 16, 19, 12, 0),
                  cx_Oracle.Timestamp(2002, 12, 18, 0, 0, 0),
                  cx_Oracle.Timestamp(2002, 12, 19, 4, 48, 0) ])

    def testBindOutSetInputSizes(self):
        "test binding out with set input sizes defined"
        vars = self.cursor.setinputsizes(value = cx_Oracle.DATETIME)
        self.cursor.execute("""
                begin
                  :value := to_date(20021209, 'YYYYMMDD');
                end;""")
        self.assertEqual(vars["value"].getvalue(),
               cx_Oracle.Timestamp(2002, 12, 9))

    def testBindInOutSetInputSizes(self):
        "test binding in/out with set input sizes defined"
        vars = self.cursor.setinputsizes(value = cx_Oracle.DATETIME)
        self.cursor.execute("""
                begin
                  :value := :value + 5.25;
                end;""",
                value = cx_Oracle.Timestamp(2002, 12, 12, 10, 0, 0))
        self.assertEqual(vars["value"].getvalue(),
                cx_Oracle.Timestamp(2002, 12, 17, 16, 0, 0))

    def testBindOutVar(self):
        "test binding out with cursor.var() method"
        var = self.cursor.var(cx_Oracle.DATETIME)
        self.cursor.execute("""
                begin
                  :value := to_date('20021231 12:31:00',
                      'YYYYMMDD HH24:MI:SS');
                end;""",
                value = var)
        self.assertEqual(var.getvalue(),
               cx_Oracle.Timestamp(2002, 12, 31, 12, 31, 0))

    def testBindInOutVarDirectSet(self):
        "test binding in/out with cursor.var() method"
        var = self.cursor.var(cx_Oracle.DATETIME)
        var.setvalue(0, cx_Oracle.Timestamp(2002, 12, 9, 6, 0, 0))
        self.cursor.execute("""
                begin
                  :value := :value + 5.25;
                end;""",
                value = var)
        self.assertEqual(var.getvalue(),
                cx_Oracle.Timestamp(2002, 12, 14, 12, 0, 0))

    def testCursorDescription(self):
        "test cursor description is accurate"
        self.cursor.execute("select * from TestDates")
        self.assertEqual(self.cursor.description,
                [ ('INTCOL', cx_Oracle.NUMBER, 10, None, 9, 0, 0),
                  ('DATECOL', cx_Oracle.DATETIME, 23, None, None, None, 0),
                  ('NULLABLECOL', cx_Oracle.DATETIME, 23, None, None, None,
                        1) ])

    def testFetchAll(self):
        "test that fetching all of the data returns the correct results"
        self.cursor.execute("select * From TestDates order by IntCol")
        self.assertEqual(self.cursor.fetchall(), self.rawData)
        self.assertEqual(self.cursor.fetchall(), [])

    def testFetchMany(self):
        "test that fetching data in chunks returns the correct results"
        self.cursor.execute("select * From TestDates order by IntCol")
        self.assertEqual(self.cursor.fetchmany(3), self.rawData[0:3])
        self.assertEqual(self.cursor.fetchmany(2), self.rawData[3:5])
        self.assertEqual(self.cursor.fetchmany(4), self.rawData[5:9])
        self.assertEqual(self.cursor.fetchmany(3), self.rawData[9:])
        self.assertEqual(self.cursor.fetchmany(3), [])

    def testFetchOne(self):
        "test that fetching a single row returns the correct results"
        self.cursor.execute("""
                select *
                from TestDates
                where IntCol in (3, 4)
                order by IntCol""")
        self.assertEqual(self.cursor.fetchone(), self.dataByKey[3])
        self.assertEqual(self.cursor.fetchone(), self.dataByKey[4])
        self.assertEqual(self.cursor.fetchone(), None)

if __name__ == "__main__":
    TestEnv.RunTestCases()

