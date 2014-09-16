"""Define test environment."""

import cx_Oracle
import os
import sys
import unittest

def GetValue(name, label):
    value = os.environ.get("CX_ORACLE_" + name)
    if value is None:
        value = raw_input(label + ": ")
    if hasattr(cx_Oracle, "UNICODE") or sys.version_info[0] >= 3:
        return value
    return unicode(value)

USERNAME = GetValue("USERNAME", "user name")
PASSWORD = GetValue("PASSWORD", "password")
TNSENTRY = GetValue("TNSENTRY", "TNS entry")
ARRAY_SIZE = int(GetValue("ARRAY_SIZE", "array size"))

