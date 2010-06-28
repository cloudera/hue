import os
import random
import time
import unittest
from beaker.container import *
from beaker.synchronization import _synchronizers
from beaker.cache import clsmap
import thread

def create(delay=0):
    global baton, totalcreates
    assert baton is None, "baton is not none , ident %r, this thread %r" % (baton, thread.get_ident())

    baton = thread.get_ident()
    try:    
        obj = object()
        time.sleep(delay)
        totalcreates += 1
        return obj
    finally:
        baton = None
        
def runthread(cls, id, runningids, value, delay, kwargs):
    print "create thread %d starting" % id
    runningids.add(id)

    try:
        if not value:
            expiretime = kwargs.pop('expiretime', None)
            starttime = kwargs.pop('starttime', None)
            value = Value('test', cls('test', **kwargs), createfunc=lambda:create(delay), expiretime=expiretime, starttime=starttime)
            
        global running, totalgets
        try:
            while running:
                item = value.get_value()
                assert item is not None
                item = None
                totalgets += 1
                time.sleep(random.random() * .00001)
        except:
            running = False
            raise
    finally:
        print "create thread %d exiting" % id
        runningids.remove(id)

def _runtest(cls, totaltime, expiretime, delay, threadlocal):
    print "\ntesting %s for %d secs with expiretime %s delay %d" % (
        cls, totaltime, expiretime, delay)

    global running, starttime, baton, totalcreates, totalgets
    
    running = False
    starttime = time.time()
    baton = None

    runningids = set()
    totalcreates = 0

    totalgets = 0
    
    kwargs = dict(
        expiretime=expiretime, 
        starttime = starttime,
        data_dir='./cache'
        )
    
    if not threadlocal:
        expiretime = kwargs.pop('expiretime', None)
        starttime = kwargs.pop('starttime', None)
        value = Value('test', cls('test', **kwargs), createfunc=lambda:create(delay), expiretime=expiretime, starttime=starttime)
        value.clear_value()
    else:
        value = None
        
    running = True    
    for t in range(1, 20):
        thread.start_new_thread(runthread, (cls, t, runningids, value, delay, kwargs))
        
    time.sleep(totaltime)
    
    failed = not running

    running = False

    while runningids:
        time.sleep(1)

    assert not failed

    print "total object creates %d" % totalcreates
    print "total object gets %d" % totalgets
    
    if expiretime is None:
        assert totalcreates == 1
    else:
        assert abs(totaltime / expiretime - totalcreates) <= 2

def test_memory_container(totaltime=10, expiretime=None, delay=0, threadlocal=False):
    _runtest(clsmap['memory'],
                  totaltime, expiretime, delay, threadlocal)

def test_dbm_container(totaltime=10, expiretime=None, delay=0):
    _runtest(clsmap['dbm'], totaltime, expiretime, delay, False)

def test_file_container(totaltime=10, expiretime=None, delay=0, threadlocal=False):
    _runtest(clsmap['file'], totaltime, expiretime, delay, threadlocal)

def test_memory_container_tlocal():
    test_memory_container(expiretime=5, delay=2, threadlocal=True)
    
def test_memory_container_2():
    test_memory_container(expiretime=2)

def test_memory_container_3():
    test_memory_container(expiretime=5, delay=2)

def test_dbm_container_2():
    test_dbm_container(expiretime=2)

def test_dbm_container_3():
    test_dbm_container(expiretime=5, delay=2)

def test_file_container_2():
    test_file_container(expiretime=2)
    
def test_file_container_3():
    test_file_container(expiretime=5, delay=2)

def test_file_container_tlocal():
    test_file_container(expiretime=5, delay=2, threadlocal=True)

def test_file_open_bug():
    """ensure errors raised during reads or writes don't lock the namespace open."""
    
    value = Value('test', clsmap['file']('reentrant_test', data_dir='./cache'))
    if os.path.exists(value.namespace.file):
        os.remove(value.namespace.file)
    
    value.set_value("x")

    f = open(value.namespace.file, 'w')
    f.write("BLAH BLAH BLAH")
    f.close()
    
    # TODO: do we have an assertRaises() in nose to use here ?
    try:
        value.set_value("y")
        assert False
    except:
        pass
        
    _synchronizers.clear()

    value = Value('test', clsmap['file']('reentrant_test', data_dir='./cache'))

    # TODO: do we have an assertRaises() in nose to use here ?
    try:
        value.set_value("z")
        assert False
    except:
        pass


def test_removing_file_refreshes():
    """test that the cache doesn't ignore file removals"""
    
    x = [0]
    def create():
        x[0] += 1
        return x[0]
        
    value = Value('test', clsmap['file']('refresh_test', data_dir='./cache'), createfunc=create, starttime=time.time())
    if os.path.exists(value.namespace.file):
        os.remove(value.namespace.file)
    assert value.get_value() == 1
    assert value.get_value() == 1
    os.remove(value.namespace.file)
    assert value.get_value() == 2
