# Copyright 2017 Dimitri Capitaine
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
import sys

import phoenixdb

from sqlalchemy import types
from sqlalchemy.engine.default import DefaultDialect, DefaultExecutionContext
from sqlalchemy.exc import CompileError
from sqlalchemy.sql.compiler import DDLCompiler
from sqlalchemy.types import BIGINT, BOOLEAN, CHAR, DATE, DECIMAL, FLOAT, INTEGER, NUMERIC,\
    SMALLINT, TIME, TIMESTAMP, VARBINARY, VARCHAR

if sys.version_info.major == 3:
    from urllib.parse import urlunsplit, SplitResult, urlencode
else:
    from urllib import urlencode
    from urlparse import urlunsplit, SplitResult


class PhoenixDDLCompiler(DDLCompiler):

    def visit_primary_key_constraint(self, constraint):
        if constraint.name is None:
            raise CompileError("can't create primary key without a name")
        return DDLCompiler.visit_primary_key_constraint(self, constraint)


AUTOCOMMIT_REGEXP = re.compile(
    r"\s*(?:UPDATE|UPSERT|CREATE|DELETE|DROP|ALTER)", re.I | re.UNICODE
)


class PhoenixExecutionContext(DefaultExecutionContext):

    def should_autocommit_text(self, statement):
        return AUTOCOMMIT_REGEXP.match(statement)


class PhoenixDialect(DefaultDialect):
    '''Phoenix dialect

    dialect:: phoenix
    :name: Phoenix

    note::

    The Phoenix dialect for SQLAlchemy is incomplete. It implements the functions required by Hue
    for basic operation, but little else.

    Connecting
    ----------

    The connection URL has the format of phoenix://host:port

    This format does not allow for specifying the http scheme, or the URL path the the server uses.
    Setting tls=True sets the server URL scheme to https.
    If the path arg is set , it used as the path of the server URL.

    The phoenix-specific authentication options can be set via the standard connect_args argument.

    Connecting to an unsecure server::

        create_engine('phoenix://localhost:8765')

    Connecting to a secure server via SPNEGO (after kinit)::

        create_engine('phoenix://localhost:8765', tls=True, connect_args={'authentication': 'SPNEGO'})

    Connecting to a secure server via Knox::

        create_engine('phoenix://localhost:8765', tls=True, path='/gateway/avatica/'\
        connect_args={'authentication':'BASIC', 'avatica_user':'user', 'avatica_password':'password'})
    '''

    name = "phoenix"

    driver = "phoenixdb"

    ddl_compiler = PhoenixDDLCompiler

    execution_ctx_cls = PhoenixExecutionContext

    def __init__(self, tls=False, path='/', **opts):
        '''
        :param tls:
            If True, then use https for connecting, otherwise use http

        :param path:
            The path component of the connection URL
        '''
        # There is no way to pass these via the SqlAlchemy url object
        self.tls = tls
        self.path = path
        super(PhoenixDialect, self).__init__(self, **opts)

    @classmethod
    def dbapi(cls):
        return phoenixdb

    def create_connect_args(self, url):
        connect_args = dict()
        if url.username is not None:
            connect_args['user'] = url.username
            if url.password is not None:
                connect_args['password'] = url.username
        phoenix_url = urlunsplit(SplitResult(
            scheme='https' if self.tls else 'http',
            netloc='{}:{}'.format(url.host, 8765 if url.port is None else url.port),
            path=self.path,
            query=urlencode(url.query),
            fragment='',
        ))
        return [phoenix_url], connect_args

    def has_table(self, connection, table_name, schema=None):
        if schema is None:
            query = "SELECT 1 FROM system.catalog WHERE table_name = ? LIMIT 1"
            params = [table_name.upper()]
        else:
            query = "SELECT 1 FROM system.catalog WHERE table_name = ? AND TABLE_SCHEM = ? LIMIT 1"
            params = [table_name.upper(), schema.upper()]
        return connection.execute(query, params).first() is not None

    def get_schema_names(self, connection, **kw):
        query = "SELECT DISTINCT TABLE_SCHEM FROM SYSTEM.CATALOG"
        return [row[0] for row in connection.execute(query)]

    def get_table_names(self, connection, schema=None, **kw):
        if schema is None:
            query = "SELECT DISTINCT table_name FROM SYSTEM.CATALOG"
            params = []
        else:
            query = "SELECT DISTINCT table_name FROM SYSTEM.CATALOG WHERE TABLE_SCHEM = ? "
            params = [schema.upper()]
        return [row[0] for row in connection.execute(query, params)]

    def get_columns(self, connection, table_name, schema=None, **kw):
        if schema is None:
            query = """SELECT COLUMN_NAME,  DATA_TYPE, NULLABLE
                    FROM system.catalog
                    WHERE table_name = ?
                    AND ORDINAL_POSITION is not null
                    ORDER BY ORDINAL_POSITION"""
            params = [table_name.upper()]
        else:
            query = """SELECT COLUMN_NAME, DATA_TYPE, NULLABLE
                    FROM system.catalog
                    WHERE TABLE_SCHEM = ?
                    AND table_name = ?
                    AND ORDINAL_POSITION is not null
                    ORDER BY ORDINAL_POSITION"""
            params = [schema.upper(), table_name.upper()]

        # get all of the fields for this table
        c = connection.execute(query, params)
        cols = []
        while True:
            row = c.fetchone()
            if row is None:
                break
            name = row[0]
            col_type = COLUMN_DATA_TYPE[row[1]]
            nullable = row[2] == 1 if True else False

            col_d = {
                'name': name,
                'type': col_type,
                'nullable': nullable,
                'default': None
            }

            cols.append(col_d)
        return cols

    # TODO This should be possible to implement
    def get_pk_constraint(self, conn, table_name, schema=None, **kw):
        return []

    def get_foreign_keys(self, conn, table_name, schema=None, **kw):
        return []

    # TODO This should be possible to implement
    def get_indexes(self, conn, table_name, schema=None, **kw):
        return []


