#------------------------------------------------------------------------------
# Copyright (c) 2019, Oracle and/or its affiliates. All rights reserved.
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# SetupTest.py
#
# Creates users and populates their schemas with the tables and packages
# necessary for the cx_Oracle test suite.
#------------------------------------------------------------------------------

from __future__ import print_function

import cx_Oracle

import TestEnv
import DropTest

# connect as SYSDBA
conn = cx_Oracle.connect(TestEnv.GetSysdbaConnectString(),
        mode = cx_Oracle.SYSDBA)

# drop existing users and editions, if applicable
DropTest.DropTests(conn)

# create test schemas
print("Creating test schemas...")
TestEnv.RunSqlScript(conn, "SetupTest",
        main_user = TestEnv.GetMainUser(),
        main_password = TestEnv.GetMainPassword(),
        proxy_user = TestEnv.GetProxyUser(),
        proxy_password = TestEnv.GetProxyPassword())
print("Done.")

