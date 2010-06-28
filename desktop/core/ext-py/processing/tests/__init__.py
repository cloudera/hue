#
# Unit tests for processing package
#

import unittest
import threading
import Queue
import time
import sys
import os
import signal
import array
import copy
import socket
import random
import logging
import ctypes

import processing.dummy
import processing.connection
import processing.managers
import processing.heap
import processing.managers
import processing.pool

#
# Constants
#

DELTA = 0.1
CHECK_TIMINGS = False     # making true makes tests take a lot longer
                          # and can sometimes cause some non-serious
                          # failures because some calls block a bit
                          # longer than expected
if CHECK_TIMINGS:
    TIMEOUT1, TIMEOUT2, TIMEOUT3 = 0.82, 0.35, 1.4
else:
    TIMEOUT1, TIMEOUT2, TIMEOUT3 = 0.1, 0.1, 0.1

HAVE_GETVALUE = not getattr(processing._processing,
                            'HAVE_BROKEN_SEM_GETVALUE', False)

#
# Creates a wrapper for a function which records the time it takes to finish
#

class TimingWrapper(object):

    def __init__(self, func):
        self.func = func
        self.elapsed = None

    def __call__(self, *args, **kwds):
        t = time.time()
        try:
            return self.func(*args, **kwds)
        finally:
            self.elapsed = time.time() - t
        
#
# Base class for test cases
#

class BaseTestCase(object):
    
    ALLOWED_TYPES = ('processes', 'manager', 'threads')

    def assertTimingAlmostEqual(self, a, b):
        if CHECK_TIMINGS:
            self.assertAlmostEqual(a, b, 1)

    def assertReturnsIfImplemented(self, value, func, *args):
        try:
            res = func(*args)
        except NotImplementedError:
            pass
        else:
            return self.assertEqual(value, res)

#
# Return the value of a semaphore
#

def getValue(self):
    try:
        return self.getValue()
    except AttributeError:
        try:
            return self._Semaphore__value
        except AttributeError:
            try:
                return self._value
            except AttributeError:
                raise NotImplementedError

#
# Testcases
#

class _TestProcess(BaseTestCase):

    ALLOWED_TYPES = ('processes', 'threads')

    def test_current(self):
        current = self.currentProcess()
        self.assertTrue(current.isAlive())
        self.assertTrue(not current.isDaemon())
        if self.TYPE != 'threads':
            authkey = current.getAuthKey()
            self.assertTrue(type(authkey) is str)
            self.assertTrue(len(authkey) > 0)
            self.assertEqual(current.getPid(), os.getpid())
            self.assertEqual(current.getExitCode(), None)

    def _test(self, q, *args, **kwds):
        current = self.currentProcess()
        q.put(args)
        q.put(kwds)
        q.put(current.getName())
        if self.TYPE != 'threads':
            q.put(current.getAuthKey())
            q.put(current.getPid())

    def test_process(self):
        q = self.Queue(1)
        e = self.Event()
        args = (q, 1, 2)
        kwargs = {'hello':23, 'bye':2.54}
        name = 'SomeProcess'
        p = self.Process(
            target=self._test, args=args, kwargs=kwargs, name=name
            )
        p.setDaemon(True)
        current = self.currentProcess()

        if self.TYPE != 'threads':
            self.assertEquals(p.getAuthKey(), current.getAuthKey())
        self.assertEquals(p.isAlive(), False)
        self.assertEquals(p.isDaemon(), True)
        self.assertTrue(p not in self.activeChildren())
        self.assertTrue(type(self.activeChildren()) is list)
        self.assertEqual(p.getExitCode(), None)
        
        p.start()
        
        self.assertEquals(p.getExitCode(), None)
        self.assertEquals(p.isAlive(), True)
        self.assertTrue(p in self.activeChildren())
        
        self.assertEquals(q.get(), args[1:])
        self.assertEquals(q.get(), kwargs)
        self.assertEquals(q.get(), p.getName())
        if self.TYPE != 'threads':
            self.assertEquals(q.get(), current.getAuthKey())
            self.assertEquals(q.get(), p.getPid())

        p.join()

        self.assertEquals(p.getExitCode(), 0)
        self.assertEquals(p.isAlive(), False)
        self.assertTrue(p not in self.activeChildren())        

    def _test_terminate(self):
        time.sleep(1000)

    def test_terminate(self):
        if self.TYPE == 'threads':
            return
        
        p = self.Process(target=self._test_terminate)
        p.setDaemon(True)
        p.start()

        self.assertEqual(p.isAlive(), True)
        self.assertTrue(p in self.activeChildren())
        self.assertEqual(p.getExitCode(), None)

        p.terminate()

        join = TimingWrapper(p.join)
        self.assertEqual(join(), None)
        self.assertTimingAlmostEqual(join.elapsed, 0.0)
        
        self.assertEqual(p.isAlive(), False)
        self.assertTrue(p not in self.activeChildren())

        p.join()

        # XXX sometimes get p.getExitCode() == 0 on Windows ...
        #self.assertEqual(p.getExitCode(), -signal.SIGTERM)

    def test_cpuCount(self):
        try:
            cpus = processing.cpuCount()
        except NotImplementedError:
            cpus = 1
        self.assertTrue(type(cpus) is int)
        self.assertTrue(cpus >= 1)

    def test_activeChildren(self):
        self.assertEqual(type(self.activeChildren()), list)

        p = self.Process(target=time.sleep, args=(DELTA,))
        self.assertTrue(p not in self.activeChildren())
        
        p.start()
        self.assertTrue(p in self.activeChildren())

        p.join()
        self.assertTrue(p not in self.activeChildren())

    def _test_recursion(self, wconn, id):
        wconn.send(id)
        if len(id) < 2:
            for i in range(2):
                p = self.Process(
                    target=self._test_recursion, args=(wconn, id+[i])
                    )
                p.start()
                p.join()

    def test_recursion(self):
        rconn, wconn = self.Pipe(duplex=False)
        self._test_recursion(wconn, [])
        
        time.sleep(DELTA)
        result = []
        while rconn.poll():
            result.append(rconn.recv())
            
        expected = [
            [],
              [0],
                [0, 0],
                [0, 1],
              [1],
                [1, 0],
                [1, 1]
            ]
        self.assertEqual(result, expected)

