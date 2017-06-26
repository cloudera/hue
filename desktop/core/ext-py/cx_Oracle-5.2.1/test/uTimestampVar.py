"""Module for testing timestamp variables."""

import time

class TestTimestampVar(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)
        self.rawData = []
        self.dataByKey = {}
        for i in range(1, 11):
            timeTuple = (2002, 12, 9, 0, 0, 0, 0, 0, -1)
            timeInTicks = time.mktime(timeTuple) + i * 86400
            dateValue = cx_Oracle.TimestampFromTicks(int(timeInTicks))
            strValue = str(i * 50)
            fsecond = int(strValue + "0" * (6 - len(strValue)))
            dateCol = cx_Oracle.Timestamp(dateValue.year, dateValue.month,
                    dateValue.day, dateValue.hour, dateValue.minute,
                    i * 2, fsecond)
            if i % 2:
                timeInTicks = time.mktime(timeTuple) + i * 86400 + 86400
                dateValue = cx_Oracle.TimestampFromTicks(int(timeInTicks))
                strValue = str(i * 125)
                fsecond = int(strValue + "0" * (6 - len(strValue)))
                nullableCol = cx_Oracle.Timestamp(dateValue.year,
                        dateValue.month, dateValue.day, dateValue.hour,
                        dateValue.minute, i * 3, fsecond)
            else:
                nullableCol = None
            tuple = (i, dateCol, nullableCol)
            self.rawData.append(tuple)
            self.dataByKey[i] = tuple

    def testBindTimestamp(self):
        "test binding in a timestamp"
        self.cursor.setinputsizes(value = cx_Oracle.TIMESTAMP)
        self.cursor.execute(u"""
                select * from TestTimestamps
                where TimestampCol = :value""",
                value = cx_Oracle.Timestamp(2002, 12, 14, 0, 0, 10, 250000))
        self.failUnlessEqual(self.cursor.fetchall(), [self.dataByKey[5]])

    def testBindNull(self):
        "test binding in a null"
        self.cursor.setinputsizes(value = cx_Oracle.TIMESTAMP)
        self.cursor.execute(u"""
                select * from TestTimestamps
                where TimestampCol = :value""",
                value = None)
        self.failUnlessEqual(self.cursor.fetchall(), [])

    def testBindOutSetInputSizes(self):
        "test binding out with set input sizes defined"
        vars = self.cursor.setinputsizes(value = cx_Oracle.TIMESTAMP)
        self.cursor.execute(u"""
                begin
                  :value := to_timestamp('20021209', 'YYYYMMDD');
                end;""")
        self.failUnlessEqual(vars["value"].getvalue(),
               cx_Oracle.Timestamp(2002, 12, 9))

    def testBindInOutSetInputSizes(self):
        "test binding in/out with set input sizes defined"
        vars = self.cursor.setinputsizes(value = cx_Oracle.TIMESTAMP)
        self.cursor.execute(u"""
                begin
                  :value := :value + 5.25;
                end;""",
                value = cx_Oracle.Timestamp(2002, 12, 12, 10, 0, 0))
        self.failUnlessEqual(vars["value"].getvalue(),
                cx_Oracle.Timestamp(2002, 12, 17, 16, 0, 0))

    def testBindOutVar(self):
        "test binding out with cursor.var() method"
        var = self.cursor.var(cx_Oracle.TIMESTAMP)
        self.cursor.execute(u"""
                begin
                  :value := to_date('20021231 12:31:00',
                      'YYYYMMDD HH24:MI:SS');
                end;""",
                value = var)
        self.failUnlessEqual(var.getvalue(),
               cx_Oracle.Timestamp(2002, 12, 31, 12, 31, 0))

    def testBindInOutVarDirectSet(self):
        "test binding in/out with cursor.var() method"
        var = self.cursor.var(cx_Oracle.TIMESTAMP)
        var.setvalue(0, cx_Oracle.Timestamp(2002, 12, 9, 6, 0, 0))
        self.cursor.execute(u"""
                begin
                  :value := :value + 5.25;
                end;""",
                value = var)
        self.failUnlessEqual(var.getvalue(),
                cx_Oracle.Timestamp(2002, 12, 14, 12, 0, 0))

    def testCursorDescription(self):
        "test cursor description is accurate"
        self.cursor.execute(u"select * from TestTimestamps")
        self.failUnlessEqual(self.cursor.description,
                [ ('INTCOL', cx_Oracle.NUMBER, 10, 22, 9, 0, 0),
                  ('TIMESTAMPCOL', cx_Oracle.TIMESTAMP, -1, 11, 0, 0, 0),
                  ('NULLABLECOL', cx_Oracle.TIMESTAMP, -1, 11, 0, 0, 1) ])

    def testFetchAll(self):
        "test that fetching all of the data returns the correct results"
        self.cursor.execute(u"select * From TestTimestamps order by IntCol")
        self.failUnlessEqual(self.cursor.fetchall(), self.rawData)
        self.failUnlessEqual(self.cursor.fetchall(), [])

    def testFetchMany(self):
        "test that fetching data in chunks returns the correct results"
        self.cursor.execute(u"select * From TestTimestamps order by IntCol")
        self.failUnlessEqual(self.cursor.fetchmany(3), self.rawData[0:3])
        self.failUnlessEqual(self.cursor.fetchmany(2), self.rawData[3:5])
        self.failUnlessEqual(self.cursor.fetchmany(4), self.rawData[5:9])
        self.failUnlessEqual(self.cursor.fetchmany(3), self.rawData[9:])
        self.failUnlessEqual(self.cursor.fetchmany(3), [])

    def testFetchOne(self):
        "test that fetching a single row returns the correct results"
        self.cursor.execute(u"""
                select *
                from TestTimestamps
                where IntCol in (3, 4)
                order by IntCol""")
        self.failUnlessEqual(self.cursor.fetchone(), self.dataByKey[3])
        self.failUnlessEqual(self.cursor.fetchone(), self.dataByKey[4])
        self.failUnlessEqual(self.cursor.fetchone(), None)

