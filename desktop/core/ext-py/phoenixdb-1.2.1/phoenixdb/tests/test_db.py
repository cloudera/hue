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

import unittest

import phoenixdb.cursor
from phoenixdb.connection import Connection
from phoenixdb.errors import InternalError, ProgrammingError
from phoenixdb.tests import DatabaseTestCase, TEST_DB_URL


@unittest.skipIf(TEST_DB_URL is None, "these tests require the PHOENIXDB_TEST_DB_URL environment variable set to a clean database")
class PhoenixDatabaseTest(DatabaseTestCase):

    def test_select_literal(self):
        with self.conn.cursor() as cursor:
            self.createTable("test", "CREATE TABLE {table} (id INTEGER PRIMARY KEY, text VARCHAR)")
            cursor.executemany("UPSERT INTO test VALUES (?, ?)", [[i, 'text {}'.format(i)] for i in range(10)])

        with self.conn.cursor() as cursor:
            cursor.itersize = 4
            cursor.execute("SELECT * FROM test WHERE id>1 ORDER BY id")
            self.assertEqual(cursor.fetchall(), [[i, 'text {}'.format(i)] for i in range(2, 10)])

    def test_select_parameter(self):
        with self.conn.cursor() as cursor:
            self.createTable("test", "CREATE TABLE {table} (id INTEGER PRIMARY KEY, text VARCHAR)")
            cursor.executemany("UPSERT INTO test VALUES (?, ?)", [[i, 'text {}'.format(i)] for i in range(10)])

        with self.conn.cursor() as cursor:
            cursor.itersize = 4
            cursor.execute("SELECT * FROM test WHERE id>? ORDER BY id", [1])
            self.assertEqual(cursor.fetchall(), [[i, 'text {}'.format(i)] for i in range(2, 10)])

    def _check_dict_cursor(self, cursor):
        self.createTable("test", "CREATE TABLE {table} (id INTEGER PRIMARY KEY, text VARCHAR)")
        cursor.execute("UPSERT INTO test VALUES (?, ?)", [1, 'text 1'])
        cursor.execute("SELECT * FROM test ORDER BY id")
        self.assertEqual(cursor.fetchall(), [{'ID': 1, 'TEXT': 'text 1'}])

    def test_dict_cursor_default_parameter(self):
        self.reopen(autocommit=True, cursor_factory=phoenixdb.cursor.DictCursor)

        with self.conn.cursor() as cursor:
            self._check_dict_cursor(cursor)

    def test_dict_cursor_default_attribute(self):
        self.conn.cursor_factory = phoenixdb.cursor.DictCursor

        with self.conn.cursor() as cursor:
            self._check_dict_cursor(cursor)

    def test_dict_cursor(self):
        self.reopen(autocommit=True, cursor_factory=phoenixdb.cursor.DictCursor)

        with self.conn.cursor(cursor_factory=phoenixdb.cursor.DictCursor) as cursor:
            self._check_dict_cursor(cursor)

    def test_schema(self):

        with self.conn.cursor() as cursor:
            try:
                cursor.execute("CREATE SCHEMA IF NOT EXISTS test_schema")
            except InternalError as e:
                if "phoenix.schema.isNamespaceMappingEnabled" in e.message:
                    self.skipTest(e.message)
                raise

            self.createTable("test_schema.test", "CREATE TABLE {table} (id INTEGER PRIMARY KEY, text VARCHAR)")
            cursor.execute("UPSERT INTO test_schema.test VALUES (?, ?)", [1, 'text 1'])
            cursor.execute("SELECT * FROM test_schema.test ORDER BY id")
            self.assertEqual(cursor.fetchall(), [[1, 'text 1']])

    def test_transaction(self):
        self.reopen(autocommit=False)
        with self.conn.cursor() as cursor:
            self.createTable("test", "CREATE TABLE {table} (id INTEGER PRIMARY KEY, text VARCHAR)")

            cursor.execute("UPSERT INTO test VALUES (?, ?)", [1, 'one'])
            cursor.execute("SELECT * FROM test ORDER BY id")
            self.assertEqual(cursor.fetchall(), [])

            self.conn.commit()
            cursor.execute("SELECT * FROM test ORDER BY id")
            self.assertEqual(cursor.fetchall(), [[1, 'one']])
            self.assertEqual(self.conn.autocommit, False)

            cursor.execute("UPSERT INTO test VALUES (?, ?)", [2, 'two'])
            self.conn.rollback()
            cursor.execute("SELECT * FROM test ORDER BY id")
            self.assertEqual(cursor.fetchall(), [[1, 'one']])
            self.assertEqual(self.conn.autocommit, False)

            cursor.execute("UPSERT INTO test VALUES (?, ?)", [2, 'two'])
            # Since we expose the JDBC semantics, this is an implicit commit
            self.conn.autocommit = True
            cursor.execute("SELECT * FROM test ORDER BY id")
            self.assertEqual(cursor.fetchall(), [[1, 'one'], [2, 'two']])

    def test_conn_props(self):
        phoenix_args, avatica_args = Connection._map_conn_props(
            {'autoCommit': True,
             'readonly': True,
             'transactionIsolation': 3,
             'schema': 'bubu',
             'phoenixArg': 'phoenixArg'})
        self.assertEqual(phoenix_args, {'phoenixArg': 'phoenixArg'})
        self.assertEqual(avatica_args, {'autoCommit': True,
                                        'readOnly': True,
                                        'transactionIsolation': 3,
                                        'schema': 'bubu'})

    def test_meta(self):
        with self.conn.cursor() as cursor:
            try:
                cursor.execute('drop table if exists USERS')
                cursor.execute('drop table if exists DEFAULT_TABLE')
                cursor.execute('drop table if exists A_SCHEMA.A_TABLE')
                cursor.execute('drop table if exists B_SCHMEA.B_TABLE')

                cursor.execute('create table DEFAULT_TABLE (ID integer primary key)')
                cursor.execute('create table A_SCHEMA.A_TABLE (ID_A integer primary key)')
                cursor.execute('create table B_SCHEMA.B_TABLE (ID_B integer primary key)')

                meta = self.conn.meta()

                self.assertEqual(meta.get_catalogs(), [])

                self.assertEqual(meta.get_schemas(), [
                    {'TABLE_SCHEM': '', 'TABLE_CATALOG': ''},
                    {'TABLE_SCHEM': 'A_SCHEMA', 'TABLE_CATALOG': ''},
                    {'TABLE_SCHEM': 'B_SCHEMA', 'TABLE_CATALOG': ''},
                    {'TABLE_SCHEM': 'SYSTEM', 'TABLE_CATALOG': ''}])

                self.assertEqual(meta.get_schemas(schemaPattern=''), [
                    {'TABLE_SCHEM': '', 'TABLE_CATALOG': ''}])

                self.assertEqual(meta.get_schemas(schemaPattern='A_SCHEMA'), [
                    {'TABLE_SCHEM': 'A_SCHEMA', 'TABLE_CATALOG': ''}])

                a_tables = meta.get_tables()
                self.assertTrue(len(a_tables) > 3)  # Don't know how many tables SYSTEM has

                a_tables = meta.get_tables(schemaPattern='')
                self.assertEqual(len(a_tables), 1)
                self.assertTrue(a_tables[0]['TABLE_NAME'] == 'DEFAULT_TABLE')

                a_tables = meta.get_tables(schemaPattern='A_SCHEMA')
                self.assertEqual(len(a_tables), 1)
                self.assertTrue(a_tables[0]['TABLE_NAME'] == 'A_TABLE')

                a_columns = meta.get_columns(schemaPattern='A_SCHEMA', tableNamePattern='A_TABLE')
                self.assertEqual(len(a_columns), 1)
                self.assertTrue(a_columns[0]['COLUMN_NAME'] == 'ID_A')

                self.assertTrue(all(elem in meta.get_table_types() for elem in [
                    {'TABLE_TYPE': 'INDEX'},
                    {'TABLE_TYPE': 'SEQUENCE'},
                    {'TABLE_TYPE': 'SYSTEM TABLE'},
                    {'TABLE_TYPE': 'TABLE'},
                    {'TABLE_TYPE': 'VIEW'}]))

                self.assertEqual(meta.get_type_info(), [])

            finally:
                cursor.execute('drop table if exists DEFAULT_TABLE')
                cursor.execute('drop table if exists A_SCHEMA.A_TABLE')
                cursor.execute('drop table if exists B_SCHEMA.B_TABLE')

    def test_meta2(self):
        with self.conn.cursor() as cursor:
            try:
                cursor.execute('drop table if exists DEFAULT_TABLE')
                cursor.execute('drop table if exists A_SCHEMA.A_TABLE')
                cursor.execute('drop table if exists B_SCHMEA.B_TABLE')

                cursor.execute('''create table DEFAULT_TABLE (ID integer not null, ID2 varchar not null,
                V1 integer, V2 varchar, constraint PK PRIMARY KEY (ID DESC, ID2 ASC))''')
                cursor.execute('CREATE INDEX GLOBAL_IDX ON DEFAULT_TABLE (V1) INCLUDE (V2)')
                cursor.execute('CREATE LOCAL INDEX LOCAL_IDX ON DEFAULT_TABLE (V1)')
                cursor.execute('create table A_SCHEMA.A_TABLE (ID_A integer primary key)')
                cursor.execute('create table B_SCHEMA.B_TABLE (ID_B integer primary key)')

                meta = self.conn.meta()
                self.assertTrue(len(meta.get_primary_keys(table='DEFAULT_TABLE')),
                                [{'ASC_OR_DESC': '\x00\x00\x00D',
                                  'COLUMN_NAME': 'ID',
                                  'COLUMN_SIZE': None,
                                  'DATA_TYPE': 4,
                                  'KEY_SEQ': 1,
                                  'PK_NAME': 'PK',
                                  'TABLE_CAT': None,
                                  'TABLE_NAME': 'DEFAULT_TABLE',
                                  'TABLE_SCHEM': None,
                                  'TYPE_ID': 4,
                                  'TYPE_NAME': 'INTEGER',
                                  'VIEW_CONSTANT': None},
                                 {'ASC_OR_DESC': '\x00\x00\x00A',
                                  'COLUMN_NAME': 'ID2',
                                  'COLUMN_SIZE': None,
                                  'DATA_TYPE': 12,
                                  'KEY_SEQ': 2,
                                  'PK_NAME': 'PK',
                                  'TABLE_CAT': None,
                                  'TABLE_NAME': 'DEFAULT_TABLE',
                                  'TABLE_SCHEM': None,
                                  'TYPE_ID': 12,
                                  'TYPE_NAME': 'VARCHAR',
                                  'VIEW_CONSTANT': None}])
                self.assertEqual(len(meta.get_primary_keys(schema='A_SCHEMA', table='A_TABLE')), 1)
                try:
                    self.assertEqual(len(meta.get_primary_keys(schema='A_SCHEMA', table='B_TABLE')), 0)
                    self.assertTrue(False)
                except ProgrammingError:
                    pass

                self.maxDiff = None

                self.assertEqual(meta.get_index_info(table='NON_EXISTENT'), [])

                self.assertTrue(len(meta.get_index_info(table='DEFAULT_TABLE')) > 1)

            finally:
                cursor.execute('drop table if exists DEFAULT_TABLE')
                cursor.execute('drop table if exists A_SCHEMA.A_TABLE')
                cursor.execute('drop table if exists B_SCHEMA.B_TABLE')

    @unittest.skip("https://issues.apache.org/jira/browse/PHOENIX-6004")
    def test_case_sensitivity(self):
        with self.conn.cursor() as cursor:
            try:
                cursor.execute('drop table if exists AAA')
                cursor.execute('drop table if exists "aaa"')
                cursor.execute('drop table if exists "Aaa"')

                cursor.execute('create table AAA (ID integer primary key, YYY integer)')
                cursor.execute('create table "aaa" ("ID_x" integer primary key, YYY integer, "Yyy" integer, "yyy" integer)')
                cursor.execute('create table "Aaa" (ID_X integer primary key, ZZZ integer, "Zzz" integer, "zzz" integer)')

                cursor.execute('upsert into AAA values (1, 2)')
                cursor.execute('upsert into "aaa" values (11, 12, 13, 14)')
                cursor.execute('upsert into "Aaa" values (21, 22, 23, 24)')

                cursor.execute('select YYY from AAA')
                self.assertEqual(cursor.fetchone(), [2])

                cursor.execute('select YYY from "aaa"')
                self.assertEqual(cursor.fetchone(), [12])

                cursor.execute('select "YYY" from "aaa"')
                self.assertEqual(cursor.fetchone(), [12])

                cursor.execute('select "Yyy" from "aaa"')
                self.assertEqual(cursor.fetchone(), [13])

                meta = self.conn.meta()

                self.assertEquals(len(meta.get_tables(schemaPattern='')), 3)

                print(meta.get_columns(schemaPattern='',
                                       tableNamePattern='"aaa"'))

                self.assertEquals(len(meta.get_tables(schemaPattern='',
                                                      tableNamePattern='AAA')), 1)
                self.assertEquals(len(meta.get_tables(schemaPattern='',
                                                      tableNamePattern='"aaa"')), 1)
                self.assertEquals(meta.get_columns(tableNamePattern='AAA',
                                                   columnNamePattern='YYY'), 1)
                self.assertEquals(meta.get_columns(tableNamePattern='AAA',
                                                   columnNamePattern='yyy'), 1)
                self.assertEquals(meta.get_columns(tableNamePattern='AAA',
                                                   columnNamePattern='"yyy"'), 0)
            finally:
                cursor.execute('drop table if exists AAA')
                cursor.execute('drop table if exists "aaa"')
                cursor.execute('drop table if exists "Aaa"')

    def test_param_number_mismatch(self):
        self.createTable("phoenixdb_test_param_number", "CREATE TABLE {table} (id INTEGER PRIMARY KEY, username VARCHAR, name VARCHAR)")
        with self.conn.cursor() as cursor:
            cursor.execute("UPSERT INTO phoenixdb_test_param_number VALUES (?, ?, ?)", (123, 'John Doe', 'Doe'))
            cursor.execute("SELECT * FROM phoenixdb_test_param_number")
            self.assertEqual(cursor.fetchall(), [
                [123, 'John Doe', 'Doe']
            ])
            with self.assertRaises(ProgrammingError) as cm:
                cursor.execute("UPSERT INTO phoenixdb_test_param_number VALUES (?, ?)", (123, 'John Doe', 'admin'))
            self.assertEqual("Number of placeholders (?) must match number of parameters."
                             " Number of placeholders: 2. Number of parameters: 3", cm.exception.message)
            with self.assertRaises(ProgrammingError) as cm:
                cursor.execute("UPSERT INTO phoenixdb_test_param_number VALUES (?, ?, ?)", (123, 'John Doe', 'admin', 'asd'))
            self.assertEqual("Number of placeholders (?) must match number of parameters."
                             " Number of placeholders: 3. Number of parameters: 4", cm.exception.message)
            with self.assertRaises(ProgrammingError) as cm:
                cursor.execute("UPSERT INTO phoenixdb_test_param_number VALUES (?, ?, ?)", (123, 'John Doe'))
            self.assertEqual("Number of placeholders (?) must match number of parameters."
                             " Number of placeholders: 3. Number of parameters: 2", cm.exception.message)