#
#
#

class _UpperCaser(processing.Process):

    def __init__(self):
        processing.Process.__init__(self)
        self.child_conn, self.parent_conn = processing.Pipe()

    def run(self):
        self.parent_conn.close()
        for s in iter(self.child_conn.recv, None):
            self.child_conn.send(s.upper())
        self.child_conn.close()

    def submit(self, s):
        assert type(s) is str
        self.parent_conn.send(s)
        return self.parent_conn.recv()

    def stop(self):
        self.parent_conn.send(None)
        self.parent_conn.close()
        self.child_conn.close()

class _TestSubclassingProcess(BaseTestCase):

    ALLOWED_TYPES = ('processes',)

    def test_subclassing(self):
        uppercaser = _UpperCaser()
        uppercaser.start()
        self.assertEqual(uppercaser.submit('hello'), 'HELLO')
        self.assertEqual(uppercaser.submit('world'), 'WORLD')
        uppercaser.stop()
        uppercaser.join()
        
#
#
#

class _TestQueue(BaseTestCase):

    def _test_put(self, queue, child_can_start, parent_can_continue):
        child_can_start.wait()
        for i in range(6):
            queue.get()
        parent_can_continue.set()

    def test_put(self):
        queue = self.Queue(maxsize=6)
        child_can_start = self.Event()
        parent_can_continue = self.Event()

        proc = self.Process(
            target=self._test_put,
            args=(queue, child_can_start, parent_can_continue)
            )
        proc.setDaemon(True)
        proc.start()
        
        self.assertEqual(queue.empty(), True)
        self.assertEqual(queue.full(), False)

        queue.put(1)
        queue.put(2, True)
        queue.put(3, True, None)
        queue.put(4, False)
        queue.put(5, False, None)
        queue.put_nowait(6)

        # the values may be in buffer but not yet in pipe so sleep a bit
        time.sleep(DELTA)     

        self.assertEqual(queue.empty(), False)
        self.assertEqual(queue.full(), True)

        put = TimingWrapper(queue.put)
        put_nowait = TimingWrapper(queue.put_nowait)

        self.assertRaises(Queue.Full, put, 7, False)
        self.assertTimingAlmostEqual(put.elapsed, 0)

        self.assertRaises(Queue.Full, put, 7, False, None)
        self.assertTimingAlmostEqual(put.elapsed, 0)

        self.assertRaises(Queue.Full, put_nowait, 7)
        self.assertTimingAlmostEqual(put_nowait.elapsed, 0)

        self.assertRaises(Queue.Full, put, 7, True, TIMEOUT1)
        self.assertTimingAlmostEqual(put.elapsed, TIMEOUT1)

        self.assertRaises(Queue.Full, put, 7, False, TIMEOUT2)
        self.assertTimingAlmostEqual(put.elapsed, 0)

        self.assertRaises(Queue.Full, put, 7, True, timeout=TIMEOUT3)
        self.assertTimingAlmostEqual(put.elapsed, TIMEOUT3)

        child_can_start.set()
        parent_can_continue.wait()

        self.assertEqual(queue.empty(), True)
        self.assertEqual(queue.full(), False)

        proc.join()

    def _test_get(self, queue, child_can_start, parent_can_continue):
        child_can_start.wait()
        queue.put(1)
        queue.put(2)
        if self.TYPE == 'processes':
            queue.putmany([3, 4, 5])
        else:
            queue.put(3)
            queue.put(4)
            queue.put(5)
        parent_can_continue.set()
        
    def test_get(self):
        queue = self.Queue()
        child_can_start = self.Event()
        parent_can_continue = self.Event()
        
        proc = self.Process(
            target=self._test_get,
            args=(queue, child_can_start, parent_can_continue)
            )
        proc.setDaemon(True)
        proc.start()
        
        self.assertEqual(queue.empty(), True)
        
        child_can_start.set()
        parent_can_continue.wait()

        time.sleep(DELTA)
        self.assertEqual(queue.empty(), False)

        self.assertEqual(queue.get(), 1)
        self.assertEqual(queue.get(True, None), 2)
        self.assertEqual(queue.get(True), 3)
        self.assertEqual(queue.get(timeout=1), 4)
        self.assertEqual(queue.get_nowait(), 5)
        
        self.assertEqual(queue.empty(), True)

        get = TimingWrapper(queue.get)
        get_nowait = TimingWrapper(queue.get_nowait)
        
        self.assertRaises(Queue.Empty, get, False)
        self.assertTimingAlmostEqual(get.elapsed, 0)

        self.assertRaises(Queue.Empty, get, False, None)
        self.assertTimingAlmostEqual(get.elapsed, 0)

        self.assertRaises(Queue.Empty, get_nowait)
        self.assertTimingAlmostEqual(get_nowait.elapsed, 0)

        self.assertRaises(Queue.Empty, get, True, TIMEOUT1)
        self.assertTimingAlmostEqual(get.elapsed, TIMEOUT1)

        self.assertRaises(Queue.Empty, get, False, TIMEOUT2)
        self.assertTimingAlmostEqual(get.elapsed, 0)

        self.assertRaises(Queue.Empty, get, timeout=TIMEOUT3)
        self.assertTimingAlmostEqual(get.elapsed, TIMEOUT3)

        proc.join()
        
    def _test_fork(self, queue):
        for i in range(10, 20):
            queue.put(i)
        # note that at this point the items may only be buffered, so the
        # process cannot shutdown until the feeder thread has finished
        # pushing items onto the pipe.

    def test_fork(self):
        # Old versions of Queue would fail to create a new feeder
        # thread for a forked process if the original process had its
        # own feeder thread.  This test checks that this no longer
        # happens.

        queue = self.Queue()

        # put items on queue so that main process starts a feeder thread
        for i in range(10):
            queue.put(i)

        # wait to make sure thread starts before we fork a new process
        time.sleep(DELTA)

        # fork process
        p = self.Process(target=self._test_fork, args=(queue,))
        p.start()

        # check that all expected items are in the queue
        for i in range(20):
            self.assertEqual(queue.get(), i)
        self.assertRaises(Queue.Empty, queue.get, False)

        p.join()

