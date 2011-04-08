from tests import LimitedTestCase, main, skip_with_pyevent, skip_if_no_itimer, skip_with_zmq
import time
import eventlet
from eventlet import hubs
from eventlet.green import socket

DELAY = 0.001
def noop():
    pass

class TestTimerCleanup(LimitedTestCase):
    TEST_TIMEOUT = 2
    @skip_with_pyevent
    def test_cancel_immediate(self):
        hub = hubs.get_hub()
        stimers = hub.get_timers_count()
        scanceled = hub.timers_canceled
        for i in xrange(2000):
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
        for i in xrange(2000):
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
        for i in xrange(1000):
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
        

class TestScheduleCall(LimitedTestCase):
    def test_local(self):
        lst = [1]
        eventlet.spawn(hubs.get_hub().schedule_call_local, DELAY, lst.pop)
        eventlet.sleep(0)
        eventlet.sleep(DELAY*2)
        assert lst == [1], lst

    def test_global(self):
        lst = [1]
        eventlet.spawn(hubs.get_hub().schedule_call_global, DELAY, lst.pop)
        eventlet.sleep(0)
        eventlet.sleep(DELAY*2)
        assert lst == [], lst
        
    def test_ordering(self):
        lst = []
        hubs.get_hub().schedule_call_global(DELAY*2, lst.append, 3)
        hubs.get_hub().schedule_call_global(DELAY, lst.append, 1)
        hubs.get_hub().schedule_call_global(DELAY, lst.append, 2)
        while len(lst) < 3:
            eventlet.sleep(DELAY)
        self.assertEquals(lst, [1,2,3])

        
class TestDebug(LimitedTestCase):
    def test_debug_listeners(self):
        hubs.get_hub().set_debug_listeners(True)
        hubs.get_hub().set_debug_listeners(False)

    def test_timer_exceptions(self):
        hubs.get_hub().set_timer_exceptions(True)
        hubs.get_hub().set_timer_exceptions(False)
        

class TestExceptionInMainloop(LimitedTestCase):
    def test_sleep(self):
        # even if there was an error in the mainloop, the hub should continue to work
        start = time.time()
        eventlet.sleep(DELAY)
        delay = time.time() - start

        assert delay >= DELAY*0.9, 'sleep returned after %s seconds (was scheduled for %s)' % (delay, DELAY)

        def fail():
            1//0

        hubs.get_hub().schedule_call_global(0, fail)

        start = time.time()
        eventlet.sleep(DELAY)
        delay = time.time() - start

        assert delay >= DELAY*0.9, 'sleep returned after %s seconds (was scheduled for %s)' % (delay, DELAY)


class TestHubSelection(LimitedTestCase):
    def test_explicit_hub(self):
        if getattr(hubs.get_hub(), 'uses_twisted_reactor', None):
            # doesn't work with twisted
            return
        oldhub = hubs.get_hub()
        try:
            hubs.use_hub(Foo)
            self.assert_(isinstance(hubs.get_hub(), Foo), hubs.get_hub())
        finally:
            hubs._threadlocal.hub = oldhub


class TestHubBlockingDetector(LimitedTestCase):
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
        

class TestSuspend(LimitedTestCase):
    TEST_TIMEOUT=3
    def test_suspend_doesnt_crash(self):
        import errno
        import os
        import shutil
        import signal
        import subprocess
        import sys
        import tempfile
        self.tempdir = tempfile.mkdtemp('test_suspend')
        filename = os.path.join(self.tempdir,  'test_suspend.py')
        fd = open(filename, "w")
        fd.write("""import eventlet
eventlet.Timeout(0.5)
try:
   eventlet.listen(("127.0.0.1", 0)).accept()
except eventlet.Timeout:
   print "exited correctly"
""")
        fd.close()
        python_path = os.pathsep.join(sys.path + [self.tempdir])
        new_env = os.environ.copy()
        new_env['PYTHONPATH'] = python_path
        p = subprocess.Popen([sys.executable, 
                              os.path.join(self.tempdir, filename)],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=new_env)
        eventlet.sleep(0.4)  # wait for process to hit accept
        os.kill(p.pid, signal.SIGSTOP) # suspend and resume to generate EINTR
        os.kill(p.pid, signal.SIGCONT)
        output, _ = p.communicate()
        lines = [l for l in output.split("\n") if l]
        self.assert_("exited correctly" in lines[-1])
        shutil.rmtree(self.tempdir)


class TestBadFilenos(LimitedTestCase):
    @skip_with_pyevent
    @skip_with_zmq
    def test_repeated_selects(self):
        from eventlet.green import select
        self.assertRaises(ValueError, select.select, [-1], [], [])
        self.assertRaises(ValueError, select.select, [-1], [], [])


class Foo(object):
    pass

if __name__=='__main__':
    main()

