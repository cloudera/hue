#------------------------------------------------------------------------------
# connect_pool2.py (Section 2.2 and 2.4)
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
#------------------------------------------------------------------------------

from __future__ import print_function

import cx_Oracle
import threading
import db_config

pool = cx_Oracle.SessionPool(db_config.user, db_config.pw, db_config.dsn,
                             min = 2, max = 5, increment = 1, threaded = True)

def Query():
    con = pool.acquire()
    cur = con.cursor()
    for i in range(4):
        cur.execute("select myseq.nextval from dual")
        seqval, = cur.fetchone()
        print("Thread", threading.current_thread().name, "fetched sequence =", seqval)

numberOfThreads = 2
threadArray = []

for i in range(numberOfThreads):
    thread = threading.Thread(name = '#' + str(i), target = Query)
    threadArray.append(thread)
    thread.start()

for t in threadArray:
    t.join()

print("All done!")
