import array
import math
import struct
import StringIO

from ttypes import Type

def read_plain_boolean(fo):
    raise NotImplemented


def read_plain_int32(fo):
    tup = struct.unpack("<i", fo.read(4))
    return tup[0]

def read_plain_int64(fo):
    tup = struct.unpack("<q", fo.read(8))
    return tup[0]

def read_plain_int96(fo):
    tup = struct.unpack("<q<i", fo.read(12))
    return tup[0] << 32 | tup[1]

def read_plain_float(fo):
    tup = struct.unpack("<f", fo.read(4))

def read_plain_double(fo):
    tup = struct.unpack("<d", fo.read(8))

def read_plain_byte_array(fo):
    length = read_plain_int32(fo)
    return fo.read(length)

def read_plain_byte_array_fixed(fo, fixed_length):
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
    return (bit_width + 7) / 8;

def read_rle(fo, header, bit_width):
    """Grabs count from the header and uses width to grab the value that's
    repeated. Returns an array with the value repeated count times."""
    count = header >> 1
    zero_data = "\x00\x00\x00\x00"
    data = ""
    width = byte_width(bit_width)
    if width >= 1:
        data += fo.read(1)
    elif width >= 2:
        data += fo.read(1)
    elif width >= 3:
        data +=  fo.read(1)
    elif width == 4:
        data = fo.read(1)
    data = data + zero_data[len(data):]
    value = struct.unpack("<i", data)[0]

    return [value]*count


def width_from_max_int(value):
    return int(math.ceil(math.log(value + 1, 2)))

def mask_for_bits(i):
    return (1 << i) - 1

def read_bitpacked(fo, header, width):
    num_groups = header >> 1;
    count = num_groups * 8
    raw_bytes = array.array('B', fo.read(count)).tolist()
    current_byte = 0
    b = raw_bytes[current_byte]
    mask = mask_for_bits(width)
    bits_in_byte = 8
    res = []
    while current_byte < width and len(res) < (count / width):
        print "width={0} bits_in_byte={1} b={2}".format(width, bits_in_byte, bin(b))
        if bits_in_byte >= width:
            res.append(b & mask)
            b >>= width
            bits_in_byte -= width
        else:
            next_b = raw_bytes[current_byte + 1]
            borrowed_bits = next_b & mask_for_bits(width - bits_in_byte)
            #print "  borrowing {0} bites".format(width - bits_in_byte)
            #print "  next_b={0}, borrowed_bits={1}".format(bin(next_b), bin(borrowed_bits))
            res.append((borrowed_bits << bits_in_byte) | b)
            b = next_b >> (width - bits_in_byte)
            #print "  shifting away: {0}".format(width - bits_in_byte)
            bits_in_byte = 8 - (width - bits_in_byte)
            current_byte += 1
        print "  added: {0}".format(res[-1])
    return res


def read_bitpacked_deprecated(fo, count, width):
    res = []
    raw_bytes = array.array('B', fo.read(count)).tolist()
    current_byte = 0
    b = raw_bytes[current_byte]
    mask = mask_for_bits(width)



def read_rle_bit_packed_hybrid(fo, width, length=None):
#    import pdb; pdb.set_trace()
    io_obj = fo
    if length is None:
        length = read_plain_int32(fo)
        raw_bytes = fo.read(length)
        if raw_bytes == '':
            return None
        io_obj = StringIO.StringIO(raw_bytes)
    res = []
    while io_obj.tell() < length:
        header = read_unsigned_var_int(io_obj)
        if header & 1 == 0:
            res += read_rle(io_obj, header, width)
        else:
            res += read_bitpacked(io_obj, header, width)
    return res
