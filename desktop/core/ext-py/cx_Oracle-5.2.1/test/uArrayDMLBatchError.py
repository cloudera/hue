"""Module for testing row count per iteration for DML Array and Batch errors"""

class TestArrayDMLBatchError(BaseTestCase):

    def testArrayDMLRowCountsOff(self):
        "test executing with arraydmlrowcounts mode disabled"
        self.cursor.execute(u"truncate table TestArrayDML")
        rows = [ (1, u"First"),
                 (2, u"Second") ]
        sql = u"insert into TestArrayDML (IntCol,StringCol) values (:1,:2)"
        self.cursor.executemany(sql, rows, arraydmlrowcounts = False)
        self.failUnlessRaises(cx_Oracle.DatabaseError,
                self.cursor.getarraydmlrowcounts)
        rows = [ (3, u"Third"),
                 (4, u"Fourth") ]
        self.cursor.executemany(sql, rows)
        self.failUnlessRaises(cx_Oracle.DatabaseError,
                self.cursor.getarraydmlrowcounts)

    def testArrayDMLRowCountsOn(self):
        "test executing with arraydmlrowcounts mode enabled"
        self.cursor.execute(u"truncate table TestArrayDML")
        rows = [ ( 1, u"First", 100),
                 ( 2, u"Second", 200),
                 ( 3, u"Third", 300),
                 ( 4, u"Fourth", 300),
                 ( 5, u"Fifth", 300) ]
        sql = u"insert into TestArrayDML (IntCol,StringCol,IntCol2) " \
                u"values (:1,:2,:3)"
        self.cursor.executemany(sql, rows, arraydmlrowcounts = True)
        self.connection.commit()
        self.failUnlessEqual(self.cursor.getarraydmlrowcounts(),
                [1L, 1L, 1L, 1L, 1L])
        self.cursor.execute(u"select count(*) from TestArrayDML")
        count, = self.cursor.fetchone()
        self.failUnlessEqual(count, len(rows))

    def testExceptionInIteration(self):
        "test executing with arraydmlrowcounts with exception"
        self.cursor.execute(u"truncate table TestArrayDML")
        rows = [ (1, u"First"),
                 (2, u"Second"),
                 (2, u"Third"),
                 (4, u"Fourth") ]
        sql = u"insert into TestArrayDML (IntCol,StringCol) values (:1,:2)"
        self.failUnlessRaises(cx_Oracle.DatabaseError, self.cursor.executemany,
                sql, rows, arraydmlrowcounts = True)
        self.failUnlessEqual(self.cursor.getarraydmlrowcounts(), [1L, 1L])

    def testExecutingDelete(self):
        "test executing delete statement with arraydmlrowcount mode"
        self.cursor.execute(u"truncate table TestArrayDML")
        rows = [ (1, u"First", 100),
                 (2, u"Second", 200),
                 (3, u"Third", 300),
                 (4, u"Fourth", 300),
                 (5, u"Fifth", 300),
                 (6, u"Sixth", 400),
                 (7, u"Seventh", 400),
                 (8, u"Eighth", 500) ]
        sql = u"insert into TestArrayDML (IntCol,StringCol,IntCol2) " \
                u"values (:1, :2, :3)"
        self.cursor.executemany(sql, rows)
        rows = [ (200,), (300,), (400,) ]
        statement = u"delete from TestArrayDML where IntCol2 = :1"
        self.cursor.executemany(statement, rows, arraydmlrowcounts = True)
        self.failUnlessEqual(self.cursor.getarraydmlrowcounts(), [1L, 3L, 2L])

    def testExecutingUpdate(self):
        "test executing update statement with arraydmlrowcount mode"
        self.cursor.execute(u"truncate table TestArrayDML")
        rows = [ (1, u"First",100),
                 (2, u"Second",200),
                 (3, u"Third",300),
                 (4, u"Fourth",300),
                 (5, u"Fifth",300),
                 (6, u"Sixth",400),
                 (7, u"Seventh",400),
                 (8, u"Eighth",500) ]
        sql = u"insert into TestArrayDML (IntCol,StringCol,IntCol2) " \
                u"values (:1, :2, :3)"
        self.cursor.executemany(sql, rows)
        rows = [ (u"One", 100),
                 (u"Two", 200),
                 (u"Three", 300),
                 (u"Four", 400) ]
        sql = u"update TestArrayDML set StringCol = :1 where IntCol2 = :2"
        self.cursor.executemany(sql, rows, arraydmlrowcounts = True)
        self.failUnlessEqual(self.cursor.getarraydmlrowcounts(),
                [1L, 1L, 3L, 2L])

    def testInsertWithBatchError(self):
        "test executing insert with multiple distinct batch errors"
        self.cursor.execute(u"truncate table TestArrayDML")
        rows = [ (1, u"First", 100),
                 (2, u"Second", 200),
                 (2, u"Third", 300),
                 (4, u"Fourth", 400),
                 (5, u"Fourth", 1000)]
        sql = u"insert into TestArrayDML (IntCol, StringCol, IntCol2) " \
                u"values (:1, :2, :3)"
        self.cursor.executemany(sql, rows, batcherrors = True,
                arraydmlrowcounts = True)
        expectedErrors = [
                ( 4, 1438, u"ORA-01438: value larger than specified " \
                        u"precision allowed for this column\n" ),
                ( 2, 1, u"ORA-00001: unique constraint " \
                        u"(CX_ORACLE.TESTARRAYDML_PK) violated\n")
        ]
        actualErrors = [(e.offset, e.code, e.message) \
                for e in self.cursor.getbatcherrors()]
        self.failUnlessEqual(actualErrors, expectedErrors)
        self.failUnlessEqual(self.cursor.getarraydmlrowcounts(),
                [1L, 1L, 0L, 1L, 0L])

    def testBatchErrorFalse(self):
        "test batcherrors mode set to False"
        self.cursor.execute(u"truncate table TestArrayDML")
        rows = [ (1, u"First", 100),
                 (2, u"Second", 200),
                 (2, u"Third", 300) ]
        sql = u"insert into TestArrayDML (IntCol, StringCol, IntCol2) " \
                u"values (:1, :2, :3)"
        self.failUnlessRaises(cx_Oracle.IntegrityError,
                self.cursor.executemany, sql, rows, batcherrors = False)

    def testUpdatewithBatchError(self):
        "test executing in succession with batch error"
        self.cursor.execute(u"truncate table TestArrayDML")
        rows = [ (1, u"First", 100),
                 (2, u"Second", 200),
                 (3, u"Third", 300),
                 (4, u"Second", 300),
                 (5, u"Fifth", 300),
                 (6, u"Sixth", 400),
                 (6, u"Seventh", 400),
                 (8, u"Eighth", 100) ]
        sql = u"insert into TestArrayDML (IntCol, StringCol, IntCol2) " \
                u"values (:1, :2, :3)"
        self.cursor.executemany(sql, rows, batcherrors = True)
        expectedErrors = [
                ( 6, 1, u"ORA-00001: unique constraint " \
                        u"(CX_ORACLE.TESTARRAYDML_PK) violated\n")
        ]
        actualErrors = [(e.offset, e.code, e.message) \
                for e in self.cursor.getbatcherrors()]
        self.failUnlessEqual(actualErrors, expectedErrors)
        rows = [ (101, u"First"),
                 (201, u"Second"),
                 (3000, u"Third"),
                 (900, u"Ninth"),
                 (301, u"Third") ]
        sql = u"update TestArrayDML set IntCol2 = :1 where StringCol = :2"
        self.cursor.executemany(sql, rows, arraydmlrowcounts = True,
                batcherrors = True)
        expectedErrors = [
                ( 2, 1438, u"ORA-01438: value larger than specified " \
                        u"precision allowed for this column\n" )
        ]
        actualErrors = [(e.offset, e.code, e.message) \
                for e in self.cursor.getbatcherrors()]
        self.failUnlessEqual(actualErrors, expectedErrors)
        self.failUnlessEqual(self.cursor.getarraydmlrowcounts(),
                [1L, 2L, 0L, 0L, 1L])
        self.failUnlessEqual(self.cursor.rowcount, 4)

