import collections
import mock
import threading
import unittest
import uuid

import pytest

from kazoo.exceptions import CancelledError
from kazoo.exceptions import LockTimeout
from kazoo.exceptions import NoNodeError
from kazoo.recipe.lock import Lock
from kazoo.testing import KazooTestCase
from kazoo.tests import util as test_util


class SleepBarrier(object):
    """A crappy spinning barrier."""

    def __init__(self, wait_for, sleep_func):
        self._wait_for = wait_for
        self._arrived = collections.deque()
        self._sleep_func = sleep_func

    def __enter__(self):
        self._arrived.append(threading.current_thread())
        return self

    def __exit__(self, type, value, traceback):
        try:
            self._arrived.remove(threading.current_thread())
        except ValueError:
            pass

    def wait(self):
        while len(self._arrived) < self._wait_for:
            self._sleep_func(0.001)


class KazooLockTests(KazooTestCase):
    thread_count = 20

    def __init__(self, *args, **kw):
        super(KazooLockTests, self).__init__(*args, **kw)
        self.threads_made = []

    def tearDown(self):
        super(KazooLockTests, self).tearDown()
        while self.threads_made:
            t = self.threads_made.pop()
            t.join()

    @staticmethod
    def make_condition():
        return threading.Condition()

    @staticmethod
    def make_event():
        return threading.Event()

    def make_thread(self, *args, **kwargs):
        t = threading.Thread(*args, **kwargs)
        t.daemon = True
        self.threads_made.append(t)
        return t

    @staticmethod
    def make_wait():
        return test_util.Wait()

    def setUp(self):
        super(KazooLockTests, self).setUp()
        self.lockpath = "/" + uuid.uuid4().hex
        self.condition = self.make_condition()
        self.released = self.make_event()
        self.active_thread = None
        self.cancelled_threads = []

    def _thread_lock_acquire_til_event(self, name, lock, event):
        try:
            with lock:
                with self.condition:
                    assert self.active_thread is None
                    self.active_thread = name
                    self.condition.notify_all()

                event.wait()

                with self.condition:
                    assert self.active_thread == name
                    self.active_thread = None
                    self.condition.notify_all()
            self.released.set()
        except CancelledError:
            with self.condition:
                self.cancelled_threads.append(name)
                self.condition.notify_all()

    def test_lock_one(self):
        lock_name = uuid.uuid4().hex
        lock = self.client.Lock(self.lockpath, lock_name)
        event = self.make_event()
        thread = self.make_thread(
            target=self._thread_lock_acquire_til_event,
            args=(lock_name, lock, event),
        )
        thread.start()

        lock2_name = uuid.uuid4().hex
        anotherlock = self.client.Lock(self.lockpath, lock2_name)

        # wait for any contender to show up on the lock
        wait = self.make_wait()
        wait(anotherlock.contenders)
        assert anotherlock.contenders() == [lock_name]

        with self.condition:
            while self.active_thread != lock_name:
                self.condition.wait()

        # release the lock
        event.set()

        with self.condition:
            while self.active_thread:
                self.condition.wait()
        self.released.wait()
        thread.join()

    def test_lock(self):
        threads = []
        names = ["contender" + str(i) for i in range(5)]

        contender_bits = {}

        for name in names:
            e = self.make_event()
            l = self.client.Lock(self.lockpath, name)
            t = self.make_thread(
                target=self._thread_lock_acquire_til_event, args=(name, l, e)
            )
            contender_bits[name] = (t, e)
            threads.append(t)

        # acquire the lock ourselves first to make the others line up
        lock = self.client.Lock(self.lockpath, "test")
        lock.acquire()

        for t in threads:
            t.start()

        # wait for everyone to line up on the lock
        wait = self.make_wait()
        wait(lambda: len(lock.contenders()) == 6)
        contenders = lock.contenders()

        assert contenders[0] == "test"
        contenders = contenders[1:]
        remaining = list(contenders)

        # release the lock and contenders should claim it in order
        lock.release()

        for contender in contenders:
            thread, event = contender_bits[contender]

            with self.condition:
                while not self.active_thread:
                    self.condition.wait()
                assert self.active_thread == contender

            assert lock.contenders() == remaining
            remaining = remaining[1:]

            event.set()

            with self.condition:
                while self.active_thread:
                    self.condition.wait()
        for thread in threads:
            thread.join()

    def test_lock_reconnect(self):
        event = self.make_event()
        other_lock = self.client.Lock(self.lockpath, "contender")
        thread = self.make_thread(
            target=self._thread_lock_acquire_til_event,
            args=("contender", other_lock, event),
        )

        # acquire the lock ourselves first to make the contender line up
        lock = self.client.Lock(self.lockpath, "test")
        lock.acquire()

        thread.start()
        # wait for the contender to line up on the lock
        wait = self.make_wait()
        wait(lambda: len(lock.contenders()) == 2)
        assert lock.contenders() == ["test", "contender"]

        self.expire_session(self.make_event)

        lock.release()

        with self.condition:
            while not self.active_thread:
                self.condition.wait()
            assert self.active_thread == "contender"

        event.set()
        thread.join()

    def test_lock_non_blocking(self):
        lock_name = uuid.uuid4().hex
        lock = self.client.Lock(self.lockpath, lock_name)
        event = self.make_event()

        thread = self.make_thread(
            target=self._thread_lock_acquire_til_event,
            args=(lock_name, lock, event),
        )
        thread.start()

        lock1 = self.client.Lock(self.lockpath, lock_name)

        # wait for the thread to acquire the lock
        with self.condition:
            if not self.active_thread:
                self.condition.wait(5)

        assert not lock1.acquire(blocking=False)
        assert lock.contenders() == [lock_name]  # just one - itself

        event.set()
        thread.join()

    def test_lock_fail_first_call(self):
        event1 = self.make_event()
        lock1 = self.client.Lock(self.lockpath, "one")
        thread1 = self.make_thread(
            target=self._thread_lock_acquire_til_event,
            args=("one", lock1, event1),
        )
        thread1.start()

        # wait for this thread to acquire the lock
        with self.condition:
            if not self.active_thread:
                self.condition.wait(5)
                assert self.active_thread == "one"
        assert lock1.contenders() == ["one"]
        event1.set()
        thread1.join()

    def test_lock_cancel(self):
        event1 = self.make_event()
        lock1 = self.client.Lock(self.lockpath, "one")
        thread1 = self.make_thread(
            target=self._thread_lock_acquire_til_event,
            args=("one", lock1, event1),
        )
        thread1.start()

        # wait for this thread to acquire the lock
        with self.condition:
            if not self.active_thread:
                self.condition.wait(5)
                assert self.active_thread == "one"

        client2 = self._get_client()
        client2.start()
        event2 = self.make_event()
        lock2 = client2.Lock(self.lockpath, "two")
        thread2 = self.make_thread(
            target=self._thread_lock_acquire_til_event,
            args=("two", lock2, event2),
        )
        thread2.start()

        # this one should block in acquire. check that it is a contender
        wait = self.make_wait()
        wait(lambda: len(lock2.contenders()) > 1)
        assert lock2.contenders() == ["one", "two"]

        lock2.cancel()
        with self.condition:
            if "two" not in self.cancelled_threads:
                self.condition.wait()
                assert "two" in self.cancelled_threads

        assert lock2.contenders() == ["one"]

        thread2.join()
        event1.set()
        thread1.join()
        client2.stop()

    def test_lock_no_double_calls(self):
        lock1 = self.client.Lock(self.lockpath, "one")
        lock1.acquire()
        assert lock1.is_acquired is True
        assert lock1.acquire(timeout=0.5) is False
        assert lock1.is_acquired is True
        lock1.release()
        assert lock1.is_acquired is False

    def test_lock_same_thread_no_block(self):
        lock = self.client.Lock(self.lockpath, "one")
        gotten = lock.acquire(blocking=False)
        assert gotten is True
        assert lock.is_acquired is True
        gotten = lock.acquire(blocking=False)
        assert gotten is False

    def test_lock_many_threads_no_block(self):
        lock = self.client.Lock(self.lockpath, "one")
        attempts = collections.deque()

        def _acquire():
            attempts.append(int(lock.acquire(blocking=False)))

        threads = []
        for _i in range(0, self.thread_count):
            t = self.make_thread(target=_acquire)
            threads.append(t)
            t.start()

        while threads:
            t = threads.pop()
            t.join()

        assert sum(list(attempts)) == 1

    def test_lock_many_threads(self):
        sleep_func = self.client.handler.sleep_func
        lock = self.client.Lock(self.lockpath, "one")
        acquires = collections.deque()
        differences = collections.deque()
        barrier = SleepBarrier(self.thread_count, sleep_func)

        def _acquire():
            # Wait until all threads are ready to go...
            with barrier as b:
                b.wait()
                with lock:
                    # Ensure that no two threads enter here and cause the
                    # count to differ by more than one, do this by recording
                    # the count that was captured and examining it post run.
                    starting_count = len(acquires)
                    acquires.append(1)
                    sleep_func(0.01)
                    end_count = len(acquires)
                    differences.append(end_count - starting_count)

        threads = []
        for _i in range(0, self.thread_count):
            t = self.make_thread(target=_acquire)
            threads.append(t)
            t.start()

        while threads:
            t = threads.pop()
            t.join()

        assert len(acquires) == self.thread_count
        assert list(differences) == [1] * self.thread_count

    def test_lock_reacquire(self):
        lock = self.client.Lock(self.lockpath, "one")
        lock.acquire()
        lock.release()
        lock.acquire()
        lock.release()

    def test_lock_ephemeral(self):
        client1 = self._get_client()
        client1.start()
        lock = client1.Lock(self.lockpath, "ephemeral")
        lock.acquire(ephemeral=False)
        znode = self.lockpath + "/" + lock.node
        client1.stop()
        try:
            self.client.get(znode)
        except NoNodeError:
            self.fail("NoNodeError raised unexpectedly!")

    def test_lock_timeout(self):
        timeout = 3
        e = self.make_event()
        started = self.make_event()

        # In the background thread, acquire the lock and wait thrice the time
        # that the main thread is going to wait to acquire the lock.
        lock1 = self.client.Lock(self.lockpath, "one")

        def _thread(lock, event, timeout):
            with lock:
                started.set()
                event.wait(timeout)
                if not event.isSet():
                    # Eventually fail to avoid hanging the tests
                    self.fail("lock2 never timed out")

        t = self.make_thread(target=_thread, args=(lock1, e, timeout * 3))
        t.start()

        # Start the main thread's kazoo client and try to acquire the lock
        # but give up after `timeout` seconds
        client2 = self._get_client()
        client2.start()
        started.wait(5)
        assert started.isSet() is True
        lock2 = client2.Lock(self.lockpath, "two")
        try:
            lock2.acquire(timeout=timeout)
        except LockTimeout:
            # A timeout is the behavior we're expecting, since the background
            # thread should still be holding onto the lock
            pass
        else:
            self.fail("Main thread unexpectedly acquired the lock")
        finally:
            # Cleanup
            e.set()
            t.join()
            client2.stop()

    def test_read_lock(self):
        # Test that we can obtain a read lock
        lock = self.client.ReadLock(self.lockpath, "reader one")
        gotten = lock.acquire(blocking=False)
        assert gotten is True
        assert lock.is_acquired is True
        # and that it's still not reentrant.
        gotten = lock.acquire(blocking=False)
        assert gotten is False
        # Test that a second client we can share the same read lock
        client2 = self._get_client()
        client2.start()
        lock2 = client2.ReadLock(self.lockpath, "reader two")
        gotten = lock2.acquire(blocking=False)
        assert gotten is True
        assert lock2.is_acquired is True
        gotten = lock2.acquire(blocking=False)
        assert gotten is False
        # Test that a writer is unable to share it
        client3 = self._get_client()
        client3.start()
        lock3 = client3.WriteLock(self.lockpath, "writer")
        gotten = lock3.acquire(blocking=False)
        assert gotten is False

    def test_write_lock(self):
        # Test that we can obtain a write lock
        lock = self.client.WriteLock(self.lockpath, "writer")
        gotten = lock.acquire(blocking=False)
        assert gotten is True
        assert lock.is_acquired is True
        gotten = lock.acquire(blocking=False)
        assert gotten is False

        # Test that we are unable to obtain a read lock while the
        # write lock is held.
        client2 = self._get_client()
        client2.start()
        lock2 = client2.ReadLock(self.lockpath, "reader")
        gotten = lock2.acquire(blocking=False)
        assert gotten is False


