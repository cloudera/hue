#------------------------------------------------------------------------------
# Copyright 2016, 2017, Oracle and/or its affiliates. All rights reserved.
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
# You can set values in environment variables to override the default values.
# If the default values are not going to be used, however, the SQL script
# sql/TestEnv.sql will also need to be modified.
#
#     CX_ORACLE_TEST_MAIN_USER: user used for most samples
#     CX_ORACLE_TEST_MAIN_PASSWORD: password of user used for most samples
#     CX_ORACLE_TEST_PROXY_USER: user for testing proxy connections
#     CX_ORACLE_TEST_PROXY_PASSWORD: password of user for proxying
#     CX_ORACLE_TEST_CONNECT_STRING: connect string
#     CX_ORACLE_TEST_ENCODING: encoding for CHAR/VARCHAR2 data
#     CX_ORACLE_TEST_NENCODING: encoding for NCHAR/NVARCHAR2 data
#     CX_ORACLE_TEST_ARRAY_SIZE: array size to use for tests
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

import os

# default values
DEFAULT_MAIN_USER = "cx_Oracle"
DEFAULT_MAIN_PASSWORD = "welcome"
DEFAULT_PROXY_USER = "cx_Oracle_proxy"
DEFAULT_PROXY_PASSWORD = "welcome"
DEFAULT_CONNECT_STRING = "localhost/orclpdb"
DEFAULT_ENCODING = "UTF-8"
DEFAULT_NENCODING = "UTF-8"
DEFAULT_ARRAY_SIZE = 5

# values that will be used are the default values unless environment variables
# have been set as noted above
MAIN_USER = os.environ.get("CX_ORACLE_TEST_MAIN_USER", DEFAULT_MAIN_USER)
MAIN_PASSWORD = os.environ.get("CX_ORACLE_TEST_MAIN_PASSWORD",
        DEFAULT_MAIN_PASSWORD)
PROXY_USER = os.environ.get("CX_ORACLE_TEST_PROXY_USER", DEFAULT_PROXY_USER)
PROXY_PASSWORD = os.environ.get("CX_ORACLE_TEST_PROXY_PASSWORD",
        DEFAULT_PROXY_PASSWORD)
CONNECT_STRING = os.environ.get("CX_ORACLE_TEST_CONNECT_STRING",
        DEFAULT_CONNECT_STRING)
ENCODING = os.environ.get("CX_ORACLE_TEST_ENCODING", DEFAULT_ENCODING)
NENCODING = os.environ.get("CX_ORACLE_TEST_NENCODING", DEFAULT_NENCODING)
ARRAY_SIZE = int(os.environ.get("CX_ORACLE_TEST_ARRAY_SIZE",
        DEFAULT_ARRAY_SIZE))

