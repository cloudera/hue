# -*- coding: utf-8 -*-

import collections
import multiprocessing
import os
import time

import pytest

from thriftpy2._compat import u
from thriftpy2.thrift import TType, TPayload, TDecodeException
from thriftpy2.transport import TSocket, TServerSocket
from thriftpy2.utils import hexlify

from thriftpy2._compat import PYPY
pytestmark = pytest.mark.skipif(PYPY,
                                reason="cython not enabled in pypy.")
if not PYPY:
    from thriftpy2.protocol import cybin as proto
    from thriftpy2.transport.memory import TCyMemoryBuffer
    from thriftpy2.transport.buffered import TCyBufferedTransport


class TItem(TPayload):
    thrift_spec = {
        1: (TType.I32, "id", False),
        2: (TType.LIST, "phones", TType.STRING, False),
    }
    default_spec = [("id", None), ("phones", None)]


def test_write_bool():
    b = TCyMemoryBuffer()
    proto.write_val(b, TType.BOOL, 1)
    b.flush()

    assert "01" == hexlify(b.getvalue())


def test_read_bool():
    b = TCyMemoryBuffer(b'\x01')
    val = proto.read_val(b, TType.BOOL)

    assert True is val


def test_write_i8():
    b = TCyMemoryBuffer()
    proto.write_val(b, TType.I08, 123)
    b.flush()

    assert "7b" == hexlify(b.getvalue())


def test_read_i8():
    b = TCyMemoryBuffer(b'\x7b')
    val = proto.read_val(b, TType.I08)

    assert 123 == val


def test_write_i16():
    b = TCyMemoryBuffer()
    proto.write_val(b, TType.I16, 12345)
    b.flush()

    assert "30 39" == hexlify(b.getvalue())


def test_read_i16():
    b = TCyMemoryBuffer(b"09")
    val = proto.read_val(b, TType.I16)

    assert 12345 == val


def test_byteswap_i16():
    i = 128
    b = TCyMemoryBuffer()
    proto.write_val(b, TType.I16, i)
    b.flush()
    v = proto.read_val(b, TType.I16)
    assert v == i


def test_write_i32():
    b = TCyMemoryBuffer()
    proto.write_val(b, TType.I32, 1234567890)
    b.flush()

    assert "49 96 02 d2" == hexlify(b.getvalue())


def test_read_i32():
    b = TCyMemoryBuffer(b"I\x96\x02\xd2")
    assert 1234567890 == proto.read_val(b, TType.I32)


def test_write_i64():
    b = TCyMemoryBuffer()
    proto.write_val(b, TType.I64, 1234567890123456789)
    b.flush()
    assert "11 22 10 f4 7d e9 81 15" == hexlify(b.getvalue())


def test_read_i64():
    b = TCyMemoryBuffer(b"\x11\"\x10\xf4}\xe9\x81\x15")
    assert 1234567890123456789 == proto.read_val(b, TType.I64)


def test_write_double():
    b = TCyMemoryBuffer()
    proto.write_val(b, TType.DOUBLE, 1234567890.1234567890)
    b.flush()
    assert "41 d2 65 80 b4 87 e6 b7" == hexlify(b.getvalue())


def test_read_double():
    b = TCyMemoryBuffer(b"A\xd2e\x80\xb4\x87\xe6\xb7")
    assert 1234567890.1234567890 == proto.read_val(b, TType.DOUBLE)


def test_write_string():
    b = TCyMemoryBuffer()
    proto.write_val(b, TType.STRING, "hello world!")
    b.flush()
    assert "00 00 00 0c 68 65 6c 6c 6f 20 77 6f 72 6c 64 21" == \
        hexlify(b.getvalue())

    b = TCyMemoryBuffer()
    proto.write_val(b, TType.STRING, u("你好世界"))
    b.flush()
    assert "00 00 00 0c e4 bd a0 e5 a5 bd e4 b8 96 e7 95 8c" == \
        hexlify(b.getvalue())


def test_read_string():
    b = TCyMemoryBuffer(b"\x00\x00\x00\x0c"
                        b"\xe4\xbd\xa0\xe5\xa5\xbd\xe4\xb8\x96\xe7\x95\x8c")
    assert u("你好世界") == proto.read_val(b, TType.STRING)


def test_read_binary():
    b = TCyMemoryBuffer(b"\x00\x00\x00\x0c"
                        b"\xe4\xbd\xa0\xe5\xa5\xbd\xe4\xb8\x96\xe7\x95\x8c")
    assert u("你好世界").encode("utf-8") == proto.read_val(
        b, TType.STRING, decode_response=False)


def test_write_message_begin():
    trans = TCyMemoryBuffer()
    b = proto.TCyBinaryProtocol(trans)
    b.write_message_begin("test", TType.STRING, 1)
    b.write_message_end()
    assert "80 01 00 0b 00 00 00 04 74 65 73 74 00 00 00 01" == \
        hexlify(trans.getvalue())


