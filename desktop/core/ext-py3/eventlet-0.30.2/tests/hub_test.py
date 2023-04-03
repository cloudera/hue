from __future__ import with_statement
import errno
import fcntl
import os
import sys
import time

import tests
from tests import skip_with_pyevent, skip_if_no_itimer, skip_unless
import eventlet
from eventlet import debug, hubs
from eventlet.support import greenlets
import six


DELAY = 0.001


def noop():
    pass


class TestTimerCleanup(tests.LimitedTestCase):
    TEST_TIMEOUT = 2

    @skip_with_pyevent
    def test_cancel_immediate(self):
        hub = hubs.get_hub()
        stimers = hub.get_timers_count()
        scanceled = hub.timers_canceled
        for i in six.moves.range(2000):
            t = hubs.get_hub().schedule_call_global(60, noop)
            t.cancel()
            self.assert_less_than_equal(hub.timers_canceled,
                                        hub.get_timers_count() + 1)
        # there should be fewer than 1000 new timers and canceled
        self.assert_less_than_equal(hub.get_timers_count(), 1000 + stimers)
        self.assert_less_than_equal(hub.timers_canceled, 1000)

    @skip_with_pyevent
    def test_cancel_accumulated(self):
        hub = hubs.get_hub()
        stimers = hub.get_timers_count()
        scanceled = hub.timers_canceled
        for i in six.moves.range(2000):
            t = hubs.get_hub().schedule_call_global(60, noop)
            eventlet.sleep()
            self.assert_less_than_equal(hub.timers_canceled,
                                        hub.get_timers_count() + 1)
            t.cancel()
            self.assert_less_than_equal(hub.timers_canceled,
                                        hub.get_timers_count() + 1, hub.timers)
        # there should be fewer than 1000 new timers and canceled
        self.assert_less_than_equal(hub.get_timers_count(), 1000 + stimers)
        self.assert_less_than_equal(hub.timers_canceled, 1000)

    @skip_with_pyevent
    def test_cancel_proportion(self):
        # if fewer than half the pending timers are canceled, it should
        # not clean them out
        hub = hubs.get_hub()
        uncanceled_timers = []
        stimers = hub.get_timers_count()
        scanceled = hub.timers_canceled
        for i in six.moves.range(1000):
            # 2/3rds of new timers are uncanceled
            t = hubs.get_hub().schedule_call_global(60, noop)
            t2 = hubs.get_hub().schedule_call_global(60, noop)
            t3 = hubs.get_hub().schedule_call_global(60, noop)
            eventlet.sleep()
            self.assert_less_than_equal(hub.timers_canceled,
                                        hub.get_timers_count() + 1)
            t.cancel()
            self.assert_less_than_equal(hub.timers_canceled,
                                        hub.get_timers_count() + 1)
            uncanceled_timers.append(t2)
            uncanceled_timers.append(t3)
        # 3000 new timers, plus a few extras
        self.assert_less_than_equal(stimers + 3000,
                                    stimers + hub.get_timers_count())
        self.assertEqual(hub.timers_canceled, 1000)
        for t in uncanceled_timers:
            t.cancel()
            self.assert_less_than_equal(hub.timers_canceled,
                                        hub.get_timers_count())
        eventlet.sleep()


class TestMultipleListenersCleanup(tests.LimitedTestCase):
    def setUp(self):
        super(TestMultipleListenersCleanup, self).setUp()
        debug.hub_prevent_multiple_readers(False)
        debug.hub_exceptions(False)

    def tearDown(self):
        super(TestMultipleListenersCleanup, self).tearDown()
        debug.hub_prevent_multiple_readers(True)
        debug.hub_exceptions(True)

    def test_cleanup(self):
        r, w = os.pipe()
        self.addCleanup(os.close, r)
        self.addCleanup(os.close, w)

        fcntl.fcntl(r, fcntl.F_SETFL,
                    fcntl.fcntl(r, fcntl.F_GETFL) | os.O_NONBLOCK)

        def readfd(fd):
            while True:
                try:
                    return os.read(fd, 1)
                except OSError as e:
                    if e.errno != errno.EAGAIN:
                        raise
                    hubs.trampoline(fd, read=True)

        first_listener = eventlet.spawn(readfd, r)
        eventlet.sleep()

        second_listener = eventlet.spawn(readfd, r)
        eventlet.sleep()

        hubs.get_hub().schedule_call_global(0, second_listener.throw,
                                            eventlet.Timeout(None))
        eventlet.sleep()

        os.write(w, b'.')
        self.assertEqual(first_listener.wait(), b'.')


