import uuid
import threading
import time

import mock

from kazoo.exceptions import LockTimeout
from kazoo.testing import KazooTestCase
from kazoo.recipe.partitioner import PartitionState


class SlowLockMock:
    """Emulates a slow ZooKeeper lock."""

    default_delay_time = 3

    def __init__(self, client, lock, delay_time=None):
        self._client = client
        self._lock = lock
        self.delay_time = self.default_delay_time \
            if delay_time is None else delay_time

    def acquire(self, timeout=None):
        sleep = self._client.handler.sleep_func
        sleep(self.delay_time)

        if timeout is None:
            return self._lock.acquire()

        start_time = time.time()

        while time.time() - start_time < timeout:
            if self._lock.acquire(False):
                return True

            sleep(0.1)

        raise LockTimeout("Mocked slow lock has timed out.")

    def release(self):
        self._lock.release()


class KazooPartitionerTests(KazooTestCase):
    @staticmethod
    def make_event():
        return threading.Event()

    def setUp(self):
        super(KazooPartitionerTests, self).setUp()
        self.path = "/" + uuid.uuid4().hex
        self.__partitioners = []

    def test_party_of_one(self):
        self.__create_partitioner(size=3)
        self.__wait_for_acquire()
        self.__assert_state(PartitionState.ACQUIRED)
        self.__assert_partitions([0, 1, 2])
        self.__finish()

    def test_party_of_two(self):
        for i in range(2):
            self.__create_partitioner(size=2, identifier=str(i))

        self.__wait_for_acquire()
        self.__assert_partitions([0], [1])

        self.__partitioners[0].finish()
        self.__wait()
        assert self.__partitioners[1].release
        self.__partitioners[1].finish()

    def test_party_expansion(self):
        for i in range(2):
            self.__create_partitioner(size=3, identifier=str(i))

        self.__wait_for_acquire()
        self.__assert_state(PartitionState.ACQUIRED)
        self.__assert_partitions([0, 2], [1])

        for partitioner in self.__partitioners:
            partitioner.state_change_event.clear()

        # Add another partition, wait till they settle
        self.__create_partitioner(size=3, identifier="2")
        self.__wait()

        self.__assert_state(PartitionState.RELEASE,
                            partitioners=self.__partitioners[:-1])
        for partitioner in self.__partitioners[-1]:
            assert partitioner.state_change_event.is_set()
        self.__release(self.__partitioners[:-1])

        self.__wait_for_acquire()
        self.__assert_partitions([0], [1], [2])

        self.__finish()

    def test_more_members_than_set_items(self):
        for i in range(2):
            self.__create_partitioner(size=1, identifier=str(i))

        self.__wait_for_acquire()
        self.__assert_state(PartitionState.ACQUIRED)
        self.__assert_partitions([0], [])

        self.__finish()

    def test_party_session_failure(self):
        partitioner = self.__create_partitioner(size=3)
        self.__wait_for_acquire()
        assert partitioner.state == PartitionState.ACQUIRED
        # simulate session failure
        partitioner._fail_out()
        partitioner.release_set()
        assert partitioner.failed is True

    def test_connection_loss(self):
        self.__create_partitioner(identifier="0", size=3)
        self.__create_partitioner(identifier="1", size=3)

        self.__wait_for_acquire()
        self.__assert_state(PartitionState.ACQUIRED)
        self.__assert_partitions([0, 2], [1])

        # Emulate connection loss
        self.lose_connection(self.make_event)
        self.__assert_state(PartitionState.RELEASE)
        self.__release()

        # Check that partitioners settle after connection loss
        self.__wait_for_acquire()
        self.__assert_state(PartitionState.ACQUIRED)
        self.__assert_partitions([0, 2], [1])

        # Check that partitioners react on new events after connection loss
        self.__create_partitioner(identifier="2", size=3)
        self.__wait()

        self.__assert_state(PartitionState.RELEASE,
                            partitioners=self.__partitioners[:-1])
        self.__release(partitioners=self.__partitioners[:-1])
        self.__wait_for_acquire()
        self.__assert_state(PartitionState.ACQUIRED)
        self.__assert_partitions([0], [1], [2])

    def test_race_condition_new_partitioner_during_the_lock(self):
        locks = {}

        def get_lock(path):
            lock = locks.setdefault(path, self.client.handler.lock_object())
            return SlowLockMock(self.client, lock)

        with mock.patch.object(self.client, "Lock", side_effect=get_lock):
            # Create first partitioner. It will start to acquire the set
            # members.
            self.__create_partitioner(identifier="0", size=2)

            # Wait until the first partitioner has acquired first lock and
            # started to acquire the second lock.
            self.client.handler.sleep_func(SlowLockMock.default_delay_time + 1)

            # Create the second partitioner a the time when the first
            # partitioner is in the process of acquiring the lock that should
            # belong to the second partitioner.
            self.__create_partitioner(identifier="1", size=2)

            # The first partitioner should acquire the both locks but then it
            # must notice that the party has changed and it must reacquire
            # the set. No deadlocks must happen.
            self.__wait_for_acquire()

        self.__assert_state(PartitionState.ACQUIRED)
        self.__assert_partitions([0], [1])

    def test_race_condition_new_partitioner_steals_the_lock(self):
        locks = {}

        def get_lock(path):
            new_lock = self.client.handler.lock_object()
            lock = locks.setdefault(path, new_lock)

            if lock is new_lock:
                # The first partitioner will be delayed
                delay_time = SlowLockMock.default_delay_time
            else:
                # The second partitioner won't be delayed
                delay_time = 0

            return SlowLockMock(self.client, lock, delay_time=delay_time)

        with mock.patch.object(self.client, "Lock", side_effect=get_lock):
            # Create first partitioner. It will start to acquire the set
            # members.
            self.__create_partitioner(identifier="0", size=2)

            # Wait until the first partitioner has acquired first lock and
            # started to acquire the second lock.
            self.client.handler.sleep_func(SlowLockMock.default_delay_time + 1)

            # Create the second partitioner a the time when the first
            # partitioner is in the process of acquiring the lock that should
            # belong to the second partitioner. The second partitioner should
            # steal the lock because it won't be delayed.
            self.__create_partitioner(identifier="1", size=2)

            # The first partitioner should fail to acquire the second lock and
            # must notice that the party has changed and it must reacquire the
            # set. No deadlocks must happen.
            self.__wait_for_acquire()

        self.__assert_state(PartitionState.ACQUIRED)
        self.__assert_partitions([0], [1])

    def __create_partitioner(self, size, identifier=None):
        partitioner = self.client.SetPartitioner(
            self.path, set=range(size), time_boundary=0.2,
            identifier=identifier)
        self.__partitioners.append(partitioner)
        return partitioner

    def __wait_for_acquire(self):
        for partitioner in self.__partitioners:
            partitioner.wait_for_acquire(14)

    def __assert_state(self, state, partitioners=None):
        if partitioners is None:
            partitioners = self.__partitioners

        for partitioner in partitioners:
            assert partitioner.state == state

    def __assert_partitions(self, *partitions):
        assert len(partitions) == len(self.__partitioners)
        for partitioner, own_partitions in zip(self.__partitioners,
                                               partitions):
            assert list(partitioner) == own_partitions

    def __wait(self):
        time.sleep(0.1)

    def __release(self, partitioners=None):
        if partitioners is None:
            partitioners = self.__partitioners

        for partitioner in partitioners:
            partitioner.release_set()

    def __finish(self):
        for partitioner in self.__partitioners:
            partitioner.finish()
