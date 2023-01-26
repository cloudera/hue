import gc
import random

import eventlet
from eventlet import hubs, pools
from eventlet.support import greenlets as greenlet
import six
import tests


def passthru(a):
    eventlet.sleep(0.01)
    return a


def passthru2(a, b):
    eventlet.sleep(0.01)
    return a, b


def raiser(exc):
    raise exc


class GreenPool(tests.LimitedTestCase):
    def test_spawn(self):
        p = eventlet.GreenPool(4)
        waiters = []
        for i in range(10):
            waiters.append(p.spawn(passthru, i))
        results = [waiter.wait() for waiter in waiters]
        self.assertEqual(results, list(range(10)))

    def test_spawn_n(self):
        p = eventlet.GreenPool(4)
        results_closure = []

        def do_something(a):
            eventlet.sleep(0.01)
            results_closure.append(a)

        for i in range(10):
            p.spawn(do_something, i)
        p.waitall()
        self.assertEqual(results_closure, list(range(10)))

    def test_waiting(self):
        pool = eventlet.GreenPool(1)
        done = eventlet.Event()

        def consume():
            done.wait()

        def waiter(pool):
            gt = pool.spawn(consume)
            gt.wait()

        waiters = []
        self.assertEqual(pool.running(), 0)
        waiters.append(eventlet.spawn(waiter, pool))
        eventlet.sleep(0)
        self.assertEqual(pool.waiting(), 0)
        waiters.append(eventlet.spawn(waiter, pool))
        eventlet.sleep(0)
        self.assertEqual(pool.waiting(), 1)
        waiters.append(eventlet.spawn(waiter, pool))
        eventlet.sleep(0)
        self.assertEqual(pool.waiting(), 2)
        self.assertEqual(pool.running(), 1)
        done.send(None)
        for w in waiters:
            w.wait()
        self.assertEqual(pool.waiting(), 0)
        self.assertEqual(pool.running(), 0)

    def test_multiple_coros(self):
        evt = eventlet.Event()
        results = []

        def producer():
            results.append('prod')
            evt.send()

        def consumer():
            results.append('cons1')
            evt.wait()
            results.append('cons2')

        pool = eventlet.GreenPool(2)
        done = pool.spawn(consumer)
        pool.spawn_n(producer)
        done.wait()
        self.assertEqual(['cons1', 'prod', 'cons2'], results)

    def test_timer_cancel(self):
        # this test verifies that local timers are not fired
        # outside of the context of the spawn
        timer_fired = []

        def fire_timer():
            timer_fired.append(True)

        def some_work():
            hubs.get_hub().schedule_call_local(0, fire_timer)

        pool = eventlet.GreenPool(2)
        worker = pool.spawn(some_work)
        worker.wait()
        eventlet.sleep(0)
        eventlet.sleep(0)
        self.assertEqual(timer_fired, [])

    def test_reentrant(self):
        pool = eventlet.GreenPool(1)

        def reenter():
            waiter = pool.spawn(lambda a: a, 'reenter')
            self.assertEqual('reenter', waiter.wait())

        outer_waiter = pool.spawn(reenter)
        outer_waiter.wait()

        evt = eventlet.Event()

        def reenter_async():
            pool.spawn_n(lambda a: a, 'reenter')
            evt.send('done')

        pool.spawn_n(reenter_async)
        self.assertEqual('done', evt.wait())

    def assert_pool_has_free(self, pool, num_free):
        self.assertEqual(pool.free(), num_free)

        def wait_long_time(e):
            e.wait()

        timer = eventlet.Timeout(1)
        try:
            evt = eventlet.Event()
            for x in six.moves.range(num_free):
                pool.spawn(wait_long_time, evt)
                # if the pool has fewer free than we expect,
                # then we'll hit the timeout error
        finally:
            timer.cancel()

        # if the runtime error is not raised it means the pool had
        # some unexpected free items
        timer = eventlet.Timeout(0, RuntimeError)
        try:
            self.assertRaises(RuntimeError, pool.spawn, wait_long_time, evt)
        finally:
            timer.cancel()

        # clean up by causing all the wait_long_time functions to return
        evt.send(None)
        eventlet.sleep(0)
        eventlet.sleep(0)

    def test_resize(self):
        pool = eventlet.GreenPool(2)
        evt = eventlet.Event()

        def wait_long_time(e):
            e.wait()

        pool.spawn(wait_long_time, evt)
        pool.spawn(wait_long_time, evt)
        self.assertEqual(pool.free(), 0)
        self.assertEqual(pool.running(), 2)
        self.assert_pool_has_free(pool, 0)

        # verify that the pool discards excess items put into it
        pool.resize(1)

        # cause the wait_long_time functions to return, which will
        # trigger puts to the pool
        evt.send(None)
        eventlet.sleep(0)
        eventlet.sleep(0)

        self.assertEqual(pool.free(), 1)
        self.assertEqual(pool.running(), 0)
        self.assert_pool_has_free(pool, 1)

        # resize larger and assert that there are more free items
        pool.resize(2)
        self.assertEqual(pool.free(), 2)
        self.assertEqual(pool.running(), 0)
        self.assert_pool_has_free(pool, 2)

    def test_pool_smash(self):
        # The premise is that a coroutine in a Pool tries to get a token out
        # of a token pool but times out before getting the token.  We verify
        # that neither pool is adversely affected by this situation.
        pool = eventlet.GreenPool(1)
        tp = pools.TokenPool(max_size=1)
        tp.get()  # empty out the pool

        def do_receive(tp):
            timer = eventlet.Timeout(0, RuntimeError())
            try:
                tp.get()
                self.fail("Shouldn't have received anything from the pool")
            except RuntimeError:
                return 'timed out'
            else:
                timer.cancel()

        # the spawn makes the token pool expect that coroutine, but then
        # immediately cuts bait
        e1 = pool.spawn(do_receive, tp)
        self.assertEqual(e1.wait(), 'timed out')

        # the pool can get some random item back
        def send_wakeup(tp):
            tp.put('wakeup')
        gt = eventlet.spawn(send_wakeup, tp)

        # now we ask the pool to run something else, which should not
        # be affected by the previous send at all
        def resume():
            return 'resumed'
        e2 = pool.spawn(resume)
        self.assertEqual(e2.wait(), 'resumed')

        # we should be able to get out the thing we put in there, too
        self.assertEqual(tp.get(), 'wakeup')
        gt.wait()

    def test_spawn_n_2(self):
        p = eventlet.GreenPool(2)
        self.assertEqual(p.free(), 2)
        r = []

        def foo(a):
            r.append(a)

        gt = p.spawn(foo, 1)
        self.assertEqual(p.free(), 1)
        gt.wait()
        self.assertEqual(r, [1])
        eventlet.sleep(0)
        self.assertEqual(p.free(), 2)

        # Once the pool is exhausted, spawning forces a yield.
        p.spawn_n(foo, 2)
        self.assertEqual(1, p.free())
        self.assertEqual(r, [1])

        p.spawn_n(foo, 3)
        self.assertEqual(0, p.free())
        self.assertEqual(r, [1])

        p.spawn_n(foo, 4)
        self.assertEqual(set(r), set([1, 2, 3]))
        eventlet.sleep(0)
        self.assertEqual(set(r), set([1, 2, 3, 4]))

    def test_exceptions(self):
        p = eventlet.GreenPool(2)
        for m in (p.spawn, p.spawn_n):
            self.assert_pool_has_free(p, 2)
            m(raiser, RuntimeError())
            self.assert_pool_has_free(p, 1)
            p.waitall()
            self.assert_pool_has_free(p, 2)
            m(raiser, greenlet.GreenletExit)
            self.assert_pool_has_free(p, 1)
            p.waitall()
            self.assert_pool_has_free(p, 2)

    def test_imap(self):
        p = eventlet.GreenPool(4)
        result_list = list(p.imap(passthru, range(10)))
        self.assertEqual(result_list, list(range(10)))

    def test_empty_imap(self):
        p = eventlet.GreenPool(4)
        result_iter = p.imap(passthru, [])
        self.assertRaises(StopIteration, result_iter.next)

    def test_imap_nonefunc(self):
        p = eventlet.GreenPool(4)
        result_list = list(p.imap(None, range(10)))
        self.assertEqual(result_list, [(x,) for x in range(10)])

    def test_imap_multi_args(self):
        p = eventlet.GreenPool(4)
        result_list = list(p.imap(passthru2, range(10), range(10, 20)))
        self.assertEqual(result_list, list(zip(range(10), range(10, 20))))

    def test_imap_raises(self):
        # testing the case where the function raises an exception;
        # both that the caller sees that exception, and that the iterator
        # continues to be usable to get the rest of the items
        p = eventlet.GreenPool(4)

        def raiser(item):
            if item == 1 or item == 7:
                raise RuntimeError("intentional error")
            else:
                return item

        it = p.imap(raiser, range(10))
        results = []
        while True:
            try:
                results.append(six.next(it))
            except RuntimeError:
                results.append('r')
            except StopIteration:
                break
        self.assertEqual(results, [0, 'r', 2, 3, 4, 5, 6, 'r', 8, 9])

    def test_starmap(self):
        p = eventlet.GreenPool(4)
        result_list = list(p.starmap(passthru, [(x,) for x in range(10)]))
        self.assertEqual(result_list, list(range(10)))

    def test_waitall_on_nothing(self):
        p = eventlet.GreenPool()
        p.waitall()

    def test_recursive_waitall(self):
        p = eventlet.GreenPool()
        gt = p.spawn(p.waitall)
        self.assertRaises(AssertionError, gt.wait)


