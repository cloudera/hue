import threading
import unittest

import mock
import pytest


class TestThreadingHandler(unittest.TestCase):
    def _makeOne(self, *args):
        from kazoo.handlers.threading import SequentialThreadingHandler

        return SequentialThreadingHandler(*args)

    def _getAsync(self, *args):
        from kazoo.handlers.threading import AsyncResult

        return AsyncResult

    def test_proper_threading(self):
        h = self._makeOne()
        h.start()
        # In Python 3.3 _Event is gone, before Event is function
        event_class = getattr(threading, '_Event', threading.Event)
        assert isinstance(h.event_object(), event_class)

    def test_matching_async(self):
        h = self._makeOne()
        h.start()
        async_result = self._getAsync()
        assert isinstance(h.async_result(), async_result)

    def test_exception_raising(self):
        h = self._makeOne()

        with pytest.raises(h.timeout_exception):
            raise h.timeout_exception("This is a timeout")

    def test_double_start_stop(self):
        h = self._makeOne()
        h.start()
        assert h._running is True
        h.start()
        h.stop()
        h.stop()
        assert h._running is False

    def test_huge_file_descriptor(self):
        from kazoo.handlers.threading import _HAS_EPOLL

        if not _HAS_EPOLL:
            self.skipTest('only run on systems with epoll()')
        import resource
        import socket
        from kazoo.handlers.utils import create_tcp_socket

        try:
            resource.setrlimit(resource.RLIMIT_NOFILE, (4096, 4096))
        except (ValueError, resource.error):
            self.skipTest('couldnt raise fd limit high enough')
        fd = 0
        socks = []
        while fd < 4000:
            sock = create_tcp_socket(socket)
            fd = sock.fileno()
            socks.append(sock)
        h = self._makeOne()
        h.start()
        h.select(socks, [], [])
        with pytest.raises(ValueError):
            h._select(socks, [], [])
        h._epoll_select(socks, [], [])
        h.stop()


