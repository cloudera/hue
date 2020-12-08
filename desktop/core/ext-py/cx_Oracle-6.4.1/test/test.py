#------------------------------------------------------------------------------
# Copyright 2016, 2017, Oracle and/or its affiliates. All rights reserved.
#
# Portions Copyright 2007-2015, Anthony Tuininga. All rights reserved.
#
# Portions Copyright 2001-2007, Computronix (Canada) Ltd., Edmonton, Alberta,
# Canada. All rights reserved.
#------------------------------------------------------------------------------

"""Runs all defined unit tests."""

from __future__ import print_function

import cx_Oracle
import imp
import os
import sys
import TestEnv
import unittest

inSetup = (os.path.basename(sys.argv[0]).lower() == "setup.py")

print("Running tests for cx_Oracle version", cx_Oracle.version,
        "built at", cx_Oracle.buildtime)
print("File:", cx_Oracle.__file__)
print("Client Version:", ".".join(str(i) for i in cx_Oracle.clientversion()))
sys.stdout.flush()

connection = cx_Oracle.Connection(TestEnv.MAIN_USER, TestEnv.MAIN_PASSWORD,
        TestEnv.CONNECT_STRING, encoding = TestEnv.ENCODING,
        nencoding = TestEnv.NENCODING)
print("Server Version:", connection.version)
sys.stdout.flush()

if len(sys.argv) > 1 and not inSetup:
    moduleNames = [os.path.splitext(v)[0] for v in sys.argv[1:]]
else:
    moduleNames = [
            "Module",
            "Connection",
            "Cursor",
            "CursorVar",
            "DateTimeVar",
            "DMLReturning",
            "Error",
            "IntervalVar",
            "LobVar",
            "LongVar",
            "NCharVar",
            "NumberVar",
            "ObjectVar",
            "SessionPool",
            "StringVar",
            "TimestampVar",
            "AQ",
            "Rowid",
            "Subscription"
    ]
    clientVersion = cx_Oracle.clientversion()
    if clientVersion[:2] >= (12, 1):
        moduleNames.append("BooleanVar")
        moduleNames.append("Features12_1")

class BaseTestCase(unittest.TestCase):

    def getConnection(self, **kwargs):
        import cx_Oracle
        import TestEnv
        return cx_Oracle.Connection(TestEnv.MAIN_USER, TestEnv.MAIN_PASSWORD,
                TestEnv.CONNECT_STRING, encoding = TestEnv.ENCODING,
                nencoding = TestEnv.NENCODING, **kwargs)

    def setUp(self):
        import TestEnv
        self.connection = self.getConnection()
        self.cursor = self.connection.cursor()
        self.cursor.arraysize = TestEnv.ARRAY_SIZE

    def tearDown(self):
        del self.cursor
        del self.connection


# determine character set ratio in use in order to determine the buffer size
# that will be reported in cursor.description; this depends on the database
# character set and the client character set
cursor = connection.cursor()
cursor.execute("select 'X' from dual")
col, = cursor.description
csratio = col[3]

loader = unittest.TestLoader()
runner = unittest.TextTestRunner(verbosity = 2)
failures = []
for name in moduleNames:
    fileName = name + ".py"
    print()
    print("Running tests in", fileName)
    if inSetup:
        fileName = os.path.join("test", fileName)
    module = imp.new_module(name)
    setattr(module, "CLIENT_VERSION", cx_Oracle.clientversion())
    setattr(module, "USERNAME", TestEnv.MAIN_USER)
    setattr(module, "PASSWORD", TestEnv.MAIN_PASSWORD)
    setattr(module, "PROXY_USERNAME", TestEnv.PROXY_USER)
    setattr(module, "PROXY_PASSWORD", TestEnv.PROXY_PASSWORD)
    setattr(module, "TNSENTRY", TestEnv.CONNECT_STRING)
    setattr(module, "ENCODING", TestEnv.ENCODING)
    setattr(module, "NENCODING", TestEnv.NENCODING)
    setattr(module, "ARRAY_SIZE", TestEnv.ARRAY_SIZE)
    setattr(module, "CS_RATIO", csratio)
    setattr(module, "TestCase", unittest.TestCase)
    setattr(module, "BaseTestCase", BaseTestCase)
    setattr(module, "cx_Oracle", cx_Oracle)
    if sys.version_info[0] >= 3:
        exec(open(fileName, encoding = "UTF-8").read(), module.__dict__)
    else:
        execfile(fileName, module.__dict__)
    tests = loader.loadTestsFromModule(module)
    result = runner.run(tests)
    if not result.wasSuccessful():
        failures.append(name)
if failures:
    print("***** Some tests in the following modules failed. *****")
    for name in failures:
        print("      %s" % name)
    sys.exit(1)

