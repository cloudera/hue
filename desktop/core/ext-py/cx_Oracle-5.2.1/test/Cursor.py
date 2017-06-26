"""Module for testing cursor objects."""

import cx_Oracle
import sys

class TestCursor(BaseTestCase):

    def testExecuteNoArgs(self):
        """test executing a statement without any arguments"""
        result = self.cursor.execute("begin null; end;")
        self.failUnlessEqual(result, None)

    def testExecuteNoStatementWithArgs(self):
        """test executing a None statement with bind variables"""
        self.failUnlessRaises(cx_Oracle.ProgrammingError, self.cursor.execute,
                None, x = 5)

    def testExecuteEmptyKeywordArgs(self):
        """test executing a statement with args and empty keyword args"""
        simpleVar = self.cursor.var(cx_Oracle.NUMBER)
        args = [simpleVar]
        kwArgs = {}
        result = self.cursor.execute("begin :1 := 25; end;", args, **kwArgs)
        self.failUnlessEqual(result, None)
        self.failUnlessEqual(simpleVar.getvalue(), 25)

    def testExecuteKeywordArgs(self):
        """test executing a statement with keyword arguments"""
        simpleVar = self.cursor.var(cx_Oracle.NUMBER)
        result = self.cursor.execute("begin :value := 5; end;",
                value = simpleVar)
        self.failUnlessEqual(result, None)
        self.failUnlessEqual(simpleVar.getvalue(), 5)

    def testExecuteDictionaryArg(self):
        """test executing a statement with a dictionary argument"""
        simpleVar = self.cursor.var(cx_Oracle.NUMBER)
        dictArg = { "value" : simpleVar }
        result = self.cursor.execute("begin :value := 10; end;", dictArg)
        self.failUnlessEqual(result, None)
        self.failUnlessEqual(simpleVar.getvalue(), 10)

    def testExecuteMultipleMethod(self):
        """test executing a statement with both a dict arg and keyword args"""
        simpleVar = self.cursor.var(cx_Oracle.NUMBER)
        dictArg = { "value" : simpleVar }
        self.failUnlessRaises(cx_Oracle.InterfaceError, self.cursor.execute,
                "begin :value := 15; end;", dictArg, value = simpleVar)

    def testExecuteAndModifyArraySize(self):
        """test executing a statement and then changing the array size"""
        self.cursor.execute("select IntCol from TestNumbers")
        self.cursor.arraysize = 20
        self.failUnlessEqual(len(self.cursor.fetchall()), 10)

    def testCallProc(self):
        """test executing a stored procedure"""
        var = self.cursor.var(cx_Oracle.NUMBER)
        results = self.cursor.callproc("proc_Test", ("hi", 5, var))
        self.failUnlessEqual(results, ["hi", 10, 2.0])

    def testCallProcNoArgs(self):
        """test executing a stored procedure without any arguments"""
        results = self.cursor.callproc("proc_TestNoArgs")
        self.failUnlessEqual(results, [])

    def testCallFunc(self):
        """test executing a stored function"""
        results = self.cursor.callfunc("func_Test", cx_Oracle.NUMBER,
                ("hi", 5))
        self.failUnlessEqual(results, 7)

    def testCallFuncNoArgs(self):
        """test executing a stored function without any arguments"""
        results = self.cursor.callfunc("func_TestNoArgs", cx_Oracle.NUMBER)
        self.failUnlessEqual(results, 712)

    def testExecuteManyByName(self):
        """test executing a statement multiple times (named args)"""
        self.cursor.execute("truncate table TestExecuteMany")
        rows = [ { "value" : n } for n in range(250) ]
        self.cursor.arraysize = 100
        statement = "insert into TestExecuteMany (IntCol) values (:value)"
        self.cursor.executemany(statement, rows)
        self.connection.commit()
        self.cursor.execute("select count(*) from TestExecuteMany")
        count, = self.cursor.fetchone()
        self.failUnlessEqual(count, len(rows))

    def testExecuteManyByPosition(self):
        """test executing a statement multiple times (positional args)"""
        self.cursor.execute("truncate table TestExecuteMany")
        rows = [ [n] for n in range(230) ]
        self.cursor.arraysize = 100
        statement = "insert into TestExecuteMany (IntCol) values (:1)"
        self.cursor.executemany(statement, rows)
        self.connection.commit()
        self.cursor.execute("select count(*) from TestExecuteMany")
        count, = self.cursor.fetchone()
        self.failUnlessEqual(count, len(rows))

    def testExecuteManyWithPrepare(self):
        """test executing a statement multiple times (with prepare)"""
        self.cursor.execute("truncate table TestExecuteMany")
        rows = [ [n] for n in range(225) ]
        self.cursor.arraysize = 100
        statement = "insert into TestExecuteMany (IntCol) values (:1)"
        self.cursor.prepare(statement)
        self.cursor.executemany(None, rows)
        self.connection.commit()
        self.cursor.execute("select count(*) from TestExecuteMany")
        count, = self.cursor.fetchone()
        self.failUnlessEqual(count, len(rows))

    def testExecuteManyWithRebind(self):
        """test executing a statement multiple times (with rebind)"""
        self.cursor.execute("truncate table TestExecuteMany")
        rows = [ [n] for n in range(235) ]
        self.cursor.arraysize = 100
        statement = "insert into TestExecuteMany (IntCol) values (:1)"
        self.cursor.executemany(statement, rows[:50])
        self.cursor.executemany(statement, rows[50:])
        self.connection.commit()
        self.cursor.execute("select count(*) from TestExecuteMany")
        count, = self.cursor.fetchone()
        self.failUnlessEqual(count, len(rows))

    def testExecuteManyWithResize(self):
        """test executing a statement multiple times (with resize)"""
        self.cursor.execute("truncate table TestExecuteMany")
        rows = [ ( 1, "First" ),
                 ( 2, "Second" ),
                 ( 3, "Third" ),
                 ( 4, "Fourth" ),
                 ( 5, "Fifth" ),
                 ( 6, "Sixth" ),
                 ( 7, "Seventh" ) ]
        self.cursor.bindarraysize = 5
        self.cursor.setinputsizes(int, 100)
        sql = "insert into TestExecuteMany (IntCol, StringCol) values (:1, :2)"
        self.cursor.executemany(sql, rows)
        var = self.cursor.bindvars[1]
        self.cursor.execute("select count(*) from TestExecuteMany")
        count, = self.cursor.fetchone()
        self.failUnlessEqual(count, len(rows))
        self.failUnlessEqual(var.maxlength,
                100 * self.connection.maxBytesPerCharacter)

    def testExecuteManyWithExecption(self):
        """test executing a statement multiple times (with exception)"""
        self.cursor.execute("truncate table TestExecuteMany")
        rows = [ { "value" : n } for n in (1, 2, 3, 2, 5) ]
        statement = "insert into TestExecuteMany (IntCol) values (:value)"
        self.failUnlessRaises(cx_Oracle.DatabaseError, self.cursor.executemany,
                statement, rows)
        self.failUnlessEqual(self.cursor.rowcount, 3)

    def testPrepare(self):
        """test preparing a statement and executing it multiple times"""
        self.failUnlessEqual(self.cursor.statement, None)
        statement = "begin :value := :value + 5; end;"
        self.cursor.prepare(statement)
        var = self.cursor.var(cx_Oracle.NUMBER)
        self.failUnlessEqual(self.cursor.statement, statement)
        var.setvalue(0, 2)
        self.cursor.execute(None, value = var)
        self.failUnlessEqual(var.getvalue(), 7)
        self.cursor.execute(None, value = var)
        self.failUnlessEqual(var.getvalue(), 12)
        self.cursor.execute("begin :value2 := 3; end;", value2 = var)
        self.failUnlessEqual(var.getvalue(), 3)

    def testExceptionOnClose(self):
        "confirm an exception is raised after closing a cursor"
        self.cursor.close()
        self.failUnlessRaises(cx_Oracle.InterfaceError, self.cursor.execute,
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
        self.failUnlessEqual(rows, [1, 2, 3])

    def testIteratorsInterrupted(self):
        """test iterators (with intermediate execute)"""
        self.cursor.execute("truncate table TestExecuteMany")
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
        self.cursor.execute("insert into TestExecuteMany (IntCol) values (1)")
        if sys.version_info[0] >= 3:
            self.failUnlessRaises(cx_Oracle.InterfaceError, next, testIter) 
        else:
            self.failUnlessRaises(cx_Oracle.InterfaceError, testIter.next) 

    def testBindNames(self):
        """test that bindnames() works correctly."""
        self.failUnlessRaises(cx_Oracle.ProgrammingError,
                self.cursor.bindnames)
        self.cursor.prepare("begin null; end;")
        self.failUnlessEqual(self.cursor.bindnames(), [])
        self.cursor.prepare("begin :retval := :inval + 5; end;")
        self.failUnlessEqual(self.cursor.bindnames(), ["RETVAL", "INVAL"])
        self.cursor.prepare("begin :retval := :a * :a + :b * :b; end;")
        self.failUnlessEqual(self.cursor.bindnames(), ["RETVAL", "A", "B"])
        self.cursor.prepare("begin :a := :b + :c + :d + :e + :f + :g + " + \
                ":h + :i + :j + :k + :l; end;")
        self.failUnlessEqual(self.cursor.bindnames(),
                ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"])

    def testBadPrepare(self):
        """test that subsequent executes succeed after bad prepare"""
        self.failUnlessRaises(cx_Oracle.DatabaseError,
                self.cursor.execute,
                "begin raise_application_error(-20000, 'this); end;")
        self.cursor.execute("begin null; end;")

    def testBadExecute(self):
        """test that subsequent fetches fail after bad execute"""
        self.failUnlessRaises(cx_Oracle.DatabaseError,
                self.cursor.execute, "select y from dual")
        self.failUnlessRaises(cx_Oracle.InterfaceError,
                self.cursor.fetchall)

    def testSetInputSizesMultipleMethod(self):
        """test setting input sizes with both positional and keyword args"""
        self.failUnlessRaises(cx_Oracle.InterfaceError,
                self.cursor.setinputsizes, 5, x = 5)

    def testSetInputSizesByPosition(self):
        """test setting input sizes with positional args"""
        var = self.cursor.var(cx_Oracle.STRING, 100)
        self.cursor.setinputsizes(None, 5, None, 10, None, cx_Oracle.NUMBER)
        self.cursor.execute("""
                begin
                  :1 := :2 || to_char(:3) || :4 || to_char(:5) || to_char(:6);
                end;""", [var, 'test_', 5, '_second_', 3, 7])
        self.failUnlessEqual(var.getvalue(), "test_5_second_37")

