import array
import StringIO
import unittest

import parquet.encoding


class TestBitPacked(unittest.TestCase):

    def testFromExample(self):
        raw_data_in = [0b10001000, 0b11000110, 0b11111010]
        encoded_bitstring = array.array('B', raw_data_in).tostring()
        fo = StringIO.StringIO(encoded_bitstring)
        count = 3 << 1
        res = parquet.encoding.read_bitpacked(fo, count, 3)
        self.assertEquals(range(8), res)


class TestBitPackedDeprecated(unittest.TestCase):

    def testFromExample(self):
        encoded_bitstring = array.array('B',
                                        [0b00000101, 0b00111001, 0b01110111])
        fo = StringIO.StringIO(encoded_bitstring)
        res = parquet.encoding.read_bitpacked_deprecated(fo, 3, 3)
        self.assertEquals(range(8), res)


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
