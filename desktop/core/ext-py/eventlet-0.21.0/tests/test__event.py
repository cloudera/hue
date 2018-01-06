from eventlet import spawn, sleep, with_timeout
from eventlet.event import Event
import eventlet
from tests import LimitedTestCase

DELAY = 0.01


class TestEvent(LimitedTestCase):

    def test_send_exc(self):
        log = []
        e = Event()

        def waiter():
            try:
                result = e.wait()
                log.append(('received', result))
            except Exception as ex:
                log.append(('catched', ex))
        spawn(waiter)
        sleep(0)  # let waiter to block on e.wait()
        obj = Exception()
        e.send(exc=obj)
        sleep(0)
        sleep(0)
        assert log == [('catched', obj)], log

    def test_send(self):
        event1 = Event()
        event2 = Event()

        spawn(event1.send, 'hello event1')
        eventlet.Timeout(0, ValueError('interrupted'))
        try:
            result = event1.wait()
        except ValueError:
            X = object()
            result = with_timeout(DELAY, event2.wait, timeout_value=X)
            assert result is X, 'Nobody sent anything to event2 yet it received %r' % (result, )
