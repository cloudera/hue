#------------------------------------------------------------------------------
# aq.py (Section 10.1)
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

# Cleanup
cur.execute(
    """begin
         dbms_aqadm.stop_queue('""" + QUEUE_NAME + """');
         dbms_aqadm.drop_queue('""" + QUEUE_NAME + """');
         dbms_aqadm.drop_queue_table('""" + QUEUE_TABLE_NAME + """');
         execute immediate 'drop type """ + BOOK_TYPE_NAME + """';
         exception when others then
           if sqlcode <> -24010 then
             raise;
           end if;
       end;""")

# Create type
print("Creating books type UDT_BOOK...")
cur.execute("""
        create type %s as object (
            title varchar2(100),
            authors varchar2(100),
            price number(5,2)
        );""" % BOOK_TYPE_NAME)

# Create queue table and queue and start the queue
print("Creating queue table...")
cur.callproc("dbms_aqadm.create_queue_table",
             (QUEUE_TABLE_NAME, BOOK_TYPE_NAME))
cur.callproc("dbms_aqadm.create_queue", (QUEUE_NAME, QUEUE_TABLE_NAME))
cur.callproc("dbms_aqadm.start_queue", (QUEUE_NAME,))

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

# Dequeue the messages
options = con.deqoptions()
options.navigation = cx_Oracle.DEQ_FIRST_MSG
options.wait = cx_Oracle.DEQ_NO_WAIT
while con.deq(QUEUE_NAME, options, messageProperties, book):
    print("Dequeued book", book.TITLE)
con.commit()
