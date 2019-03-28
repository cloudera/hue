#------------------------------------------------------------------------------
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# Portions Copyright 2007-2015, Anthony Tuininga. All rights reserved.
#
# Portions Copyright 2001-2007, Computronix (Canada) Ltd., Edmonton, Alberta,
# Canada. All rights reserved.
#------------------------------------------------------------------------------

"""Module for testing NCHAR variables."""

import TestEnv

import cx_Oracle

class TestCase(TestEnv.BaseTestCase):

    def setUp(self):
        TestEnv.BaseTestCase.setUp(self)
        self.rawData = []
        self.dataByKey = {}
        for i in range(1, 11):
            unicodeCol = u"Unicode \u3042 %d" % i
            fixedCharCol = (u"Fixed Unicode %d" % i).ljust(40)
            if i % 2:
                nullableCol = u"Nullable %d" % i
            else:
                nullableCol = None
            dataTuple = (i, unicodeCol, fixedCharCol, nullableCol)
            self.rawData.append(dataTuple)
            self.dataByKey[i] = dataTuple

    def testUnicodeLength(self):
        "test value length"
        returnValue = self.cursor.var(int)
        self.cursor.execute("""
                begin
                  :retval := LENGTH(:value);
                end;""",
                value = u"InVal \u3042",
                retval = returnValue)
        self.assertEqual(returnValue.getvalue(), 7)

    def testBindUnicode(self):
        "test binding in a unicode"
        self.cursor.setinputsizes(value = cx_Oracle.NCHAR)
        self.cursor.execute("""
                select * from TestUnicodes
                where UnicodeCol = :value""",
                value = u"Unicode \u3042 5")
        self.assertEqual(self.cursor.fetchall(), [self.dataByKey[5]])

    def testBindDifferentVar(self):
        "test binding a different variable on second execution"
        retval_1 = self.cursor.var(cx_Oracle.NCHAR, 30)
        retval_2 = self.cursor.var(cx_Oracle.NCHAR, 30)
        self.cursor.execute(r"begin :retval := unistr('Called \3042'); end;",
                retval = retval_1)
        self.assertEqual(retval_1.getvalue(), u"Called \u3042")
        self.cursor.execute("begin :retval := 'Called'; end;",
                retval = retval_2)
        self.assertEqual(retval_2.getvalue(), "Called")

    def testBindUnicodeAfterNumber(self):
        "test binding in a unicode after setting input sizes to a number"
        unicodeVal = self.cursor.var(cx_Oracle.NCHAR)
        unicodeVal.setvalue(0, u"Unicode \u3042 6")
        self.cursor.setinputsizes(value = cx_Oracle.NUMBER)
        self.cursor.execute("""
                select * from TestUnicodes
                where UnicodeCol = :value""",
                value = unicodeVal)
        self.assertEqual(self.cursor.fetchall(), [self.dataByKey[6]])

    def testBindUnicodeArrayDirect(self):
        "test binding in a unicode array"
        returnValue = self.cursor.var(cx_Oracle.NUMBER)
        array = [r[1] for r in self.rawData]
        arrayVar = self.cursor.arrayvar(cx_Oracle.NCHAR, array)
        statement = """
                begin
                  :retval := pkg_TestUnicodeArrays.TestInArrays(
                      :integerValue, :array);
                end;"""
        self.cursor.execute(statement,
                retval = returnValue,
                integerValue = 5,
                array = arrayVar)
        self.assertEqual(returnValue.getvalue(), 116)
        array = [ u"Unicode - \u3042 %d" % i for i in range(15) ]
        arrayVar = self.cursor.arrayvar(cx_Oracle.NCHAR, array)
        self.cursor.execute(statement,
                integerValue = 8,
                array = arrayVar)
        self.assertEqual(returnValue.getvalue(), 208)

    def testBindUnicodeArrayBySizes(self):
        "test binding in a unicode array (with setinputsizes)"
        returnValue = self.cursor.var(cx_Oracle.NUMBER)
        self.cursor.setinputsizes(array = [cx_Oracle.NCHAR, 10])
        array = [r[1] for r in self.rawData]
        self.cursor.execute("""
                begin
                  :retval := pkg_TestUnicodeArrays.TestInArrays(:integerValue,
                      :array);
                end;""",
                retval = returnValue,
                integerValue = 6,
                array = array)
        self.assertEqual(returnValue.getvalue(), 117)

    def testBindUnicodeArrayByVar(self):
        "test binding in a unicode array (with arrayvar)"
        returnValue = self.cursor.var(cx_Oracle.NUMBER)
        array = self.cursor.arrayvar(cx_Oracle.NCHAR, 10, 20)
        array.setvalue(0, [r[1] for r in self.rawData])
        self.cursor.execute("""
                begin
                  :retval := pkg_TestUnicodeArrays.TestInArrays(:integerValue,
                      :array);
                end;""",
                retval = returnValue,
                integerValue = 7,
                array = array)
        self.assertEqual(returnValue.getvalue(), 118)

    def testBindInOutUnicodeArrayByVar(self):
        "test binding in/out a unicode array (with arrayvar)"
        array = self.cursor.arrayvar(cx_Oracle.NCHAR, 10, 100)
        originalData = [r[1] for r in self.rawData]
        format = u"Converted element \u3042 # %d originally had length %d"
        expectedData = [format % (i, len(originalData[i - 1])) \
                for i in range(1, 6)] + originalData[5:]
        array.setvalue(0, originalData)
        self.cursor.execute("""
                begin
                  pkg_TestUnicodeArrays.TestInOutArrays(:numElems, :array);
                end;""",
                numElems = 5,
                array = array)
        self.assertEqual(array.getvalue(), expectedData)

    def testBindOutUnicodeArrayByVar(self):
        "test binding out a unicode array (with arrayvar)"
        array = self.cursor.arrayvar(cx_Oracle.NCHAR, 6, 100)
        format = u"Test out element \u3042 # %d"
        expectedData = [format % i for i in range(1, 7)]
        self.cursor.execute("""
                begin
                  pkg_TestUnicodeArrays.TestOutArrays(:numElems, :array);
                end;""",
                numElems = 6,
                array = array)
        self.assertEqual(array.getvalue(), expectedData)

    def testBindNull(self):
        "test binding in a null"
        self.cursor.execute("""
                select * from TestUnicodes
                where UnicodeCol = :value""",
                value = None)
        self.assertEqual(self.cursor.fetchall(), [])

    def testBindOutSetInputSizesByType(self):
        "test binding out with set input sizes defined (by type)"
        vars = self.cursor.setinputsizes(value = cx_Oracle.NCHAR)
        self.cursor.execute(r"""
                begin
                  :value := unistr('TSI \3042');
                end;""")
        self.assertEqual(vars["value"].getvalue(), u"TSI \u3042")

    def testBindInOutSetInputSizesByType(self):
        "test binding in/out with set input sizes defined (by type)"
        vars = self.cursor.setinputsizes(value = cx_Oracle.NCHAR)
        self.cursor.execute(r"""
                begin
                  :value := :value || unistr(' TSI \3042');
                end;""",
                value = u"InVal \u3041")
        self.assertEqual(vars["value"].getvalue(),
                u"InVal \u3041 TSI \u3042")

    def testBindOutVar(self):
        "test binding out with cursor.var() method"
        var = self.cursor.var(cx_Oracle.NCHAR)
        self.cursor.execute(r"""
                begin
                  :value := unistr('TSI (VAR) \3042');
                end;""",
                value = var)
        self.assertEqual(var.getvalue(), u"TSI (VAR) \u3042")

    def testBindInOutVarDirectSet(self):
        "test binding in/out with cursor.var() method"
        var = self.cursor.var(cx_Oracle.NCHAR)
        var.setvalue(0, u"InVal \u3041")
        self.cursor.execute(r"""
                begin
                  :value := :value || unistr(' TSI (VAR) \3042');
                end;""",
                value = var)
        self.assertEqual(var.getvalue(), u"InVal \u3041 TSI (VAR) \u3042")

    def testCursorDescription(self):
        "test cursor description is accurate"
        self.cursor.execute("select * from TestUnicodes")
        self.assertEqual(self.cursor.description,
                [ ('INTCOL', cx_Oracle.NUMBER, 10, None, 9, 0, 0),
                  ('UNICODECOL', cx_Oracle.NCHAR, 20, 80, None, None, 0),
                  ('FIXEDUNICODECOL', cx_Oracle.FIXED_NCHAR, 40, 160, None,
                        None, 0),
                  ('NULLABLECOL', cx_Oracle.NCHAR, 50, 200, None, None, 1) ])

    def testFetchAll(self):
        "test that fetching all of the data returns the correct results"
        self.cursor.execute("select * From TestUnicodes order by IntCol")
        self.assertEqual(self.cursor.fetchall(), self.rawData)
        self.assertEqual(self.cursor.fetchall(), [])

    def testFetchMany(self):
        "test that fetching data in chunks returns the correct results"
        self.cursor.execute("select * From TestUnicodes order by IntCol")
        self.assertEqual(self.cursor.fetchmany(3), self.rawData[0:3])
        self.assertEqual(self.cursor.fetchmany(2), self.rawData[3:5])
        self.assertEqual(self.cursor.fetchmany(4), self.rawData[5:9])
        self.assertEqual(self.cursor.fetchmany(3), self.rawData[9:])
        self.assertEqual(self.cursor.fetchmany(3), [])

    def testFetchOne(self):
        "test that fetching a single row returns the correct results"
        self.cursor.execute("""
                select *
                from TestUnicodes
                where IntCol in (3, 4)
                order by IntCol""")
        self.assertEqual(self.cursor.fetchone(), self.dataByKey[3])
        self.assertEqual(self.cursor.fetchone(), self.dataByKey[4])
        self.assertEqual(self.cursor.fetchone(), None)

if __name__ == "__main__":
    TestEnv.RunTestCases()