class TINYINT(types.Integer):
    __visit_name__ = "SMALLINT"


class UNSIGNED_TINYINT(types.Integer):
    __visit_name__ = "SMALLINT"


class UNSIGNED_INTEGER(types.Integer):
    __visit_name__ = "INTEGER"


class DOUBLE(types.FLOAT):
    __visit_name__ = "FLOAT"


class UNSIGNED_DOUBLE(types.FLOAT):
    __visit_name__ = "FLOAT"


class UNSIGNED_FLOAT(types.FLOAT):
    __visit_name__ = "FLOAT"


class UNSIGNED_LONG(types.BIGINT):
    __visit_name__ = "BIGINT"


class UNSIGNED_TIME(types.TIME):
    __visit_name__ = "TIME"


class UNSIGNED_DATE(types.DATE):
    __visit_name__ = "DATE"


class UNSIGNED_TIMESTAMP(types.TIMESTAMP):
    __visit_name__ = "TIMESTAMP"


class ROWID (types.String):
    __visit_name__ = "VARCHAR"


COLUMN_DATA_TYPE = {
    -6: TINYINT,
    -5: BIGINT,
    -3: VARBINARY,
    1: CHAR,
    2: NUMERIC,
    3: DECIMAL,
    4: INTEGER,
    5: SMALLINT,
    6: FLOAT,
    8: DOUBLE,
    9: UNSIGNED_INTEGER,
    10: UNSIGNED_LONG,
    11: UNSIGNED_TINYINT,
    12: VARCHAR,
    13: ROWID,
    14: UNSIGNED_FLOAT,
    15: UNSIGNED_DOUBLE,
    16: BOOLEAN,
    18: UNSIGNED_TIME,
    19: UNSIGNED_DATE,
    20: UNSIGNED_TIMESTAMP,
    91: DATE,
    92: TIME,
    93: TIMESTAMP
}
