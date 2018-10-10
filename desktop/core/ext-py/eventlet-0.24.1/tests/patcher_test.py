import os
import shutil
import sys
import tempfile

import six
import tests


base_module_contents = """
import socket
import urllib
print("base {0} {1}".format(socket, urllib))
"""

patching_module_contents = """
from eventlet.green import socket
from eventlet.green import urllib
from eventlet import patcher
print('patcher {0} {1}'.format(socket, urllib))
patcher.inject('base', globals(), ('socket', socket), ('urllib', urllib))
del patcher
"""

import_module_contents = """
import patching
import socket
print("importing {0} {1} {2} {3}".format(patching, socket, patching.socket, patching.urllib))
"""


class ProcessBase(tests.LimitedTestCase):
    TEST_TIMEOUT = 3  # starting processes is time-consuming

    def setUp(self):
        super(ProcessBase, self).setUp()
        self._saved_syspath = sys.path
        self.tempdir = tempfile.mkdtemp('_patcher_test')

    def tearDown(self):
        super(ProcessBase, self).tearDown()
        sys.path = self._saved_syspath
        shutil.rmtree(self.tempdir)

    def write_to_tempfile(self, name, contents):
        filename = os.path.join(self.tempdir, name)
        if not filename.endswith('.py'):
            filename = filename + '.py'
        with open(filename, "w") as fd:
            fd.write(contents)

    def launch_subprocess(self, filename):
        path = os.path.join(self.tempdir, filename)
        output = tests.run_python(path)
        if six.PY3:
            output = output.decode('utf-8')
            separator = '\n'
        else:
            separator = b'\n'
        lines = output.split(separator)
        return output, lines

    def run_script(self, contents, modname=None):
        if modname is None:
            modname = "testmod"
        self.write_to_tempfile(modname, contents)
        return self.launch_subprocess(modname)


class ImportPatched(ProcessBase):
    def test_patch_a_module(self):
        self.write_to_tempfile("base", base_module_contents)
        self.write_to_tempfile("patching", patching_module_contents)
        self.write_to_tempfile("importing", import_module_contents)
        output, lines = self.launch_subprocess('importing.py')
        assert lines[0].startswith('patcher'), repr(output)
        assert lines[1].startswith('base'), repr(output)
        assert lines[2].startswith('importing'), repr(output)
        assert 'eventlet.green.socket' in lines[1], repr(output)
        assert 'eventlet.green.urllib' in lines[1], repr(output)
        assert 'eventlet.green.socket' in lines[2], repr(output)
        assert 'eventlet.green.urllib' in lines[2], repr(output)
        assert 'eventlet.green.httplib' not in lines[2], repr(output)


def test_import_patched_defaults():
    tests.run_isolated('patcher_import_patched_defaults.py')


