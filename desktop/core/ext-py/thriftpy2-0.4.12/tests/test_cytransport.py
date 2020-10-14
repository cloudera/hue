# -*- coding: utf-8 -*-

import pytest

from thriftpy2._compat import PYPY

pytestmark = pytest.mark.skipif(PYPY, reason="cython not enabled in pypy.")

if not PYPY:
    from thriftpy2.transport.framed import TCyFramedTransport
    from thriftpy2.transport.buffered import TCyBufferedTransport
    from thriftpy2.transport import TMemoryBuffer, TTransportException


def test_transport_mismatch():
    s = TMemoryBuffer()

    t1 = TCyBufferedTransport(s)
    t1.write(b"\x80\x01\x00\x01\x00\x00\x00\x04ping hello world")
    t1.flush()

    with pytest.raises(TTransportException) as exc:
        t2 = TCyFramedTransport(s)
        t2.read(4)

    assert "No frame" in str(exc.value)


def test_buffered_read():
    s = TMemoryBuffer()

    t = TCyBufferedTransport(s)
    t.write(b"ping")
    t.flush()

    assert t.read(4) == b"ping"


def test_transport_handle():
    from thriftpy2._compat import CYTHON
    if not CYTHON:
        return

    from thriftpy2.transport import TSocket
    from thriftpy2.transport.memory import TCyMemoryBuffer

    s = TSocket()
    s.set_handle('the sock')

    assert TCyBufferedTransport(s).sock == 'the sock'
    assert TCyFramedTransport(s).sock == 'the sock'
    assert TCyMemoryBuffer().sock is None
    assert TCyBufferedTransport(TCyFramedTransport(s)).sock == 'the sock'
    assert TCyBufferedTransport(TCyMemoryBuffer()).sock is None
