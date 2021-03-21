#------------------------------------------------------------------------------
# Copyright 2017, Oracle and/or its affiliates. All rights reserved.
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# Sets the environment used by most Python cx_Oracle samples. Production
# applications should consider using External Authentication to
# avoid hard coded credentials.
#
# You can set values in environment variables to override the default values.
# If the default values are not going to be used, however, the SQL script
# sql/SampleEnv.sql will also need to be modified.
#
#     CX_ORACLE_SAMPLES_MAIN_USER: user used for most samples
#     CX_ORACLE_SAMPLES_MAIN_PASSWORD: password of user used for most samples
#     CX_ORACLE_SAMPLES_EDITION_USER: user for editioning
#     CX_ORACLE_SAMPLES_EDITION_PASSWORD: password of user for editioning
#     CX_ORACLE_SAMPLES_EDITION_NAME: name of edition for editioning
#     CX_ORACLE_SAMPLES_CONNECT_STRING: connect string
#
# CX_ORACLE_SAMPLES_CONNECT_STRING can be set to an Easy Connect string, or a
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
DEFAULT_MAIN_USER = "pythondemo"
DEFAULT_MAIN_PASSWORD = "welcome"
DEFAULT_EDITION_USER = "pythoneditions"
DEFAULT_EDITION_PASSWORD = "welcome"
DEFAULT_EDITION_NAME = "python_e1"
DEFAULT_CONNECT_STRING = "localhost/orclpdb"

# values that will be used are the default values unless environment variables
# have been set as noted above
MAIN_USER = os.environ.get("CX_ORACLE_SAMPLES_MAIN_USER", DEFAULT_MAIN_USER)
MAIN_PASSWORD = os.environ.get("CX_ORACLE_SAMPLES_MAIN_PASSWORD",
        DEFAULT_MAIN_PASSWORD)
EDITION_USER = os.environ.get("CX_ORACLE_SAMPLES_EDITION_USER",
        DEFAULT_EDITION_USER)
EDITION_PASSWORD = os.environ.get("CX_ORACLE_SAMPLES_EDITION_PASSWORD",
        DEFAULT_EDITION_PASSWORD)
EDITION_NAME = os.environ.get("CX_ORACLE_SAMPLES_EDITION_NAME",
        DEFAULT_EDITION_NAME)
CONNECT_STRING = os.environ.get("CX_ORACLE_SAMPLES_CONNECT_STRING",
        DEFAULT_CONNECT_STRING)

# calculated values based on the values above
MAIN_CONNECT_STRING = "%s/%s@%s" % (MAIN_USER, MAIN_PASSWORD, CONNECT_STRING)
EDITION_CONNECT_STRING = "%s/%s@%s" % \
        (EDITION_USER, EDITION_PASSWORD, CONNECT_STRING)
DRCP_CONNECT_STRING = MAIN_CONNECT_STRING + ":pooled"