class MonkeyPatch(ProcessBase):
    def test_patched_modules(self):
        new_mod = """
from eventlet import patcher
patcher.monkey_patch()
import socket
try:
    import urllib.request as urllib
except ImportError:
    import urllib
print("newmod {0} {1}".format(socket.socket, urllib.socket.socket))
"""
        self.write_to_tempfile("newmod", new_mod)
        output, lines = self.launch_subprocess('newmod.py')
        assert lines[0].startswith('newmod'), repr(output)
        self.assertEqual(lines[0].count('GreenSocket'), 2, repr(output))

    def test_early_patching(self):
        new_mod = """
from eventlet import patcher
patcher.monkey_patch()
import eventlet
eventlet.sleep(0.01)
print("newmod")
"""
        self.write_to_tempfile("newmod", new_mod)
        output, lines = self.launch_subprocess('newmod.py')
        self.assertEqual(len(lines), 2, repr(output))
        assert lines[0].startswith('newmod'), repr(output)

    def test_late_patching(self):
        new_mod = """
import eventlet
eventlet.sleep(0.01)
from eventlet import patcher
patcher.monkey_patch()
eventlet.sleep(0.01)
print("newmod")
"""
        self.write_to_tempfile("newmod", new_mod)
        output, lines = self.launch_subprocess('newmod.py')
        self.assertEqual(len(lines), 2, repr(output))
        assert lines[0].startswith('newmod'), repr(output)

    def test_typeerror(self):
        new_mod = """
from eventlet import patcher
patcher.monkey_patch(finagle=True)
"""
        self.write_to_tempfile("newmod", new_mod)
        output, lines = self.launch_subprocess('newmod.py')
        assert lines[-2].startswith('TypeError'), repr(output)
        assert 'finagle' in lines[-2], repr(output)

    def assert_boolean_logic(self, call, expected, not_expected=''):
        expected_list = ", ".join(['"%s"' % x for x in expected.split(',') if len(x)])
        not_expected_list = ", ".join(['"%s"' % x for x in not_expected.split(',') if len(x)])
        new_mod = """
from eventlet import patcher
%s
for mod in [%s]:
    assert patcher.is_monkey_patched(mod), mod
for mod in [%s]:
    assert not patcher.is_monkey_patched(mod), mod
print("already_patched {0}".format(",".join(sorted(patcher.already_patched.keys()))))
""" % (call, expected_list, not_expected_list)
        self.write_to_tempfile("newmod", new_mod)
        output, lines = self.launch_subprocess('newmod.py')
        ap = 'already_patched'
        assert lines[0].startswith(ap), repr(output)
        patched_modules = lines[0][len(ap):].strip()
        # psycopg might or might not be patched based on installed modules
        patched_modules = patched_modules.replace("psycopg,", "")
        # ditto for MySQLdb
        patched_modules = patched_modules.replace("MySQLdb,", "")
        self.assertEqual(
            patched_modules, expected,
            "Logic:%s\nExpected: %s != %s" % (call, expected, patched_modules))

    def test_boolean(self):
        self.assert_boolean_logic("patcher.monkey_patch()",
                                  'os,select,socket,subprocess,thread,time')

    def test_boolean_all(self):
        self.assert_boolean_logic("patcher.monkey_patch(all=True)",
                                  'os,select,socket,subprocess,thread,time')

    def test_boolean_all_single(self):
        self.assert_boolean_logic("patcher.monkey_patch(all=True, socket=True)",
                                  'os,select,socket,subprocess,thread,time')

    def test_boolean_all_negative(self):
        self.assert_boolean_logic(
            "patcher.monkey_patch(all=False, socket=False, select=True)",
            'select')

    def test_boolean_single(self):
        self.assert_boolean_logic("patcher.monkey_patch(socket=True)",
                                  'socket')

    def test_boolean_double(self):
        self.assert_boolean_logic("patcher.monkey_patch(socket=True, select=True)",
                                  'select,socket')

    def test_boolean_negative(self):
        self.assert_boolean_logic("patcher.monkey_patch(socket=False)",
                                  'os,select,subprocess,thread,time')

    def test_boolean_negative2(self):
        self.assert_boolean_logic("patcher.monkey_patch(socket=False, time=False)",
                                  'os,select,subprocess,thread')

    def test_conflicting_specifications(self):
        self.assert_boolean_logic("patcher.monkey_patch(socket=False, select=True)",
                                  'select')


test_monkey_patch_threading = """
def test_monkey_patch_threading():
    tickcount = [0]

    def tick():
        import six
        for i in six.moves.range(1000):
            tickcount[0] += 1
            eventlet.sleep()

    def do_sleep():
        tpool.execute(time.sleep, 0.5)

    eventlet.spawn(tick)
    w1 = eventlet.spawn(do_sleep)
    w1.wait()
    print(tickcount[0])
    assert tickcount[0] > 900
    tpool.killall()
"""