#
#
#

class _TestLock(BaseTestCase):

    def test_lock(self):
        lock = self.Lock()
        self.assertEqual(lock.acquire(), True)
        self.assertEqual(lock.acquire(False), False)
        self.assertEqual(lock.release(), None)
        self.assertRaises((ValueError, threading.ThreadError), lock.release)

    def test_rlock(self):
        lock = self.RLock()
        self.assertEqual(lock.acquire(), True)
        self.assertEqual(lock.acquire(), True)
        self.assertEqual(lock.acquire(), True)
        self.assertEqual(lock.release(), None)
        self.assertEqual(lock.release(), None)
        self.assertEqual(lock.release(), None)
        self.assertRaises((AssertionError, RuntimeError), lock.release)
        
        
class _TestSemaphore(BaseTestCase):

    def _test_semaphore(self, sem):
        self.assertReturnsIfImplemented(2, getValue, sem)
        self.assertEqual(sem.acquire(), True)
        self.assertReturnsIfImplemented(1, getValue, sem)
        self.assertEqual(sem.acquire(), True)
        self.assertReturnsIfImplemented(0, getValue, sem)
        self.assertEqual(sem.acquire(False), False)
        self.assertReturnsIfImplemented(0, getValue, sem)
        self.assertEqual(sem.release(), None)
        self.assertReturnsIfImplemented(1, getValue, sem)
        self.assertEqual(sem.release(), None)
        self.assertReturnsIfImplemented(2, getValue, sem)
        
    def test_semaphore(self):
        sem = self.Semaphore(2)
        self._test_semaphore(sem)
        self.assertEqual(sem.release(), None)
        self.assertReturnsIfImplemented(3, getValue, sem)
        self.assertEqual(sem.release(), None)
        self.assertReturnsIfImplemented(4, getValue, sem)

    def test_bounded_semaphore(self):
        sem = self.BoundedSemaphore(2)
        self._test_semaphore(sem)
        if HAVE_GETVALUE:
            self.assertRaises(ValueError, sem.release)
            self.assertReturnsIfImplemented(2, getValue, sem)

    def test_timeout(self):
        if self.TYPE != 'processes':
            return

        sem = self.Semaphore(0)
        acquire = TimingWrapper(sem.acquire)

        self.assertEqual(acquire(False), False)
        self.assertTimingAlmostEqual(acquire.elapsed, 0.0)

        self.assertEqual(acquire(False, None), False)
        self.assertTimingAlmostEqual(acquire.elapsed, 0.0)

        self.assertEqual(acquire(False, TIMEOUT1), False)
        self.assertTimingAlmostEqual(acquire.elapsed, 0)

        self.assertEqual(acquire(True, TIMEOUT2), False)
        self.assertTimingAlmostEqual(acquire.elapsed, TIMEOUT2)

        self.assertEqual(acquire(timeout=TIMEOUT3), False)
        self.assertTimingAlmostEqual(acquire.elapsed, TIMEOUT3)


class _TestCondition(BaseTestCase):
    
    def f(self, cond, sleeping, woken, timeout=None):
        cond.acquire()
        sleeping.release()
        cond.wait(timeout)
        woken.release()
        cond.release()
    
    def check_invariant(self, cond):
        # this is only supposed to succeed when there are no sleepers
        if self.TYPE == 'processes':
            try:
                sleepers = (cond._sleeping_count.getValue() -
                            cond._woken_count.getValue())
                self.assertEqual(sleepers, 0)
                self.assertEqual(cond._wait_semaphore.getValue(), 0)
            except NotImplementedError:
                pass
            
    def test_notify(self):
        cond = self.Condition()
        sleeping = self.Semaphore(0)
        woken = self.Semaphore(0)
        
        p = self.Process(target=self.f, args=(cond, sleeping, woken))
        p.setDaemon(True)
        p.start()

        p = threading.Thread(target=self.f, args=(cond, sleeping, woken))
        p.setDaemon(True)
        p.start()
        
        # wait for both children to start sleeping
        sleeping.acquire()
        sleeping.acquire()
        
        # check no process/thread has woken up
        time.sleep(DELTA)
        self.assertReturnsIfImplemented(0, getValue, woken)

        # wake up one process/thread
        cond.acquire()
        cond.notify()
        cond.release()
        
        # check one process/thread has woken up
        time.sleep(DELTA)
        self.assertReturnsIfImplemented(1, getValue, woken)

        # wake up another
        cond.acquire()
        cond.notify()
        cond.release()
        
        # check other has woken up
        time.sleep(DELTA)
        self.assertReturnsIfImplemented(2, getValue, woken)
        
        # check state is not mucked up
        self.check_invariant(cond)
        p.join()
        
    def test_notifyAll(self):
        cond = self.Condition()
        sleeping = self.Semaphore(0)
        woken = self.Semaphore(0)

        # start some threads/processes which will timeout
        for i in range(3):
            p = self.Process(target=self.f,
                             args=(cond, sleeping, woken, TIMEOUT1))
            p.setDaemon(True)
            p.start()

            t = threading.Thread(target=self.f,
                                 args=(cond, sleeping, woken, TIMEOUT1))
            t.setDaemon(True)
            t.start()

        # wait for them all to sleep
        for i in xrange(6):
            sleeping.acquire()

        # check they have all timed out
        for i in xrange(6):
            woken.acquire()
        self.assertReturnsIfImplemented(0, getValue, woken)

        # check state is not mucked up
        self.check_invariant(cond)

        # start some more threads/processes
        for i in range(3):
            p = self.Process(target=self.f, args=(cond, sleeping, woken))
            p.setDaemon(True)
            p.start()
            
            t = threading.Thread(target=self.f, args=(cond, sleeping, woken))
            t.setDaemon(True)
            t.start()
            
        # wait for them to all sleep
        for i in xrange(6):
            sleeping.acquire()
            
        # check no process/thread has woken up
        time.sleep(DELTA)
        self.assertReturnsIfImplemented(0, getValue, woken)

        # wake them all up
        cond.acquire()
        cond.notifyAll()
        cond.release()

        # check they have all woken
        time.sleep(DELTA)
        self.assertReturnsIfImplemented(6, getValue, woken)

        # check state is not mucked up
        self.check_invariant(cond)

    def test_timeout(self):
        cond = self.Condition()
        wait = TimingWrapper(cond.wait)
        cond.acquire()
        res = wait(TIMEOUT1)
        cond.release()
        self.assertEqual(res, None)
        self.assertTimingAlmostEqual(wait.elapsed, TIMEOUT1)

        