class TestScheduleCall(tests.LimitedTestCase):

    def test_local(self):
        lst = [1]
        eventlet.spawn(hubs.get_hub().schedule_call_local, DELAY, lst.pop)
        eventlet.sleep(0)
        eventlet.sleep(DELAY * 2)
        assert lst == [1], lst

    def test_global(self):
        lst = [1]
        eventlet.spawn(hubs.get_hub().schedule_call_global, DELAY, lst.pop)
        eventlet.sleep(0)
        eventlet.sleep(DELAY * 2)
        assert lst == [], lst

    def test_ordering(self):
        lst = []
        hubs.get_hub().schedule_call_global(DELAY * 2, lst.append, 3)
        hubs.get_hub().schedule_call_global(DELAY, lst.append, 1)
        hubs.get_hub().schedule_call_global(DELAY, lst.append, 2)
        while len(lst) < 3:
            eventlet.sleep(DELAY)
        self.assertEqual(lst, [1, 2, 3])


class TestDebug(tests.LimitedTestCase):

    def test_debug_listeners(self):
        hubs.get_hub().set_debug_listeners(True)
        hubs.get_hub().set_debug_listeners(False)

    def test_timer_exceptions(self):
        hubs.get_hub().set_timer_exceptions(True)
        hubs.get_hub().set_timer_exceptions(False)


class TestExceptionInMainloop(tests.LimitedTestCase):

    def test_sleep(self):
        # even if there was an error in the mainloop, the hub should continue
        # to work
        start = time.time()
        eventlet.sleep(DELAY)
        delay = time.time() - start

        assert delay >= DELAY * \
            0.9, 'sleep returned after %s seconds (was scheduled for %s)' % (
                delay, DELAY)

        def fail():
            1 // 0

        hubs.get_hub().schedule_call_global(0, fail)

        start = time.time()
        eventlet.sleep(DELAY)
        delay = time.time() - start

        assert delay >= DELAY * \
            0.9, 'sleep returned after %s seconds (was scheduled for %s)' % (
                delay, DELAY)


class TestExceptionInGreenthread(tests.LimitedTestCase):

    @skip_unless(greenlets.preserves_excinfo)
    def test_exceptionpreservation(self):
        # events for controlling execution order
        gt1event = eventlet.Event()
        gt2event = eventlet.Event()

        def test_gt1():
            try:
                raise KeyError()
            except KeyError:
                gt1event.send('exception')
                gt2event.wait()
                assert sys.exc_info()[0] is KeyError
                gt1event.send('test passed')

        def test_gt2():
            gt1event.wait()
            gt1event.reset()
            assert sys.exc_info()[0] is None
            try:
                raise ValueError()
            except ValueError:
                gt2event.send('exception')
                gt1event.wait()
                assert sys.exc_info()[0] is ValueError

        g1 = eventlet.spawn(test_gt1)
        g2 = eventlet.spawn(test_gt2)
        try:
            g1.wait()
            g2.wait()
        finally:
            g1.kill()
            g2.kill()

    def test_exceptionleaks(self):
        # tests expected behaviour with all versions of greenlet
        def test_gt(sem):
            try:
                raise KeyError()
            except KeyError:
                sem.release()
                hubs.get_hub().switch()

        # semaphores for controlling execution order
        sem = eventlet.Semaphore()
        sem.acquire()
        g = eventlet.spawn(test_gt, sem)
        try:
            sem.acquire()
            assert sys.exc_info()[0] is None
        finally:
            g.kill()


class TestHubBlockingDetector(tests.LimitedTestCase):
    TEST_TIMEOUT = 10

    @skip_with_pyevent
    def test_block_detect(self):
        def look_im_blocking():
            import time
            time.sleep(2)
        from eventlet import debug
        debug.hub_blocking_detection(True)
        gt = eventlet.spawn(look_im_blocking)
        self.assertRaises(RuntimeError, gt.wait)
        debug.hub_blocking_detection(False)

    @skip_with_pyevent
    @skip_if_no_itimer
    def test_block_detect_with_itimer(self):
        def look_im_blocking():
            import time
            time.sleep(0.5)

        from eventlet import debug
        debug.hub_blocking_detection(True, resolution=0.1)
        gt = eventlet.spawn(look_im_blocking)
        self.assertRaises(RuntimeError, gt.wait)
        debug.hub_blocking_detection(False)


