import eventlet
import eventlet.hubs
from tests import LimitedTestCase


class TestEvent(LimitedTestCase):
    def test_waiting_for_event(self):
        evt = eventlet.Event()
        value = 'some stuff'

        def send_to_event():
            evt.send(value)
        eventlet.spawn_n(send_to_event)
        self.assertEqual(evt.wait(), value)

    def test_multiple_waiters(self):
        self._test_multiple_waiters(False)

    def test_multiple_waiters_with_exception(self):
        self._test_multiple_waiters(True)

    def _test_multiple_waiters(self, exception):
        evt = eventlet.Event()
        results = []

        def wait_on_event(i_am_done):
            evt.wait()
            results.append(True)
            i_am_done.send()
            if exception:
                raise Exception()

        waiters = []
        count = 5
        for i in range(count):
            waiters.append(eventlet.Event())
            eventlet.spawn_n(wait_on_event, waiters[-1])
        eventlet.sleep()  # allow spawns to start executing
        evt.send()

        for w in waiters:
            w.wait()

        self.assertEqual(len(results), count)

    def test_reset(self):
        evt = eventlet.Event()

        # calling reset before send should throw
        self.assertRaises(AssertionError, evt.reset)

        value = 'some stuff'

        def send_to_event():
            evt.send(value)
        eventlet.spawn_n(send_to_event)
        self.assertEqual(evt.wait(), value)

        # now try it again, and we should get the same exact value,
        # and we shouldn't be allowed to resend without resetting
        value2 = 'second stuff'
        self.assertRaises(AssertionError, evt.send, value2)
        self.assertEqual(evt.wait(), value)

        # reset and everything should be happy
        evt.reset()

        def send_to_event2():
            evt.send(value2)
        eventlet.spawn_n(send_to_event2)
        self.assertEqual(evt.wait(), value2)

    def test_double_exception(self):
        evt = eventlet.Event()
        # send an exception through the event
        evt.send(exc=RuntimeError('from test_double_exception'))
        self.assertRaises(RuntimeError, evt.wait)
        evt.reset()
        # shouldn't see the RuntimeError again
        eventlet.Timeout(0.001)
        self.assertRaises(eventlet.Timeout, evt.wait)


def test_wait_timeout_ok():
    evt = eventlet.Event()
    delay = 0.1
    eventlet.spawn_after(delay, evt.send, True)
    t1 = eventlet.hubs.get_hub().clock()
    with eventlet.Timeout(delay * 3, False):
        result = evt.wait(timeout=delay * 2)
        td = eventlet.hubs.get_hub().clock() - t1
        assert result
        assert td >= delay


def test_wait_timeout_exceed():
    evt = eventlet.Event()
    delay = 0.1
    eventlet.spawn_after(delay * 2, evt.send, True)
    t1 = eventlet.hubs.get_hub().clock()
    with eventlet.Timeout(delay, False):
        result = evt.wait(timeout=delay)
        td = eventlet.hubs.get_hub().clock() - t1
        assert not result
        assert td >= delay
