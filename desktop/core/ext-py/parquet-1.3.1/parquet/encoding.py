"""encoding.py - methods for reading parquet encoded data blocks."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import array
import io
import logging
import math
import os
import struct
import sys

import thriftpy2 as thriftpy

THRIFT_FILE = os.path.join(os.path.dirname(__file__), "parquet.thrift")
parquet_thrift = thriftpy.load(THRIFT_FILE, module_name=str("parquet_thrift"))  # pylint: disable=invalid-name

logger = logging.getLogger("parquet")  # pylint: disable=invalid-name

PY3 = sys.version_info.major > 2

ARRAY_BYTE_STR = u'B' if PY3 else b'B'


def read_plain_boolean(file_obj, count):
    """Read `count` booleans using the plain encoding."""
    # for bit packed, the count is stored shifted up. But we want to pass in a count,
    # so we shift up.
    # bit width is 1 for a single-bit boolean.
    return read_bitpacked(file_obj, count << 1, 1, logger.isEnabledFor(logging.DEBUG))


def read_plain_int32(file_obj, count):
    """Read `count` 32-bit ints using the plain encoding."""
    length = 4 * count
    data = file_obj.read(length)
    if len(data) != length:
        raise EOFError("Expected {} bytes but got {} bytes".format(length, len(data)))
    res = struct.unpack("<{}i".format(count).encode("utf-8"), data)
    return res


def read_plain_int64(file_obj, count):
    """Read `count` 64-bit ints using the plain encoding."""
    return struct.unpack("<{}q".format(count).encode("utf-8"), file_obj.read(8 * count))


def read_plain_int96(file_obj, count):
    """Read `count` 96-bit ints using the plain encoding."""
    items = struct.unpack(b"<" + b"qi" * count, file_obj.read(12 * count))
    return [q << 32 | i for (q, i) in zip(items[0::2], items[1::2])]


def read_plain_float(file_obj, count):
    """Read `count` 32-bit floats using the plain encoding."""
    return struct.unpack("<{}f".format(count).encode("utf-8"), file_obj.read(4 * count))


def read_plain_double(file_obj, count):
    """Read `count` 64-bit float (double) using the plain encoding."""
    return struct.unpack("<{}d".format(count).encode("utf-8"), file_obj.read(8 * count))


def read_plain_byte_array(file_obj, count):
    """Read `count` byte arrays using the plain encoding."""
    return [file_obj.read(struct.unpack(b"<i", file_obj.read(4))[0]) for i in range(count)]


def read_plain_byte_array_fixed(file_obj, fixed_length):
    """Read a byte array of the given fixed_length."""
    return file_obj.read(fixed_length)


DECODE_PLAIN = {
    parquet_thrift.Type.BOOLEAN: read_plain_boolean,
    parquet_thrift.Type.INT32: read_plain_int32,
    parquet_thrift.Type.INT64: read_plain_int64,
    parquet_thrift.Type.INT96: read_plain_int96,
    parquet_thrift.Type.FLOAT: read_plain_float,
    parquet_thrift.Type.DOUBLE: read_plain_double,
    parquet_thrift.Type.BYTE_ARRAY: read_plain_byte_array,
    parquet_thrift.Type.FIXED_LEN_BYTE_ARRAY: read_plain_byte_array_fixed
}


def read_plain(file_obj, type_, count):
    """Read `count` items `type` from the fo using the plain encoding."""
    if count == 0:
        return []
    conv = DECODE_PLAIN[type_]
    return conv(file_obj, count)


def read_unsigned_var_int(file_obj):
    """Read a value using the unsigned, variable int encoding."""
    result = 0
    shift = 0
    while True:
        byte = struct.unpack(b"<B", file_obj.read(1))[0]
        result |= ((byte & 0x7F) << shift)
        if (byte & 0x80) == 0:
            break
        shift += 7
    return result


def read_rle(file_obj, header, bit_width, debug_logging):
    """Read a run-length encoded run from the given fo with the given header and bit_width.

    The count is determined from the header and the width is used to grab the
    value that's repeated. Yields the value repeated count times.
    """
    count = header >> 1
    zero_data = b"\x00\x00\x00\x00"
    width = (bit_width + 7) // 8
    data = file_obj.read(width)
    data = data + zero_data[len(data):]
    value = struct.unpack(b"<i", data)[0]
    if debug_logging:
        logger.debug("Read RLE group with value %s of byte-width %s and count %s",
                     value, width, count)
    for _ in range(count):
        yield value


def width_from_max_int(value):
    """Convert the value specified to a bit_width."""
    return int(math.ceil(math.log(value + 1, 2)))


def _mask_for_bits(i):
    """Generate a mask to grab `i` bits from an int value."""
    return (1 << i) - 1


def read_bitpacked(file_obj, header, width, debug_logging):
    """Read a bitpacked run of the rle/bitpack hybrid.

    Supports width >8 (crossing bytes).
    """
    num_groups = header >> 1
    count = num_groups * 8
    byte_count = (width * count) // 8
    if debug_logging:
        logger.debug("Reading a bit-packed run with: %s groups, count %s, bytes %s",
                     num_groups, count, byte_count)
    if width == 0:
        return [0 for _ in range(count)]
    raw_bytes = array.array(ARRAY_BYTE_STR, file_obj.read(byte_count)).tolist()
    current_byte = 0
    data = raw_bytes[current_byte]
    mask = _mask_for_bits(width)
    bits_wnd_l = 8
    bits_wnd_r = 0
    res = []
    total = len(raw_bytes) * 8
    while total >= width:
        # NOTE zero-padding could produce extra zero-values
        if debug_logging:
            logger.debug("  read bitpacked: width=%s window=(%s %s) b=%s,"
                         " current_byte=%s",
                         width, bits_wnd_l, bits_wnd_r, bin(data), current_byte)
        if bits_wnd_r >= 8:
            bits_wnd_r -= 8
            bits_wnd_l -= 8
            data >>= 8
        elif bits_wnd_l - bits_wnd_r >= width:
            res.append((data >> bits_wnd_r) & mask)
            total -= width
            bits_wnd_r += width
            if debug_logging:
                logger.debug("  read bitpackage: added: %s", res[-1])
        elif current_byte + 1 < len(raw_bytes):
            current_byte += 1
            data |= (raw_bytes[current_byte] << bits_wnd_l)
            bits_wnd_l += 8
    return res


def read_bitpacked_deprecated(file_obj, byte_count, count, width, debug_logging):
    """Read `count` values from `fo` using the deprecated bitpacking encoding."""
    raw_bytes = array.array(ARRAY_BYTE_STR, file_obj.read(byte_count)).tolist()

    mask = _mask_for_bits(width)
    index = 0
    res = []
    word = 0
    bits_in_word = 0
    while len(res) < count and index <= len(raw_bytes):
        if debug_logging:
            logger.debug("index = %d", index)
            logger.debug("bits in word = %d", bits_in_word)
            logger.debug("word = %s", bin(word))
        if bits_in_word >= width:
            # how many bits over the value is stored
            offset = (bits_in_word - width)

            # figure out the value
            value = (word & (mask << offset)) >> offset
            if debug_logging:
                logger.debug("offset = %d", offset)
                logger.debug("value = %d (%s)", value, bin(value))
            res.append(value)

            bits_in_word -= width
        else:
            word = (word << 8) | raw_bytes[index]
            index += 1
            bits_in_word += 8
    return res


def read_rle_bit_packed_hybrid(file_obj, width, length=None):
    """Read values from `fo` using the rel/bit-packed hybrid encoding.

    If length is not specified, then a 32-bit int is read first to grab the
    length of the encoded data.
    """
    debug_logging = logger.isEnabledFor(logging.DEBUG)
    io_obj = file_obj
    if length is None:
        length = read_plain_int32(file_obj, 1)[0]
        raw_bytes = file_obj.read(length)
        if raw_bytes == b'':
            return None
        io_obj = io.BytesIO(raw_bytes)
    res = []
    while io_obj.tell() < length:
        header = read_unsigned_var_int(io_obj)
        if header & 1 == 0:
            res += read_rle(io_obj, header, width, debug_logging)
        else:
            res += read_bitpacked(io_obj, header, width, debug_logging)
    return res
