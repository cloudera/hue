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
import unittest
from decimal import Decimal

import phoenixdb
from phoenixdb.tests import DatabaseTestCase


class TypesTest(DatabaseTestCase):

    def checkIntType(self, type_name, min_value, max_value):
        self.createTable("phoenixdb_test_tbl1", "CREATE TABLE {table} (id integer primary key, val {})".format(type_name, table="{table}"))
        with self.conn.cursor() as cursor:
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (1, 1)")
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (2, NULL)")
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (3, ?)", [1])
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (4, ?)", [None])
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (5, ?)", [min_value])
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (6, ?)", [max_value])
            cursor.execute("SELECT id, val FROM phoenixdb_test_tbl1 ORDER BY id")
            self.assertEqual(cursor.description[1].type_code, phoenixdb.NUMBER)
            self.assertEqual(cursor.fetchall(), [[1, 1], [2, None], [3, 1], [4, None], [5, min_value], [6, max_value]])

            self.assertRaises(
                self.conn.DatabaseError, cursor.execute,
                "UPSERT INTO phoenixdb_test_tbl1 VALUES (100, {})".format(min_value - 1))

            self.assertRaises(
                self.conn.DatabaseError, cursor.execute,
                "UPSERT INTO phoenixdb_test_tbl1 VALUES (100, {})".format(max_value + 1))

            # XXX The server silently truncates the values
