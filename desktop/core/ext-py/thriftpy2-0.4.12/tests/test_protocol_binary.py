# -*- coding: utf-8 -*-

from io import BytesIO

from thriftpy2._compat import u
from thriftpy2.thrift import TType, TPayload
from thriftpy2.utils import hexlify
from thriftpy2.protocol import binary as proto


class TItem(TPayload):
    thrift_spec = {
        1: (TType.I32, "id", False),
        2: (TType.LIST, "phones", (TType.STRING), False),
    }
    default_spec = [("id", None), ("phones", None)]


def test_pack_i8():
    b = BytesIO()
    proto.write_val(b, TType.I08, 123)
    assert "7b" == hexlify(b.getvalue())


def test_unpack_i8():
    b = BytesIO(b"{")
    assert 123 == proto.read_val(b, TType.I08)


def test_pack_i16():
    b = BytesIO()
    proto.write_val(b, TType.I16, 12345)
    assert "30 39" == hexlify(b.getvalue())


def test_unpack_i16():
    b = BytesIO(b"09")
    assert 12345 == proto.read_val(b, TType.I16)


def test_pack_i32():
    b = BytesIO()
    proto.write_val(b, TType.I32, 1234567890)
    assert "49 96 02 d2" == hexlify(b.getvalue())


def test_unpack_i32():
    b = BytesIO(b"I\x96\x02\xd2")
    assert 1234567890 == proto.read_val(b, TType.I32)


def test_pack_i64():
    b = BytesIO()
    proto.write_val(b, TType.I64, 1234567890123456789)
    assert "11 22 10 f4 7d e9 81 15" == hexlify(b.getvalue())


def test_unpack_i64():
    b = BytesIO(b"\x11\"\x10\xf4}\xe9\x81\x15")
    assert 1234567890123456789 == proto.read_val(b, TType.I64)


def test_pack_double():
    b = BytesIO()
    proto.write_val(b, TType.DOUBLE, 1234567890.1234567890)
    assert "41 d2 65 80 b4 87 e6 b7" == hexlify(b.getvalue())


def test_unpack_double():
    b = BytesIO(b"A\xd2e\x80\xb4\x87\xe6\xb7")
    assert 1234567890.1234567890 == proto.read_val(b, TType.DOUBLE)


def test_pack_string():
    b = BytesIO()
    proto.write_val(b, TType.STRING, "hello world!")
    assert "00 00 00 0c 68 65 6c 6c 6f 20 77 6f 72 6c 64 21" == \
        hexlify(b.getvalue())

    b = BytesIO()
    proto.write_val(b, TType.STRING, u("你好世界"))
    assert "00 00 00 0c e4 bd a0 e5 a5 bd e4 b8 96 e7 95 8c" == \
        hexlify(b.getvalue())


def test_unpack_string():
    b = BytesIO(b"\x00\x00\x00\x0c"
                b"\xe4\xbd\xa0\xe5\xa5\xbd\xe4\xb8\x96\xe7\x95\x8c")
    assert u("你好世界") == proto.read_val(b, TType.STRING)


def test_unpack_binary():
    bs = BytesIO(b"\x00\x00\x00\x0c"
                 b"\xe4\xbd\xa0\xe5\xa5\xbd\xe4\xb8\x96\xe7\x95\x8c")
    assert u("你好世界").encode("utf-8") == proto.read_val(
        bs, TType.STRING, decode_response=False)


def test_write_message_begin():
    b = BytesIO()
    proto.TBinaryProtocol(b).write_message_begin("test", TType.STRING, 1)
    assert "80 01 00 0b 00 00 00 04 74 65 73 74 00 00 00 01" == \
        hexlify(b.getvalue())


def test_write_message_begin_not_strict():
    b = BytesIO()
    proto.TBinaryProtocol(b, strict_write=False) \
        .write_message_begin("test", TType.STRING, 1)
    assert "00 00 00 04 74 65 73 74 0b 00 00 00 01" == \
        hexlify(b.getvalue())


def test_read_message_begin():
    b = BytesIO(b"\x80\x01\x00\x0b\x00\x00\x00\x04test\x00\x00\x00\x01")
    res = proto.TBinaryProtocol(b).read_message_begin()
    assert res == ("test", TType.STRING, 1)


def test_read_message_begin_not_strict():
    b = BytesIO(b"\x00\x00\x00\x04test\x0b\x00\x00\x00\x01")
    res = proto.TBinaryProtocol(b, strict_read=False).read_message_begin()
    assert res == ("test", TType.STRING, 1)


def test_write_struct():
    b = BytesIO()
    item = TItem(id=123, phones=["123456", "abcdef"])
    proto.TBinaryProtocol(b).write_struct(item)
    assert ("08 00 01 00 00 00 7b 0f 00 02 0b 00 00 00 02 00 00 00 "
            "06 31 32 33 34 35 36 00 00 00 06 61 62 63 64 65 66 00") == \
        hexlify(b.getvalue())


def test_read_struct():
    b = BytesIO(b"\x08\x00\x01\x00\x00\x00{\x0f\x00\x02\x0b\x00\x00\x00"
                b"\x02\x00\x00\x00\x06123456\x00\x00\x00\x06abcdef\x00")
    _item = TItem(id=123, phones=["123456", "abcdef"])
    _item2 = TItem()
    proto.TBinaryProtocol(b).read_struct(_item2)
    assert _item == _item2


def test_write_empty_struct():
    b = BytesIO()
    item = TItem()
    proto.TBinaryProtocol(b).write_struct(item)
    assert "00" == hexlify(b.getvalue())


def test_read_empty_struct():
    b = BytesIO(b"\x00")
    _item = TItem()
    _item2 = TItem()
    proto.TBinaryProtocol(b).read_struct(_item2)
    assert _item == _item2


def test_write_huge_struct():
    b = BytesIO()
    item = TItem(id=12345, phones=["1234567890"] * 100000)
    proto.TBinaryProtocol(b).write_struct(item)
