#------------------------------------------------------------------------------
# type_converter.py (Section 6.2)
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

def ReturnNumbersAsDecimal(cursor, name, defaultType, size, precision, scale):
    if defaultType == cx_Oracle.NUMBER:
        return cursor.var(str, 9, cursor.arraysize, outconverter = decimal.Decimal)

cur.outputtypehandler = ReturnNumbersAsDecimal

for value, in cur.execute("select 0.1 from dual"):
    print("Value:", value, "* 3 =", value * 3)
