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

from phoenixdb.tests import DatabaseTestCase


class ProgrammingErrorTest(DatabaseTestCase):

    def test_invalid_sql(self):
        with self.conn.cursor() as cursor:
            with self.assertRaises(self.conn.ProgrammingError) as cm:
                cursor.execute("UPS")
            self.assertEqual("Syntax error. Encountered \"UPS\" at line 1, column 1.", cm.exception.message)
            self.assertEqual(601, cm.exception.code)
            self.assertEqual("42P00", cm.exception.sqlstate)


class IntegrityErrorTest(DatabaseTestCase):

    def test_null_in_pk(self):
        self.createTable("phoenixdb_test_tbl1", "CREATE TABLE {table} (id integer primary key)")
        with self.conn.cursor() as cursor:
            with self.assertRaises(self.conn.IntegrityError) as cm:
                cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (NULL)")
            self.assertEqual("Constraint violation. PHOENIXDB_TEST_TBL1.ID may not be null", cm.exception.message)
            self.assertEqual(218, cm.exception.code)
            self.assertIn(cm.exception.sqlstate, ("22018", "23018"))


class DataErrorTest(DatabaseTestCase):

    def test_number_outside_of_range(self):
        self.createTable("phoenixdb_test_tbl1", "CREATE TABLE {table} (id tinyint primary key)")
        with self.conn.cursor() as cursor:
            with self.assertRaises(self.conn.DataError) as cm:
                cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (10000)")
            self.assertEqual("Type mismatch. TINYINT and INTEGER for 10000", cm.exception.message)
            self.assertEqual(203, cm.exception.code)
            self.assertEqual("22005", cm.exception.sqlstate)

    def test_division_by_zero(self):
        self.createTable("phoenixdb_test_tbl1", "CREATE TABLE {table} (id integer primary key)")
        with self.conn.cursor() as cursor:
            with self.assertRaises(self.conn.DataError) as cm:
                cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (2/0)")
            self.assertEqual("Divide by zero.", cm.exception.message)
            self.assertEqual(202, cm.exception.code)
            self.assertEqual("22012", cm.exception.sqlstate)
