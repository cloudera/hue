import sys
import unittest
import warnings
warnings.simplefilter('ignore', DeprecationWarning)
from eventlet import proc
warnings.simplefilter('default', DeprecationWarning)
from eventlet import coros
from eventlet import event as _event
from eventlet import Timeout, sleep, getcurrent, with_timeout
from tests import LimitedTestCase, skipped, silence_warnings

DELAY = 0.01

class ExpectedError(Exception):
    pass

class TestLink_Signal(LimitedTestCase):

    @silence_warnings
    def test_send(self):
        s = proc.Source()
        q1, q2, q3 = coros.queue(), coros.queue(), coros.queue()
        s.link_value(q1)
        self.assertRaises(Timeout, s.wait, 0)
        assert s.wait(0, None) is None
        assert s.wait(0.001, None) is None
        self.assertRaises(Timeout, s.wait, 0.001)
        s.send(1)
        assert not q1.ready()
        assert s.wait()==1
        sleep(0)
        assert q1.ready()
        s.link_exception(q2)
        s.link(q3)
        assert not q2.ready()
        sleep(0)
        assert q3.ready()
        assert s.wait()==1

    @silence_warnings
    def test_send_exception(self):
        s = proc.Source()
        q1, q2, q3 = coros.queue(), coros.queue(), coros.queue()
        s.link_exception(q1)
        s.send_exception(OSError('hello'))
        sleep(0)
        assert q1.ready()
        s.link_value(q2)
        s.link(q3)
        assert not q2.ready()
        sleep(0)
        assert q3.ready()
        self.assertRaises(OSError, q1.wait)
        self.assertRaises(OSError, q3.wait)
        self.assertRaises(OSError, s.wait)


class TestProc(LimitedTestCase):

    def test_proc(self):
        p = proc.spawn(lambda : 100)
        receiver = proc.spawn(sleep, 1)
        p.link(receiver)
        self.assertRaises(proc.LinkedCompleted, receiver.wait)
        receiver2 = proc.spawn(sleep, 1)
        p.link(receiver2)
        self.assertRaises(proc.LinkedCompleted, receiver2.wait)

    def test_event(self):
        p = proc.spawn(lambda : 100)
        event = _event.Event()
        p.link(event)
        self.assertEqual(event.wait(), 100)

        for i in xrange(3):
            event2 = _event.Event()
            p.link(event2)
            self.assertEqual(event2.wait(), 100)

    def test_current(self):
        p = proc.spawn(lambda : 100)
        p.link()
        self.assertRaises(proc.LinkedCompleted, sleep, 0.1)


class TestCase(LimitedTestCase):

    def link(self, p, listener=None):
        getattr(p, self.link_method)(listener)

    def tearDown(self):
        LimitedTestCase.tearDown(self)
        self.p.unlink()

    def set_links(self, p, first_time, kill_exc_type):
        event = _event.Event()
        self.link(p, event)

        proc_flag = []
        def receiver():
            sleep(DELAY)
            proc_flag.append('finished')
        receiver = proc.spawn(receiver)
        self.link(p, receiver)

        queue = coros.queue(1)
        self.link(p, queue)

        try:
            self.link(p)
        except kill_exc_type:
            if first_time:
                raise
        else:
            assert first_time, 'not raising here only first time'

        callback_flag = ['initial']
        self.link(p, lambda *args: callback_flag.remove('initial'))

        for _ in range(10):
            self.link(p, _event.Event())
            self.link(p, coros.queue(1))
        return event, receiver, proc_flag, queue, callback_flag

    def set_links_timeout(self, link):
        # stuff that won't be touched
        event = _event.Event()
        link(event)

        proc_finished_flag = []
        def myproc():
            sleep(10)
            proc_finished_flag.append('finished')
            return 555
        myproc = proc.spawn(myproc)
        link(myproc)

        queue = coros.queue(0)
        link(queue)
        return event, myproc, proc_finished_flag, queue

    def check_timed_out(self, event, myproc, proc_finished_flag, queue):
        X = object()
        assert with_timeout(DELAY, event.wait, timeout_value=X) is X
        assert with_timeout(DELAY, queue.wait, timeout_value=X) is X
        assert with_timeout(DELAY, proc.waitall, [myproc], timeout_value=X) is X
        assert proc_finished_flag == [], proc_finished_flag


