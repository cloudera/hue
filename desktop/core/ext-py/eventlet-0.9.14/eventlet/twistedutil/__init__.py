from eventlet.hubs import get_hub
from eventlet import spawn, getcurrent

def block_on(deferred):
    cur = [getcurrent()]
    synchronous = []
    def cb(value):
        if cur:
            if getcurrent() is cur[0]:
                synchronous.append((value, None))
            else:
                cur[0].switch(value)
        return value
    def eb(fail):
        if cur:
            if getcurrent() is cur[0]:
                synchronous.append((None, fail))
            else:
                fail.throwExceptionIntoGenerator(cur[0])
    deferred.addCallbacks(cb, eb)
    if synchronous:
        result, fail = synchronous[0]
        if fail is not None:
            fail.raiseException()
        return result
    try:
        return get_hub().switch()
    finally:
        del cur[0]

def _putResultInDeferred(deferred, f, args, kwargs):
    try:
        result = f(*args, **kwargs)
    except:
        from twisted.python import failure
        f = failure.Failure()
        deferred.errback(f)
    else:
        deferred.callback(result)

def deferToGreenThread(func, *args, **kwargs):
    from twisted.internet import defer
    d = defer.Deferred()
    spawn(_putResultInDeferred, d, func, args, kwargs)
    return d

def callInGreenThread(func, *args, **kwargs):
    return spawn(func, *args, **kwargs)


if __name__=='__main__':
    import sys
    try:
        num = int(sys.argv[1])
    except:
        sys.exit('Supply number of test as an argument, 0, 1, 2 or 3')
    from twisted.internet import reactor
    def test():
        print block_on(reactor.resolver.getHostByName('www.google.com'))
        print block_on(reactor.resolver.getHostByName('###'))
    if num==0:
        test()
    elif num==1:
        spawn(test)
        from eventlet.api import sleep
        print 'sleeping..'
        sleep(5)
        print 'done sleeping..'
    elif num==2:
        from eventlet.twistedutil import join_reactor
        spawn(test)
        reactor.run()
    elif num==3:
        from eventlet.twistedutil import join_reactor
        print "fails because it's impossible to use block_on from the mainloop"
        reactor.callLater(0, test)
        reactor.run()

