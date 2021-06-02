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

from phoenixdb.avatica.proto import common_pb2
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

    def get_primary_keys(self, catalog=None, schema=None, table=None):
        if self._connection._closed:
            raise ProgrammingError('The cursor is already closed.')

        state = common_pb2.QueryState()
        state.type = common_pb2.StateType.METADATA
        state.op = common_pb2.MetaDataOperation.GET_PRIMARY_KEYS
        state.has_args = True
        state.has_op = True

        catalog_arg = self._moa_string_arg_factory(catalog)
        schema_arg = self._moa_string_arg_factory(schema)
        table_arg = self._moa_string_arg_factory(table)
        state.args.extend([catalog_arg, schema_arg, table_arg])

        with DictCursor(self._connection) as cursor:
            syncResultResponse = cursor.get_sync_results(state)
            if not syncResultResponse.more_results:
                return []

            signature = common_pb2.Signature()
            signature.columns.append(self._column_meta_data_factory(1, 'TABLE_CAT', 12))
            signature.columns.append(self._column_meta_data_factory(2, 'TABLE_SCHEM', 12))
            signature.columns.append(self._column_meta_data_factory(3, 'TABLE_NAME', 12))
            signature.columns.append(self._column_meta_data_factory(4, 'COLUMN_NAME', 12))
            signature.columns.append(self._column_meta_data_factory(5, 'KEY_SEQ', 5))
            signature.columns.append(self._column_meta_data_factory(6, 'PK_NAME', 12))
            # The following are non-standard Phoenix extensions
            # This returns '\x00\x00\x00A' or '\x00\x00\x00D' , but that's consistent with Java
            signature.columns.append(self._column_meta_data_factory(7, 'ASC_OR_DESC', 12))
            signature.columns.append(self._column_meta_data_factory(8, 'DATA_TYPE', 5))
            signature.columns.append(self._column_meta_data_factory(9, 'TYPE_NAME', 12))
            signature.columns.append(self._column_meta_data_factory(10, 'COLUMN_SIZE', 5))
            signature.columns.append(self._column_meta_data_factory(11, 'TYPE_ID', 5))
            signature.columns.append(self._column_meta_data_factory(12, 'VIEW_CONSTANT', 12))

            cursor.fetch(signature)
            return cursor.fetchall()

    def get_index_info(self, catalog=None, schema=None, table=None, unique=False, approximate=False):
        if self._connection._closed:
            raise ProgrammingError('The cursor is already closed.')

        state = common_pb2.QueryState()
        state.type = common_pb2.StateType.METADATA
        state.op = common_pb2.MetaDataOperation.GET_INDEX_INFO
        state.has_args = True
        state.has_op = True

        catalog_arg = self._moa_string_arg_factory(catalog)
        schema_arg = self._moa_string_arg_factory(schema)
        table_arg = self._moa_string_arg_factory(table)
        unique_arg = self._moa_bool_arg_factory(unique)
        approximate_arg = self._moa_bool_arg_factory(approximate)

        state.args.extend([catalog_arg, schema_arg, table_arg, unique_arg, approximate_arg])

        with DictCursor(self._connection) as cursor:
            syncResultResponse = cursor.get_sync_results(state)
            if not syncResultResponse.more_results:
                return []

            signature = common_pb2.Signature()
            signature.columns.append(self._column_meta_data_factory(1, 'TABLE_CAT', 12))
            signature.columns.append(self._column_meta_data_factory(2, 'TABLE_SCHEM', 12))
            signature.columns.append(self._column_meta_data_factory(3, 'TABLE_NAME', 12))
            signature.columns.append(self._column_meta_data_factory(4, 'NON_UNIQUE', 16))
            signature.columns.append(self._column_meta_data_factory(5, 'INDEX_QUALIFIER', 12))
            signature.columns.append(self._column_meta_data_factory(6, 'INDEX_NAME', 12))
            signature.columns.append(self._column_meta_data_factory(7, 'TYPE', 5))
            signature.columns.append(self._column_meta_data_factory(8, 'ORDINAL_POSITION', 5))
            signature.columns.append(self._column_meta_data_factory(9, 'COLUMN_NAME', 12))
            signature.columns.append(self._column_meta_data_factory(10, 'ASC_OR_DESC', 12))
            signature.columns.append(self._column_meta_data_factory(11, 'CARDINALITY', 5))
            signature.columns.append(self._column_meta_data_factory(12, 'PAGES', 5))
            signature.columns.append(self._column_meta_data_factory(13, 'FILTER_CONDITION', 12))
            # The following are non-standard Phoenix extensions
            signature.columns.append(self._column_meta_data_factory(14, 'DATA_TYPE', 5))
            signature.columns.append(self._column_meta_data_factory(15, 'TYPE_NAME', 12))
            signature.columns.append(self._column_meta_data_factory(16, 'TYPE_ID', 5))
            signature.columns.append(self._column_meta_data_factory(17, 'COLUMN_FAMILY', 12))
            signature.columns.append(self._column_meta_data_factory(18, 'COLUMN_SIZE', 5))
            signature.columns.append(self._column_meta_data_factory(19, 'ARRAY_SIZE', 5))

            cursor.fetch(signature)
            return cursor.fetchall()

    def _column_meta_data_factory(self, ordinal, column_name, jdbc_code):
        cmd = common_pb2.ColumnMetaData()
        cmd.ordinal = ordinal
        cmd.column_name = column_name
        cmd.type.id = jdbc_code
        cmd.nullable = 2
        return cmd

    def _moa_string_arg_factory(self, arg):
        moa = common_pb2.MetaDataOperationArgument()
        if arg is None:
            moa.type = common_pb2.MetaDataOperationArgument.ArgumentType.NULL
        else:
            moa.type = common_pb2.MetaDataOperationArgument.ArgumentType.STRING
            moa.string_value = arg
        return moa

    def _moa_bool_arg_factory(self, arg):
        moa = common_pb2.MetaDataOperationArgument()
        if arg is None:
            moa.type = common_pb2.MetaDataOperationArgument.ArgumentType.NULL
        else:
            moa.type = common_pb2.MetaDataOperationArgument.ArgumentType.BOOL
            moa.bool_value = arg
        return moa

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
