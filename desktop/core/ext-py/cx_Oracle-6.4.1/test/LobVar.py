#------------------------------------------------------------------------------
# Copyright 2016, 2017, Oracle and/or its affiliates. All rights reserved.
#
# Portions Copyright 2007-2015, Anthony Tuininga. All rights reserved.
#
# Portions Copyright 2001-2007, Computronix (Canada) Ltd., Edmonton, Alberta,
# Canada. All rights reserved.
#------------------------------------------------------------------------------

"""Module for testing LOB (CLOB and BLOB) variables."""

import sys

class TestLobVar(BaseTestCase):

    def __GetTempLobs(self, sid):
        cursor = self.connection.cursor()
        cursor.execute("""
                select abstract_lobs
                from v$temporary_lobs
                where sid = :sid""", sid = sid)
        row = cursor.fetchone()
        if row is None:
            return 0
        return int(row[0])

    def __PerformTest(self, lobType, inputType):
        longString = ""
        directType = getattr(cx_Oracle, lobType)
        self.cursor.execute("truncate table Test%ss" % lobType)
        for i in range(0, 11):
            if i > 0:
                char = chr(ord('A') + i - 1)
                longString += char * 25000
            elif inputType != directType:
                continue
            self.cursor.setinputsizes(longString = inputType)
            if lobType == "BLOB" and sys.version_info[0] >= 3:
                bindValue = longString.encode("ascii")
            else:
                bindValue = longString
            self.cursor.execute("""
                    insert into Test%ss (
                      IntCol,
                      %sCol
                    ) values (
                      :integerValue,
                      :longString
                    )""" % (lobType, lobType),
                    integerValue = i,
                    longString = bindValue)
        self.connection.commit()
        self.cursor.execute("""
                select *
                from Test%ss
                order by IntCol""" % lobType)
        self.__ValidateQuery(self.cursor, lobType)

    def __TestLobOperations(self, lobType):
        self.cursor.execute("truncate table Test%ss" % lobType)
        self.cursor.setinputsizes(longString = getattr(cx_Oracle, lobType))
        longString = "X" * 75000
        writeValue = "TEST"
        if lobType == "BLOB" and sys.version_info[0] >= 3:
            longString = longString.encode("ascii")
            writeValue = writeValue.encode("ascii")
        self.cursor.execute("""
                insert into Test%ss (
                  IntCol,
                  %sCol
                ) values (
                  :integerValue,
                  :longString
                )""" % (lobType, lobType),
                integerValue = 1,
                longString = longString)
        self.cursor.execute("""
                select %sCol
                from Test%ss
                where IntCol = 1""" % (lobType, lobType))
        lob, = self.cursor.fetchone()
        self.assertEqual(lob.isopen(), False)
        lob.open()
        self.assertEqual(lob.isopen(), True)
        lob.close()
        self.assertEqual(lob.isopen(), False)
        self.assertEqual(lob.size(), 75000)
        lob.write(writeValue, 75001)
        self.assertEqual(lob.size(), 75000 + len(writeValue))
        self.assertEqual(lob.read(), longString + writeValue)
        lob.write(writeValue, 1)
        self.assertEqual(lob.read(), writeValue + longString[4:] + writeValue)
        lob.trim(25000)
        self.assertEqual(lob.size(), 25000)
        lob.trim()
        self.assertEqual(lob.size(), 0)

    def __TestTemporaryLOB(self, lobType):
        self.cursor.execute("truncate table Test%ss" % lobType)
        value = "A test string value"
        if lobType == "BLOB" and sys.version_info[0] >= 3:
            value = value.encode("ascii")
        lobTypeObj = getattr(cx_Oracle, lobType)
        lob = self.connection.createlob(lobTypeObj)
        lob.write(value)
        self.cursor.execute("""
                insert into Test%ss (IntCol, %sCol)
                values (:intVal, :lobVal)""" % (lobType, lobType),
                intVal = 1,
                lobVal = lob)
        self.cursor.execute("select %sCol from Test%ss" % (lobType, lobType))
        lob, = self.cursor.fetchone()
        self.assertEqual(lob.read(), value)

    def __ValidateQuery(self, rows, lobType):
        longString = ""
        for row in rows:
            integerValue, lob = row
            if integerValue == 0:
                self.assertEqual(lob.size(), 0)
                expectedValue = ""
                if lobType == "BLOB" and sys.version_info[0] >= 3:
                    expectedValue = expectedValue.encode("ascii")
                self.assertEqual(lob.read(), expectedValue)
            else:
                char = chr(ord('A') + integerValue - 1)
                prevChar = chr(ord('A') + integerValue - 2)
                longString += char * 25000
                if lobType == "BLOB" and sys.version_info[0] >= 3:
                    actualValue = longString.encode("ascii")
                    char = char.encode("ascii")
                    prevChar = prevChar.encode("ascii")
                else:
                    actualValue = longString
                self.assertEqual(lob.size(), len(actualValue))
                self.assertEqual(lob.read(), actualValue)
                if lobType == "CLOB":
                    self.assertEqual(str(lob), actualValue)
                self.assertEqual(lob.read(len(actualValue)), char)
            if integerValue > 1:
                offset = (integerValue - 1) * 25000 - 4
                string = prevChar * 5 + char * 5
                self.assertEqual(lob.read(offset, 10), string)

    def testBindLobValue(self):
        "test binding a LOB value directly"
        self.cursor.execute("truncate table TestCLOBs")
        self.cursor.execute("insert into TestCLOBs values (1, 'Short value')")
        self.cursor.execute("select ClobCol from TestCLOBs")
        lob, = self.cursor.fetchone()
        self.cursor.execute("insert into TestCLOBs values (2, :value)",
                value = lob)

    def testBLOBCursorDescription(self):
        "test cursor description is accurate for BLOBs"
        self.cursor.execute("select * from TestBLOBs")
        self.assertEqual(self.cursor.description,
                [ ('INTCOL', cx_Oracle.NUMBER, 10, None, 9, 0, 0),
                  ('BLOBCOL', cx_Oracle.BLOB, None, None, None, None, 0) ])

    def testBLOBsDirect(self):
        "test binding and fetching BLOB data (directly)"
        self.__PerformTest("BLOB", cx_Oracle.BLOB)

    def testBLOBsIndirect(self):
        "test binding and fetching BLOB data (indirectly)"
        self.__PerformTest("BLOB", cx_Oracle.LONG_BINARY)

    def testBLOBOperations(self):
        "test operations on BLOBs"
        self.__TestLobOperations("BLOB")

    def testCLOBCursorDescription(self):
        "test cursor description is accurate for CLOBs"
        self.cursor.execute("select * from TestCLOBs")
        self.assertEqual(self.cursor.description,
                [ ('INTCOL', cx_Oracle.NUMBER, 10, None, 9, 0, 0),
                  ('CLOBCOL', cx_Oracle.CLOB, None, None, None, None, 0) ])

    def testCLOBsDirect(self):
        "test binding and fetching CLOB data (directly)"
        self.__PerformTest("CLOB", cx_Oracle.CLOB)

    def testCLOBsIndirect(self):
        "test binding and fetching CLOB data (indirectly)"
        self.__PerformTest("CLOB", cx_Oracle.LONG_STRING)

    def testCLOBOperations(self):
        "test operations on CLOBs"
        self.__TestLobOperations("CLOB")

    def testCreateBlob(self):
        "test creating a temporary BLOB"
        self.__TestTemporaryLOB("BLOB")

    def testCreateClob(self):
        "test creating a temporary CLOB"
        self.__TestTemporaryLOB("CLOB")

    def testCreateNclob(self):
        "test creating a temporary NCLOB"
        self.__TestTemporaryLOB("NCLOB")

    def testMultipleFetch(self):
        "test retrieving data from a CLOB after multiple fetches"
        self.cursor.arraysize = 1
        self.cursor.execute("select * from TestCLOBS")
        rows = self.cursor.fetchall()
        self.__ValidateQuery(rows, "CLOB")

    def testNCLOBCursorDescription(self):
        "test cursor description is accurate for NCLOBs"
        self.cursor.execute("select * from TestNCLOBs")
        self.assertEqual(self.cursor.description,
                [ ('INTCOL', cx_Oracle.NUMBER, 10, None, 9, 0, 0),
                  ('NCLOBCOL', cx_Oracle.NCLOB, None, None, None, None, 0) ])

    def testNCLOBsDirect(self):
        "test binding and fetching NCLOB data (directly)"
        self.__PerformTest("NCLOB", cx_Oracle.NCLOB)

    def testNCLOBDifferentEncodings(self):
        "test binding and fetching NCLOB data (different encodings)"
        connection = cx_Oracle.connect(USERNAME, PASSWORD, TNSENTRY,
                encoding = "UTF-8", nencoding = "UTF-16")
        value = u"\u03b4\u4e2a"
        cursor = connection.cursor()
        cursor.execute("truncate table TestNCLOBs")
        cursor.setinputsizes(val = cx_Oracle.NCHAR)
        cursor.execute("insert into TestNCLOBs values (1, :val)", val = value)
        cursor.execute("select NCLOBCol from TestNCLOBs")
        nclob, = cursor.fetchone()
        cursor.setinputsizes(val = cx_Oracle.NCHAR)
        cursor.execute("update TestNCLOBs set NCLOBCol = :val",
                val = nclob.read() + value)
        cursor.execute("select NCLOBCol from TestNCLOBs")
        nclob, = cursor.fetchone()
        self.assertEqual(nclob.read(), value + value)

    def testNCLOBsIndirect(self):
        "test binding and fetching NCLOB data (indirectly)"
        self.__PerformTest("NCLOB", cx_Oracle.LONG_STRING)

    def testNCLOBOperations(self):
        "test operations on NCLOBs"
        self.__TestLobOperations("NCLOB")

    def testTemporaryLobs(self):
        "test temporary LOBs"
        cursor = self.connection.cursor()
        cursor.arraysize = self.cursor.arraysize
        cursor.execute("""
                select sid
                from v$session
                where audsid = userenv('sessionid')""")
        sid, = cursor.fetchone()
        tempLobs = self.__GetTempLobs(sid)
        self.assertEqual(tempLobs, 0)
        cursor.execute("""
                select extract(xmlcol, '/').getclobval()
                from TestXML""")
        for lob, in cursor:
            value = lob.read()
            del lob
        cursor.close()
        tempLobs = self.__GetTempLobs(sid)
        self.assertEqual(tempLobs, 0)

    def testAssignStringBeyondArraySize(self):
        "test assign string to NCLOB beyond array size"
        nclobVar = self.cursor.var(cx_Oracle.NCLOB)
        self.assertRaises(IndexError, nclobVar.setvalue, 1, "test char")

