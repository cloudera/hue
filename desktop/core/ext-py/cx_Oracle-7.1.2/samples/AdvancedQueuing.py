#------------------------------------------------------------------------------
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# Portions Copyright 2007-2015, Anthony Tuininga. All rights reserved.
#
# Portions Copyright 2001-2007, Computronix (Canada) Ltd., Edmonton, Alberta,
# Canada. All rights reserved.
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# AdvancedQueuing.py
#   This script demonstrates how to use advanced queuing using cx_Oracle. It
# makes use of a simple type and queue created in the sample setup.
#
# This script requires cx_Oracle 5.3 and higher.
#------------------------------------------------------------------------------

from __future__ import print_function

BOOK_TYPE_NAME = "UDT_BOOK"
QUEUE_NAME = "BOOKS"
QUEUE_TABLE_NAME = "BOOK_QUEUE"

import cx_Oracle
import SampleEnv
import decimal

# connect to database
connection = cx_Oracle.connect(SampleEnv.GetMainConnectString())
cursor = connection.cursor()

# dequeue all existing messages to ensure the queue is empty, just so that
# the results are consistent
booksType = connection.gettype(BOOK_TYPE_NAME)
book = booksType.newobject()
options = connection.deqoptions()
options.wait = cx_Oracle.DEQ_NO_WAIT
messageProperties = connection.msgproperties()
while connection.deq(QUEUE_NAME, options, messageProperties, book):
    pass

# enqueue a few messages
book1 = booksType.newobject()
book1.TITLE = "The Fellowship of the Ring"
book1.AUTHORS = "Tolkien, J.R.R."
book1.PRICE = decimal.Decimal("10.99")
book2 = booksType.newobject()
book2.TITLE = "Harry Potter and the Philosopher's Stone"
book2.AUTHORS = "Rowling, J.K."
book2.PRICE = decimal.Decimal("7.99")
options = connection.enqoptions()
for book in (book1, book2):
    print("Enqueuing book", book.TITLE)
    connection.enq(QUEUE_NAME, options, messageProperties, book)
connection.commit()

# dequeue the messages
options = connection.deqoptions()
options.navigation = cx_Oracle.DEQ_FIRST_MSG
options.wait = cx_Oracle.DEQ_NO_WAIT
while connection.deq(QUEUE_NAME, options, messageProperties, book):
    print("Dequeued book", book.TITLE)
connection.commit()

