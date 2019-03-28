#------------------------------------------------------------------------------
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# Portions Copyright 2007-2015, Anthony Tuininga. All rights reserved.
#
# Portions Copyright 2001-2007, Computronix (Canada) Ltd., Edmonton, Alberta,
# Canada. All rights reserved.
#------------------------------------------------------------------------------

"""Module for testing long and long raw variables."""

import TestEnv

import cx_Oracle
import sys

class TestCase(TestEnv.BaseTestCase):

    def __PerformTest(self, a_Type, a_InputType):
        self.cursor.execute("truncate table Test%ss" % a_Type)
        longString = ""
        for i in range(1, 11):
            char = chr(ord('A') + i - 1)
            longString += char * 25000
            self.cursor.setinputsizes(longString = a_InputType)
            if a_Type == "LongRaw" and sys.version_info[0] >= 3:
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
                    )""" % (a_Type, a_Type),
                    integerValue = i,
                    longString = bindValue)
        self.connection.commit()
        self.cursor.execute("""
                select *
                from Test%ss
                order by IntCol""" % a_Type)
        longString = ""
        while 1:
            row = self.cursor.fetchone()
            if row is None:
                break
            integerValue, fetchedValue = row
            char = chr(ord('A') + integerValue - 1)
            longString += char * 25000
            if a_Type == "LongRaw" and sys.version_info[0] >= 3:
                actualValue = longString.encode("ascii")
            else:
                actualValue = longString
            self.assertEqual(len(fetchedValue), integerValue * 25000)
            self.assertEqual(fetchedValue, actualValue)

    def testLongs(self):
        "test binding and fetching long data"
        self.__PerformTest("Long", cx_Oracle.LONG_STRING)

    def testLongWithExecuteMany(self):
        "test binding long data with executemany()"
        data = []
        self.cursor.execute("truncate table TestLongs")
        for i in range(5):
            char = chr(ord('A') + i)
            longStr = char * (32768 * (i + 1))
            data.append((i + 1, longStr))
        self.cursor.executemany("insert into TestLongs values (:1, :2)", data)
        self.connection.commit()
        self.cursor.execute("select * from TestLongs order by IntCol")
        fetchedData = self.cursor.fetchall()
        self.assertEqual(fetchedData, data)

    def testLongRaws(self):
        "test binding and fetching long raw data"
        self.__PerformTest("LongRaw", cx_Oracle.LONG_BINARY)

    def testLongCursorDescription(self):
        "test cursor description is accurate for longs"
        self.cursor.execute("select * from TestLongs")
        self.assertEqual(self.cursor.description,
                [ ('INTCOL', cx_Oracle.NUMBER, 10, None, 9, 0, 0),
                  ('LONGCOL', cx_Oracle.LONG_STRING, None, None, None, None,
                        0) ])

    def testLongRawCursorDescription(self):
        "test cursor description is accurate for long raws"
        self.cursor.execute("select * from TestLongRaws")
        self.assertEqual(self.cursor.description,
                [ ('INTCOL', cx_Oracle.NUMBER, 10, None, 9, 0, 0),
                  ('LONGRAWCOL', cx_Oracle.LONG_BINARY, None, None, None, None,
                        0) ])

    def testArraySizeTooLarge(self):
        "test array size too large generates an exception"
        self.cursor.arraysize = 268435456
        self.assertRaises(cx_Oracle.DatabaseError, self.cursor.execute,
                "select * from TestLongRaws")

if __name__ == "__main__":
    TestEnv.RunTestCases()

