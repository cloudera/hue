# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import sys
import time
from decimal import Decimal

from phoenixdb.avatica.proto import common_pb2


__all__ = [
    'Date', 'Time', 'Timestamp', 'DateFromTicks', 'TimeFromTicks', 'TimestampFromTicks',
    'Binary', 'STRING', 'BINARY', 'NUMBER', 'DATETIME', 'ROWID', 'BOOLEAN',
    'TypeHelper',
]


def Date(year, month, day):
    """Constructs an object holding a date value."""
    return datetime.date(year, month, day)


def Time(hour, minute, second):
    """Constructs an object holding a time value."""
    return datetime.time(hour, minute, second)


def Timestamp(year, month, day, hour, minute, second):
    """Constructs an object holding a datetime/timestamp value."""
    return datetime.datetime(year, month, day, hour, minute, second)


def DateFromTicks(ticks):
    """Constructs an object holding a date value from the given UNIX timestamp."""
    return Date(*time.localtime(ticks)[:3])


def TimeFromTicks(ticks):
    """Constructs an object holding a time value from the given UNIX timestamp."""
    return Time(*time.localtime(ticks)[3:6])


def TimestampFromTicks(ticks):
    """Constructs an object holding a datetime/timestamp value from the given UNIX timestamp."""
    return Timestamp(*time.localtime(ticks)[:6])


def Binary(value):
    """Constructs an object capable of holding a binary (long) string value."""
    return bytes(value)


def time_from_java_sql_time(n):
    dt = datetime.datetime(1970, 1, 1) + datetime.timedelta(milliseconds=n)
    return dt.time()


def time_to_java_sql_time(t):
    return ((t.hour * 60 + t.minute) * 60 + t.second) * 1000 + t.microsecond // 1000


def date_from_java_sql_date(n):
    return datetime.date(1970, 1, 1) + datetime.timedelta(days=n)


def date_to_java_sql_date(d):
    if isinstance(d, datetime.datetime):
        d = d.date()
    td = d - datetime.date(1970, 1, 1)
    return td.days


def datetime_from_java_sql_timestamp(n):
    return datetime.datetime(1970, 1, 1) + datetime.timedelta(milliseconds=n)


def datetime_to_java_sql_timestamp(d):
    td = d - datetime.datetime(1970, 1, 1)
    return td.microseconds // 1000 + (td.seconds + td.days * 24 * 3600) * 1000


# FIXME This doesn't seem to be used anywhere in the code
class ColumnType(object):

    def __init__(self, eq_types):
        self.eq_types = tuple(eq_types)
        self.eq_types_set = set(eq_types)

    def __eq__(self, other):
        return other in self.eq_types_set

    def __cmp__(self, other):
        if other in self.eq_types_set:
            return 0
        if other < self.eq_types:
            return 1
        else:
            return -1


STRING = ColumnType(['VARCHAR', 'CHAR'])
"""Type object that can be used to describe string-based columns."""

BINARY = ColumnType(['BINARY', 'VARBINARY'])
"""Type object that can be used to describe (long) binary columns."""

NUMBER = ColumnType([
    'INTEGER', 'UNSIGNED_INT', 'BIGINT', 'UNSIGNED_LONG', 'TINYINT', 'UNSIGNED_TINYINT',
    'SMALLINT', 'UNSIGNED_SMALLINT', 'FLOAT', 'UNSIGNED_FLOAT', 'DOUBLE', 'UNSIGNED_DOUBLE', 'DECIMAL'
])
"""Type object that can be used to describe numeric columns."""

DATETIME = ColumnType(['TIME', 'DATE', 'TIMESTAMP', 'UNSIGNED_TIME', 'UNSIGNED_DATE', 'UNSIGNED_TIMESTAMP'])
"""Type object that can be used to describe date/time columns."""

ROWID = ColumnType([])
"""Only implemented for DB API 2.0 compatibility, not used."""

