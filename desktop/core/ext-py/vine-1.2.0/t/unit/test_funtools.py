from __future__ import absolute_import, unicode_literals

import pytest

from case import Mock

from vine.abstract import Thenable
from vine.funtools import (
    maybe_promise, ppartial, preplace,
    ready_promise, starpromise, transform, wrap,
)
from vine.promises import promise


def test_wrap():
    cb1 = Mock()
    cb2 = Mock()
    x = wrap(promise(cb1))
    x(1, y=2)
    cb1.assert_called_with(1, y=2)
    p2 = promise(cb2)
    x(p2)
    p2()
    cb1.assert_called_with(cb2())


def test_transform():
    callback = Mock()

    def filter_key_value(key, filter_, mapping):
        return filter_(mapping[key])

    x = transform(filter_key_value, promise(callback), 'Value', int)
    x({'Value': 303})
    callback.assert_called_with(303)

    with pytest.raises(KeyError):
        x({})


class test_maybe_promise:

    def test_when_none(self):
        assert maybe_promise(None) is None

    def test_when_promise(self):
        p = promise()
        assert maybe_promise(p) is p

    def test_when_other(self):
        m = Mock()
        p = maybe_promise(m)
        assert isinstance(p, Thenable)


def test_starpromise():
    m = Mock()
    p = starpromise(m, 1, 2, z=3)
    p()
    m.assert_called_with(1, 2, z=3)


def test_ready_promise():
    m = Mock()
    p = ready_promise(m, 1, 2, 3)
    m.assert_called_with(1, 2, 3)
    assert p.ready


def test_ppartial():
    m = Mock()
    p = ppartial(m, 1)
    p()
    m.assert_called_with(1)
    p = ppartial(m, z=2)
    p()
    m.assert_called_with(z=2)


def test_preplace():
    m = Mock()
    p = promise(m)
    p2 = preplace(p, 1, 2, z=3)
    p2(4, 5, x=3)
    m.assert_called_with(1, 2, z=3)
