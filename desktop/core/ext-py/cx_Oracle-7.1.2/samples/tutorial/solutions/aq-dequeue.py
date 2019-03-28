#------------------------------------------------------------------------------
# aq-dequeue.py (Section 10.1)
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
#------------------------------------------------------------------------------

from __future__ import print_function

import cx_Oracle
import decimal
import db_config

con = cx_Oracle.connect(db_config.user, db_config.pw, db_config.dsn)
cur = con.cursor()

BOOK_TYPE_NAME = "UDT_BOOK"
QUEUE_NAME = "BOOKS"
QUEUE_TABLE_NAME = "BOOK_QUEUE_TABLE"

# Dequeue the messages
options = con.deqoptions()
options.navigation = cx_Oracle.DEQ_FIRST_MSG
options.wait = cx_Oracle.DEQ_NO_WAIT
messageProperties = con.msgproperties()
booksType = con.gettype(BOOK_TYPE_NAME)
book = booksType.newobject()
while con.deq(QUEUE_NAME, options, messageProperties, book):
    print("Dequeued book", book.TITLE)
con.commit()
