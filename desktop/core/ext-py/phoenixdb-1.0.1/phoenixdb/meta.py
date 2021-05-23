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

import sys
import logging

from phoenixdb.errors import ProgrammingError
from phoenixdb.cursor import DictCursor


__all__ = ['Meta']

logger = logging.getLogger(__name__)


class Meta(object):
    """Database meta for querying MetaData
    """

    def __init__(self, connection):
        self._connection = connection

    def get_catalogs(self):
        if self._connection._closed:
            raise ProgrammingError('The connection is already closed.')
        result = self._connection._client.get_catalogs(self._connection._id)
        with DictCursor(self._connection) as cursor:
            cursor._process_result(result)
            return cursor.fetchall()

    def get_schemas(self, catalog=None, schemaPattern=None):
        if self._connection._closed:
            raise ProgrammingError('The connection is already closed.')
        result = self._connection._client.get_schemas(self._connection._id, catalog, schemaPattern)
        with DictCursor(self._connection) as cursor:
            cursor._process_result(result)
            return self._fix_default(cursor.fetchall(), schemaPattern=schemaPattern)

    def get_tables(self, catalog=None, schemaPattern=None, tableNamePattern=None, typeList=None):
        if self._connection._closed:
            raise ProgrammingError('The connection is already closed.')
        result = self._connection._client.get_tables(
            self._connection._id, catalog, schemaPattern, tableNamePattern, typeList=typeList)
        with DictCursor(self._connection) as cursor:
            cursor._process_result(result)
            return self._fix_default(cursor.fetchall(), catalog, schemaPattern)

    def get_columns(self, catalog=None, schemaPattern=None, tableNamePattern=None,
                    columnNamePattern=None):
        if self._connection._closed:
            raise ProgrammingError('The connection is already closed.')
        result = self._connection._client.get_columns(
            self._connection._id, catalog, schemaPattern, tableNamePattern, columnNamePattern)
        with DictCursor(self._connection) as cursor:
            cursor._process_result(result)
            return self._fix_default(cursor.fetchall(), catalog, schemaPattern)

    def get_table_types(self):
        if self._connection._closed:
            raise ProgrammingError('The connection is already closed.')
        result = self._connection._client.get_table_types(self._connection._id)
        with DictCursor(self._connection) as cursor:
            cursor._process_result(result)
            return cursor.fetchall()

    def get_type_info(self):
        if self._connection._closed:
            raise ProgrammingError('The connection is already closed.')
        result = self._connection._client.get_type_info(self._connection._id)
        with DictCursor(self._connection) as cursor:
            cursor._process_result(result)
            return cursor.fetchall()

    def _fix_default(self, rows, catalog=None, schemaPattern=None):
        '''Workaround for PHOENIX-6003'''
        if schemaPattern == '':
            rows = [row for row in rows if row['TABLE_SCHEM'] is None]
        if catalog == '':
            rows = [row for row in rows if row['TABLE_CATALOG'] is None]
        # Couldn't find a sane way to do it that works on 2 and 3
        if sys.version_info.major == 3:
            return [{k: v or '' for k, v in row.items()} for row in rows]
        else:
            return [{k: v or '' for k, v in row.iteritems()} for row in rows]
