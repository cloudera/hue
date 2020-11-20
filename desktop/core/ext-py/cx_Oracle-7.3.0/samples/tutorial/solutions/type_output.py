#------------------------------------------------------------------------------
# type_output.py (Section 6.1)
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
#------------------------------------------------------------------------------

from __future__ import print_function

import cx_Oracle
import db_config

con = cx_Oracle.connect(db_config.user, db_config.pw, db_config.dsn)

cur = con.cursor()

print("Standard output...")
for row in cur.execute("select * from dept"):
    print(row)

def ReturnNumbersAsStrings(cursor, name, defaultType, size, precision, scale):
    if defaultType == cx_Oracle.NUMBER:
        return cursor.var(str, 9, cursor.arraysize)

print("Output type handler output...")
cur = con.cursor()
cur.outputtypehandler = ReturnNumbersAsStrings
for row in cur.execute("select * from dept"):
    print(row)
