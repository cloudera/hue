# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# Portions Copyright 2007-2015, Anthony Tuininga. All rights reserved.
#
# Portions Copyright 2001-2007, Computronix (Canada) Ltd., Edmonton, Alberta,
# Canada. All rights reserved.
#------------------------------------------------------------------------------

"""Module for testing string variables."""

import TestEnv

import cx_Oracle
import datetime
import string
import random

class TestCase(TestEnv.BaseTestCase):

    def setUp(self):
        TestEnv.BaseTestCase.setUp(self)
        self.rawData = []
        self.dataByKey = {}
        for i in range(1, 11):
            stringCol = "String %d" % i
            fixedCharCol = ("Fixed Char %d" % i).ljust(40)
            rawCol = ("Raw %d" % i).encode("ascii")
            if i % 2:
                nullableCol = "Nullable %d" % i
            else:
                nullableCol = None
            dataTuple = (i, stringCol, rawCol, fixedCharCol, nullableCol)
            self.rawData.append(dataTuple)
            self.dataByKey[i] = dataTuple

    def testArrayWithIncreasedSize(self):
        "test creating an array var and then increasing the internal size"
        val = ["12345678901234567890"] * 3
        arrayVar = self.cursor.arrayvar(str, len(val), 4)
        arrayVar.setvalue(0, val)
        self.assertEqual(arrayVar.getvalue(), val)

    def testBindString(self):
        "test binding in a string"
        self.cursor.execute("""
                select * from TestStrings
                where StringCol = :value""",
                value = "String 5")
        self.assertEqual(self.cursor.fetchall(), [self.dataByKey[5]])

    def testBindDifferentVar(self):
        "test binding a different variable on second execution"
        retval_1 = self.cursor.var(cx_Oracle.STRING, 30)
        retval_2 = self.cursor.var(cx_Oracle.STRING, 30)
        self.cursor.execute("begin :retval := 'Called'; end;",
                retval = retval_1)
        self.assertEqual(retval_1.getvalue(), "Called")
        self.cursor.execute("begin :retval := 'Called'; end;",
                retval = retval_2)
        self.assertEqual(retval_2.getvalue(), "Called")

    def testExceedsNumElements(self):
        "test exceeding the number of elements returns IndexError"
        var = self.cursor.var(str)
        self.assertRaises(IndexError, var.getvalue, 1)

    def testBindStringAfterNumber(self):
        "test binding in a string after setting input sizes to a number"
        self.cursor.setinputsizes(value = cx_Oracle.NUMBER)
        self.cursor.execute("""
                select * from TestStrings
                where StringCol = :value""",
                value = "String 6")
        self.assertEqual(self.cursor.fetchall(), [self.dataByKey[6]])

    def testBindStringArrayDirect(self):
        "test binding in a string array"
        returnValue = self.cursor.var(cx_Oracle.NUMBER)
        array = [r[1] for r in self.rawData]
        statement = """
                begin
                  :returnValue := pkg_TestStringArrays.TestInArrays(
                      :integerValue, :array);
                end;"""
        self.cursor.execute(statement,
                returnValue = returnValue,
                integerValue = 5,
                array = array)
        self.assertEqual(returnValue.getvalue(), 86)
        array = [ "String - %d" % i for i in range(15) ]
        self.cursor.execute(statement,
                integerValue = 8,
                array = array)
        self.assertEqual(returnValue.getvalue(), 163)

    def testBindStringArrayBySizes(self):
        "test binding in a string array (with setinputsizes)"
        returnValue = self.cursor.var(cx_Oracle.NUMBER)
        self.cursor.setinputsizes(array = [cx_Oracle.STRING, 10])
        array = [r[1] for r in self.rawData]
        self.cursor.execute("""
                begin
                  :returnValue := pkg_TestStringArrays.TestInArrays(
                      :integerValue, :array);
                end;""",
                returnValue = returnValue,
                integerValue = 6,
                array = array)
        self.assertEqual(returnValue.getvalue(), 87)

    def testBindStringArrayByVar(self):
        "test binding in a string array (with arrayvar)"
        returnValue = self.cursor.var(cx_Oracle.NUMBER)
        array = self.cursor.arrayvar(cx_Oracle.STRING, 10, 20)
        array.setvalue(0, [r[1] for r in self.rawData])
        self.cursor.execute("""
                begin
                  :returnValue := pkg_TestStringArrays.TestInArrays(
                      :integerValue, :array);
                end;""",
                returnValue = returnValue,
                integerValue = 7,
                array = array)
        self.assertEqual(returnValue.getvalue(), 88)

    def testBindInOutStringArrayByVar(self):
        "test binding in/out a string array (with arrayvar)"
        array = self.cursor.arrayvar(cx_Oracle.STRING, 10, 100)
        originalData = [r[1] for r in self.rawData]
        expectedData = ["Converted element # %d originally had length %d" % \
                (i, len(originalData[i - 1])) for i in range(1, 6)] + \
                originalData[5:]
        array.setvalue(0, originalData)
        self.cursor.execute("""
                begin
                  pkg_TestStringArrays.TestInOutArrays(:numElems, :array);
                end;""",
                numElems = 5,
                array = array)
        self.assertEqual(array.getvalue(), expectedData)

    def testBindOutStringArrayByVar(self):
        "test binding out a string array (with arrayvar)"
        array = self.cursor.arrayvar(cx_Oracle.STRING, 6, 100)
        expectedData = ["Test out element # %d" % i for i in range(1, 7)]
        self.cursor.execute("""
                begin
                  pkg_TestStringArrays.TestOutArrays(:numElems, :array);
                end;""",
                numElems = 6,
                array = array)
        self.assertEqual(array.getvalue(), expectedData)

    def testBindRaw(self):
        "test binding in a raw"
        self.cursor.setinputsizes(value = cx_Oracle.BINARY)
        self.cursor.execute("""
                select * from TestStrings
                where RawCol = :value""",
                value = "Raw 4".encode("ascii"))
        self.assertEqual(self.cursor.fetchall(), [self.dataByKey[4]])

    def testBindAndFetchRowid(self):
        "test binding (and fetching) a rowid"
        self.cursor.execute("""
                select rowid
                from TestStrings
                where IntCol = 3""")
        rowid, = self.cursor.fetchone()
        self.cursor.execute("""
                select *
                from TestStrings
                where rowid = :value""",
                value = rowid)
        self.assertEqual(self.cursor.fetchall(), [self.dataByKey[3]])

    def testBindAndFetchUniversalRowids(self):
        "test binding (and fetching) universal rowids"
        self.cursor.execute("truncate table TestUniversalRowids")
        data = [
            (1, "ABC" * 75, datetime.datetime(2017, 4, 11)),
            (2, "DEF" * 80, datetime.datetime(2017, 4, 12))
        ]
        for row in data:
            self.cursor.execute("""
                    insert into TestUniversalRowids
                    values (:1, :2, :3)""", row)
        self.connection.commit()
        self.cursor.execute("""
                select rowid
                from TestUniversalRowIds
                order by IntCol""")
        rowids = [r for r, in self.cursor]
        fetchedData = []
        for rowid in rowids:
            self.cursor.execute("""
                    select *
                    from TestUniversalRowids
                    where rowid = :rid""",
                    rid = rowid)
            fetchedData.extend(self.cursor.fetchall())
        self.assertEqual(fetchedData, data)

    def testBindNull(self):
        "test binding in a null"
        self.cursor.execute("""
                select * from TestStrings
                where StringCol = :value""",
                value = None)
        self.assertEqual(self.cursor.fetchall(), [])

    def testBindOutSetInputSizesByType(self):
        "test binding out with set input sizes defined (by type)"
        vars = self.cursor.setinputsizes(value = cx_Oracle.STRING)
        self.cursor.execute("""
                begin
                  :value := 'TSI';
                end;""")
        self.assertEqual(vars["value"].getvalue(), "TSI")

    def testBindOutSetInputSizesByInteger(self):
        "test binding out with set input sizes defined (by integer)"
        vars = self.cursor.setinputsizes(value = 30)
        self.cursor.execute("""
                begin
                  :value := 'TSI (I)';
                end;""")
        self.assertEqual(vars["value"].getvalue(), "TSI (I)")

    def testBindInOutSetInputSizesByType(self):
        "test binding in/out with set input sizes defined (by type)"
        vars = self.cursor.setinputsizes(value = cx_Oracle.STRING)
        self.cursor.execute("""
                begin
                  :value := :value || ' TSI';
                end;""",
                value = "InVal")
        self.assertEqual(vars["value"].getvalue(), "InVal TSI")

    def testBindInOutSetInputSizesByInteger(self):
        "test binding in/out with set input sizes defined (by integer)"
        vars = self.cursor.setinputsizes(value = 30)
        self.cursor.execute("""
                begin
                  :value := :value || ' TSI (I)';
                end;""",
                value = "InVal")
        self.assertEqual(vars["value"].getvalue(), "InVal TSI (I)")

    def testBindOutVar(self):
        "test binding out with cursor.var() method"
        var = self.cursor.var(cx_Oracle.STRING)
        self.cursor.execute("""
                begin
                  :value := 'TSI (VAR)';
                end;""",
                value = var)
        self.assertEqual(var.getvalue(), "TSI (VAR)")

    def testBindInOutVarDirectSet(self):
        "test binding in/out with cursor.var() method"
        var = self.cursor.var(cx_Oracle.STRING)
        var.setvalue(0, "InVal")
        self.cursor.execute("""
                begin
                  :value := :value || ' TSI (VAR)';
                end;""",
                value = var)
        self.assertEqual(var.getvalue(), "InVal TSI (VAR)")

    def testBindLongString(self):
        "test that binding a long string succeeds"
        self.cursor.setinputsizes(bigString = cx_Oracle.LONG_STRING)
        self.cursor.execute("""
                declare
                  t_Temp varchar2(20000);
                begin
                  t_Temp := :bigString;
                end;""",
                bigString = "X" * 10000)

    def testBindLongStringAfterSettingSize(self):
        "test that setinputsizes() returns a long variable"
        var = self.cursor.setinputsizes(test = 90000)["test"]
        inString = "1234567890" * 9000
        var.setvalue(0, inString)
        outString = var.getvalue()
        self.assertEqual(inString, outString,
                "output does not match: in was %d, out was %d" % \
                (len(inString), len(outString)))

    def testCursorDescription(self):
        "test cursor description is accurate"
        self.cursor.execute("select * from TestStrings")
        self.assertEqual(self.cursor.description,
                [ ('INTCOL', cx_Oracle.NUMBER, 10, None, 9, 0, 0),
                  ('STRINGCOL', cx_Oracle.STRING, 20,
                        20 * TestEnv.GetCharSetRatio(), None,
                    None, 0),
                  ('RAWCOL', cx_Oracle.BINARY, 30, 30, None, None, 0),
                  ('FIXEDCHARCOL', cx_Oracle.FIXED_CHAR, 40,
                        40 * TestEnv.GetCharSetRatio(),
                    None, None, 0),
                  ('NULLABLECOL', cx_Oracle.STRING, 50,
                        50 * TestEnv.GetCharSetRatio(), None,
                    None, 1) ])

    def testFetchAll(self):
        "test that fetching all of the data returns the correct results"
        self.cursor.execute("select * From TestStrings order by IntCol")
        self.assertEqual(self.cursor.fetchall(), self.rawData)
        self.assertEqual(self.cursor.fetchall(), [])

    def testFetchMany(self):
        "test that fetching data in chunks returns the correct results"
        self.cursor.execute("select * From TestStrings order by IntCol")
        self.assertEqual(self.cursor.fetchmany(3), self.rawData[0:3])
        self.assertEqual(self.cursor.fetchmany(2), self.rawData[3:5])
        self.assertEqual(self.cursor.fetchmany(4), self.rawData[5:9])
        self.assertEqual(self.cursor.fetchmany(3), self.rawData[9:])
        self.assertEqual(self.cursor.fetchmany(3), [])

    def testFetchOne(self):
        "test that fetching a single row returns the correct results"
        self.cursor.execute("""
                select *
                from TestStrings
                where IntCol in (3, 4)
                order by IntCol""")
        self.assertEqual(self.cursor.fetchone(), self.dataByKey[3])
        self.assertEqual(self.cursor.fetchone(), self.dataByKey[4])
        self.assertEqual(self.cursor.fetchone(), None)

    def testSupplementalCharacters(self):
        "test that binding and fetching supplemental charcters works correctly"
        self.cursor.execute("""
                select value
                from nls_database_parameters
                where parameter = 'NLS_CHARACTERSET'""")
        charset, = self.cursor.fetchone()
        if charset != "AL32UTF8":
            self.skipTest("Database character set must be AL32UTF8")
        supplementalChars = "𠜎 𠜱 𠝹 𠱓 𠱸 𠲖 𠳏 𠳕 𠴕 𠵼 𠵿 𠸎 𠸏 𠹷 𠺝 " \
                "𠺢 𠻗 𠻹 𠻺 𠼭 𠼮 𠽌 𠾴 𠾼 𠿪 𡁜 𡁯 𡁵 𡁶 𡁻 𡃁 𡃉 𡇙 𢃇 " \
                "𢞵 𢫕 𢭃 𢯊 𢱑 𢱕 𢳂 𢴈 𢵌 𢵧 𢺳 𣲷 𤓓 𤶸 𤷪 𥄫 𦉘 𦟌 𦧲 " \
                "𦧺 𧨾 𨅝 𨈇 𨋢 𨳊 𨳍 𨳒 𩶘"
        self.cursor.execute("truncate table TestTempTable")
        self.cursor.execute("""
                insert into TestTempTable (IntCol, StringCol)
                values (:1, :2)""",
                (1, supplementalChars))
        self.connection.commit()
        self.cursor.execute("select StringCol from TestTempTable")
        value, = self.cursor.fetchone()
        self.assertEqual(value, supplementalChars)

    def testBindTwiceWithLargeStringSecond(self):
        "test binding twice with a larger string the second time"
        self.cursor.execute("truncate table TestTempTable")
        sql = "insert into TestTempTable (IntCol, StringCol) values (:1, :2)"
        shortString = "short string"
        longString = "long string " * 30
        self.cursor.execute(sql, (1, shortString))
        self.cursor.execute(sql, (2, longString))
        self.connection.commit()
        self.cursor.execute("""
                select IntCol, StringCol
                from TestTempTable
                order by IntCol""")
        self.assertEqual(self.cursor.fetchall(),
                [(1, shortString), (2, longString)])

    def testIssue50(self):
        "test issue 50 - avoid error ORA-24816"
        cursor = self.connection.cursor()
        try:
            cursor.execute("drop table issue_50 purge")
        except cx_Oracle.DatabaseError:
            pass
        cursor.execute("""
                create table issue_50 (
                    Id          number(11) primary key,
                    Str1        nvarchar2(256),
                    Str2        nvarchar2(256),
                    Str3        nvarchar2(256),
                    NClob1      nclob,
                    NClob2      nclob
                )""")
        idVar = cursor.var(cx_Oracle.NUMBER)
        cursor.execute("""
                insert into issue_50 (Id, Str2, Str3, NClob1, NClob2, Str1)
                values (:arg0, :arg1, :arg2, :arg3, :arg4, :arg5)
                returning id into :arg6""",
                [1, '555a4c78', 'f319ef0e', '23009914', '', '', idVar])
        cursor = self.connection.cursor()
        cursor.execute("""
                insert into issue_50 (Id, Str2, Str3, NClob1, NClob2, Str1)
                values (:arg0, :arg1, :arg2, :arg3, :arg4, :arg5)
                returning id into :arg6""",
                [2, u'd5ff845a', u'94275767', u'bf161ff6', u'', u'', idVar])
        cursor.execute("drop table issue_50 purge")

    def testSetRowidToString(self):
        "test assigning a string to rowid"
        var = self.cursor.var(cx_Oracle.ROWID)
        self.assertRaises(cx_Oracle.NotSupportedError, var.setvalue, 0,
                "ABDHRYTHFJGKDKKDH")

    def testShortXMLAsString(self):
        "test fetching XMLType object as a string"
        self.cursor.execute("""
                select XMLElement("string", stringCol)
                from TestStrings
                where intCol = 1""")
        actualValue, = self.cursor.fetchone()
        expectedValue = "<string>String 1</string>"
        self.assertEqual(actualValue, expectedValue)

    def testLongXMLAsString(self):
        "test inserting and fetching an XMLType object (1K) as a string"
        chars = string.ascii_uppercase + string.ascii_lowercase
        randomString = ''.join(random.choice(chars) for _ in range(1024))
        intVal = 200
        xmlString = '<data>' + randomString + '</data>'
        self.cursor.execute("""
                insert into TestXML (IntCol, XMLCol)
                values (:1, :2)""", (intVal, xmlString))
        self.cursor.execute("select XMLCol from TestXML where intCol = :1",
                (intVal,))
        actualValue, = self.cursor.fetchone()
        self.assertEqual(actualValue.strip(), xmlString)

if __name__ == "__main__":
    TestEnv.RunTestCases()