class TestReturn_link(TestCase):
    link_method = 'link'

    def test_return(self):
        def return25():
            return 25
        p = self.p = proc.spawn(return25)
        self._test_return(p, True, 25, proc.LinkedCompleted, lambda : sleep(0))
        # repeating the same with dead process
        for _ in xrange(3):
            self._test_return(p, False, 25, proc.LinkedCompleted, lambda : sleep(0))

    def _test_return(self, p, first_time, result, kill_exc_type, action):
        event, receiver, proc_flag, queue, callback_flag = self.set_links(p, first_time, kill_exc_type)

        # stuff that will time out because there's no unhandled exception:
        xxxxx = self.set_links_timeout(p.link_exception)

        try:
            sleep(DELAY*2)
        except kill_exc_type:
             assert first_time, 'raising here only first time'
        else:
            assert not first_time, 'Should not raise LinkedKilled here after first time'

        assert not p, p

        self.assertEqual(event.wait(), result)
        self.assertEqual(queue.wait(), result)
        self.assertRaises(kill_exc_type, receiver.wait)
        self.assertRaises(kill_exc_type, proc.waitall, [receiver])

        sleep(DELAY)
        assert not proc_flag, proc_flag
        assert not callback_flag, callback_flag

        self.check_timed_out(*xxxxx)

class TestReturn_link_value(TestReturn_link):
    sync = False
    link_method = 'link_value'


class TestRaise_link(TestCase):
    link_method = 'link'

    def _test_raise(self, p, first_time, kill_exc_type):
        event, receiver, proc_flag, queue, callback_flag = self.set_links(p, first_time, kill_exc_type)
        xxxxx = self.set_links_timeout(p.link_value)

        try:
            sleep(DELAY)
        except kill_exc_type:
             assert first_time, 'raising here only first time'
        else:
            assert not first_time, 'Should not raise LinkedKilled here after first time'

        assert not p, p

        self.assertRaises(ExpectedError, event.wait)
        self.assertRaises(ExpectedError, queue.wait)
        self.assertRaises(kill_exc_type, receiver.wait)
        self.assertRaises(kill_exc_type, proc.waitall, [receiver])
        sleep(DELAY)
        assert not proc_flag, proc_flag
        assert not callback_flag, callback_flag

        self.check_timed_out(*xxxxx)

    @silence_warnings
    def test_raise(self):
        p = self.p = proc.spawn(lambda : getcurrent().throw(ExpectedError('test_raise')))
        self._test_raise(p, True, proc.LinkedFailed)
        # repeating the same with dead process
        for _ in xrange(3):
            self._test_raise(p, False, proc.LinkedFailed)

    def _test_kill(self, p, first_time, kill_exc_type):
        event, receiver, proc_flag, queue, callback_flag = self.set_links(p, first_time, kill_exc_type)
        xxxxx = self.set_links_timeout(p.link_value)

        p.kill()
        try:
            sleep(DELAY)
        except kill_exc_type:
             assert first_time, 'raising here only first time'
        else:
            assert not first_time, 'Should not raise LinkedKilled here after first time'

        assert not p, p

        self.assertRaises(proc.ProcExit, event.wait)
        self.assertRaises(proc.ProcExit, queue.wait)
        self.assertRaises(kill_exc_type, proc.waitall, [receiver])
        self.assertRaises(kill_exc_type, receiver.wait)

        sleep(DELAY)
        assert not proc_flag, proc_flag
        assert not callback_flag, callback_flag

        self.check_timed_out(*xxxxx)

    @silence_warnings
    def test_kill(self):
        p = self.p = proc.spawn(sleep, DELAY)
        self._test_kill(p, True, proc.LinkedKilled)
        # repeating the same with dead process
        for _ in xrange(3):
            self._test_kill(p, False, proc.LinkedKilled)

class TestRaise_link_exception(TestRaise_link):
    link_method = 'link_exception'


