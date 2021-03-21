import threading

from kazoo.testing import KazooTestCase


class KazooBarrierTests(KazooTestCase):
    def test_barrier_not_exist(self):
        b = self.client.Barrier("/some/path")
        assert b.wait()

    def test_barrier_exists(self):
        b = self.client.Barrier("/some/path")
        b.create()
        assert not b.wait(0)
        b.remove()
        assert b.wait()

    def test_remove_nonexistent_barrier(self):
        b = self.client.Barrier("/some/path")
        assert not b.remove()


class KazooDoubleBarrierTests(KazooTestCase):
    def test_basic_barrier(self):
        b = self.client.DoubleBarrier("/some/path", 1)
        assert not b.participating
        b.enter()
        assert b.participating
        b.leave()
        assert not b.participating

    def test_two_barrier(self):
        av = threading.Event()
        ev = threading.Event()
        bv = threading.Event()
        release_all = threading.Event()
        b1 = self.client.DoubleBarrier("/some/path", 2)
        b2 = self.client.DoubleBarrier("/some/path", 2)

        def make_barrier_one():
            b1.enter()
            ev.set()
            release_all.wait()
            b1.leave()
            ev.set()

        def make_barrier_two():
            bv.wait()
            b2.enter()
            av.set()
            release_all.wait()
            b2.leave()
            av.set()

        # Spin up both of them
        t1 = threading.Thread(target=make_barrier_one)
        t1.start()
        t2 = threading.Thread(target=make_barrier_two)
        t2.start()

        assert not b1.participating
        assert not b2.participating

        bv.set()
        av.wait()
        ev.wait()
        assert b1.participating
        assert b2.participating

        av.clear()
        ev.clear()

        release_all.set()
        av.wait()
        ev.wait()
        assert not b1.participating
        assert not b2.participating
        t1.join()
        t2.join()

    def test_three_barrier(self):
        av = threading.Event()
        ev = threading.Event()
        bv = threading.Event()
        release_all = threading.Event()
        b1 = self.client.DoubleBarrier("/some/path", 3)
        b2 = self.client.DoubleBarrier("/some/path", 3)
        b3 = self.client.DoubleBarrier("/some/path", 3)

        def make_barrier_one():
            b1.enter()
            ev.set()
            release_all.wait()
            b1.leave()
            ev.set()

        def make_barrier_two():
            bv.wait()
            b2.enter()
            av.set()
            release_all.wait()
            b2.leave()
            av.set()

        # Spin up both of them
        t1 = threading.Thread(target=make_barrier_one)
        t1.start()
        t2 = threading.Thread(target=make_barrier_two)
        t2.start()

        assert not b1.participating
        assert not b2.participating

        bv.set()
        assert not b1.participating
        assert not b2.participating
        b3.enter()
        ev.wait()
        av.wait()

        assert b1.participating
        assert b2.participating
        assert b3.participating

        av.clear()
        ev.clear()

        release_all.set()
        b3.leave()
        av.wait()
        ev.wait()
        assert not b1.participating
        assert not b2.participating
        assert not b3.participating
        t1.join()
        t2.join()

    def test_barrier_existing_parent_node(self):
        b = self.client.DoubleBarrier('/some/path', 1)
        assert b.participating is False
        self.client.create('/some', ephemeral=True)
        # the barrier cannot create children under an ephemeral node
        b.enter()
        assert b.participating is False

    def test_barrier_existing_node(self):
        b = self.client.DoubleBarrier('/some', 1)
        assert b.participating is False
        self.client.ensure_path(b.path)
        self.client.create(b.create_path, ephemeral=True)
        # the barrier will re-use an existing node
        b.enter()
        assert b.participating is True
        b.leave()
