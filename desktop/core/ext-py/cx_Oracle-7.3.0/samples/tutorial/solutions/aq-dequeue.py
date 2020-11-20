#------------------------------------------------------------------------------
# aq-dequeue.py (Section 10.1)
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# Copyright (c) 2017, 2019, Oracle and/or its affiliates. All rights reserved.
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
booksType = con.gettype(BOOK_TYPE_NAME)
queue = con.queue(QUEUE_NAME, booksType)
queue.deqOptions.wait = cx_Oracle.DEQ_NO_WAIT
queue.deqOptions.visibility = cx_Oracle.DEQ_IMMEDIATE

print("\nDequeuing messages...")
while True:
    props = queue.deqOne()
    if not props:
        break
    print(props.payload.TITLE)

print("\nDone.")
