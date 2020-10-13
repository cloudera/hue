import unittest

import pytest

class TestRetrySleeper(unittest.TestCase):
    def _pass(self):
        pass

    def _fail(self, times=1):
        from kazoo.retry import ForceRetryError

        scope = dict(times=0)

        def inner():
            if scope['times'] >= times:
                pass
            else:
                scope['times'] += 1
                raise ForceRetryError('Failed!')

        return inner

    def _makeOne(self, *args, **kwargs):
        from kazoo.retry import KazooRetry

        return KazooRetry(*args, **kwargs)

    def test_reset(self):
        retry = self._makeOne(delay=0, max_tries=2)
        retry(self._fail())
        assert retry._attempts == 1
        retry.reset()
        assert retry._attempts == 0

    def test_too_many_tries(self):
        from kazoo.retry import RetryFailedError

        retry = self._makeOne(delay=0)
        with pytest.raises(RetryFailedError):
            retry(self._fail(times=999))
        assert retry._attempts == 1

    def test_maximum_delay(self):
        def sleep_func(_time):
            pass

        retry = self._makeOne(delay=10, max_tries=100, sleep_func=sleep_func)
        retry(self._fail(times=10))
        assert retry._cur_delay < 4000
        # gevent's sleep function is picky about the type
        assert type(retry._cur_delay) == float

    def test_copy(self):
        def _sleep(t):
            return None

        retry = self._makeOne(sleep_func=_sleep)
        rcopy = retry.copy()
        assert rcopy.sleep_func is _sleep


class TestKazooRetry(unittest.TestCase):
    def _makeOne(self, **kw):
        from kazoo.retry import KazooRetry

        return KazooRetry(**kw)

    def test_connection_closed(self):
        from kazoo.exceptions import ConnectionClosedError

        retry = self._makeOne()

        def testit():
            raise ConnectionClosedError()

        with pytest.raises(ConnectionClosedError):
            retry(testit)

    def test_session_expired(self):
        from kazoo.exceptions import SessionExpiredError

        retry = self._makeOne(max_tries=1)

        def testit():
            raise SessionExpiredError()

        with pytest.raises(Exception):
            retry(testit)
