#------------------------------------------------------------------------------
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# Portions Copyright 2007-2015, Anthony Tuininga. All rights reserved.
#
# Portions Copyright 2001-2007, Computronix (Canada) Ltd., Edmonton, Alberta,
# Canada. All rights reserved.
#------------------------------------------------------------------------------

"""Module for testing session pools."""

import TestEnv

import cx_Oracle
import threading

class TestCase(TestEnv.BaseTestCase):

    def __ConnectAndDrop(self):
        """Connect to the database, perform a query and drop the connection."""
        connection = self.pool.acquire()
        cursor = connection.cursor()
        cursor.execute("select count(*) from TestNumbers")
        count, = cursor.fetchone()
        self.assertEqual(count, 10)

    def __ConnectAndGenerateError(self):
        """Connect to the database, perform a query which raises an error"""
        connection = self.pool.acquire()
        cursor = connection.cursor()
        self.assertRaises(cx_Oracle.DatabaseError, cursor.execute,
                "select 1 / 0 from dual")

    def __VerifyConnection(self, connection, expectedUser,
            expectedProxyUser = None):
        cursor = connection.cursor()
        cursor.execute("""
                select
                    sys_context('userenv', 'session_user'),
                    sys_context('userenv', 'proxy_user')
                from dual""")
        actualUser, actualProxyUser = cursor.fetchone()
        self.assertEqual(actualUser, expectedUser.upper())
        self.assertEqual(actualProxyUser,
                expectedProxyUser and expectedProxyUser.upper())

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testPool(self):
        """test that the pool is created and has the right attributes"""
        pool = TestEnv.GetPool(min=2, max=8, increment=3,
                getmode=cx_Oracle.SPOOL_ATTRVAL_WAIT)
        self.assertEqual(pool.username, TestEnv.GetMainUser(),
                "user name differs")
        self.assertEqual(pool.tnsentry, TestEnv.GetConnectString(),
                "tnsentry differs")
        self.assertEqual(pool.dsn, TestEnv.GetConnectString(), "dsn differs")
        self.assertEqual(pool.max, 8, "max differs")
        self.assertEqual(pool.min, 2, "min differs")
        self.assertEqual(pool.increment, 3, "increment differs")
        self.assertEqual(pool.opened, 2, "opened differs")
        self.assertEqual(pool.busy, 0, "busy not 0 at start")
        connection_1 = pool.acquire()
        self.assertEqual(pool.busy, 1, "busy not 1 after acquire")
        self.assertEqual(pool.opened, 2, "opened not unchanged (1)")
        connection_2 = pool.acquire()
        self.assertEqual(pool.busy, 2, "busy not 2 after acquire")
        self.assertEqual(pool.opened, 2, "opened not unchanged (2)")
        connection_3 = pool.acquire()
        self.assertEqual(pool.busy, 3, "busy not 3 after acquire")
        self.assertEqual(pool.opened, 5, "opened not changed (3)")
        pool.release(connection_3)
        self.assertEqual(pool.busy, 2, "busy not 2 after release")
        del connection_2
        self.assertEqual(pool.busy, 1, "busy not 1 after del")
        pool.getmode = cx_Oracle.SPOOL_ATTRVAL_NOWAIT
        self.assertEqual(pool.getmode, cx_Oracle.SPOOL_ATTRVAL_NOWAIT)
        if TestEnv.GetClientVersion() >= (12, 2):
            pool.getmode = cx_Oracle.SPOOL_ATTRVAL_TIMEDWAIT
            self.assertEqual(pool.getmode, cx_Oracle.SPOOL_ATTRVAL_TIMEDWAIT)
        pool.stmtcachesize = 50
        self.assertEqual(pool.stmtcachesize, 50)
        pool.timeout = 10
        self.assertEqual(pool.timeout, 10)
        if TestEnv.GetClientVersion() >= (12, 1):
            pool.max_lifetime_session = 10
            self.assertEqual(pool.max_lifetime_session, 10)

    def testProxyAuth(self):
        """test that proxy authentication is possible"""
        pool = TestEnv.GetPool(min=2, max=8, increment=3,
                getmode=cx_Oracle.SPOOL_ATTRVAL_WAIT)
        self.assertEqual(pool.homogeneous, 1,
                "homogeneous should be 1 by default")
        self.assertRaises(cx_Oracle.ProgrammingError, pool.acquire,
                user = u"missing_proxyuser")
        pool = TestEnv.GetPool(min=2, max=8, increment=3,
                getmode=cx_Oracle.SPOOL_ATTRVAL_WAIT, homogeneous=False)
        self.assertEqual(pool.homogeneous, 0,
                "homogeneous should be 0 after setting it in the constructor")
        connection = pool.acquire(user = TestEnv.GetProxyUser())
        cursor = connection.cursor()
        cursor.execute('select user from dual')
        result, = cursor.fetchone()
        self.assertEqual(result, TestEnv.GetProxyUser().upper())

    def testRollbackOnDel(self):
        "connection rolls back before being destroyed"
        pool = TestEnv.GetPool()
        connection = pool.acquire()
        cursor = connection.cursor()
        cursor.execute("truncate table TestTempTable")
        cursor.execute("insert into TestTempTable (IntCol) values (1)")
        pool = TestEnv.GetPool()
        connection = pool.acquire()
        cursor = connection.cursor()
        cursor.execute("select count(*) from TestTempTable")
        count, = cursor.fetchone()
        self.assertEqual(count, 0)

    def testRollbackOnRelease(self):
        "connection rolls back before released back to the pool"
        pool = TestEnv.GetPool()
        connection = pool.acquire()
        cursor = connection.cursor()
        cursor.execute("truncate table TestTempTable")
        cursor.execute("insert into TestTempTable (IntCol) values (1)")
        cursor.close()
        pool.release(connection)
        pool = TestEnv.GetPool()
        connection = pool.acquire()
        cursor = connection.cursor()
        cursor.execute("select count(*) from TestTempTable")
        count, = cursor.fetchone()
        self.assertEqual(count, 0)

    def testThreading(self):
        """test session pool to database with multiple threads"""
        self.pool = TestEnv.GetPool(min=5, max=20, increment=2, threaded=True,
                getmode=cx_Oracle.SPOOL_ATTRVAL_WAIT)
        threads = []
        for i in range(20):
            thread = threading.Thread(None, self.__ConnectAndDrop)
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()

    def testThreadingWithErrors(self):
        """test session pool to database with multiple threads (with errors)"""
        self.pool = TestEnv.GetPool(min=5, max=20, increment=2, threaded=True,
                getmode=cx_Oracle.SPOOL_ATTRVAL_WAIT)
        threads = []
        for i in range(20):
            thread = threading.Thread(None, self.__ConnectAndGenerateError)
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()

    def testPurity(self):
        """test session pool with various types of purity"""
        action = "TEST_ACTION"
        pool = TestEnv.GetPool(min=1, max=8, increment=1,
                getmode=cx_Oracle.SPOOL_ATTRVAL_WAIT)

        # get connection and set the action
        connection = pool.acquire()
        connection.action = action
        cursor = connection.cursor()
        cursor.execute("select 1 from dual")
        cursor.close()
        pool.release(connection)
        self.assertEqual(pool.opened, 1, "opened (1)")

        # verify that the connection still has the action set on it
        connection = pool.acquire()
        cursor = connection.cursor()
        cursor.execute("select sys_context('userenv', 'action') from dual")
        result, = cursor.fetchone()
        self.assertEqual(result, action)
        cursor.close()
        pool.release(connection)
        self.assertEqual(pool.opened, 1, "opened (2)")

        # get a new connection with new purity (should not have state)
        connection = pool.acquire(purity = cx_Oracle.ATTR_PURITY_NEW)
        cursor = connection.cursor()
        cursor.execute("select sys_context('userenv', 'action') from dual")
        result, = cursor.fetchone()
        self.assertEqual(result, None)
        cursor.close()
        self.assertEqual(pool.opened, 2, "opened (3)")
        pool.drop(connection)
        self.assertEqual(pool.opened, 1, "opened (4)")

    def testHeterogeneous(self):
        """test heterogeneous pool with user and password specified"""
        pool = TestEnv.GetPool(min=2, max=8, increment=3, homogeneous=False,
                getmode=cx_Oracle.SPOOL_ATTRVAL_WAIT)
        self.assertEqual(pool.homogeneous, 0)
        self.__VerifyConnection(pool.acquire(), TestEnv.GetMainUser())
        self.__VerifyConnection(pool.acquire(TestEnv.GetMainUser(),
                TestEnv.GetMainPassword()), TestEnv.GetMainUser())
        self.__VerifyConnection(pool.acquire(TestEnv.GetProxyUser(),
                TestEnv.GetProxyPassword()), TestEnv.GetProxyUser())
        userStr = "%s[%s]" % (TestEnv.GetMainUser(), TestEnv.GetProxyUser())
        self.__VerifyConnection(pool.acquire(userStr,
                TestEnv.GetMainPassword()), TestEnv.GetProxyUser(),
                TestEnv.GetMainUser())

    def testHeterogenousWithoutUser(self):
        """test heterogeneous pool without user and password specified"""
        pool = TestEnv.GetPool(user="", password="", min=2, max=8, increment=3,
                getmode=cx_Oracle.SPOOL_ATTRVAL_WAIT, homogeneous=False)
        self.__VerifyConnection(pool.acquire(TestEnv.GetMainUser(),
                TestEnv.GetMainPassword()), TestEnv.GetMainUser())
        self.__VerifyConnection(pool.acquire(TestEnv.GetProxyUser(),
                TestEnv.GetProxyPassword()), TestEnv.GetProxyUser())
        userStr = "%s[%s]" % (TestEnv.GetMainUser(), TestEnv.GetProxyUser())
        self.__VerifyConnection(pool.acquire(userStr,
                TestEnv.GetMainPassword()), TestEnv.GetProxyUser(),
                TestEnv.GetMainUser())

    def testHeterogenousWithoutPassword(self):
        """test heterogeneous pool without password"""
        pool = TestEnv.GetPool(min=2, max=8, increment=3,
                getmode=cx_Oracle.SPOOL_ATTRVAL_WAIT, homogeneous=False)
        self.assertRaises(cx_Oracle.DatabaseError,  pool.acquire,
                TestEnv.GetMainUser())

    def testHeterogeneousWrongPassword(self):
        """test heterogeneous pool with wrong password specified"""
        pool = TestEnv.GetPool(min=2, max=8, increment=3,
                getmode=cx_Oracle.SPOOL_ATTRVAL_WAIT, homogeneous=False)
        self.assertRaises(cx_Oracle.DatabaseError, pool.acquire,
                TestEnv.GetProxyUser(), "this is the wrong password")

    def testTaggingSession(self):
        "test tagging a session"
        pool = TestEnv.GetPool(min=2, max=8, increment=3,
                getmode=cx_Oracle.SPOOL_ATTRVAL_NOWAIT)

        tagMST = "TIME_ZONE=MST"
        tagUTC = "TIME_ZONE=UTC"

        conn = pool.acquire()
        self.assertEqual(conn.tag, None)
        pool.release(conn, tag=tagMST)

        conn = pool.acquire()
        self.assertEqual(conn.tag, None)
        conn.tag = tagUTC
        conn.close()

        conn = pool.acquire(tag=tagMST)
        self.assertEqual(conn.tag, tagMST)
        conn.close()

        conn = pool.acquire(tag=tagUTC)
        self.assertEqual(conn.tag, tagUTC)
        conn.close()

    def testPLSQLSessionCallbacks(self):
        "test PL/SQL session callbacks"
        clientVersion = cx_Oracle.clientversion()
        if clientVersion < (12, 2):
            self.skipTest("PL/SQL session callbacks not supported before 12.2")
        pool = TestEnv.GetPool(min=2, max=8, increment=3,
                getmode=cx_Oracle.SPOOL_ATTRVAL_NOWAIT,
                sessionCallback="pkg_SessionCallback.TheCallback")
        tags = ["NLS_DATE_FORMAT=SIMPLE", "NLS_DATE_FORMAT=FULL;TIME_ZONE=UTC",
                "NLS_DATE_FORMAT=FULL;TIME_ZONE=MST"]
        actualTags = [None, None, "NLS_DATE_FORMAT=FULL;TIME_ZONE=UTC"]

        # truncate PL/SQL session callback log
        conn = pool.acquire()
        cursor = conn.cursor()
        cursor.execute("truncate table PLSQLSessionCallbacks")
        conn.close()

        # request sessions with each of the first two tags
        for tag in tags[:2]:
            conn = pool.acquire(tag=tag)
            conn.close()

        # for the last tag, use the matchanytag flag
        conn = pool.acquire(tag=tags[2], matchanytag=True)
        conn.close()

        # verify the PL/SQL session callback log is accurate
        conn = pool.acquire()
        cursor = conn.cursor()
        cursor.execute("""
                select RequestedTag, ActualTag
                from PLSQLSessionCallbacks
                order by FixupTimestamp""")
        results = cursor.fetchall()
        expectedResults = list(zip(tags, actualTags))
        self.assertEqual(results, expectedResults)

    def testTaggingInvalidKey(self):
        """testTagging with Invalid key"""
        pool = TestEnv.GetPool(getmode=cx_Oracle.SPOOL_ATTRVAL_NOWAIT)
        conn = pool.acquire()
        self.assertRaises(TypeError, pool.release, conn, tag=12345)
        clientVersion = cx_Oracle.clientversion()
        if clientVersion >= (12, 2):
            self.assertRaises(cx_Oracle.DatabaseError, pool.release, conn,
                    tag="INVALID_TAG")

if __name__ == "__main__":
    TestEnv.RunTestCases()

