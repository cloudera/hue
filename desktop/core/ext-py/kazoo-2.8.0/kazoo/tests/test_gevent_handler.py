import unittest

import pytest

from kazoo.client import KazooClient
from kazoo.exceptions import NoNodeError
from kazoo.protocol.states import Callback
from kazoo.testing import KazooTestCase
from kazoo.tests import test_client


class TestGeventHandler(unittest.TestCase):
    def setUp(self):
        try:
            import gevent  # NOQA
        except ImportError:
            pytest.skip("gevent not available.")

    def _makeOne(self, *args):
        from kazoo.handlers.gevent import SequentialGeventHandler

        return SequentialGeventHandler(*args)

    def _getAsync(self, *args):
        from kazoo.handlers.gevent import AsyncResult

        return AsyncResult

    def _getEvent(self):
        from gevent.event import Event

        return Event

    def test_proper_threading(self):
        h = self._makeOne()
        h.start()
        assert isinstance(h.event_object(), self._getEvent())

    def test_matching_async(self):
        h = self._makeOne()
        h.start()
        async_handler = self._getAsync()
        assert isinstance(h.async_result(), async_handler)

    def test_exception_raising(self):
        h = self._makeOne()

        with pytest.raises(h.timeout_exception):
            raise h.timeout_exception("This is a timeout")

    def test_exception_in_queue(self):
        h = self._makeOne()
        h.start()
        ev = self._getEvent()()

        def func():
            ev.set()
            raise ValueError("bang")

        call1 = Callback("completion", func, ())
        h.dispatch_callback(call1)
        ev.wait()

    def test_queue_empty_exception(self):
        from gevent.queue import Empty

        h = self._makeOne()
        h.start()
        ev = self._getEvent()()

        def func():
            ev.set()
            raise Empty()

        call1 = Callback("completion", func, ())
        h.dispatch_callback(call1)
        ev.wait()


class TestBasicGeventClient(KazooTestCase):
    def setUp(self):
        try:
            import gevent  # NOQA
        except ImportError:
            pytest.skip("gevent not available.")
        KazooTestCase.setUp(self)

    def _makeOne(self, *args):
        from kazoo.handlers.gevent import SequentialGeventHandler

        return SequentialGeventHandler(*args)

    def _getEvent(self):
        from gevent.event import Event

        return Event

    def test_start(self):
        client = self._get_client(handler=self._makeOne())
        client.start()
        assert client.state == "CONNECTED"
        client.stop()

    def test_start_stop_double(self):
        client = self._get_client(handler=self._makeOne())
        client.start()
        assert client.state == "CONNECTED"
        client.handler.start()
        client.handler.stop()
        client.stop()

    def test_basic_commands(self):
        client = self._get_client(handler=self._makeOne())
        client.start()
        assert client.state == "CONNECTED"
        client.create("/anode", b"fred")
        assert client.get("/anode")[0] == b"fred"
        assert client.delete("/anode")
        assert client.exists("/anode") is None
        client.stop()

    def test_failures(self):
        client = self._get_client(handler=self._makeOne())
        client.start()
        with pytest.raises(NoNodeError):
            client.get("/none")
        client.stop()

    def test_data_watcher(self):
        client = self._get_client(handler=self._makeOne())
        client.start()
        client.ensure_path("/some/node")
        ev = self._getEvent()()

        @client.DataWatch("/some/node")
        def changed(d, stat):
            ev.set()

        ev.wait()
        ev.clear()
        client.set("/some/node", b"newvalue")
        ev.wait()
        client.stop()


class TestGeventClient(test_client.TestClient):
    def setUp(self):
        try:
            import gevent  # NOQA
        except ImportError:
            pytest.skip("gevent not available.")
        KazooTestCase.setUp(self)

    def _makeOne(self, *args):
        from kazoo.handlers.gevent import SequentialGeventHandler

        return SequentialGeventHandler(*args)

    def _get_client(self, **kwargs):
        kwargs["handler"] = self._makeOne()
        return KazooClient(self.hosts, **kwargs)