BOOLEAN = ColumnType(['BOOLEAN'])
"""Type object that can be used to describe boolean columns. This is a phoenixdb-specific extension."""

if sys.version_info[0] < 3:
    _long = long  # noqa: F821
else:
    _long = int

FIELD_MAP = {
    'bool_value': [
        (common_pb2.BOOLEAN, None, None),
        (common_pb2.PRIMITIVE_BOOLEAN, None, None),
    ],
    'string_value': [
        (common_pb2.CHARACTER, None, None),
        (common_pb2.PRIMITIVE_CHAR, None, None),
        (common_pb2.STRING, None, None),
        (common_pb2.BIG_DECIMAL, str, Decimal),
    ],
    'number_value': [
        (common_pb2.INTEGER, None, int),
        (common_pb2.PRIMITIVE_INT, None, int),
        (common_pb2.SHORT, None, int),
        (common_pb2.PRIMITIVE_SHORT, None, int),
        (common_pb2.LONG, None, _long),
        (common_pb2.PRIMITIVE_LONG, None, _long),
        (common_pb2.BYTE, None, int),
        (common_pb2.JAVA_SQL_TIME, time_to_java_sql_time, time_from_java_sql_time),
        (common_pb2.JAVA_SQL_DATE, date_to_java_sql_date, date_from_java_sql_date),
        (common_pb2.JAVA_SQL_TIMESTAMP, datetime_to_java_sql_timestamp, datetime_from_java_sql_timestamp),
    ],
    'bytes_value': [
        (common_pb2.BYTE_STRING, Binary, None),
    ],
    'double_value': [
        (common_pb2.DOUBLE, float, float),
        (common_pb2.PRIMITIVE_DOUBLE, float, float)
    ]
}
"""The master map that describes how to handle types, keyed by TypedData field"""

REP_MAP = dict((v[0], (k, v[0], v[1], v[2])) for k in FIELD_MAP for v in FIELD_MAP[k])
"""Flips the available types to allow for faster lookup by protobuf Rep

This mapping should be structured as:
    {
        'common_pb2.BIG_DECIMAL': ('string_value', common_pb2.BIG_DECIMAL, str, Decimal),),
        ...
        '<Rep enum>': (<field_name>, <mutate_to function>, <cast_from function>),
    }
"""

JDBC_TO_REP = dict([
    # These are the standard types that are used in Phoenix
    (-6, common_pb2.BYTE),  # TINYINT
    (5, common_pb2.SHORT),  # SMALLINT
    (4, common_pb2.INTEGER),  # INTEGER
    (-5, common_pb2.LONG),  # BIGINT
    (6, common_pb2.DOUBLE),  # FLOAT
    (8, common_pb2.DOUBLE),  # DOUBLE
    (2, common_pb2.BIG_DECIMAL),  # NUMERIC
    (1, common_pb2.STRING),  # CHAR
    (91, common_pb2.JAVA_SQL_DATE),  # DATE
    (92, common_pb2.JAVA_SQL_TIME),  # TIME
    (93, common_pb2.JAVA_SQL_TIMESTAMP),  # TIMESTAMP
    (-2, common_pb2.BYTE_STRING),  # BINARY
    (-3, common_pb2.BYTE_STRING),  # VARBINARY
    (16, common_pb2.BOOLEAN),  # BOOLEAN
    # These are the Non-standard types defined by Phoenix
    (19, common_pb2.JAVA_SQL_DATE),  # UNSIGNED_DATE
    (15, common_pb2.DOUBLE),  # UNSIGNED_DOUBLE
    (14, common_pb2.DOUBLE),  # UNSIGNED_FLOAT
    (9, common_pb2.INTEGER),  # UNSIGNED_INT
    (10, common_pb2.LONG),  # UNSIGNED_LONG
    (13, common_pb2.SHORT),  # UNSIGNED_SMALLINT
    (20, common_pb2.JAVA_SQL_TIMESTAMP),  # UNSIGNED_TIMESTAMP
    (11, common_pb2.BYTE),  # UNSIGNED_TINYINT
    # The following are not used by Phoenix, but some of these are used by Avaticafor
    # parameter types
    (-7, common_pb2.BOOLEAN),  # BIT
    (7, common_pb2.DOUBLE),  # REAL
    (3, common_pb2.BIG_DECIMAL),  # DECIMAL
    (12, common_pb2.STRING),  # VARCHAR
    (-1, common_pb2.STRING),  # LONGVARCHAR
    (-4, common_pb2.BYTE_STRING),  # LONGVARBINARY
    (2004, common_pb2.BYTE_STRING),  # BLOB
    (2005, common_pb2.STRING),  # CLOB
    (-15, common_pb2.STRING),  # NCHAR
    (-9, common_pb2.STRING),  # NVARCHAR
    (-16, common_pb2.STRING),  # LONGNVARCHAR
    (2011, common_pb2.STRING),  # NCLOB
    (2009, common_pb2.STRING),  # SQLXML
    # Returned by Avatica for Arrays in EMPTY resultsets
    (2000, common_pb2.BYTE_STRING)  # JAVA_OBJECT
    # These are defined by JDBC, but cannot be mapped
    # NULL
    # OTHER
    # DISTINCT
    # STRUCT
    # ARRAY 2003 - We are handling this as a special case
    # REF
    # DATALINK
    # ROWID
    # REF_CURSOR
    # TIME WITH TIMEZONE
    # TIMESTAMP WITH TIMEZONE

    ])
