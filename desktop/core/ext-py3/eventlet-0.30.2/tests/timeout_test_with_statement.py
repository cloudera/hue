"""Tests with-statement behavior of Timeout class."""

import gc
import sys
import time
import weakref

from eventlet import sleep
from eventlet.timeout import Timeout
from tests import LimitedTestCase


DELAY = 0.01


class Error(Exception):
    pass


class Test(LimitedTestCase):
    def test_cancellation(self):
        # Nothing happens if with-block finishes before the timeout expires
        t = Timeout(DELAY * 2)
        sleep(0)  # make it pending
        assert t.pending, repr(t)
        with t:
            assert t.pending, repr(t)
            sleep(DELAY)
        # check if timer was actually cancelled
        assert not t.pending, repr(t)
        sleep(DELAY * 2)

    def test_raising_self(self):
        # An exception will be raised if it's not
        try:
            with Timeout(DELAY) as t:
                sleep(DELAY * 2)
        except Timeout as ex:
            assert ex is t, (ex, t)
        else:
            raise AssertionError('must raise Timeout')

    def test_raising_self_true(self):
        # specifying True as the exception raises self as well
        try:
            with Timeout(DELAY, True) as t:
                sleep(DELAY * 2)
        except Timeout as ex:
            assert ex is t, (ex, t)
        else:
            raise AssertionError('must raise Timeout')

    def test_raising_custom_exception(self):
        # You can customize the exception raised:
        try:
            with Timeout(DELAY, IOError("Operation takes way too long")):
                sleep(DELAY * 2)
        except IOError as ex:
            assert str(ex) == "Operation takes way too long", repr(ex)

    def test_raising_exception_class(self):
        # Providing classes instead of values should be possible too:
        try:
            with Timeout(DELAY, ValueError):
                sleep(DELAY * 2)
        except ValueError:
            pass

    def test_raising_exc_tuple(self):
        try:
            1 // 0
        except:
            try:
                with Timeout(DELAY, sys.exc_info()[0]):
                    sleep(DELAY * 2)
                    raise AssertionError('should not get there')
                raise AssertionError('should not get there')
            except ZeroDivisionError:
                pass
        else:
            raise AssertionError('should not get there')

    def test_cancel_timer_inside_block(self):
        # It's possible to cancel the timer inside the block:
        with Timeout(DELAY) as timer:
            timer.cancel()
            sleep(DELAY * 2)

    def test_silent_block(self):
        # To silence the exception before exiting the block, pass
        # False as second parameter.
        XDELAY = 0.1
        start = time.time()
        with Timeout(XDELAY, False):
            sleep(XDELAY * 2)
        delta = (time.time() - start)
        assert delta < XDELAY * 2, delta

    def test_dummy_timer(self):
        # passing None as seconds disables the timer
        with Timeout(None):
            sleep(DELAY)
        sleep(DELAY)

    def test_ref(self):
        err = Error()
        err_ref = weakref.ref(err)
        with Timeout(DELAY * 2, err):
            sleep(DELAY)
        del err
        gc.collect()
        assert not err_ref(), repr(err_ref())

    def test_nested_timeout(self):
        with Timeout(DELAY, False):
            with Timeout(DELAY * 2, False):
                sleep(DELAY * 3)
            raise AssertionError('should not get there')

        with Timeout(DELAY) as t1:
            with Timeout(DELAY * 2) as t2:
                try:
                    sleep(DELAY * 3)
                except Timeout as ex:
                    assert ex is t1, (ex, t1)
                assert not t1.pending, t1
                assert t2.pending, t2
            assert not t2.pending, t2

        with Timeout(DELAY * 2) as t1:
            with Timeout(DELAY) as t2:
                try:
                    sleep(DELAY * 3)
                except Timeout as ex:
                    assert ex is t2, (ex, t2)
                assert t1.pending, t1
                assert not t2.pending, t2
        assert not t1.pending, t1
