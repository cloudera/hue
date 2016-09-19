from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import array
import io
import math
import os
import struct
import logging

import thriftpy

THRIFT_FILE = os.path.join(os.path.dirname(__file__), "parquet.thrift")
parquet_thrift = thriftpy.load(THRIFT_FILE, module_name=str("parquet_thrift"))

logger = logging.getLogger("parquet")


def read_plain_boolean(fo, count):
    """Reads `count` booleans using the plain encoding"""
    # for bit packed, the count is stored shifted up. But we want to pass in a count,
    # so we shift up.
    # bit width is 1 for a single-bit boolean.
    return read_bitpacked(fo, count << 1, 1, logger.isEnabledFor(logging.DEBUG))


def read_plain_int32(fo, count):
    """Reads `count` 32-bit ints using the plain encoding"""
    length = 4 * count
    data = fo.read(length)
    if len(data) != length:
        raise EOFError("Expected {} bytes but got {} bytes".format(length, len(data)))
    res = struct.unpack("<{}i".format(count), data)
    return res


def read_plain_int64(fo, count):
    """Reads `count` 64-bit ints using the plain encoding"""
    return struct.unpack("<{}q".format(count), fo.read(8 * count))


def read_plain_int96(fo, count):
    """Reads `count` 96-bit ints using the plain encoding"""
    items = struct.unpack("<qi" * count, fo.read(12) * count)
    args = [iter(items)] * 2
    return [q << 32 | i for (q, i) in zip(*args)]


def read_plain_float(fo, count):
    """Reads `count` 32-bit floats using the plain encoding"""
    return struct.unpack("<{}f".format(count), fo.read(4 * count))


def read_plain_double(fo, count):
    """Reads `count` 64-bit float (double) using the plain encoding"""
    return struct.unpack("<{}d".format(count), fo.read(8 * count))


def read_plain_byte_array(fo, count):
    """Read `count` byte arrays using the plain encoding"""
    return [fo.read(struct.unpack("<i", fo.read(4))[0]) for i in range(count)]


def read_plain_byte_array_fixed(fo, fixed_length):
    """Reads a byte array of the given fixed_length"""
    return fo.read(fixed_length)


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


def read_plain(fo, type_, count):
    """Reads `count` items `type` from the fo using the plain encoding."""
    if count == 0:
        return []
    conv = DECODE_PLAIN[type_]
    return conv(fo, count)


def read_unsigned_var_int(fo):
    result = 0
    shift = 0
    while True:
        byte = struct.unpack("<B", fo.read(1))[0]
        result |= ((byte & 0x7F) << shift)
        if (byte & 0x80) == 0:
            break
        shift += 7
    return result


def read_rle(fo, header, bit_width, debug_logging):
    """Read a run-length encoded run from the given fo with the given header
    and bit_width.

    The count is determined from the header and the width is used to grab the
    value that's repeated. Yields the value repeated count times.
    """
    count = header >> 1
    zero_data = b"\x00\x00\x00\x00"
    width = (bit_width + 7) // 8
    data = fo.read(width)
    data = data + zero_data[len(data):]
    value = struct.unpack("<i", data)[0]
    if debug_logging:
        logger.debug("Read RLE group with value %s of byte-width %s and count %s",
                     value, width, count)
    for i in range(count):
        yield value


def width_from_max_int(value):
    """Converts the value specified to a bit_width."""
    return int(math.ceil(math.log(value + 1, 2)))


def _mask_for_bits(i):
    """Helper function for read_bitpacked to generage a mask to grab i bits."""
    return (1 << i) - 1


def read_bitpacked(fo, header, width, debug_logging):
    """Reads a bitpacked run of the rle/bitpack hybrid.

    Supports width >8 (crossing bytes).
    """
    num_groups = header >> 1
    count = num_groups * 8
    byte_count = (width * count) // 8
    if debug_logging:
        logger.debug("Reading a bit-packed run with: %s groups, count %s, bytes %s",
            num_groups, count, byte_count)
    raw_bytes = array.array(str('B'), fo.read(byte_count)).tolist()
    current_byte = 0
    b = raw_bytes[current_byte]
    mask = _mask_for_bits(width)
    bits_wnd_l = 8
    bits_wnd_r = 0
    res = []
    total = len(raw_bytes)*8;
    while (total >= width):
        # TODO zero-padding could produce extra zero-values
        if debug_logging:
            logger.debug("  read bitpacked: width=%s window=(%s %s) b=%s,"
                         " current_byte=%s",
                         width, bits_wnd_l, bits_wnd_r, bin(b), current_byte)
        if bits_wnd_r >= 8:
            bits_wnd_r -= 8
            bits_wnd_l -= 8
            b >>= 8
        elif bits_wnd_l - bits_wnd_r >= width:
            res.append((b >> bits_wnd_r) & mask)
            total -= width
            bits_wnd_r += width
            if debug_logging:
                logger.debug("  read bitpackage: added: %s", res[-1])
        elif current_byte + 1 < len(raw_bytes):
            current_byte += 1
            b |= (raw_bytes[current_byte] << bits_wnd_l)
            bits_wnd_l += 8
    return res


def read_bitpacked_deprecated(fo, byte_count, count, width, debug_logging):
    raw_bytes = array.array(str('B'), fo.read(byte_count)).tolist()

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


def read_rle_bit_packed_hybrid(fo, width, length=None):
    """Implemenation of a decoder for the rel/bit-packed hybrid encoding.

    If length is not specified, then a 32-bit int is read first to grab the
    length of the encoded data.
    """
    debug_logging = logger.isEnabledFor(logging.DEBUG)
    io_obj = fo
    if length is None:
        length = read_plain_int32(fo, 1)[0]
        raw_bytes = fo.read(length)
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
