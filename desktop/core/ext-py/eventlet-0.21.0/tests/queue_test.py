import eventlet
from eventlet import event, hubs, queue
from tests import LimitedTestCase, main


def do_bail(q):
    eventlet.Timeout(0, RuntimeError())
    try:
        result = q.get()
        return result
    except RuntimeError:
        return 'timed out'


class TestQueue(LimitedTestCase):
    def test_send_first(self):
        q = eventlet.Queue()
        q.put('hi')
        self.assertEqual(q.get(), 'hi')

    def test_send_last(self):
        q = eventlet.Queue()

        def waiter(q):
            self.assertEqual(q.get(), 'hi2')

        gt = eventlet.spawn(eventlet.with_timeout, 0.1, waiter, q)
        eventlet.sleep(0)
        eventlet.sleep(0)
        q.put('hi2')
        gt.wait()

    def test_max_size(self):
        q = eventlet.Queue(2)
        results = []

        def putter(q):
            q.put('a')
            results.append('a')
            q.put('b')
            results.append('b')
            q.put('c')
            results.append('c')

        gt = eventlet.spawn(putter, q)
        eventlet.sleep(0)
        self.assertEqual(results, ['a', 'b'])
        self.assertEqual(q.get(), 'a')
        eventlet.sleep(0)
        self.assertEqual(results, ['a', 'b', 'c'])
        self.assertEqual(q.get(), 'b')
        self.assertEqual(q.get(), 'c')
        gt.wait()

    def test_zero_max_size(self):
        q = eventlet.Queue(0)

        def sender(evt, q):
            q.put('hi')
            evt.send('done')

        def receiver(q):
            x = q.get()
            return x

        evt = event.Event()
        gt = eventlet.spawn(sender, evt, q)
        eventlet.sleep(0)
        assert not evt.ready()
        gt2 = eventlet.spawn(receiver, q)
        self.assertEqual(gt2.wait(), 'hi')
        self.assertEqual(evt.wait(), 'done')
        gt.wait()

    def test_resize_up(self):
        q = eventlet.Queue(0)

        def sender(evt, q):
            q.put('hi')
            evt.send('done')

        evt = event.Event()
        gt = eventlet.spawn(sender, evt, q)
        eventlet.sleep(0)
        assert not evt.ready()
        q.resize(1)
        eventlet.sleep(0)
        assert evt.ready()
        gt.wait()

    def test_resize_down(self):
        q = eventlet.Queue(5)

        for i in range(5):
            q.put(i)

        self.assertEqual(list(q.queue), list(range(5)))
        q.resize(1)
        eventlet.sleep(0)
        self.assertEqual(list(q.queue), list(range(5)))

    def test_resize_to_Unlimited(self):
        q = eventlet.Queue(0)

        def sender(evt, q):
            q.put('hi')
            evt.send('done')

        evt = event.Event()
        gt = eventlet.spawn(sender, evt, q)
        eventlet.sleep()
        self.assertFalse(evt.ready())
        q.resize(None)
        eventlet.sleep()
        self.assertTrue(evt.ready())
        gt.wait()

    def test_multiple_waiters(self):
        # tests that multiple waiters get their results back
        q = eventlet.Queue()

        sendings = ['1', '2', '3', '4']
        gts = [eventlet.spawn(q.get) for x in sendings]

        eventlet.sleep(0.01)  # get 'em all waiting

        q.put(sendings[0])
        q.put(sendings[1])
        q.put(sendings[2])
        q.put(sendings[3])
        results = set()
        for i, gt in enumerate(gts):
            results.add(gt.wait())
        self.assertEqual(results, set(sendings))

    def test_waiters_that_cancel(self):
        q = eventlet.Queue()

        gt = eventlet.spawn(do_bail, q)
        self.assertEqual(gt.wait(), 'timed out')

        q.put('hi')
        self.assertEqual(q.get(), 'hi')

    def test_getting_before_sending(self):
        q = eventlet.Queue()
        gt = eventlet.spawn(q.put, 'sent')
        self.assertEqual(q.get(), 'sent')
        gt.wait()

    def test_two_waiters_one_dies(self):
        def waiter(q):
            return q.get()

        q = eventlet.Queue()
        dying = eventlet.spawn(do_bail, q)
        waiting = eventlet.spawn(waiter, q)
        eventlet.sleep(0)
        q.put('hi')
        self.assertEqual(dying.wait(), 'timed out')
        self.assertEqual(waiting.wait(), 'hi')

    def test_two_bogus_waiters(self):
        q = eventlet.Queue()
        gt1 = eventlet.spawn(do_bail, q)
        gt2 = eventlet.spawn(do_bail, q)
        eventlet.sleep(0)
        q.put('sent')
        self.assertEqual(gt1.wait(), 'timed out')
        self.assertEqual(gt2.wait(), 'timed out')
        self.assertEqual(q.get(), 'sent')

    def test_waiting(self):
        q = eventlet.Queue()
        gt1 = eventlet.spawn(q.get)
        eventlet.sleep(0)
        self.assertEqual(1, q.getting())
        q.put('hi')
        eventlet.sleep(0)
        self.assertEqual(0, q.getting())
        self.assertEqual('hi', gt1.wait())
        self.assertEqual(0, q.getting())

    def test_channel_send(self):
        channel = eventlet.Queue(0)
        events = []

        def another_greenlet():
            events.append(channel.get())
            events.append(channel.get())

        eventlet.spawn(another_greenlet)

        events.append('sending')
        channel.put('hello')
        events.append('sent hello')
        channel.put('world')
        events.append('sent world')

        self.assertEqual(['sending', 'hello', 'sent hello', 'world', 'sent world'], events)

    def test_channel_wait(self):
        channel = eventlet.Queue(0)
        events = []

        def another_greenlet():
            events.append('sending hello')
            channel.put('hello')
            events.append('sending world')
            channel.put('world')
            events.append('sent world')

        eventlet.spawn(another_greenlet)

        events.append('waiting')
        events.append(channel.get())
        events.append(channel.get())

        self.assertEqual(['waiting', 'sending hello', 'hello', 'sending world', 'world'], events)
        eventlet.sleep(0)
        self.assertEqual(
            ['waiting', 'sending hello', 'hello', 'sending world', 'world', 'sent world'], events)

    def test_channel_waiters(self):
        c = eventlet.Queue(0)
        w1 = eventlet.spawn(c.get)
        w2 = eventlet.spawn(c.get)
        w3 = eventlet.spawn(c.get)
        eventlet.sleep(0)
        self.assertEqual(c.getting(), 3)
        s1 = eventlet.spawn(c.put, 1)
        s2 = eventlet.spawn(c.put, 2)
        s3 = eventlet.spawn(c.put, 3)

        s1.wait()
        s2.wait()
        s3.wait()
        self.assertEqual(c.getting(), 0)
        # NOTE: we don't guarantee that waiters are served in order
        results = sorted([w1.wait(), w2.wait(), w3.wait()])
        self.assertEqual(results, [1, 2, 3])

    def test_channel_sender_timing_out(self):
        c = eventlet.Queue(0)
        self.assertRaises(queue.Full, c.put, "hi", timeout=0.001)
        self.assertRaises(queue.Empty, c.get_nowait)

    def test_task_done(self):
        channel = queue.Queue(0)
        X = object()
        gt = eventlet.spawn(channel.put, X)
        result = channel.get()
        assert result is X, (result, X)
        assert channel.unfinished_tasks == 1, channel.unfinished_tasks
        channel.task_done()
        assert channel.unfinished_tasks == 0, channel.unfinished_tasks
        gt.wait()

    def test_join_doesnt_block_when_queue_is_already_empty(self):
        queue = eventlet.Queue()
        queue.join()


