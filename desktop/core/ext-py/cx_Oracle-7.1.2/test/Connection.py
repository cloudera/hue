#------------------------------------------------------------------------------
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# Portions Copyright 2007-2015, Anthony Tuininga. All rights reserved.
#
# Portions Copyright 2001-2007, Computronix (Canada) Ltd., Edmonton, Alberta,
# Canada. All rights reserved.
#------------------------------------------------------------------------------

"""Module for testing connections."""

import TestEnv

import cx_Oracle
import random
import string
import threading

class TestCase(TestEnv.BaseTestCase):

    def __ConnectAndDrop(self):
        """Connect to the database, perform a query and drop the connection."""
        connection = TestEnv.GetConnection(threaded=True)
        cursor = connection.cursor()
        cursor.execute(u"select count(*) from TestNumbers")
        count, = cursor.fetchone()
        self.assertEqual(count, 10)

    def __VerifyAttributes(self, connection, attrName, value, sql):
        setattr(connection, attrName, value)
        cursor = connection.cursor()
        cursor.execute(sql)
        result, = cursor.fetchone()
        self.assertEqual(result, value, "%s value mismatch" % attrName)

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def verifyArgs(self, connection):
        self.assertEqual(connection.username, TestEnv.GetMainUser(),
                "user name differs")
        self.assertEqual(connection.tnsentry, TestEnv.GetConnectString(),
                "tnsentry differs")
        self.assertEqual(connection.dsn, TestEnv.GetConnectString(),
                "dsn differs")

    def testAllArgs(self):
        "connection to database with user, password, TNS separate"
        connection = TestEnv.GetConnection()
        self.verifyArgs(connection)

    def testAppContext(self):
        "test use of application context"
        namespace = "CLIENTCONTEXT"
        appContextEntries = [
            ( namespace, "ATTR1", "VALUE1" ),
            ( namespace, "ATTR2", "VALUE2" ),
            ( namespace, "ATTR3", "VALUE3" )
        ]
        connection = TestEnv.GetConnection(appcontext=appContextEntries)
        cursor = connection.cursor()
        for namespace, name, value in appContextEntries:
            cursor.execute("select sys_context(:1, :2) from dual",
                    (namespace, name))
            actualValue, = cursor.fetchone()
            self.assertEqual(actualValue, value)

    def testAppContextNegative(self):
        "test invalid use of application context"
        self.assertRaises(TypeError, cx_Oracle.connect, TestEnv.GetMainUser(),
                TestEnv.GetMainPassword(), TestEnv.GetConnectString(),
                appcontext=[('userenv', 'action')])

    def testAttributes(self):
        "test connection end-to-end tracing attributes"
        connection = TestEnv.GetConnection()
        if TestEnv.GetClientVersion() >= (12, 1):
            self.__VerifyAttributes(connection, "dbop", "cx_OracleTest_DBOP",
                    "select dbop_name from v$sql_monitor "
                    "where sid = sys_context('userenv', 'sid')"
                    "and status = 'EXECUTING'")
        self.__VerifyAttributes(connection, "action", "cx_OracleTest_Action",
                "select sys_context('userenv', 'action') from dual")
        self.__VerifyAttributes(connection, "module", "cx_OracleTest_Module",
                "select sys_context('userenv', 'module') from dual")
        self.__VerifyAttributes(connection, "clientinfo",
                "cx_OracleTest_CInfo",
                "select sys_context('userenv', 'client_info') from dual")
        self.__VerifyAttributes(connection, "client_identifier",
                "cx_OracleTest_CID",
                "select sys_context('userenv', 'client_identifier') from dual")

    def testAutoCommit(self):
        "test use of autocommit"
        connection = TestEnv.GetConnection()
        cursor = connection.cursor()
        otherConnection = TestEnv.GetConnection()
        otherCursor = otherConnection.cursor()
        cursor.execute("truncate table TestTempTable")
        cursor.execute("insert into TestTempTable (IntCol) values (1)")
        otherCursor.execute("select IntCol from TestTempTable")
        rows = otherCursor.fetchall()
        self.assertEqual(rows, [])
        connection.autocommit = True
        cursor.execute("insert into TestTempTable (IntCol) values (2)")
        otherCursor.execute("select IntCol from TestTempTable order by IntCol")
        rows = otherCursor.fetchall()
        self.assertEqual(rows, [(1,), (2,)])

    def testBadConnectString(self):
        "connection to database with bad connect string"
        self.assertRaises(cx_Oracle.DatabaseError, cx_Oracle.connect,
                TestEnv.GetMainUser())
        self.assertRaises(cx_Oracle.DatabaseError, cx_Oracle.connect,
                TestEnv.GetMainUser() + u"@" + TestEnv.GetConnectString())
        self.assertRaises(cx_Oracle.DatabaseError, cx_Oracle.connect,
                TestEnv.GetMainUser() + "@" + \
                TestEnv.GetConnectString() + "/" + TestEnv.GetMainPassword())

    def testBadPassword(self):
        "connection to database with bad password"
        self.assertRaises(cx_Oracle.DatabaseError, cx_Oracle.connect,
                TestEnv.GetMainUser(), TestEnv.GetMainPassword() + "X",
                TestEnv.GetConnectString())

    def testChangePassword(self):
        "test changing password"
        sysRandom = random.SystemRandom()
        newPassword = "".join(sysRandom.choice(string.ascii_letters) \
                for i in range(20))
        connection = TestEnv.GetConnection()
        connection.changepassword(TestEnv.GetMainPassword(), newPassword)
        cconnection = cx_Oracle.connect(TestEnv.GetMainUser(), newPassword,
                TestEnv.GetConnectString())
        connection.changepassword(newPassword, TestEnv.GetMainPassword())

    def testChangePasswordNegative(self):
        "test changing password to an invalid value"
        newPassword = "1" * 150
        connection = TestEnv.GetConnection()
        self.assertRaises(cx_Oracle.DatabaseError, connection.changepassword,
                TestEnv.GetMainPassword(), newPassword)

    def testEncodings(self):
        "connection with only encoding or nencoding specified should work"
        connection = cx_Oracle.connect(TestEnv.GetMainUser(),
                TestEnv.GetMainPassword(), TestEnv.GetConnectString())
        encoding = connection.encoding
        nencoding = connection.nencoding
        altEncoding = "ISO-8859-1"
        connection = cx_Oracle.connect(TestEnv.GetMainUser(),
                TestEnv.GetMainPassword(), TestEnv.GetConnectString(),
                encoding=altEncoding)
        self.assertEqual(connection.encoding, altEncoding)
        self.assertEqual(connection.nencoding, nencoding)
        connection = cx_Oracle.connect(TestEnv.GetMainUser(),
                TestEnv.GetMainPassword(), TestEnv.GetConnectString(),
                nencoding=altEncoding)
        self.assertEqual(connection.encoding, encoding)
        self.assertEqual(connection.nencoding, altEncoding)

    def testDifferentEncodings(self):
        connection = cx_Oracle.connect(TestEnv.GetMainUser(),
                TestEnv.GetMainPassword(), TestEnv.GetConnectString(),
                encoding="UTF-8", nencoding="UTF-16")
        value = u"\u03b4\u4e2a"
        cursor = connection.cursor()
        ncharVar = cursor.var(cx_Oracle.NCHAR, 100)
        ncharVar.setvalue(0, value)
        cursor.execute("select :value from dual", value = ncharVar)
        result, = cursor.fetchone()
        self.assertEqual(result, value)

    def testExceptionOnClose(self):
        "confirm an exception is raised after closing a connection"
        connection = TestEnv.GetConnection()
        connection.close()
        self.assertRaises(cx_Oracle.DatabaseError, connection.rollback)

    def testConnectWithHandle(self):
        "test creating a connection using a handle"
        connection = TestEnv.GetConnection()
        cursor = connection.cursor()
        cursor.execute("truncate table TestTempTable")
        intValue = random.randint(1, 32768)
        cursor.execute("""
                insert into TestTempTable (IntCol, StringCol)
                values (:val, null)""", val = intValue)
        connection2 = cx_Oracle.connect(handle = connection.handle)
        cursor = connection2.cursor()
        cursor.execute("select IntCol from TestTempTable")
        fetchedIntValue, = cursor.fetchone()
        self.assertEqual(fetchedIntValue, intValue)
        cursor.close()
        self.assertRaises(cx_Oracle.DatabaseError, connection2.close)
        connection.close()
        cursor = connection2.cursor()
        self.assertRaises(cx_Oracle.DatabaseError, cursor.execute,
                "select count(*) from TestTempTable")

    def testMakeDSN(self):
        "test making a data source name from host, port and sid"
        formatString = u"(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)" + \
                "(HOST=%s)(PORT=%d))(CONNECT_DATA=(SID=%s)))"
        args = ("hostname", 1521, "TEST")
        result = cx_Oracle.makedsn(*args)
        self.assertEqual(result, formatString % args)
        args = (u"hostname", 1521, u"TEST")
        result = cx_Oracle.makedsn(*args)
        self.assertEqual(result, formatString % args)

    def testSingleArg(self):
        "connection to database with user, password, DSN together"
        connection = cx_Oracle.connect("%s/%s@%s" % \
                (TestEnv.GetMainUser(), TestEnv.GetMainPassword(),
                 TestEnv.GetConnectString()))
        self.verifyArgs(connection)

    def testVersion(self):
        "connection version is a string"
        connection = TestEnv.GetConnection()
        self.assertTrue(isinstance(connection.version, str))

    def testRollbackOnClose(self):
        "connection rolls back before close"
        connection = TestEnv.GetConnection()
        cursor = connection.cursor()
        cursor.execute("truncate table TestTempTable")
        otherConnection = TestEnv.GetConnection()
        otherCursor = otherConnection.cursor()
        otherCursor.execute("insert into TestTempTable (IntCol) values (1)")
        otherCursor.close()
        otherConnection.close()
        cursor.execute("select count(*) from TestTempTable")
        count, = cursor.fetchone()
        self.assertEqual(count, 0)

    def testRollbackOnDel(self):
        "connection rolls back before destruction"
        connection = TestEnv.GetConnection()
        cursor = connection.cursor()
        cursor.execute("truncate table TestTempTable")
        otherConnection = TestEnv.GetConnection()
        otherCursor = otherConnection.cursor()
        otherCursor.execute("insert into TestTempTable (IntCol) values (1)")
        del otherCursor
        del otherConnection
        cursor.execute("select count(*) from TestTempTable")
        count, = cursor.fetchone()
        self.assertEqual(count, 0)

    def testThreading(self):
        "connection to database with multiple threads"
        threads = []
        for i in range(20):
            thread = threading.Thread(None, self.__ConnectAndDrop)
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()

    def testStringFormat(self):
        "test string format of connection"
        connection = TestEnv.GetConnection()
        expectedValue = "<cx_Oracle.Connection to %s@%s>" % \
                (TestEnv.GetMainUser(), TestEnv.GetConnectString())
        self.assertEqual(str(connection), expectedValue)

    def testCtxMgrClose(self):
        "test context manager - close"
        connection = TestEnv.GetConnection()
        with connection:
            cursor = connection.cursor()
            cursor.execute("truncate table TestTempTable")
            cursor.execute("insert into TestTempTable (IntCol) values (1)")
            connection.commit()
            cursor.execute("insert into TestTempTable (IntCol) values (2)")
        self.assertRaises(cx_Oracle.DatabaseError, connection.ping)
        connection = TestEnv.GetConnection()
        cursor = connection.cursor()
        cursor.execute("select count(*) from TestTempTable")
        count, = cursor.fetchone()
        self.assertEqual(count, 1)

    def testConnectionAttributes(self):
        "test connection attribute values"
        connection = cx_Oracle.connect(TestEnv.GetMainUser(),
                TestEnv.GetMainPassword(), TestEnv.GetConnectString(),
                encoding="ASCII")
        self.assertEqual(connection.maxBytesPerCharacter, 1)
        connection = cx_Oracle.connect(TestEnv.GetMainUser(),
                TestEnv.GetMainPassword(), TestEnv.GetConnectString(),
                encoding="UTF-8")
        self.assertEqual(connection.maxBytesPerCharacter, 4)
        if TestEnv.GetClientVersion() >= (12, 1):
            self.assertEqual(connection.ltxid, b'')
        self.assertEqual(connection.current_schema, None)
        connection.current_schema = "test_schema"
        self.assertEqual(connection.current_schema, "test_schema")
        self.assertEqual(connection.edition, None)
        connection.external_name = "test_external"
        self.assertEqual(connection.external_name, "test_external")
        connection.internal_name = "test_internal"
        self.assertEqual(connection.internal_name, "test_internal")
        connection.stmtcachesize = 30
        self.assertEqual(connection.stmtcachesize, 30)
        self.assertRaises(TypeError, connection.stmtcachesize, 20.5)
        self.assertRaises(TypeError, connection.stmtcachesize, "value")

    def testClosedConnectionAttributes(self):
        "test closed connection attribute values"
        connection = TestEnv.GetConnection()
        connection.close()
        attrNames = ["current_schema", "edition", "external_name",
                "internal_name", "stmtcachesize"]
        if TestEnv.GetClientVersion() >= (12, 1):
            attrNames.append("ltxid")
        for name in attrNames:
            self.assertRaises(cx_Oracle.DatabaseError, getattr, connection,
                    name)

    def testPing(self):
        "test connection ping"
        connection = TestEnv.GetConnection()
        connection.ping()

    def testTransactionBegin(self):
        "test begin, prepare, cancel transaction"
        connection = TestEnv.GetConnection()
        cursor = connection.cursor()
        cursor.execute("truncate table TestTempTable")
        connection.begin(10, 'trxnId', 'branchId')
        self.assertEqual(connection.prepare(), False)
        connection.begin(10, 'trxnId', 'branchId')
        cursor.execute("""
                insert into TestTempTable (IntCol, StringCol)
                values (1, 'tesName')""")
        self.assertEqual(connection.prepare(), True)
        connection.cancel()
        connection.rollback()
        cursor.execute("select count(*) from TestTempTable")
        count, = cursor.fetchone()
        self.assertEqual(count, 0)

if __name__ == "__main__":
    TestEnv.RunTestCases()

