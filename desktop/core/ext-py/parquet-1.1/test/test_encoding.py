import array
import struct
import io
import unittest

from parquet import parquet_thrift
import parquet.encoding
from nose import SkipTest


class TestPlain(unittest.TestCase):

    def test_int32(self):
        self.assertEquals(
            999,
            parquet.encoding.read_plain_int32(
                io.BytesIO(struct.pack("<i", 999)), 1)[0])

    def test_int64(self):
        self.assertEquals(
            999,
            parquet.encoding.read_plain_int64(
                io.BytesIO(struct.pack("<q", 999)), 1)[0])

    def test_int96(self):
        self.assertEquals(
            999,
            parquet.encoding.read_plain_int96(
                io.BytesIO(struct.pack("<qi", 0, 999)), 1)[0])

    def test_float(self):
        self.assertAlmostEquals(
            9.99,
            parquet.encoding.read_plain_float(
                io.BytesIO(struct.pack("<f", 9.99)), 1)[0],
            2)

    def test_double(self):
        self.assertEquals(
            9.99,
            parquet.encoding.read_plain_double(
                io.BytesIO(struct.pack("<d", 9.99)), 1)[0])

    def test_fixed(self):
        data = b"foobar"
        fo = io.BytesIO(data)
        self.assertEquals(
            data[:3],
            parquet.encoding.read_plain_byte_array_fixed(
                fo, 3))
        self.assertEquals(
            data[3:],
            parquet.encoding.read_plain_byte_array_fixed(
                fo, 3))

    def test_fixed_read_plain(self):
        data = b"foobar"
        fo = io.BytesIO(data)
        self.assertEquals(
            data[:3],
            parquet.encoding.read_plain(
                fo, parquet_thrift.Type.FIXED_LEN_BYTE_ARRAY, 3))

    def test_boolean(self):
        data = 0b1101
        fo = io.BytesIO(struct.pack("<i", data))
        self.assertEquals(
            [True, False, True, True],
            parquet.encoding.read_plain_boolean(fo, 1)[:4]
        )


class TestRle(unittest.TestCase):

    def testFourByteValue(self):
        fo = io.BytesIO(struct.pack("<i", 1 << 30))
        out = parquet.encoding.read_rle(fo, 2 << 1, 30, True)
        self.assertEquals([1 << 30] * 2, list(out))


class TestVarInt(unittest.TestCase):

    def testSingleByte(self):
        fo = io.BytesIO(struct.pack("<B", 0x7F))
        out = parquet.encoding.read_unsigned_var_int(fo)
        self.assertEquals(0x7F, out)

    def testFourByte(self):
        fo = io.BytesIO(struct.pack("<BBBB", 0xFF, 0xFF, 0xFF, 0x7F))
        out = parquet.encoding.read_unsigned_var_int(fo)
        self.assertEquals(0x0FFFFFFF, out)


class TestBitPacked(unittest.TestCase):

    def testFromExample(self):
        raw_data_in = [0b10001000, 0b11000110, 0b11111010]
        encoded_bitstring = array.array('B', raw_data_in).tostring()
        fo = io.BytesIO(encoded_bitstring)
        count = 3 << 1
        res = parquet.encoding.read_bitpacked(fo, count, 3, True)
        self.assertEquals(list(range(8)), res)


class TestBitPackedDeprecated(unittest.TestCase):

    def testFromExample(self):
        encoded_bitstring = array.array(
            'B', [0b00000101, 0b00111001, 0b01110111]).tostring()
        fo = io.BytesIO(encoded_bitstring)
        res = parquet.encoding.read_bitpacked_deprecated(fo, 3, 8, 3, True)
        self.assertEquals(list(range(8)), res)


class TestWidthFromMaxInt(unittest.TestCase):

    def testWidths(self):
        self.assertEquals(0, parquet.encoding.width_from_max_int(0))
        self.assertEquals(1, parquet.encoding.width_from_max_int(1))
        self.assertEquals(2, parquet.encoding.width_from_max_int(2))
        self.assertEquals(2, parquet.encoding.width_from_max_int(3))
        self.assertEquals(3, parquet.encoding.width_from_max_int(4))
        self.assertEquals(3, parquet.encoding.width_from_max_int(5))
        self.assertEquals(3, parquet.encoding.width_from_max_int(6))
        self.assertEquals(3, parquet.encoding.width_from_max_int(7))
        self.assertEquals(4, parquet.encoding.width_from_max_int(8))
        self.assertEquals(4, parquet.encoding.width_from_max_int(15))
        self.assertEquals(5, parquet.encoding.width_from_max_int(16))
        self.assertEquals(5, parquet.encoding.width_from_max_int(31))
        self.assertEquals(6, parquet.encoding.width_from_max_int(32))
        self.assertEquals(6, parquet.encoding.width_from_max_int(63))
        self.assertEquals(7, parquet.encoding.width_from_max_int(64))
        self.assertEquals(7, parquet.encoding.width_from_max_int(127))
        self.assertEquals(8, parquet.encoding.width_from_max_int(128))
        self.assertEquals(8, parquet.encoding.width_from_max_int(255))
