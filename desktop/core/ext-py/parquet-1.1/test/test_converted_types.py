# -*- coding: UTF-8 -*-
"""test_converted_types.py - tests for decoding data to their logical data types."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import unittest
from decimal import Decimal

from parquet import parquet_thrift as pt
from parquet.converted_types import convert_column


class TestDecimal(unittest.TestCase):
    """Test the decimal converted type."""

    def test_int32(self):
        """Test decimal data stored as int32."""
        schema = pt.SchemaElement(
            type=pt.Type.INT32,
            name="test",
            converted_type=pt.ConvertedType.DECIMAL,
            scale=10,
            precision=9
        )

        self.assertEqual(
            convert_column([9876543210], schema)[0],
            Decimal('9.87654321')
        )

    def test_int64(self):
        """Test decimal data stored as int64."""
        schema = pt.SchemaElement(
            type=pt.Type.INT64,
            name="test",
            converted_type=pt.ConvertedType.DECIMAL,
            scale=3,
            precision=13
        )

        self.assertEqual(
            convert_column([1099511627776], schema)[0],
            Decimal('10995116277.76')
        )

    def test_fixedlength(self):
        """Test decimal data stored as fixed length bytes."""
        schema = pt.SchemaElement(
            type=pt.Type.FIXED_LEN_BYTE_ARRAY,
            type_length=3,
            name="test",
            converted_type=pt.ConvertedType.DECIMAL,
            scale=3,
            precision=13
        )

        self.assertEqual(
            convert_column([b'\x02\x00\x01'], schema)[0],
            Decimal('1310.73')
        )

    def test_binary(self):
        """Test decimal data stored as bytes."""
        schema = pt.SchemaElement(
            type=pt.Type.BYTE_ARRAY,
            name="test",
            converted_type=pt.ConvertedType.DECIMAL,
            scale=3,
            precision=13
        )

        self.assertEqual(
            convert_column([b'\x02\x00\x00\x00\x00\x00\x00\x00\x00\x01'], schema)[0],
            Decimal('94447329657392904273.93')
        )


class TestDateTypes(unittest.TestCase):
    """Test date types."""

    def test_date(self):
        """Test int32 encoding a date."""
        schema = pt.SchemaElement(
            type=pt.Type.INT32,
            name="test",
            converted_type=pt.ConvertedType.DATE,
        )
        self.assertEqual(
            convert_column([731888], schema)[0],
            datetime.date(2004, 11, 3)
        )

    def test_time_millis(self):
        """Test int32 encoding a timedelta in millis."""
        schema = pt.SchemaElement(
            type=pt.Type.INT32,
            name="test",
            converted_type=pt.ConvertedType.TIME_MILLIS,
        )
        self.assertEqual(
            convert_column([731888], schema)[0],
            datetime.timedelta(milliseconds=731888)
        )

    def test_timestamp_millis(self):
        """Test int64 encoding a datetime."""
        schema = pt.SchemaElement(
            type=pt.Type.INT64,
            name="test",
            converted_type=pt.ConvertedType.TIMESTAMP_MILLIS,
        )
        self.assertEqual(
            convert_column([1099511625014], schema)[0],
            datetime.datetime(2004, 11, 3, 19, 53, 45, 14 * 1000)
        )


class TestSBytes(unittest.TestCase):
    """Test encoding of bytes."""

    def test_utf8(self):
        """Test bytes representing utf-8 string."""
        schema = pt.SchemaElement(
            type=pt.Type.BYTE_ARRAY,
            name="test",
            converted_type=pt.ConvertedType.UTF8
        )
        data = b'foo\xf0\x9f\x91\xbe'
        self.assertEqual(
            convert_column([data], schema)[0],
            'foo👾'
        )

    def test_json(self):
        """Test bytes representing json."""
        schema = pt.SchemaElement(
            type=pt.Type.BYTE_ARRAY,
            name="test",
            converted_type=pt.ConvertedType.JSON
        )
        self.assertEqual(
            convert_column([b'{"foo": ["bar", "\\ud83d\\udc7e"]}'], schema)[0],
            {'foo': ['bar', '👾']}
        )

    def test_bson(self):
        """Test bytes representing bson."""
        schema = pt.SchemaElement(
            type=pt.Type.BYTE_ARRAY,
            name="test",
            converted_type=pt.ConvertedType.BSON
        )
        self.assertEqual(
            convert_column(
                [b'&\x00\x00\x00\x04foo\x00\x1c\x00\x00\x00\x020'
                 b'\x00\x04\x00\x00\x00bar\x00\x021\x00\x05\x00\x00\x00\xf0\x9f\x91\xbe\x00\x00\x00'], schema)[0],
            {'foo': ['bar', '👾']}
        )


class TestUnsignedInts(unittest.TestCase):
    """Test data types stored signed by representing unsigned ints."""

    def test_uint8(self):
        """Test decoding int32 as uint8."""
        schema = pt.SchemaElement(
            type=pt.Type.INT32,
            name="test",
            converted_type=pt.ConvertedType.UINT_8
        )
        self.assertEqual(
            convert_column([-3], schema)[0],
            253
        )

    def test_uint16(self):
        """Test decoding int32 as uint16."""
        schema = pt.SchemaElement(
            type=pt.Type.INT32,
            name="test",
            converted_type=pt.ConvertedType.UINT_16
        )
        self.assertEqual(
            convert_column([-3], schema)[0],
            65533
        )

    def test_uint32(self):
        """Test decoding int32 as uint32."""
        schema = pt.SchemaElement(
            type=pt.Type.INT32,
            name="test",
            converted_type=pt.ConvertedType.UINT_32
        )
        self.assertEqual(
            convert_column([-6884376], schema)[0],
            4288082920
        )

    def test_uint64(self):
        """Test decoding int64 as uint64."""
        schema = pt.SchemaElement(
            type=pt.Type.INT64,
            name="test",
            converted_type=pt.ConvertedType.UINT_64
        )
        self.assertEqual(
            convert_column([-6884376], schema)[0],
            18446744073702667240
        )
