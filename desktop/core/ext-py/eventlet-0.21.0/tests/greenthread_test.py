from tests import LimitedTestCase
from eventlet import greenthread
from eventlet.support import greenlets as greenlet

_g_results = []


def passthru(*args, **kw):
    _g_results.append((args, kw))
    return args, kw


def waiter(a):
    greenthread.sleep(0.1)
    return a


class Asserts(object):
    def assert_dead(self, gt):
        if hasattr(gt, 'wait'):
            self.assertRaises(greenlet.GreenletExit, gt.wait)
        assert gt.dead
        assert not gt


class Spawn(LimitedTestCase, Asserts):
    def tearDown(self):
        global _g_results
        super(Spawn, self).tearDown()
        _g_results = []

    def test_simple(self):
        gt = greenthread.spawn(passthru, 1, b=2)
        self.assertEqual(gt.wait(), ((1,), {'b': 2}))
        self.assertEqual(_g_results, [((1,), {'b': 2})])

    def test_n(self):
        gt = greenthread.spawn_n(passthru, 2, b=3)
        assert not gt.dead
        greenthread.sleep(0)
        assert gt.dead
        self.assertEqual(_g_results, [((2,), {'b': 3})])

    def test_kill(self):
        gt = greenthread.spawn(passthru, 6)
        greenthread.kill(gt)
        self.assert_dead(gt)
        greenthread.sleep(0.001)
        self.assertEqual(_g_results, [])
        greenthread.kill(gt)
        self.assert_dead(gt)

    def test_kill_meth(self):
        gt = greenthread.spawn(passthru, 6)
        gt.kill()
        self.assert_dead(gt)
        greenthread.sleep(0.001)
        self.assertEqual(_g_results, [])
        gt.kill()
        self.assert_dead(gt)

    def test_kill_n(self):
        gt = greenthread.spawn_n(passthru, 7)
        greenthread.kill(gt)
        self.assert_dead(gt)
        greenthread.sleep(0.001)
        self.assertEqual(_g_results, [])
        greenthread.kill(gt)
        self.assert_dead(gt)

    def test_link(self):
        results = []

        def link_func(g, *a, **kw):
            results.append(g)
            results.append(a)
            results.append(kw)
        gt = greenthread.spawn(passthru, 5)
        gt.link(link_func, 4, b=5)
        self.assertEqual(gt.wait(), ((5,), {}))
        self.assertEqual(results, [gt, (4,), {'b': 5}])

    def test_link_after_exited(self):
        results = []

        def link_func(g, *a, **kw):
            results.append(g)
            results.append(a)
            results.append(kw)
        gt = greenthread.spawn(passthru, 5)
        self.assertEqual(gt.wait(), ((5,), {}))
        gt.link(link_func, 4, b=5)
        self.assertEqual(results, [gt, (4,), {'b': 5}])

    def test_link_relinks(self):
        # test that linking in a linked func doesn't cause infinite recursion.
        called = []

        def link_func(g):
            g.link(link_func_pass)

        def link_func_pass(g):
            called.append(True)

        gt = greenthread.spawn(passthru)
        gt.link(link_func)
        gt.wait()
        self.assertEqual(called, [True])


class SpawnAfter(Spawn):
    def test_basic(self):
        gt = greenthread.spawn_after(0.1, passthru, 20)
        self.assertEqual(gt.wait(), ((20,), {}))

    def test_cancel(self):
        gt = greenthread.spawn_after(0.1, passthru, 21)
        gt.cancel()
        self.assert_dead(gt)

    def test_cancel_already_started(self):
        gt = greenthread.spawn_after(0, waiter, 22)
        greenthread.sleep(0)
        gt.cancel()
        self.assertEqual(gt.wait(), 22)

    def test_kill_already_started(self):
        gt = greenthread.spawn_after(0, waiter, 22)
        greenthread.sleep(0)
        gt.kill()
        self.assert_dead(gt)


class SpawnAfterLocal(LimitedTestCase, Asserts):
    def setUp(self):
        super(SpawnAfterLocal, self).setUp()
        self.lst = [1]

    def test_timer_fired(self):
        def func():
            greenthread.spawn_after_local(0.1, self.lst.pop)
            greenthread.sleep(0.2)

        greenthread.spawn(func)
        assert self.lst == [1], self.lst
        greenthread.sleep(0.3)
        assert self.lst == [], self.lst

    def test_timer_cancelled_upon_greenlet_exit(self):
        def func():
            greenthread.spawn_after_local(0.1, self.lst.pop)

        greenthread.spawn(func)
        assert self.lst == [1], self.lst
        greenthread.sleep(0.2)
        assert self.lst == [1], self.lst

    def test_spawn_is_not_cancelled(self):
        def func():
            greenthread.spawn(self.lst.pop)
            # exiting immediatelly, but self.lst.pop must be called
        greenthread.spawn(func)
        greenthread.sleep(0.1)
        assert self.lst == [], self.lst
