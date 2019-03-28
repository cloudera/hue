#------------------------------------------------------------------------------
# rowfactory.py (Section 8.1)
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
#------------------------------------------------------------------------------

from __future__ import print_function

import collections
import cx_Oracle
import db_config

con = cx_Oracle.connect(db_config.user, db_config.pw, db_config.dsn)
cur = con.cursor()

cur.execute("select deptno, dname from dept")
res = cur.fetchall()

print('Array indexes:')
for row in res:
    print(row[0], "->", row[1])

print('Loop target variables:')
for c1, c2 in res:
    print(c1, "->", c2)
