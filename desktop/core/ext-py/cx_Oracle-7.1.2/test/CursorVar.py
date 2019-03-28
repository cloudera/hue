#------------------------------------------------------------------------------
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# Portions Copyright 2007-2015, Anthony Tuininga. All rights reserved.
#
# Portions Copyright 2001-2007, Computronix (Canada) Ltd., Edmonton, Alberta,
# Canada. All rights reserved.
#------------------------------------------------------------------------------

"""Module for testing cursor variables."""

import TestEnv

import cx_Oracle
import sys

class TestCase(TestEnv.BaseTestCase):

    def testBindCursor(self):
        "test binding in a cursor"
        cursor = self.connection.cursor()
        self.assertEqual(cursor.description, None)
        self.cursor.execute("""
                begin
                  open :cursor for select 'X' StringValue from dual;
                end;""",
                cursor = cursor)
        self.assertEqual(cursor.description,
                [ ('STRINGVALUE', cx_Oracle.FIXED_CHAR, 1,
                        TestEnv.GetCharSetRatio(), None, None, 1) ])
        self.assertEqual(cursor.fetchall(), [('X',)])

    def testBindCursorInPackage(self):
        "test binding in a cursor from a package"
        cursor = self.connection.cursor()
        self.assertEqual(cursor.description, None)
        self.cursor.callproc("pkg_TestRefCursors.TestOutCursor", (2, cursor))
        self.assertEqual(cursor.description,
                [ ('INTCOL', cx_Oracle.NUMBER, 10, None, 9, 0, 0),
                  ('STRINGCOL', cx_Oracle.STRING, 20, 20 *
                        TestEnv.GetCharSetRatio(), None, None, 0) ])
        self.assertEqual(cursor.fetchall(),
                [ (1, 'String 1'), (2, 'String 2') ])

    def testBindSelf(self):
        "test that binding the cursor itself is not supported"
        cursor = self.connection.cursor()
        sql = """
                begin
                    open :pcursor for
                        select 1 from dual;
                end;"""
        self.assertRaises(cx_Oracle.DatabaseError, cursor.execute, sql,
                pcursor = cursor)

    def testExecuteAfterClose(self):
        "test executing a statement returning a ref cursor after closing it"
        outCursor = self.connection.cursor()
        sql = """
                begin
                    open :pcursor for
                    select IntCol
                    from TestNumbers
                    order by IntCol;
                end;"""
        self.cursor.execute(sql, pcursor = outCursor)
        rows = outCursor.fetchall()
        outCursor.close()
        outCursor = self.connection.cursor()
        self.cursor.execute(sql, pcursor = outCursor)
        rows2 = outCursor.fetchall()
        self.assertEqual(rows, rows2)

    def testFetchCursor(self):
        "test fetching a cursor"
        self.cursor.execute("""
                select
                  IntCol,
                  cursor(select IntCol + 1 from dual) CursorValue
                from TestNumbers
                order by IntCol""")
        self.assertEqual(self.cursor.description,
                [ ('INTCOL', cx_Oracle.NUMBER, 10, None, 9, 0, 0),
                  ('CURSORVALUE', cx_Oracle.CURSOR, None, None, None, None,
                        1) ])
        for i in range(1, 11):
            number, cursor = self.cursor.fetchone()
            self.assertEqual(number, i)
            self.assertEqual(cursor.fetchall(), [(i + 1,)])

if __name__ == "__main__":
    TestEnv.RunTestCases()

