#
# Simple benchmarks for the processing package
#

import time, sys, processing, threading, Queue, gc

if sys.platform == 'win32':
    _timer = time.clock
else:
    _timer = time.time

delta = 1


#### TEST_QUEUESPEED

def queuespeed_func(q, c, iterations):
    a = '0' * 256
    c.acquire()
    c.notify()
    c.release()

    for i in xrange(iterations):
        q.put(a)
#    q.putMany((a for i in xrange(iterations))

    q.put('STOP')

def test_queuespeed(Process, q, c):
    elapsed = 0
    iterations = 1

    while elapsed < delta:
        iterations *= 2

        p = Process(target=queuespeed_func, args=(q, c, iterations))
        c.acquire()
        p.start()
        c.wait()
        c.release()

        result = None
        t = _timer()

        while result != 'STOP':
            result = q.get()

        elapsed = _timer() - t

        p.join()

    print iterations, 'objects passed through the queue in', elapsed, 'seconds'
    print 'average number/sec:', iterations/elapsed


#### TEST_PIPESPEED

def pipe_func(c, cond, iterations):
    a = '0' * 256
    cond.acquire()
    cond.notify()
    cond.release()

    for i in xrange(iterations):
        c.send(a)

    c.send('STOP')

def test_pipespeed():
    c, d = processing.Pipe()
    cond = processing.Condition()
    elapsed = 0
    iterations = 1

    while elapsed < delta:
        iterations *= 2

        p = processing.Process(target=pipe_func, args=(d, cond, iterations))
        cond.acquire()
        p.start()
        cond.wait()
        cond.release()

        result = None
        t = _timer()

        while result != 'STOP':
            result = c.recv()

        elapsed = _timer() - t
        p.join()

    print iterations, 'objects passed through connection in',elapsed,'seconds'
    print 'average number/sec:', iterations/elapsed


#### TEST_SEQSPEED

def test_seqspeed(seq):
    elapsed = 0
    iterations = 1

    while elapsed < delta:
        iterations *= 2

        t = _timer()

        for i in xrange(iterations):
            a = seq[5]

        elapsed = _timer()-t

    print iterations, 'iterations in', elapsed, 'seconds'
    print 'average number/sec:', iterations/elapsed


#### TEST_LOCK

def test_lockspeed(l):
    elapsed = 0
    iterations = 1

    while elapsed < delta:
        iterations *= 2

        t = _timer()

        for i in xrange(iterations):
            l.acquire()
            l.release()

        elapsed = _timer()-t

    print iterations, 'iterations in', elapsed, 'seconds'
    print 'average number/sec:', iterations/elapsed


#### TEST_CONDITION

def conditionspeed_func(c, N):
    c.acquire()
    c.notify()

    for i in xrange(N):
        c.wait()
        c.notify()

    c.release()

def test_conditionspeed(Process, c):
    elapsed = 0
    iterations = 1

    while elapsed < delta:
        iterations *= 2

        c.acquire()
        p = Process(target=conditionspeed_func, args=(c, iterations))
        p.start()

        c.wait()

        t = _timer()

        for i in xrange(iterations):
            c.notify()
            c.wait()

        elapsed = _timer()-t

        c.release()
        p.join()

    print iterations * 2, 'waits in', elapsed, 'seconds'
    print 'average number/sec:', iterations * 2 / elapsed

####

def test():
    manager = processing.Manager()
    
    gc.disable()
    
    print '\n\t######## testing Queue.Queue\n'
    test_queuespeed(threading.Thread, Queue.Queue(),
                    threading.Condition())
    print '\n\t######## testing processing.Queue\n'
    test_queuespeed(processing.Process, processing.Queue(),
                    processing.Condition())
    print '\n\t######## testing Queue managed by server process\n'
    test_queuespeed(processing.Process, manager.Queue(),
                    manager.Condition())
    print '\n\t######## testing processing.Pipe\n'
    test_pipespeed()
    
    print
    
    print '\n\t######## testing list\n'
    test_seqspeed(range(10))
    print '\n\t######## testing list managed by server process\n'
    test_seqspeed(manager.list(range(10)))
    print '\n\t######## testing Array("i", ..., lock=False)\n'
    test_seqspeed(processing.Array('i', range(10), lock=False))
    print '\n\t######## testing Array("i", ..., lock=True)\n'
    test_seqspeed(processing.Array('i', range(10), lock=True))

    print

    print '\n\t######## testing threading.Lock\n'
    test_lockspeed(threading.Lock())
    print '\n\t######## testing threading.RLock\n'
    test_lockspeed(threading.RLock())
    print '\n\t######## testing processing.Lock\n'
    test_lockspeed(processing.Lock())
    print '\n\t######## testing processing.RLock\n'
    test_lockspeed(processing.RLock())
    print '\n\t######## testing lock managed by server process\n'
    test_lockspeed(manager.Lock())
    print '\n\t######## testing rlock managed by server process\n'
    test_lockspeed(manager.RLock())

    print

    print '\n\t######## testing threading.Condition\n'
    test_conditionspeed(threading.Thread, threading.Condition())
    print '\n\t######## testing processing.Condition\n'
    test_conditionspeed(processing.Process, processing.Condition())
    print '\n\t######## testing condition managed by a server process\n'
    test_conditionspeed(processing.Process, manager.Condition())

    gc.enable()

if __name__ == '__main__':
    processing.freezeSupport()
    test()
