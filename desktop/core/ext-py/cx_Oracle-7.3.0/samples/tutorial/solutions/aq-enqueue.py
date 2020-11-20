#------------------------------------------------------------------------------
# aq-enqueue.py (Section 10.1)
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

# Enqueue a few messages
print("Enqueuing messages...")

BOOK_DATA = [
    ("The Fellowship of the Ring", "Tolkien, J.R.R.", decimal.Decimal("10.99")),
    ("Harry Potter and the Philosopher's Stone", "Rowling, J.K.", decimal.Decimal("7.99"))
]

booksType = con.gettype(BOOK_TYPE_NAME)
queue = con.queue(QUEUE_NAME, booksType)

for title, authors, price in BOOK_DATA:
    book = booksType.newobject()
    book.TITLE = title
    book.AUTHORS = authors
    book.PRICE = price
    print(title)
    queue.enqOne(con.msgproperties(payload=book, expiration=4))
    con.commit()
