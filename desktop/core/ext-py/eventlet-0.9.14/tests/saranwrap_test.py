import warnings
warnings.simplefilter('ignore', DeprecationWarning)
from eventlet import saranwrap
warnings.simplefilter('default', DeprecationWarning)
from eventlet import greenpool, sleep

import os
import eventlet
import sys
import tempfile
import time
from tests import LimitedTestCase, main, skip_on_windows, skip_with_pyevent
import re
import StringIO

# random test stuff
def list_maker():
    return [0,1,2]

one = 1
two = 2
three = 3

class CoroutineCallingClass(object):
    def __init__(self):
        self._my_dict = {}

    def run_coroutine(self):
        eventlet.spawn_n(self._add_random_key)

    def _add_random_key(self):
        self._my_dict['random'] = 'yes, random'

    def get_dict(self):
        return self._my_dict


class TestSaranwrap(LimitedTestCase):
    TEST_TIMEOUT=8
    def assert_server_exists(self, prox):
        self.assert_(saranwrap.status(prox))
        prox.foo = 0
        self.assertEqual(0, prox.foo)

    @skip_on_windows
    @skip_with_pyevent
    def test_wrap_tuple(self):
        my_tuple = (1, 2)
        prox = saranwrap.wrap(my_tuple)
        self.assertEqual(prox[0], 1)
        self.assertEqual(prox[1], 2)
        self.assertEqual(len(my_tuple), 2)

    @skip_on_windows
    @skip_with_pyevent
    def test_wrap_string(self):
        my_object = "whatever"
        prox = saranwrap.wrap(my_object)
        self.assertEqual(str(my_object), str(prox))
        self.assertEqual(len(my_object), len(prox))
        self.assertEqual(my_object.join(['a', 'b']), prox.join(['a', 'b']))

    @skip_on_windows
    @skip_with_pyevent
    def test_wrap_uniterable(self):
        # here we're treating the exception as just a normal class
        prox = saranwrap.wrap(FloatingPointError())
        def index():
            prox[0]
        def key():
            prox['a']

        self.assertRaises(IndexError, index)
        self.assertRaises(TypeError, key)

    @skip_on_windows
    @skip_with_pyevent
    def test_wrap_dict(self):
        my_object = {'a':1}
        prox = saranwrap.wrap(my_object)
        self.assertEqual('a', prox.keys()[0])
        self.assertEqual(1, prox['a'])
        self.assertEqual(str(my_object), str(prox))
        self.assertEqual('saran:' + repr(my_object), repr(prox))

    @skip_on_windows
    @skip_with_pyevent
    def test_wrap_module_class(self):
        prox = saranwrap.wrap(re)
        self.assertEqual(saranwrap.Proxy, type(prox))
        exp = prox.compile('.')
        self.assertEqual(exp.flags, 0)
        self.assert_(repr(prox.compile))

    @skip_on_windows
    @skip_with_pyevent
    def test_wrap_eq(self):
        prox = saranwrap.wrap(re)
        exp1 = prox.compile('.')
        exp2 = prox.compile(exp1.pattern)
        self.assertEqual(exp1, exp2)
        exp3 = prox.compile('/')
        self.assert_(exp1 != exp3)

    @skip_on_windows
    @skip_with_pyevent
    def test_wrap_nonzero(self):
        prox = saranwrap.wrap(re)
        exp1 = prox.compile('.')
        self.assert_(bool(exp1))
        prox2 = saranwrap.Proxy([1, 2, 3])
        self.assert_(bool(prox2))

    @skip_on_windows
    @skip_with_pyevent
    def test_multiple_wraps(self):
        prox1 = saranwrap.wrap(re)
        prox2 = saranwrap.wrap(re)
        x1 = prox1.compile('.')
        x2 = prox1.compile('.')
        del x2
        x3 = prox2.compile('.')

    @skip_on_windows
    @skip_with_pyevent
    def test_dict_passthru(self):
        prox = saranwrap.wrap(StringIO)
        x = prox.StringIO('a')
        self.assertEqual(type(x.__dict__), saranwrap.ObjectProxy)
        # try it all on one line just for the sake of it
        self.assertEqual(type(saranwrap.wrap(StringIO).StringIO('a').__dict__), saranwrap.ObjectProxy)

    @skip_on_windows
    @skip_with_pyevent
    def test_is_value(self):
        server = saranwrap.Server(None, None, None)
        self.assert_(server.is_value(None))

    @skip_on_windows
    @skip_with_pyevent
    def test_wrap_getitem(self):
        prox = saranwrap.wrap([0,1,2])
        self.assertEqual(prox[0], 0)

    @skip_on_windows
    @skip_with_pyevent
    def test_wrap_setitem(self):
        prox = saranwrap.wrap([0,1,2])
        prox[1] = 2
        self.assertEqual(prox[1], 2)

    @skip_on_windows
    @skip_with_pyevent
    def test_raising_exceptions(self):
        prox = saranwrap.wrap(re)
        def nofunc():
            prox.never_name_a_function_like_this()
        self.assertRaises(AttributeError, nofunc)

    @skip_on_windows
    @skip_with_pyevent
    def test_unpicklable_server_exception(self):
        prox = saranwrap.wrap(saranwrap)
        def unpickle():
            prox.raise_an_unpicklable_error()

        self.assertRaises(saranwrap.UnrecoverableError, unpickle)

        # It's basically dead
        #self.assert_server_exists(prox)

    @skip_on_windows
    @skip_with_pyevent
    def test_pickleable_server_exception(self):
        prox = saranwrap.wrap(saranwrap)
        def fperror():
            prox.raise_standard_error()

        self.assertRaises(FloatingPointError, fperror)
        self.assert_server_exists(prox)

    @skip_on_windows
    @skip_with_pyevent
    def test_print_does_not_break_wrapper(self):
        prox = saranwrap.wrap(saranwrap)
        prox.print_string('hello')
        self.assert_server_exists(prox)

    @skip_on_windows
    @skip_with_pyevent
    def test_stderr_does_not_break_wrapper(self):
        prox = saranwrap.wrap(saranwrap)
        prox.err_string('goodbye')
        self.assert_server_exists(prox)

    @skip_on_windows
    @skip_with_pyevent
    def test_status(self):
        prox = saranwrap.wrap(time)
        a = prox.gmtime(0)
        status = saranwrap.status(prox)
        self.assertEqual(status['object_count'], 1)
        self.assertEqual(status['next_id'], 2)
        self.assert_(status['pid'])  # can't guess what it will be
        # status of an object should be the same as the module
        self.assertEqual(saranwrap.status(a), status)
        # create a new one then immediately delete it
        prox.gmtime(1)
        is_id = prox.ctime(1) # sync up deletes
        status = saranwrap.status(prox)
        self.assertEqual(status['object_count'], 1)
        self.assertEqual(status['next_id'], 3)
        prox2 = saranwrap.wrap(re)
        self.assert_(status['pid'] != saranwrap.status(prox2)['pid'])

    @skip_on_windows
    @skip_with_pyevent
    def test_del(self):
        prox = saranwrap.wrap(time)
        delme = prox.gmtime(0)
        status_before = saranwrap.status(prox)
        #print status_before['objects']
        del delme
        # need to do an access that doesn't create an object
        # in order to sync up the deleted objects
        prox.ctime(1)
        status_after = saranwrap.status(prox)
        #print status_after['objects']
        self.assertLessThan(status_after['object_count'], status_before['object_count'])

    @skip_on_windows
    @skip_with_pyevent
    def test_contains(self):
        prox = saranwrap.wrap({'a':'b'})
        self.assert_('a' in prox)
        self.assert_('x' not in prox)

    @skip_on_windows
    @skip_with_pyevent
    def test_variable_and_keyword_arguments_with_function_calls(self):
        import optparse
        prox = saranwrap.wrap(optparse)
        parser = prox.OptionParser()
        z = parser.add_option('-n', action='store', type='string', dest='n')
        opts,args = parser.parse_args(["-nfoo"])
        self.assertEqual(opts.n, 'foo')

    @skip_on_windows
    @skip_with_pyevent
    def test_original_proxy_going_out_of_scope(self):
        def make_re():
            prox = saranwrap.wrap(re)
            # after this function returns, prox should fall out of scope
            return prox.compile('.')
        tid = make_re()
        self.assertEqual(tid.flags, 0)
        def make_list():
            from tests import saranwrap_test
            prox = saranwrap.wrap(saranwrap_test.list_maker)
            # after this function returns, prox should fall out of scope
            return prox()
        proxl = make_list()
        self.assertEqual(proxl[2], 2)

    def test_status_of_none(self):
        try:
            saranwrap.status(None)
            self.assert_(False)
        except AttributeError, e:
            pass

    @skip_on_windows
    @skip_with_pyevent
    def test_not_inheriting_pythonpath(self):
        # construct a fake module in the temp directory
        temp_dir = tempfile.mkdtemp("saranwrap_test")
        fp = open(os.path.join(temp_dir, "tempmod.py"), "w")
        fp.write("""import os, sys
pypath = os.environ['PYTHONPATH']
sys_path = sys.path""")
        fp.close()

        # this should fail because we haven't stuck the temp_dir in our path yet
        prox = saranwrap.wrap_module('tempmod')
        try:
            prox.pypath
            self.fail()
        except ImportError:
            pass

        # now try to saranwrap it
        sys.path.append(temp_dir)
        try:
            import tempmod
            prox = saranwrap.wrap(tempmod)
            self.assert_(prox.pypath.count(temp_dir))
            self.assert_(prox.sys_path.count(temp_dir))
        finally:
            import shutil
            shutil.rmtree(temp_dir)
            sys.path.remove(temp_dir)

    @skip_on_windows
    @skip_with_pyevent
    def test_contention(self):
        from tests import saranwrap_test
        prox = saranwrap.wrap(saranwrap_test)

        pool = greenpool.GreenPool(4)
        pool.spawn_n(lambda: self.assertEquals(prox.one, 1))
        pool.spawn_n(lambda: self.assertEquals(prox.two, 2))
        pool.spawn_n(lambda: self.assertEquals(prox.three, 3))
        pool.waitall()

    @skip_on_windows
    @skip_with_pyevent
    def test_copy(self):
        import copy
        compound_object = {'a':[1,2,3]}
        prox = saranwrap.wrap(compound_object)
        def make_assertions(copied):
            self.assert_(isinstance(copied, dict))
            self.assert_(isinstance(copied['a'], list))
            self.assertEquals(copied, compound_object)
            self.assertNotEqual(id(compound_object), id(copied))

        make_assertions(copy.copy(prox))
        make_assertions(copy.deepcopy(prox))

    @skip_on_windows
    @skip_with_pyevent
    def test_list_of_functions(self):
        return # this test is known to fail, we can implement it sometime in the future if we wish
        from tests import saranwrap_test
        prox = saranwrap.wrap([saranwrap_test.list_maker])
        self.assertEquals(list_maker(), prox[0]())

    @skip_on_windows
    @skip_with_pyevent
    def test_under_the_hood_coroutines(self):
        # so, we want to write a class which uses a coroutine to call
        # a function.  Then we want to saranwrap that class, have
        # the object call the coroutine and verify that it ran

        from tests import saranwrap_test
        mod_proxy = saranwrap.wrap(saranwrap_test)
        obj_proxy = mod_proxy.CoroutineCallingClass()
        obj_proxy.run_coroutine()

        # sleep for a bit to make sure out coroutine ran by the time
        # we check the assert below
        sleep(0.1)

        self.assert_(
            'random' in obj_proxy.get_dict(),
            'Coroutine in saranwrapped object did not run')

    @skip_on_windows
    @skip_with_pyevent
    def test_child_process_death(self):
        prox = saranwrap.wrap({})
        pid = saranwrap.getpid(prox)
        self.assertEqual(os.kill(pid, 0), None)   # assert that the process is running
        del prox  # removing all references to the proxy should kill the child process
        sleep(0.1)  # need to let the signal handler run
        self.assertRaises(OSError, os.kill, pid, 0)  # raises OSError if pid doesn't exist

    @skip_on_windows
    @skip_with_pyevent
    def test_detection_of_server_crash(self):
        # make the server crash here
        pass

    @skip_on_windows
    @skip_with_pyevent
    def test_equality_with_local_object(self):
        # we'll implement this if there's a use case for it
        pass

    @skip_on_windows
    @skip_with_pyevent
    def test_non_blocking(self):
        # here we test whether it's nonblocking
        pass

if __name__ == '__main__':
    main()
