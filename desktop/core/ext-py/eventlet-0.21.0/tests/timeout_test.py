import eventlet

import tests


DELAY = 0.01


class TestDirectRaise(tests.LimitedTestCase):
    def test_direct_raise_class(self):
        try:
            raise eventlet.Timeout
        except eventlet.Timeout as t:
            assert not t.pending, repr(t)

    def test_direct_raise_instance(self):
        tm = eventlet.Timeout()
        try:
            raise tm
        except eventlet.Timeout as t:
            assert tm is t, (tm, t)
            assert not t.pending, repr(t)

    def test_repr(self):
        # just verify these don't crash
        tm = eventlet.Timeout(1)
        eventlet.sleep(0)
        repr(tm)
        str(tm)
        tm.cancel()
        tm = eventlet.Timeout(None, RuntimeError)
        repr(tm)
        str(tm)
        tm = eventlet.Timeout(None, False)
        repr(tm)
        str(tm)


class TestWithTimeout(tests.LimitedTestCase):
    def test_with_timeout(self):
        self.assertRaises(eventlet.Timeout, eventlet.with_timeout, DELAY, eventlet.sleep, DELAY * 10)
        X = object()
        r = eventlet.with_timeout(DELAY, eventlet.sleep, DELAY * 10, timeout_value=X)
        assert r is X, (r, X)
        r = eventlet.with_timeout(DELAY * 10, eventlet.sleep, DELAY, timeout_value=X)
        assert r is None, r

    def test_with_outer_timer(self):
        def longer_timeout():
            # this should not catch the outer timeout's exception
            return eventlet.with_timeout(DELAY * 10, eventlet.sleep, DELAY * 20, timeout_value='b')
        self.assertRaises(
            eventlet.Timeout,
            eventlet.with_timeout,
            DELAY, longer_timeout)


def test_is_timeout_attribute():
    tests.check_is_timeout(eventlet.Timeout())