class TestThreadingAsync(unittest.TestCase):
    def _makeOne(self, *args):
        from kazoo.handlers.threading import AsyncResult

        return AsyncResult(*args)

    def _makeHandler(self):
        from kazoo.handlers.threading import SequentialThreadingHandler

        return SequentialThreadingHandler()

    def test_ready(self):
        mock_handler = mock.Mock()
        async_result = self._makeOne(mock_handler)

        assert async_result.ready() is False
        async_result.set('val')
        assert async_result.ready() is True
        assert async_result.successful() is True
        assert async_result.exception is None

    def test_callback_queued(self):
        mock_handler = mock.Mock()
        mock_handler.completion_queue = mock.Mock()
        async_result = self._makeOne(mock_handler)

        async_result.rawlink(lambda a: a)
        async_result.set('val')

        assert mock_handler.completion_queue.put.called

    def test_set_exception(self):
        mock_handler = mock.Mock()
        mock_handler.completion_queue = mock.Mock()
        async_result = self._makeOne(mock_handler)
        async_result.rawlink(lambda a: a)
        async_result.set_exception(ImportError('Error occured'))

        assert isinstance(async_result.exception, ImportError)
        assert mock_handler.completion_queue.put.called

    def test_get_wait_while_setting(self):
        mock_handler = mock.Mock()
        async_result = self._makeOne(mock_handler)

        lst = []
        bv = threading.Event()
        cv = threading.Event()

        def wait_for_val():
            bv.set()
            val = async_result.get()
            lst.append(val)
            cv.set()

        th = threading.Thread(target=wait_for_val)
        th.start()
        bv.wait()

        async_result.set('fred')
        cv.wait()
        assert lst == ['fred']
        th.join()

    def test_get_with_nowait(self):
        mock_handler = mock.Mock()
        async_result = self._makeOne(mock_handler)
        timeout = self._makeHandler().timeout_exception

        with pytest.raises(timeout):
            async_result.get(block=False)

        with pytest.raises(timeout):
            async_result.get_nowait()

    def test_get_with_exception(self):
        mock_handler = mock.Mock()
        async_result = self._makeOne(mock_handler)

        lst = []
        bv = threading.Event()
        cv = threading.Event()

        def wait_for_val():
            bv.set()
            try:
                val = async_result.get()
            except ImportError:
                lst.append('oops')
            else:
                lst.append(val)
            cv.set()

        th = threading.Thread(target=wait_for_val)
        th.start()
        bv.wait()

        async_result.set_exception(ImportError)
        cv.wait()
        assert lst == ['oops']
        th.join()

    def test_wait(self):
        mock_handler = mock.Mock()
        async_result = self._makeOne(mock_handler)

        lst = []
        bv = threading.Event()
        cv = threading.Event()

        def wait_for_val():
            bv.set()
            try:
                val = async_result.wait(10)
            except ImportError:
                lst.append('oops')
            else:
                lst.append(val)
            cv.set()

        th = threading.Thread(target=wait_for_val)
        th.start()
        bv.wait(10)

        async_result.set("fred")
        cv.wait(15)
        assert lst == [True]
        th.join()

    def test_wait_race(self):
        """Test that there is no race condition in `IAsyncResult.wait()`.

        Guards against the reappearance of:
            https://github.com/python-zk/kazoo/issues/485
        """
        mock_handler = mock.Mock()
        async_result = self._makeOne(mock_handler)

        async_result.set("immediate")

        cv = threading.Event()

        def wait_for_val():
            # NB: should not sleep
            async_result.wait(20)
            cv.set()

        th = threading.Thread(target=wait_for_val)
        th.daemon = True
        th.start()

        # if the wait() didn't sleep (correctly), cv will be set quickly
        # if it did sleep, the cv will not be set yet and this will timeout
        cv.wait(10)
        assert cv.is_set() is True
        th.join()

    def test_set_before_wait(self):
        mock_handler = mock.Mock()
        async_result = self._makeOne(mock_handler)

        lst = []
        cv = threading.Event()
        async_result.set('fred')

        def wait_for_val():
            val = async_result.get()
            lst.append(val)
            cv.set()

        th = threading.Thread(target=wait_for_val)
        th.start()
        cv.wait()
        assert lst == ['fred']
        th.join()

    def test_set_exc_before_wait(self):
        mock_handler = mock.Mock()
        async_result = self._makeOne(mock_handler)

        lst = []
        cv = threading.Event()
        async_result.set_exception(ImportError)

        def wait_for_val():
            try:
                val = async_result.get()
            except ImportError:
                lst.append('ooops')
            else:
                lst.append(val)
            cv.set()

        th = threading.Thread(target=wait_for_val)
        th.start()
        cv.wait()
        assert lst == ['ooops']
        th.join()

    def test_linkage(self):
        mock_handler = mock.Mock()
        async_result = self._makeOne(mock_handler)
        cv = threading.Event()

        lst = []

        def add_on():
            lst.append(True)

        def wait_for_val():
            async_result.get()
            cv.set()

        th = threading.Thread(target=wait_for_val)
        th.start()

        async_result.rawlink(add_on)
        async_result.set(b'fred')
        assert mock_handler.completion_queue.put.called
        async_result.unlink(add_on)
        cv.wait()
        assert async_result.value == b'fred'
        th.join()

    def test_linkage_not_ready(self):
        mock_handler = mock.Mock()
        async_result = self._makeOne(mock_handler)

        lst = []

        def add_on():
            lst.append(True)

        async_result.set('fred')
        assert not mock_handler.completion_queue.called
        async_result.rawlink(add_on)
        assert mock_handler.completion_queue.put.called

    def test_link_and_unlink(self):
        mock_handler = mock.Mock()
        async_result = self._makeOne(mock_handler)

        lst = []

        def add_on():
            lst.append(True)

        async_result.rawlink(add_on)
        assert not mock_handler.completion_queue.put.called
        async_result.unlink(add_on)
        async_result.set('fred')
        assert not mock_handler.completion_queue.put.called

    def test_captured_exception(self):
        from kazoo.handlers.utils import capture_exceptions

        mock_handler = mock.Mock()
        async_result = self._makeOne(mock_handler)

        @capture_exceptions(async_result)
        def exceptional_function():
            return 1 / 0

        exceptional_function()

        with pytest.raises(ZeroDivisionError):
            async_result.get()

    def test_no_capture_exceptions(self):
        from kazoo.handlers.utils import capture_exceptions

        mock_handler = mock.Mock()
        async_result = self._makeOne(mock_handler)

        lst = []

        def add_on():
            lst.append(True)

        async_result.rawlink(add_on)

        @capture_exceptions(async_result)
        def regular_function():
            return True

        regular_function()

        assert not mock_handler.completion_queue.put.called

    def test_wraps(self):
        from kazoo.handlers.utils import wrap

        mock_handler = mock.Mock()
        async_result = self._makeOne(mock_handler)

        lst = []

        def add_on(result):
            lst.append(result.get())

        async_result.rawlink(add_on)

        @wrap(async_result)
        def regular_function():
            return 'hello'

        assert regular_function() == 'hello'
        assert mock_handler.completion_queue.put.called
        assert async_result.get() == 'hello'

    def test_multiple_callbacks(self):
        mockback1 = mock.Mock(name='mockback1')
        mockback2 = mock.Mock(name='mockback2')
        handler = self._makeHandler()
        handler.start()

        async_result = self._makeOne(handler)
        async_result.rawlink(mockback1)
        async_result.rawlink(mockback2)
        async_result.set('howdy')
        async_result.wait()
        handler.stop()

        mockback2.assert_called_once_with(async_result)
        mockback1.assert_called_once_with(async_result)
