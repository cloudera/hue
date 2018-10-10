# Copyright (c) 2007, Linden Research, Inc.
# Copyright (c) 2007, IBM Corp.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import print_function

import gc
import random
import re
import time

import eventlet
from eventlet import tpool
import six
import tests


one = 1
two = 2
three = 3
none = None


def noop():
    pass


def raise_exception():
    raise RuntimeError("hi")


class TestTpool(tests.LimitedTestCase):
    def setUp(self):
        super(TestTpool, self).setUp()

    def tearDown(self):
        tpool.killall()
        super(TestTpool, self).tearDown()

    @tests.skip_with_pyevent
    def test_wrap_tuple(self):
        my_tuple = (1, 2)
        prox = tpool.Proxy(my_tuple)
        self.assertEqual(prox[0], 1)
        self.assertEqual(prox[1], 2)
        self.assertEqual(len(my_tuple), 2)

    @tests.skip_with_pyevent
    def test_wrap_string(self):
        my_object = "whatever"
        prox = tpool.Proxy(my_object)
        self.assertEqual(str(my_object), str(prox))
        self.assertEqual(len(my_object), len(prox))
        self.assertEqual(my_object.join(['a', 'b']), prox.join(['a', 'b']))

    @tests.skip_with_pyevent
    def test_wrap_uniterable(self):
        prox = tpool.Proxy([])

        def index():
            prox[0]

        def key():
            prox['a']

        self.assertRaises(IndexError, index)
        self.assertRaises(TypeError, key)

    @tests.skip_with_pyevent
    def test_wrap_dict(self):
        my_object = {'a': 1}
        prox = tpool.Proxy(my_object)
        self.assertEqual('a', list(prox.keys())[0])
        self.assertEqual(1, prox['a'])
        self.assertEqual(str(my_object), str(prox))
        self.assertEqual(repr(my_object), repr(prox))

    @tests.skip_with_pyevent
    def test_wrap_module_class(self):
        prox = tpool.Proxy(re)
        self.assertEqual(tpool.Proxy, type(prox))
        exp = prox.compile('(.)(.)(.)')
        self.assertEqual(exp.groups, 3)
        assert repr(prox.compile)

    @tests.skip_with_pyevent
    def test_wrap_eq(self):
        prox = tpool.Proxy(re)
        exp1 = prox.compile('.')
        exp2 = prox.compile(exp1.pattern)
        self.assertEqual(exp1, exp2)
        exp3 = prox.compile('/')
        assert exp1 != exp3

    @tests.skip_with_pyevent
    def test_wrap_ints(self):
        p = tpool.Proxy(4)
        assert p == 4

    @tests.skip_with_pyevent
    def test_wrap_hash(self):
        prox1 = tpool.Proxy('' + 'A')
        prox2 = tpool.Proxy('A' + '')
        assert prox1 == 'A'
        assert 'A' == prox2
        # assert prox1 == prox2 FIXME - could __eq__ unwrap rhs if it is other proxy?
        self.assertEqual(hash(prox1), hash(prox2))
        proxList = tpool.Proxy([])
        self.assertRaises(TypeError, hash, proxList)

    @tests.skip_with_pyevent
    def test_wrap_nonzero(self):
        prox = tpool.Proxy(re)
        exp1 = prox.compile('.')
        assert bool(exp1)
        prox2 = tpool.Proxy([1, 2, 3])
        assert bool(prox2)

    @tests.skip_with_pyevent
    def test_multiple_wraps(self):
        prox1 = tpool.Proxy(re)
        prox2 = tpool.Proxy(re)
        prox1.compile('.')
        x2 = prox1.compile('.')
        del x2
        prox2.compile('.')

    @tests.skip_with_pyevent
    def test_wrap_getitem(self):
        prox = tpool.Proxy([0, 1, 2])
        self.assertEqual(prox[0], 0)

    @tests.skip_with_pyevent
    def test_wrap_setitem(self):
        prox = tpool.Proxy([0, 1, 2])
        prox[1] = 2
        self.assertEqual(prox[1], 2)

    @tests.skip_with_pyevent
    def test_wrap_iterator(self):
        self.reset_timeout(2)
        prox = tpool.Proxy(range(10))
        result = []
        for i in prox:
            result.append(i)
        self.assertEqual(list(range(10)), result)

    @tests.skip_with_pyevent
    def test_wrap_iterator2(self):
        self.reset_timeout(5)  # might take a while due to imprecise sleeping

        def foo():
            import time
            for x in range(2):
                yield x
                time.sleep(0.001)

        counter = [0]

        def tick():
            for i in six.moves.range(20000):
                counter[0] += 1
                if counter[0] % 20 == 0:
                    eventlet.sleep(0.0001)
                else:
                    eventlet.sleep()

        gt = eventlet.spawn(tick)
        previtem = 0
        for item in tpool.Proxy(foo()):
            assert item >= previtem
        # make sure the tick happened at least a few times so that we know
        # that our iterations in foo() were actually tpooled
        assert counter[0] > 10, counter[0]
        gt.kill()

    @tests.skip_with_pyevent
    def test_raising_exceptions(self):
        prox = tpool.Proxy(re)

        def nofunc():
            prox.never_name_a_function_like_this()
        self.assertRaises(AttributeError, nofunc)

        from tests import tpool_test
        prox = tpool.Proxy(tpool_test)
        self.assertRaises(RuntimeError, prox.raise_exception)

    @tests.skip_with_pyevent
    def test_variable_and_keyword_arguments_with_function_calls(self):
        import optparse
        parser = tpool.Proxy(optparse.OptionParser())
        parser.add_option('-n', action='store', type='string', dest='n')
        opts, args = parser.parse_args(["-nfoo"])
        self.assertEqual(opts.n, 'foo')

    @tests.skip_with_pyevent
    def test_contention(self):
        from tests import tpool_test
        prox = tpool.Proxy(tpool_test)

        pile = eventlet.GreenPile(4)
        pile.spawn(lambda: self.assertEqual(prox.one, 1))
        pile.spawn(lambda: self.assertEqual(prox.two, 2))
        pile.spawn(lambda: self.assertEqual(prox.three, 3))
        results = list(pile)
        self.assertEqual(len(results), 3)

    @tests.skip_with_pyevent
    def test_timeout(self):
        blocking = eventlet.patcher.original('time')
        eventlet.Timeout(0.1, eventlet.Timeout())
        try:
            tpool.execute(blocking.sleep, 0.3)
            assert False, 'Expected Timeout'
        except eventlet.Timeout:
            pass

    @tests.skip_with_pyevent
    def test_killall(self):
        tpool.killall()
        tpool.setup()

    @tests.skip_with_pyevent
    def test_killall_remaining_results(self):
        semaphore = eventlet.Event()

        def native_fun():
            time.sleep(.5)

        def gt_fun():
            semaphore.send(None)
            tpool.execute(native_fun)

        gt = eventlet.spawn(gt_fun)
        semaphore.wait()
        tpool.killall()
        gt.wait()

    @tests.skip_with_pyevent
    def test_autowrap(self):
        x = tpool.Proxy({'a': 1, 'b': 2}, autowrap=(int,))
        assert isinstance(x.get('a'), tpool.Proxy)
        assert not isinstance(x.items(), tpool.Proxy)
        # attributes as well as callables
        from tests import tpool_test
        x = tpool.Proxy(tpool_test, autowrap=(int,))
        assert isinstance(x.one, tpool.Proxy)
        assert not isinstance(x.none, tpool.Proxy)

    @tests.skip_with_pyevent
    def test_autowrap_names(self):
        x = tpool.Proxy({'a': 1, 'b': 2}, autowrap_names=('get',))
        assert isinstance(x.get('a'), tpool.Proxy)
        assert not isinstance(x.items(), tpool.Proxy)
        from tests import tpool_test
        x = tpool.Proxy(tpool_test, autowrap_names=('one',))
        assert isinstance(x.one, tpool.Proxy)
        assert not isinstance(x.two, tpool.Proxy)

    @tests.skip_with_pyevent
    def test_autowrap_both(self):
        from tests import tpool_test
        x = tpool.Proxy(tpool_test, autowrap=(int,), autowrap_names=('one',))
        assert isinstance(x.one, tpool.Proxy)
        # violating the abstraction to check that we didn't double-wrap
        assert not isinstance(x._obj, tpool.Proxy)

    @tests.skip_with_pyevent
    def test_callable(self):
        def wrapped(arg):
            return arg
        x = tpool.Proxy(wrapped)
        self.assertEqual(4, x(4))
        # verify that it wraps return values if specified
        x = tpool.Proxy(wrapped, autowrap_names=('__call__',))
        assert isinstance(x(4), tpool.Proxy)
        self.assertEqual("4", str(x(4)))

    @tests.skip_with_pyevent
    def test_callable_iterator(self):
        def wrapped(arg):
            yield arg
            yield arg
            yield arg

        x = tpool.Proxy(wrapped, autowrap_names=('__call__',))
        for r in x(3):
            self.assertEqual(3, r)

    @tests.skip_with_pyevent
    def test_eventlet_timeout(self):
        def raise_timeout():
            raise eventlet.Timeout()
        self.assertRaises(eventlet.Timeout, tpool.execute, raise_timeout)

    @tests.skip_with_pyevent
    def test_tpool_set_num_threads(self):
        tpool.set_num_threads(5)
        self.assertEqual(5, tpool._nthreads)