class Tpool(ProcessBase):
    TEST_TIMEOUT = 3

    @tests.skip_with_pyevent
    def test_simple(self):
        new_mod = """
import eventlet
from eventlet import patcher
patcher.monkey_patch()
from eventlet import tpool
print("newmod {0}".format(tpool.execute(len, "hi")))
print("newmod {0}".format(tpool.execute(len, "hi2")))
tpool.killall()
"""
        self.write_to_tempfile("newmod", new_mod)
        output, lines = self.launch_subprocess('newmod.py')
        self.assertEqual(len(lines), 3, output)
        assert lines[0].startswith('newmod'), repr(output)
        assert '2' in lines[0], repr(output)
        assert '3' in lines[1], repr(output)

    @tests.skip_with_pyevent
    def test_unpatched_thread(self):
        new_mod = """import eventlet
eventlet.monkey_patch(time=False, thread=False)
from eventlet import tpool
import time
"""
        new_mod += test_monkey_patch_threading
        new_mod += "\ntest_monkey_patch_threading()\n"
        self.write_to_tempfile("newmod", new_mod)
        output, lines = self.launch_subprocess('newmod.py')
        self.assertEqual(len(lines), 2, lines)

    @tests.skip_with_pyevent
    def test_patched_thread(self):
        new_mod = """import eventlet
eventlet.monkey_patch(time=False, thread=True)
from eventlet import tpool
import time
"""
        new_mod += test_monkey_patch_threading
        new_mod += "\ntest_monkey_patch_threading()\n"
        self.write_to_tempfile("newmod", new_mod)
        output, lines = self.launch_subprocess('newmod.py')
        self.assertEqual(len(lines), 2, "\n".join(lines))


def test_subprocess_after_monkey_patch():
    code = '''\
import sys
import eventlet
eventlet.monkey_patch()
from eventlet.green import subprocess
subprocess.Popen([sys.executable, '-c', ''], stdin=subprocess.PIPE).wait()
print('pass')
'''
    output = tests.run_python(
        path=None,
        args=['-c', code],
    )
    assert output.rstrip() == b'pass'


class Threading(ProcessBase):
    def test_orig_thread(self):
        new_mod = """import eventlet
eventlet.monkey_patch()
from eventlet import patcher
import threading
_threading = patcher.original('threading')
def test():
    print(repr(threading.currentThread()))
t = _threading.Thread(target=test)
t.start()
t.join()
print(len(threading._active))
print(len(_threading._active))
"""
        self.write_to_tempfile("newmod", new_mod)
        output, lines = self.launch_subprocess('newmod.py')
        self.assertEqual(len(lines), 4, "\n".join(lines))
        assert lines[0].startswith('<Thread'), lines[0]
        assert lines[1] == '1', lines
        assert lines[2] == '1', lines

    def test_tpool(self):
        new_mod = """import eventlet
eventlet.monkey_patch()
from eventlet import tpool
import threading
def test():
    print(repr(threading.currentThread()))
tpool.execute(test)
print(len(threading._active))
"""
        self.write_to_tempfile("newmod", new_mod)
        output, lines = self.launch_subprocess('newmod.py')
        self.assertEqual(len(lines), 3, "\n".join(lines))
        assert lines[0].startswith('<Thread'), lines[0]
        self.assertEqual(lines[1], "1", lines[1])

    def test_greenlet(self):
        new_mod = """import eventlet
eventlet.monkey_patch()
from eventlet import event
import threading
evt = event.Event()
def test():
    print(repr(threading.currentThread()))
    evt.send()
eventlet.spawn_n(test)
evt.wait()
print(len(threading._active))
"""
        self.write_to_tempfile("newmod", new_mod)
        output, lines = self.launch_subprocess('newmod.py')
        self.assertEqual(len(lines), 3, "\n".join(lines))
        assert lines[0].startswith('<_MainThread'), lines[0]
        self.assertEqual(lines[1], "1", lines[1])

    def test_greenthread(self):
        new_mod = """import eventlet
eventlet.monkey_patch()
import threading
def test():
    print(repr(threading.currentThread()))
t = eventlet.spawn(test)
t.wait()
print(len(threading._active))
"""
        self.write_to_tempfile("newmod", new_mod)
        output, lines = self.launch_subprocess('newmod.py')
        self.assertEqual(len(lines), 3, "\n".join(lines))
        assert lines[0].startswith('<_GreenThread'), lines[0]
        self.assertEqual(lines[1], "1", lines[1])

    def test_keyerror(self):
        new_mod = """import eventlet
eventlet.monkey_patch()
"""
        self.write_to_tempfile("newmod", new_mod)
        output, lines = self.launch_subprocess('newmod.py')
        self.assertEqual(len(lines), 1, "\n".join(lines))


