#------------------------------------------------------------------------------
# aq-enqueue.py (Section 10.1)
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

# Enqueue a few messages
booksType = con.gettype(BOOK_TYPE_NAME)
book1 = booksType.newobject()
book1.TITLE = "The Fellowship of the Ring"
book1.AUTHORS = "Tolkien, J.R.R."
book1.PRICE = decimal.Decimal("10.99")
book2 = booksType.newobject()
book2.TITLE = "Harry Potter and the Philosopher's Stone"
book2.AUTHORS = "Rowling, J.K."
book2.PRICE = decimal.Decimal("7.99")
options = con.enqoptions()
messageProperties = con.msgproperties()
for book in (book1, book2):
    print("Enqueuing book", book.TITLE)
    con.enq(QUEUE_NAME, options, messageProperties, book)
con.commit()
