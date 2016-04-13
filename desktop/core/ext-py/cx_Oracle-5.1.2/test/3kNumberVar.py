"""Module for testing number variables."""

import cx_Oracle
import decimal

class TestNumberVar(BaseTestCase):

    def setUp(self):
      BaseTestCase.setUp(self)
      self.rawData = []
      self.dataByKey = {}
      for i in range(1, 11):
          numberCol = i + i * 0.25
          floatCol = i + i * 0.75
          unconstrainedCol = i ** 3 + i * 0.5
          if i % 2:
              nullableCol = 143 ** i
          else:
              nullableCol = None
          dataTuple = (i, numberCol, floatCol, unconstrainedCol, nullableCol)
          self.rawData.append(dataTuple)
          self.dataByKey[i] = dataTuple

    def testBindDecimal(self):
        "test binding in a decimal.Decimal"
        self.cursor.execute("""
                select * from TestNumbers
                where NumberCol - :value1 - :value2 = trunc(NumberCol)""",
                value1 = decimal.Decimal("0.20"),
                value2 = decimal.Decimal("0.05"))
        self.failUnlessEqual(self.cursor.fetchall(),
                [self.dataByKey[1], self.dataByKey[5], self.dataByKey[9]])

    def testBindFloat(self):
        "test binding in a float"
        self.cursor.execute("""
                select * from TestNumbers
                where NumberCol - :value = trunc(NumberCol)""",
                value = 0.25)
        self.failUnlessEqual(self.cursor.fetchall(),
                [self.dataByKey[1], self.dataByKey[5], self.dataByKey[9]])

    def testBindSmallLong(self):
        "test binding in a small long integer"
        self.cursor.execute("""
                select * from TestNumbers
                where IntCol = :value""",
                value = 3)
        self.failUnlessEqual(self.cursor.fetchall(), [self.dataByKey[3]])

    def testBindLargeLong(self):
        "test binding in a large long integer"
        valueVar = self.cursor.var(cx_Oracle.NUMBER)
        valueVar.setvalue(0, 6088343244)
        self.cursor.execute("""
                begin
                  :value := :value + 5;
                end;""",
                value = valueVar)
        value = valueVar.getvalue()
        self.failUnlessEqual(value, 6088343249)

    def testBindIntegerAfterString(self):
        "test binding in an number after setting input sizes to a string"
        self.cursor.setinputsizes(value = 15)
        self.cursor.execute("""
                select * from TestNumbers
                where IntCol = :value""",
                value = 3)
        self.failUnlessEqual(self.cursor.fetchall(), [self.dataByKey[3]])

    def testBindNull(self):
        "test binding in a null"
        self.cursor.execute("""
                select * from TestNumbers
                where IntCol = :value""",
                value = None)
        self.failUnlessEqual(self.cursor.fetchall(), [])

    def testBindNumberArrayDirect(self):
        "test binding in a number array"
        returnValue = self.cursor.var(cx_Oracle.NUMBER)
        array = [r[1] for r in self.rawData]
        statement = """
                begin
                  :p_ReturnValue := pkg_TestNumberArrays.TestInArrays(
                      :p_StartValue, :p_Array);
                end;"""
        self.cursor.execute(statement,
                p_ReturnValue = returnValue,
                p_StartValue = 5,
                p_Array = array)
        self.failUnlessEqual(returnValue.getvalue(), 73.75)
        array = list(range(15))
        self.cursor.execute(statement,
                p_StartValue = 10,
                p_Array = array)
        self.failUnlessEqual(returnValue.getvalue(), 115.0)

    def testBindNumberArrayBySizes(self):
        "test binding in a number array (with setinputsizes)"
        returnValue = self.cursor.var(cx_Oracle.NUMBER)
        self.cursor.setinputsizes(p_Array = [cx_Oracle.NUMBER, 10])
        array = [r[1] for r in self.rawData]
        self.cursor.execute("""
                begin
                  :p_ReturnValue := pkg_TestNumberArrays.TestInArrays(
                      :p_StartValue, :p_Array);
                end;""",
                p_ReturnValue = returnValue,
                p_StartValue = 6,
                p_Array = array)
        self.failUnlessEqual(returnValue.getvalue(), 74.75)

    def testBindNumberArrayByVar(self):
        "test binding in a number array (with arrayvar)"
        returnValue = self.cursor.var(cx_Oracle.NUMBER)
        array = self.cursor.arrayvar(cx_Oracle.NUMBER,
                [r[1] for r in self.rawData])
        array.setvalue(0, [r[1] for r in self.rawData])
        self.cursor.execute("""
                begin
                  :p_ReturnValue := pkg_TestNumberArrays.TestInArrays(
                      :p_IntegerValue, :p_Array);
                end;""",
                p_ReturnValue = returnValue,
                p_IntegerValue = 7,
                p_Array = array)
        self.failUnlessEqual(returnValue.getvalue(), 75.75)

    def testBindZeroLengthNumberArrayByVar(self):
        "test binding in a zero length number array (with arrayvar)"
        returnValue = self.cursor.var(cx_Oracle.NUMBER)
        array = self.cursor.arrayvar(cx_Oracle.NUMBER, 0)
        self.cursor.execute("""
                begin
                  :p_ReturnValue := pkg_TestNumberArrays.TestInArrays(
                      :p_IntegerValue, :p_Array);
                end;""",
                p_ReturnValue = returnValue,
                p_IntegerValue = 8,
                p_Array = array)
        self.failUnlessEqual(returnValue.getvalue(), 8.0)
        self.failUnlessEqual(array.getvalue(), [])

    def testBindInOutNumberArrayByVar(self):
        "test binding in/out a number array (with arrayvar)"
        array = self.cursor.arrayvar(cx_Oracle.NUMBER, 10)
        originalData = [r[1] for r in self.rawData]
        expectedData = [originalData[i - 1] * 10 for i in range(1, 6)] + \
                originalData[5:]
        array.setvalue(0, originalData)
        self.cursor.execute("""
                begin
                  pkg_TestNumberArrays.TestInOutArrays(:p_NumElems, :p_Array);
                end;""",
                p_NumElems = 5,
                p_Array = array)
        self.failUnlessEqual(array.getvalue(), expectedData)

    def testBindOutNumberArrayByVar(self):
        "test binding out a Number array (with arrayvar)"
        array = self.cursor.arrayvar(cx_Oracle.NUMBER, 6)
        expectedData = [i * 100 for i in range(1, 7)]
        self.cursor.execute("""
                begin
                  pkg_TestNumberArrays.TestOutArrays(:p_NumElems, :p_Array);
                end;""",
                p_NumElems = 6,
                p_Array = array)
        self.failUnlessEqual(array.getvalue(), expectedData)

    def testBindOutSetInputSizes(self):
        "test binding out with set input sizes defined"
        vars = self.cursor.setinputsizes(value = cx_Oracle.NUMBER)
        self.cursor.execute("""
                begin
                  :value := 5;
                end;""")
        self.failUnlessEqual(vars["value"].getvalue(), 5)

    def testBindInOutSetInputSizes(self):
        "test binding in/out with set input sizes defined"
        vars = self.cursor.setinputsizes(value = cx_Oracle.NUMBER)
        self.cursor.execute("""
                begin
                  :value := :value + 5;
                end;""",
                value = 1.25)
        self.failUnlessEqual(vars["value"].getvalue(), 6.25)

    def testBindOutVar(self):
        "test binding out with cursor.var() method"
        var = self.cursor.var(cx_Oracle.NUMBER)
        self.cursor.execute("""
                begin
                  :value := 5;
                end;""",
                value = var)
        self.failUnlessEqual(var.getvalue(), 5)

    def testBindInOutVarDirectSet(self):
        "test binding in/out with cursor.var() method"
        var = self.cursor.var(cx_Oracle.NUMBER)
        var.setvalue(0, 2.25)
        self.cursor.execute("""
                begin
                  :value := :value + 5;
                end;""",
                value = var)
        self.failUnlessEqual(var.getvalue(), 7.25)

    def testCursorDescription(self):
        "test cursor description is accurate"
        self.cursor.execute("select * from TestNumbers")
        self.failUnlessEqual(self.cursor.description,
                [ ('INTCOL', cx_Oracle.NUMBER, 10, 22, 9, 0, 0),
                  ('NUMBERCOL', cx_Oracle.NUMBER, 13, 22, 9, 2, 0),
                  ('FLOATCOL', cx_Oracle.NUMBER, 127, 22, 126, -127, 0),
                  ('UNCONSTRAINEDCOL', cx_Oracle.NUMBER, 127, 22, 0, -127, 0),
                  ('NULLABLECOL', cx_Oracle.NUMBER, 39, 22, 38, 0, 1) ])

    def testFetchAll(self):
        "test that fetching all of the data returns the correct results"
        self.cursor.execute("select * From TestNumbers order by IntCol")
        self.failUnlessEqual(self.cursor.fetchall(), self.rawData)
        self.failUnlessEqual(self.cursor.fetchall(), [])

    def testFetchMany(self):
        "test that fetching data in chunks returns the correct results"
        self.cursor.execute("select * From TestNumbers order by IntCol")
        self.failUnlessEqual(self.cursor.fetchmany(3), self.rawData[0:3])
        self.failUnlessEqual(self.cursor.fetchmany(2), self.rawData[3:5])
        self.failUnlessEqual(self.cursor.fetchmany(4), self.rawData[5:9])
        self.failUnlessEqual(self.cursor.fetchmany(3), self.rawData[9:])
        self.failUnlessEqual(self.cursor.fetchmany(3), [])

    def testFetchOne(self):
        "test that fetching a single row returns the correct results"
        self.cursor.execute("""
                select *
                from TestNumbers
                where IntCol in (3, 4)
                order by IntCol""")
        self.failUnlessEqual(self.cursor.fetchone(), self.dataByKey[3])
        self.failUnlessEqual(self.cursor.fetchone(), self.dataByKey[4])
        self.failUnlessEqual(self.cursor.fetchone(), None)

    def testReturnAsFloat(self):
        "test that fetching a floating point number returns such in Python"
        self.cursor.execute("select 1.25 from dual")
        result, = self.cursor.fetchone()
        self.failUnlessEqual(result, 1.25)

