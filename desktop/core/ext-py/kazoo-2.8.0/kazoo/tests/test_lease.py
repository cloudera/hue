import datetime
import uuid

from kazoo.recipe.lease import NonBlockingLease
from kazoo.recipe.lease import MultiNonBlockingLease

from kazoo.testing import KazooTestCase


class MockClock(object):
    def __init__(self, epoch=0):
        self.epoch = epoch

    def forward(self, seconds):
        self.epoch += seconds

    def __call__(self):
        return datetime.datetime.utcfromtimestamp(self.epoch)


class KazooLeaseTests(KazooTestCase):
    def setUp(self):
        super(KazooLeaseTests, self).setUp()
        self.client2 = self._get_client(timeout=0.8)
        self.client2.start()
        self.client3 = self._get_client(timeout=0.8)
        self.client3.start()
        self.path = "/" + uuid.uuid4().hex
        self.clock = MockClock(10)

    def tearDown(self):
        for cl in [self.client2, self.client3]:
            if cl.connected:
                cl.stop()
                cl.close()
        del self.client2
        del self.client3


class NonBlockingLeaseTests(KazooLeaseTests):
    def test_renew(self):
        # Use client convenience method here to test it at least once.  Use
        # class directly in
        # other tests in order to get better IDE support.
        lease = self.client.NonBlockingLease(self.path,
                                             datetime.timedelta(seconds=3),
                                             utcnow=self.clock)
        assert lease
        assert lease.obtained is True

        self.clock.forward(2)
        renewed_lease = self.client.NonBlockingLease(
            self.path, datetime.timedelta(seconds=3), utcnow=self.clock)
        assert renewed_lease

    def test_busy(self):
        lease = NonBlockingLease(self.client, self.path,
                                 datetime.timedelta(seconds=3),
                                 utcnow=self.clock)
        assert lease

        self.clock.forward(2)
        foreigner_lease = NonBlockingLease(
            self.client2, self.path, datetime.timedelta(seconds=3),
            identifier="some.other.host", utcnow=self.clock)
        assert not foreigner_lease
        assert foreigner_lease.obtained is False

    def test_overtake(self):
        lease = NonBlockingLease(self.client, self.path,
                                 datetime.timedelta(seconds=3),
                                 utcnow=self.clock)
        assert lease

        self.clock.forward(4)
        foreigner_lease = NonBlockingLease(
            self.client2, self.path, datetime.timedelta(seconds=3),
            identifier="some.other.host", utcnow=self.clock)
        assert foreigner_lease

    def test_renew_no_overtake(self):
        lease = self.client.NonBlockingLease(self.path,
                                             datetime.timedelta(seconds=3),
                                             utcnow=self.clock)
        assert lease
        assert lease.obtained is True

        self.clock.forward(2)
        renewed_lease = self.client.NonBlockingLease(
            self.path, datetime.timedelta(seconds=3), utcnow=self.clock)
        assert renewed_lease

        self.clock.forward(2)
        foreigner_lease = NonBlockingLease(
            self.client2, self.path, datetime.timedelta(seconds=3),
            identifier="some.other.host", utcnow=self.clock)
        assert not foreigner_lease

    def test_overtaker_renews(self):
        lease = NonBlockingLease(self.client, self.path,
                                 datetime.timedelta(seconds=3),
                                 utcnow=self.clock)
        assert lease

        self.clock.forward(4)
        foreigner_lease = NonBlockingLease(
            self.client2, self.path, datetime.timedelta(seconds=3),
            identifier="some.other.host", utcnow=self.clock)
        assert foreigner_lease

        self.clock.forward(2)
        foreigner_renew = NonBlockingLease(
            self.client2, self.path, datetime.timedelta(seconds=3),
            identifier="some.other.host", utcnow=self.clock)
        assert foreigner_renew

    def test_overtake_refuse_first(self):
        lease = NonBlockingLease(self.client, self.path,
                                 datetime.timedelta(seconds=3),
                                 utcnow=self.clock)
        assert lease

        self.clock.forward(4)
        foreigner_lease = NonBlockingLease(
            self.client2, self.path, datetime.timedelta(seconds=3),
            identifier="some.other.host", utcnow=self.clock)
        assert foreigner_lease

        self.clock.forward(2)
        first_again_lease = NonBlockingLease(
            self.client, self.path, datetime.timedelta(seconds=3),
            utcnow=self.clock)
        assert not first_again_lease

    def test_old_version(self):
        # Skip to a future version
        NonBlockingLease._version += 1
        lease = NonBlockingLease(self.client, self.path,
                                 datetime.timedelta(seconds=3),
                                 utcnow=self.clock)
        assert lease

        # Then back to today.
        NonBlockingLease._version -= 1
        self.clock.forward(4)
        foreigner_lease = NonBlockingLease(
            self.client2, self.path, datetime.timedelta(seconds=3),
            identifier="some.other.host", utcnow=self.clock)
        # Since a newer version wrote the lease file, the lease is not taken.
        assert not foreigner_lease


