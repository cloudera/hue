"""Module for testing date/time variables."""

import datetime
import time

class TestDateTimeVar(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)
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
        self.cursor.execute(u"""
                select * from TestDates
                where DateCol = :p_Value""",
                p_Value = cx_Oracle.Timestamp(2002, 12, 13, 9, 36, 0))
        self.failUnlessEqual(self.cursor.fetchall(), [self.dataByKey[4]])

    def testBindDateTime(self):
        "test binding in a Python 2.3 and higher date time"
        self.cursor.execute(u"""
                select * from TestDates
                where DateCol = :value""",
                value = datetime.datetime(2002, 12, 13, 9, 36, 0))
        self.failUnlessEqual(self.cursor.fetchall(), [self.dataByKey[4]])

    def testBindDateAfterString(self):
        "test binding in a date after setting input sizes to a string"
        self.cursor.setinputsizes(p_Value = 15)
        self.cursor.execute(u"""
                select * from TestDates
                where DateCol = :p_Value""",
                p_Value = cx_Oracle.Timestamp(2002, 12, 14, 12, 0, 0))
        self.failUnlessEqual(self.cursor.fetchall(), [self.dataByKey[5]])

    def testBindNull(self):
        "test binding in a null"
        self.cursor.setinputsizes(p_Value = cx_Oracle.DATETIME)
        self.cursor.execute(u"""
                select * from TestDates
                where DateCol = :p_Value""",
                p_Value = None)
        self.failUnlessEqual(self.cursor.fetchall(), [])

    def testBindDateArrayDirect(self):
        "test binding in a date array"
        returnValue = self.cursor.var(cx_Oracle.NUMBER)
        array = [r[1] for r in self.rawData]
        statement = u"""
                begin
                  :p_ReturnValue := pkg_TestDateArrays.TestInArrays(
                      :p_StartValue, :p_BaseDate, :p_Array);
                end;"""
        self.cursor.execute(statement,
                p_ReturnValue = returnValue,
                p_StartValue = 5,
                p_BaseDate = cx_Oracle.Date(2002, 12, 12),
                p_Array = array)
        self.failUnlessEqual(returnValue.getvalue(), 35.5)
        array = array + array[:5]
        self.cursor.execute(statement,
                p_StartValue = 7,
                p_BaseDate = cx_Oracle.Date(2002, 12, 13),
                p_Array = array)
        self.failUnlessEqual(returnValue.getvalue(), 24.0)

    def testBindDateArrayBySizes(self):
        "test binding in a date array (with setinputsizes)"
        returnValue = self.cursor.var(cx_Oracle.NUMBER)
        self.cursor.setinputsizes(p_Array = [cx_Oracle.DATETIME, 10])
        array = [r[1] for r in self.rawData]
        self.cursor.execute(u"""
                begin
                  :p_ReturnValue := pkg_TestDateArrays.TestInArrays(
                      :p_StartValue, :p_BaseDate, :p_Array);
                end;""",
                p_ReturnValue = returnValue,
                p_StartValue = 6,
                p_BaseDate = cx_Oracle.Date(2002, 12, 13),
                p_Array = array)
        self.failUnlessEqual(returnValue.getvalue(), 26.5)

    def testBindDateArrayByVar(self):
        "test binding in a date array (with arrayvar)"
        returnValue = self.cursor.var(cx_Oracle.NUMBER)
        array = self.cursor.arrayvar(cx_Oracle.DATETIME, 10, 20)
        array.setvalue(0, [r[1] for r in self.rawData])
        self.cursor.execute(u"""
                begin
                  :p_ReturnValue := pkg_TestDateArrays.TestInArrays(
                      :p_StartValue, :p_BaseDate, :p_Array);
                end;""",
                p_ReturnValue = returnValue,
                p_StartValue = 7,
                p_BaseDate = cx_Oracle.Date(2002, 12, 14),
                p_Array = array)
        self.failUnlessEqual(returnValue.getvalue(), 17.5)

    def testBindInOutDateArrayByVar(self):
        "test binding in/out a date array (with arrayvar)"
        array = self.cursor.arrayvar(cx_Oracle.DATETIME, 10, 100)
        originalData = [r[1] for r in self.rawData]
        array.setvalue(0, originalData)
        self.cursor.execute(u"""
                begin
                  pkg_TestDateArrays.TestInOutArrays(:p_NumElems, :p_Array);
                end;""",
                p_NumElems = 5,
                p_Array = array)
        self.failUnlessEqual(array.getvalue(),
                [ cx_Oracle.Timestamp(2002, 12, 17, 2, 24, 0),
                  cx_Oracle.Timestamp(2002, 12, 18, 4, 48, 0),
                  cx_Oracle.Timestamp(2002, 12, 19, 7, 12, 0),
                  cx_Oracle.Timestamp(2002, 12, 20, 9, 36, 0),
                  cx_Oracle.Timestamp(2002, 12, 21, 12, 0, 0) ] + \
                originalData[5:])

    def testBindOutDateArrayByVar(self):
        "test binding out a date array (with arrayvar)"
        array = self.cursor.arrayvar(cx_Oracle.DATETIME, 6, 100)
        self.cursor.execute(u"""
                begin
                  pkg_TestDateArrays.TestOutArrays(:p_NumElems, :p_Array);
                end;""",
                p_NumElems = 6,
                p_Array = array)
        self.failUnlessEqual(array.getvalue(),
                [ cx_Oracle.Timestamp(2002, 12, 13, 4, 48, 0),
                  cx_Oracle.Timestamp(2002, 12, 14, 9, 36, 0),
                  cx_Oracle.Timestamp(2002, 12, 15, 14, 24, 0),
                  cx_Oracle.Timestamp(2002, 12, 16, 19, 12, 0),
                  cx_Oracle.Timestamp(2002, 12, 18, 0, 0, 0),
                  cx_Oracle.Timestamp(2002, 12, 19, 4, 48, 0) ])

    def testBindOutSetInputSizes(self):
        "test binding out with set input sizes defined"
        vars = self.cursor.setinputsizes(p_Value = cx_Oracle.DATETIME)
        self.cursor.execute(u"""
                begin
                  :p_Value := to_date(20021209, 'YYYYMMDD');
                end;""")
        self.failUnlessEqual(vars["p_Value"].getvalue(),
               cx_Oracle.Timestamp(2002, 12, 9))

    def testBindInOutSetInputSizes(self):
        "test binding in/out with set input sizes defined"
        vars = self.cursor.setinputsizes(p_Value = cx_Oracle.DATETIME)
        self.cursor.execute(u"""
                begin
                  :p_Value := :p_Value + 5.25;
                end;""",
                p_Value = cx_Oracle.Timestamp(2002, 12, 12, 10, 0, 0))
        self.failUnlessEqual(vars["p_Value"].getvalue(),
                cx_Oracle.Timestamp(2002, 12, 17, 16, 0, 0))

    def testBindOutVar(self):
        "test binding out with cursor.var() method"
        var = self.cursor.var(cx_Oracle.DATETIME)
        self.cursor.execute(u"""
                begin
                  :p_Value := to_date('20021231 12:31:00',
                      'YYYYMMDD HH24:MI:SS');
                end;""",
                p_Value = var)
        self.failUnlessEqual(var.getvalue(),
               cx_Oracle.Timestamp(2002, 12, 31, 12, 31, 0))

    def testBindInOutVarDirectSet(self):
        "test binding in/out with cursor.var() method"
        var = self.cursor.var(cx_Oracle.DATETIME)
        var.setvalue(0, cx_Oracle.Timestamp(2002, 12, 9, 6, 0, 0))
        self.cursor.execute(u"""
                begin
                  :p_Value := :p_Value + 5.25;
                end;""",
                p_Value = var)
        self.failUnlessEqual(var.getvalue(),
                cx_Oracle.Timestamp(2002, 12, 14, 12, 0, 0))

    def testCursorDescription(self):
        "test cursor description is accurate"
        self.cursor.execute(u"select * from TestDates")
        self.failUnlessEqual(self.cursor.description,
                [ (u'INTCOL', cx_Oracle.NUMBER, 10, 22, 9, 0, 0),
                  (u'DATECOL', cx_Oracle.DATETIME, 23, 7, 0, 0, 0),
                  (u'NULLABLECOL', cx_Oracle.DATETIME, 23, 7, 0, 0, 1) ])

    def testFetchAll(self):
        "test that fetching all of the data returns the correct results"
        self.cursor.execute(u"select * From TestDates order by IntCol")
        self.failUnlessEqual(self.cursor.fetchall(), self.rawData)
        self.failUnlessEqual(self.cursor.fetchall(), [])

    def testFetchMany(self):
        "test that fetching data in chunks returns the correct results"
        self.cursor.execute(u"select * From TestDates order by IntCol")
        self.failUnlessEqual(self.cursor.fetchmany(3), self.rawData[0:3])
        self.failUnlessEqual(self.cursor.fetchmany(2), self.rawData[3:5])
        self.failUnlessEqual(self.cursor.fetchmany(4), self.rawData[5:9])
        self.failUnlessEqual(self.cursor.fetchmany(3), self.rawData[9:])
        self.failUnlessEqual(self.cursor.fetchmany(3), [])

    def testFetchOne(self):
        "test that fetching a single row returns the correct results"
        self.cursor.execute(u"""
                select *
                from TestDates
                where IntCol in (3, 4)
                order by IntCol""")
        self.failUnlessEqual(self.cursor.fetchone(), self.dataByKey[3])
        self.failUnlessEqual(self.cursor.fetchone(), self.dataByKey[4])
        self.failUnlessEqual(self.cursor.fetchone(), None)

