from __future__ import absolute_import, unicode_literals

from case import Mock, patch

from amqp.five import text_t
from amqp.utils import (NullHandler, bytes_to_str, coro, get_errno, get_logger,
                        str_to_bytes)


class test_get_errno:

    def test_has_attr(self):
        exc = KeyError('foo')
        exc.errno = 23
        assert get_errno(exc) == 23

    def test_in_args(self):
        exc = KeyError(34, 'foo')
        exc.args = (34, 'foo')
        assert get_errno(exc) == 34

    def test_args_short(self):
        exc = KeyError(34)
        assert not get_errno(exc)

    def test_no_args(self):
        assert not get_errno(object())


class test_coro:

    def test_advances(self):
        @coro
        def x():
            yield 1
            yield 2
        it = x()
        assert next(it) == 2


class test_str_to_bytes:

    def test_from_unicode(self):
        assert isinstance(str_to_bytes(u'foo'), bytes)

    def test_from_bytes(self):
        assert isinstance(str_to_bytes(b'foo'), bytes)

    def test_supports_surrogates(self):
        bytes_with_surrogates = '\ud83d\ude4f'.encode('utf-8', 'surrogatepass')
        assert str_to_bytes(u'\ud83d\ude4f') == bytes_with_surrogates


class test_bytes_to_str:

    def test_from_unicode(self):
        assert isinstance(bytes_to_str(u'foo'), text_t)

    def test_from_bytes(self):
        assert bytes_to_str(b'foo')

    def test_support_surrogates(self):
        assert bytes_to_str(u'\ud83d\ude4f') == u'\ud83d\ude4f'


class test_NullHandler:

    def test_emit(self):
        NullHandler().emit(Mock(name='record'))


class test_get_logger:

    def test_as_str(self):
        with patch('logging.getLogger') as getLogger:
            x = get_logger('foo.bar')
            getLogger.assert_called_with('foo.bar')
            assert x is getLogger()

    def test_as_logger(self):
        with patch('amqp.utils.NullHandler') as _NullHandler:
            m = Mock(name='logger')
            m.handlers = None
            x = get_logger(m)
            assert x is m
            x.addHandler.assert_called_with(_NullHandler())
