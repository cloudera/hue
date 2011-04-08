import sys

import eventlet
from eventlet import debug
from tests import LimitedTestCase, main, s2b
from unittest import TestCase

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class TestSpew(TestCase):
    def setUp(self):
        self.orig_trace = sys.settrace
        sys.settrace = self._settrace
        self.tracer = None

    def tearDown(self):
        sys.settrace = self.orig_trace
        sys.stdout = sys.__stdout__

    def _settrace(self, cb):
        self.tracer = cb

    def test_spew(self):
        debug.spew()
        self.failUnless(isinstance(self.tracer, debug.Spew))

    def test_unspew(self):
        debug.spew()
        debug.unspew()
        self.failUnlessEqual(self.tracer, None)

    def test_line(self):
        sys.stdout = StringIO()
        s = debug.Spew()
        f = sys._getframe()
        s(f, "line", None)
        lineno = f.f_lineno - 1 # -1 here since we called with frame f in the line above
        output = sys.stdout.getvalue()
        self.failUnless("%s:%i" % (__name__, lineno) in output, "Didn't find line %i in %s" % (lineno, output))
        self.failUnless("f=<frame object at" in output)

    def test_line_nofile(self):
        sys.stdout = StringIO()
        s = debug.Spew()
        g = globals().copy()
        del g['__file__']
        f = eval("sys._getframe()", g)
        lineno = f.f_lineno
        s(f, "line", None)
        output = sys.stdout.getvalue()
        self.failUnless("[unknown]:%i" % lineno in output, "Didn't find [unknown]:%i in %s" % (lineno, output))
        self.failUnless("VM instruction #" in output, output)

    def test_line_global(self):
        global GLOBAL_VAR
        sys.stdout = StringIO()
        GLOBAL_VAR = debug.Spew()
        f = sys._getframe()
        GLOBAL_VAR(f, "line", None)
        lineno = f.f_lineno - 1 # -1 here since we called with frame f in the line above
        output = sys.stdout.getvalue()
        self.failUnless("%s:%i" % (__name__, lineno) in output, "Didn't find line %i in %s" % (lineno, output))
        self.failUnless("f=<frame object at" in output)
        self.failUnless("GLOBAL_VAR" in f.f_globals)
        self.failUnless("GLOBAL_VAR=<eventlet.debug.Spew object at" in output)
        del GLOBAL_VAR

    def test_line_novalue(self):
        sys.stdout = StringIO()
        s = debug.Spew(show_values=False)
        f = sys._getframe()
        s(f, "line", None)
        lineno = f.f_lineno - 1 # -1 here since we called with frame f in the line above
        output = sys.stdout.getvalue()
        self.failUnless("%s:%i" % (__name__, lineno) in output, "Didn't find line %i in %s" % (lineno, output))
        self.failIf("f=<frame object at" in output)

    def test_line_nooutput(self):
        sys.stdout = StringIO()
        s = debug.Spew(trace_names=['foo'])
        f = sys._getframe()
        s(f, "line", None)
        lineno = f.f_lineno - 1 # -1 here since we called with frame f in the line above
        output = sys.stdout.getvalue()
        self.failUnlessEqual(output, "")


class TestDebug(LimitedTestCase):
    def test_everything(self):
        debug.hub_exceptions(True)
        debug.hub_exceptions(False)
        debug.tpool_exceptions(True)
        debug.tpool_exceptions(False)
        debug.hub_listener_stacks(True)
        debug.hub_listener_stacks(False)
        debug.hub_timer_stacks(True)
        debug.hub_timer_stacks(False)
        debug.format_hub_listeners()
        debug.format_hub_timers()

    def test_hub_exceptions(self):
        debug.hub_exceptions(True)
        server = eventlet.listen(('0.0.0.0', 0))
        client = eventlet.connect(('127.0.0.1', server.getsockname()[1]))
        client_2, addr = server.accept()
        
        def hurl(s):
            s.recv(1)
            {}[1]  # keyerror

        fake = StringIO()
        orig = sys.stderr
        sys.stderr = fake
        try:
            gt = eventlet.spawn(hurl, client_2)            
            eventlet.sleep(0)
            client.send(s2b(' '))
            eventlet.sleep(0)
            # allow the "hurl" greenlet to trigger the KeyError
            # not sure why the extra context switch is needed
            eventlet.sleep(0)
        finally:
            sys.stderr = orig
            self.assertRaises(KeyError, gt.wait)
            debug.hub_exceptions(False)
        # look for the KeyError exception in the traceback
        self.assert_('KeyError: 1' in fake.getvalue(), 
            "Traceback not in:\n" + fake.getvalue())
        
if __name__ == "__main__":
    main()