class Os(ProcessBase):
    def test_waitpid(self):
        new_mod = """import subprocess
import eventlet
eventlet.monkey_patch(all=False, os=True)
process = subprocess.Popen("sleep 0.1 && false", shell=True)
print(process.wait())"""
        self.write_to_tempfile("newmod", new_mod)
        output, lines = self.launch_subprocess('newmod.py')
        self.assertEqual(len(lines), 2, "\n".join(lines))
        self.assertEqual('1', lines[0], repr(output))


class GreenThreadWrapper(ProcessBase):
    prologue = """import eventlet
eventlet.monkey_patch()
import threading
def test():
    t = threading.currentThread()
"""
    epilogue = """
t = eventlet.spawn(test)
t.wait()
"""

    def test_join(self):
        self.write_to_tempfile("newmod", self.prologue + """
    def test2():
        global t2
        t2 = threading.currentThread()
    eventlet.spawn(test2)
""" + self.epilogue + """
print(repr(t2))
t2.join()
""")
        output, lines = self.launch_subprocess('newmod.py')
        self.assertEqual(len(lines), 2, "\n".join(lines))
        assert lines[0].startswith('<_GreenThread'), lines[0]

    def test_name(self):
        self.write_to_tempfile("newmod", self.prologue + """
    print(t.name)
    print(t.getName())
    print(t.get_name())
    t.name = 'foo'
    print(t.name)
    print(t.getName())
    print(t.get_name())
    t.setName('bar')
    print(t.name)
    print(t.getName())
    print(t.get_name())
""" + self.epilogue)
        output, lines = self.launch_subprocess('newmod.py')
        self.assertEqual(len(lines), 10, "\n".join(lines))
        for i in range(0, 3):
            self.assertEqual(lines[i], "GreenThread-1", lines[i])
        for i in range(3, 6):
            self.assertEqual(lines[i], "foo", lines[i])
        for i in range(6, 9):
            self.assertEqual(lines[i], "bar", lines[i])

    def test_ident(self):
        self.write_to_tempfile("newmod", self.prologue + """
    print(id(t._g))
    print(t.ident)
""" + self.epilogue)
        output, lines = self.launch_subprocess('newmod.py')
        self.assertEqual(len(lines), 3, "\n".join(lines))
        self.assertEqual(lines[0], lines[1])

    def test_is_alive(self):
        self.write_to_tempfile("newmod", self.prologue + """
    print(t.is_alive())
    print(t.isAlive())
""" + self.epilogue)
        output, lines = self.launch_subprocess('newmod.py')
        self.assertEqual(len(lines), 3, "\n".join(lines))
        self.assertEqual(lines[0], "True", lines[0])
        self.assertEqual(lines[1], "True", lines[1])

    def test_is_daemon(self):
        self.write_to_tempfile("newmod", self.prologue + """
    print(t.is_daemon())
    print(t.isDaemon())
""" + self.epilogue)
        output, lines = self.launch_subprocess('newmod.py')
        self.assertEqual(len(lines), 3, "\n".join(lines))
        self.assertEqual(lines[0], "True", lines[0])
        self.assertEqual(lines[1], "True", lines[1])


def test_patcher_existing_locks_early():
    tests.run_isolated('patcher_existing_locks_early.py')


def test_patcher_existing_locks_late():
    tests.run_isolated('patcher_existing_locks_late.py')


def test_patcher_existing_locks_locked():
    tests.run_isolated('patcher_existing_locks_locked.py')


@tests.skip_if_CRLock_exist
def test_patcher_existing_locks_unlocked():
    tests.run_isolated('patcher_existing_locks_unlocked.py')


def test_importlib_lock():
    tests.run_isolated('patcher_importlib_lock.py')


def test_threading_condition():
    tests.run_isolated('patcher_threading_condition.py')


def test_threading_join():
    tests.run_isolated('patcher_threading_join.py')


def test_socketserver_selectors():
    tests.run_isolated('patcher_socketserver_selectors.py')


def test_blocking_select_methods_are_deleted():
    tests.run_isolated('patcher_blocking_select_methods_are_deleted.py')


def test_regular_file_readall():
    tests.run_isolated('regular_file_readall.py')


def test_threading_current():
    tests.run_isolated('patcher_threading_current.py')
