from unittest import TestCase, main

import eventlet
from eventlet import Queue
from eventlet import pools
from eventlet.support import six


class IntPool(pools.Pool):
    def create(self):
        self.current_integer = getattr(self, 'current_integer', 0) + 1
        return self.current_integer


class TestIntPool(TestCase):
    def setUp(self):
        self.pool = IntPool(min_size=0, max_size=4)

    def test_integers(self):
        # Do not actually use this pattern in your code. The pool will be
        # exhausted, and unrestoreable.
        # If you do a get, you should ALWAYS do a put, probably like this:
        # try:
        #     thing = self.pool.get()
        # do stuff
        # finally:
        #     self.pool.put(thing)

        # with self.pool.some_api_name() as thing:
        # do stuff
        self.assertEqual(self.pool.get(), 1)
        self.assertEqual(self.pool.get(), 2)
        self.assertEqual(self.pool.get(), 3)
        self.assertEqual(self.pool.get(), 4)

    def test_free(self):
        self.assertEqual(self.pool.free(), 4)
        gotten = self.pool.get()
        self.assertEqual(self.pool.free(), 3)
        self.pool.put(gotten)
        self.assertEqual(self.pool.free(), 4)

    def test_exhaustion(self):
        waiter = Queue(0)

        def consumer():
            gotten = None
            try:
                gotten = self.pool.get()
            finally:
                waiter.put(gotten)

        eventlet.spawn(consumer)

        one, two, three, four = (
            self.pool.get(), self.pool.get(), self.pool.get(), self.pool.get())
        self.assertEqual(self.pool.free(), 0)

        # Let consumer run; nothing will be in the pool, so he will wait
        eventlet.sleep(0)

        # Wake consumer
        self.pool.put(one)

        # wait for the consumer
        self.assertEqual(waiter.get(), one)

    def test_blocks_on_pool(self):
        waiter = Queue(0)

        def greedy():
            self.pool.get()
            self.pool.get()
            self.pool.get()
            self.pool.get()
            # No one should be waiting yet.
            self.assertEqual(self.pool.waiting(), 0)
            # The call to the next get will unschedule this routine.
            self.pool.get()
            # So this put should never be called.
            waiter.put('Failed!')

        killable = eventlet.spawn(greedy)

        # no one should be waiting yet.
        self.assertEqual(self.pool.waiting(), 0)

        # Wait for greedy
        eventlet.sleep(0)

        # Greedy should be blocking on the last get
        self.assertEqual(self.pool.waiting(), 1)

        # Send will never be called, so balance should be 0.
        self.assertFalse(not waiter.full())

        eventlet.kill(killable)

    def test_ordering(self):
        # normal case is that items come back out in the
        # same order they are put
        one, two = self.pool.get(), self.pool.get()
        self.pool.put(one)
        self.pool.put(two)
        self.assertEqual(self.pool.get(), one)
        self.assertEqual(self.pool.get(), two)

    def test_putting_to_queue(self):
        timer = eventlet.Timeout(0.1)
        try:
            size = 2
            self.pool = IntPool(min_size=0, max_size=size)
            queue = Queue()
            results = []

            def just_put(pool_item, index):
                self.pool.put(pool_item)
                queue.put(index)
            for index in six.moves.range(size + 1):
                pool_item = self.pool.get()
                eventlet.spawn(just_put, pool_item, index)

            for _ in six.moves.range(size + 1):
                x = queue.get()
                results.append(x)
            self.assertEqual(sorted(results), list(six.moves.range(size + 1)))
        finally:
            timer.cancel()

    def test_resize(self):
        pool = IntPool(max_size=2)
        a = pool.get()
        b = pool.get()
        self.assertEqual(pool.free(), 0)

        # verify that the pool discards excess items put into it
        pool.resize(1)
        pool.put(a)
        pool.put(b)
        self.assertEqual(pool.free(), 1)

        # resize larger and assert that there are more free items
        pool.resize(2)
        self.assertEqual(pool.free(), 2)

    def test_create_contention(self):
        creates = [0]

        def sleep_create():
            creates[0] += 1
            eventlet.sleep()
            return "slept"

        p = pools.Pool(max_size=4, create=sleep_create)

        def do_get():
            x = p.get()
            self.assertEqual(x, "slept")
            p.put(x)

        gp = eventlet.GreenPool()
        for i in six.moves.range(100):
            gp.spawn_n(do_get)
        gp.waitall()
        self.assertEqual(creates[0], 4)


class TestAbstract(TestCase):
    mode = 'static'

    def test_abstract(self):
        # Going for 100% coverage here
        # A Pool cannot be used without overriding create()
        pool = pools.Pool()
        self.assertRaises(NotImplementedError, pool.get)


class TestIntPool2(TestCase):
    mode = 'static'

    def setUp(self):
        self.pool = IntPool(min_size=3, max_size=3)

    def test_something(self):
        self.assertEqual(len(self.pool.free_items), 3)
        # Cover the clause in get where we get from the free list instead of creating
        # an item on get
        gotten = self.pool.get()
        self.assertEqual(gotten, 1)


class TestOrderAsStack(TestCase):
    mode = 'static'

    def setUp(self):
        self.pool = IntPool(max_size=3, order_as_stack=True)

    def test_ordering(self):
        # items come out in the reverse order they are put
        one, two = self.pool.get(), self.pool.get()
        self.pool.put(one)
        self.pool.put(two)
        self.assertEqual(self.pool.get(), two)
        self.assertEqual(self.pool.get(), one)


class RaisePool(pools.Pool):
    def create(self):
        raise RuntimeError()


class TestCreateRaises(TestCase):
    mode = 'static'

    def setUp(self):
        self.pool = RaisePool(max_size=3)

    def test_it(self):
        self.assertEqual(self.pool.free(), 3)
        self.assertRaises(RuntimeError, self.pool.get)
        self.assertEqual(self.pool.free(), 3)


ALWAYS = RuntimeError('I always fail')
SOMETIMES = RuntimeError('I fail half the time')


class TestTookTooLong(Exception):
    pass

if __name__ == '__main__':
    main()
