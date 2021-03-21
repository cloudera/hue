#------------------------------------------------------------------------------
# versions.py (Section 1.5)
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# Copyright 2017, 2018, Oracle and/or its affiliates. All rights reserved.
#------------------------------------------------------------------------------

from __future__ import print_function

import cx_Oracle
import db_config

con = cx_Oracle.connect(db_config.user, db_config.pw, db_config.dsn)

print(cx_Oracle.version)
print("Database version:", con.version)
print("Client version:", cx_Oracle.clientversion())
