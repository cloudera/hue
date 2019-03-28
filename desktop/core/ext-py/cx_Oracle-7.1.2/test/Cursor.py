#------------------------------------------------------------------------------
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# Portions Copyright 2007-2015, Anthony Tuininga. All rights reserved.
#
# Portions Copyright 2001-2007, Computronix (Canada) Ltd., Edmonton, Alberta,
# Canada. All rights reserved.
#------------------------------------------------------------------------------

"""Module for testing cursor objects."""

import TestEnv

import cx_Oracle
import decimal
import sys

class TestCase(TestEnv.BaseTestCase):

    def testCreateScrollableCursor(self):
        """test creating a scrollable cursor"""
        cursor = self.connection.cursor()
        self.assertEqual(cursor.scrollable, False)
        cursor = self.connection.cursor(True)
        self.assertEqual(cursor.scrollable, True)
        cursor = self.connection.cursor(scrollable = True)
        self.assertEqual(cursor.scrollable, True)
        cursor.scrollable = False
        self.assertEqual(cursor.scrollable, False)

    def testExecuteNoArgs(self):
        """test executing a statement without any arguments"""
        result = self.cursor.execute("begin null; end;")
        self.assertEqual(result, None)

    def testExecuteNoStatementWithArgs(self):
        """test executing a None statement with bind variables"""
        self.assertRaises(cx_Oracle.ProgrammingError, self.cursor.execute,
                None, x = 5)

    def testExecuteEmptyKeywordArgs(self):
        """test executing a statement with args and empty keyword args"""
        simpleVar = self.cursor.var(cx_Oracle.NUMBER)
        args = [simpleVar]
        kwArgs = {}
        result = self.cursor.execute("begin :1 := 25; end;", args, **kwArgs)
        self.assertEqual(result, None)
        self.assertEqual(simpleVar.getvalue(), 25)

    def testExecuteKeywordArgs(self):
        """test executing a statement with keyword arguments"""
        simpleVar = self.cursor.var(cx_Oracle.NUMBER)
        result = self.cursor.execute("begin :value := 5; end;",
                value = simpleVar)
        self.assertEqual(result, None)
        self.assertEqual(simpleVar.getvalue(), 5)

    def testExecuteDictionaryArg(self):
        """test executing a statement with a dictionary argument"""
        simpleVar = self.cursor.var(cx_Oracle.NUMBER)
        dictArg = { "value" : simpleVar }
        result = self.cursor.execute("begin :value := 10; end;", dictArg)
        self.assertEqual(result, None)
        self.assertEqual(simpleVar.getvalue(), 10)
        dictArg = { u"value" : simpleVar }
        result = self.cursor.execute("begin :value := 25; end;", dictArg)
        self.assertEqual(result, None)
        self.assertEqual(simpleVar.getvalue(), 25)

    def testExecuteMultipleMethod(self):
        """test executing a statement with both a dict arg and keyword args"""
        simpleVar = self.cursor.var(cx_Oracle.NUMBER)
        dictArg = { "value" : simpleVar }
        self.assertRaises(cx_Oracle.InterfaceError, self.cursor.execute,
                "begin :value := 15; end;", dictArg, value = simpleVar)

    def testExecuteAndModifyArraySize(self):
        """test executing a statement and then changing the array size"""
        self.cursor.execute("select IntCol from TestNumbers")
        self.cursor.arraysize = 20
        self.assertEqual(len(self.cursor.fetchall()), 10)

    def testCallProc(self):
        """test executing a stored procedure"""
        var = self.cursor.var(cx_Oracle.NUMBER)
        results = self.cursor.callproc("proc_Test", ("hi", 5, var))
        self.assertEqual(results, ["hi", 10, 2.0])

    def testCallProcNoArgs(self):
        """test executing a stored procedure without any arguments"""
        results = self.cursor.callproc(u"proc_TestNoArgs")
        self.assertEqual(results, [])

    def testCallFunc(self):
        """test executing a stored function"""
        results = self.cursor.callfunc(u"func_Test", cx_Oracle.NUMBER,
                (u"hi", 5))
        self.assertEqual(results, 7)

    def testCallFuncNoArgs(self):
        """test executing a stored function without any arguments"""
        results = self.cursor.callfunc("func_TestNoArgs", cx_Oracle.NUMBER)
        self.assertEqual(results, 712)

    def testCallFuncNegative(self):
        """test executing a stored function with wrong parameters"""
        funcName = "func_Test"
        self.assertRaises(TypeError, self.cursor.callfunc, cx_Oracle.NUMBER,
                funcName, ("hi", 5))
        self.assertRaises(cx_Oracle.DatabaseError, self.cursor.callfunc,
                funcName, cx_Oracle.NUMBER, ("hi", 5, 7))
        self.assertRaises(TypeError, self.cursor.callfunc, funcName,
                cx_Oracle.NUMBER, "hi", 7)
        self.assertRaises(cx_Oracle.DatabaseError, self.cursor.callfunc,
                funcName, cx_Oracle.NUMBER, [5, "hi"])
        self.assertRaises(cx_Oracle.DatabaseError, self.cursor.callfunc,
                funcName, cx_Oracle.NUMBER)
        self.assertRaises(TypeError, self.cursor.callfunc, funcName,
                cx_Oracle.NUMBER, 5)

    def testExecuteManyByName(self):
        """test executing a statement multiple times (named args)"""
        self.cursor.execute("truncate table TestTempTable")
        rows = [ { u"value" : n } for n in range(250) ]
        self.cursor.arraysize = 100
        statement = "insert into TestTempTable (IntCol) values (:value)"
        self.cursor.executemany(statement, rows)
        self.connection.commit()
        self.cursor.execute("select count(*) from TestTempTable")
        count, = self.cursor.fetchone()
        self.assertEqual(count, len(rows))

    def testExecuteManyByPosition(self):
        """test executing a statement multiple times (positional args)"""
        self.cursor.execute("truncate table TestTempTable")
        rows = [ [n] for n in range(230) ]
        self.cursor.arraysize = 100
        statement = "insert into TestTempTable (IntCol) values (:1)"
        self.cursor.executemany(statement, rows)
        self.connection.commit()
        self.cursor.execute("select count(*) from TestTempTable")
        count, = self.cursor.fetchone()
        self.assertEqual(count, len(rows))

    def testExecuteManyWithPrepare(self):
        """test executing a statement multiple times (with prepare)"""
        self.cursor.execute("truncate table TestTempTable")
        rows = [ [n] for n in range(225) ]
        self.cursor.arraysize = 100
        statement = "insert into TestTempTable (IntCol) values (:1)"
        self.cursor.prepare(statement)
        self.cursor.executemany(None, rows)
        self.connection.commit()
        self.cursor.execute("select count(*) from TestTempTable")
        count, = self.cursor.fetchone()
        self.assertEqual(count, len(rows))

    def testExecuteManyWithRebind(self):
        """test executing a statement multiple times (with rebind)"""
        self.cursor.execute("truncate table TestTempTable")
        rows = [ [n] for n in range(235) ]
        self.cursor.arraysize = 100
        statement = "insert into TestTempTable (IntCol) values (:1)"
        self.cursor.executemany(statement, rows[:50])
        self.cursor.executemany(statement, rows[50:])
        self.connection.commit()
        self.cursor.execute("select count(*) from TestTempTable")
        count, = self.cursor.fetchone()
        self.assertEqual(count, len(rows))

    def testExecuteManyWithInputSizesWrong(self):
        "test executing a statement multiple times (with input sizes wrong)"
        cursor = self.connection.cursor()
        cursor.setinputsizes(cx_Oracle.NUMBER)
        data = [[decimal.Decimal("25.8")], [decimal.Decimal("30.0")]]
        cursor.executemany("declare t number; begin t := :1; end;", data)

    def testExecuteManyMultipleBatches(self):
        "test executing a statement multiple times (with multiple batches)"
        self.cursor.execute("truncate table TestTempTable")
        sql = "insert into TestTempTable (IntCol, StringCol) values (:1, :2)"
        self.cursor.executemany(sql, [(1, None), (2, None)])
        self.cursor.executemany(sql, [(3, None), (4, "Testing")])

    def testExecuteManyNumeric(self):
        "test executemany() with various numeric types"
        self.cursor.execute("truncate table TestTempTable")
        data = [(1, 5), (2, 7.0), (3, 6.5), (4, 2 ** 65),
                (5, decimal.Decimal("24.5"))]
        sql = "insert into TestTempTable (IntCol, NumberCol) values (:1, :2)"
        self.cursor.executemany(sql, data)
        self.cursor.execute("""
                select IntCol, NumberCol
                from TestTempTable
                order by IntCol""")
        self.assertEqual(self.cursor.fetchall(), data)

    def testExecuteManyWithResize(self):
        """test executing a statement multiple times (with resize)"""
        self.cursor.execute("truncate table TestTempTable")
        rows = [ ( 1, "First" ),
                 ( 2, "Second" ),
                 ( 3, "Third" ),
                 ( 4, "Fourth" ),
                 ( 5, "Fifth" ),
                 ( 6, "Sixth" ),
                 ( 7, "Seventh and the longest one" ) ]
        sql = "insert into TestTempTable (IntCol, StringCol) values (:1, :2)"
        self.cursor.executemany(sql, rows)
        self.cursor.execute("""
                select IntCol, StringCol
                from TestTempTable
                order by IntCol""")
        fetchedRows = self.cursor.fetchall()
        self.assertEqual(fetchedRows, rows)

    def testExecuteManyWithExecption(self):
        """test executing a statement multiple times (with exception)"""
        self.cursor.execute("truncate table TestTempTable")
        rows = [ { "value" : n } for n in (1, 2, 3, 2, 5) ]
        statement = "insert into TestTempTable (IntCol) values (:value)"
        self.assertRaises(cx_Oracle.DatabaseError, self.cursor.executemany,
                statement, rows)
        self.assertEqual(self.cursor.rowcount, 3)

    def testExecuteManyWithInvalidParameters(self):
        "test calling executemany() with invalid parameters"
        self.assertRaises(TypeError, self.cursor.executemany,
                "insert into TestTempTable (IntCol, StringCol) values (:1, :2)",
                "These are not valid parameters")

    def testExecuteManyNoParameters(self):
        "test calling executemany() without any bind parameters"
        numRows = 5
        self.cursor.execute("truncate table TestTempTable")
        self.cursor.executemany("""
                declare
                    t_Id          number;
                begin
                    select nvl(count(*), 0) + 1 into t_Id
                    from TestTempTable;

                    insert into TestTempTable (IntCol, StringCol)
                    values (t_Id, 'Test String ' || t_Id);
                end;""", numRows)
        self.cursor.execute("select count(*) from TestTempTable")
        count, = self.cursor.fetchone()
        self.assertEqual(count, numRows)

    def testExecuteManyBoundEarlier(self):
        "test calling executemany() with binds performed earlier"
        numRows = 9
        self.cursor.execute("truncate table TestTempTable")
        var = self.cursor.var(int, arraysize = numRows)
        self.cursor.setinputsizes(var)
        self.cursor.executemany("""
                declare
                    t_Id          number;
                begin
                    select nvl(count(*), 0) + 1 into t_Id
                    from TestTempTable;

                    insert into TestTempTable (IntCol, StringCol)
                    values (t_Id, 'Test String ' || t_Id);

                    select sum(IntCol) into :1
                    from TestTempTable;
                end;""", numRows)
        expectedData = [1, 3, 6, 10, 15, 21, 28, 36, 45]
        self.assertEqual(var.values, expectedData)

    def testPrepare(self):
        """test preparing a statement and executing it multiple times"""
        self.assertEqual(self.cursor.statement, None)
        statement = "begin :value := :value + 5; end;"
        self.cursor.prepare(statement)
        var = self.cursor.var(cx_Oracle.NUMBER)
        self.assertEqual(self.cursor.statement, statement)
        var.setvalue(0, 2)
        self.cursor.execute(None, value = var)
        self.assertEqual(var.getvalue(), 7)
        self.cursor.execute(None, value = var)
        self.assertEqual(var.getvalue(), 12)
        self.cursor.execute("begin :value2 := 3; end;", value2 = var)
        self.assertEqual(var.getvalue(), 3)

    def testExceptionOnClose(self):
        "confirm an exception is raised after closing a cursor"
        self.cursor.close()
        self.assertRaises(cx_Oracle.InterfaceError, self.cursor.execute,
                "select 1 from dual")

    def testIterators(self):
        """test iterators"""
        self.cursor.execute("""
                select IntCol
                from TestNumbers
                where IntCol between 1 and 3
                order by IntCol""")
        rows = []
        for row in self.cursor:
            rows.append(row[0])
        self.assertEqual(rows, [1, 2, 3])

    def testIteratorsInterrupted(self):
        """test iterators (with intermediate execute)"""
        self.cursor.execute("truncate table TestTempTable")
        self.cursor.execute("""
                select IntCol
                from TestNumbers
                where IntCol between 1 and 3
                order by IntCol""")
        testIter = iter(self.cursor)
        if sys.version_info[0] >= 3:
            value, = next(testIter)
        else:
            value, = testIter.next()
        self.cursor.execute("insert into TestTempTable (IntCol) values (1)")
        if sys.version_info[0] >= 3:
            self.assertRaises(cx_Oracle.InterfaceError, next, testIter)
        else:
            self.assertRaises(cx_Oracle.InterfaceError, testIter.next)

    def testBindNames(self):
        """test that bindnames() works correctly."""
        self.assertRaises(cx_Oracle.ProgrammingError, self.cursor.bindnames)
        self.cursor.prepare(u"begin null; end;")
        self.assertEqual(self.cursor.bindnames(), [])
        self.cursor.prepare("begin :retval := :inval + 5; end;")
        self.assertEqual(self.cursor.bindnames(), ["RETVAL", "INVAL"])
        self.cursor.prepare("begin :retval := :a * :a + :b * :b; end;")
        self.assertEqual(self.cursor.bindnames(), ["RETVAL", "A", "B"])
        self.cursor.prepare("begin :a := :b + :c + :d + :e + :f + :g + " + \
                ":h + :i + :j + :k + :l; end;")
        self.assertEqual(self.cursor.bindnames(),
                ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"])
        self.cursor.prepare("select :a * :a + :b * :b from dual")
        self.assertEqual(self.cursor.bindnames(), ["A", "B"])

    def testBadPrepare(self):
        """test that subsequent executes succeed after bad prepare"""
        self.assertRaises(cx_Oracle.DatabaseError,
                self.cursor.execute,
                "begin raise_application_error(-20000, 'this); end;")
        self.cursor.execute("begin null; end;")

    def testBadExecute(self):
        """test that subsequent fetches fail after bad execute"""
        self.assertRaises(cx_Oracle.DatabaseError,
                self.cursor.execute, "select y from dual")
        self.assertRaises(cx_Oracle.InterfaceError,
                self.cursor.fetchall)

    def testScrollAbsoluteExceptionAfter(self):
        """test scrolling absolute yields an exception (after result set)"""
        cursor = self.connection.cursor(scrollable = True)
        cursor.arraysize = self.cursor.arraysize
        cursor.execute("""
                select NumberCol
                from TestNumbers
                order by IntCol""")
        self.assertRaises(cx_Oracle.DatabaseError, cursor.scroll, 12,
                "absolute")

    def testScrollAbsoluteInBuffer(self):
        """test scrolling absolute (when in buffers)"""
        cursor = self.connection.cursor(scrollable = True)
        cursor.arraysize = self.cursor.arraysize
        cursor.execute("""
                select NumberCol
                from TestNumbers
                order by IntCol""")
        cursor.fetchmany()
        self.assertTrue(cursor.arraysize > 1,
                "array size must exceed 1 for this test to work correctly")
        cursor.scroll(1, mode = "absolute")
        row = cursor.fetchone()
        self.assertEqual(row[0], 1.25)
        self.assertEqual(cursor.rowcount, 1)

    def testScrollAbsoluteNotInBuffer(self):
        """test scrolling absolute (when not in buffers)"""
        cursor = self.connection.cursor(scrollable = True)
        cursor.arraysize = self.cursor.arraysize
        cursor.execute("""
                select NumberCol
                from TestNumbers
                order by IntCol""")
        cursor.scroll(6, mode = "absolute")
        row = cursor.fetchone()
        self.assertEqual(row[0], 7.5)
        self.assertEqual(cursor.rowcount, 6)

    def testScrollFirstInBuffer(self):
        """test scrolling to first row in result set (when in buffers)"""
        cursor = self.connection.cursor(scrollable = True)
        cursor.arraysize = self.cursor.arraysize
        cursor.execute("""
                select NumberCol
                from TestNumbers
                order by IntCol""")
        cursor.fetchmany()
        cursor.scroll(mode = "first")
        row = cursor.fetchone()
        self.assertEqual(row[0], 1.25)
        self.assertEqual(cursor.rowcount, 1)

    def testScrollFirstNotInBuffer(self):
        """test scrolling to first row in result set (when not in buffers)"""
        cursor = self.connection.cursor(scrollable = True)
        cursor.arraysize = self.cursor.arraysize
        cursor.execute("""
                select NumberCol
                from TestNumbers
                order by IntCol""")
        cursor.fetchmany()
        cursor.fetchmany()
        cursor.scroll(mode = "first")
        row = cursor.fetchone()
        self.assertEqual(row[0], 1.25)
        self.assertEqual(cursor.rowcount, 1)

    def testScrollLast(self):
        """test scrolling to last row in result set"""
        cursor = self.connection.cursor(scrollable = True)
        cursor.arraysize = self.cursor.arraysize
        cursor.execute("""
                select NumberCol
                from TestNumbers
                order by IntCol""")
        cursor.scroll(mode = "last")
        row = cursor.fetchone()
        self.assertEqual(row[0], 12.5)
        self.assertEqual(cursor.rowcount, 10)

    def testScrollRelativeExceptionAfter(self):
        """test scrolling relative yields an exception (after result set)"""
        cursor = self.connection.cursor(scrollable = True)
        cursor.arraysize = self.cursor.arraysize
        cursor.execute("""
                select NumberCol
                from TestNumbers
                order by IntCol""")
        self.assertRaises(cx_Oracle.DatabaseError, cursor.scroll, 15)

    def testScrollRelativeExceptionBefore(self):
        """test scrolling relative yields an exception (before result set)"""
        cursor = self.connection.cursor(scrollable = True)
        cursor.arraysize = self.cursor.arraysize
        cursor.execute("""
                select NumberCol
                from TestNumbers
                order by IntCol""")
        self.assertRaises(cx_Oracle.DatabaseError, cursor.scroll, -5)

    def testScrollRelativeInBuffer(self):
        """test scrolling relative (when in buffers)"""
        cursor = self.connection.cursor(scrollable = True)
        cursor.arraysize = self.cursor.arraysize
        cursor.execute("""
                select NumberCol
                from TestNumbers
                order by IntCol""")
        cursor.fetchmany()
        self.assertTrue(cursor.arraysize > 1,
                "array size must exceed 1 for this test to work correctly")
        cursor.scroll(2 - cursor.rowcount)
        row = cursor.fetchone()
        self.assertEqual(row[0], 2.5)
        self.assertEqual(cursor.rowcount, 2)

    def testScrollRelativeNotInBuffer(self):
        """test scrolling relative (when not in buffers)"""
        cursor = self.connection.cursor(scrollable = True)
        cursor.arraysize = self.cursor.arraysize
        cursor.execute("""
                select NumberCol
                from TestNumbers
                order by IntCol""")
        cursor.fetchmany()
        cursor.fetchmany()
        self.assertTrue(cursor.arraysize > 1,
                "array size must exceed 2 for this test to work correctly")
        cursor.scroll(3 - cursor.rowcount)
        row = cursor.fetchone()
        self.assertEqual(row[0], 3.75)
        self.assertEqual(cursor.rowcount, 3)

    def testScrollNoRows(self):
        """test scrolling when there are no rows"""
        self.cursor.execute("truncate table TestTempTable")
        cursor = self.connection.cursor(scrollable = True)
        cursor.execute("select * from TestTempTable")
        cursor.scroll(mode = "last")
        self.assertEqual(cursor.fetchall(), [])
        cursor.scroll(mode = "first")
        self.assertEqual(cursor.fetchall(), [])
        self.assertRaises(cx_Oracle.DatabaseError, cursor.scroll, 1,
                mode = "absolute")

    def testScrollDifferingArrayAndFetchSizes(self):
        """test scrolling with differing array sizes and fetch array sizes"""
        self.cursor.execute("truncate table TestTempTable")
        for i in range(30):
            self.cursor.execute("""
                    insert into TestTempTable (IntCol, StringCol)
                    values (:1, null)""",
                    (i + 1,))
        for arraySize in range(1, 6):
            cursor = self.connection.cursor(scrollable = True)
            cursor.arraysize = arraySize
            cursor.execute("select IntCol from TestTempTable order by IntCol")
            for numRows in range(1, arraySize + 1):
                cursor.scroll(15, "absolute")
                rows = cursor.fetchmany(numRows)
                self.assertEqual(rows[0][0], 15)
                self.assertEqual(cursor.rowcount, 15 + numRows - 1)
                cursor.scroll(9)
                rows = cursor.fetchmany(numRows)
                numRowsFetched = len(rows)
                self.assertEqual(rows[0][0], 15 + numRows + 8)
                self.assertEqual(cursor.rowcount,
                        15 + numRows + numRowsFetched + 7)
                cursor.scroll(-12)
                rows = cursor.fetchmany(numRows)
                self.assertEqual(rows[0][0], 15 + numRows + numRowsFetched - 5)
                self.assertEqual(cursor.rowcount,
                        15 + numRows + numRowsFetched + numRows - 6)

    def testSetInputSizesNegative(self):
        "test cursor.setinputsizes() with invalid parameters"
        val = decimal.Decimal(5)
        self.assertRaises(cx_Oracle.InterfaceError,
                self.cursor.setinputsizes, val, x = val)
        self.assertRaises(TypeError, self.cursor.setinputsizes, val)

    def testSetInputSizesNoParameters(self):
        "test setting input sizes without any parameters"
        self.cursor.setinputsizes()
        self.cursor.execute("select :val from dual", val = "Test Value")
        self.assertEqual(self.cursor.fetchall(), [("Test Value",)])

    def testSetInputSizesEmptyDict(self):
        "test setting input sizes with an empty dictionary"
        emptyDict = {}
        self.cursor.prepare("select 236 from dual")
        self.cursor.setinputsizes(**emptyDict)
        self.cursor.execute(None, emptyDict)
        self.assertEqual(self.cursor.fetchall(), [(236,)])

    def testSetInputSizesEmptyList(self):
        "test setting input sizes with an empty list"
        emptyList = {}
        self.cursor.prepare("select 239 from dual")
        self.cursor.setinputsizes(*emptyList)
        self.cursor.execute(None, emptyList)
        self.assertEqual(self.cursor.fetchall(), [(239,)])

    def testSetInputSizesByPosition(self):
        """test setting input sizes with positional args"""
        var = self.cursor.var(cx_Oracle.STRING, 100)
        self.cursor.setinputsizes(None, 5, None, 10, None, cx_Oracle.NUMBER)
        self.cursor.execute("""
                begin
                  :1 := :2 || to_char(:3) || :4 || to_char(:5) || to_char(:6);
                end;""", [var, 'test_', 5, '_second_', 3, 7])
        self.assertEqual(var.getvalue(), u"test_5_second_37")

    def testStringFormat(self):
        """test string format of cursor"""
        formatString = "<cx_Oracle.Cursor on <cx_Oracle.Connection to %s@%s>>"
        expectedValue = formatString % \
                (TestEnv.GetMainUser(), TestEnv.GetConnectString())
        self.assertEqual(str(self.cursor), expectedValue)

    def testCursorFetchRaw(self):
        """test cursor.fetchraw()"""
        cursor = self.connection.cursor()
        cursor.arraysize = 25
        cursor.execute("select LongIntCol from TestNumbers order by IntCol")
        self.assertEqual(cursor.fetchraw(), 10)
        self.assertEqual(cursor.fetchvars[0].getvalue(), 38)

    def testParse(self):
        """test parsing statements"""
        sql = "select LongIntCol from TestNumbers where IntCol = :val"
        self.cursor.parse(sql)
        self.assertEqual(self.cursor.statement, sql)
        self.assertEqual(self.cursor.description,
                [ ('LONGINTCOL', cx_Oracle.NUMBER, 17, None, 16, 0, 0) ])

    def testSetOutputSize(self):
        "test cursor.setoutputsize() does not fail (but does nothing)"
        self.cursor.setoutputsize(100, 2)

    def testVarNegative(self):
        "test cursor.var() with invalid parameters"
        self.assertRaises(TypeError, self.cursor.var, 5)

    def testArrayVarNegative(self):
        "test cursor.arrayvar() with invalid parameters"
        self.assertRaises(TypeError, self.cursor.arrayvar, 5, 1)

    def testBooleanWithoutPlsql(self):
        "test binding boolean data without the use of PL/SQL"
        self.cursor.execute("truncate table TestTempTable")
        sql = "insert into TestTempTable (IntCol, StringCol) values (:1, :2)"
        self.cursor.execute(sql, (False, "Value should be 0"))
        self.cursor.execute(sql, (True, "Value should be 1"))
        self.cursor.execute("""
                select IntCol, StringCol
                from TestTempTable
                order by IntCol""")
        self.assertEqual(self.cursor.fetchall(),
                [ (0, "Value should be 0"), (1, "Value should be 1") ])

    def testAsContextManager(self):
        "test using a cursor as a context manager"
        with self.cursor as cursor:
            cursor.execute("truncate table TestTempTable")
            cursor.execute("select count(*) from TestTempTable")
            count, = cursor.fetchone()
            self.assertEqual(count, 0)
        self.assertRaises(cx_Oracle.InterfaceError, self.cursor.close)

    def testQueryRowCount(self):
        "test that the rowcount attribute is reset to zero on query execute"
        sql = "select * from dual where 1 = :s"
        self.cursor.execute(sql, [0])
        self.cursor.fetchone()
        self.assertEqual(self.cursor.rowcount, 0)
        self.cursor.execute(sql, [1])
        self.cursor.fetchone()
        self.assertEqual(self.cursor.rowcount, 1)
        self.cursor.execute(sql, [1])
        self.cursor.fetchone()
        self.assertEqual(self.cursor.rowcount, 1)
        self.cursor.execute(sql, [0])
        self.cursor.fetchone()
        self.assertEqual(self.cursor.rowcount, 0)

    def testVarTypeNameNone(self):
        "test that the typename attribute can be passed a value of None"
        valueToSet = 5
        var = self.cursor.var(int, typename=None)
        var.setvalue(0, valueToSet)
        self.assertEqual(var.getvalue(), valueToSet)

    def testVarTypeWithObjectType(self):
        "test that an object type can be used as type in cursor.var()"
        objType = self.connection.gettype("UDT_OBJECT")
        var = self.cursor.var(objType)
        self.cursor.callproc("pkg_TestBindObject.BindObjectOut",
                (28, "Bind obj out", var))
        obj = var.getvalue()
        result = self.cursor.callfunc("pkg_TestBindObject.GetStringRep", str,
                (obj,))
        self.assertEqual(result,
                "udt_Object(28, 'Bind obj out', null, null, null, null, null)")

    def testFetchXMLType(self):
        "test that fetching an XMLType returns a string contains its contents"
        intVal = 5
        label = "IntCol"
        expectedResult = "<%s>%s</%s>" % (label, intVal, label)
        self.cursor.execute("""
                select XMLElement("%s", IntCol)
                from TestStrings
                where IntCol = :intVal""" % label,
                intVal = intVal)
        result, = self.cursor.fetchone()
        self.assertEqual(result, expectedResult)

if __name__ == "__main__":
    TestEnv.RunTestCases()

