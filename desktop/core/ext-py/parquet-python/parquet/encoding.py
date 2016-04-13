import array
import math
import struct
import cStringIO
import logging

from ttypes import Type

logger = logging.getLogger("parquet")


def read_plain_boolean(fo):
    """Reads a boolean using the plain encoding"""
    raise NotImplemented


def read_plain_int32(fo):
    """Reads a 32-bit int using the plain encoding"""
    tup = struct.unpack("<i", fo.read(4))
    return tup[0]


def read_plain_int64(fo):
    """Reads a 64-bit int using the plain encoding"""
    tup = struct.unpack("<q", fo.read(8))
    return tup[0]


def read_plain_int96(fo):
    """Reads a 96-bit int using the plain encoding"""
    tup = struct.unpack("<qi", fo.read(12))
    return tup[0] << 32 | tup[1]


def read_plain_float(fo):
    """Reads a 32-bit float using the plain encoding"""
    tup = struct.unpack("<f", fo.read(4))
    return tup[0]


def read_plain_double(fo):
    """Reads a 64-bit float (double) using the plain encoding"""
    tup = struct.unpack("<d", fo.read(8))
    return tup[0]


def read_plain_byte_array(fo):
    """Reads a byte array using the plain encoding"""
    length = read_plain_int32(fo)
    return fo.read(length)


def read_plain_byte_array_fixed(fo, fixed_length):
    """Reads a byte array of the given fixed_length"""
    return fo.read(fixed_length)

DECODE_PLAIN = {
    Type.BOOLEAN: read_plain_boolean,
    Type.INT32: read_plain_int32,
    Type.INT64: read_plain_int64,
    Type.INT96: read_plain_int96,
    Type.FLOAT: read_plain_float,
    Type.DOUBLE: read_plain_double,
    Type.BYTE_ARRAY: read_plain_byte_array,
    Type.FIXED_LEN_BYTE_ARRAY: read_plain_byte_array_fixed
}


def read_plain(fo, type_, type_length):
    conv = DECODE_PLAIN[type_]
    if type_ == Type.FIXED_LEN_BYTE_ARRAY:
        return conv(fo, type_length)
    return conv(fo)


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


def byte_width(bit_width):
    "Returns the byte width for the given bit_width"
    return (bit_width + 7) / 8


def read_rle(fo, header, bit_width):
    """Read a run-length encoded run from the given fo with the given header
    and bit_width.

    The count is determined from the header and the width is used to grab the
    value that's repeated. Yields the value repeated count times.
    """
    count = header >> 1
    zero_data = "\x00\x00\x00\x00"
    data = ""
    width = byte_width(bit_width)
    if width >= 1:
        data += fo.read(1)
    if width >= 2:
        data += fo.read(1)
    if width >= 3:
        data += fo.read(1)
    if width == 4:
        data += fo.read(1)
    data = data + zero_data[len(data):]
    value = struct.unpack("<i", data)[0]
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


def read_bitpacked(fo, header, width):
    """Reads a bitpacked run of the rle/bitpack hybrid.

    Supports width >8 (crossing bytes).
    """
    num_groups = header >> 1
    count = num_groups * 8
    byte_count = (width * count)/8
    logger.debug("Reading a bit-packed run with: %s groups, count %s, bytes %s",
        num_groups, count, byte_count)
    raw_bytes = array.array('B', fo.read(byte_count)).tolist()
    current_byte = 0
    b = raw_bytes[current_byte]
    mask = _mask_for_bits(width)
    bits_wnd_l = 8
    bits_wnd_r = 0
    res = []
    total = len(raw_bytes)*8;
    while (total >= width):
        # TODO zero-padding could produce extra zero-values
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
            logger.debug("  read bitpackage: added: %s", res[-1])
        elif current_byte + 1 < len(raw_bytes):
            current_byte += 1
            b |= (raw_bytes[current_byte] << bits_wnd_l)
            bits_wnd_l += 8
    return res


def read_bitpacked_deprecated(fo, byte_count, count, width):
    raw_bytes = array.array('B', fo.read(byte_count)).tolist()

    mask = _mask_for_bits(width)
    index = 0
    res = []
    word = 0
    bits_in_word = 0
    while len(res) < count and index <= len(raw_bytes):
        logger.debug("index = %d", index)
        logger.debug("bits in word = %d", bits_in_word)
        logger.debug("word = %s", bin(word))
        if bits_in_word >= width:
            # how many bits over the value is stored
            offset = (bits_in_word - width)
            logger.debug("offset = %d", offset)

            # figure out the value
            value = (word & (mask << offset)) >> offset
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
    io_obj = fo
    if length is None:
        length = read_plain_int32(fo)
        raw_bytes = fo.read(length)
        if raw_bytes == '':
            return None
        io_obj = cStringIO.StringIO(raw_bytes)
    res = []
    while io_obj.tell() < length:
        header = read_unsigned_var_int(io_obj)
        if header & 1 == 0:
            res += read_rle(io_obj, header, width)
        else:
            res += read_bitpacked(io_obj, header, width)
    return res
