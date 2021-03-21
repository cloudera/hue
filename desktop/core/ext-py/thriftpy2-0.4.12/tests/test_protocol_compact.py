# -*- coding: utf-8 -*-

from io import BytesIO

from thriftpy2._compat import u
from thriftpy2.thrift import TType, TPayload
from thriftpy2.utils import hexlify
from thriftpy2.protocol import compact


class TItem(TPayload):
    thrift_spec = {
        1: (TType.I32, "id", False),
        2: (TType.LIST, "phones", (TType.STRING), False),
    }
    default_spec = [("id", None), ("phones", None)]


class TPkg(TPayload):
    thrift_spec = {
        1: (TType.I32, "id", False),
        2: (TType.LIST, "items", (TType.STRUCT, TItem), False),
    }
    default_spec = [("id", None), ("items", None)]


def gen_proto(bytearray=b''):
    b = BytesIO(bytearray)
    proto = compact.TCompactProtocol(b)
    return (b, proto)


def test_pack_byte():
    b, proto = gen_proto()
    proto._write_val(TType.BYTE, 77)
    assert "4d" == hexlify(b.getvalue())


def test_unpack_byte():
    b, proto = gen_proto(b'\x4d')
    assert 77 == proto._read_val(TType.BYTE)


def test_pack_i16():
    b, proto = gen_proto()
    proto._write_val(TType.I16, 12345)
    assert "f2 c0 01" == hexlify(b.getvalue())


def test_unpack_i16():
    b, proto = gen_proto(b"\xf2\xc0\x01")
    assert 12345 == proto._read_val(TType.I16)


def test_pack_i32():
    b, proto = gen_proto()
    proto._write_val(TType.I32, 1234567890)
    assert "a4 8b b0 99 09" == hexlify(b.getvalue())


def test_unpack_i32():
    b, proto = gen_proto(b"\xa4\x8b\xb0\x99\x09")
    assert 1234567890 == proto._read_val(TType.I32)


def test_pack_i64():
    b, proto = gen_proto()
    proto._write_val(TType.I64, 1234567890123456789)
    assert "aa 84 cc de 8f bd 88 a2 22" == hexlify(b.getvalue())


def test_unpack_i64():
    b, proto = gen_proto(b"\xaa\x84\xcc\xde\x8f\xbd\x88\xa2\x22")
    assert 1234567890123456789 == proto._read_val(TType.I64)


def test_pack_double():
    b, proto = gen_proto()
    proto._write_val(TType.DOUBLE, 1234567890.1234567890)
    assert "b7 e6 87 b4 80 65 d2 41" == hexlify(b.getvalue())


def test_unpack_double():
    b, proto = gen_proto(b"\xb7\xe6\x87\xb4\x80\x65\xd2\x41")
    assert 1234567890.1234567890 == proto._read_val(TType.DOUBLE)


def test_pack_string():
    b, proto = gen_proto()
    proto._write_val(TType.STRING, "hello world!")
    assert "0c 68 65 6c 6c 6f 20 77 6f 72 6c 64 21" == \
           hexlify(b.getvalue())

    b1, proto1 = gen_proto()
    proto1._write_val(TType.STRING, "你好世界")
    assert "0c e4 bd a0 e5 a5 bd e4 b8 96 e7 95 8c" == \
           hexlify(b1.getvalue())


def test_unpack_string():
    b, proto = gen_proto(b"\x0c\x68\x65\x6c\x6c\x6f"
                         b"\x20\x77\x6f\x72\x6c\x64\x21")
    assert u('hello world!') == proto._read_val(TType.STRING)

    b, proto = gen_proto(b'\x0c\xe4\xbd\xa0\xe5\xa5'
                         b'\xbd\xe4\xb8\x96\xe7\x95\x8c')
    assert u('你好世界') == proto._read_val(TType.STRING)


def test_unpack_binary():
    b, proto = gen_proto(b'\x0c\xe4\xbd\xa0\xe5\xa5'
                         b'\xbd\xe4\xb8\x96\xe7\x95\x8c')
    proto.decode_response = False

    assert u('你好世界').encode("utf-8") == proto._read_val(TType.STRING)


def test_pack_bool():
    b, proto = gen_proto()
    proto._write_bool(True)
    assert "01" == hexlify(b.getvalue())


def test_unpack_bool():
    b, proto = gen_proto(b"\x01")
    assert proto._read_bool()


def test_pack_container_bool():
    b, proto = gen_proto()
    proto._write_val(TType.LIST, [True, False, True], TType.BOOL)
    assert "31 01 02 01" == hexlify(b.getvalue())

    b, proto = gen_proto()
    proto._write_val(TType.MAP, {"a": True}, (TType.STRING, TType.BOOL))
    assert "01 81 01 61 01" == hexlify(b.getvalue())

    b, proto = gen_proto()
    proto._write_val(TType.MAP, {"a": [True, False]},
                     (TType.STRING, (TType.LIST, TType.BOOL)))
    assert "01 89 01 61 21 01 02" == hexlify(b.getvalue())


