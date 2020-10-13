import uuid

import pytest

from kazoo.testing import KazooTestCase
from kazoo.tests.util import TRAVIS_ZK_VERSION


class KazooQueueTests(KazooTestCase):
    def _makeOne(self):
        path = "/" + uuid.uuid4().hex
        return self.client.Queue(path)

    def test_queue_validation(self):
        queue = self._makeOne()
        with pytest.raises(TypeError):
            queue.put({})
        with pytest.raises(TypeError):
            queue.put(b"one", b"100")
        with pytest.raises(TypeError):
            queue.put(b"one", 10.0)
        with pytest.raises(ValueError):
            queue.put(b"one", -100)
        with pytest.raises(ValueError):
            queue.put(b"one", 100000)

    def test_empty_queue(self):
        queue = self._makeOne()
        assert len(queue) == 0
        assert queue.get() is None
        assert len(queue) == 0

    def test_queue(self):
        queue = self._makeOne()
        queue.put(b"one")
        queue.put(b"two")
        queue.put(b"three")
        assert len(queue) == 3

        assert queue.get() == b"one"
        assert queue.get() == b"two"
        assert queue.get() == b"three"
        assert len(queue) == 0

    def test_priority(self):
        queue = self._makeOne()
        queue.put(b"four", priority=101)
        queue.put(b"one", priority=0)
        queue.put(b"two", priority=0)
        queue.put(b"three", priority=10)

        assert queue.get() == b"one"
        assert queue.get() == b"two"
        assert queue.get() == b"three"
        assert queue.get() == b"four"


class KazooLockingQueueTests(KazooTestCase):
    def setUp(self):
        KazooTestCase.setUp(self)
        skip = False
        if TRAVIS_ZK_VERSION and TRAVIS_ZK_VERSION < (3, 4):
            skip = True
        elif TRAVIS_ZK_VERSION and TRAVIS_ZK_VERSION >= (3, 4):
            skip = False
        else:
            ver = self.client.server_version()
            if ver[1] < 4:
                skip = True
        if skip:
            pytest.skip("Must use Zookeeper 3.4 or above")

    def _makeOne(self):
        path = "/" + uuid.uuid4().hex
        return self.client.LockingQueue(path)

    def test_queue_validation(self):
        queue = self._makeOne()
        with pytest.raises(TypeError):
            queue.put({})
        with pytest.raises(TypeError):
            queue.put(b"one", b"100")
        with pytest.raises(TypeError):
            queue.put(b"one", 10.0)
        with pytest.raises(ValueError):
            queue.put(b"one", -100)
        with pytest.raises(ValueError):
            queue.put(b"one", 100000)
        with pytest.raises(TypeError):
            queue.put_all({})
        with pytest.raises(TypeError):
            queue.put_all([{}])
        with pytest.raises(TypeError):
            queue.put_all([b"one"], b"100")
        with pytest.raises(TypeError):
            queue.put_all([b"one"], 10.0)
        with pytest.raises(ValueError):
            queue.put_all([b"one"], -100)
        with pytest.raises(ValueError):
            queue.put_all([b"one"], 100000)

    def test_empty_queue(self):
        queue = self._makeOne()
        assert len(queue) == 0
        assert queue.get(0) is None
        assert len(queue) == 0

    def test_queue(self):
        queue = self._makeOne()
        queue.put(b"one")
        queue.put_all([b"two", b"three"])
        assert len(queue) == 3

        assert not queue.consume()
        assert not queue.holds_lock()
        assert queue.get(1) == b"one"
        assert queue.holds_lock()
        # Without consuming, should return the same element
        assert queue.get(1) == b"one"
        assert queue.consume()
        assert not queue.holds_lock()
        assert queue.get(1) == b"two"
        assert queue.holds_lock()
        assert queue.consume()
        assert not queue.holds_lock()
        assert queue.get(1) == b"three"
        assert queue.holds_lock()
        assert queue.consume()
        assert not queue.holds_lock()
        assert not queue.consume()
        assert len(queue) == 0

    def test_consume(self):
        queue = self._makeOne()

        queue.put(b"one")
        assert not queue.consume()
        queue.get(0.1)
        assert queue.consume()
        assert not queue.consume()

    def test_release(self):
        queue = self._makeOne()

        queue.put(b"one")
        assert queue.get(1) == b"one"
        assert queue.holds_lock()
        assert queue.release()
        assert not queue.holds_lock()
        assert queue.get(1) == b"one"
        assert queue.consume()
        assert not queue.release()
        assert len(queue) == 0

    def test_holds_lock(self):
        queue = self._makeOne()

        assert not queue.holds_lock()
        queue.put(b"one")
        queue.get(0.1)
        assert queue.holds_lock()
        queue.consume()
        assert not queue.holds_lock()

    def test_priority(self):
        queue = self._makeOne()
        queue.put(b"four", priority=101)
        queue.put(b"one", priority=0)
        queue.put(b"two", priority=0)
        queue.put(b"three", priority=10)

        assert queue.get(1) == b"one"
        assert queue.consume()
        assert queue.get(1) == b"two"
        assert queue.consume()
        assert queue.get(1) == b"three"
        assert queue.consume()
        assert queue.get(1) == b"four"
        assert queue.consume()

    def test_concurrent_execution(self):
        queue = self._makeOne()
        value1 = []
        value2 = []
        value3 = []
        event1 = self.client.handler.event_object()
        event2 = self.client.handler.event_object()
        event3 = self.client.handler.event_object()

        def get_concurrently(value, event):
            q = self.client.LockingQueue(queue.path)
            value.append(q.get(0.1))
            event.set()

        self.client.handler.spawn(get_concurrently, value1, event1)
        self.client.handler.spawn(get_concurrently, value2, event2)
        self.client.handler.spawn(get_concurrently, value3, event3)
        queue.put(b"one")
        event1.wait(0.2)
        event2.wait(0.2)
        event3.wait(0.2)

        result = value1 + value2 + value3
        assert result.count(b"one") == 1
        assert result.count(None) == 2
