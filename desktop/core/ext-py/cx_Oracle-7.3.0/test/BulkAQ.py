#------------------------------------------------------------------------------
# Copyright (c) 2019, Oracle and/or its affiliates. All rights reserved.
#------------------------------------------------------------------------------

"""Module for testing AQ Bulk enqueue/dequeue."""

import TestEnv

import cx_Oracle
import decimal
import threading

RAW_QUEUE_NAME = "TEST_RAW_QUEUE"
RAW_PAYLOAD_DATA = [
    "The first message",
    "The second message",
    "The third message",
    "The fourth message",
    "The fifth message",
    "The sixth message",
    "The seventh message",
    "The eighth message",
    "The ninth message",
    "The tenth message",
    "The eleventh message",
    "The twelfth and final message"
]

class TestCase(TestEnv.BaseTestCase):

    def __deqInThread(self, results):
        connection = TestEnv.GetConnection(threaded=True)
        queue = connection.queue(RAW_QUEUE_NAME)
        queue.deqOptions.wait = 10
        queue.deqOptions.navigation = cx_Oracle.DEQ_FIRST_MSG
        while len(results) < len(RAW_PAYLOAD_DATA):
            messages = queue.deqMany(5)
            if not messages:
                break
            for m in messages:
                results.append(m.payload.decode(connection.encoding))
        connection.commit()

    def __getAndClearRawQueue(self):
        queue = self.connection.queue(RAW_QUEUE_NAME)
        queue.deqOptions.wait = cx_Oracle.DEQ_NO_WAIT
        queue.deqOptions.navigation = cx_Oracle.DEQ_FIRST_MSG
        while queue.deqOne():
            pass
        self.connection.commit()
        return queue

    def testEnqAndDeq(self):
        "test bulk enqueue and dequeue"
        queue = self.__getAndClearRawQueue()
        messages = [self.connection.msgproperties(payload=d) \
                for d in RAW_PAYLOAD_DATA]
        queue.enqMany(messages)
        messages = queue.deqMany(len(RAW_PAYLOAD_DATA))
        data = [m.payload.decode(self.connection.encoding) for m in messages]
        self.connection.commit()
        self.assertEqual(data, RAW_PAYLOAD_DATA)

    def testDequeueEmpty(self):
        "test empty bulk dequeue"
        queue = self.__getAndClearRawQueue()
        messages = queue.deqMany(5)
        self.connection.commit()
        self.assertEqual(messages, [])

    def testDeqWithWait(self):
        "test bulk dequeue with wait"
        queue = self.__getAndClearRawQueue()
        results = []
        thread = threading.Thread(target=self.__deqInThread, args=(results,))
        thread.start()
        messages = [self.connection.msgproperties(payload=d) \
                for d in RAW_PAYLOAD_DATA]
        queue.enqOptions.visibility = cx_Oracle.ENQ_IMMEDIATE
        queue.enqMany(messages)
        thread.join()
        self.assertEqual(results, RAW_PAYLOAD_DATA)

    def testEnqAndDeqMultipleTimes(self):
        "test enqueue and dequeue multiple times"
        queue = self.__getAndClearRawQueue()
        dataToEnqueue = RAW_PAYLOAD_DATA
        for num in (2, 6, 4):
            messages = [self.connection.msgproperties(payload=d) \
                    for d in dataToEnqueue[:num]]
            dataToEnqueue = dataToEnqueue[num:]
            queue.enqMany(messages)
        self.connection.commit()
        allData = []
        for num in (3, 5, 10):
            messages = queue.deqMany(num)
            allData.extend(m.payload.decode(self.connection.encoding) \
                    for m in messages)
        self.connection.commit()
        self.assertEqual(allData, RAW_PAYLOAD_DATA)

    def testEnqAndDeqVisibility(self):
        "test visibility option for enqueue and dequeue"
        queue = self.__getAndClearRawQueue()

        # first test with ENQ_ON_COMMIT (commit required)
        queue.enqOptions.visibility = cx_Oracle.ENQ_ON_COMMIT
        props1 = self.connection.msgproperties(payload="A first message")
        props2 = self.connection.msgproperties(payload="A second message")
        queue.enqMany([props1, props2])
        otherConnection = TestEnv.GetConnection()
        otherQueue = otherConnection.queue(RAW_QUEUE_NAME)
        otherQueue.deqOptions.wait = cx_Oracle.DEQ_NO_WAIT
        otherQueue.deqOptions.visibility = cx_Oracle.DEQ_ON_COMMIT
        messages = otherQueue.deqMany(5)
        self.assertEqual(len(messages), 0)
        self.connection.commit()
        messages = otherQueue.deqMany(5)
        self.assertEqual(len(messages), 2)
        otherConnection.rollback()

        # second test with ENQ_IMMEDIATE (no commit required)
        queue.enqOptions.visibility = cx_Oracle.ENQ_IMMEDIATE
        otherQueue.deqOptions.visibility = cx_Oracle.DEQ_IMMEDIATE
        queue.enqMany([props1, props2])
        messages = otherQueue.deqMany(5)
        self.assertEqual(len(messages), 4)
        otherConnection.rollback()
        messages = otherQueue.deqMany(5)
        self.assertEqual(len(messages), 0)

if __name__ == "__main__":
    TestEnv.RunTestCases()
