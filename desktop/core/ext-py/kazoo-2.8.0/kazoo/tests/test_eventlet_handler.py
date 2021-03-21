import contextlib
import unittest

import pytest

from kazoo.client import KazooClient
from kazoo.handlers import utils
from kazoo.protocol import states as kazoo_states
from kazoo.tests import test_client
from kazoo.tests import test_lock
from kazoo.tests import util as test_util

try:
    import eventlet
    from eventlet.green import threading
    from kazoo.handlers import eventlet as eventlet_handler

    EVENTLET_HANDLER_AVAILABLE = True
except ImportError:
    EVENTLET_HANDLER_AVAILABLE = False


@contextlib.contextmanager
def start_stop_one(handler=None):
    if not handler:
        handler = eventlet_handler.SequentialEventletHandler()
    handler.start()
    try:
        yield handler
    finally:
        handler.stop()


class TestEventletHandler(unittest.TestCase):
    def setUp(self):
        if not EVENTLET_HANDLER_AVAILABLE:
            pytest.skip("eventlet handler not available.")
        super(TestEventletHandler, self).setUp()

    def test_started(self):
        with start_stop_one() as handler:
            assert handler.running is True
            assert len(handler._workers) != 0
        assert handler.running is False
        assert len(handler._workers) == 0

    def test_spawn(self):
        captures = []

        def cb():
            captures.append(1)

        with start_stop_one() as handler:
            handler.spawn(cb)

        assert len(captures) == 1

    def test_dispatch(self):
        captures = []

        def cb():
            captures.append(1)

        with start_stop_one() as handler:
            handler.dispatch_callback(kazoo_states.Callback("watch", cb, []))

        assert len(captures) == 1

    def test_async_link(self):
        captures = []

        def cb(handler):
            captures.append(handler)

        with start_stop_one() as handler:
            r = handler.async_result()
            r.rawlink(cb)
            r.set(2)

        assert len(captures) == 1
        assert r.get() == 2

    def test_timeout_raising(self):
        handler = eventlet_handler.SequentialEventletHandler()

        with pytest.raises(handler.timeout_exception):
            raise handler.timeout_exception("This is a timeout")

    def test_async_ok(self):
        captures = []

        def delayed():
            captures.append(1)
            return 1

        def after_delayed(handler):
            captures.append(handler)

        with start_stop_one() as handler:
            r = handler.async_result()
            r.rawlink(after_delayed)
            w = handler.spawn(utils.wrap(r)(delayed))
            w.join()

        assert len(captures) == 2
        assert captures[0] == 1
        assert r.get() == 1

    def test_get_with_no_block(self):
        handler = eventlet_handler.SequentialEventletHandler()

        with start_stop_one(handler):
            r = handler.async_result()

            with pytest.raises(handler.timeout_exception):
                r.get(block=False)
            r.set(1)
            assert r.get() == 1

    def test_async_exception(self):
        def broken():
            raise IOError("Failed")

        with start_stop_one() as handler:
            r = handler.async_result()
            w = handler.spawn(utils.wrap(r)(broken))
            w.join()

        assert r.successful() is False
        with pytest.raises(IOError):
            r.get()


class TestEventletClient(test_client.TestClient):
    def setUp(self):
        if not EVENTLET_HANDLER_AVAILABLE:
            pytest.skip("eventlet handler not available.")
        super(TestEventletClient, self).setUp()

    @staticmethod
    def make_event():
        return threading.Event()

    @staticmethod
    def make_condition():
        return threading.Condition()

    def _makeOne(self, *args):
        return eventlet_handler.SequentialEventletHandler(*args)

    def _get_client(self, **kwargs):
        kwargs["handler"] = self._makeOne()
        return KazooClient(self.hosts, **kwargs)


class TestEventletSemaphore(test_lock.TestSemaphore):
    def setUp(self):
        if not EVENTLET_HANDLER_AVAILABLE:
            pytest.skip("eventlet handler not available.")
        super(TestEventletSemaphore, self).setUp()

    @staticmethod
    def make_condition():
        return threading.Condition()

    @staticmethod
    def make_event():
        return threading.Event()

    @staticmethod
    def make_thread(*args, **kwargs):
        return threading.Thread(*args, **kwargs)

    def _makeOne(self, *args):
        return eventlet_handler.SequentialEventletHandler(*args)

    def _get_client(self, **kwargs):
        kwargs["handler"] = self._makeOne()
        c = KazooClient(self.hosts, **kwargs)
        try:
            self._clients.append(c)
        except AttributeError:
            self._client = [c]
        return c


class TestEventletLock(test_lock.KazooLockTests):
    def setUp(self):
        if not EVENTLET_HANDLER_AVAILABLE:
            pytest.skip("eventlet handler not available.")
        super(TestEventletLock, self).setUp()

    @staticmethod
    def make_condition():
        return threading.Condition()

    @staticmethod
    def make_event():
        return threading.Event()

    @staticmethod
    def make_thread(*args, **kwargs):
        return threading.Thread(*args, **kwargs)

    @staticmethod
    def make_wait():
        return test_util.Wait(getsleep=(lambda: eventlet.sleep))

    def _makeOne(self, *args):
        return eventlet_handler.SequentialEventletHandler(*args)

    def _get_client(self, **kwargs):
        kwargs["handler"] = self._makeOne()
        c = KazooClient(self.hosts, **kwargs)
        try:
            self._clients.append(c)
        except AttributeError:
            self._client = [c]
        return c
