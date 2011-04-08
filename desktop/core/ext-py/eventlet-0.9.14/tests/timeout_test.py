from tests import LimitedTestCase
from eventlet import timeout
from eventlet import greenthread
DELAY = 0.01

class TestDirectRaise(LimitedTestCase):
    def test_direct_raise_class(self):
        try:
            raise timeout.Timeout
        except timeout.Timeout, t:
            assert not t.pending, repr(t)

    def test_direct_raise_instance(self):
        tm = timeout.Timeout()
        try:
            raise tm
        except timeout.Timeout, t:
            assert tm is t, (tm, t)
            assert not t.pending, repr(t)
            
    def test_repr(self):
        # just verify these don't crash
        tm = timeout.Timeout(1)
        greenthread.sleep(0)
        repr(tm)
        str(tm)
        tm.cancel()
        tm = timeout.Timeout(None, RuntimeError)
        repr(tm)
        str(tm)
        tm = timeout.Timeout(None, False)
        repr(tm)
        str(tm)

class TestWithTimeout(LimitedTestCase):
    def test_with_timeout(self):
        self.assertRaises(timeout.Timeout, timeout.with_timeout, DELAY, greenthread.sleep, DELAY*10)
        X = object()
        r = timeout.with_timeout(DELAY, greenthread.sleep, DELAY*10, timeout_value=X)
        self.assert_(r is X, (r, X))
        r = timeout.with_timeout(DELAY*10, greenthread.sleep, 
                                 DELAY, timeout_value=X)
        self.assert_(r is None, r)


    def test_with_outer_timer(self):
        def longer_timeout():
            # this should not catch the outer timeout's exception
            return timeout.with_timeout(DELAY * 10, 
                                        greenthread.sleep, DELAY * 20,
                                        timeout_value='b')
        self.assertRaises(timeout.Timeout,
            timeout.with_timeout, DELAY, longer_timeout)
        