def store_result(result, func, *args):
    try:
        result.append(func(*args))
    except Exception as exc:
        result.append(exc)


class TestNoWait(LimitedTestCase):
    def test_put_nowait_simple(self):
        hub = hubs.get_hub()
        result = []
        q = eventlet.Queue(1)
        hub.schedule_call_global(0, store_result, result, q.put_nowait, 2)
        hub.schedule_call_global(0, store_result, result, q.put_nowait, 3)
        eventlet.sleep(0)
        eventlet.sleep(0)
        assert len(result) == 2, result
        assert result[0] is None, result
        assert isinstance(result[1], queue.Full), result

    def test_get_nowait_simple(self):
        hub = hubs.get_hub()
        result = []
        q = queue.Queue(1)
        q.put(4)
        hub.schedule_call_global(0, store_result, result, q.get_nowait)
        hub.schedule_call_global(0, store_result, result, q.get_nowait)
        eventlet.sleep(0)
        assert len(result) == 2, result
        assert result[0] == 4, result
        assert isinstance(result[1], queue.Empty), result

    # get_nowait must work from the mainloop
    def test_get_nowait_unlock(self):
        hub = hubs.get_hub()
        result = []
        q = queue.Queue(0)
        p = eventlet.spawn(q.put, 5)
        assert q.empty(), q
        assert q.full(), q
        eventlet.sleep(0)
        assert q.empty(), q
        assert q.full(), q
        hub.schedule_call_global(0, store_result, result, q.get_nowait)
        eventlet.sleep(0)
        assert q.empty(), q
        assert q.full(), q
        assert result == [5], result
        # TODO add ready to greenthread
        # assert p.ready(), p
        assert p.dead, p
        assert q.empty(), q

    # put_nowait must work from the mainloop
    def test_put_nowait_unlock(self):
        hub = hubs.get_hub()
        result = []
        q = queue.Queue(0)
        eventlet.spawn(q.get)
        assert q.empty(), q
        assert q.full(), q
        eventlet.sleep(0)
        assert q.empty(), q
        assert q.full(), q
        hub.schedule_call_global(0, store_result, result, q.put_nowait, 10)
        # TODO ready method on greenthread
        # assert not p.ready(), p
        eventlet.sleep(0)
        assert result == [None], result
        # TODO ready method
        # assert p.ready(), p
        assert q.full(), q
        assert q.empty(), q


if __name__ == '__main__':
    main()