class _TestEvent(BaseTestCase):

    def _test_event(self, event):
        time.sleep(TIMEOUT2)
        event.set()

    def test_event(self):
        event = self.Event()
        wait = TimingWrapper(event.wait)

        self.assertEqual(event.isSet(), False)
        self.assertEqual(wait(0.0), None)
        self.assertTimingAlmostEqual(wait.elapsed, 0.0)
        self.assertEqual(wait(TIMEOUT1), None)
        self.assertTimingAlmostEqual(wait.elapsed, TIMEOUT1)

        event.set()

        self.assertEqual(event.isSet(), True)
        self.assertEqual(wait(), None)
        self.assertTimingAlmostEqual(wait.elapsed, 0.0)
        self.assertEqual(wait(TIMEOUT1), None)
        self.assertTimingAlmostEqual(wait.elapsed, 0.0)
        self.assertEqual(event.isSet(), True)

        event.clear()

        self.assertEqual(event.isSet(), False)

        self.Process(target=self._test_event, args=(event,)).start()
        self.assertEqual(wait(), None)

#
#
#

class _TestValue(BaseTestCase):

    codes_values = [
        ('i', 4343, 24234),
        ('d', 3.625, -4.25),
        ('h', -232, 234),
        ('c', 'x', 'y'),
        ]

    def _test(self, values):
        for sv, cv in zip(values, self.codes_values):
            sv.value = cv[2]
        
    def test_sharedvalue(self, lock=False):
        values = [self.Value(code, value)
                  for code, value, _ in self.codes_values]

        for sv, cv in zip(values, self.codes_values):
            self.assertEqual(sv.value, cv[1])
        
        proc = self.Process(target=self._test, args=(values,))
        proc.start()
        proc.join()

        for sv, cv in zip(values, self.codes_values):
            self.assertEqual(sv.value, cv[2])

    def test_synchronized(self):
        self.test_sharedvalue(lock=True)

    def test_getobj_getlock(self):
        if self.TYPE != 'processes':
            return
        lock = self.Lock()
        obj = self.Value('i', 5, lock=lock)
        self.assertEqual(obj.getlock(), lock)
        self.assertEqual(obj.getobj().value, 5)


class _TestArray(BaseTestCase):

    def f(self, seq):
        for i in range(1, len(seq)):
            seq[i] += seq[i-1]

    def test_sharedarray(self, lock=False):
        seq = [680, 626, 934, 821, 150, 233, 548, 982, 714, 831]
        arr = self.Array('i', seq, lock=lock)
        
        self.assertEqual(len(arr), len(seq))
        self.assertEqual(arr[3], seq[3])
        self.assertEqual(list(arr[2:7]), list(seq[2:7]))
        
        arr[4:8] = seq[4:8] = array.array('i', [1, 2, 3, 4])
        
        self.assertEqual(list(arr), seq)
        
        self.f(seq)
        
        p = self.Process(target=self.f, args=(arr,))
        p.start()
        p.join()
        
        self.assertEqual(list(arr), list(seq))
        
    def test_synchronized(self):
        self.test_sharedarray(lock=True)
        
#
#
#