def test_write_message_begin_no_strict():
    trans = TCyMemoryBuffer()
    b = proto.TCyBinaryProtocol(trans, strict_write=False)
    b.write_message_begin("test", TType.STRING, 1)
    b.write_message_end()
    assert "00 00 00 04 74 65 73 74 0b 00 00 00 01" == \
        hexlify(trans.getvalue())


def test_read_message_begin():
    b = TCyMemoryBuffer(b"\x80\x01\x00\x0b\x00\x00\x00\x04test"
                        b"\x00\x00\x00\x01")
    res = proto.TCyBinaryProtocol(b).read_message_begin()
    assert res == ("test", TType.STRING, 1)


def test_read_message_begin_not_strict():
    b = TCyMemoryBuffer(b"\x00\x00\x00\x04test\x0b\x00\x00\x00\x01")
    res = proto.TCyBinaryProtocol(b, strict_read=False).read_message_begin()
    assert res == ("test", TType.STRING, 1)


def test_write_struct():
    trans = TCyMemoryBuffer()
    b = proto.TCyBinaryProtocol(trans)
    item = TItem(id=123, phones=["123456", "abcdef"])
    b.write_struct(item)
    b.write_message_end()
    assert ("08 00 01 00 00 00 7b 0f 00 02 0b 00 00 00 02 00 00 00 "
            "06 31 32 33 34 35 36 00 00 00 06 61 62 63 64 65 66 00") == \
        hexlify(trans.getvalue())


def test_read_struct():
    b = TCyMemoryBuffer(b"\x08\x00\x01\x00\x00\x00{"
                        b"\x0f\x00\x02\x0b\x00\x00\x00"
                        b"\x02\x00\x00\x00\x06123456"
                        b"\x00\x00\x00\x06abcdef\x00")
    b = proto.TCyBinaryProtocol(b)
    _item = TItem(id=123, phones=["123456", "abcdef"])
    _item2 = TItem()
    b.read_struct(_item2)
    assert _item == _item2


def test_write_empty_struct():
    trans = TCyMemoryBuffer()
    b = proto.TCyBinaryProtocol(trans)
    item = TItem()
    b.write_struct(item)
    b.write_message_end()
    assert "00" == hexlify(trans.getvalue())


def test_read_empty_struct():
    b = TCyMemoryBuffer(b"\x00")
    b = proto.TCyBinaryProtocol(b)
    _item = TItem()
    _item2 = TItem()
    b.read_struct(_item2)
    assert _item == _item2


def test_write_huge_struct():
    b = TCyMemoryBuffer()
    b = proto.TCyBinaryProtocol(b)
    item = TItem(id=12345, phones=["1234567890"] * 100000)
    b.write_struct(item)
    b.write_message_end()


def test_read_huge_args():

    class Hello(TPayload):
        thrift_spec = {
            1: (TType.STRING, "name", False),
            2: (TType.STRING, "world", False),
        }
        default_spec = [("name", None), ("world", None)]

    b = TCyMemoryBuffer()
    item = Hello(name='我' * 326, world='你' * 1365)
    p = proto.TCyBinaryProtocol(b)
    p.write_struct(item)
    p.write_message_end()

    item2 = Hello()
    p.read_struct(item2)


def test_skip_bool():
    b = TCyMemoryBuffer()
    proto.write_val(b, TType.BOOL, 1)
    proto.write_val(b, TType.I32, 123)
    b.flush()

    proto.skip(b, TType.BOOL)
    assert 123 == proto.read_val(b, TType.I32)


def test_skip_double():
    b = TCyMemoryBuffer()
    proto.write_val(b, TType.DOUBLE, 0.123425897)
    proto.write_val(b, TType.I32, 123)
    b.flush()

    proto.skip(b, TType.DOUBLE)
    assert 123 == proto.read_val(b, TType.I32)


def test_skip_string():
    b = TCyMemoryBuffer()
    proto.write_val(b, TType.STRING, "hello world")
    proto.write_val(b, TType.I32, 123)
    b.flush()

    proto.skip(b, TType.STRING)
    assert 123 == proto.read_val(b, TType.I32)


def test_skip_list():
    b = TCyMemoryBuffer()
    proto.write_val(b, TType.LIST, [5, 6, 7, 8, 9], spec=TType.I32)
    proto.write_val(b, TType.I32, 123)
    b.flush()

    proto.skip(b, TType.LIST)
    assert 123 == proto.read_val(b, TType.I32)


def test_skip_map():
    b = TCyMemoryBuffer()
    proto.write_val(b, TType.MAP, {"hello": 0.3456},
                    spec=(TType.STRING, TType.DOUBLE))
    proto.write_val(b, TType.I32, 123)
    b.flush()

    proto.skip(b, TType.MAP)
    assert 123 == proto.read_val(b, TType.I32)


def test_skip_struct():
    b = TCyMemoryBuffer()
    p = proto.TCyBinaryProtocol(b)
    item = TItem(id=123, phones=["123456", "abcdef"])
    p.write_struct(item)
    p.write_message_end()

    proto.write_val(b, TType.I32, 123)
    b.flush()

    proto.skip(b, TType.STRUCT)
    assert 123 == proto.read_val(b, TType.I32)