class TestSuspend(tests.LimitedTestCase):
    TEST_TIMEOUT = 4
    longMessage = True
    maxDiff = None

    def test_suspend_doesnt_crash(self):
        import os
        import shutil
        import signal
        import subprocess
        import sys
        import tempfile
        self.tempdir = tempfile.mkdtemp('test_suspend')
        filename = os.path.join(self.tempdir, 'test_suspend.py')
        fd = open(filename, "w")
        fd.write("""import eventlet
eventlet.Timeout(0.5)
try:
   eventlet.listen(("127.0.0.1", 0)).accept()
except eventlet.Timeout:
   print("exited correctly")
""")
        fd.close()
        python_path = os.pathsep.join(sys.path + [self.tempdir])
        new_env = os.environ.copy()
        new_env['PYTHONPATH'] = python_path
        p = subprocess.Popen([sys.executable,
                              os.path.join(self.tempdir, filename)],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=new_env)
        eventlet.sleep(0.4)  # wait for process to hit accept
        os.kill(p.pid, signal.SIGSTOP)  # suspend and resume to generate EINTR
        os.kill(p.pid, signal.SIGCONT)
        output, _ = p.communicate()
        lines = output.decode('utf-8', 'replace').splitlines()
        assert "exited correctly" in lines[-1], output
        shutil.rmtree(self.tempdir)


def test_repeated_select_bad_fd():
    from eventlet.green import select

    def once():
        try:
            select.select([-1], [], [])
            assert False, 'Expected ValueError'
        except ValueError:
            pass

    once()
    once()


@skip_with_pyevent
def test_fork():
    tests.run_isolated('hub_fork.py')


def test_fork_simple():
    tests.run_isolated('hub_fork_simple.py')


class TestDeadRunLoop(tests.LimitedTestCase):
    TEST_TIMEOUT = 2

    class CustomException(Exception):
        pass

    def test_kill(self):
        """ Checks that killing a process after the hub runloop dies does
        not immediately return to hub greenlet's parent and schedule a
        redundant timer. """
        hub = hubs.get_hub()

        def dummyproc():
            hub.switch()

        g = eventlet.spawn(dummyproc)
        eventlet.sleep(0)  # let dummyproc run
        assert hub.greenlet.parent == eventlet.greenthread.getcurrent()
        self.assertRaises(KeyboardInterrupt, hub.greenlet.throw,
                          KeyboardInterrupt())

        # kill dummyproc, this schedules a timer to return execution to
        # this greenlet before throwing an exception in dummyproc.
        # it is from this timer that execution should be returned to this
        # greenlet, and not by propogating of the terminating greenlet.
        g.kill()
        with eventlet.Timeout(0.5, self.CustomException()):
            # we now switch to the hub, there should be no existing timers
            # that switch back to this greenlet and so this hub.switch()
            # call should block indefinitely.
            self.assertRaises(self.CustomException, hub.switch)

    def test_parent(self):
        """ Checks that a terminating greenthread whose parent
        was a previous, now-defunct hub greenlet returns execution to
        the hub runloop and not the hub greenlet's parent. """
        hub = hubs.get_hub()

        def dummyproc():
            pass

        g = eventlet.spawn(dummyproc)
        assert hub.greenlet.parent == eventlet.greenthread.getcurrent()
        self.assertRaises(KeyboardInterrupt, hub.greenlet.throw,
                          KeyboardInterrupt())

        assert not g.dead  # check dummyproc hasn't completed
        with eventlet.Timeout(0.5, self.CustomException()):
            # we now switch to the hub which will allow
            # completion of dummyproc.
            # this should return execution back to the runloop and not
            # this greenlet so that hub.switch() would block indefinitely.
            self.assertRaises(self.CustomException, hub.switch)
        assert g.dead  # sanity check that dummyproc has completed


def test_use_hub_class():
    tests.run_isolated('hub_use_hub_class.py')


def test_kqueue_unsupported():
    # https://github.com/eventlet/eventlet/issues/38
    # get_hub on windows broken by kqueue
    tests.run_isolated('hub_kqueue_unsupported.py')
