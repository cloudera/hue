import sys
from unittest import TestCase

from eventlet import debug
from eventlet.support import capture_stderr, six
from tests import LimitedTestCase, main
import eventlet


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
        assert isinstance(self.tracer, debug.Spew)

    def test_unspew(self):
        debug.spew()
        debug.unspew()
        assert self.tracer is None

    def test_line(self):
        sys.stdout = six.StringIO()
        s = debug.Spew()
        f = sys._getframe()
        s(f, "line", None)
        lineno = f.f_lineno - 1  # -1 here since we called with frame f in the line above
        output = sys.stdout.getvalue()
        assert "%s:%i" % (__name__, lineno) in output, "Didn't find line %i in %s" % (lineno, output)
        assert "f=<frame object at" in output

    def test_line_nofile(self):
        sys.stdout = six.StringIO()
        s = debug.Spew()
        g = globals().copy()
        del g['__file__']
        f = eval("sys._getframe()", g)
        lineno = f.f_lineno
        s(f, "line", None)
        output = sys.stdout.getvalue()
        assert "[unknown]:%i" % lineno in output, "Didn't find [unknown]:%i in %s" % (lineno, output)
        assert "VM instruction #" in output, output

    def test_line_global(self):
        global GLOBAL_VAR
        sys.stdout = six.StringIO()
        GLOBAL_VAR = debug.Spew()
        f = sys._getframe()
        GLOBAL_VAR(f, "line", None)
        lineno = f.f_lineno - 1  # -1 here since we called with frame f in the line above
        output = sys.stdout.getvalue()
        assert "%s:%i" % (__name__, lineno) in output, "Didn't find line %i in %s" % (lineno, output)
        assert "f=<frame object at" in output
        assert "GLOBAL_VAR" in f.f_globals
        assert "GLOBAL_VAR=<eventlet.debug.Spew object at" in output
        del GLOBAL_VAR

    def test_line_novalue(self):
        sys.stdout = six.StringIO()
        s = debug.Spew(show_values=False)
        f = sys._getframe()
        s(f, "line", None)
        lineno = f.f_lineno - 1  # -1 here since we called with frame f in the line above
        output = sys.stdout.getvalue()
        assert "%s:%i" % (__name__, lineno) in output, "Didn't find line %i in %s" % (lineno, output)
        assert "f=<frame object at" not in output

    def test_line_nooutput(self):
        sys.stdout = six.StringIO()
        s = debug.Spew(trace_names=['foo'])
        f = sys._getframe()
        s(f, "line", None)
        output = sys.stdout.getvalue()
        assert output == ""


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

        with capture_stderr() as fake:
            gt = eventlet.spawn(hurl, client_2)
            eventlet.sleep(0)
            client.send(b' ')
            eventlet.sleep(0)
            # allow the "hurl" greenlet to trigger the KeyError
            # not sure why the extra context switch is needed
            eventlet.sleep(0)
        self.assertRaises(KeyError, gt.wait)
        debug.hub_exceptions(False)
        # look for the KeyError exception in the traceback
        assert 'KeyError: 1' in fake.getvalue(), "Traceback not in:\n" + fake.getvalue()

if __name__ == "__main__":
    main()