def test_read_long_data():
    val = 'z' * 97 * 1024

    unix_sock = "/tmp/thriftpy_test.sock"

    def serve():
        server_sock = TServerSocket(unix_socket=unix_sock)
        server_sock.listen()
        client = server_sock.accept()
        t = TCyBufferedTransport(client)
        proto.write_val(t, TType.STRING, val)
        t.flush()

        # wait for client to read
        time.sleep(1)

    p = multiprocessing.Process(target=serve)
    p.start()
    time.sleep(0.1)

    try:
        sock = TSocket(unix_socket=unix_sock)
        b = TCyBufferedTransport(sock)
        b.open()
        assert val == proto.read_val(b, TType.STRING)
        sock.close()
    finally:
        p.terminate()
        try:
            os.remove(unix_sock)
        except IOError:
            pass


def test_write_wrong_arg_type():
    trans = TCyMemoryBuffer()
    b = proto.TCyBinaryProtocol(trans)
    item = TItem(id="wrong type", phones=["123456", "abcdef"])
    try:
        b.write_struct(item)
    except Exception:
        pass
    b.write_message_end()

    item2 = TItem(id=123, phones=["123456", "abcdef"])
    b.write_struct(item2)
    b.write_message_end()
    assert ("08 00 01 00 00 00 7b 0f 00 02 0b 00 00 00 02 00 00 00 "
            "06 31 32 33 34 35 36 00 00 00 06 61 62 63 64 65 66 00") == \
        hexlify(trans.getvalue())


def test_read_wrong_arg_type():

    class TWrongTypeItem(TPayload):
        thrift_spec = {
            1: (TType.STRING, "id", False),
            2: (TType.LIST, "phones", TType.STRING, False),
        }
        default_spec = [("id", None), ("phones", None)]

    trans = TCyMemoryBuffer()
    b = proto.TCyBinaryProtocol(trans)
    item = TItem(id=58, phones=["123456", "abcdef"])
    b.write_struct(item)
    b.write_message_end()

    item2 = TWrongTypeItem()
    try:
        b.read_struct(item2)
    except Exception:
        pass

    item3 = TItem(id=123, phones=["123456", "abcdef"])
    b.write_struct(item3)
    b.write_message_end()

    item4 = TItem()
    b.read_struct(item4)

    assert item3 == item4


def test_multiple_read_struct():
    t = TCyMemoryBuffer()
    p = proto.TCyBinaryProtocol(t)

    item1 = TItem(id=123, phones=["123456", "abcdef"])
    item2 = TItem(id=234, phones=["110", "120"])
    p.write_struct(item1)
    p.write_struct(item2)
    p.write_message_end()

    _item1 = TItem()
    _item2 = TItem()
    p.read_struct(_item1)
    p.read_struct(_item2)

    assert _item1 == item1 and _item2 == item2


def test_write_decode_error():
    t = TCyMemoryBuffer()
    p = proto.TCyBinaryProtocol(t)

    class T(TPayload):
        thrift_spec = {
            1: (TType.I32, "id", False),
            2: (TType.LIST, "phones", TType.STRING, False),
            3: (TType.STRUCT, "item", TItem, False),
            4: (TType.MAP, "mm", (TType.STRING, (TType.STRUCT, TItem)), False)
        }
        default_spec = [("id", None), ("phones", None), ("item", None),
                        ("mm", None)]

    cases = [
        (T(id="hello"), "Field 'id(1)' of 'T' needs type 'I32', but the value is `'hello'`"),  # noqa
        (T(phones=[90, 12]), "Field 'phones(2)' of 'T' needs type 'LIST<STRING>', but the value is `[90, 12]`"),  # noqa
        (T(item=12), "Field 'item(3)' of 'T' needs type 'TItem', but the value is `12`"),  # noqa
        (T(mm=[45, 56]), "Field 'mm(4)' of 'T' needs type 'MAP<STRING, TItem>', but the value is `[45, 56]`")  # noqa
    ]

    for obj, res in cases:
        with pytest.raises(TDecodeException) as exc:
            p.write_struct(obj)
        assert str(exc.value) == res


def test_type_tolerance():
    t = TCyMemoryBuffer()
    p = proto.TCyBinaryProtocol(t)

    class T(TPayload):
        thrift_spec = {
            1: (TType.LIST, "phones", TType.STRING, False),
            2: (TType.MAP, "mm", (TType.I32, (TType.LIST, TType.I32)), False)
        }
        default_spec = [("phones", None), ("mm", None)]

    defaultdict = collections.defaultdict(list)
    defaultdict.update({234: [3, 4, 5], 123: [6, 7, 8]})

    cases = [
        T(phones=["123", "234"]),
        T(phones=("123", "234")),
        T(phones={"123", "234"}),
        T(phones={"123": 'a', "234": 'b'}),

        T(mm={234: [3, 4, 5], 123: [6, 7, 8]}),
        T(mm=collections.defaultdict(list)),
        T(mm=defaultdict)
    ]

    for obj in cases:
        p.write_struct(obj)
