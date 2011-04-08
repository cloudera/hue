import weakref
from eventlet.green import thread
from eventlet import greenthread
from eventlet import event
import eventlet
from eventlet import corolocal

from tests import LimitedTestCase, skipped

class Locals(LimitedTestCase):
    def passthru(self, *args, **kw):
        self.results.append((args, kw))
        return args, kw

    def setUp(self):
        self.results = []
        super(Locals, self).setUp()

    def tearDown(self):
        self.results = []
        super(Locals, self).tearDown()

    @skipped  # cause it relies on internal details of corolocal that are no longer true
    def test_simple(self):
        tls = thread._local()
        g_ids = []
        evt = event.Event()
        def setter(tls, v):
            g_id = id(greenthread.getcurrent())
            g_ids.append(g_id)
            tls.value = v
            evt.wait()
        thread.start_new_thread(setter, args=(tls, 1))
        thread.start_new_thread(setter, args=(tls, 2))
        eventlet.sleep()
        objs = object.__getattribute__(tls, "__objs")
        self.failUnlessEqual(sorted(g_ids), sorted(objs.keys()))
        self.failUnlessEqual(objs[g_ids[0]]['value'], 1)
        self.failUnlessEqual(objs[g_ids[1]]['value'], 2)
        self.failUnlessRaises(AttributeError, lambda: tls.value)
        evt.send("done")
        eventlet.sleep()

    def test_assignment(self):
        my_local = corolocal.local()
        my_local.a = 1
        def do_something():
            my_local.b = 2
            self.assertEqual(my_local.b, 2)
            try:
                my_local.a
                self.fail()
            except AttributeError:
                pass
        eventlet.spawn(do_something).wait()
        self.assertEqual(my_local.a, 1)
        
    def test_calls_init(self):
        init_args = []
        class Init(corolocal.local):
            def __init__(self, *args):
                init_args.append((args, eventlet.getcurrent()))
        
        my_local = Init(1,2,3)
        self.assertEqual(init_args[0][0], (1,2,3))
        self.assertEqual(init_args[0][1], eventlet.getcurrent())
        
        def do_something():
            my_local.foo = 'bar'
            self.assertEqual(len(init_args), 2, init_args)
            self.assertEqual(init_args[1][0], (1,2,3))
            self.assertEqual(init_args[1][1], eventlet.getcurrent())
            
        eventlet.spawn(do_something).wait()
        
    def test_calling_methods(self):
        class Caller(corolocal.local):
            def callme(self):
                return self.foo
        
        my_local = Caller()
        my_local.foo = "foo1"
        self.assertEquals("foo1", my_local.callme())
        
        def do_something():
            my_local.foo = "foo2"
            self.assertEquals("foo2", my_local.callme())
            
        eventlet.spawn(do_something).wait()        
            
        my_local.foo = "foo3"
        self.assertEquals("foo3", my_local.callme())
        
    def test_no_leaking(self):
        refs = weakref.WeakKeyDictionary()
        my_local = corolocal.local()
        class X(object):
            pass
        def do_something(i):
            o = X()
            refs[o] = True
            my_local.foo = o
            
        p = eventlet.GreenPool()
        for i in xrange(100):
            p.spawn(do_something, i)
        p.waitall()
        del p
        # at this point all our coros have terminated
        self.assertEqual(len(refs), 1)
        