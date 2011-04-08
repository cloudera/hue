import os
import shutil
import subprocess
import sys
import tempfile

from tests import LimitedTestCase, main, skip_with_pyevent

base_module_contents = """
import socket
import urllib
print "base", socket, urllib
"""

patching_module_contents = """
from eventlet.green import socket
from eventlet.green import urllib
from eventlet import patcher
print 'patcher', socket, urllib
patcher.inject('base', globals(), ('socket', socket), ('urllib', urllib))
del patcher
"""

import_module_contents = """
import patching
import socket
print "importing", patching, socket, patching.socket, patching.urllib
"""

class ProcessBase(LimitedTestCase):
    TEST_TIMEOUT=3 # starting processes is time-consuming
    def setUp(self):
        self._saved_syspath = sys.path
        self.tempdir = tempfile.mkdtemp('_patcher_test')
        
    def tearDown(self):
        sys.path = self._saved_syspath
        shutil.rmtree(self.tempdir)
        
    def write_to_tempfile(self, name, contents):
        filename = os.path.join(self.tempdir, name + '.py')
        fd = open(filename, "w")
        fd.write(contents)
        fd.close()
        
    def launch_subprocess(self, filename):
        python_path = os.pathsep.join(sys.path + [self.tempdir])
        new_env = os.environ.copy()
        new_env['PYTHONPATH'] = python_path
        if not filename.endswith('.py'):
            filename = filename + '.py'
        p = subprocess.Popen([sys.executable, 
                              os.path.join(self.tempdir, filename)],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=new_env)
        output, _ = p.communicate()
        lines = output.split("\n")
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
        self.assert_(lines[0].startswith('patcher'), repr(output))
        self.assert_(lines[1].startswith('base'), repr(output))
        self.assert_(lines[2].startswith('importing'), repr(output))
        self.assert_('eventlet.green.socket' in lines[1], repr(output))
        self.assert_('eventlet.green.urllib' in lines[1], repr(output))
        self.assert_('eventlet.green.socket' in lines[2], repr(output))
        self.assert_('eventlet.green.urllib' in lines[2], repr(output))
        self.assert_('eventlet.green.httplib' not in lines[2], repr(output))
        
    def test_import_patched_defaults(self):
        self.write_to_tempfile("base", base_module_contents)
        new_mod = """
from eventlet import patcher
base = patcher.import_patched('base')
print "newmod", base, base.socket, base.urllib.socket.socket
"""
        self.write_to_tempfile("newmod", new_mod)
        output, lines = self.launch_subprocess('newmod.py')
        self.assert_(lines[0].startswith('base'), repr(output))
        self.assert_(lines[1].startswith('newmod'), repr(output))
        self.assert_('eventlet.green.socket' in lines[1], repr(output))
        self.assert_('GreenSocket' in lines[1], repr(output))


