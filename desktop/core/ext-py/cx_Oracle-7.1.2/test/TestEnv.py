#------------------------------------------------------------------------------
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# Portions Copyright 2007-2015, Anthony Tuininga. All rights reserved.
#
# Portions Copyright 2001-2007, Computronix (Canada) Ltd., Edmonton, Alberta,
# Canada. All rights reserved.
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# Sets the environment used by the cx_Oracle test suite. Production
# applications should consider using External Authentication to
# avoid hard coded credentials.
#
# You can set values in environment variables to bypass having the test suite
# request the information it requires.
#
#     CX_ORACLE_TEST_MAIN_USER: user used for most samples
#     CX_ORACLE_TEST_MAIN_PASSWORD: password of user used for most samples
#     CX_ORACLE_TEST_PROXY_USER: user for testing proxy connections
#     CX_ORACLE_TEST_PROXY_PASSWORD: password of user for proxying
#     CX_ORACLE_TEST_CONNECT_STRING: connect string
#     CX_ORACLE_TEST_SYSDBA_USER: SYSDBA user for setting up test suite
#     CX_ORACLE_TEST_SYSDBA_PASSWORD: SYSDBA password for setting up test suite
#
# CX_ORACLE_TEST_CONNECT_STRING can be set to an Easy Connect string, or a
# Net Service Name from a tnsnames.ora file or external naming service,
# or it can be the name of a local Oracle database instance.
#
# If cx_Oracle is using Instant Client, then an Easy Connect string is
# generally appropriate. The syntax is:
#
#   [//]host_name[:port][/service_name][:server_type][/instance_name]
#
# Commonly just the host_name and service_name are needed
# e.g. "localhost/orclpdb" or "localhost/XE"
#
# If using a tnsnames.ora file, the file can be in a default
# location such as $ORACLE_HOME/network/admin/tnsnames.ora or
# /etc/tnsnames.ora.  Alternatively set the TNS_ADMIN environment
# variable and put the file in $TNS_ADMIN/tnsnames.ora.
#------------------------------------------------------------------------------

from __future__ import print_function

import cx_Oracle
import getpass
import os
import sys
import unittest

# default values
DEFAULT_MAIN_USER = "pythontest"
DEFAULT_PROXY_USER = "pythontestproxy"
DEFAULT_CONNECT_STRING = "localhost/orclpdb"

# dictionary containing all parameters; these are acquired as needed by the
# methods below (which should be used instead of consulting this dictionary
# directly) and then stored so that a value is not requested more than once
PARAMETERS = {}

def GetValue(name, label, defaultValue=""):
    value = PARAMETERS.get(name)
    if value is not None:
        return value
    envName = "CX_ORACLE_TEST_" + name
    value = os.environ.get(envName)
    if value is None:
        if defaultValue:
            label += " [%s]" % defaultValue
        label += ": "
        if defaultValue:
            value = input(label).strip()
        else:
            value = getpass.getpass(label)
        if not value:
            value = defaultValue
    PARAMETERS[name] = value
    return value

def GetMainUser():
    return GetValue("MAIN_USER", "Main User Name", DEFAULT_MAIN_USER)

def GetMainPassword():
    return GetValue("MAIN_PASSWORD", "Password for %s" % GetMainUser())

def GetProxyUser():
    return GetValue("PROXY_USER", "Proxy User Name", DEFAULT_PROXY_USER)

def GetProxyPassword():
    return GetValue("PROXY_PASSWORD", "Password for %s" % GetProxyUser())

def GetConnectString():
    return GetValue("CONNECT_STRING", "Connect String", DEFAULT_CONNECT_STRING)

def GetCharSetRatio():
    value = PARAMETERS.get("CS_RATIO")
    if value is None:
        connection = GetConnection()
        cursor = connection.cursor()
        cursor.execute("select 'X' from dual")
        col, = cursor.description
        value = col[3]
        PARAMETERS["CS_RATIO"] = value
    return value

def GetSysdbaConnectString():
    sysdbaUser = GetValue("SYSDBA_USER", "SYSDBA user", "sys")
    sysdbaPassword = GetValue("SYSDBA_PASSWORD",
            "Password for %s" % sysdbaUser)
    return "%s/%s@%s" % (sysdbaUser, sysdbaPassword, GetConnectString())

def RunSqlScript(conn, scriptName, **kwargs):
    statementParts = []
    cursor = conn.cursor()
    replaceValues = [("&" + k + ".", v) for k, v in kwargs.items()] + \
            [("&" + k, v) for k, v in kwargs.items()]
    scriptDir = os.path.dirname(os.path.abspath(sys.argv[0]))
    fileName = os.path.join(scriptDir, "sql", scriptName + "Exec.sql")
    for line in open(fileName):
        if line.strip() == "/":
            statement = "".join(statementParts).strip()
            if statement:
                for searchValue, replaceValue in replaceValues:
                    statement = statement.replace(searchValue, replaceValue)
                cursor.execute(statement)
            statementParts = []
        else:
            statementParts.append(line)
    cursor.execute("""
            select name, type, line, position, text
            from dba_errors
            where owner = upper(:owner)
            order by name, type, line, position""",
            owner = GetMainUser())
    prevName = prevObjType = None
    for name, objType, lineNum, position, text in cursor:
        if name != prevName or objType != prevObjType:
            print("%s (%s)" % (name, objType))
            prevName = name
            prevObjType = objType
        print("    %s/%s %s" % (lineNum, position, text))

def RunTestCases():
    unittest.main(testRunner=unittest.TextTestRunner(verbosity=2))

def GetConnection(**kwargs):
    return cx_Oracle.connect(GetMainUser(), GetMainPassword(),
            GetConnectString(), encoding="UTF-8", nencoding="UTF-8", **kwargs)

def GetPool(user=None, password=None, **kwargs):
    if user is None:
        user = GetMainUser()
    if password is None:
        password = GetMainPassword()
    return cx_Oracle.SessionPool(user, password, GetConnectString(),
            encoding="UTF-8", nencoding="UTF-8", **kwargs)

def GetClientVersion():
    return cx_Oracle.clientversion()

class BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.connection = GetConnection()
        self.cursor = self.connection.cursor()

    def tearDown(self):
        self.connection.close()
        del self.cursor
        del self.connection

