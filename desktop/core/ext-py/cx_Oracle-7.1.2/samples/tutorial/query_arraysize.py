#------------------------------------------------------------------------------
# query_arraysize.py (Section 3.5)
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
#------------------------------------------------------------------------------

from __future__ import print_function

import cx_Oracle
import time
import db_config

con = cx_Oracle.connect(db_config.user, db_config.pw, db_config.dsn)

start = time.time()

cur = con.cursor()
cur.arraysize = 10
cur.execute("select * from bigtab")
res = cur.fetchall()
# print(res)  # uncomment to display the query results

elapsed = (time.time() - start)
print(elapsed, "seconds")