class MonkeyPatch(ProcessBase):        
    def test_patched_modules(self):
        new_mod = """
from eventlet import patcher
patcher.monkey_patch()
import socket
import urllib
print "newmod", socket.socket, urllib.socket.socket
"""
        self.write_to_tempfile("newmod", new_mod)
        output, lines = self.launch_subprocess('newmod.py')
        self.assert_(lines[0].startswith('newmod'), repr(output))
        self.assertEqual(lines[0].count('GreenSocket'), 2, repr(output))
        
    def test_early_patching(self):
        new_mod = """
from eventlet import patcher
patcher.monkey_patch()
import eventlet
eventlet.sleep(0.01)
print "newmod"
"""
        self.write_to_tempfile("newmod", new_mod)
        output, lines = self.launch_subprocess('newmod.py')
        self.assertEqual(len(lines), 2, repr(output))
        self.assert_(lines[0].startswith('newmod'), repr(output))

    def test_late_patching(self):
        new_mod = """
import eventlet
eventlet.sleep(0.01)
from eventlet import patcher
patcher.monkey_patch()
eventlet.sleep(0.01)
print "newmod"
"""
        self.write_to_tempfile("newmod", new_mod)
        output, lines = self.launch_subprocess('newmod.py')
        self.assertEqual(len(lines), 2, repr(output))
        self.assert_(lines[0].startswith('newmod'), repr(output))
        

    def test_typeerror(self):
        new_mod = """
from eventlet import patcher
patcher.monkey_patch(finagle=True)
"""
        self.write_to_tempfile("newmod", new_mod)
        output, lines = self.launch_subprocess('newmod.py')
        self.assert_(lines[-2].startswith('TypeError'), repr(output))
        self.assert_('finagle' in lines[-2], repr(output))
        

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
print "already_patched", ",".join(sorted(patcher.already_patched.keys()))
""" % (call, expected_list, not_expected_list)
        self.write_to_tempfile("newmod", new_mod)
        output, lines = self.launch_subprocess('newmod.py')
        ap = 'already_patched'
        self.assert_(lines[0].startswith(ap), repr(output))
        patched_modules = lines[0][len(ap):].strip()
        # psycopg might or might not be patched based on installed modules
        patched_modules = patched_modules.replace("psycopg,", "")
        # ditto for MySQLdb
        patched_modules = patched_modules.replace("MySQLdb,", "")
        self.assertEqual(patched_modules, expected,
                         "Logic:%s\nExpected: %s != %s" %(call, expected,
                                                          patched_modules))

    def test_boolean(self):
        self.assert_boolean_logic("patcher.monkey_patch()",
                                         'os,select,socket,thread,time')

    def test_boolean_all(self):
        self.assert_boolean_logic("patcher.monkey_patch(all=True)",
                                         'os,select,socket,thread,time')

    def test_boolean_all_single(self):
        self.assert_boolean_logic("patcher.monkey_patch(all=True, socket=True)",
                                         'os,select,socket,thread,time')

    def test_boolean_all_negative(self):
        self.assert_boolean_logic("patcher.monkey_patch(all=False, "\
                                      "socket=False, select=True)",
                                         'select')

    def test_boolean_single(self):
        self.assert_boolean_logic("patcher.monkey_patch(socket=True)",
                                         'socket')

    def test_boolean_double(self):
        self.assert_boolean_logic("patcher.monkey_patch(socket=True,"\
                                      " select=True)",
                                         'select,socket')

    def test_boolean_negative(self):
        self.assert_boolean_logic("patcher.monkey_patch(socket=False)",
                                         'os,select,thread,time')

    def test_boolean_negative2(self):
        self.assert_boolean_logic("patcher.monkey_patch(socket=False,"\
                                      "time=False)",
                                         'os,select,thread')

    def test_conflicting_specifications(self):
        self.assert_boolean_logic("patcher.monkey_patch(socket=False, "\
                                      "select=True)",
                                         'select')


test_monkey_patch_threading = """
def test_monkey_patch_threading():
    tickcount = [0]
    def tick():
        for i in xrange(1000):
            tickcount[0] += 1
            eventlet.sleep()

    def do_sleep():
        tpool.execute(time.sleep, 0.5)

    eventlet.spawn(tick)
    w1 = eventlet.spawn(do_sleep)
    w1.wait()
    print tickcount[0]
    assert tickcount[0] > 900
    tpool.killall()
"""

class Tpool(ProcessBase):
    TEST_TIMEOUT=3

    @skip_with_pyevent
    def test_simple(self):
        new_mod = """
import eventlet
from eventlet import patcher
patcher.monkey_patch()
from eventlet import tpool
print "newmod", tpool.execute(len, "hi")
print "newmod", tpool.execute(len, "hi2")
tpool.killall()
"""
        self.write_to_tempfile("newmod", new_mod)
        output, lines = self.launch_subprocess('newmod.py')
        self.assertEqual(len(lines), 3, output)
        self.assert_(lines[0].startswith('newmod'), repr(output))
        self.assert_('2' in lines[0], repr(output))
        self.assert_('3' in lines[1], repr(output))

    @skip_with_pyevent
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

    @skip_with_pyevent
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


if __name__ == '__main__':
    main()
