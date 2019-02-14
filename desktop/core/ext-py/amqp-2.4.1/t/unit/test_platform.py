from __future__ import absolute_import, unicode_literals

import itertools
import operator

import pytest

from amqp.platform import _linux_version_to_tuple


def reload_module(module):
    try:
        import importlib
        importlib.reload(module)
    except Exception:
        reload(module)  # noqa -- does not exist on Python3


def test_struct_argument_type():
    from amqp.exceptions import FrameSyntaxError
    FrameSyntaxError()


@pytest.mark.parametrize('s,expected', [
    ('3.13.0-46-generic', (3, 13, 0)),
    ('3.19.43-1-amd64', (3, 19, 43)),
    ('4.4.34+', (4, 4, 34)),
    ('4.4.what', (4, 4, 0)),
    ('4.what.what', (4, 0, 0)),
    ('4.4.0-43-Microsoft', (4, 4, 0)),
])
def test_linux_version_to_tuple(s, expected):
    assert _linux_version_to_tuple(s) == expected


def monkeypatch_platform(monkeypatch, sys_platform, platform_release):
    monkeypatch.setattr("sys.platform", sys_platform)

    def release():
        return platform_release

    monkeypatch.setattr("platform.release", release)


def test_tcp_opts_change(monkeypatch):
    monkeypatch_platform(monkeypatch, 'linux', '2.6.36-1-amd64')

    import amqp.platform
    reload_module(amqp.platform)
    old_linux = amqp.platform.KNOWN_TCP_OPTS

    monkeypatch_platform(monkeypatch, 'linux', '2.6.37-0-41-generic')
    reload_module(amqp.platform)
    new_linux = amqp.platform.KNOWN_TCP_OPTS

    monkeypatch_platform(monkeypatch, 'win32', '7')
    reload_module(amqp.platform)
    win = amqp.platform.KNOWN_TCP_OPTS

    monkeypatch_platform(monkeypatch, 'linux', '4.4.0-43-Microsoft')
    reload_module(amqp.platform)
    win_bash = amqp.platform.KNOWN_TCP_OPTS

    li = [old_linux, new_linux, win, win_bash]
    assert all(operator.ne(*i) for i in itertools.combinations(li, 2))

    assert len(win) <= len(win_bash) < len(old_linux) < len(new_linux)