def test_unpack_container_bool():
    b, proto = gen_proto(b"\x31\x01\x02\x01")
    assert [True, False, True] == proto._read_val(TType.LIST, TType.BOOL)

    b, proto = gen_proto(b"\x01\x81\x01\x61\x01")
    assert {u("a"): True} == proto._read_val(TType.MAP,
                                             (TType.STRING, TType.BOOL))

    b, proto = gen_proto(b"\x01\x89\x01\x61\x21\x01\x02")
    assert {u("a"): [True, False]} == proto._read_val(
        TType.MAP, (TType.STRING, (TType.LIST, TType.BOOL)))

    b, proto = gen_proto(b"\x03\x81\x01\x61\x01\x01\x63\x01\x01\x62\x02")
    bool_hash = proto._read_val(TType.MAP, (TType.STRING, TType.BOOL))
    assert bool_hash['a'] is True
    assert bool_hash['b'] is False
    assert bool_hash['c'] is True


def test_pack_list():
    b, proto = gen_proto()
    proto._write_val(TType.LIST, [1, 2, 3, 4, 5], TType.I16)
    assert "54 02 04 06 08 0a" == hexlify(b.getvalue())


def test_unpack_list():
    b, proto = gen_proto(b"\x54\x02\x04\x06\x08\x0a")
    assert [1, 2, 3, 4, 5] == proto._read_val(TType.LIST, TType.I16)


def test_pack_map():
    b, proto = gen_proto()
    proto._write_val(TType.MAP, {'a': 2}, (TType.STRING, TType.I16))
    assert "01 84 01 61 04" == hexlify(b.getvalue())


def test_unpack_map():
    b, proto = gen_proto(b"\x01\x84\x01\x61\x04")
    assert {u'a': 2} == proto._read_val(TType.MAP, (TType.STRING, TType.I16))


def test_write_message_begin():
    b, proto = gen_proto()
    proto.write_message_begin("test", 2, 1)
    assert "82 41 01 04 74 65 73 74" == \
           hexlify(b.getvalue())


def test_read_message_begin():
    b, proto = gen_proto(b"\x82\x41\x01\x04\x74\x65\x73\x74")
    res = proto.read_message_begin()
    assert res == ("test", 2, 1)


def test_write_struct():
    b, proto = gen_proto()
    item = TItem(id=123, phones=["123456", "abcdef"])
    proto.write_struct(item)
    assert ("15 f6 01 19 28 06 31 32 33 34 "
            "35 36 06 61 62 63 64 65 66 00" == hexlify(b.getvalue()))


def test_write_struct2():
    b, proto = gen_proto()
    item = TItem(id=123, phones=["123456", "abcdef"])
    proto._write_val(TType.STRUCT, item)
    assert ("15 f6 01 19 28 06 31 32 33 34 "
            "35 36 06 61 62 63 64 65 66 00" == hexlify(b.getvalue()))


def test_read_struct():
    b, proto = gen_proto(b"\x15\xf6\x01\x19\x28\x06\x31\x32\x33\x34"
                         b"\x35\x36\x06\x61\x62\x63\x64\x65\x66\x00")
    _item = TItem(id=123, phones=["123456", "abcdef"])
    _item2 = TItem()
    proto.read_struct(_item2)
    assert _item == _item2


def test_write_struct_recur():
    b, proto = gen_proto()
    item1 = TItem(id=123, phones=["123456", "abcdef"])
    item2 = TItem(id=456, phones=["123456", "abcdef"])
    pkg = TPkg(id=123, items=[item1, item2])
    proto._write_val(TType.STRUCT, pkg)
    assert ("15 f6 01 19 2c 15 f6 01 19 28 06 31 32 33 34 35 36 06 61 62 63 "
            "64 65 66 00 15 90 07 19 28 06 31 32 33 34 35 36 06 61 62 63 64 "
            "65 66 00 00" == hexlify(b.getvalue()))


def test_read_struct_recur():
    b, proto = gen_proto(b'\x15\xf6\x01\x19,\x15\xf6\x01\x19(\x06123456\x06'
                         b'abcdef\x00\x15\x90\x07\x19(\x06123456\x06abcdef'
                         b'\x00\x00')
    pkg = TPkg()
    proto.read_struct(pkg)
    item1 = TItem(id=123, phones=["123456", "abcdef"])
    item2 = TItem(id=456, phones=["123456", "abcdef"])
    _pkg = TPkg(id=123, items=[item1, item2])
    assert _pkg == pkg


def test_write_empty_struct():
    b, proto = gen_proto()
    item = TItem()
    proto.write_struct(item)
    assert "00" == hexlify(b.getvalue())


def test_read_empty_struct():
    b, proto = gen_proto(b"\x00")
    _item = TItem()
    _item2 = TItem()
    proto.read_struct(_item2)
    assert _item == _item2


def test_write_huge_struct():
    b, proto = gen_proto()
    item = TItem(id=12345, phones=["1234567890"] * 100000)
    proto.write_struct(item)