class TestSemaphore(KazooTestCase):
    def __init__(self, *args, **kw):
        super(TestSemaphore, self).__init__(*args, **kw)
        self.threads_made = []

    def tearDown(self):
        super(TestSemaphore, self).tearDown()
        while self.threads_made:
            t = self.threads_made.pop()
            t.join()

    @staticmethod
    def make_condition():
        return threading.Condition()

    @staticmethod
    def make_event():
        return threading.Event()

    def make_thread(self, *args, **kwargs):
        t = threading.Thread(*args, **kwargs)
        t.daemon = True
        self.threads_made.append(t)
        return t

    def setUp(self):
        super(TestSemaphore, self).setUp()
        self.lockpath = "/" + uuid.uuid4().hex
        self.condition = self.make_condition()
        self.released = self.make_event()
        self.active_thread = None
        self.cancelled_threads = []

    def test_basic(self):
        sem1 = self.client.Semaphore(self.lockpath)
        sem1.acquire()
        sem1.release()

    def test_lock_one(self):
        sem1 = self.client.Semaphore(self.lockpath, max_leases=1)
        sem2 = self.client.Semaphore(self.lockpath, max_leases=1)
        started = self.make_event()
        event = self.make_event()

        sem1.acquire()

        def sema_one():
            started.set()
            with sem2:
                event.set()

        thread = self.make_thread(target=sema_one, args=())
        thread.start()
        started.wait(10)

        assert event.is_set() is False

        sem1.release()
        event.wait(10)
        assert event.is_set() is True
        thread.join()

    def test_non_blocking(self):
        sem1 = self.client.Semaphore(
            self.lockpath, identifier="sem1", max_leases=2
        )
        sem2 = self.client.Semaphore(
            self.lockpath, identifier="sem2", max_leases=2
        )
        sem3 = self.client.Semaphore(
            self.lockpath, identifier="sem3", max_leases=2
        )

        sem1.acquire()
        sem2.acquire()
        assert not sem3.acquire(blocking=False)
        assert set(sem1.lease_holders()) == set(["sem1", "sem2"])
        sem2.release()
        # the next line isn't required, but avoids timing issues in tests
        sem3.acquire()
        assert set(sem1.lease_holders()) == set(["sem1", "sem3"])
        sem1.release()
        sem3.release()

    def test_non_blocking_release(self):
        sem1 = self.client.Semaphore(
            self.lockpath, identifier="sem1", max_leases=1
        )
        sem2 = self.client.Semaphore(
            self.lockpath, identifier="sem2", max_leases=1
        )
        sem1.acquire()
        sem2.acquire(blocking=False)

        # make sure there's no shutdown / cleanup error
        sem1.release()
        sem2.release()

    def test_holders(self):
        started = self.make_event()
        event = self.make_event()

        def sema_one():
            with self.client.Semaphore(self.lockpath, "fred", max_leases=1):
                started.set()
                event.wait()

        thread = self.make_thread(target=sema_one, args=())
        thread.start()
        started.wait()
        sem1 = self.client.Semaphore(self.lockpath)
        holders = sem1.lease_holders()
        assert holders == ["fred"]
        event.set()
        thread.join()

    def test_semaphore_cancel(self):
        sem1 = self.client.Semaphore(self.lockpath, "fred", max_leases=1)
        sem2 = self.client.Semaphore(self.lockpath, "george", max_leases=1)
        sem1.acquire()
        started = self.make_event()
        event = self.make_event()

        def sema_one():
            started.set()
            try:
                with sem2:
                    started.set()
            except CancelledError:
                event.set()

        thread = self.make_thread(target=sema_one, args=())
        thread.start()
        started.wait()
        assert sem1.lease_holders() == ["fred"]
        assert not event.is_set()
        sem2.cancel()
        event.wait()
        assert event.is_set()
        thread.join()

    def test_multiple_acquire_and_release(self):
        sem1 = self.client.Semaphore(self.lockpath, "fred", max_leases=1)
        sem1.acquire()
        sem1.acquire()

        assert sem1.release()
        assert not sem1.release()

    def test_handle_session_loss(self):
        expire_semaphore = self.client.Semaphore(
            self.lockpath, "fred", max_leases=1
        )

        client = self._get_client()
        client.start()
        lh_semaphore = client.Semaphore(self.lockpath, "george", max_leases=1)
        lh_semaphore.acquire()

        started = self.make_event()
        event = self.make_event()
        event2 = self.make_event()

        def sema_one():
            started.set()
            with expire_semaphore:
                event.set()
                event2.wait()

        thread1 = self.make_thread(target=sema_one, args=())
        thread1.start()

        started.wait()
        assert lh_semaphore.lease_holders() == ["george"]

        # Fired in a separate thread to make sure we can see the effect
        expired = self.make_event()

        def expire():
            self.expire_session(self.make_event)
            expired.set()

        thread2 = self.make_thread(target=expire, args=())
        thread2.start()
        expire_semaphore.wake_event.wait()
        expired.wait()

        lh_semaphore.release()
        client.stop()

        event.wait(15)
        assert expire_semaphore.lease_holders() == ["fred"]
        event2.set()

        for t in (thread1, thread2):
            t.join()

    def test_inconsistent_max_leases(self):
        sem1 = self.client.Semaphore(self.lockpath, max_leases=1)
        sem2 = self.client.Semaphore(self.lockpath, max_leases=2)

        sem1.acquire()
        with pytest.raises(ValueError):
            sem2.acquire()

    def test_inconsistent_max_leases_other_data(self):
        sem1 = self.client.Semaphore(self.lockpath, max_leases=1)
        sem2 = self.client.Semaphore(self.lockpath, max_leases=2)

        self.client.ensure_path(self.lockpath)
        self.client.set(self.lockpath, b"a$")

        sem1.acquire()
        # sem2 thinks it's ok to have two lease holders
        assert sem2.acquire(blocking=False)

    def test_reacquire(self):
        lock = self.client.Semaphore(self.lockpath)
        lock.acquire()
        lock.release()
        lock.acquire()
        lock.release()

    def test_acquire_after_cancelled(self):
        lock = self.client.Semaphore(self.lockpath)
        assert lock.acquire() is True
        assert lock.release() is True
        lock.cancel()
        assert lock.cancelled is True
        assert lock.acquire() is True

    def test_timeout(self):
        timeout = 3
        e = self.make_event()
        started = self.make_event()

        # In the background thread, acquire the lock and wait thrice the time
        # that the main thread is going to wait to acquire the lock.
        sem1 = self.client.Semaphore(self.lockpath, "one")

        def _thread(sem, event, timeout):
            with sem:
                started.set()
                event.wait(timeout)
                if not event.isSet():
                    # Eventually fail to avoid hanging the tests
                    self.fail("sem2 never timed out")

        t = self.make_thread(target=_thread, args=(sem1, e, timeout * 3))
        t.start()

        # Start the main thread's kazoo client and try to acquire the lock
        # but give up after `timeout` seconds
        client2 = self._get_client()
        client2.start()
        started.wait(5)
        assert started.isSet() is True
        sem2 = client2.Semaphore(self.lockpath, "two")
        try:
            sem2.acquire(timeout=timeout)
        except LockTimeout:
            # A timeout is the behavior we're expecting, since the background
            # thread will still be holding onto the lock
            e.set()
        finally:
            # Cleanup
            t.join()
            client2.stop()


class TestSequence(unittest.TestCase):
    def test_get_predecessor(self):
        """Validate selection of predecessors.
        """
        goLock = "_c_8eb60557ba51e0da67eefc47467d3f34-lock-0000000031"
        pyLock = "514e5a831836450cb1a56c741e990fd8__lock__0000000032"
        children = ["hello", goLock, "world", pyLock]
        client = mock.MagicMock()
        client.get_children.return_value = children
        lock = Lock(client, "test")
        assert lock._get_predecessor(pyLock) is None

    def test_get_predecessor_go(self):
        """Test selection of predecessor when instructed to consider go-zk
        locks.
        """
        goLock = "_c_8eb60557ba51e0da67eefc47467d3f34-lock-0000000031"
        pyLock = "514e5a831836450cb1a56c741e990fd8__lock__0000000032"
        children = ["hello", goLock, "world", pyLock]
        client = mock.MagicMock()
        client.get_children.return_value = children
        lock = Lock(client, "test", extra_lock_patterns=["-lock-"])
        assert lock._get_predecessor(pyLock) == goLock
