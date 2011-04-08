import sys
import threading
from twisted.internet.base import DelayedCall as TwistedDelayedCall
from eventlet.support import greenlets as greenlet
from eventlet.hubs.hub import FdListener, READ, WRITE

class DelayedCall(TwistedDelayedCall):
    "fix DelayedCall to behave like eventlet's Timer in some respects"

    def cancel(self):
        if self.cancelled or self.called:
            self.cancelled = True
            return
        return TwistedDelayedCall.cancel(self)

class LocalDelayedCall(DelayedCall):

    def __init__(self, *args, **kwargs):
        self.greenlet = greenlet.getcurrent()
        DelayedCall.__init__(self, *args, **kwargs)

    def _get_cancelled(self):
        if self.greenlet is None or self.greenlet.dead:
            return True
        return self.__dict__['cancelled']

    def _set_cancelled(self, value):
        self.__dict__['cancelled'] = value

    cancelled = property(_get_cancelled, _set_cancelled)

def callLater(DelayedCallClass, reactor, _seconds, _f, *args, **kw):
    # the same as original but creates fixed DelayedCall instance
    assert callable(_f), "%s is not callable" % _f
    if not isinstance(_seconds, (int, long, float)):
        raise TypeError("Seconds must be int, long, or float, was " + type(_seconds))
    assert sys.maxint >= _seconds >= 0, \
           "%s is not greater than or equal to 0 seconds" % (_seconds,)
    tple = DelayedCallClass(reactor.seconds() + _seconds, _f, args, kw,
                            reactor._cancelCallLater,
                            reactor._moveCallLaterSooner,
                            seconds=reactor.seconds)
    reactor._newTimedCalls.append(tple)
    return tple

class socket_rwdescriptor(FdListener):
    #implements(IReadWriteDescriptor)
    def __init__(self, evtype, fileno, cb):
        super(socket_rwdescriptor, self).__init__(evtype, fileno, cb)
        if not isinstance(fileno, (int,long)):
            raise TypeError("Expected int or long, got %s" % type(fileno))
        # Twisted expects fileno to be a callable, not an attribute
        def _fileno():
            return fileno
        self.fileno = _fileno

    # required by glib2reactor
    disconnected = False

    def doRead(self):
        if self.evtype is READ:
            self.cb(self)

    def doWrite(self):
        if self.evtype == WRITE:
            self.cb(self)

    def connectionLost(self, reason):
        self.disconnected = True
        if self.cb:
            self.cb(reason)
        # trampoline() will now switch into the greenlet that owns the socket
        # leaving the mainloop unscheduled. However, when the next switch
        # to the mainloop occurs, twisted will not re-evaluate the delayed calls
        # because it assumes that none were scheduled since no client code was executed
        # (it has no idea it was switched away). So, we restart the mainloop.
        # XXX this is not enough, pollreactor prints the traceback for
        # this and epollreactor times out. see test__hub.TestCloseSocketWhilePolling
        raise greenlet.GreenletExit

    logstr = "twistedr"

    def logPrefix(self):
        return self.logstr


