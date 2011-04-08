from unittest import main
from tests import LimitedTestCase, silence_warnings
import eventlet
from eventlet import coros
from eventlet import event
from eventlet import greenthread

class IncrActor(coros.Actor):
    def received(self, evt):
        self.value = getattr(self, 'value', 0) + 1
        if evt: evt.send()


class TestActor(LimitedTestCase):
    mode = 'static'

    @silence_warnings
    def setUp(self):
        super(TestActor, self).setUp()
        self.actor = IncrActor()

    def tearDown(self):
        super(TestActor, self).tearDown()
        greenthread.kill(self.actor._killer)

    def test_cast(self):
        evt = event.Event()
        self.actor.cast(evt)
        evt.wait()
        evt.reset()
        self.assertEqual(self.actor.value, 1)
        self.actor.cast(evt)
        evt.wait()
        self.assertEqual(self.actor.value, 2)

    def test_cast_multi_1(self):
        # make sure that both messages make it in there
        evt = event.Event()
        evt1 = event.Event()
        self.actor.cast(evt)
        self.actor.cast(evt1)
        evt.wait()
        evt1.wait()
        self.assertEqual(self.actor.value, 2)

    def test_cast_multi_2(self):
        # the actor goes through a slightly different code path if it
        # is forced to enter its event loop prior to any cast()s
        eventlet.sleep(0)
        self.test_cast_multi_1()

    def test_sleeping_during_received(self):
        # ensure that even if the received method cooperatively
        # yields, eventually all messages are delivered
        msgs = []
        waiters = []
        def received( (message, evt) ):
            eventlet.sleep(0)
            msgs.append(message)
            evt.send()
        self.actor.received = received

        waiters.append(event.Event())
        self.actor.cast( (1, waiters[-1]))
        eventlet.sleep(0)
        waiters.append(event.Event())
        self.actor.cast( (2, waiters[-1]) )
        waiters.append(event.Event())
        self.actor.cast( (3, waiters[-1]) )
        eventlet.sleep(0)
        waiters.append(event.Event())
        self.actor.cast( (4, waiters[-1]) )
        waiters.append(event.Event())
        self.actor.cast( (5, waiters[-1]) )
        for evt in waiters:
            evt.wait()
        self.assertEqual(msgs, [1,2,3,4,5])

    def test_raising_received(self):
        msgs = []
        def received( (message, evt) ):
            evt.send()
            if message == 'fail':
                raise RuntimeError()
            else:
                msgs.append(message)

        self.actor.received = received

        evt = event.Event()
        self.actor.cast( ('fail', evt) )
        evt.wait()
        evt.reset()
        self.actor.cast( ('should_appear', evt) )
        evt.wait()
        self.assertEqual(['should_appear'], msgs)

    @silence_warnings
    def test_multiple(self):
        self.actor = IncrActor(concurrency=2)
        total = [0]
        def received( (func, ev, value) ):
            func()
            total[0] += value
            ev.send()
        self.actor.received = received

        def onemoment():
            eventlet.sleep(0.1)

        evt = event.Event()
        evt1 = event.Event()

        self.actor.cast( (onemoment, evt, 1) )
        self.actor.cast( (lambda: None, evt1, 2) )

        evt1.wait()
        self.assertEqual(total[0], 2)
        eventlet.sleep(0)
        self.assertEqual(self.actor._pool.free(), 1)
        evt.wait()
        self.assertEqual(total[0], 3)
        eventlet.sleep(0)
        self.assertEqual(self.actor._pool.free(), 2)


if __name__ == '__main__':
    main()
