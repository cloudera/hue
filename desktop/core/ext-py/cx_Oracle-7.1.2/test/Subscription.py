#------------------------------------------------------------------------------
# Copyright (c) 2017, 2019, Oracle and/or its affiliates. All rights reserved.
#------------------------------------------------------------------------------

"""Module for testing subscriptions."""

import TestEnv

import cx_Oracle
import threading

class SubscriptionData(object):

    def __init__(self, numMessagesExpected):
        self.condition = threading.Condition()
        self.numMessagesExpected = numMessagesExpected
        self.numMessagesReceived = 0
        self.tableOperations = []
        self.rowOperations = []
        self.rowids = []

    def CallbackHandler(self, message):
        if message.type != cx_Oracle.EVENT_DEREG:
            table, = message.tables
            self.tableOperations.append(table.operation)
            for row in table.rows:
                self.rowOperations.append(row.operation)
                self.rowids.append(row.rowid)
            self.numMessagesReceived += 1
        if message.type == cx_Oracle.EVENT_DEREG or \
                self.numMessagesReceived == self.numMessagesExpected:
            self.condition.acquire()
            self.condition.notify()
            self.condition.release()


class TestCase(TestEnv.BaseTestCase):

    def testSubscription(self):
        "test Subscription for insert, update, delete and truncate"
        self.cursor.execute("truncate table TestTempTable")

        # expected values
        tableOperations = [ cx_Oracle.OPCODE_INSERT, cx_Oracle.OPCODE_UPDATE,
                cx_Oracle.OPCODE_INSERT, cx_Oracle.OPCODE_DELETE,
                cx_Oracle.OPCODE_ALTER | cx_Oracle.OPCODE_ALLROWS ]
        rowOperations = [ cx_Oracle.OPCODE_INSERT, cx_Oracle.OPCODE_UPDATE,
                cx_Oracle.OPCODE_INSERT, cx_Oracle.OPCODE_DELETE ]
        rowids = []

        # set up subscription
        data = SubscriptionData(5)
        connection = TestEnv.GetConnection(threaded=True, events=True)
        sub = connection.subscribe(callback = data.CallbackHandler,
                timeout = 10, qos = cx_Oracle.SUBSCR_QOS_ROWIDS)
        sub.registerquery("select * from TestTempTable")
        connection.autocommit = True
        cursor = connection.cursor()

        # insert statement
        cursor.execute("""
                insert into TestTempTable (IntCol, StringCol)
                values (1, 'test')""")
        cursor.execute("select rowid from TestTempTable where IntCol = 1")
        rowids.extend(r for r, in cursor)

        # update statement
        cursor.execute("""
                update TestTempTable set
                    StringCol = 'update'
                where IntCol = 1""")
        cursor.execute("select rowid from TestTempTable where IntCol = 1")
        rowids.extend(r for r, in cursor)

        # second insert statement
        cursor.execute("""
                insert into TestTempTable (IntCol, StringCol)
                values (2, 'test2')""")
        cursor.execute("select rowid from TestTempTable where IntCol = 2")
        rowids.extend(r for r, in cursor)

        # delete statement
        cursor.execute("delete TestTempTable where IntCol = 2")
        rowids.append(rowids[-1])

        # truncate table
        cursor.execute("truncate table TestTempTable")

        # wait for all messages to be sent
        data.condition.acquire()
        data.condition.wait(10)

        # verify the correct messages were sent
        self.assertEqual(data.tableOperations, tableOperations)
        self.assertEqual(data.rowOperations, rowOperations)
        self.assertEqual(data.rowids, rowids)

        # test string format of subscription object is as expected
        fmt = "<cx_Oracle.Subscription on <cx_Oracle.Connection to %s@%s>>"
        expectedValue = fmt % \
                (TestEnv.GetMainUser(), TestEnv.GetConnectString())
        self.assertEqual(str(sub), expectedValue)

if __name__ == "__main__":
    TestEnv.RunTestCases()