class GreenPile(tests.LimitedTestCase):
    def test_pile(self):
        p = eventlet.GreenPile(4)
        for i in range(10):
            p.spawn(passthru, i)
        result_list = list(p)
        self.assertEqual(result_list, list(range(10)))

    def test_pile_spawn_times_out(self):
        p = eventlet.GreenPile(4)
        for i in range(4):
            p.spawn(passthru, i)
        # now it should be full and this should time out
        eventlet.Timeout(0)
        self.assertRaises(eventlet.Timeout, p.spawn, passthru, "time out")
        # verify that the spawn breakage didn't interrupt the sequence
        # and terminates properly
        for i in range(4, 10):
            p.spawn(passthru, i)
        self.assertEqual(list(p), list(range(10)))

    def test_empty_pile(self):
        p = eventlet.GreenPile(4)
        # no spawn()s
        # If this hangs, LimitedTestCase should time out
        self.assertEqual(list(p), [])

    def test_constructing_from_pool(self):
        pool = eventlet.GreenPool(2)
        pile1 = eventlet.GreenPile(pool)
        pile2 = eventlet.GreenPile(pool)

        def bunch_of_work(pile, unique):
            for i in range(10):
                pile.spawn(passthru, i + unique)

        eventlet.spawn(bunch_of_work, pile1, 0)
        eventlet.spawn(bunch_of_work, pile2, 100)
        eventlet.sleep(0)
        self.assertEqual(list(pile2), list(range(100, 110)))
        self.assertEqual(list(pile1), list(range(10)))