"""Maps the JDBC Type IDs to Protobuf Reps """

JDBC_MAP = {}
for k, v in JDBC_TO_REP.items():
    JDBC_MAP[k & 0xffffffff] = REP_MAP[v]
"""Flips the available types to allow for faster lookup by JDBC type ID

It has the same format as REP_MAP, but is keyed by JDBC type ID
"""


class TypeHelper(object):

    @staticmethod
    def from_param(param):
        """Retrieves a field name and functions to cast to/from based on an AvaticaParameter object

        :param param:
            Protobuf AvaticaParameter object

        :returns: tuple ``(field_name, rep, mutate_to, cast_from, is_array)``
            WHERE
            ``field_name`` is the attribute in ``common_pb2.TypedValue``
            ``rep`` is the common_pb2.Rep enum
            ``mutate_to`` is the function to cast values into Phoenix values, if any
            ``cast_from`` is the function to cast from the Phoenix value to the Python value, if any
            ``is_array`` the param expects an array instead of scalar

        :raises:
            NotImplementedError
        """
        jdbc_code = param.parameter_type
        if jdbc_code > 2900 and jdbc_code < 3100:
            return TypeHelper._from_jdbc(jdbc_code-3000) + (True,)
        else:
            return TypeHelper._from_jdbc(jdbc_code) + (False,)

    @staticmethod
    def from_column(column):
        """Retrieves a field name and functions to cast to/from based on a TypedValue object

        :param column:
            Protobuf TypedValue object

        :returns: tuple ``(field_name, rep, mutate_to, cast_from)``
            WHERE
            ``field_name`` is the attribute in ``common_pb2.TypedValue``
            ``rep`` is the common_pb2.Rep enum
            ``mutate_to`` is the function to cast values into Phoenix values, if any
            ``cast_from`` is the function to cast from the Phoenix value to the Python value, if any

        :raises:
            NotImplementedError
        """
        if column.type.id == 2003:
            return TypeHelper._from_jdbc(column.type.component.id)
        else:
            return TypeHelper._from_jdbc(column.type.id)

    @staticmethod
    def _from_jdbc(jdbc_code):
        if jdbc_code not in JDBC_MAP:
            # This should not happen. It's either a bug, or Avatica has added new types
            raise NotImplementedError('JDBC TYPE CODE {} is not supported'.format(jdbc_code))

        return JDBC_MAP[jdbc_code]
