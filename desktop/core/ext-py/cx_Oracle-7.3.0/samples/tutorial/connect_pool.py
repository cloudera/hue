#------------------------------------------------------------------------------
# connect_pool.py (Section 2.1)
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

thread1 = threading.Thread(name='#1', target=Query)
thread1.start()

thread2 = threading.Thread(name='#2', target=Query)
thread2.start()

thread1.join()
thread2.join()

print("All done!")
