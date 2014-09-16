"""Module for testing LOB (CLOB and BLOB) variables."""

class TestLobVar(BaseTestCase):

    def __PerformTest(self, type, inputType):
        if type.endswith("CLOB"):
            longString = u""
        else:
            longString = ""
        directType = getattr(cx_Oracle, type)
        self.cursor.execute(u"truncate table Test%ss" % type)
        for i in range(0, 11):
            if i > 0:
                if type.endswith("CLOB"):
                    char = unichr(ord('A') + i - 1)
                else:
                    char = chr(ord('A') + i - 1)
                longString += char * 25000
            elif inputType != directType:
                continue
            self.cursor.setinputsizes(longString = inputType)
            self.cursor.execute(u"""
                    insert into Test%ss (
                      IntCol,
                      %sCol
                    ) values (
                      :integerValue,
                      :longString
                    )""" % (type, type),
                    integerValue = i,
                    longString = longString)
        self.connection.commit()
        self.cursor.execute(u"""
                select *
                from Test%ss
                order by IntCol""" % type)
        longString = ""
        for row in self.cursor:
            integerValue, lob = row
            if integerValue == 0:
                self.failUnlessEqual(lob.size(), 0)
                self.failUnlessEqual(lob.read(), "")
            else:
                if type.endswith("CLOB"):
                    char = unichr(ord('A') + integerValue - 1)
                    prevChar = unichr(ord('A') + integerValue - 2)
                    actualValue = unicode(lob)
                else:
                    char = chr(ord('A') + integerValue - 1)
                    prevChar = chr(ord('A') + integerValue - 2)
                    actualValue = str(lob)
                longString += char * 25000
                self.failUnlessEqual(lob.size(), len(longString))
                self.failUnlessEqual(lob.read(), longString)
                self.failUnlessEqual(actualValue, longString)
                self.failUnlessEqual(lob.read(len(longString)), char)
            if integerValue > 1:
                offset = (integerValue - 1) * 25000 - 4
                string = prevChar * 5 + char * 5
                self.failUnlessEqual(lob.read(offset, 10), string)

    def __TestTrim(self, type):
        self.cursor.execute(u"truncate table Test%ss" % type)
        self.cursor.setinputsizes(longString = getattr(cx_Oracle, type))
        longString = "X" * 75000
        if type.endswith("CLOB"):
            longString = unicode(longString)
        self.cursor.execute(u"""
                insert into Test%ss (
                  IntCol,
                  %sCol
                ) values (
                  :integerValue,
                  :longString
                )""" % (type, type),
                integerValue = 1,
                longString = longString)
        self.cursor.execute(u"""
                select %sCol
                from Test%ss
                where IntCol = 1""" % (type, type))
        lob, = self.cursor.fetchone()
        self.failUnlessEqual(lob.size(), 75000)
        lob.trim(25000)
        self.failUnlessEqual(lob.size(), 25000)
        lob.trim()
        self.failUnlessEqual(lob.size(), 0)

    def testBLOBCursorDescription(self):
        "test cursor description is accurate for BLOBs"
        self.cursor.execute(u"select * from TestBLOBs")
        self.failUnlessEqual(self.cursor.description,
                [ (u'INTCOL', cx_Oracle.NUMBER, 10, 22, 9, 0, 0),
                  (u'BLOBCOL', cx_Oracle.BLOB, -1, 4000, 0, 0, 0) ])

    def testBLOBsDirect(self):
        "test binding and fetching BLOB data (directly)"
        self.__PerformTest("BLOB", cx_Oracle.BLOB)

    def testBLOBsIndirect(self):
        "test binding and fetching BLOB data (indirectly)"
        self.__PerformTest("BLOB", cx_Oracle.LONG_BINARY)

    def testBLOBTrim(self):
        "test trimming a BLOB"
        self.__TestTrim("BLOB")

    def testCLOBCursorDescription(self):
        "test cursor description is accurate for CLOBs"
        self.cursor.execute(u"select * from TestCLOBs")
        self.failUnlessEqual(self.cursor.description,
                [ (u'INTCOL', cx_Oracle.NUMBER, 10, 22, 9, 0, 0),
                  (u'CLOBCOL', cx_Oracle.CLOB, -1, 4000, 0, 0, 0) ])

    def testCLOBsDirect(self):
        "test binding and fetching CLOB data (directly)"
        self.__PerformTest("CLOB", cx_Oracle.CLOB)

    def testCLOBsIndirect(self):
        "test binding and fetching CLOB data (indirectly)"
        self.__PerformTest("CLOB", cx_Oracle.LONG_STRING)

    def testCLOBTrim(self):
        "test trimming a CLOB"
        self.__TestTrim("CLOB")

    def testMultipleFetch(self):
        "test retrieving data from a CLOB after multiple fetches"
        self.cursor.arraysize = 1
        self.cursor.execute(u"select CLOBCol from TestCLOBS")
        rows = self.cursor.fetchall()
        self.failUnlessRaises(cx_Oracle.ProgrammingError, rows[1][0].read)

    def testNCLOBCursorDescription(self):
        "test cursor description is accurate for NCLOBs"
        self.cursor.execute(u"select * from TestNCLOBs")
        self.failUnlessEqual(self.cursor.description,
                [ (u'INTCOL', cx_Oracle.NUMBER, 10, 22, 9, 0, 0),
                  (u'NCLOBCOL', cx_Oracle.NCLOB, -1, 4000, 0, 0, 0) ])

    def testNCLOBsDirect(self):
        "test binding and fetching NCLOB data (directly)"
        self.__PerformTest("NCLOB", cx_Oracle.NCLOB)

    def testNCLOBsIndirect(self):
        "test binding and fetching NCLOB data (indirectly)"
        self.__PerformTest("NCLOB", cx_Oracle.LONG_STRING)

    def testNCLOBTrim(self):
        "test trimming a NCLOB"
        self.__TestTrim("NCLOB")