def test_greenpool_type_check():
    eventlet.GreenPool(0)
    eventlet.GreenPool(1)
    eventlet.GreenPool(1e3)

    with tests.assert_raises(TypeError):
        eventlet.GreenPool('foo')
    with tests.assert_raises(ValueError):
        eventlet.GreenPool(-1)


class StressException(Exception):
    pass

r = random.Random(0)


def pressure(arg):
    while r.random() < 0.5:
        eventlet.sleep(r.random() * 0.001)
    if r.random() < 0.8:
        return arg
    else:
        raise StressException(arg)


def passthru(arg):
    while r.random() < 0.5:
        eventlet.sleep(r.random() * 0.001)
    return arg


class Stress(tests.LimitedTestCase):
    # tests will take extra-long
    TEST_TIMEOUT = 60

    def spawn_order_check(self, concurrency):
        # checks that piles are strictly ordered
        p = eventlet.GreenPile(concurrency)

        def makework(count, unique):
            for i in six.moves.range(count):
                token = (unique, i)
                p.spawn(pressure, token)

        iters = 1000
        eventlet.spawn(makework, iters, 1)
        eventlet.spawn(makework, iters, 2)
        eventlet.spawn(makework, iters, 3)
        p.spawn(pressure, (0, 0))
        latest = [-1] * 4
        received = 0
        it = iter(p)
        while True:
            try:
                i = six.next(it)
            except StressException as exc:
                i = exc.args[0]
            except StopIteration:
                break
            received += 1
            if received % 5 == 0:
                eventlet.sleep(0.0001)
            unique, order = i
            assert latest[unique] < order
            latest[unique] = order
        for l in latest[1:]:
            self.assertEqual(l, iters - 1)

    def test_ordering_5(self):
        self.spawn_order_check(5)

    def test_ordering_50(self):
        self.spawn_order_check(50)

    def imap_memory_check(self, concurrency):
        # checks that imap is strictly
        # ordered and consumes a constant amount of memory
        p = eventlet.GreenPool(concurrency)
        count = 1000
        it = p.imap(passthru, six.moves.range(count))
        latest = -1
        while True:
            try:
                i = six.next(it)
            except StopIteration:
                break

            if latest == -1:
                gc.collect()
                initial_obj_count = len(gc.get_objects())
            assert i > latest
            latest = i
            if latest % 5 == 0:
                eventlet.sleep(0.001)
            if latest % 10 == 0:
                gc.collect()
                objs_created = len(gc.get_objects()) - initial_obj_count
                assert objs_created < 25 * concurrency, objs_created
        # make sure we got to the end
        self.assertEqual(latest, count - 1)

    def test_imap_50(self):
        self.imap_memory_check(50)

    def test_imap_500(self):
        self.imap_memory_check(500)

    def test_with_intpool(self):
        class IntPool(pools.Pool):
            def create(self):
                self.current_integer = getattr(self, 'current_integer', 0) + 1
                return self.current_integer

        def subtest(intpool_size, pool_size, num_executes):
            def run(int_pool):
                token = int_pool.get()
                eventlet.sleep(0.0001)
                int_pool.put(token)
                return token

            int_pool = IntPool(max_size=intpool_size)
            pool = eventlet.GreenPool(pool_size)
            for ix in six.moves.range(num_executes):
                pool.spawn(run, int_pool)
            pool.waitall()

        subtest(4, 7, 7)
        subtest(50, 75, 100)
        for isize in (10, 20, 30, 40, 50):
            for psize in (5, 25, 35, 50):
                subtest(isize, psize, psize)