class BaseTwistedHub(object):
    """This hub does not run a dedicated greenlet for the mainloop (unlike TwistedHub).
    Instead, it assumes that the mainloop is run in the main greenlet.

    This makes running "green" functions in the main greenlet impossible but is useful
    when you want to call reactor.run() yourself.
    """

    # XXX: remove me from here. make functions that depend on reactor
    # XXX: hub's methods
    uses_twisted_reactor = True

    WRITE = WRITE
    READ = READ

    def __init__(self, mainloop_greenlet):
        self.greenlet = mainloop_greenlet

    def switch(self):
        assert greenlet.getcurrent() is not self.greenlet, \
               "Cannot switch from MAINLOOP to MAINLOOP"
        try:
           greenlet.getcurrent().parent = self.greenlet
        except ValueError:
           pass
        return self.greenlet.switch()

    def stop(self):
        from twisted.internet import reactor
        reactor.stop()

    def add(self, evtype, fileno, cb):
        from twisted.internet import reactor
        descriptor = socket_rwdescriptor(evtype, fileno, cb)
        if evtype is READ:
            reactor.addReader(descriptor)
        if evtype is WRITE:
            reactor.addWriter(descriptor)
        return descriptor

    def remove(self, descriptor):
        from twisted.internet import reactor
        reactor.removeReader(descriptor)
        reactor.removeWriter(descriptor)

    def schedule_call_local(self, seconds, func, *args, **kwargs):
        from twisted.internet import reactor
        def call_if_greenlet_alive(*args1, **kwargs1):
            if timer.greenlet.dead:
                return
            return func(*args1, **kwargs1)
        timer = callLater(LocalDelayedCall, reactor, seconds,
                          call_if_greenlet_alive, *args, **kwargs)
        return timer

    schedule_call = schedule_call_local

    def schedule_call_global(self, seconds, func, *args, **kwargs):
        from twisted.internet import reactor
        return callLater(DelayedCall, reactor, seconds, func, *args, **kwargs)

    def abort(self):
        from twisted.internet import reactor
        reactor.crash()

    @property
    def running(self):
        from twisted.internet import reactor
        return reactor.running

    # for debugging:

    def get_readers(self):
        from twisted.internet import reactor
        readers = reactor.getReaders()
        readers.remove(getattr(reactor, 'waker'))
        return readers

    def get_writers(self):
        from twisted.internet import reactor
        return reactor.getWriters()


    def get_timers_count(self):
        from twisted.internet import reactor
        return len(reactor.getDelayedCalls())


class TwistedHub(BaseTwistedHub):
    # wrapper around reactor that runs reactor's main loop in a separate greenlet.
    # whenever you need to wait, i.e. inside a call that must appear
    # blocking, call hub.switch() (then your blocking operation should switch back to you
    # upon completion)

    # unlike other eventlet hubs, which are created per-thread,
    # this one cannot be instantiated more than once, because
    # twisted doesn't allow that

    # 0-not created
    # 1-initialized but not started
    # 2-started
    # 3-restarted
    state = 0

    installSignalHandlers = False

    def __init__(self):
        assert Hub.state==0, ('%s hub can only be instantiated once'%type(self).__name__,
                              Hub.state)
        Hub.state = 1
        make_twisted_threadpool_daemonic() # otherwise the program
                                        # would hang after the main
                                        # greenlet exited
        g = greenlet.greenlet(self.run)
        BaseTwistedHub.__init__(self, g)

    def switch(self):
        assert greenlet.getcurrent() is not self.greenlet, \
               "Cannot switch from MAINLOOP to MAINLOOP"
        if self.greenlet.dead:
            self.greenlet = greenlet.greenlet(self.run)
        try:
            greenlet.getcurrent().parent = self.greenlet
        except ValueError:
            pass
        return self.greenlet.switch()

    def run(self, installSignalHandlers=None):
        if installSignalHandlers is None:
            installSignalHandlers = self.installSignalHandlers

        # main loop, executed in a dedicated greenlet
        from twisted.internet import reactor
        assert Hub.state in [1, 3], ('run function is not reentrant', Hub.state)

        if Hub.state == 1:
            reactor.startRunning(installSignalHandlers=installSignalHandlers)
        elif not reactor.running:
            # if we're here, then reactor was explicitly stopped with reactor.stop()
            # restarting reactor (like we would do after an exception) in this case
            # is not an option.
            raise AssertionError("reactor is not running")

        try:
            self.mainLoop(reactor)
        except:
            # an exception in the mainLoop is a normal operation (e.g. user's
            # signal handler could raise an exception). In this case we will re-enter
            # the main loop at the next switch.
            Hub.state = 3
            raise

        # clean exit here is needed for abort() method to work
        # do not raise an exception here.

    def mainLoop(self, reactor):
        Hub.state = 2
        # Unlike reactor's mainLoop, this function does not catch exceptions.
        # Anything raised goes into the main greenlet (because it is always the
        # parent of this one)
        while reactor.running:
            # Advance simulation time in delayed event processors.
            reactor.runUntilCurrent()
            t2 = reactor.timeout()
            t = reactor.running and t2
            reactor.doIteration(t)

Hub = TwistedHub

class DaemonicThread(threading.Thread):
    def _set_daemon(self):
        return True

def make_twisted_threadpool_daemonic():
    from twisted.python.threadpool import ThreadPool
    if ThreadPool.threadFactory != DaemonicThread:
        ThreadPool.threadFactory = DaemonicThread
