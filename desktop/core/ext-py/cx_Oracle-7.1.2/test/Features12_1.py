#------------------------------------------------------------------------------
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# Portions Copyright 2007-2015, Anthony Tuininga. All rights reserved.
#
# Portions Copyright 2001-2007, Computronix (Canada) Ltd., Edmonton, Alberta,
# Canada. All rights reserved.
#------------------------------------------------------------------------------

"""Module for testing features introduced in 12.1"""

import TestEnv

import cx_Oracle
import datetime
# import sys

# if sys.version_info > (3,):
#     long = int

class TestCase(TestEnv.BaseTestCase):

    def testArrayDMLRowCountsOff(self):
        "test executing with arraydmlrowcounts mode disabled"
        self.cursor.execute("truncate table TestArrayDML")
        rows = [ (1, "First"),
                 (2, "Second") ]
        sql = "insert into TestArrayDML (IntCol,StringCol) values (:1,:2)"
        self.cursor.executemany(sql, rows, arraydmlrowcounts = False)
        self.assertRaises(cx_Oracle.DatabaseError,
                self.cursor.getarraydmlrowcounts)
        rows = [ (3, "Third"),
                 (4, "Fourth") ]
        self.cursor.executemany(sql, rows)
        self.assertRaises(cx_Oracle.DatabaseError,
                self.cursor.getarraydmlrowcounts)

    def testArrayDMLRowCountsOn(self):
        "test executing with arraydmlrowcounts mode enabled"
        self.cursor.execute("truncate table TestArrayDML")
        rows = [ ( 1, "First", 100),
                 ( 2, "Second", 200),
                 ( 3, "Third", 300),
                 ( 4, "Fourth", 300),
                 ( 5, "Fifth", 300) ]
        sql = "insert into TestArrayDML (IntCol,StringCol,IntCol2) " \
                "values (:1,:2,:3)"
        self.cursor.executemany(sql, rows, arraydmlrowcounts = True)
        self.connection.commit()
        self.assertEqual(self.cursor.getarraydmlrowcounts(), [1, 1, 1, 1, 1])
        self.cursor.execute("select count(*) from TestArrayDML")
        count, = self.cursor.fetchone()
        self.assertEqual(count, len(rows))

    def testBindPLSQLBooleanCollectionIn(self):
        "test binding a boolean collection (in)"
        typeObj = self.connection.gettype("PKG_TESTBOOLEANS.UDT_BOOLEANLIST")
        obj = typeObj.newobject()
        obj.setelement(1, True)
        obj.extend([True, False, True, True, False, True])
        result = self.cursor.callfunc("pkg_TestBooleans.TestInArrays", int,
                (obj,))
        self.assertEqual(result, 5)

    def testBindPLSQLBooleanCollectionOut(self):
        "test binding a boolean collection (out)"
        typeObj = self.connection.gettype("PKG_TESTBOOLEANS.UDT_BOOLEANLIST")
        obj = typeObj.newobject()
        self.cursor.callproc("pkg_TestBooleans.TestOutArrays", (6, obj))
        self.assertEqual(obj.aslist(), [True, False, True, False, True, False])

    def testBindPLSQLDateCollectionIn(self):
        "test binding a PL/SQL date collection (in)"
        typeObj = self.connection.gettype("PKG_TESTDATEARRAYS.UDT_DATELIST")
        obj = typeObj.newobject()
        obj.setelement(1, datetime.datetime(2016, 2, 5))
        obj.append(datetime.datetime(2016, 2, 8, 12, 15, 30))
        obj.append(datetime.datetime(2016, 2, 12, 5, 44, 30))
        result = self.cursor.callfunc("pkg_TestDateArrays.TestInArrays",
                cx_Oracle.NUMBER, (2, datetime.datetime(2016, 2, 1), obj))
        self.assertEqual(result, 24.75)

    def testBindPLSQLDateCollectionInOut(self):
        "test binding a PL/SQL date collection (in/out)"
        typeObj = self.connection.gettype("PKG_TESTDATEARRAYS.UDT_DATELIST")
        obj = typeObj.newobject()
        obj.setelement(1, datetime.datetime(2016, 1, 1))
        obj.append(datetime.datetime(2016, 1, 7))
        obj.append(datetime.datetime(2016, 1, 13))
        obj.append(datetime.datetime(2016, 1, 19))
        self.cursor.callproc("pkg_TestDateArrays.TestInOutArrays", (4, obj))
        self.assertEqual(obj.aslist(),
                [datetime.datetime(2016, 1, 8),
                 datetime.datetime(2016, 1, 14),
                 datetime.datetime(2016, 1, 20),
                 datetime.datetime(2016, 1, 26)])

    def testBindPLSQLDateCollectionOut(self):
        "test binding a PL/SQL date collection (out)"
        typeObj = self.connection.gettype("PKG_TESTDATEARRAYS.UDT_DATELIST")
        obj = typeObj.newobject()
        self.cursor.callproc("pkg_TestDateArrays.TestOutArrays", (3, obj))
        self.assertEqual(obj.aslist(),
                [datetime.datetime(2002, 12, 13, 4, 48),
                 datetime.datetime(2002, 12, 14, 9, 36),
                 datetime.datetime(2002, 12, 15, 14, 24)])

    def testBindPLSQLNumberCollectionIn(self):
        "test binding a PL/SQL number collection (in)"
        typeObj = self.connection.gettype("PKG_TESTNUMBERARRAYS.UDT_NUMBERLIST")
        obj = typeObj.newobject()
        obj.setelement(1, 10)
        obj.extend([20, 30, 40, 50])
        result = self.cursor.callfunc("pkg_TestNumberArrays.TestInArrays", int,
                (5, obj))
        self.assertEqual(result, 155)

    def testBindPLSQLNumberCollectionInOut(self):
        "test binding a PL/SQL number collection (in/out)"
        typeObj = self.connection.gettype("PKG_TESTNUMBERARRAYS.UDT_NUMBERLIST")
        obj = typeObj.newobject()
        obj.setelement(1, 5)
        obj.extend([8, 3, 2])
        self.cursor.callproc("pkg_TestNumberArrays.TestInOutArrays", (4, obj))
        self.assertEqual(obj.aslist(), [50, 80, 30, 20])

    def testBindPLSQLNumberCollectionOut(self):
        "test binding a PL/SQL number collection (out)"
        typeObj = self.connection.gettype("PKG_TESTNUMBERARRAYS.UDT_NUMBERLIST")
        obj = typeObj.newobject()
        self.cursor.callproc("pkg_TestNumberArrays.TestOutArrays", (3, obj))
        self.assertEqual(obj.aslist(), [100, 200, 300])

    def testBindPLSQLRecordArray(self):
        "test binding an array of PL/SQL records (in)"
        recType = self.connection.gettype("PKG_TESTRECORDS.UDT_RECORD")
        arrayType = self.connection.gettype("PKG_TESTRECORDS.UDT_RECORDARRAY")
        arrayObj = arrayType.newobject()
        for i in range(3):
            obj = recType.newobject()
            obj.NUMBERVALUE = i + 1
            obj.STRINGVALUE = "String in record #%d" % (i + 1)
            obj.DATEVALUE = datetime.datetime(2017, i + 1, 1)
            obj.TIMESTAMPVALUE = datetime.datetime(2017, 1, i + 1)
            obj.BOOLEANVALUE = (i % 2) == 1
            arrayObj.append(obj)
        result = self.cursor.callfunc("pkg_TestRecords.TestInArrays", str,
                (arrayObj,))
        self.assertEqual(result,
                "udt_Record(1, 'String in record #1', " \
                "to_date('2017-01-01', 'YYYY-MM-DD'), " \
                "to_timestamp('2017-01-01 00:00:00', " \
                "'YYYY-MM-DD HH24:MI:SS'), false); " \
                "udt_Record(2, 'String in record #2', " \
                "to_date('2017-02-01', 'YYYY-MM-DD'), " \
                "to_timestamp('2017-01-02 00:00:00', " \
                "'YYYY-MM-DD HH24:MI:SS'), true); " \
                "udt_Record(3, 'String in record #3', " \
                "to_date('2017-03-01', 'YYYY-MM-DD'), " \
                "to_timestamp('2017-01-03 00:00:00', " \
                "'YYYY-MM-DD HH24:MI:SS'), false)")

    def testBindPLSQLRecordIn(self):
        "test binding a PL/SQL record (in)"
        typeObj = self.connection.gettype("PKG_TESTRECORDS.UDT_RECORD")
        obj = typeObj.newobject()
        obj.NUMBERVALUE = 18
        obj.STRINGVALUE = "A string in a record"
        obj.DATEVALUE = datetime.datetime(2016, 2, 15)
        obj.TIMESTAMPVALUE = datetime.datetime(2016, 2, 12, 14, 25, 36)
        obj.BOOLEANVALUE = False
        result = self.cursor.callfunc("pkg_TestRecords.GetStringRep", str,
                (obj,))
        self.assertEqual(result,
                "udt_Record(18, 'A string in a record', " \
                "to_date('2016-02-15', 'YYYY-MM-DD'), " \
                "to_timestamp('2016-02-12 14:25:36', " \
                "'YYYY-MM-DD HH24:MI:SS'), false)")

    def testBindPLSQLRecordOut(self):
        "test binding a PL/SQL record (out)"
        typeObj = self.connection.gettype("PKG_TESTRECORDS.UDT_RECORD")
        obj = typeObj.newobject()
        obj.NUMBERVALUE = 5
        obj.STRINGVALUE = "Test value"
        obj.DATEVALUE = datetime.datetime.today()
        obj.TIMESTAMPVALUE = datetime.datetime.today()
        obj.BOOLEANVALUE = False
        self.cursor.callproc("pkg_TestRecords.TestOut", (obj,))
        self.assertEqual(obj.NUMBERVALUE, 25)
        self.assertEqual(obj.STRINGVALUE, "String in record")
        self.assertEqual(obj.DATEVALUE, datetime.datetime(2016, 2, 16))
        self.assertEqual(obj.TIMESTAMPVALUE,
                datetime.datetime(2016, 2, 16, 18, 23, 55))
        self.assertEqual(obj.BOOLEANVALUE, True)

    def testBindPLSQLStringCollectionIn(self):
        "test binding a PL/SQL string collection (in)"
        typeObj = self.connection.gettype("PKG_TESTSTRINGARRAYS.UDT_STRINGLIST")
        obj = typeObj.newobject()
        obj.setelement(1, "First element")
        obj.setelement(2, "Second element")
        obj.setelement(3, "Third element")
        result = self.cursor.callfunc("pkg_TestStringArrays.TestInArrays", int,
                (5, obj))
        self.assertEqual(result, 45)

    def testBindPLSQLStringCollectionInOut(self):
        "test binding a PL/SQL string collection (in/out)"
        typeObj = self.connection.gettype("PKG_TESTSTRINGARRAYS.UDT_STRINGLIST")
        obj = typeObj.newobject()
        obj.setelement(1, "The first element")
        obj.append("The second element")
        obj.append("The third and final element")
        self.cursor.callproc("pkg_TestStringArrays.TestInOutArrays", (3, obj))
        self.assertEqual(obj.aslist(),
                ['Converted element # 1 originally had length 17',
                 'Converted element # 2 originally had length 18',
                 'Converted element # 3 originally had length 27'])

    def testBindPLSQLStringCollectionOut(self):
        "test binding a PL/SQL string collection (out)"
        typeObj = self.connection.gettype("PKG_TESTSTRINGARRAYS.UDT_STRINGLIST")
        obj = typeObj.newobject()
        self.cursor.callproc("pkg_TestStringArrays.TestOutArrays", (4, obj))
        self.assertEqual(obj.aslist(),
                ['Test out element # 1',
                 'Test out element # 2',
                 'Test out element # 3',
                 'Test out element # 4'])

    def testBindPLSQLStringCollectionOutWithHoles(self):
        "test binding a PL/SQL string collection (out with holes)"
        typeObj = self.connection.gettype("PKG_TESTSTRINGARRAYS.UDT_STRINGLIST")
        obj = typeObj.newobject()
        self.cursor.callproc("pkg_TestStringArrays.TestIndexBy", (obj,))
        self.assertEqual(obj.first(), -1048576)
        self.assertEqual(obj.last(), 8388608)
        self.assertEqual(obj.next(-576), 284)
        self.assertEqual(obj.prev(284), -576)
        self.assertEqual(obj.size(), 4)
        self.assertEqual(obj.exists(-576), True)
        self.assertEqual(obj.exists(-577), False)
        self.assertEqual(obj.getelement(284), 'Third element')
        self.assertEqual(obj.aslist(),
                ["First element", "Second element", "Third element",
                 "Fourth element"])
        self.assertEqual(obj.asdict(),
                { -1048576 : 'First element',
                  -576 : 'Second element',
                  284 : 'Third element',
                  8388608: 'Fourth element' })
        obj.delete(-576)
        obj.delete(284)
        self.assertEqual(obj.aslist(), ["First element", "Fourth element"])
        self.assertEqual(obj.asdict(),
                { -1048576 : 'First element',
                  8388608: 'Fourth element' })

    def testExceptionInIteration(self):
        "test executing with arraydmlrowcounts with exception"
        self.cursor.execute("truncate table TestArrayDML")
        rows = [ (1, "First"),
                 (2, "Second"),
                 (2, "Third"),
                 (4, "Fourth") ]
        sql = "insert into TestArrayDML (IntCol,StringCol) values (:1,:2)"
        self.assertRaises(cx_Oracle.DatabaseError, self.cursor.executemany,
                sql, rows, arraydmlrowcounts = True)
        self.assertEqual(self.cursor.getarraydmlrowcounts(), [1, 1])

    def testExecutingDelete(self):
        "test executing delete statement with arraydmlrowcount mode"
        self.cursor.execute("truncate table TestArrayDML")
        rows = [ (1, "First", 100),
                 (2, "Second", 200),
                 (3, "Third", 300),
                 (4, "Fourth", 300),
                 (5, "Fifth", 300),
                 (6, "Sixth", 400),
                 (7, "Seventh", 400),
                 (8, "Eighth", 500) ]
        sql = "insert into TestArrayDML (IntCol,StringCol,IntCol2) " \
                "values (:1, :2, :3)"
        self.cursor.executemany(sql, rows)
        rows = [ (200,), (300,), (400,) ]
        statement = "delete from TestArrayDML where IntCol2 = :1"
        self.cursor.executemany(statement, rows, arraydmlrowcounts = True)
        self.assertEqual(self.cursor.getarraydmlrowcounts(), [1, 3, 2])

    def testExecutingUpdate(self):
        "test executing update statement with arraydmlrowcount mode"
        self.cursor.execute("truncate table TestArrayDML")
        rows = [ (1, "First",100),
                 (2, "Second",200),
                 (3, "Third",300),
                 (4, "Fourth",300),
                 (5, "Fifth",300),
                 (6, "Sixth",400),
                 (7, "Seventh",400),
                 (8, "Eighth",500) ]
        sql = "insert into TestArrayDML (IntCol,StringCol,IntCol2) " \
                "values (:1, :2, :3)"
        self.cursor.executemany(sql, rows)
        rows = [ ("One", 100),
                 ("Two", 200),
                 ("Three", 300),
                 ("Four", 400) ]
        sql = "update TestArrayDML set StringCol = :1 where IntCol2 = :2"
        self.cursor.executemany(sql, rows, arraydmlrowcounts = True)
        self.assertEqual(self.cursor.getarraydmlrowcounts(), [1, 1, 3, 2])

    def testImplicitResults(self):
        "test getimplicitresults() returns the correct data"
        self.cursor.execute("""
                declare
                    c1 sys_refcursor;
                    c2 sys_refcursor;
                begin

                    open c1 for
                    select NumberCol
                    from TestNumbers
                    where IntCol between 3 and 5;

                    dbms_sql.return_result(c1);

                    open c2 for
                    select NumberCol
                    from TestNumbers
                    where IntCol between 7 and 10;

                    dbms_sql.return_result(c2);

                end;""")
        results = self.cursor.getimplicitresults()
        self.assertEqual(len(results), 2)
        self.assertEqual([n for n, in results[0]], [3.75, 5, 6.25])
        self.assertEqual([n for n, in results[1]], [8.75, 10, 11.25, 12.5])

    def testImplicitResultsNoStatement(self):
        "test getimplicitresults() without executing a statement"
        self.assertRaises(cx_Oracle.InterfaceError,
                self.cursor.getimplicitresults)

    def testInsertWithBatchError(self):
        "test executing insert with multiple distinct batch errors"
        self.cursor.execute("truncate table TestArrayDML")
        rows = [ (1, "First", 100),
                 (2, "Second", 200),
                 (2, "Third", 300),
                 (4, "Fourth", 400),
                 (5, "Fourth", 1000)]
        sql = "insert into TestArrayDML (IntCol, StringCol, IntCol2) " \
                "values (:1, :2, :3)"
        self.cursor.executemany(sql, rows, batcherrors = True,
                arraydmlrowcounts = True)
        user = TestEnv.GetMainUser()
        expectedErrors = [
                ( 4, 1438, "ORA-01438: value larger than specified " \
                        "precision allowed for this column" ),
                ( 2, 1, "ORA-00001: unique constraint " \
                        "(%s.TESTARRAYDML_PK) violated" % user.upper())
        ]
        actualErrors = [(e.offset, e.code, e.message) \
                for e in self.cursor.getbatcherrors()]
        self.assertEqual(actualErrors, expectedErrors)
        self.assertEqual(self.cursor.getarraydmlrowcounts(), [1, 1, 0, 1, 0])

    def testBatchErrorFalse(self):
        "test batcherrors mode set to False"
        self.cursor.execute("truncate table TestArrayDML")
        rows = [ (1, "First", 100),
                 (2, "Second", 200),
                 (2, "Third", 300) ]
        sql = "insert into TestArrayDML (IntCol, StringCol, IntCol2) " \
                "values (:1, :2, :3)"
        self.assertRaises(cx_Oracle.IntegrityError,
                self.cursor.executemany, sql, rows, batcherrors = False)

    def testUpdatewithBatchError(self):
        "test executing in succession with batch error"
        self.cursor.execute("truncate table TestArrayDML")
        rows = [ (1, "First", 100),
                 (2, "Second", 200),
                 (3, "Third", 300),
                 (4, "Second", 300),
                 (5, "Fifth", 300),
                 (6, "Sixth", 400),
                 (6, "Seventh", 400),
                 (8, "Eighth", 100) ]
        sql = "insert into TestArrayDML (IntCol, StringCol, IntCol2) " \
                "values (:1, :2, :3)"
        self.cursor.executemany(sql, rows, batcherrors = True)
        user = TestEnv.GetMainUser()
        expectedErrors = [
                ( 6, 1, "ORA-00001: unique constraint " \
                        "(%s.TESTARRAYDML_PK) violated" % user.upper())
        ]
        actualErrors = [(e.offset, e.code, e.message) \
                for e in self.cursor.getbatcherrors()]
        self.assertEqual(actualErrors, expectedErrors)
        rows = [ (101, "First"),
                 (201, "Second"),
                 (3000, "Third"),
                 (900, "Ninth"),
                 (301, "Third") ]
        sql = "update TestArrayDML set IntCol2 = :1 where StringCol = :2"
        self.cursor.executemany(sql, rows, arraydmlrowcounts = True,
                batcherrors = True)
        expectedErrors = [
                ( 2, 1438, "ORA-01438: value larger than specified " \
                        "precision allowed for this column" )
        ]
        actualErrors = [(e.offset, e.code, e.message) \
                for e in self.cursor.getbatcherrors()]
        self.assertEqual(actualErrors, expectedErrors)
        self.assertEqual(self.cursor.getarraydmlrowcounts(),
                [1, 2, 0, 0, 1])
        self.assertEqual(self.cursor.rowcount, 4)

if __name__ == "__main__":
    TestEnv.RunTestCases()