class _TestContainers(BaseTestCase):

    ALLOWED_TYPES = ('manager',)

    def test_list(self):
        a = self.list(range(10))
        self.assertEqual(a[:], range(10))
        
        b = self.list()
        self.assertEqual(b[:], [])
        
        b.extend(range(5))
        self.assertEqual(b[:], range(5))
        
        self.assertEqual(b[2], 2)
        self.assertEqual(b[2:10], [2,3,4])

        b *= 2
        self.assertEqual(b[:], [0, 1, 2, 3, 4, 0, 1, 2, 3, 4])

        self.assertEqual(b + [5, 6], [0, 1, 2, 3, 4, 0, 1, 2, 3, 4, 5, 6])

        self.assertEqual(a, self.list(range(10)))
        self.assertEqual(a, range(10))
        self.assertTrue(a != range(11))
        self.assertTrue(range(9) < a)
        self.assertTrue(a < range(11))

        d = [a, b]
        e = self.list(d)
        self.assertEqual(
            e, [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [0, 1, 2, 3, 4, 0, 1, 2, 3, 4]]
            )

        it = iter(a)
        self.assertEqual(tuple(it), (0, 1, 2, 3, 4, 5, 6, 7, 8, 9))
        
        f = self.list([a])
        a.append('hello')
        self.assertEqual(f, [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 'hello']])

    def test_dict(self):
        d = self.dict()
        for i in range(5):
            d[i] = chr(65 + i)
        self.assertEqual(
            d, {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E'}
            )
        self.assertEqual(list(d), range(5))
        self.assertEqual(
            list(d.iteritems()),
            [(0, 'A'), (1, 'B'), (2, 'C'), (3, 'D'), (4, 'E')]
            )
        
    def test_namespace(self):
        n = self.Namespace()
        n.name = 'Bob'
        n.job = 'Builder'
        self.assertEqual((n.name, n.job), ('Bob', 'Builder'))
        del n.job
        self.assertEqual(str(n), "Namespace(name='Bob')")
        self.assertTrue(hasattr(n, 'name'))
        self.assertTrue(not hasattr(n, 'job'))

#
#
#

def sqr(x, wait=0.0):
    time.sleep(wait)
    return x*x

class _TestPool(BaseTestCase):

    ALLOWED_TYPES = ('processes',)

    def test_apply(self):
        papply = self.pool.apply
        self.assertEqual(papply(sqr, (5,)), apply(sqr, (5,)))
        self.assertEqual(papply(sqr, (), {'x':3}), apply(sqr, (), {'x':3}))

    def test_map(self):
        pmap = self.pool.map
        self.assertEqual(pmap(sqr, range(10)), map(sqr, range(10)))
        self.assertEqual(pmap(sqr, range(100), chunksize=20),
                         map(sqr, range(100)))
        
    def test_async(self):
        res = self.pool.applyAsync(sqr, (7, TIMEOUT1,))
        get = TimingWrapper(res.get)
        self.assertEqual(get(), 49)
        self.assertTimingAlmostEqual(get.elapsed, TIMEOUT1)

    def test_async_timeout(self):
        res = self.pool.applyAsync(sqr, (6, 100))
        get = TimingWrapper(res.get)
        self.assertRaises(processing.TimeoutError, get, timeout=TIMEOUT2)
        self.assertTimingAlmostEqual(get.elapsed, TIMEOUT2)
        # One of the workers will be occupied a long time (probably
        # till the pool gets terminated), but there are other workers
        # so who cares.

    def test_imap(self):
        it = self.pool.imap(sqr, range(10))
        self.assertEqual(list(it), map(sqr, range(10)))

        it = self.pool.imap(sqr, range(10))
        for i in range(10):
            self.assertEqual(it.next(), i*i)
        self.assertRaises(StopIteration, it.next)

        it = self.pool.imap(sqr, range(1000), chunksize=100)
        for i in range(1000):
            self.assertEqual(it.next(), i*i)
        self.assertRaises(StopIteration, it.next)

    def test_imap_unordered(self):
        it = self.pool.imapUnordered(sqr, range(1000))
        self.assertEqual(sorted(it), map(sqr, range(1000)))

        it = self.pool.imapUnordered(sqr, range(1000), chunksize=53)
        self.assertEqual(sorted(it), map(sqr, range(1000)))

    def test_make_pool(self):
        p = processing.Pool(3)
        self.assertEqual(3, len(p._pool))

#
#
#

class _TestZZZDebugInfo(BaseTestCase):

    ALLOWED_TYPES = ('manager',)

    def test_debug_info(self):
        # this gets run after all the other tests for the manager
        # and it tests that there have been no reference leaks for
        # the managers shared objects
        debug = self._debugInfo()
        if debug:
            print debug
        self.assertTrue(not debug)

#
#
#

from processing.managers import (
    BaseManager, BaseProxy, CreatorMethod, RemoteError
    )
    
class FooBar(object):
    def f(self):
        return 'f()'
    def g(self):
        raise ValueError
    def _h(self):
        return '_h()'
    
def baz():
    for i in xrange(10):
        yield i*i

class IteratorProxy(BaseProxy):
    def __iter__(self):
        return self
    def next(self):
        return self._callMethod('next')

class MyManager(BaseManager):
    Foo = CreatorMethod(FooBar)
    Bar = CreatorMethod(FooBar, exposed=('f', '_h'))
    baz = CreatorMethod(baz, proxytype=IteratorProxy)


class _TestMyManager(BaseTestCase):
    
    ALLOWED_TYPES = ('manager',)

    def test_mymanager(self):
        manager = MyManager()
        manager.start()
        
        foo = manager.Foo()
        bar = manager.Bar()
        baz = manager.baz()
        
        foo_methods = [name for name in ('f', 'g', '_h') if hasattr(foo, name)]
        bar_methods = [name for name in ('f', 'g', '_h') if hasattr(bar, name)]
        
        self.assertEqual(foo_methods, ['f', 'g'])
        self.assertEqual(bar_methods, ['f', '_h'])
        
        self.assertEqual(foo.f(), 'f()')
        self.assertRaises(ValueError, foo.g)
        self.assertEqual(foo._callMethod('f'), 'f()')
        self.assertRaises(RemoteError, foo._callMethod, '_h')
        
        self.assertEqual(bar.f(), 'f()')
        self.assertEqual(bar._h(), '_h()')
        self.assertEqual(bar._callMethod('f'), 'f()')
        self.assertEqual(bar._callMethod('_h'), '_h()')
        
        self.assertEqual(list(baz), [i*i for i in range(10)])

        manager.shutdown()
        
#
#
#

_queue = Queue.Queue()

def get_queue():
    return _queue

class QueueManager(BaseManager):
    # manager class used by server process
    get_proxy = CreatorMethod(callable=get_queue, typeid='get_proxy')

class QueueManager2(BaseManager):
    # manager class which specifies the same interface as QueueManager
    get_proxy = CreatorMethod(typeid='get_proxy')


class _TestRemoteManager(BaseTestCase):

    ALLOWED_TYPES = ('manager',)
    
    def _putter(self, address):
        m2 = QueueManager2.fromAddress(address=address, authkey='none')
        queue = m2.get_proxy()
        queue.put('hello world')

    def test_remote(self):
        m = QueueManager(address=('localhost', 0), authkey='none')
        m.start()
        
        p = self.Process(target=self._putter, args=(m.address,))
        p.start()
        
        m2 = QueueManager2.fromAddress(address=m.address, authkey='none')
        queue = m2.get_proxy()
        self.assertEqual(queue.get(), 'hello world')
        
        # Since queue was not created using m it has no way of knowing
        # when the server process associated with m has been
        # finalized.  Therefore we should take care that queue is
        # finalized before m is finalized.  Otherwise the finalizer
        # for queue can hang for a few seconds (on Windows) while it
        # tries to contact the manager process (which is no longer
        # running) in order to decrement the reference count.
        del queue
        del m

#
#
#

class _TestConnection(BaseTestCase):

    ALLOWED_TYPES = ('processes', 'threads')

    def _echo(self, conn):
        for msg in iter(conn.recvBytes, ''):
            conn.sendBytes(msg)
        conn.close()

    def test_connection(self):
        conn, child_conn = self.Pipe()
        
        p = self.Process(target=self._echo, args=(child_conn,))
        p.setDaemon(True)
        p.start()

        seq = [1, 2.25, None]
        msg = 'hello world'
        longmsg = msg * 10
        arr = array.array('i', range(4))

        if self.TYPE == 'processes':
            self.assertEqual(type(conn.fileno()), int)

        self.assertEqual(conn.send(seq), None)
        self.assertEqual(conn.recv(), seq)

        self.assertEqual(conn.sendBytes(msg), None)
        self.assertEqual(conn.recvBytes(), msg)

        if self.TYPE == 'processes':
            buffer = array.array('i', [0]*10)
            expected = list(arr) + [0] * (10 - len(arr))
            self.assertEqual(conn.sendBytes(arr), None)
            self.assertEqual(conn.recvBytesInto(buffer),
                             len(arr) * buffer.itemsize)
            self.assertEqual(list(buffer), expected)

            buffer = array.array('i', [0]*10)
            expected = [0] * 3 + list(arr) + [0] * (10 - 3 - len(arr))
            self.assertEqual(conn.sendBytes(arr), None)
            self.assertEqual(conn.recvBytesInto(buffer, 3 * buffer.itemsize),
                             len(arr) * buffer.itemsize)
            self.assertEqual(list(buffer), expected)

            buffer = array.array('c', ' ' * 40)
            self.assertEqual(conn.sendBytes(longmsg), None)
            try:
                res = conn.recvBytesInto(buffer)
            except processing.BufferTooShort, e:
                self.assertEqual(e.args, (longmsg,))
            else:
                self.fail('expected BufferTooShort, got %s' % res)

        poll = TimingWrapper(conn.poll)

        self.assertEqual(poll(), False)
        self.assertTimingAlmostEqual(poll.elapsed, 0)

        self.assertEqual(poll(TIMEOUT1), False)
        self.assertTimingAlmostEqual(poll.elapsed, TIMEOUT1)

        conn.send(None)

        self.assertEqual(poll(TIMEOUT1), True)
        self.assertTimingAlmostEqual(poll.elapsed, 0)
        
        self.assertEqual(conn.recv(), None)

        really_big_msg = 'X' * (1024 * 1024 * 16)       # 16 megabytes
        conn.sendBytes(really_big_msg)
        self.assertEqual(conn.recvBytes(), really_big_msg)
        
        conn.sendBytes('')                              # tell child to quit
        child_conn.close()

        if self.TYPE == 'processes':
            self.assertRaises(EOFError, conn.recv)
            self.assertRaises(EOFError, conn.recvBytes)

        p.join()
        
    def test_duplex_false(self):
        reader, writer = self.Pipe(duplex=False)
        self.assertEqual(writer.send(1), None)
        self.assertEqual(reader.recv(), 1)
        if self.TYPE == 'processes':
            self.assertRaises(IOError, writer.recv)
            self.assertRaises(IOError, reader.send, 2)

    def test_spawn_close(self):
        # We test that a pipe connection can be closed by parent
        # process immediately after child is spawned.  On Windows this
        # would have sometimes failed on old versions because
        # child_conn would be closed before the child got a chance to
        # duplicate it.
        conn, child_conn = self.Pipe()
        
        p = self.Process(target=self._echo, args=(child_conn,))
        p.start()
        child_conn.close()    # this might complete before child initializes
        
        conn.sendBytes('hello')
        self.assertEqual(conn.recvBytes(), 'hello')

        conn.sendBytes('')
        conn.close()
        p.join()


class _TestListenerClient(BaseTestCase):

    ALLOWED_TYPES = ('processes', 'threads')

    def _test(self, address):
        conn = self.connection.Client(address)
        conn.send('hello')
        conn.close()

    def test_listener_client(self):        
        for family in self.connection.families:
            l = self.connection.Listener(family=family)
            p = self.Process(target=self._test, args=(l.address,))
            p.setDaemon(True)
            p.start()
            conn = l.accept()
            self.assertEqual(conn.recv(), 'hello')
            p.join()
            l.close()


class _TestPicklingConnections(BaseTestCase):

    ALLOWED_TYPES = ('processes', 'threads')

    def _listener(self, conn, families):
        for fam in families:
            l = self.connection.Listener(family=fam)
            conn.send(l.address)
            new_conn = l.accept()
            conn.send(new_conn)

        if self.TYPE == 'processes':
            l = socket.socket()
            l.bind(('localhost', 0))
            conn.send(l.getsockname())
            l.listen(1)
            new_conn, addr = l.accept()
            conn.send(new_conn)
        
        conn.recv()

    def _remote(self, conn):
        for (address, msg) in iter(conn.recv, None):
            client = self.connection.Client(address)
            client.send(msg.upper())
            client.close()

        if self.TYPE == 'processes':
            address, msg = conn.recv()
            client = socket.socket()
            client.connect(address)
            client.sendall(msg.upper())
            client.close()

        conn.close()

    def test_pickling(self):
        if not self.connection.connections_are_picklable:
            return
        
        families = self.connection.families

        lconn, lconn0 = self.Pipe()
        lp = self.Process(target=self._listener, args=(lconn0, families))
        lp.start()
        lconn0.close()

        rconn, rconn0 = self.Pipe()
        rp = self.Process(target=self._remote, args=(rconn0,))
        rp.start()
        rconn0.close()

        for fam in families:
            msg = 'This connection uses family %s' % fam
            address = lconn.recv()
            rconn.send((address, msg))
            new_conn = lconn.recv()
            self.assertEqual(new_conn.recv(), msg.upper())
            
        rconn.send(None)

        if self.TYPE == 'processes':
            msg = 'This connection uses a normal socket'
            address = lconn.recv()
            rconn.send((address, msg))
            new_conn = lconn.recv()
            self.assertEqual(new_conn.recv(100), msg.upper())

        lconn.send(None)

        rconn.close()
        lconn.close()

        lp.join()
        rp.join()

#
#
#

class _TestHeap(BaseTestCase):

    ALLOWED_TYPES = ('processes',)

    def test_heap(self):
        iterations = 5000
        maxblocks = 50
        blocks = []

        # create and destroy lots of blocks of different sizes
        for i in xrange(iterations):
            size = int(random.lognormvariate(0, 1) * 1000)
            b = processing.heap.BufferWrapper(size)
            blocks.append(b)
            if len(blocks) > maxblocks:
                i = random.randrange(maxblocks)
                del blocks[i]

        # get the heap object
        heap = processing.heap.BufferWrapper._heap

        # verify the state of the heap
        all = []
        occupied = 0
        for L in heap._len_to_seq.values():
            for arena, start, stop in L:
                all.append((heap._arenas.index(arena), start, stop,
                            stop-start, 'free'))
        for arena, start, stop in heap._allocated_blocks:
            all.append((heap._arenas.index(arena), start, stop,
                        stop-start, 'occupied'))
            occupied += (stop-start)

        all.sort()

        for i in range(len(all)-1):
            (arena, start, stop) = all[i][:3]
            (narena, nstart, nstop) = all[i+1][:3]
            self.assertTrue((arena != narena and nstart == 0) or
                            (stop == nstart))
            
#
#
#

class _Foo(ctypes.Structure):
    _fields_ = [
        ('x', ctypes.c_int),
        ('y', ctypes.c_double)
        ]

class _TestSharedCTypes(BaseTestCase):

    ALLOWED_TYPES = ('processes',)

    def _double(self, x, y, foo, arr, string):
        x.value *= 2
        y.value *= 2
        foo.x *= 2
        foo.y *= 2
        string.value *= 2
        for i in range(len(arr)):
            arr[i] *= 2

    def test_sharedctypes(self, lock=False):
        from processing.sharedctypes import Value, Array
        
        x = Value('i', 7, lock=lock)
        y = Value(ctypes.c_double, 1.0/3.0, lock=lock)
        foo = Value(_Foo, 3, 2, lock=lock)
        arr = Array('d', range(10), lock=lock)
        string = Array('c', 20, lock=lock)
        string.value = 'hello'

        p = self.Process(target=self._double, args=(x, y, foo, arr, string))
        p.start()
        p.join()

        self.assertEqual(x.value, 14)
        self.assertAlmostEqual(y.value, 2.0/3.0)
        self.assertEqual(foo.x, 6)
        self.assertAlmostEqual(foo.y, 4.0)
        for i in range(10):
            self.assertAlmostEqual(arr[i], i*2)
        self.assertEqual(string.value, 'hellohello')

    def test_synchronize(self):
        self.test_sharedctypes(lock=True)

    def test_copy(self):
        from processing.sharedctypes import Value, copy
        foo = _Foo(2, 5.0)
        bar = copy(foo)
        foo.x = 0
        foo.y = 0
        self.assertEqual(bar.x, 2)
        self.assertAlmostEqual(bar.y, 5.0)

#
#
#

class _TestFinalize(BaseTestCase):

    ALLOWED_TYPES = ('processes',)

    def _test_finalize(self, conn):
        from processing.finalize import Finalize
        from processing.process import _exitFunction

        class Foo(object):
            pass

        a = Foo()
        Finalize(a, conn.send, args=('a',))
        del a           # triggers callback for a

        b = Foo()
        close_b = Finalize(b, conn.send, args=('b',))    
        close_b()       # triggers callback for b
        close_b()       # does nothing because callback has already been called
        del b           # does nothing because callback has already been called

        c = Foo()
        Finalize(c, conn.send, args=('c',))

        d10 = Foo()
        Finalize(d10, conn.send, args=('d10',), exitpriority=1)

        d01 = Foo()
        Finalize(d01, conn.send, args=('d01',), exitpriority=0)
        d02 = Foo()
        Finalize(d02, conn.send, args=('d02',), exitpriority=0)
        d03 = Foo()
        Finalize(d03, conn.send, args=('d03',), exitpriority=0)

        Finalize(None, conn.send, args=('STOP',), exitpriority=-100)

        # call processing's cleanup function then exit process without
        # garbage collecting locals
        _exitFunction()
        conn.close()
        os._exit(0)

    def test_finalize(self):
        conn, child_conn = self.Pipe()
        
        p = self.Process(target=self._test_finalize, args=(child_conn,))
        p.start()
        p.join()

        result = [obj for obj in iter(conn.recv, 'STOP')]
        self.assertEqual(result, ['a', 'b', 'd10', 'd03', 'd02', 'd01'])

#
# Test that from ... import * works for each module
#

class _TestImportStar(BaseTestCase):

    ALLOWED_TYPES = ('processes',)

    def test_import(self):
        modules = (
            'processing', 'processing.connection',
            'processing.finalize', 'processing.forking',
            'processing.heap', 'processing.logger',
            'processing.managers', 'processing.pool',
            'processing.process', 'processing.reduction',
            'processing.sharedctypes', 'processing.synchronize'
            )
        
        for name in modules:
            __import__(name)
            mod = sys.modules[name]
            
            for attr in getattr(mod, '__all__', ()):
                self.assertTrue(
                    hasattr(mod, attr),
                    '%r does not have attribute %r' % (mod, attr)
                    )

#
# Quick test that logging works -- does not test logging output
#

class _TestLogging(BaseTestCase):

    ALLOWED_TYPES = ('processes',)

    def test_enable_logging(self):
        processing.enableLogging(level=processing.SUBWARNING)
        logger = processing.getLogger()
        self.assertTrue(logger is not None)
        logger.debug('this will not be printed')
        logger.info('nor will this')

    def _test_level(self, conn):
        logger = processing.getLogger()
        conn.send(logger.getEffectiveLevel())

    def test_level(self):
        LEVEL1 = 32
        LEVEL2 = 37
        LEVEL3 = 41
        reader, writer = processing.Pipe(duplex=False)
        root_logger = logging.getLogger('')

        processing.enableLogging(level=LEVEL1)
        self.Process(target=self._test_level, args=(writer,)).start()
        self.assertEqual(LEVEL1, reader.recv())

        processing.getLogger().setLevel(LEVEL2)
        self.Process(target=self._test_level, args=(writer,)).start()
        self.assertEqual(LEVEL2, reader.recv())

        self.assertEqual(processing.NOTSET, logging.NOTSET)
        processing.enableLogging(level=logging.NOTSET)
        root_logger.setLevel(LEVEL3)
        self.Process(target=self._test_level, args=(writer,)).start()
        self.assertEqual(LEVEL3, reader.recv())

        processing.enableLogging(level=processing.SUBWARNING)

#
# Functions used to create test cases from the base ones in this module
#

def get_attributes(Source, names):
    d = {}
    for name in names:
        obj = getattr(Source, name)
        if type(obj) == type(get_attributes):
            obj = staticmethod(obj)
        d[name] = obj
    return d

def create_test_cases(Mixin, type):
    result = {}
    glob = globals()
    Type = type[0].upper() + type[1:]

    for name in glob.keys():
        if name.startswith('_Test'):
            base = glob[name]
            if type in base.ALLOWED_TYPES:
                newname = 'With' + Type + name[1:]
                class Temp(base, unittest.TestCase, Mixin):
                    pass
                result[newname] = Temp
                Temp.__name__ = newname
                Temp.__module__ = Mixin.__module__
    return result

#
# Create test cases
#

class ProcessesMixin(object):
    TYPE = 'processes'
    Process = processing.Process
    locals().update(get_attributes(processing, (
        'Queue', 'Lock', 'RLock', 'Semaphore', 'BoundedSemaphore',
        'Condition', 'Event', 'Value', 'Array',
        'currentProcess', 'activeChildren', 'Pipe', 'connection'
        )))

testcases_processes = create_test_cases(ProcessesMixin, type='processes')
globals().update(testcases_processes)


class ManagerMixin(object):
    TYPE = 'manager'
    Process = processing.Process
    manager = object.__new__(processing.managers.SyncManager)
    locals().update(get_attributes(manager, (
        'Queue', 'Lock', 'RLock', 'Semaphore', 'BoundedSemaphore',
        'Condition', 'Event', 'Value', 'Array', 'list', 'dict',
        'Namespace', '_debugInfo'
        )))

testcases_manager = create_test_cases(ManagerMixin, type='manager')
globals().update(testcases_manager)


class ThreadsMixin(object):
    TYPE = 'threads'
    Process = processing.dummy.Process
    locals().update(get_attributes(processing.dummy, (
        'Queue', 'Lock', 'RLock', 'Semaphore', 'BoundedSemaphore',
        'Condition', 'Event', 'Value', 'Array', 'currentProcess',
        'activeChildren', 'Pipe', 'connection', 'dict', 'list',
        'Namespace'
        )))

testcases_threads = create_test_cases(ThreadsMixin, type='threads')
globals().update(testcases_threads)

#
#
#

def test_main(run=None):
    if run is None:
        from test.test_support import run_suite as run

    ProcessesMixin.pool = processing.Pool(4)
    ManagerMixin.manager.__init__()
    ManagerMixin.manager.start()

    testcases = (
        sorted(testcases_processes.values(), key=lambda tc:tc.__name__) +
        sorted(testcases_threads.values(), key=lambda tc:tc.__name__) +
        sorted(testcases_manager.values(), key=lambda tc:tc.__name__)
        )

    loadTestsFromTestCase = unittest.defaultTestLoader.loadTestsFromTestCase
    suite = unittest.TestSuite(loadTestsFromTestCase(tc) for tc in testcases)
    run(suite)
    
    ManagerMixin.manager.shutdown()
    ProcessesMixin.pool.terminate()
    del ProcessesMixin.pool

def main():
    test_main(unittest.TextTestRunner(verbosity=2).run)

if __name__ == '__main__':
    main()
