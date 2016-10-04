"""test_encoding.py - tests for deserializing parquet data."""
import array
import io
import struct
import unittest

import parquet.encoding
from parquet import parquet_thrift


class TestPlain(unittest.TestCase):
    """Test plain encoding."""

    def test_int32(self):
        """Test reading bytes containing int32 data."""
        self.assertEqual(
            999,
            parquet.encoding.read_plain_int32(
                io.BytesIO(struct.pack(b"<i", 999)), 1)[0])

    def test_int64(self):
        """Test reading bytes containing int64 data."""
        self.assertEqual(
            999,
            parquet.encoding.read_plain_int64(
                io.BytesIO(struct.pack(b"<q", 999)), 1)[0])

    def test_int96(self):
        """Test reading bytes containing int96 data."""
        self.assertEqual(
            999,
            parquet.encoding.read_plain_int96(
                io.BytesIO(struct.pack(b"<qi", 0, 999)), 1)[0])

    def test_float(self):
        """Test reading bytes containing float data."""
        self.assertAlmostEquals(
            9.99,
            parquet.encoding.read_plain_float(
                io.BytesIO(struct.pack(b"<f", 9.99)), 1)[0],
            2)

    def test_double(self):
        """Test reading bytes containing double data."""
        self.assertEqual(
            9.99,
            parquet.encoding.read_plain_double(
                io.BytesIO(struct.pack(b"<d", 9.99)), 1)[0])

    def test_fixed(self):
        """Test reading bytes containing fixed bytes data."""
        data = b"foobar"
        fo = io.BytesIO(data)
        self.assertEqual(
            data[:3],
            parquet.encoding.read_plain_byte_array_fixed(
                fo, 3))
        self.assertEqual(
            data[3:],
            parquet.encoding.read_plain_byte_array_fixed(
                fo, 3))

    def test_fixed_read_plain(self):
        """Test reading bytes containing fixed bytes data."""
        data = b"foobar"
        fo = io.BytesIO(data)
        self.assertEqual(
            data[:3],
            parquet.encoding.read_plain(
                fo, parquet_thrift.Type.FIXED_LEN_BYTE_ARRAY, 3))

    def test_boolean(self):
        """Test reading bytes containing boolean data."""
        data = 0b1101
        fo = io.BytesIO(struct.pack(b"<i", data))
        self.assertEqual(
            [True, False, True, True],
            parquet.encoding.read_plain_boolean(fo, 1)[:4]
        )


class TestRle(unittest.TestCase):
    """Test reading run-length encoded data."""

    def testFourByteValue(self):
        """Test reading a run with a single four-byte value."""
        fo = io.BytesIO(struct.pack(b"<i", 1 << 30))
        out = parquet.encoding.read_rle(fo, 2 << 1, 30, True)
        self.assertEqual([1 << 30] * 2, list(out))


class TestVarInt(unittest.TestCase):
    """Test reading variable-int encoded values."""

    def testSingleByte(self):
        """Test reading a single byte value."""
        fo = io.BytesIO(struct.pack(b"<B", 0x7F))
        out = parquet.encoding.read_unsigned_var_int(fo)
        self.assertEqual(0x7F, out)

    def testFourByte(self):
        """Test reading a four byte value."""
        fo = io.BytesIO(struct.pack(b"<BBBB", 0xFF, 0xFF, 0xFF, 0x7F))
        out = parquet.encoding.read_unsigned_var_int(fo)
        self.assertEqual(0x0FFFFFFF, out)


class TestBitPacked(unittest.TestCase):
    """Test reading bit-packed encoded data."""

    def testFromExample(self):
        """Test a simple example."""
        raw_data_in = [0b10001000, 0b11000110, 0b11111010]
        encoded_bitstring = array.array('B', raw_data_in).tostring()
        fo = io.BytesIO(encoded_bitstring)
        count = 3 << 1
        res = parquet.encoding.read_bitpacked(fo, count, 3, True)
        self.assertEqual(list(range(8)), res)


class TestBitPackedDeprecated(unittest.TestCase):
    """Test reading the deprecated bit-packed encoded data."""

    def testFromExample(self):
        """Test a simple example."""
        encoded_bitstring = array.array(
            'B', [0b00000101, 0b00111001, 0b01110111]).tostring()
        fo = io.BytesIO(encoded_bitstring)
        res = parquet.encoding.read_bitpacked_deprecated(fo, 3, 8, 3, True)
        self.assertEqual(list(range(8)), res)


class TestWidthFromMaxInt(unittest.TestCase):
    """Test determining the max width for an int."""

    def testWidths(self):
        """Test all possible widths for a single byte."""
        self.assertEqual(0, parquet.encoding.width_from_max_int(0))
        self.assertEqual(1, parquet.encoding.width_from_max_int(1))
        self.assertEqual(2, parquet.encoding.width_from_max_int(2))
        self.assertEqual(2, parquet.encoding.width_from_max_int(3))
        self.assertEqual(3, parquet.encoding.width_from_max_int(4))
        self.assertEqual(3, parquet.encoding.width_from_max_int(5))
        self.assertEqual(3, parquet.encoding.width_from_max_int(6))
        self.assertEqual(3, parquet.encoding.width_from_max_int(7))
        self.assertEqual(4, parquet.encoding.width_from_max_int(8))
        self.assertEqual(4, parquet.encoding.width_from_max_int(15))
        self.assertEqual(5, parquet.encoding.width_from_max_int(16))
        self.assertEqual(5, parquet.encoding.width_from_max_int(31))
        self.assertEqual(6, parquet.encoding.width_from_max_int(32))
        self.assertEqual(6, parquet.encoding.width_from_max_int(63))
        self.assertEqual(7, parquet.encoding.width_from_max_int(64))
        self.assertEqual(7, parquet.encoding.width_from_max_int(127))
        self.assertEqual(8, parquet.encoding.width_from_max_int(128))
        self.assertEqual(8, parquet.encoding.width_from_max_int(255))
