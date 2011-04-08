import os
from tests.patcher_test import ProcessBase
from tests import skip_with_pyevent

class Socket(ProcessBase):
    def test_patched_thread(self):
        new_mod = """from eventlet.green import socket
socket.gethostbyname('localhost')
socket.getaddrinfo('localhost', 80)
"""
        os.environ['EVENTLET_TPOOL_DNS'] = 'yes'
        try:
            self.write_to_tempfile("newmod", new_mod)
            output, lines = self.launch_subprocess('newmod.py')
            self.assertEqual(len(lines), 1, lines)
        finally:
            del os.environ['EVENTLET_TPOOL_DNS']

class Tpool(ProcessBase):
    @skip_with_pyevent
    def test_tpool_size(self):
        expected = "40"
        normal = "20"
        new_mod = """from eventlet import tpool
import eventlet
import time
current = [0]
highwater = [0]
def count():
    current[0] += 1
    time.sleep(0.1)
    if current[0] > highwater[0]:
        highwater[0] = current[0]
    current[0] -= 1
expected = %s
normal = %s
p = eventlet.GreenPool()
for i in xrange(expected*2):
    p.spawn(tpool.execute, count)
p.waitall()
assert highwater[0] > 20, "Highwater %%s  <= %%s" %% (highwater[0], normal)
"""
        os.environ['EVENTLET_THREADPOOL_SIZE'] = expected
        try:
            self.write_to_tempfile("newmod", new_mod % (expected, normal))
            output, lines = self.launch_subprocess('newmod.py')
            self.assertEqual(len(lines), 1, lines)
        finally:
            del os.environ['EVENTLET_THREADPOOL_SIZE']

    def test_tpool_negative(self):
        new_mod = """from eventlet import tpool
import eventlet
import time
def do():
    print "should not get here"
try:
    tpool.execute(do)
except AssertionError:
    print "success"
"""
        os.environ['EVENTLET_THREADPOOL_SIZE'] = "-1"
        try:
            self.write_to_tempfile("newmod", new_mod)
            output, lines = self.launch_subprocess('newmod.py')
            self.assertEqual(len(lines), 2, lines)
            self.assertEqual(lines[0], "success", output)
        finally:
            del os.environ['EVENTLET_THREADPOOL_SIZE']

    def test_tpool_zero(self):
        new_mod = """from eventlet import tpool
import eventlet
import time
def do():
    print "ran it"
tpool.execute(do)
"""
        os.environ['EVENTLET_THREADPOOL_SIZE'] = "0"
        try:
            self.write_to_tempfile("newmod", new_mod)
            output, lines = self.launch_subprocess('newmod.py')
            self.assertEqual(len(lines), 4, lines)
            self.assertEqual(lines[-2], 'ran it', lines)
            self.assert_('Warning' in lines[1] or 'Warning' in lines[0], lines)
        finally:
            del os.environ['EVENTLET_THREADPOOL_SIZE']



class Hub(ProcessBase):

    def setUp(self):
        super(Hub, self).setUp()
        self.old_environ = os.environ.get('EVENTLET_HUB')
        os.environ['EVENTLET_HUB'] = 'selects'

    def tearDown(self):
        if self.old_environ:
            os.environ['EVENTLET_HUB'] = self.old_environ
        else:
            del os.environ['EVENTLET_HUB']
        super(Hub, self).tearDown()

    def test_eventlet_hub(self):
        new_mod = """from eventlet import hubs
print hubs.get_hub()
"""
        self.write_to_tempfile("newmod", new_mod)
        output, lines = self.launch_subprocess('newmod.py')
        self.assertEqual(len(lines), 2, "\n".join(lines))
        self.assert_("selects" in lines[0])

