#------------------------------------------------------------------------------
# connect_pool2.py (Section 2.5)
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
#------------------------------------------------------------------------------

from __future__ import print_function

import cx_Oracle
import threading
import time
import db_config

pool = cx_Oracle.SessionPool(db_config.user, db_config.pw, db_config.dsn + ":pooled",
                             min = 2, max = 5, increment = 1, threaded = True,
                             getmode = cx_Oracle.SPOOL_ATTRVAL_WAIT)

def Query():
    con = pool.acquire(cclass="PYTHONHOL", purity=cx_Oracle.ATTR_PURITY_SELF)
    #con = pool.acquire(cclass="PYTHONHOL", purity=cx_Oracle.ATTR_PURITY_NEW)
    cur = con.cursor()
    for i in range(4):
        cur.execute("select myseq.nextval from dual")
        seqval, = cur.fetchone()
        print("Thread", threading.current_thread().name, "fetched sequence =", seqval)
        #time.sleep(1)

numberOfThreads = 5
threadArray = []

for i in range(numberOfThreads):
    thread = threading.Thread(name='#'+str(i), target=Query)
    threadArray.append(thread)
    #time.sleep(4)
    thread.start()

for t in threadArray:
    t.join()

print("All done!")