class MultiNonBlockingLeaseTest(KazooLeaseTests):
    def test_1_renew(self):
        ls = self.client.MultiNonBlockingLease(1, self.path,
                                               datetime.timedelta(seconds=4),
                                               utcnow=self.clock)
        assert ls
        self.clock.forward(2)
        ls2 = MultiNonBlockingLease(self.client, 1, self.path,
                                    datetime.timedelta(seconds=4),
                                    utcnow=self.clock)
        assert ls2

    def test_1_reject(self):
        ls = MultiNonBlockingLease(self.client, 1, self.path,
                                   datetime.timedelta(seconds=4),
                                   utcnow=self.clock)
        assert ls
        self.clock.forward(2)
        ls2 = MultiNonBlockingLease(self.client2, 1, self.path,
                                    datetime.timedelta(seconds=4),
                                    identifier="some.other.host",
                                    utcnow=self.clock)
        assert not ls2

    def test_2_renew(self):
        ls = MultiNonBlockingLease(self.client, 2, self.path,
                                   datetime.timedelta(seconds=7),
                                   utcnow=self.clock)
        assert ls
        self.clock.forward(2)
        ls2 = MultiNonBlockingLease(self.client2, 2, self.path,
                                    datetime.timedelta(seconds=7),
                                    identifier="host2", utcnow=self.clock)
        assert ls2
        self.clock.forward(2)
        ls3 = MultiNonBlockingLease(self.client, 2, self.path,
                                    datetime.timedelta(seconds=7),
                                    utcnow=self.clock)
        assert ls3
        self.clock.forward(2)
        ls4 = MultiNonBlockingLease(self.client2, 2, self.path,
                                    datetime.timedelta(seconds=7),
                                    identifier="host2", utcnow=self.clock)
        assert ls4

    def test_2_reject(self):
        ls = MultiNonBlockingLease(self.client, 2, self.path,
                                   datetime.timedelta(seconds=7),
                                   utcnow=self.clock)
        assert ls
        self.clock.forward(2)
        ls2 = MultiNonBlockingLease(self.client2, 2, self.path,
                                    datetime.timedelta(seconds=7),
                                    identifier="host2", utcnow=self.clock)
        assert ls2
        self.clock.forward(2)
        ls3 = MultiNonBlockingLease(self.client3, 2, self.path,
                                    datetime.timedelta(seconds=7),
                                    identifier="host3", utcnow=self.clock)
        assert not ls3

    def test_2_handover(self):
        ls = MultiNonBlockingLease(self.client, 2, self.path,
                                   datetime.timedelta(seconds=4),
                                   utcnow=self.clock)
        assert ls
        self.clock.forward(2)
        ls2 = MultiNonBlockingLease(self.client2, 2, self.path,
                                    datetime.timedelta(seconds=4),
                                    identifier="host2", utcnow=self.clock)
        assert ls2
        self.clock.forward(3)
        ls3 = MultiNonBlockingLease(self.client3, 2, self.path,
                                    datetime.timedelta(seconds=4),
                                    identifier="host3", utcnow=self.clock)
        assert ls3
        self.clock.forward(2)
        ls4 = MultiNonBlockingLease(self.client, 2, self.path,
                                    datetime.timedelta(seconds=4),
                                    utcnow=self.clock)
        assert ls4
