#------------------------------------------------------------------------------
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# Portions Copyright 2007-2015, Anthony Tuininga. All rights reserved.
#
# Portions Copyright 2001-2007, Computronix (Canada) Ltd., Edmonton, Alberta,
# Canada. All rights reserved.
#------------------------------------------------------------------------------

"""Runs all defined unit tests."""

from __future__ import print_function

import cx_Oracle
import os
import sys
import TestEnv
import unittest

# display version of cx_Oracle and Oracle client for which tests are being run
print("Running tests for cx_Oracle version", cx_Oracle.version,
        "built at", cx_Oracle.buildtime)
print("File:", cx_Oracle.__file__)
print("Client Version:", ".".join(str(i) for i in cx_Oracle.clientversion()))
sys.stdout.flush()

# verify that we can connect to the database and display database version
connection = TestEnv.GetConnection()
print("Server Version:", connection.version)
sys.stdout.flush()

# define test cases to run
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
if clientVersion[:2] >= (18, 3):
    moduleNames.append("SodaDatabase")
    moduleNames.append("SodaCollection")

# run all test cases
failures = []
loader = unittest.TestLoader()
runner = unittest.TextTestRunner(verbosity = 2)
for name in moduleNames:
    print()
    print("Running tests in", name)
    tests = loader.loadTestsFromName(name + ".TestCase")
    result = runner.run(tests)
    if not result.wasSuccessful():
        failures.append(name)
if failures:
    print("***** Some tests in the following modules failed. *****")
    for name in failures:
        print("      %s" % name)
    sys.exit(1)