#            self.assertRaises(self.conn.DatabaseError, cursor.execute, "UPSERT INTO phoenixdb_test_tbl1 VALUES (100, ?)", [min_value - 1])
#            self.assertRaises(self.conn.DatabaseError, cursor.execute, "UPSERT INTO phoenixdb_test_tbl1 VALUES (100, ?)", [max_value + 1])

    def test_integer(self):
        self.checkIntType("integer", -2147483648, 2147483647)

    def test_unsigned_int(self):
        self.checkIntType("unsigned_int", 0, 2147483647)

    def test_bigint(self):
        self.checkIntType("bigint", -9223372036854775808, 9223372036854775807)

    def test_unsigned_long(self):
        self.checkIntType("unsigned_long", 0, 9223372036854775807)

    def test_tinyint(self):
        self.checkIntType("tinyint", -128, 127)

    def test_unsigned_tinyint(self):
        self.checkIntType("unsigned_tinyint", 0, 127)

    def test_smallint(self):
        self.checkIntType("smallint", -32768, 32767)

    def test_unsigned_smallint(self):
        self.checkIntType("unsigned_smallint", 0, 32767)

    def checkFloatType(self, type_name, min_value, max_value):
        self.createTable("phoenixdb_test_tbl1", "CREATE TABLE {table} (id integer primary key, val {})".format(type_name, table="{table}"))
        with self.conn.cursor() as cursor:
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (1, 1)")
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (2, NULL)")
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (3, ?)", [1])
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (4, ?)", [None])
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (5, ?)", [min_value])
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (6, ?)", [max_value])
            cursor.execute("SELECT id, val FROM phoenixdb_test_tbl1 ORDER BY id")
            self.assertEqual(cursor.description[1].type_code, phoenixdb.NUMBER)
            rows = cursor.fetchall()
            self.assertEqual([r[0] for r in rows], [1, 2, 3, 4, 5, 6])
            self.assertEqual(rows[0][1], 1.0)
            self.assertEqual(rows[1][1], None)
            self.assertEqual(rows[2][1], 1.0)
            self.assertEqual(rows[3][1], None)
            self.assertAlmostEqual(rows[4][1], min_value)
            self.assertAlmostEqual(rows[5][1], max_value)

    def test_float(self):
        self.checkFloatType("float", -3.4028234663852886e+38, 3.4028234663852886e+38)

    def test_unsigned_float(self):
        self.checkFloatType("unsigned_float", 0, 3.4028234663852886e+38)

    def test_double(self):
        self.checkFloatType("double", -1.7976931348623158E+308, 1.7976931348623158E+308)

    def test_unsigned_double(self):
        self.checkFloatType("unsigned_double", 0, 1.7976931348623158E+308)

    def test_decimal(self):
        self.createTable("phoenixdb_test_tbl1", "CREATE TABLE {table} (id integer primary key, val decimal(8,3))")
        with self.conn.cursor() as cursor:
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (1, 33333.333)")
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (2, NULL)")
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (3, ?)", [33333.333])
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (4, ?)", [Decimal('33333.333')])
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (5, ?)", [None])
            cursor.execute("SELECT id, val FROM phoenixdb_test_tbl1 ORDER BY id")
            self.assertEqual(cursor.description[1].type_code, phoenixdb.NUMBER)
            rows = cursor.fetchall()
            self.assertEqual([r[0] for r in rows], [1, 2, 3, 4, 5])
            self.assertEqual(rows[0][1], Decimal('33333.333'))
            self.assertEqual(rows[1][1], None)
            self.assertEqual(rows[2][1], Decimal('33333.333'))
            self.assertEqual(rows[3][1], Decimal('33333.333'))
            self.assertEqual(rows[4][1], None)
            self.assertRaises(
                self.conn.DatabaseError, cursor.execute,
                "UPSERT INTO phoenixdb_test_tbl1 VALUES (100, ?)", [Decimal('1234567890')])
            self.assertRaises(
                self.conn.DatabaseError, cursor.execute,
                "UPSERT INTO phoenixdb_test_tbl1 VALUES (101, ?)", [Decimal('123456.789')])

    def test_boolean(self):
        self.createTable("phoenixdb_test_tbl1", "CREATE TABLE {table} (id integer primary key, val boolean)")
        with self.conn.cursor() as cursor:
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (1, TRUE)")
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (2, FALSE)")
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (3, NULL)")
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (4, ?)", [True])
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (5, ?)", [False])
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (6, ?)", [None])
            cursor.execute("SELECT id, val FROM phoenixdb_test_tbl1 ORDER BY id")
            self.assertEqual(cursor.description[1].type_code, phoenixdb.BOOLEAN)
            self.assertEqual(cursor.fetchall(), [[1, True], [2, False], [3, None], [4, True], [5, False], [6, None]])

    @unittest.skip("https://issues.apache.org/jira/browse/PHOENIX-4664")
    def test_time(self):
        self.createTable("phoenixdb_test_tbl1", "CREATE TABLE {table} (id integer primary key, val time)")
        with self.conn.cursor() as cursor:
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (1, '1970-01-01 12:01:02')")
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (2, NULL)")
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (3, ?)", [phoenixdb.Time(12, 1, 2)])
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (4, ?)", [datetime.time(12, 1, 2)])
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (5, ?)", [None])
            cursor.execute("SELECT id, val FROM phoenixdb_test_tbl1 ORDER BY id")
            self.assertEqual(cursor.fetchall(), [
                [1, datetime.time(12, 1, 2)],
                [2, None],
                [3, datetime.time(12, 1, 2)],
                [4, datetime.time(12, 1, 2)],
                [5, None],
            ])

    @unittest.skip("https://issues.apache.org/jira/browse/CALCITE-797")
    def test_time_full(self):
        self.createTable("phoenixdb_test_tbl1", "CREATE TABLE {table} (id integer primary key, val time)")
        with self.conn.cursor() as cursor:
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (1, '2015-07-12 13:01:02.123')")
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (2, ?)", [datetime.datetime(2015, 7, 12, 13, 1, 2, 123000)])
            cursor.execute("SELECT id, val FROM phoenixdb_test_tbl1 ORDER BY id")
            self.assertEqual(cursor.fetchall(), [
                [1, datetime.datetime(2015, 7, 12, 13, 1, 2, 123000)],
                [2, datetime.datetime(2015, 7, 12, 13, 1, 2, 123000)],
            ])

    @unittest.skip("https://issues.apache.org/jira/browse/PHOENIX-4664")
    def test_date(self):
        self.createTable("phoenixdb_test_tbl1", "CREATE TABLE {table} (id integer primary key, val date)")
        with self.conn.cursor() as cursor:
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (1, '2015-07-12 00:00:00')")
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (3, ?)", [phoenixdb.Date(2015, 7, 12)])
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (4, ?)", [datetime.date(2015, 7, 12)])
            cursor.execute("SELECT id, val FROM phoenixdb_test_tbl1 ORDER BY id")
            self.assertEqual(cursor.fetchall(), [
                [1, datetime.date(2015, 7, 12)],
                [3, datetime.date(2015, 7, 12)],
                [4, datetime.date(2015, 7, 12)],
            ])

    @unittest.skip("https://issues.apache.org/jira/browse/CALCITE-798")
    def test_date_full(self):
        self.createTable("phoenixdb_test_tbl1", "CREATE TABLE {table} (id integer primary key, val date)")
        with self.conn.cursor() as cursor:
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (1, '2015-07-12 13:01:02.123')")
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (2, ?)", [datetime.datetime(2015, 7, 12, 13, 1, 2, 123000)])
            cursor.execute("SELECT id, val FROM phoenixdb_test_tbl1 ORDER BY id")
            self.assertEqual(cursor.fetchall(), [
                [1, datetime.datetime(2015, 7, 12, 13, 1, 2, 123000)],
                [2, datetime.datetime(2015, 7, 12, 13, 1, 2, 123000)],
            ])

    def test_date_null(self):
        self.createTable("phoenixdb_test_tbl1", "CREATE TABLE {table} (id integer primary key, val date)")
        with self.conn.cursor() as cursor:
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (1, NULL)")
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (2, ?)", [None])
            cursor.execute("SELECT id, val FROM phoenixdb_test_tbl1 ORDER BY id")  # raises NullPointerException on the server
            self.assertEqual(cursor.fetchall(), [
                [1, None],
                [2, None],
            ])

    @unittest.skip("https://issues.apache.org/jira/browse/PHOENIX-4664")
    def test_timestamp(self):
        self.createTable("phoenixdb_test_tbl1", "CREATE TABLE {table} (id integer primary key, val timestamp)")
        with self.conn.cursor() as cursor:
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (1, '2015-07-12 13:01:02.123')")
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (2, NULL)")
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (3, ?)", [phoenixdb.Timestamp(2015, 7, 12, 13, 1, 2)])
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (4, ?)", [datetime.datetime(2015, 7, 12, 13, 1, 2, 123000)])
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (5, ?)", [None])
            cursor.execute("SELECT id, val FROM phoenixdb_test_tbl1 ORDER BY id")
            self.assertEqual(cursor.fetchall(), [
                [1, datetime.datetime(2015, 7, 12, 13, 1, 2, 123000)],
                [2, None],
                [3, datetime.datetime(2015, 7, 12, 13, 1, 2)],
                [4, datetime.datetime(2015, 7, 12, 13, 1, 2, 123000)],
                [5, None],
            ])

    # Minimal date/time/timestamp type test that doesn't trigger PHOENIX-4664
    def test_time_minimal(self):
        self.createTable("phoenixdb_test_tbl1", "CREATE TABLE {table} (id integer primary key, val1 date, val2 time, val3 timestamp)")
        with self.conn.cursor() as cursor:
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (1, '2015-07-12', '2015-07-12 13:01:02', '2015-07-12 13:01:02.123')")
            cursor.execute("SELECT * FROM phoenixdb_test_tbl1 ORDER BY id")
            self.assertEqual(cursor.fetchall(), [
                [1, datetime.date(2015, 7, 12), datetime.time(13, 1, 2), datetime.datetime(2015, 7, 12, 13, 1, 2, 123000)]
            ])

    @unittest.skip("https://issues.apache.org/jira/browse/CALCITE-796")
    def test_timestamp_full(self):
        self.createTable("phoenixdb_test_tbl1", "CREATE TABLE {table} (id integer primary key, val timestamp)")
        with self.conn.cursor() as cursor:
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (1, '2015-07-12 13:01:02.123456789')")
            cursor.execute("SELECT id, val FROM phoenixdb_test_tbl1 ORDER BY id")
            self.assertEqual(cursor.fetchall(), [
                [1, datetime.datetime(2015, 7, 12, 13, 1, 2, 123456789)],
            ])

    def test_varchar(self):
        self.createTable("phoenixdb_test_tbl1", "CREATE TABLE {table} (id integer primary key, val varchar)")
        with self.conn.cursor() as cursor:
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (1, 'abc')")
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (2, NULL)")
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (3, ?)", ['abc'])
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (4, ?)", [None])
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (5, '')")
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (6, ?)", [''])
            cursor.execute("SELECT id, val FROM phoenixdb_test_tbl1 ORDER BY id")
            self.assertEqual(cursor.fetchall(), [[1, 'abc'], [2, None], [3, 'abc'], [4, None], [5, None], [6, None]])

    @unittest.skipIf(sys.version_info[0] < 3, "phoenixdb doesn't support unicode strings in Python2")
    def test_unicode(self):
        self.createTable("phoenixdb_test_tbl1", "CREATE TABLE {table} (id integer primary key, val varchar)")
        with self.conn.cursor() as cursor:
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (1, \
            '\u00E1rv\u00EDzt\u0171r\u0151 t\u00FCk\u00F6rf\u00FAr\u00F3g\u00E9p')")
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (2, '\u265E')")
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (3, '\U0001F600')")
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (4, ?)",
                           ['\u00E1rv\u00EDzt\u0171r\u0151 t\u00FCk\u00F6rf\u00FAr\u00F3g\u00E9p'])
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (5, ?)", ['\u265E'])
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (6, ?)", ['\U0001F600'])
            cursor.execute("SELECT id, val FROM phoenixdb_test_tbl1 ORDER BY id")
            self.assertEqual(cursor.fetchall(),
                             [[1, '\u00E1rv\u00EDzt\u0171r\u0151 t\u00FCk\u00F6rf\u00FAr\u00F3g\u00E9p'],
                              [2, '\u265E'], [3, '\U0001F600'],
                              [4, '\u00E1rv\u00EDzt\u0171r\u0151 t\u00FCk\u00F6rf\u00FAr\u00F3g\u00E9p'],
                              [5, '\u265E'], [6, '\U0001F600']])

    def test_varchar_very_long(self):
        self.createTable("phoenixdb_test_tbl1", "CREATE TABLE {table} (id integer primary key, val varchar)")
        with self.conn.cursor() as cursor:
            value = '1234567890' * 1000
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (1, ?)", [value])
            cursor.execute("SELECT id, val FROM phoenixdb_test_tbl1 ORDER BY id")
            self.assertEqual(cursor.fetchall(), [[1, value]])

    def test_varchar_limited(self):
        self.createTable("phoenixdb_test_tbl1", "CREATE TABLE {table} (id integer primary key, val varchar(2))")
        with self.conn.cursor() as cursor:
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (1, 'ab')")
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (2, NULL)")
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (3, ?)", ['ab'])
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (4, ?)", [None])
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (5, '')")
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (6, ?)", [''])
            cursor.execute("SELECT id, val FROM phoenixdb_test_tbl1 ORDER BY id")
            self.assertEqual(cursor.fetchall(), [[1, 'ab'], [2, None], [3, 'ab'], [4, None], [5, None], [6, None]])
            self.assertRaises(self.conn.DataError, cursor.execute, "UPSERT INTO phoenixdb_test_tbl1 VALUES (100, 'abc')")

    def test_char_null(self):
        self.createTable("phoenixdb_test_tbl1", "CREATE TABLE {table} (id integer primary key, val char(2))")
        with self.conn.cursor() as cursor:
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (2, NULL)")
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (4, ?)", [None])
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (5, '')")
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (6, ?)", [''])
            cursor.execute("SELECT id, val FROM phoenixdb_test_tbl1 ORDER BY id")
            self.assertEqual(cursor.fetchall(), [[2, None], [4, None], [5, None], [6, None]])
            self.assertRaises(self.conn.DataError, cursor.execute, "UPSERT INTO phoenixdb_test_tbl1 VALUES (100, 'abc')")

    def test_char(self):
        self.createTable("phoenixdb_test_tbl1", "CREATE TABLE {table} (id integer primary key, val char(2))")
        with self.conn.cursor() as cursor:
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (1, 'ab')")
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (2, ?)", ['ab'])
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (3, 'a')")
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (4, ?)", ['b'])
            cursor.execute("SELECT id, val FROM phoenixdb_test_tbl1 ORDER BY id")
            self.assertEqual(cursor.fetchall(), [[1, 'ab'], [2, 'ab'], [3, 'a'], [4, 'b']])
            self.assertRaises(self.conn.DataError, cursor.execute, "UPSERT INTO phoenixdb_test_tbl1 VALUES (100, 'abc')")

    def test_binary(self):
        self.createTable("phoenixdb_test_tbl1", "CREATE TABLE {table} (id integer primary key, val binary(2))")
        with self.conn.cursor() as cursor:
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (1, 'ab')")
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (2, ?)", [phoenixdb.Binary(b'ab')])
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (3, '\x01\x00')")
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (4, ?)", [phoenixdb.Binary(b'\x01\x00')])
            cursor.execute("SELECT id, val FROM phoenixdb_test_tbl1 ORDER BY id")
            self.assertEqual(cursor.fetchall(), [
                [1, b'ab'],
                [2, b'ab'],
                [3, b'\x01\x00'],
                [4, b'\x01\x00'],
            ])

    def test_binary_all_bytes(self):
        self.createTable("phoenixdb_test_tbl1", "CREATE TABLE {table} (id integer primary key, val binary(256))")
        with self.conn.cursor() as cursor:
            if sys.version_info[0] < 3:
                value = ''.join(map(chr, range(256)))
            else:
                value = bytes(range(256))
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (1, ?)", [phoenixdb.Binary(value)])
            cursor.execute("SELECT id, val FROM phoenixdb_test_tbl1 ORDER BY id")
            self.assertEqual(cursor.fetchall(), [[1, value]])

    def test_array(self):
        self.createTable("phoenixdb_test_tbl1", "CREATE TABLE {table} (id integer primary key, val integer[])")
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT id, val FROM phoenixdb_test_tbl1 ORDER BY id")
            self.assertEqual(cursor.fetchall(), [])
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (1, ARRAY[1, 2])")
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (2, ?)", [[2, 3]])
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (3, ?)", [[4]])
            cursor.execute("SELECT id, val FROM phoenixdb_test_tbl1 ORDER BY id")
            self.assertEqual(cursor.fetchall(), [
                [1, [1, 2]],
                [2, [2, 3]],
                [3, [4]],
            ])

    def test_array_boolean(self):
        self.createTable("phoenixdb_test_tbl1", "CREATE TABLE {table} (id integer primary key, val boolean[])")
        with self.conn.cursor() as cursor:
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (1, ARRAY[TRUE, TRUE, FALSE])")
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (2, NULL)")
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (3, ?)", ((1, 0, 1),))
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (4, ?)", [[True, True, True]])
            cursor.execute("UPSERT INTO phoenixdb_test_tbl1 VALUES (5, ?)", [[]])
            cursor.execute("SELECT id, val FROM phoenixdb_test_tbl1 ORDER BY id")
            self.assertEqual(cursor.fetchall(), [
                [1, [True, True, False]],
                [2, None],
                [3, [True, False, True]],
                [4, [True, True, True]],
                [5, None]
            ])
