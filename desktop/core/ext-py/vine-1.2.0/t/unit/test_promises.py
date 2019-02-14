from __future__ import absolute_import, unicode_literals

import pytest
import sys
import traceback

from collections import deque
from struct import pack, unpack
import weakref

from case import Mock

from vine.funtools import wrap
from vine.promises import promise


class test_promise:

    def test_example(self):

        _pending = deque()

        class Protocol(object):

            def __init__(self):
                self.buffer = []

            def read(self, size, callback=None):
                callback = callback or promise()
                _pending.append((size, callback))
                return callback

            def read_header(self, callback=None):
                return self.read(4, callback)

            def read_body(self, header, callback=None):
                body_size, = unpack('>L', header)
                return self.read(body_size, callback)

            def prepare_body(self, value):
                self.buffer.append(value)

        proto = Protocol()
        proto.read_header().then(
            proto.read_body).then(wrap(proto.prepare_body))

        while _pending:
            size, callback = _pending.popleft()
            if size == 4:
                callback(pack('>L', 1231012302))
            else:
                callback('Hello world')

        assert proto.buffer
        assert proto.buffer[0] == 'Hello world'

    def test_signal(self):
        callback = Mock(name='callback')
        a = promise()
        a.then(callback)
        a(42)
        callback.assert_called_with(42)

    def test_chained(self):

        def add(x, y):
            return x + y

        def pow2(x):
            return x ** 2

        adder = Mock(name='adder')
        adder.side_effect = add

        power = Mock(name='multiplier')
        power.side_effect = pow2

        final = Mock(name='final')

        p = promise()
        p.then(adder).then(power).then(final)

        p(42, 42)
        assert p.value == ((42, 42), {})
        adder.assert_called_with(42, 42)
        power.assert_called_with(84)
        final.assert_called_with(7056)

    def test_shallow_filter(self):
        a, b = promise(Mock(name='a')), promise(Mock(name='b'))
        p = promise(a, callback=b)
        assert p._svpending is not None
        assert p._lvpending is None
        p(30)
        assert p._svpending is None
        a.fun.assert_called_with(30)
        b.fun.assert_called_with(a.fun.return_value)

        c, d = Mock(name='c'), Mock(name='d')
        promise(c, callback=d)(1)
        c.assert_called_with(1)
        d.assert_called_with(c.return_value)

    def test_deep_filter(self):
        a = promise(Mock(name='a'))
        b1, b2, b3 = (
            promise(Mock(name='a1')),
            promise(Mock(name='a2')),
            promise(Mock(name='a3')),
        )
        p = promise(a)
        p.then(b1)
        assert p._lvpending is None
        assert p._svpending is not None
        p.then(b2)
        assert p._lvpending is not None
        assert p._svpending is None
        p.then(b3)

        p(42)
        a.fun.assert_called_with(42)
        b1.fun.assert_called_with(a.fun.return_value)
        b2.fun.assert_called_with(a.fun.return_value)
        b3.fun.assert_called_with(a.fun.return_value)

    def test_chained_filter(self):
        a = promise(Mock(name='a'))
        b = promise(Mock(name='b'))
        c = promise(Mock(name='c'))
        d = promise(Mock(name='d'))

        p = promise(a)
        p.then(b).then(c).then(d)

        p(42, kw=300)

        a.fun.assert_called_with(42, kw=300)
        b.fun.assert_called_with(a.fun.return_value)
        c.fun.assert_called_with(b.fun.return_value)
        d.fun.assert_called_with(c.fun.return_value)

    def test_repr(self):
        assert repr(promise())
        assert repr(promise(Mock()))

    def test_cancel(self):
        on_error = promise(Mock(name='on_error'))
        p = promise(on_error=on_error)
        a, b, c = (
            promise(Mock(name='a')),
            promise(Mock(name='b')),
            promise(Mock(name='c')),
        )
        a2 = promise(Mock(name='a1'))
        p.then(a).then(b).then(c)
        p.then(a2)

        p.cancel()
        p(42)
        assert p.cancelled
        assert a.cancelled
        assert a2.cancelled
        assert b.cancelled
        assert c.cancelled
        assert on_error.cancelled
        d = promise(Mock(name='d'))
        p.then(d)
        assert d.cancelled

    def test_svpending_raises(self):
        p = promise()
        a_on_error = promise(Mock(name='a_on_error'))
        a = promise(Mock(name='a'), on_error=a_on_error)
        p.then(a)
        exc = KeyError()
        a.fun.side_effect = exc

        p(42)
        a_on_error.fun.assert_called_with(exc)

    def test_empty_promise(self):
        p = promise()
        p(42)
        x = Mock(name='x')
        p.then(x)
        x.assert_called_with(42)

    def test_with_partial_args(self):
        m = Mock(name='m')
        p = promise(m, (1, 2, 3), {'foobar': 2})
        p()
        m.assert_called_with(1, 2, 3, foobar=2)

    def test_with_partial_args_and_args(self):
        m = Mock(name='m')
        p = promise(m, (1, 2, 3), {'foobar': 2})
        p(4, 5, bazbar=3)
        m.assert_called_with(1, 2, 3, 4, 5, foobar=2, bazbar=3)

    def test_lvpending_raises(self):
        p = promise()
        a_on_error = promise(Mock(name='a_on_error'))
        a = promise(Mock(name='a'), on_error=a_on_error)
        b_on_error = promise(Mock(name='b_on_error'))
        b = promise(Mock(name='a'), on_error=b_on_error)
        p.then(a)
        p.then(b)
        exc = KeyError()
        a.fun.side_effect = exc

        a.then(Mock(name='foobar'))
        a.then(Mock(name='foozi'))

        p.on_error = a_on_error
        p(42)
        a_on_error.fun.assert_called_with(exc)
        b.fun.assert_called_with(42)

    def test_cancel_sv(self):
        p = promise()
        a = promise(Mock(name='a'))
        p.then(a)
        p.cancel()
        assert p.cancelled
        assert a.cancelled

        p.throw(KeyError())
        p.throw1(KeyError())

    def test_cancel_no_cb(self):
        p = promise()
        p.cancel()
        assert p.cancelled
        assert p.on_error is None
        p.throw(KeyError())

    def test_throw_no_exc(self):
        p = promise()
        with pytest.raises((TypeError, RuntimeError)):
            p.throw()

    def test_throw_no_excinfo(self):
        p = promise()
        with pytest.raises(KeyError):
            p.throw(KeyError())

    def test_throw_with_tb(self):
        p = promise()

        def foo():
            raise KeyError()

        try:
            foo()
        except KeyError:
            try:
                p.throw()
            except KeyError:
                err = traceback.format_exc()
                assert 'in foo\n    raise KeyError()' in err
            else:
                raise AssertionError('Did not throw.')

    def test_throw_with_other_tb(self):
        p = promise()

        def foo():
            raise KeyError()

        def bar():
            raise ValueError()

        try:
            bar()
        except ValueError:
            tb = sys.exc_info()[2]

        try:
            foo()
        except KeyError as exc:
            try:
                p.throw(exc, tb)
            except KeyError:
                err = traceback.format_exc()
                assert 'in bar\n    raise ValueError()' in err
            else:
                raise AssertionError('Did not throw.')

    def test_throw_None(self):
        try:
            raise KeyError()
        except Exception:
            with pytest.raises(KeyError):
                promise().throw()

    def test_listeners(self):
        p = promise()
        p.then(Mock())
        assert len(p.listeners) == 1
        p.then(Mock())
        assert len(p.listeners) == 2

    def test_throw_from_cb(self):
        ae = promise(Mock(name='ae'))
        a = Mock(name='a')
        be = promise(Mock(name='be'))
        b = promise(Mock(name='b'), on_error=be)
        ce = promise(Mock(name='ce'))
        c = promise(Mock(name='c'), on_error=ce)

        exc = a.side_effect = KeyError()
        p1 = promise(a, on_error=ae)
        p1.then(b)
        assert p1._svpending
        p1(42)
        p1.on_error.fun.assert_called_with(exc)

        p2 = promise(a)
        p2.then(b).then(c)
        with pytest.raises(KeyError):
            p2(42)

        de = promise(Mock(name='de'))
        d = promise(Mock(name='d'), on_error=de)
        p2.then(d)
        de.fun.assert_called_with(exc)

    def test_weak_reference_unbound(self):
        def f(x):
            return x ** 2

        promise_f = promise(f, weak=True)

        assert isinstance(promise_f.fun, weakref.ref)
        assert promise_f(2) == 4

    def test_weak_reference_bound(self):
        class Example(object):
            def __init__(self, y):
                self.y = y

            def f(self, x):
                return self.y + x ** 2

        example = Example(5)
        promise_f = promise(example.f, weak=True)

        assert isinstance(promise_f.fun, weakref.ref)
        assert promise_f(2) == 9
