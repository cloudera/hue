#------------------------------------------------------------------------------
# query_one.py (Section 3.2)
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
row = cur.fetchone()
print(row)

row = cur.fetchone()
print(row)