class TpoolLongTests(tests.LimitedTestCase):
    TEST_TIMEOUT = 60

    @tests.skip_with_pyevent
    def test_a_buncha_stuff(self):
        assert_ = self.assert_

        class Dummy(object):
            def foo(self, when, token=None):
                assert_(token is not None)
                time.sleep(random.random() / 200.0)
                return token

        def sender_loop(loopnum):
            obj = tpool.Proxy(Dummy())
            count = 100
            for n in six.moves.range(count):
                eventlet.sleep(random.random() / 200.0)
                now = time.time()
                token = loopnum * count + n
                rv = obj.foo(now, token=token)
                self.assertEqual(token, rv)
                eventlet.sleep(random.random() / 200.0)

        cnt = 10
        pile = eventlet.GreenPile(cnt)
        for i in six.moves.range(cnt):
            pile.spawn(sender_loop, i)
        results = list(pile)
        self.assertEqual(len(results), cnt)
        tpool.killall()

    @tests.skip_with_pyevent
    def test_leakage_from_tracebacks(self):
        tpool.execute(noop)  # get it started
        gc.collect()
        initial_objs = len(gc.get_objects())
        for i in range(10):
            self.assertRaises(RuntimeError, tpool.execute, raise_exception)
        gc.collect()
        middle_objs = len(gc.get_objects())
        # some objects will inevitably be created by the previous loop
        # now we test to ensure that running the loop an order of
        # magnitude more doesn't generate additional objects
        for i in six.moves.range(100):
            self.assertRaises(RuntimeError, tpool.execute, raise_exception)
        first_created = middle_objs - initial_objs
        gc.collect()
        second_created = len(gc.get_objects()) - middle_objs
        self.assert_(second_created - first_created < 10,
                     "first loop: %s, second loop: %s" % (first_created,
                                                          second_created))
        tpool.killall()


def test_isolate_from_socket_default_timeout():
    tests.run_isolated('tpool_isolate_socket_default_timeout.py', timeout=1)


def test_exception_leak():
    tests.run_isolated('tpool_exception_leak.py')