class TestStuff(LimitedTestCase):

    def test_wait_noerrors(self):
        x = proc.spawn(lambda : 1)
        y = proc.spawn(lambda : 2)
        z = proc.spawn(lambda : 3)
        self.assertEqual(proc.waitall([x, y, z]), [1, 2, 3])
        e = _event.Event()
        x.link(e)
        self.assertEqual(e.wait(), 1)
        x.unlink(e)
        e = _event.Event()
        x.link(e)
        self.assertEqual(e.wait(), 1)
        self.assertEqual([proc.waitall([X]) for X in [x, y, z]], [[1], [2], [3]])

    # this test is timing-sensitive
    @skipped
    def test_wait_error(self):
        def x():
            sleep(DELAY)
            return 1
        x = proc.spawn(x)
        z = proc.spawn(lambda : 3)
        y = proc.spawn(lambda : getcurrent().throw(ExpectedError('test_wait_error')))
        y.link(x)
        x.link(y)
        y.link(z)
        z.link(y)
        self.assertRaises(ExpectedError, proc.waitall, [x, y, z])
        self.assertRaises(proc.LinkedFailed, proc.waitall, [x])
        self.assertEqual(proc.waitall([z]), [3])
        self.assertRaises(ExpectedError, proc.waitall, [y])

    def test_wait_all_exception_order(self):
        # if there're several exceptions raised, the earliest one must be raised by wait
        def first():
            sleep(0.1)
            raise ExpectedError('first')
        a = proc.spawn(first)
        b = proc.spawn(lambda : getcurrent().throw(ExpectedError('second')))
        try:
            proc.waitall([a, b])
        except ExpectedError, ex:
            assert 'second' in str(ex), repr(str(ex))
        sleep(0.2)   # sleep to ensure that the other timer is raised

    def test_multiple_listeners_error(self):
        # if there was an error while calling a callback
        # it should not prevent the other listeners from being called
        # also, all of the errors should be logged, check the output
        # manually that they are
        p = proc.spawn(lambda : 5)
        results = []
        def listener1(*args):
            results.append(10)
            raise ExpectedError('listener1')
        def listener2(*args):
            results.append(20)
            raise ExpectedError('listener2')
        def listener3(*args):
            raise ExpectedError('listener3')
        p.link(listener1)
        p.link(listener2)
        p.link(listener3)
        sleep(DELAY*10)
        assert results in [[10, 20], [20, 10]], results

        p = proc.spawn(lambda : getcurrent().throw(ExpectedError('test_multiple_listeners_error')))
        results = []
        p.link(listener1)
        p.link(listener2)
        p.link(listener3)
        sleep(DELAY*10)
        assert results in [[10, 20], [20, 10]], results

    def _test_multiple_listeners_error_unlink(self, p):
        # notification must not happen after unlink even
        # though notification process has been already started
        results = []
        def listener1(*args):
            p.unlink(listener2)
            results.append(5)
            raise ExpectedError('listener1')
        def listener2(*args):
            p.unlink(listener1)
            results.append(5)
            raise ExpectedError('listener2')
        def listener3(*args):
            raise ExpectedError('listener3')
        p.link(listener1)
        p.link(listener2)
        p.link(listener3)
        sleep(DELAY*10)
        assert results == [5], results

    def test_multiple_listeners_error_unlink_Proc(self):
        p = proc.spawn(lambda : 5)
        self._test_multiple_listeners_error_unlink(p)

    def test_multiple_listeners_error_unlink_Source(self):
        p = proc.Source()
        proc.spawn(p.send, 6)
        self._test_multiple_listeners_error_unlink(p)

    def test_killing_unlinked(self):
        e = _event.Event()
        def func():
            try:
                raise ExpectedError('test_killing_unlinked')
            except:
                e.send_exception(*sys.exc_info())
        p = proc.spawn_link(func)
        try:
            try:
                e.wait()
            except ExpectedError:
                pass
        finally:
            p.unlink() # this disables LinkedCompleted that otherwise would be raised by the next line
        sleep(DELAY)


if __name__=='__main__':
    unittest.main()
