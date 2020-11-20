#------------------------------------------------------------------------------
# subclass.py (Section 9.1 and 9.2)
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
#------------------------------------------------------------------------------

from __future__ import print_function

import cx_Oracle
import db_config

class MyConnection(cx_Oracle.Connection):

    def __init__(self):
        print("Connecting to database")
        return super(MyConnection, self).__init__(db_config.user, db_config.pw, db_config.dsn)

con = MyConnection()
cur = con.cursor()

cur.execute("select count(*) from emp where deptno = :bv", (10,))
count, = cur.fetchone()
print("Number of rows:", count)
