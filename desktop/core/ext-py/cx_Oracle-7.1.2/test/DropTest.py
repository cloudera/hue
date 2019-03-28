#------------------------------------------------------------------------------
# Copyright (c) 2019, Oracle and/or its affiliates. All rights reserved.
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# DropTest.py
#
# Drops the database objects used for the cx_Oracle test suite.
#------------------------------------------------------------------------------

from __future__ import print_function

import cx_Oracle
import TestEnv

def DropTests(conn):
    print("Dropping test schemas...")
    TestEnv.RunSqlScript(conn, "DropTest",
            main_user = TestEnv.GetMainUser(),
            proxy_user = TestEnv.GetProxyUser())

if __name__ == "__main__":
    conn = cx_Oracle.connect(TestEnv.GetSysdbaConnectString(),
            mode = cx_Oracle.SYSDBA)
    DropTests(conn)
    print("Done.")

