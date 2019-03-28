#------------------------------------------------------------------------------
# query_many.py (Section 3.3)
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
#------------------------------------------------------------------------------

from __future__ import print_function

import cx_Oracle
import db_config

con = cx_Oracle.connect(db_config.user, db_config.pw, db_config.dsn)
cur = con.cursor()

cur.execute("select * from dept order by deptno")
res = cur.fetchmany(numRows=3)
print(res)

print(res[0])    # first row
print(res[0][1]) # second element of first row
