from beaker.util import SyncDict, WeakValuedRegistry
import gc, random, sys, time, weakref

# this script tests SyncDict for its thread safety, 
# ability to always return a value even for a dictionary 
# that loses data randomly,  and
# insures that when used as a registry, only one instance
# of a particular key/value exists at any one time.

import thread
    
jython = sys.platform.startswith('java')

def collect():
    """The tests assume CPython GC behavior in regard to weakrefs, but
    we can coerce Jython into passing by triggering GC when we expect
    it to have happened on CPython
    """
    if jython:
        gc.collect()


class item:
    
    def __init__(self, id):
        self.id = id
        
    def __str__(self):
        return "item id %d" % self.id

# keep running indicator
running = False

# one item is referenced at a time (to insure singleton pattern)
theitem = weakref.ref(item(0))

# creation func entrance detector to detect non-synchronized access
# to the create function
baton = None


def create(id):
    global baton
    assert baton is None, "baton is not none !"

    baton = True
    try:    
        global theitem
        collect()
        
        assert theitem() is None, "create %d old item is still referenced" % id
            
        i = item(id)
        theitem = weakref.ref(i)

        global totalcreates
        totalcreates += 1

        return i
    finally:
        baton = None
        
def threadtest(s, id, statusdict):
    print "create thread %d starting" % id
    statusdict[id] = True

    try:
        global running
        global totalgets
        try:
            while running:
                s.get('test', lambda: create(id))
                totalgets += 1
                time.sleep(random.random() * .00001)
        except:
            e = sys.exc_info()[0]
            running = False
            print e
    finally:
        print "create thread %d exiting" % id
        statusdict[id] = False

def runtest(s):

    statusdict = {}
    global totalcreates
    totalcreates = 0

    global totalremoves
    totalremoves = 0

    global totalgets
    totalgets = 0

    global running
    running = True    
    for t in range(1, 10):
        thread.start_new_thread(threadtest, (s, t, statusdict))
        
    time.sleep(1)
    
    for x in range (0,10):
        if not running:
            break
        print "Removing item"
        try: 
            del s['test']
            totalremoves += 1
        except KeyError:
            pass
        sleeptime = random.random() * .89
        time.sleep(sleeptime)

    failed = not running

    running = False

    pause = True
    while pause:
        time.sleep(1)    
        pause = False
        for v in statusdict.values():
            if v:
                pause = True
                break

    if failed:
        raise Exception("test failed")

    print "total object creates %d" % totalcreates
    print "total object gets %d" % totalgets
    print "total object removes %d" % totalremoves

    
def test_dict():
    # normal dictionary test, where we will remove the value
    # periodically. the number of creates should be equal to
    # the number of removes plus one.    
    collect()
    print "\ntesting with normal dict"
    runtest(SyncDict())

    assert(totalremoves + 1 == totalcreates)


def test_weakdict():
    collect()
    print "\ntesting with weak dict"
    runtest(WeakValuedRegistry())
