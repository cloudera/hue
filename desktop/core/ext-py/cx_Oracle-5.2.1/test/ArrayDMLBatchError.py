"""Module for testing row count per iteration for DML Array and Batch errors"""

class TestArrayDMLBatchError(BaseTestCase):

    def testArrayDMLRowCountsOff(self):
        "test executing with arraydmlrowcounts mode disabled"
        self.cursor.execute("truncate table TestArrayDML")
        rows = [ (1, "First"),
                 (2, "Second") ]
        sql = "insert into TestArrayDML (IntCol,StringCol) values (:1,:2)"
        self.cursor.executemany(sql, rows, arraydmlrowcounts = False)
        self.failUnlessRaises(cx_Oracle.DatabaseError,
                self.cursor.getarraydmlrowcounts)
        rows = [ (3, "Third"),
                 (4, "Fourth") ]
        self.cursor.executemany(sql, rows)
        self.failUnlessRaises(cx_Oracle.DatabaseError,
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
        self.failUnlessEqual(self.cursor.getarraydmlrowcounts(),
                [1L, 1L, 1L, 1L, 1L])
        self.cursor.execute("select count(*) from TestArrayDML")
        count, = self.cursor.fetchone()
        self.failUnlessEqual(count, len(rows))

    def testExceptionInIteration(self):
        "test executing with arraydmlrowcounts with exception"
        self.cursor.execute("truncate table TestArrayDML")
        rows = [ (1, "First"),
                 (2, "Second"),
                 (2, "Third"),
                 (4, "Fourth") ]
        sql = "insert into TestArrayDML (IntCol,StringCol) values (:1,:2)"
        self.failUnlessRaises(cx_Oracle.DatabaseError, self.cursor.executemany,
                sql, rows, arraydmlrowcounts = True)
        self.failUnlessEqual(self.cursor.getarraydmlrowcounts(), [1L, 1L])

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
        self.failUnlessEqual(self.cursor.getarraydmlrowcounts(), [1L, 3L, 2L])

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
        self.failUnlessEqual(self.cursor.getarraydmlrowcounts(),
                [1L, 1L, 3L, 2L])

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
        expectedErrors = [
                ( 4, 1438, "ORA-01438: value larger than specified " \
                        "precision allowed for this column\n" ),
                ( 2, 1, "ORA-00001: unique constraint " \
                        "(CX_ORACLE.TESTARRAYDML_PK) violated\n")
        ]
        actualErrors = [(e.offset, e.code, e.message) \
                for e in self.cursor.getbatcherrors()]
        self.failUnlessEqual(actualErrors, expectedErrors)
        self.failUnlessEqual(self.cursor.getarraydmlrowcounts(),
                [1L, 1L, 0L, 1L, 0L])

    def testBatchErrorFalse(self):
        "test batcherrors mode set to False"
        self.cursor.execute("truncate table TestArrayDML")
        rows = [ (1, "First", 100),
                 (2, "Second", 200),
                 (2, "Third", 300) ]
        sql = "insert into TestArrayDML (IntCol, StringCol, IntCol2) " \
                "values (:1, :2, :3)"
        self.failUnlessRaises(cx_Oracle.IntegrityError,
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
        expectedErrors = [
                ( 6, 1, "ORA-00001: unique constraint " \
                        "(CX_ORACLE.TESTARRAYDML_PK) violated\n")
        ]
        actualErrors = [(e.offset, e.code, e.message) \
                for e in self.cursor.getbatcherrors()]
        self.failUnlessEqual(actualErrors, expectedErrors)
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
                        "precision allowed for this column\n" )
        ]
        actualErrors = [(e.offset, e.code, e.message) \
                for e in self.cursor.getbatcherrors()]
        self.failUnlessEqual(actualErrors, expectedErrors)
        self.failUnlessEqual(self.cursor.getarraydmlrowcounts(),
                [1L, 2L, 0L, 0L, 1L])
        self.failUnlessEqual(self.cursor.rowcount, 4)

